import copy
import gc
import re
import unicodedata
from collections import defaultdict
from datetime import datetime
from itertools import product

import faiss
import rdflib
from rdflib import Literal, URIRef
from rdflib.namespace import RDF, XSD
import spacy
from sentence_transformers import SentenceTransformer

from schema_loader import JS_DATA

# =====================================================================
# Configuration
# =====================================================================

SEMANTIC_EMBED_MODEL = "all-MiniLM-L6-v2"
SEMANTIC_THRESHOLD = 0.7
SEMANTIC_TOP_K = 3
SEMANTIC_BATCH_SIZE = 128


# =====================================================================
# NLP
# =====================================================================

nlp = spacy.load(
    "en_core_web_sm",
    disable=["ner"],
)


# =====================================================================
# Literal and legal-reference handling
# =====================================================================

TYPE_MAP = {
    "string": XSD.string,
    "integer": XSD.integer,
    "decimal": XSD.decimal,
    "boolean": XSD.boolean,
    "date": XSD.date,
    "datetime": XSD.dateTime,
}

DATE_FORMATS = [
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%d.%m.%Y",
    "%d %B %Y",
    "%d %b %Y",
]

DATETIME_FORMATS = [
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%dT%H:%M:%S.%f%z",
]

LEGAL_IDENTIFIER_PATTERNS = [
    r"\b(article|art\.?)\s*\d+(\s*\([a-z0-9]+\))?",
    (
        r"\b(regulation|directive|decision|recommendation|opinion)"
        r".*\b(no\.?|number)?\s*\d+[-/]\d+"
    ),
    r"\b\d{1,4}/\d{1,4}/[a-z]{2,5}\b",
    r"\b\d{5}[A-Z]\d{4}\b",
]

NEGATION_WORDS = {
    "not",
    "no",
    "never",
    "without",
    "neither",
    "nor",
    "n't",
}


def detect_literal_type(value: str):
    """Infer the RDF literal type from a textual value."""

    value = str(value).strip()

    if value.casefold() in {"true", "false"}:
        return "boolean"

    if re.fullmatch(r"-?\d+", value):
        return "integer"

    if re.fullmatch(r"-?\d+\.\d+", value):
        return "decimal"

    for fmt in DATETIME_FORMATS:
        try:
            datetime.strptime(value, fmt)
            return "datetime"
        except ValueError:
            pass

    for fmt in DATE_FORMATS:
        try:
            datetime.strptime(value, fmt)
            return "date"
        except ValueError:
            pass

    return "class"


def normalize_date(value: str, literal_type: str):
    """Normalize date/datetime literals to canonical ISO forms."""

    if literal_type == "date":
        for fmt in DATE_FORMATS:
            try:
                dt = datetime.strptime(value, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue

    elif literal_type == "datetime":
        for fmt in DATETIME_FORMATS:
            try:
                dt = datetime.strptime(value, fmt)
                return dt.isoformat()
            except ValueError:
                continue

    return value


def is_legal_identifier_reference(text: str) -> bool:
    """Heuristically detect explicit legal identifiers/references."""

    text = text.casefold()

    return any(
        re.search(pattern, text)
        for pattern in LEGAL_IDENTIFIER_PATTERNS
    )


def extract_polarity_doc(doc):
    """
    Return False for explicitly negative predicates and True otherwise.

    This is intended for short ontology labels/predicates.
    """

    for token in doc:
        if token.lower_ in NEGATION_WORDS:
            return False

    return True


def extract_polarity(text: str):
    """Convenience wrapper for predicate polarity detection."""

    return extract_polarity_doc(nlp.make_doc(text))


def create_custom_uri(text: str, prefix=JS_DATA):
    """
    Generate a stable Jurisynth URI for an unresolved resource.
    """

    text = unicodedata.normalize(
        "NFKC",
        text.casefold(),
    )

    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^a-z0-9_\-]", "", text)

    return URIRef(prefix[text])


# =====================================================================
# Build semantic resource indices
# =====================================================================

