from llm_proc_utils import get_completion, wait_for_rate_limit

from collections import defaultdict
import re
import unicodedata
import json
import time
import random

from rdflib import URIRef
from rdflib.namespace import split_uri
import numpy as np
import asyncio


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

resolution_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "cluster_id": {
                "type": "integer"
            },
            "resolutions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "canonical_label": {
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
                        "canonical_label",
                        "members"
                    ],
                    "additionalProperties": False
                }
            }
        },
        "required": [
            "cluster_id",
            "resolutions"
        ],
        "additionalProperties": False
    }
}

resolution_prompt = """
You are resolving potentially duplicate labels extracted from EU legal documents.

Your task is to decide whether labels within each cluster refer to the same resource.

Rules:

1. This is a clustering task, not a rewriting task.
- The canonical_label MUST be copied exactly from one of the provided members.
- Do not create, modify, or improve labels.

2. Each cluster must be partitioned correctly.
- Every input label must appear exactly once in the output.
- Do not assign a label to multiple groups.
- Do not omit any labels.

3. Merge labels only when they clearly refer to the same resource.
- If uncertain, keep labels separate.
- A cluster being provided does not mean all labels should be merged.


Example:

Cluster ID: 5
Resource type: entity

Candidates:

Resource ID: c5_r1
Label: the member

Resource ID: c5_r2
Label: a member

Output:
{
    "cluster_id": 5,
    "resolutions": [
        {
            "canonical_label": "c5_r1",
            "members": ["c5_r1", "c5_r2"]
        }
    ]
                    
    
}

Now resolve the following clusters:

"""

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
        ra = self.find(a)
        rb = self.find(b)

        if ra != rb:
            self.parent[rb] = ra

def normalize_key(label: str) -> str:
    """
    Normalize labels for clustering/matching.

    This function should only remove superficial differences:
    - casing
    - Unicode variants
    - whitespace inconsistencies
    - punctuation formatting
    - legal identifier spacing

    It should NOT attempt semantic equivalence.
    """

    # Case normalization
    label = label.casefold()

    # Normalize Unicode representations
    label = unicodedata.normalize("NFKC", label)

    # Replace common invisible whitespace characters
    label = label.replace("\u00a0", " ")   # non-breaking space
    label = label.replace("\u202f", " ")   # narrow no-break space
    label = label.replace("\u200b", "")    # zero-width space

    # Normalize dash variants
    label = re.sub(
        r"[\u2010\u2011\u2012\u2013\u2014\u2212]",
        "-",
        label
    )

    # Collapse whitespace
    label = re.sub(r"\s+", " ", label)

    # Normalize numeric subdivisions:
    # Article 93 (3) -> Article 93(3)
    # Point 5 (1) -> Point 5(1)
    label = re.sub(
        r"(\d+)\s+\(\s*(\d+)\s*\)",
        r"\1(\2)",
        label
    )

    # Normalize alphabetic subdivisions:
    # Article 5 (a) -> Article 5(a)
    label = re.sub(
        r"(\d+)\s+\(\s*([a-z])\s*\)",
        r"\1(\2)",
        label
    )

    # Clean spaces inside parentheses:
    # ( EEC ) -> (eec)
    # ( 3 ) -> (3)
    label = re.sub(r"\(\s+", "(", label)
    label = re.sub(r"\s+\)", ")", label)

    return label.strip()

def has_identifier_1(text: str) -> bool:
    """
    Returns True if the label looks like a legal identifier
    or numbered designation.

    Conservative by design.
    """

    return bool(
        re.search(
            r"""
            \d                      # any digit
            |
            \([A-Za-z0-9]+\)        # (1), (a), (ii)
            |
            \b[IVXLCDM]+\b          # Roman numerals
            """,
            text,
            flags=re.IGNORECASE | re.VERBOSE,
        )
    )

def extract_uri_label(uri: URIRef):
    """
    Extract readable local name from a URI.

    Example:
        http://jurisynth/data/decision_no_30
            ->
        decision no 30
    """

    try:
        _, local = split_uri(uri)
    except Exception:
        local = str(uri).rsplit("/", 1)[-1]

    return local.replace("_", " ")

