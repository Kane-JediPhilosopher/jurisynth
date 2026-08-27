import pytest
import rdflib
from rdflib import Literal, URIRef
from rdflib.namespace import RDF, XSD

from semantic_matcher import (
    detect_literal_type,
    normalize_date,
    is_legal_identifier_reference,
    collect_lookup_requests,
    perform_semantic_lookups,
    apply_resource_matches,
    create_custom_uri,
)


# =====================================================================
# Helpers
# =====================================================================

class FakeEmbeddingModel:
    """
    Minimal deterministic embedding model for unit tests.

    Each text is represented by a simple vector. The actual semantic
    quality of embeddings is not under test here; FAISS/indexing and
    downstream matching behavior are.
    """

    def encode(
        self,
        texts,
        batch_size=128,
        normalize_embeddings=True,
        convert_to_numpy=True,
    ):
        import numpy as np

        vectors = []

        for text in texts:
            text = str(text).lower()

            if "animal" in text:
                vectors.append([1.0, 0.0, 0.0, 0.0])
            elif "has value" in text:
                vectors.append([0.0, 1.0, 0.0, 0.0])
            elif "submit" in text:
                vectors.append([0.0, 0.0, 1.0, 0.0])
            elif "prohibit" in text or "forbid" in text:
                vectors.append([0.0, 0.0, 0.0, 1.0])
            else:
                vectors.append([0.0, 0.0, 0.0, 0.0])

        return np.asarray(vectors, dtype="float32")


# =====================================================================
# Literal handling
# =====================================================================

@pytest.mark.parametrize(
    "value, expected",
    [
        ("true", "boolean"),
        ("FALSE", "boolean"),
        ("42", "integer"),
        ("-17", "integer"),
        ("3.14", "decimal"),
        ("-0.5", "decimal"),
        ("2025-01-31", "date"),
        ("31/01/2025", "date"),
        ("2025-01-31T12:30:00", "datetime"),
        ("ordinary text", "class"),
    ],
)
def test_detect_literal_type(value, expected):
    assert detect_literal_type(value) == expected


@pytest.mark.parametrize(
    "value, literal_type, expected",
    [
        ("31/01/2025", "date", "2025-01-31"),
        ("31 January 2025", "date", "2025-01-31"),
        (
            "2025-01-31T12:30:00",
            "datetime",
            "2025-01-31T12:30:00",
        ),
    ],
)
def test_normalize_date(value, literal_type, expected):
    assert normalize_date(value, literal_type) == expected


# =====================================================================
# Legal-reference handling
# =====================================================================

@pytest.mark.parametrize(
    "text",
    [
        "Article 12",
        "Art. 5(2)",
        "Regulation No. 123/2024",
        "Directive 2019/123",
    ],
)
def test_legal_identifier_is_detected(text):
    assert is_legal_identifier_reference(text)


def test_non_legal_text_is_not_treated_as_identifier():
    assert not is_legal_identifier_reference(
        "undertaking established within the territory"
    )


# =====================================================================
# Assertion preparation
# =====================================================================

def test_objectless_assertion_is_preserved():
    assertions = [
        {
            "doc_id": "doc1",
            "chunk_id": "chunk1",
            "assertion": {
                "subject": "authorisation",
                "predicate": "may be withdrawn",
                "object": None,
            },
            "modifiers": [],
        }
    ]

    scored, requests = collect_lookup_requests(assertions)

    assert scored[0]["assertion"]["object"] is None

    # Subject and predicate still require semantic matching.
    assert len(requests["class"]) == 1
    assert len(requests["datatype_prop"]) == 1


def test_type_of_predicate_maps_to_rdf_type():
    assertions = [
        {
            "doc_id": "doc1",
            "chunk_id": "chunk1",
            "assertion": {
                "subject": "animal",
                "predicate": "type of",
                "object": "Cervid",
            },
            "modifiers": [],
        }
    ]

    scored, requests = collect_lookup_requests(assertions)

    assert scored[0]["assertion"]["predicate"] == RDF.type

    predicate_requests = requests["datatype_prop"]
    assert predicate_requests == []


def test_collect_lookup_requests_separates_literals_and_resources():
    assertions = [
        {
            "doc_id": "doc1",
            "chunk_id": "chunk1",
            "assertion": {
                "subject": "undertaking",
                "predicate": "has value",
                "object": "42",
            },
            "modifiers": [],
        }
    ]

    scored, requests = collect_lookup_requests(assertions)

    object_value = scored[0]["assertion"]["object"]

    assert isinstance(object_value, Literal)
    assert object_value.datatype == XSD.integer
    assert int(object_value) == 42

    assert len(requests["class"]) == 1
    assert requests["class"][0]["field"] == "subject"

    assert len(requests["datatype_prop"]) == 1
    assert requests["datatype_prop"][0]["field"] == "predicate"


def test_legal_reference_bypasses_semantic_matching():
    assertions = [
        {
            "doc_id": "doc1",
            "chunk_id": "chunk1",
            "assertion": {
                "subject": "Article 12",
                "predicate": "applies to",
                "object": None,
            },
            "modifiers": [],
        }
    ]

    scored, requests = collect_lookup_requests(assertions)

    assert scored[0]["assertion"]["subject"] == create_custom_uri(
        "Article 12"
    )

    assert not any(
        request["field"] == "subject"
        for requests_for_type in requests.values()
        for request in requests_for_type
    )


# =====================================================================
# Semantic lookup behavior
# =====================================================================

