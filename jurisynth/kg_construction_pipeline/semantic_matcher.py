import re
import unicodedata
import datetime import datetime

import faiss
from spacy import nlp
from rdflib import RDF, URIRef, Literal
from rdflib.namespace import XSD

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

    # Common EU/legal formats
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%d.%m.%Y",

    # Written dates
    "%d %B %Y",
    "%d %b %Y",
]

DATETIME_FORMATS = [
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S%z",

    # ISO with fractional seconds
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%dT%H:%M:%S.%f%z",
]

LEGAL_IDENTIFIER_PATTERNS = [

    # Article / paragraph references
    r"\b(article|art\.?)\s*\d+(\s*\([a-z0-9]+\))?",

    # EU legal acts with numbers
    # Regulation No 1395/69
    # Decision 68/302/EEC
    # Directive 2006/123/EC
    r"\b(regulation|directive|decision|recommendation|opinion)"
    r".*\b(no\.?|number)?\s*\d+[-/]\d+",

    # EU identifiers:
    # 2006/123/EC
    # 68/302/EEC
    r"\b\d{1,4}/\d{1,4}/[a-z]{2,5}\b",

    # CELEX-like identifiers
    r"\b\d{5}[A-Z]\d{4}\b",
]

NEGATION_WORDS = {
    "not",
    "no",
    "never",
    "without",
    "neither",
    "nor",
    "n't"
}


def build_resource_lookup(resources, resource_metadata, embedding_model):
    index_lookup = dict()

    for resource_type, resource_dict in resources.items():
        texts = [
            resource_metadata[uri]["text"]
            for uri in resource_dict.keys()
        ]
        
        uris = list(resource_dict.keys())

        embeddings = embedding_model.encode(
            texts,
            normalize_embeddings=True
        )

        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)

        index_lookup[resource_type] = (index, uris, texts)

    return index_lookup