def prepare_document_resources(scored_triples, namespace):
    """
    Prepare custom resources for per-document deduplication.

    Returns
    -------
    document_resources

    {
        doc_id:
        {
            uri:
            {
                "uri": str,
                "label": str,
                "occurrences": [...],
                "contexts": set(),
                "neighbors": set()
            }
        }
    }
    """

    document_entities = defaultdict(dict)
    document_relations = defaultdict(dict)
    js_namespace = str(namespace)

    for element in scored_triples:

        doc_id = element["doc_id"]
        chunk_id = element["chunk_id"]
        triple = element["triple"]

        for component in ("subject", "predicate", "object"):
            
            value = triple[component]

            if not isinstance(value, URIRef):
                continue
            if component != "predicate" and has_identifier_1(value):
                continue
            elif component == "predicate":
                target = document_relations
            else:
                target = document_entities
            
            uri = str(value)

            # Only deduplicate custom resources
            if not uri.startswith(js_namespace):
                continue

            if uri not in target[doc_id]:

                label = extract_uri_label(value)

                target[doc_id][uri] = {
                    "uri": uri,
                    "label": label,         # Original human-readable label
                    "occurrences": list(),  # Direct references into scored_triples
                    "contexts": set(),      # Optional future enrichment
                    "neighbors": set()      # Graph neighbours
                }

            target[doc_id][uri]["occurrences"].append({
                "triple_id": element["triple_id"],
                "chunk_id": chunk_id,
                "component": component
            })

    return document_entities, document_relations

def ngram_tokenize(text, n=3):
    text = text.lower().replace(" ", "")

    return [
        text[i:i+n]
        for i in range(len(text)-n+1)
    ]

