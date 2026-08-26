import re
from itertools import product

import spacy


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

NLP_MODEL = "en_core_web_sm"

nlp = spacy.load(
    NLP_MODEL,
    disable=["ner"],
)


# ---------------------------------------------------------------------
# Text normalization
# ---------------------------------------------------------------------

def normalize_entity(text: str) -> str:
    """Conservatively clean an entity while preserving legal wording."""
    text = re.sub(r"\s+", " ", text.strip())
    return text.rstrip(".,;:")


def normalize_predicate(text: str) -> str:
    """Clean and canonicalize common predicate formulations."""
    text = re.sub(r"\s+", " ", text.strip())

    replacements = {
        "is obliged to": "obligated to",
        "is required to": "required to",
        "is subject to": "subject to",
        "is entitled to": "entitled to",
    }

    lowered = text.lower()

    for old, new in replacements.items():
        if lowered.startswith(old):
            text = new + text[len(old):]
            break

    return text


# ---------------------------------------------------------------------
# Composite entity detection
# ---------------------------------------------------------------------

def split_legal_reference(text: str) -> list[str] | None:
    """Split explicitly coordinated legal references."""
    pattern = (
        r"\s+(?:and|or)\s+"
        r"(?=(?:article|paragraph|point|section|annex)\b)"
    )

    parts = re.split(
        pattern,
        text,
        flags=re.IGNORECASE,
    )

    if len(parts) <= 1:
        return None

    return [part.strip() for part in parts]


def should_attempt_split(text: str) -> bool:
    """Cheap heuristic to avoid unnecessary dependency parsing."""
    indicators = (
        " and ",
        " or ",
        ",",
        "article ",
        "paragraph ",
        "point ",
        "section ",
        "annex ",
    )

    lowered = text.lower()
    return any(indicator in lowered for indicator in indicators)


def split_entity(text: str) -> list[str] | None:
    """
    Return safely separable components of a coordinated entity.

    Returns None when no sufficiently safe expansion is detected.
    """
    legal_split = split_legal_reference(text)

    if legal_split:
        return legal_split

    if not should_attempt_split(text):
        return None

    doc = nlp(text)

    if not any(token.dep_ == "conj" for token in doc):
        return None

    # Avoid attempting to expand syntactically complex clauses.
    complex_dependencies = {
        "relcl",
        "advcl",
        "ccomp",
        "xcomp",
    }

    if any(
        token.dep_ in complex_dependencies
        for token in doc
    ):
        return None

    noun_chunks = list(doc.noun_chunks)

    if len(noun_chunks) < 2:
        return None

    entities = list(
        dict.fromkeys(
            chunk.text.strip()
            for chunk in noun_chunks
        )
    )

    return entities if len(entities) > 1 else None


# ---------------------------------------------------------------------
# Assertion expansion
# ---------------------------------------------------------------------

def expand_assertion(assertion: dict) -> list[dict]:
    """Normalize and safely expand coordinated subjects and objects."""
    subject = normalize_entity(assertion["subject"])
    predicate = normalize_predicate(assertion["predicate"])

    object_value = assertion["object"]

    # Object may legitimately be null for objectless assertions.
    if object_value is None:
        objects = [None]
    else:
        object_value = normalize_entity(object_value)
        objects = split_entity(object_value) or [object_value]

    subjects = split_entity(subject) or [subject]

    if len(subjects) == len(objects) and len(subjects) > 1:
        pairs = zip(subjects, objects)
    else:
        pairs = product(subjects, objects)

    return [
        {
            "subject": subject,
            "predicate": predicate,
            "object": object_value,
        }
        for subject, object_value in pairs
    ]


# ---------------------------------------------------------------------
# Batch normalization
# ---------------------------------------------------------------------

def normalize_assertions(
    extracted_chunks: list[dict],
) -> list[dict]:
    """
    Normalize and expand extracted assertions.

    Expected input:
        [
            {
                "doc_id": str,
                "chunk_id": str,
                "assertions": [
                    {
                        "assertion": {
                            "subject": str,
                            "predicate": str,
                            "object": str | None,
                        },
                        "modifiers": list[str],
                    },
                    ...
                ],
            },
            ...
        ]

    Returns:
        Flat list of normalized assertions.
    """
    normalized = []

    for chunk in extracted_chunks:
        doc_id = chunk["doc_id"]
        chunk_id = chunk["chunk_id"]

        for extracted in chunk.get("assertions", []):
            assertion = extracted.get("assertion")
            modifiers = extracted.get("modifiers", [])

            if not isinstance(assertion, dict):
                continue

            required_fields = {
                "subject",
                "predicate",
                "object",
            }

            if not required_fields.issubset(assertion):
                continue

            for expanded in expand_assertion(assertion):
                normalized.append(
                    {
                        "doc_id": doc_id,
                        "chunk_id": chunk_id,
                        "assertion_id": len(normalized),
                        "assertion": expanded,
                        "modifiers": list(modifiers),
                    }
                )

    return normalized