# Cleans documents
def clean_text(text: str) -> str:
    if not text:
        return text

    # 1. Normalize Unicode (fixes odd composed characters)
    text = unicodedata.normalize("NFKC", text)

    # 2. Replace the following:
    replacements = {
        "\u00A0": " ",  # NBSP
        "\u202F": " ",  # narrow NBSP
        "\u202f": " ",  # narrow NBSP
        "\u2009": " ",  # thin space
        "\u2007": " ",  # figure space
        "\x00": "",     # null bytes
        "\ufffd": ""    # Unicode replacement char
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    # 4. Remove control characters (but keep newlines/tabs)
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", text)

    return text


def detect_literal_type(value: str):

    v = clean_text(str(value)).strip()

    # boolean
    if v.lower() in {"true", "false"}:
        return "boolean"
    # integer
    if re.fullmatch(r"-?\d+", v):
        return "integer"
    # decimal
    if re.fullmatch(r"-?\d+\.\d+", v):
        return "decimal"

    # datetime
    for fmt in DATETIME_FORMATS:
        try:
            datetime.strptime(v, fmt)
            return "datetime"
        except ValueError:
            pass

    # date
    for fmt in DATE_FORMATS:
        try:
            datetime.strptime(v, fmt)
            return "date"
        except ValueError:
            pass

    return "class"


def normalize_date(value: str, literal_type: str):
    # value is expected to already be cleaned by the caller
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
    """
    Detect whether a label contains a likely legal identifier.

    This is a heuristic filter only.
    """

    text = text.casefold()

    for pattern in LEGAL_IDENTIFIER_PATTERNS:
        if re.search(pattern, text):
            return True

    return False

def extract_polarity_doc(doc):
    """
    Returns True for affirmative predicates,
    False for explicitly negative predicates.

    Designed for short ontology labels rather than
    full natural-language sentences.
    """

    for token in doc:
        if token.lower_ in NEGATION_WORDS:
            return False

    return True

def extract_polarity(text):
    """Convenience wrapper when a Doc is unavailable."""

    return extract_polarity_doc(nlp.make_doc(text))

def create_custom_uri(text: str, prefix):
    """
    Generate a stable URI for unresolved components.

    Applies conservative normalization only.
    """

    text = text.casefold()

    # Unicode normalization
    text = unicodedata.normalize("NFKC", text)

    # Replace whitespace with underscores
    text = re.sub(r"\s+", "_", text)

    # Remove unsafe URI characters
    text = re.sub(r"[^a-z0-9_\-]", "", text)

    return URIRef(prefix[text])


# --------------------------------------------------
# 1. Collect lookup requests
# --------------------------------------------------

lookup_requests = defaultdict(list)
scored_triples = copy.deepcopy(normalized_triples)

for idx, triple in enumerate(normalized_triples):
    triple = normalized_triples[idx]["triple"]
    scored_triple = scored_triples[idx]["triple"]

    # Subject -> always class lookup for now
    if is_legal_identifier_reference(triple["subject"]):
        scored_triple["subject"] = create_custom_uri(triple["subject"])

    else:
        lookup_requests["class"].append({
            "idx": idx,
            "field": "subject",
            "text": str(triple["subject"])
        })

    # Object
    object_type = detect_literal_type(triple["object"])

    if object_type == "class":

        if is_legal_identifier_reference(triple["object"]):
            scored_triple["object"] = create_custom_uri(triple["object"])
        
        else:
            lookup_requests["class"].append({
                "idx": idx,
                "field": "object",
                "text": str(triple["object"])
            })


    else:
        clean_value = clean_text(str(triple["object"])).strip()

        if object_type in {"date", "datetime"}:
            value = normalize_date(clean_value, object_type)
        elif object_type == "integer":
            value = int(clean_value)
        elif object_type == "decimal":
            value = float(clean_value)
        else:
            value = scored_triple["object"]

        lit = Literal(value, datatype=TYPE_MAP[object_type])

        if object_type == "date":
            try:
                rdflib.xsd_datetime.parse_xsd_date(str(lit))
            except Exception as e:
                raise ValueError(
                    f"Bad date literal at idx={idx}: raw={triple['object']!r} "
                    f"clean={clean_value!r} normalized={value!r}"
                ) from e

        scored_triple["object"] = lit

    # Predicate
    if triple["predicate"] == "type of":
        scored_triple["predicate"] = RDF.type

    else:
        prop_type = (
            "obj_prop"
            if object_type == "class"
            else "datatype_prop"
        )

        lookup_requests[prop_type].append({
            "idx": idx,
            "field": "predicate",
            "text": str(triple["predicate"])
        })


# --------------------------------------------------
# 2. Batch semantic lookup
# --------------------------------------------------

lookup_results = dict()

# Cache polarity across all predicate lookups
polarity_cache = dict()

for resource_type, requests in lookup_requests.items():

    texts = [
        r["text"]
        for r in requests
    ]

    # --------------------------------------------------
    # Sentence embeddings
    # --------------------------------------------------

    embeddings = emb_model.encode(
        texts,
        batch_size=128,
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    index, uris, labels = index_lookup[resource_type]

    scores, indices = index.search(embeddings, 3)

    # --------------------------------------------------
    # Candidate construction
    # --------------------------------------------------

    for req, score_row, idx_row in zip(
        requests,
        scores,
        indices
    ):

        candidates = [
            (
                labels[i],
                uris[i],
                float(score_row[j])
            )
            for j, i in enumerate(idx_row)
        ]


        # --------------------------------------------------
        # Predicate polarity filtering
        # --------------------------------------------------

        if req["field"] == "predicate":
            query_text = req["text"]

            if query_text not in polarity_cache:

                polarity_cache[query_text] = extract_polarity(
                    query_text
                )

            query_polarity = polarity_cache[query_text]
            filtered_candidates = list()

            for candidate in candidates:
                candidate_label = candidate[0]

                if candidate_label not in polarity_cache:

                    polarity_cache[candidate_label] = extract_polarity(
                        candidate_label
                    )

                if (
                    polarity_cache[candidate_label]
                    == query_polarity
                ):
                    filtered_candidates.append(candidate)

            # Only apply filtering if at least one candidate survives
            if filtered_candidates:
                candidates = filtered_candidates

        lookup_results[
            (
                req["idx"],
                req["field"],
                req["text"]
            )
        ] = candidates


# --------------------------------------------------
# 3. Resource Matching/Filtering
# --------------------------------------------------

custom_resources = dict()

THRESHOLD = 0.7

for (idx, field, text), candidates in lookup_results.items():

    scored_triple = scored_triples[idx]["triple"]

    best = candidates[0]
    score = best[2]

    if score >= THRESHOLD:
        # High-confidence semantic match
        scored_triple[field] = URIRef(best[1])

    else:
        # Assign custom URI
        custom_uri = create_custom_uri(text)
        scored_triple[field] = custom_uri
        custom_resources.setdefault(
            custom_uri,
            {
                "text": text,
                "field": field,
                "candidates": candidates
            }
        )