def test_predicate_polarity_filtering():
    """
    Negative queries should not retain candidates whose labels express
    the opposite polarity.
    """

    fake_index = None

    # We test the filtering logic with a deliberately tiny fake index.
    class FakeIndex:
        def search(self, embeddings, top_k):
            import numpy as np

            return (
                np.asarray([[0.95, 0.90]], dtype="float32"),
                np.asarray([[0, 1]], dtype="int64"),
            )

    index_lookup = {
        "datatype_prop": (
            FakeIndex(),
            [
                URIRef("http://example.org/shall_submit"),
                URIRef("http://example.org/shall_not_submit"),
            ],
            [
                "shall submit",
                "shall not submit",
            ],
        )
    }

    requests = {
        "datatype_prop": [
            {
                "idx": 0,
                "field": "predicate",
                "text": "shall submit",
            }
        ]
    }

    results = perform_semantic_lookups(
        requests,
        index_lookup,
        FakeEmbeddingModel(),
        top_k=2,
    )

    candidates = results[(0, "predicate", "shall submit")]

    assert all(
        "not" not in candidate[0].lower()
        for candidate in candidates
    )


def test_predicate_polarity_filtering_rejects_all_opposite_candidates():
    class FakeIndex:
        def search(self, embeddings, top_k):
            import numpy as np

            return (
                np.asarray([[0.95, 0.90]], dtype="float32"),
                np.asarray([[0, 1]], dtype="int64"),
            )

    index_lookup = {
        "datatype_prop": (
            FakeIndex(),
            [
                URIRef("http://example.org/shall_submit"),
                URIRef("http://example.org/shall_provide"),
            ],
            [
                "shall submit",
                "shall provide",
            ],
        )
    }

    requests = {
        "datatype_prop": [
            {
                "idx": 0,
                "field": "predicate",
                "text": "shall not submit",
            }
        ]
    }

    results = perform_semantic_lookups(
        requests,
        index_lookup,
        FakeEmbeddingModel(),
        top_k=2,
    )

    candidates = results[(0, "predicate", "shall not submit")]

    assert candidates == []


# =====================================================================
# Applying matches
# =====================================================================

def test_high_confidence_match_uses_ontology_uri():
    ontology_uri = URIRef(
        "http://example.org/Animal"
    )

    scored = [
        {
            "assertion": {
                "subject": "animal",
                "predicate": "is",
                "object": None,
            }
        }
    ]

    lookup_results = {
        (0, "subject", "animal"): [
            (
                "Animal",
                ontology_uri,
                0.91,
            )
        ]
    }

    result = apply_resource_matches(
        scored,
        lookup_results,
        threshold=0.7,
    )

    assert result[0]["assertion"]["subject"] == ontology_uri


def test_low_confidence_match_uses_custom_uri():
    ontology_uri = URIRef(
        "http://example.org/Animal"
    )

    scored = [
        {
            "assertion": {
                "subject": "unusual animal",
                "predicate": "is",
                "object": None,
            }
        }
    ]

    lookup_results = {
        (0, "subject", "unusual animal"): [
            (
                "Animal",
                ontology_uri,
                0.42,
            )
        ]
    }

    result = apply_resource_matches(
        scored,
        lookup_results,
        threshold=0.7,
    )

    expected = create_custom_uri("unusual animal")

    assert result[0]["assertion"]["subject"] == expected
    assert result[0]["assertion"]["subject"] != ontology_uri


def test_no_candidates_uses_custom_uri():
    scored = [
        {
            "assertion": {
                "subject": "unknown concept",
                "predicate": "is",
                "object": None,
            }
        }
    ]

    lookup_results = {
        (0, "subject", "unknown concept"): []
    }

    result = apply_resource_matches(
        scored,
        lookup_results,
        threshold=0.7,
    )

    assert result[0]["assertion"]["subject"] == (
        create_custom_uri("unknown concept")
    )


def test_resource_object_uses_object_property_lookup():
    assertions = [
        {
            "doc_id": "doc1",
            "chunk_id": "chunk1",
            "assertion": {
                "subject": "undertaking",
                "predicate": "established in",
                "object": "territory",
            },
            "modifiers": [],
        }
    ]

    scored, requests = collect_lookup_requests(assertions)

    assert len(requests["class"]) == 2
    assert len(requests["obj_prop"]) == 1
    assert requests["obj_prop"][0]["field"] == "predicate"
    assert requests["obj_prop"][0]["text"] == "established in"
    assert requests["datatype_prop"] == []
    

# =====================================================================
# End-to-end semantic matching
# =====================================================================

def test_match_assertions_end_to_end():
    """
    Exercise the complete matching pipeline using a fake embedding model.

    This verifies:
        assertion preparation
        -> semantic lookup
        -> threshold application
        -> final URI replacement
    """

    from semantic_matcher import match_assertions

    classes = {
        URIRef("http://example.org/Animal"): {},
    }

    datatype_properties = {
        URIRef("http://example.org/has_value"): {},
    }

    obj_properties = {}

    resource_metadata = {
        URIRef("http://example.org/Animal"): {
            "text": "animal",
        },
        URIRef("http://example.org/has_value"): {
            "text": "has value",
        },
    }

    assertions = [
        {
            "doc_id": "doc1",
            "chunk_id": "chunk1",
            "assertion_id": 0,
            "assertion": {
                "subject": "animal",
                "predicate": "has value",
                "object": "42",
            },
            "modifiers": [],
        }
    ]

    result = match_assertions(
        assertions,
        classes,
        obj_properties,
        datatype_properties,
        resource_metadata,
        emb_model=FakeEmbeddingModel(),
        threshold=0.7,
        top_k=1,
    )

    assertion = result[0]["assertion"]

    assert assertion["subject"] == (
        URIRef("http://example.org/Animal")
    )

    assert assertion["predicate"] == (
        URIRef("http://example.org/has_value")
    )

    assert isinstance(assertion["object"], Literal)
    assert assertion["object"].datatype == XSD.integer
    assert int(assertion["object"]) == 42