def build_resource_indices(
    resources,
    resource_metadata,
    emb_model,
):
    """
    Build temporary FAISS indices for ontology resources.

    Returns
    -------
    dict
        Maps resource type to:
        (FAISS index, URIs, labels)
    """

    index_lookup = {}

    for resource_type, resource_dict in resources.items():

        if not resource_dict:
            continue

        uris = list(resource_dict.keys())

        texts = [
            resource_metadata[uri]["text"]
            for uri in uris
        ]

        embeddings = emb_model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        index = faiss.IndexFlatIP(
            embeddings.shape[1]
        )

        index.add(embeddings)

        index_lookup[resource_type] = (
            index,
            uris,
            texts,
        )

    return index_lookup


# =====================================================================
# Prepare assertions for semantic matching
# =====================================================================

def collect_lookup_requests(normalized_assertions):
    """
    Prepare assertion components for semantic resource matching.

    Literal objects are converted directly to RDF Literals.
    Explicit legal references are converted directly to custom URIs.
    Remaining resource components are queued for semantic matching.
    """

    lookup_requests = defaultdict(list)

    scored_assertions = copy.deepcopy(
        normalized_assertions
    )

    for idx, record in enumerate(normalized_assertions):

        assertion = record["assertion"]
        scored_assertion = (
            scored_assertions[idx]["assertion"]
        )

        # -------------------------------------------------------------
        # Subject
        # -------------------------------------------------------------

        subject = assertion["subject"]

        if is_legal_identifier_reference(subject):
            scored_assertion["subject"] = create_custom_uri(
                subject
            )
        else:
            lookup_requests["class"].append(
                {
                    "idx": idx,
                    "field": "subject",
                    "text": str(subject),
                }
            )

        # -------------------------------------------------------------
        # Object
        # -------------------------------------------------------------

        object_value = assertion["object"]

        if object_value is None:
            scored_assertion["object"] = None
            object_type = None

        else:
            object_type = detect_literal_type(
                object_value
            )

            if object_type == "class":

                if is_legal_identifier_reference(
                    object_value
                ):
                    scored_assertion["object"] = (
                        create_custom_uri(object_value)
                    )
                else:
                    lookup_requests["class"].append(
                        {
                            "idx": idx,
                            "field": "object",
                            "text": str(object_value),
                        }
                    )

            else:
                clean_value = str(object_value).strip()

                if object_type in {"date", "datetime"}:
                    value = normalize_date(
                        clean_value,
                        object_type,
                    )
                elif object_type == "integer":
                    value = int(clean_value)
                elif object_type == "decimal":
                    value = float(clean_value)
                else:
                    value = clean_value

                literal = Literal(
                    value,
                    datatype=TYPE_MAP[object_type],
                )

                if object_type == "date":
                    try:
                        rdflib.xsd_datetime.parse_xsd_date(
                            str(literal)
                        )
                    except Exception as exc:
                        raise ValueError(
                            f"Bad date literal at idx={idx}: "
                            f"raw={object_value!r} "
                            f"clean={clean_value!r} "
                            f"normalized={value!r}"
                        ) from exc

                scored_assertion["object"] = literal

        # -------------------------------------------------------------
        # Predicate
        # -------------------------------------------------------------

        predicate = assertion["predicate"]

        if predicate.casefold() == "type of":

            scored_assertion["predicate"] = RDF.type

        else:

            property_type = (
                "obj_prop"
                if object_type == "class"
                else "datatype_prop"
            )

            lookup_requests[property_type].append(
                {
                    "idx": idx,
                    "field": "predicate",
                    "text": str(predicate),
                }
            )

    return (
        scored_assertions,
        lookup_requests,
    )


# =====================================================================
# Semantic matching
# =====================================================================