def attach_resource_embeddings(
    document_resources,
    emb_model,
    batch_size=128
):
    """
    Compute embeddings for all resources across
    all documents.

    Adds:
        resource["embedding"]

    Parameters
    ----------
    document_resources : dict
        {
            doc_id:
                {
                    uri:
                        resource_dict
                }
        }

    """

    resource_entries = list()
    labels = list()


    for doc_id, resources in document_resources.items():
        for uri, resource in resources.items():
            resource_entries.append(
                (
                    doc_id,
                    uri,
                    resource
                )
            )

            labels.append(resource["label"])

    embeddings = emb_model.encode(
        labels,
        batch_size=batch_size,
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    for (_, _, resource), embedding in zip(
        resource_entries,
        embeddings
    ):

        resource["embedding"] = embedding

def build_candidate_clusters(
    doc_resources,
    similarity_threshold=0.9,
):
    """
    Build candidate equivalence clusters using
    pairwise cosine similarity.

    Parameters
    ----------
    doc_resources : dict

        Mapping:

        URIRef ->
        {
            "uri": URIRef,
            "label": str,
            "embedding": np.ndarray,
            "occurrences": list,
            "contexts": set,
            "neighbors": set
        }


    similarity_threshold : float
        Minimum cosine similarity required
        to merge two resources.


    Returns
    -------
    list[dict]

        [
            {
                "cluster_id": int,
                "resources": {
                    URIRef:
                        resource_dict
                }
            }
        ]
    """


    if not doc_resources:
        return list()


    uris = list(
        doc_resources.keys()
    )


    # ---------------------------------
    # Collect embeddings
    # ---------------------------------

    embeddings = np.stack(
        [
            doc_resources[uri]["embedding"]
            for uri in uris
        ]
    )


    # ---------------------------------
    # Pairwise cosine similarity
    #
    # embeddings are already normalized
    # ---------------------------------

    similarity_matrix = (
        embeddings @ embeddings.T
    )


    # ---------------------------------
    # Union-Find clustering
    # ---------------------------------

    uf = UnionFind(
        len(uris)
    )


    for i in range(len(uris)):

        for j in range(
            i + 1,
            len(uris)
        ):

            if (
                similarity_matrix[i, j]
                >= similarity_threshold
            ):

                uf.union(
                    i,
                    j
                )


    # ---------------------------------
    # Connected components
    # ---------------------------------

    grouped = defaultdict(list)


    for idx in range(len(uris)):

        grouped[
            uf.find(idx)
        ].append(idx)



    clusters = list()

    cluster_id = 1


    for members in grouped.values():

        # Ignore singleton resources
        if len(members) < 2:
            continue


        cluster_resources = dict()


        for idx in members:

            uri = uris[idx]

            cluster_resources[uri] = (
                doc_resources[uri]
            )


        clusters.append(
            {
                "cluster_id": cluster_id,
                "resources": cluster_resources
            }
        )

        cluster_id += 1


    return clusters

def build_resolution_batches(queries, batch_size=10):
    """
    Convert resolution queries into batched LLM requests.

    Each batch contains:
        - query: string sent to the LLM
        - lookup: mapping from
          (doc_id, cluster_type, cluster_id)
          to temporary resource ID -> URI

    Parameters
    ----------
    queries : list[dict]

        Expected format:

        {
            "doc_id": str,
            "cluster_type": str,
            "cluster_id": int,
            "resources": {
                uri: {
                    "label": str,
                    ...
                }
            },
            "query": str
        }

    batch_size : int
        Number of clusters per LLM request.

    Returns
    -------
    list[dict]
    """

    batches = list()

    for batch_start in range(
        0,
        len(queries),
        batch_size
    ):

        batch = queries[
            batch_start:
            batch_start + batch_size
        ]

        query_parts = list()
        lookup = dict()

        for cluster_query in batch:
            doc_id = cluster_query["doc_id"]
            cluster_type = cluster_query["cluster_type"]
            cluster_id = cluster_query["cluster_id"]

            key = (
                doc_id,
                cluster_type,
                cluster_id
            )

            resource_map = dict()

            for idx, (uri, resource) in enumerate(
                cluster_query["resources"].items(),
                start=1
            ):
                temp_id = f"r{idx}"
                resource_map[temp_id] = uri

            lookup[key] = resource_map
            query_parts.append(cluster_query["query"])

        batches.append(
            {
                "query": "\n\n".join(query_parts),
                "lookup": lookup
            }
        )

    return batches

def has_identifier_2(label: str) -> bool:
    """
    Returns True if a resource label contains an
    identifier-like component.

    Identifier-bearing entities are treated as
    unsafe for automatic deduplication because
    small differences may represent genuinely
    different legal concepts.

    Examples:

        Article 5
        Article 6
        Decision No 30/53
        Directive 2004/18/EC
        Annex III

    """

    if not label:
        return False

    label = label.strip()

    return any(
        regex.search(label)
        for regex in IDENTIFIER_REGEX
    )

def filter_resolution_clusters(clusters):
    """
    Split candidate equivalence clusters into:

    review_clusters:
        Clusters that can proceed to semantic
        resolution.

    skipped_clusters:
        Clusters where every resource contains an
        identifier-like component and should not be
        merged automatically.


    Parameters
    ----------
    clusters : list[dict]

        Expected format:

        {
            "cluster_id": int,
            "resources": {
                URIRef:
                    {
                        "uri": URIRef,
                        "label": str,
                        ...
                    }
            }
        }


    Returns
    -------
    tuple[list, list]

        review_clusters,
        skipped_clusters

    """


    review_clusters = list()
    skipped_clusters = list()


    for cluster in clusters:

        labels = [
            resource["label"]
            for resource in cluster["resources"].values()
        ]

        # Conservative rule:
        # only skip when ALL resources are
        # identifier-bearing.
        if labels and all(
            has_identifier_2(label)
            for label in labels
        ):

            skipped_clusters.append(cluster)

        else:

            review_clusters.append(cluster)


    return (
        review_clusters,
        skipped_clusters
    )

def build_resolution_query(cluster, cluster_type, doc_id):
    """
    Build an LLM resolution query for a candidate
    equivalence cluster.

    Parameters
    ----------
    cluster : dict
        Candidate cluster containing resources.

    cluster_type : str
        "entity" or "relation"
    
    doc_id : str
        Source document identifier.

    Returns
    -------
    str
        Structured query string for LLM resolution.
    """

    lines = [
        f"Document: {doc_id}",
        f"Resource type: {cluster_type}",
        f"Cluster ID: {cluster['cluster_id']}",
        "",
        "Candidate resources:"
    ]


    for idx, (uri, resource) in enumerate(
        cluster["resources"].items(),
        start=1
    ):

        lines.extend([
            f"{idx}.",
            f"URI: {uri}",
            f"Label: {resource['label']}",
            ""
        ])


    return "\n".join(lines)

async def resolution_worker(
    batch,
    semaphore,
    rate_lock,
    last_request_time,
    cooldown_until,
    current_rps,
    max_rps,
    max_backoff=30,
    min_rps=0.25,
    recovery_step=0.10,
):
    """
    Resolve one batch of candidate clusters.
    """

    attempt = 0

    while True:
        async with semaphore:
            await wait_for_rate_limit(
                rate_lock,
                last_request_time,
                cooldown_until,
                current_rps,
            )

            try:
                response = await get_completion(
                    system_prompt=resolution_prompt,
                    query=batch["query"],
                    schema=resolution_schema,
                )

                clusters = json.loads(response)

                # ------------------------------------------
                # Slowly recover request rate
                # ------------------------------------------

                async with rate_lock:
                    current_rps[0] = min(max_rps, current_rps[0] + recovery_step)

                return {
                    "success": True,
                    "clusters": clusters,
                    "lookup": batch["lookup"],
                }


            except Exception as e:

                error_text = str(e)

                # ------------------------------------------
                # Retry transient API failures
                # ------------------------------------------

                if (
                    "429" in error_text
                    or
                    "503" in error_text
                ):
                    backoff = min(2 ** attempt, max_backoff)
                    backoff += random.uniform(0, 1)

                    async with rate_lock:
                        cooldown_until[0] = max(cooldown_until[0], time.monotonic() + backoff)
                        current_rps[0] = max(min_rps, current_rps[0] / 2)
                        current_rate = current_rps[0]

                    print(
                        f"[Resolution] "
                        f"{error_text}\n"
                        f"Cooldown: {backoff:.1f}s | "
                        f"RPS: {current_rate:.2f}"
                    )

                    attempt += 1

                    continue


                # ------------------------------------------
                # Non-retryable failure
                # ------------------------------------------

                print(f"Resolution failed: {e}")

                return {
                    "success": False,
                    "clusters": list(),
                    "lookup": batch["lookup"],
                }

def attach_lookup_metadata(clusters, lookup):
    """
    Restore local metadata omitted from the LLM prompt.

    Parameters
    ----------
    clusters : list[dict]

    lookup : dict

        Expected format:
        {
            cluster_id: {
                "doc_id": ...,
                "cluster_type": ...,
                "resource_map": ...
            }
        }

    Returns
    -------
    list[dict]
    """

    for cluster in clusters:
        cluster_id = cluster["cluster_id"]

        matches = [
            (key, resource_map)
            for key, resource_map in lookup.items()
            if key[2] == cluster_id
            ]

        if not matches:
            raise KeyError(f"No lookup found for cluster {cluster_id}")

        key, resource_map = matches[0]

        doc_id, cluster_type, _ = key

        cluster["doc_id"] = doc_id
        cluster["cluster_type"] = cluster_type
        cluster["resource_map"] = resource_map

    return clusters

async def resolve_batches(
    batches,
    semaphore,
    requests_per_second=2,
    max_backoff=30,
):

    rate_lock = asyncio.Lock()

    last_request_time = [0.0]
    cooldown_until = [0.0]

    current_rps = [requests_per_second]


    tasks = [

        resolution_worker(
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

    batch_results = await asyncio.gather(*tasks)
    resolved = list()

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

def build_resolution_map(resolved_clusters):
    """
    Convert LLM cluster resolutions into:

        old_uri -> canonical_uri

    Parameters
    ----------
    resolved_clusters : list[dict]
        Enriched LLM outputs containing:

        {
            "cluster_id": int,
            "resolutions": [...],
            "resource_map": {
                temporary_id: URI
            }
        }

    Returns
    -------
    dict
        URI replacement map.
    """

    resolution_map = dict()

    for cluster in resolved_clusters:
        for resolution in cluster["resolutions"]:
            canonical_uri = resolution["canonical_label"]

            for member_uri in resolution["members"]:
                resolution_map[member_uri] = canonical_uri

    return resolution_map

def apply_resolution(
    scored_triples,
    entity_map,
    relation_map
):
    """
    Apply URI resolution maps to scored triples.

    Parameters
    ----------
    scored_triples : list[dict]

    Returns
    -------
    list[dict]
    """

    resolved_triples = list()

    for element in scored_triples:
        updated = element.copy()
        triple = element["triple"].copy()

        # -----------------------------
        # Resolve all components
        # -----------------------------

        if (
            isinstance(triple["subject"], URIRef)
            and triple["subject"] in entity_map
        ):
            triple["subject"] = entity_map[triple["subject"]]

        if (
            isinstance(triple["object"], URIRef)
            and triple["object"] in entity_map
        ):
            triple["object"] = entity_map[triple["object"]]

        if (
            isinstance(triple["predicate"], URIRef)
            and triple["predicate"] in relation_map
        ):
            triple["predicate"] = relation_map[triple["predicate"]]

        updated["triple"] = triple
        resolved_triples.append(updated)

    return resolved_triples