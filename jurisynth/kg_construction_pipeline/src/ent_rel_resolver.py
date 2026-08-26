# ================================================================
# Entity-Relation Resolver
# ================================================================

import asyncio
import copy
import json
import random
import re
import time
import unicodedata
from collections import defaultdict

import numpy as np
from openai import AsyncOpenAI
from rdflib import URIRef
from rdflib.namespace import split_uri

from schema_loader import JS_DATA
from llm_utils import (
    get_completion,
    wait_for_rate_limit,
    MAX_CONCURRENT_REQUESTS,
    DEFAULT_REQUESTS_PER_SECOND,
    MAX_BACKOFF,
    MIN_RPS,
    RECOVERY_STEP
)

# ---------------------------------------------------------------------
# Identifier patterns
# ---------------------------------------------------------------------

IDENTIFIER_PATTERNS = [
    # Legal structural references
    r"\barticle\s+\d+",
    r"\bart\.\s*\d+",
    r"\bparagraph\s+\d+",
    r"\bpara\.\s*\d+",
    r"\bpoint\s+\(?[a-z0-9]+\)?",
    r"\bsection\s+\d+",
    r"\bchapter\s+[ivxlcdm\d]+",
    r"\btitle\s+[ivxlcdm\d]+",
    r"\bannex\s+[ivxlcdm\d]+",
    r"\brecital\s+\d+",

    # Legal instrument identifiers
    r"\bno\.?\s*\d+",
    r"\b\d+/\d+\b",

    # Directive / regulation style identifiers
    r"\b\d{4}/\d+\b",

    # Standalone year identifiers
    r"\b(19|20)\d{2}\b",

    # Explicit subdivisions
    r"\([a-z]\)",
    r"\(\d+\)",
]

IDENTIFIER_REGEX = [
    re.compile(
        pattern,
        flags=re.IGNORECASE
    )
    for pattern in IDENTIFIER_PATTERNS
]


# ---------------------------------------------------------------------
# LLM resolution schema / prompt
# ---------------------------------------------------------------------

RESOLUTION_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "document_id": {
                "type": "string"
            },
            "cluster_id": {
                "type": "integer"
            },
            "resolutions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "canonical_id": {
                            "type": "string"
                        },
                        "members": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "minItems": 1
                        }
                    },
                    "required": [
                        "canonical_id",
                        "members"
                    ],
                    "additionalProperties": False
                }
            }
        },
        "required": [
            "document_id",
            "cluster_id",
            "resolutions"
        ],
        "additionalProperties": False
    }
}


RESOLUTION_PROMPT = """
You are resolving potentially duplicate resources extracted from EU legal documents.
Your task is to decide which candidate resources within each cluster refer to the same resource.

Rules:
1. This is a clustering task, not a rewriting task.
- The document_id MUST be copied exactly from the provided document identifier.
- The cluster_id MUST be copied exactly from the provided cluster identifier.
- The canonical_id MUST be copied exactly from one of the provided Resource IDs.
- Do not create, modify, or invent any identifiers.

2. Each cluster must be partitioned correctly.
- Every provided Resource ID must appear exactly once in the output.
- Do not assign a Resource ID to multiple groups.
- Do not omit any Resource IDs.

3. Merge resources only when their labels clearly refer to the same resource.
- If uncertain, keep resources separate.
- A candidate cluster does not mean that all resources should be merged.

Example:
Document ID: d1
Cluster ID: 5
Resource type: entity
Candidates:
Resource ID: c5_r1
Label: the member
Resource ID: c5_r2
Label: a member

Output:
{
    "document_id": "d1",
    "cluster_id": 5,
    "resolutions": [
        {
            "canonical_id": "c5_r1",
            "members": ["c5_r1", "c5_r2"]
        }
    ]
}

Now resolve the following clusters:
"""


# ---------------------------------------------------------------------
# Union-Find
# ---------------------------------------------------------------------

class UnionFind:

    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(
                self.parent[x]
            )
        return self.parent[x]

    def union(self, a, b):
        root_a = self.find(a)
        root_b = self.find(b)

        if root_a != root_b:
            self.parent[root_b] = root_a