def perform_semantic_lookups(
    lookup_requests,
    index_lookup,
    emb_model,
    top_k=3,
    batch_size=128,
):
    """
    Perform batched semantic searches against temporary
    ontology resource indices.
    """

    lookup_results = {}
    polarity_cache = {}

    for resource_type, requests in lookup_requests.items():

        if not requests:
            continue

        if resource_type not in index_lookup:
            continue

        texts = [
            request["text"]
            for request in requests
        ]

        embeddings = emb_model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        index, uris, labels = (
            index_lookup[resource_type]
        )

        scores, indices = index.search(
            embeddings,
            top_k,
        )

        for request, score_row, idx_row in zip(
            requests,
            scores,
            indices,
        ):

            candidates = [
                (
                    labels[i],
                    uris[i],
                    float(score_row[j]),
                )
                for j, i in enumerate(idx_row)
                if i >= 0
            ]

            # ---------------------------------------------------------
            # Predicate polarity filtering
            # ---------------------------------------------------------

            if request["field"] == "predicate":

                query_text = request["text"]

                if query_text not in polarity_cache:
                    polarity_cache[query_text] = (
                        extract_polarity(query_text)
                    )

                query_polarity = polarity_cache[
                    query_text
                ]

                filtered_candidates = []

                for candidate in candidates:

                    candidate_label = candidate[0]

                    if candidate_label not in polarity_cache:
                        polarity_cache[candidate_label] = (
                            extract_polarity(
                                candidate_label
                            )
                        )

                    if (
                        polarity_cache[candidate_label]
                        == query_polarity
                    ):
                        filtered_candidates.append(
                            candidate
                        )

                if filtered_candidates:
                    candidates = filtered_candidates

            lookup_results[
                (
                    request["idx"],
                    request["field"],
                    request["text"],
                )
            ] = candidates

    return lookup_results


# =====================================================================
# Apply semantic matches
# =====================================================================

def apply_resource_matches(
    scored_assertions,
    lookup_results,
    threshold=0.7,
):
    """
    Replace unresolved assertion components with matched
    ontology URIs or Jurisynth custom URIs.
    """

    for (
        idx,
        field,
        text,
    ), candidates in lookup_results.items():

        scored_assertion = (
            scored_assertions[idx]["assertion"]
        )

        if not candidates:
            scored_assertion[field] = (
                create_custom_uri(text)
            )
            continue

        _, best_uri, best_score = candidates[0]

        if best_score >= threshold:
            scored_assertion[field] = URIRef(
                best_uri
            )
        else:
            scored_assertion[field] = (
                create_custom_uri(text)
            )

    return scored_assertions


# =====================================================================
# Main module function
# =====================================================================

def match_assertions(
    normalized_assertions,
    classes,
    obj_properties,
    datatype_properties,
    resource_metadata,
    emb_model=None,
    threshold=SEMANTIC_THRESHOLD,
    top_k=SEMANTIC_TOP_K,
    batch_size=SEMANTIC_BATCH_SIZE,
):
    """
    Semantically match normalized assertions against ontology resources.

    The embedding model defaults to all-MiniLM-L6-v2.

    FAISS indices are temporary and are explicitly released after
    semantic matching because they are not required downstream.

    Returns
    -------
    list[dict]
        Assertions whose resolvable components have been replaced
        with ontology URIs or stable Jurisynth custom URIs.
    """

    if emb_model is None:
        emb_model = SentenceTransformer(
            SEMANTIC_EMBED_MODEL
        )

    resources = {
        "class": classes,
        "obj_prop": obj_properties,
        "datatype_prop": datatype_properties,
    }

    # -------------------------------------------------------------
    # Build temporary resource indices
    # -------------------------------------------------------------

    index_lookup = build_resource_indices(
        resources,
        resource_metadata,
        emb_model,
    )

    try:
        # ---------------------------------------------------------
        # Prepare assertions
        # ---------------------------------------------------------

        scored_assertions, lookup_requests = (
            collect_lookup_requests(
                normalized_assertions
            )
        )

        # ---------------------------------------------------------
        # Perform semantic matching
        # ---------------------------------------------------------

        lookup_results = perform_semantic_lookups(
            lookup_requests,
            index_lookup,
            emb_model,
            top_k=top_k,
            batch_size=batch_size,
        )

        # ---------------------------------------------------------
        # Apply best matches
        # ---------------------------------------------------------

        scored_assertions = apply_resource_matches(
            scored_assertions,
            lookup_results,
            threshold=threshold,
        )

        return scored_assertions

    finally:
        # ---------------------------------------------------------
        # FAISS indices are module-local temporary state.
        # They are not needed by downstream modules.
        # ---------------------------------------------------------

        del index_lookup
        gc.collect()