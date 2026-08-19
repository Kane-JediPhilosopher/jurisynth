import spacy
import re
from itertools import product

nlp = spacy.load(
    "en_core_web_sm",
    disable=["ner"]
)

# ---------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------

def normalize_entity(text: str) -> str:
    """
    Conservative cleanup of entity names.
    Preserves legal wording.
    """

    text = text.strip()

    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove trailing punctuation
    text = text.rstrip(".,;:")

    return text


def normalize_predicate(text: str) -> str:
    """
    Cleanup and canonicalize predicate phrases.
    """

    text = re.sub(r"\s+", " ", text.strip())

    replacements = {
        "is obliged to": "obligated to",
        "is required to": "required to",
        "is subject to": "subject to",
        "is entitled to": "entitled to",
    }

    lower = text.lower()

    for old, new in replacements.items():
        if lower.startswith(old):
            text = new + text[len(old):]
            break

    return text


# ---------------------------------------------------------------------
# Legal reference splitting
# ---------------------------------------------------------------------

def split_legal_reference(text: str):

    pattern = (
        r"\s+(?:and|or)\s+"
        r"(?=(?:article|paragraph|point|section|annex)\b)"
    )

    parts = re.split(
        pattern,
        text,
        flags=re.IGNORECASE
    )

    if len(parts) > 1:
        return [
            part.strip()
            for part in parts
        ]

    return None


# ---------------------------------------------------------------------
# Cheap composite detection heuristic
# ---------------------------------------------------------------------

def should_attempt_split(text: str):
    """
    Avoid unnecessary spaCy parsing.

    Only attempt NLP splitting when the text
    contains likely coordination markers.
    """

    indicators = [
        " and ",
        " or ",
        ",",
        "Article ",
        "Paragraph ",
        "Point ",
        "Section ",
        "Annex "
    ]

    text_lower = text.lower()

    return any(
        indicator.lower() in text_lower
        for indicator in indicators
    )


# ---------------------------------------------------------------------
# Composite entity detection
# ---------------------------------------------------------------------

def split_entity(text: str):
    """
    Returns:
        None              -> no safe expansion
        list[str]         -> safe expansion
    """

    # First handle explicit legal references
    legal_split = split_legal_reference(text)

    if legal_split:
        return legal_split

    # Skip expensive NLP when unlikely to be composite
    if not should_attempt_split(text):
        return None

    # Fall back to dependency parsing
    doc = nlp(text)

    # Require coordination
    if not any(
        tok.dep_ == "conj"
        for tok in doc
    ):
        return None

    # Avoid complex clauses
    if any(
        tok.dep_ in {
            "relcl",
            "advcl",
            "ccomp",
            "xcomp"
        }
        for tok in doc
    ):
        return None

    noun_chunks = list(doc.noun_chunks)

    if len(noun_chunks) < 2:
        return None

    entities = [
        chunk.text.strip()
        for chunk in noun_chunks
    ]

    entities = list(dict.fromkeys(entities))

    return (
        entities
        if len(entities) > 1
        else None
    )


# ---------------------------------------------------------------------
# Triple expansion
# ---------------------------------------------------------------------

def expand_triple(triple: dict):

    subject = normalize_entity(triple["subject"])
    predicate = normalize_predicate(triple["predicate"])
    object = normalize_entity(triple["object"])

    subjects = (split_entity(subject) or [subject])
    objects = (split_entity(object) or [object])

    expanded = list()

    # Avoid unnecessary Cartesian expansion
    if (
        len(subjects) == len(objects)
        and len(subjects) > 1
    ):
        pairs = zip(subjects, objects)

    else:
        pairs = product(subjects, objects)

    for s, o in pairs:
        expanded.append({
            "subject": s,
            "predicate": predicate,
            "object": o
            })

    return expanded


# ---------------------------------------------------------------------
# Batch normalization
# ---------------------------------------------------------------------

def normalize_triples(extracted_triples):
    """
    Normalize and expand extracted triples.

    Input:
        [
            {
                "doc_id": ...,
                "chunk_id": ...,
                "triples": [...]
            },
            ...
        ]

    Output:
        [
            {
                "doc_id": ...,
                "chunk_id": ...,
                "triple": {...}
            },
            ...
        ]
    """

    normalized = list()

    required_fields = {
        "subject",
        "predicate",
        "object"
    }

    for chunk in extracted_triples:

        doc_id = chunk["doc_id"]
        chunk_id = chunk["chunk_id"]

        for triple in chunk["triples"]:

            # Skip malformed triples
            if not isinstance(triple, dict):
                continue

            if not required_fields.issubset(triple):
                continue

            expanded = expand_triple(triple)

            for tr in expanded:

                normalized.append(
                    {
                        "doc_id": doc_id,
                        "chunk_id": chunk_id,
                        "triple_id": len(normalized),
                        "triple": tr
                    }
                )

    return normalized