# ---------------------------------------------------------------------
# Label normalization
# ---------------------------------------------------------------------

def normalize_key(label: str) -> str:
    """
    Normalize labels for clustering/matching.

    Only removes superficial differences:
    - casing
    - Unicode variants
    - whitespace inconsistencies
    - punctuation formatting
    - legal identifier spacing

    Does not attempt semantic equivalence.
    """

    label = label.casefold()
    label = unicodedata.normalize("NFKC", label)

    label = label.replace("\u00a0", " ")
    label = label.replace("\u202f", " ")
    label = label.replace("\u200b", "")

    label = re.sub(
        r"[\u2010\u2011\u2012\u2013\u2014\u2212]",
        "-",
        label
    )

    label = re.sub(r"\s+", " ", label)

    label = re.sub(
        r"(\d+)\s+\(\s*(\d+)\s*\)",
        r"\1(\2)",
        label
    )

    label = re.sub(
        r"(\d+)\s+\(\s*([a-z])\s*\)",
        r"\1(\2)",
        label
    )

    label = re.sub(
        r"\(\s+",
        "(",
        label
    )

    label = re.sub(
        r"\s+\)",
        ")",
        label
    )

    return label.strip()


def has_identifier(label: str) -> bool:
    """
    Detect legal identifier-like components.

    Identifier-bearing resources are treated conservatively
    during automatic deduplication.
    """

    if not label:
        return False

    label = label.strip()

    return any(
        regex.search(label)
        for regex in IDENTIFIER_REGEX
    )


# ---------------------------------------------------------------------
# URI helpers
# ---------------------------------------------------------------------

def extract_uri_label(uri: URIRef):
    """
    Extract a readable local name from a URI.
    """

    try:
        _, local = split_uri(uri)
    except Exception:
        local = str(uri).rsplit("/", 1)[-1]

    return local.replace("_", " ")


# ---------------------------------------------------------------------
# Resource preparation
# ---------------------------------------------------------------------

def prepare_document_resources(scored_assertions):
    """
    Prepare custom Jurisynth resources for per-document
    deduplication.

    Returns
    -------
    tuple[defaultdict, defaultdict]
        document_entities
        document_relations
    """

    document_entities = defaultdict(dict)
    document_relations = defaultdict(dict)

    js_namespace = str(JS_DATA)

    for element in scored_assertions:

        doc_id = element["doc_id"]
        chunk_id = element["chunk_id"]
        assertion_id = element["assertion_id"]
        assertion = element["assertion"]

        for component in (
            "subject",
            "predicate",
            "object",
        ):

            value = assertion[component]

            if not isinstance(value, URIRef):
                continue

            # Legal identifiers are deliberately excluded
            # from automatic deduplication.
            if (
                component != "predicate"
                and has_identifier(str(value))
            ):
                continue

            target = (
                document_relations
                if component == "predicate"
                else document_entities
            )

            uri = str(value)

            # Only custom Jurisynth resources are candidates
            # for document-level deduplication.
            if not uri.startswith(js_namespace):
                continue

            if uri not in target[doc_id]:

                target[doc_id][uri] = {
                    "uri": uri,
                    "label": extract_uri_label(value),
                    "occurrences": [],
                    "contexts": set(),
                    "neighbors": set(),
                }

            target[doc_id][uri]["occurrences"].append(
                {
                    "assertion_id": assertion_id,
                    "chunk_id": chunk_id,
                    "component": component,
                }
            )

    return (
        document_entities,
        document_relations,
    )


# ---------------------------------------------------------------------
# Embeddings
# ---------------------------------------------------------------------

def attach_resource_embeddings(
    document_resources,
    emb_model,
    batch_size=128,
):
    """
    Compute embeddings for all resources across all documents.

    The supplied embedding model is reused; this function does
    not instantiate a new model.
    """

    resource_entries = []
    labels = []

    for doc_id, resources in document_resources.items():

        for uri, resource in resources.items():

            resource_entries.append(
                (
                    doc_id,
                    uri,
                    resource,
                )
            )

            labels.append(
                resource["label"]
            )

    if not labels:
        return

    embeddings = emb_model.encode(
        labels,
        batch_size=batch_size,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    for (_, _, resource), embedding in zip(
        resource_entries,
        embeddings,
    ):
        resource["embedding"] = embedding


# ---------------------------------------------------------------------
# Candidate clustering
# ---------------------------------------------------------------------

def build_candidate_clusters(
    doc_resources,
    similarity_threshold=0.9,
):
    """
    Build candidate equivalence clusters using pairwise
    cosine similarity.

    Only non-singleton clusters are returned.
    """

    if not doc_resources:
        return []

    uris = list(
        doc_resources.keys()
    )

    embeddings = np.stack(
        [
            doc_resources[uri]["embedding"]
            for uri in uris
        ]
    )

    similarity_matrix = (
        embeddings @ embeddings.T
    )

    uf = UnionFind(
        len(uris)
    )

    for i in range(len(uris)):

        for j in range(
            i + 1,
            len(uris),
        ):

            if (
                similarity_matrix[i, j]
                >= similarity_threshold
            ):
                uf.union(i, j)

    grouped = defaultdict(list)

    for idx in range(len(uris)):
        grouped[
            uf.find(idx)
        ].append(idx)

    clusters = []
    cluster_id = 1

    for members in grouped.values():

        if len(members) < 2:
            continue

        cluster_resources = {}

        for idx in members:

            uri = uris[idx]

            cluster_resources[uri] = (
                doc_resources[uri]
            )

        clusters.append(
            {
                "cluster_id": cluster_id,
                "resources": cluster_resources,
            }
        )

        cluster_id += 1

    return clusters


def build_document_clusters(
    document_resources,
    similarity_threshold=0.9,
):
    """
    Build candidate clusters independently for each document.
    """

    return {
        doc_id: build_candidate_clusters(
            resources,
            similarity_threshold=similarity_threshold,
        )
        for doc_id, resources
        in document_resources.items()
    }


def release_resource_embeddings(
    document_resources,
):
    """
    Remove temporary embeddings once candidate clustering
    has completed.

    The embeddings are not needed by the LLM resolution stage.
    """

    for resources in document_resources.values():

        for resource in resources.values():

            resource.pop(
                "embedding",
                None,
            )


# ---------------------------------------------------------------------
# Cluster filtering
# ---------------------------------------------------------------------

def filter_resolution_clusters(clusters):
    """
    Split candidate clusters into reviewable and skipped
    identifier-heavy clusters.
    """

    review_clusters = []
    skipped_clusters = []

    for cluster in clusters:

        labels = [
            resource["label"]
            for resource in cluster["resources"].values()
        ]

        if labels and all(
            has_identifier(label)
            for label in labels
        ):
            skipped_clusters.append(cluster)
        else:
            review_clusters.append(cluster)

    return (
        review_clusters,
        skipped_clusters,
    )


# ---------------------------------------------------------------------
# Resolution query construction
# ---------------------------------------------------------------------

def build_resolution_query(
    cluster_query,
    resource_map,
    document_id,
):
    """
    Build the actual LLM prompt fragment using temporary
    document and resource IDs.

    This prevents the model from having to reproduce long
    document IDs or URIs.
    """
    uri_to_temp = {
        uri: temp_id
        for temp_id, uri in resource_map.items()
    }

    lines = [
        f"Document ID: {document_id}",
        f"Resource type: {cluster_query['cluster_type']}",
        f"Cluster ID: {cluster_query['cluster_id']}",
        "",
        "Candidates:",
    ]

    for uri, resource in cluster_query["resources"].items():
        temp_id = uri_to_temp[uri]
        lines.extend(
            [
                f"Resource ID: {temp_id}",
                f"Label: {resource['label']}",
                "",
            ]
        )

    return "\n".join(lines)


def collect_resolution_queries(
    entity_clusters,
    relation_clusters,
):
    """
    Convert candidate clusters into LLM resolution queries.
    """

    resolution_queries = []
    skipped_clusters = []

    for cluster_type, cluster_collection in (
        ("entity", entity_clusters),
        ("relation", relation_clusters),
    ):

        for doc_id, clusters in (
            cluster_collection.items()
        ):

            review_clusters, skipped = (
                filter_resolution_clusters(
                    clusters
                )
            )

            skipped_clusters.extend(
                skipped
            )

            for cluster in review_clusters:

                resolution_queries.append(
                    {
                        "doc_id": doc_id,
                        "cluster_type": cluster_type,
                        "cluster_id": cluster["cluster_id"],
                        "resources": cluster["resources"]
                    }
                )

    return (
        resolution_queries,
        skipped_clusters,
    )


# ---------------------------------------------------------------------
# Resolution batching
# ---------------------------------------------------------------------

def build_resolution_batches(
    queries,
    batch_size=10,
):
    """
    Convert resolution queries into batched LLM requests.
    """

    batches = []

    for batch_start in range(
        0,
        len(queries),
        batch_size,
    ):
        batch = queries[
            batch_start:
            batch_start + batch_size
        ]

        query_parts = []
        lookup = {}
        document_ids = {}

        for cluster_query in batch:
            doc_id = cluster_query["doc_id"]
            cluster_type = cluster_query["cluster_type"]
            cluster_id = cluster_query["cluster_id"]

            # Assign a short, batch-local document ID.
            if doc_id not in document_ids:
                document_ids[doc_id] = (
                    f"d{len(document_ids) + 1}"
                )

            document_id = document_ids[doc_id]

            key = (
                document_id,
                cluster_type,
                cluster_id,
            )

            resource_map = {}

            for idx, (uri, _) in enumerate(
                cluster_query["resources"].items(),
                start=1,
            ):
                temp_id = f"c{cluster_id}_r{idx}"
                resource_map[temp_id] = uri

            lookup[key] = {
                "resource_map": resource_map,
                "doc_id": doc_id,
                "cluster_type": cluster_type,
            }

            query_parts.append(
                build_resolution_query(
                    cluster_query,
                    resource_map,
                    document_id
                )
            )

        batches.append(
            {
                "query": "\n\n".join(query_parts),
                "lookup": lookup,
            }
        )

    return batches


# ---------------------------------------------------------------------
# LLM resolution
# ---------------------------------------------------------------------

def validate_resolution_output(
    clusters,
    lookup,
):
    """
    Validate LLM resolution output against the authoritative
    batch lookup.
    """

    for cluster in clusters:
        document_id = cluster["document_id"]
        cluster_id = cluster["cluster_id"]

        matches = [
            metadata
            for (doc_id, _, cid), metadata in lookup.items()
            if doc_id == document_id and cid == cluster_id
        ]

        if len(matches) != 1:
            raise ValueError(
                f"Invalid document/cluster ID: "
                f"{document_id}/{cluster_id}"
            )

        resource_map = matches[0]["resource_map"]

        valid_ids = set(resource_map)
        seen_members = set()

        for resolution in cluster["resolutions"]:
            canonical_id = resolution["canonical_id"]

            if canonical_id not in valid_ids:
                raise ValueError(
                    f"Unknown canonical resource ID: "
                    f"{canonical_id}"
                )

            if canonical_id not in resolution["members"]:
                raise ValueError(
                    f"Canonical ID {canonical_id} "
                    f"is not listed as a member."
                )

            for member_id in resolution["members"]:
                if member_id not in valid_ids:
                    raise ValueError(
                        f"Unknown member resource ID: "
                        f"{member_id}"
                    )

                if member_id in seen_members:
                    raise ValueError(
                        f"Resource ID {member_id} "
                        f"appears more than once."
                    )

                seen_members.add(member_id)

        if seen_members != valid_ids:
            missing = valid_ids - seen_members
            raise ValueError(
                f"Cluster {cluster_id} "
                f"(document {document_id}) has missing "
                f"members: {missing}"
            )

    return True


async def resolution_worker(
    client: AsyncOpenAI,
    batch,
    semaphore,
    rate_lock,
    last_request_time,
    cooldown_until,
    current_rps,
    max_rps,
    max_backoff: int = MAX_BACKOFF,
    min_rps: float = MIN_RPS,
    recovery_step: float = RECOVERY_STEP,
    max_attempts: int = 3
):
    """
    Resolve one batch of candidate clusters.
    """

    attempt = 0

    while attempt < max_attempts:
        attempt += 1

        async with semaphore:
            await wait_for_rate_limit(
                rate_lock,
                last_request_time,
                cooldown_until,
                current_rps,
            )

            try:
                response = await get_completion(
                    client=client,
                    query=batch["query"],
                    system_prompt=RESOLUTION_PROMPT,
                    schema={
                        "name": "resolutions",
                        "schema": RESOLUTION_SCHEMA
                        },
                )

                clusters = json.loads(response)

                validate_resolution_output(
                    clusters,
                    batch["lookup"],
                )

                async with rate_lock:
                    current_rps[0] = min(
                        max_rps,
                        current_rps[0]
                        + recovery_step,
                    )

                return {
                    "success": True,
                    "clusters": clusters,
                    "lookup": batch["lookup"],
                }

            except Exception as exc:
                error_text = str(exc)

                if attempt >= max_attempts:
                    print(
                        f"[Resolution] Failed after "
                        f"{max_attempts} attempts: {exc}"
                    )
                    break

                if (
                    "429" in error_text
                    or "503" in error_text
                ):

                    backoff = min(
                        2 ** attempt,
                        max_backoff,
                    )

                    backoff += random.uniform(0, 1)

                    async with rate_lock:
                        cooldown_until[0] = max(
                            cooldown_until[0],
                            time.monotonic()
                            + backoff,
                        )

                        current_rps[0] = max(
                            min_rps,
                            current_rps[0] / 2,
                        )

                        current_rate = (current_rps[0])

                    print(
                        f"[Resolution] "
                        f"{error_text}\n"
                        f"Cooldown: {backoff:.1f}s | "
                        f"RPS: {current_rate:.2f}"
                    )

                else:
                    print(
                        f"[Resolution] Invalid response: "
                        f"{exc} | "
                        f"Attempt: {attempt}/{max_attempts}"
                    )

                return {
                    "success": False,
                    "clusters": [],
                    "lookup": batch["lookup"],
                }


def attach_lookup_metadata(
    clusters,
    lookup,
):
    """
    Restore document/type/resource mapping omitted from
    the LLM output.
    """

    for cluster in clusters:
        document_id = cluster["document_id"]
        cluster_id = cluster["cluster_id"]

        matches = [
            (key, metadata)
            for key, metadata in lookup.items()
            if key[0] == document_id
            and key[2] == cluster_id
        ]

        if not matches:
            raise KeyError(
                f"No lookup found for document/cluster "
                f"{document_id}/{cluster_id}"
            )

        if len(matches) > 1:
            raise KeyError(
                f"Ambiguous lookup for document/cluster "
                f"{document_id}/{cluster_id}"
            )

        _, metadata = matches[0]

        cluster["doc_id"] = metadata["doc_id"]
        cluster["cluster_type"] = metadata["cluster_type"]
        cluster["resource_map"] = metadata["resource_map"]

    return clusters


async def resolve_batches(
    client: AsyncOpenAI,
    batches,
    semaphore: asyncio.Semaphore,
    requests_per_second: int = DEFAULT_REQUESTS_PER_SECOND,
    max_backoff: int = MAX_BACKOFF,
):
    """
    Resolve all batches asynchronously.
    """

    if not batches:
        return []

    rate_lock = asyncio.Lock()

    last_request_time = [0.0]
    cooldown_until = [0.0]
    current_rps = [requests_per_second]

    tasks = [
        resolution_worker(
            client,
            batch,
            semaphore,
            rate_lock,
            last_request_time,
            cooldown_until,
            current_rps,
            requests_per_second,
            max_backoff,
        )
        for batch in batches
    ]

    batch_results = await asyncio.gather(
        *tasks
    )

    resolved = []

    for result in batch_results:

        if not result["success"]:
            continue

        resolved.extend(
            attach_lookup_metadata(
                result["clusters"],
                result["lookup"],
            )
        )

    return resolved


# ---------------------------------------------------------------------
# Resolution map
# ---------------------------------------------------------------------

def build_resolution_map(
    resolved_clusters,
):
    """
    Convert resolved cluster memberships into:

        old_uri -> canonical_uri

    Temporary Resource IDs returned by the LLM are resolved
    through the authoritative resource_map restored during
    post-resolution metadata attachment.
    """

    resolution_map = {}

    for cluster in resolved_clusters:

        resource_map = cluster["resource_map"]

        for resolution in cluster["resolutions"]:

            canonical_id = (
                resolution["canonical_id"]
            )

            if canonical_id not in resource_map:
                raise KeyError(
                    f"Unknown canonical resource ID: "
                    f"{canonical_id}"
                )

            canonical_uri = URIRef(
                resource_map[canonical_id]
            )

            for member_id in resolution["members"]:

                if member_id not in resource_map:
                    raise KeyError(
                        f"Unknown member resource ID: "
                        f"{member_id}"
                    )

                member_uri = URIRef(
                    resource_map[member_id]
                )

                resolution_map[
                    member_uri
                ] = canonical_uri

    return resolution_map


# ---------------------------------------------------------------------
# Apply resolutions
# ---------------------------------------------------------------------

def apply_resolution(
    scored_assertions,
    entity_map,
    relation_map,
):
    """
    Apply URI resolution maps to assertion components.

    Modifiers are preserved unchanged.
    """

    resolved_assertions = []

    for element in scored_assertions:

        updated = element.copy()
        assertion = element["assertion"].copy()

        subject = assertion["subject"]

        if (
            isinstance(subject, URIRef)
            and subject in entity_map
        ):
            assertion["subject"] = (
                entity_map[subject]
            )

        object_value = assertion["object"]

        if (
            isinstance(object_value, URIRef)
            and object_value in entity_map
        ):
            assertion["object"] = (
                entity_map[object_value]
            )

        predicate = assertion["predicate"]

        if (
            isinstance(predicate, URIRef)
            and predicate in relation_map
        ):
            assertion["predicate"] = (
                relation_map[predicate]
            )

        updated["assertion"] = assertion

        resolved_assertions.append(
            updated
        )

    return resolved_assertions


# ---------------------------------------------------------------------
# Main pipeline helpers
# ---------------------------------------------------------------------

def prepare_resolution_resources(
    scored_assertions,
    emb_model,
    embedding_batch_size=128,
):
    """
    Prepare document-level entity and relation resources,
    then attach temporary embeddings.
    """

    document_entities, document_relations = (
        prepare_document_resources(
            scored_assertions
        )
    )

    attach_resource_embeddings(
        document_entities,
        emb_model,
        batch_size=embedding_batch_size,
    )

    attach_resource_embeddings(
        document_relations,
        emb_model,
        batch_size=embedding_batch_size,
    )

    return (
        document_entities,
        document_relations,
    )


def generate_resolution_clusters(
    document_entities,
    document_relations,
    similarity_threshold=0.9,
):
    """
    Generate candidate entity and relation clusters.
    """

    entity_clusters = build_document_clusters(
        document_entities,
        similarity_threshold=similarity_threshold,
    )

    relation_clusters = build_document_clusters(
        document_relations,
        similarity_threshold=similarity_threshold,
    )

    return (
        entity_clusters,
        relation_clusters,
    )


def prepare_resolution_batches(
    entity_clusters,
    relation_clusters,
    batch_size=10,
):
    """
    Build and batch all LLM resolution queries.
    """

    (
        resolution_queries,
        skipped_clusters,
    ) = collect_resolution_queries(
        entity_clusters,
        relation_clusters,
    )

    entity_queries = [
        query
        for query in resolution_queries
        if query["cluster_type"] == "entity"
    ]

    relation_queries = [
        query
        for query in resolution_queries
        if query["cluster_type"] == "relation"
    ]

    entity_batches = build_resolution_batches(
        entity_queries,
        batch_size=batch_size,
    )

    relation_batches = build_resolution_batches(
        relation_queries,
        batch_size=batch_size,
    )

    return (
        entity_batches,
        relation_batches,
        skipped_clusters,
    )


async def resolve_entities_and_relations(
    client: AsyncOpenAI,
    entity_batches,
    relation_batches,
    semaphore: asyncio.Semaphore,
    requests_per_second: int = DEFAULT_REQUESTS_PER_SECOND,
    max_backoff: int = MAX_BACKOFF,
):
    """
    Resolve entity and relation batches independently.
    """

    resolved_entities = await resolve_batches(
        client,
        entity_batches,
        semaphore,
        requests_per_second=requests_per_second,
        max_backoff=max_backoff,
    )

    resolved_relations = await resolve_batches(
        client,
        relation_batches,
        semaphore,
        requests_per_second=requests_per_second,
        max_backoff=max_backoff,
    )

    return (
        resolved_entities,
        resolved_relations,
    )


def build_resolution_maps(
    resolved_entities,
    resolved_relations,
):
    """
    Build canonical URI replacement maps.
    """

    entity_map = build_resolution_map(
        resolved_entities
    )

    relation_map = build_resolution_map(
        resolved_relations
    )

    return (
        entity_map,
        relation_map,
    )


# ---------------------------------------------------------------------
# Public module entry point
# ---------------------------------------------------------------------

async def resolve_assertions(
    client: AsyncOpenAI,
    scored_assertions,
    emb_model,
    max_concurrent_requests: int = MAX_CONCURRENT_REQUESTS,
    similarity_threshold: float = 0.9,
    embedding_batch_size: int = 128,
    resolution_batch_size: int = 10,
    requests_per_second: int = DEFAULT_REQUESTS_PER_SECOND,
    max_backoff: int = MAX_BACKOFF,
):
    """
    Complete Entity-Relation Resolution stage.

    Parameters
    ----------
    scored_assertions:
        Assertions produced by the Semantic Matcher.

    emb_model:
        Existing SentenceTransformer model. The model is reused
        rather than instantiated here.

    semaphore:
        Shared async request semaphore.

    Returns
    -------
    resolved_assertions:
        Assertions with resolved entity/relation URIs.

    metadata:
        Resolution diagnostics, including skipped clusters
        and generated maps.
    """

    # --------------------------------------------------------------
    # 1. Prepare resources
    # --------------------------------------------------------------

    semaphore = asyncio.Semaphore(max_concurrent_requests)

    (
        document_entities,
        document_relations,
    ) = prepare_resolution_resources(
        scored_assertions,
        emb_model,
        embedding_batch_size=embedding_batch_size,
    )

    # --------------------------------------------------------------
    # 2. Build candidate clusters
    # --------------------------------------------------------------

    (
        entity_clusters,
        relation_clusters,
    ) = generate_resolution_clusters(
        document_entities,
        document_relations,
        similarity_threshold=similarity_threshold,
    )

    # Embeddings are no longer needed after clustering.
    release_resource_embeddings(
        document_entities
    )

    release_resource_embeddings(
        document_relations
    )

    # --------------------------------------------------------------
    # 3. Build LLM resolution batches
    # --------------------------------------------------------------

    (
        entity_batches,
        relation_batches,
        skipped_clusters,
    ) = prepare_resolution_batches(
        entity_clusters,
        relation_clusters,
        batch_size=resolution_batch_size,
    )

    # --------------------------------------------------------------
    # 4. Resolve candidate clusters
    # --------------------------------------------------------------

    (
        resolved_entities,
        resolved_relations,
    ) = await resolve_entities_and_relations(
        client,
        entity_batches,
        relation_batches,
        semaphore,
        requests_per_second=requests_per_second,
        max_backoff=max_backoff,
    )

    # --------------------------------------------------------------
    # 5. Build URI replacement maps
    # --------------------------------------------------------------

    (
        entity_map,
        relation_map,
    ) = build_resolution_maps(
        resolved_entities,
        resolved_relations,
    )

    # --------------------------------------------------------------
    # 6. Apply canonical URIs
    # --------------------------------------------------------------

    resolved_assertions = apply_resolution(
        scored_assertions,
        entity_map,
        relation_map,
    )

    # --------------------------------------------------------------
    # 7. Return assertions + diagnostics
    # --------------------------------------------------------------

    metadata = {
        "entity_clusters": entity_clusters,
        "relation_clusters": relation_clusters,
        "skipped_clusters": skipped_clusters,
        "resolved_entities": resolved_entities,
        "resolved_relations": resolved_relations,
        "entity_map": entity_map,
        "relation_map": relation_map,
    }

    return (
        resolved_assertions,
        metadata,
    )