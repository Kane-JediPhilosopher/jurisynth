import pytest

from assertion_normalizer import (
    normalize_entity,
    normalize_predicate,
    split_legal_reference,
    split_entity,
    expand_assertion,
    normalize_assertions,
)


# =============================================================================
# T01 — Entity normalization
# =============================================================================

def test_entity_normalization():
    """
    Entity whitespace should be collapsed and trailing punctuation removed,
    while the substantive legal wording remains unchanged.
    """

    result = normalize_entity(
        "  undertaking   established within the territory.  "
    )

    assert result == (
        "undertaking established within the territory"
    )


# =============================================================================
# T02 — Predicate normalization
# =============================================================================

@pytest.mark.parametrize(
    ("predicate", "expected"),
    [
        (
            "is obliged to maintain",
            "obligated to maintain",
        ),
        (
            "is required to submit",
            "required to submit",
        ),
        (
            "is subject to authorisation",
            "subject to authorisation",
        ),
        (
            "is entitled to receive",
            "entitled to receive",
        ),
    ],
)
def test_predicate_normalization(predicate, expected):
    """
    Common predicate formulations should be canonicalized without changing
    the remainder of the predicate.
    """

    assert normalize_predicate(predicate) == expected


# =============================================================================
# T03 — Objectless assertion
# =============================================================================

def test_objectless_assertion_is_preserved():
    """
    Objectless assertions should retain object=None.
    """

    assertion = {
        "subject": "The register",
        "predicate": "shall be maintained",
        "object": None,
    }

    result = expand_assertion(assertion)

    assert result == [
        {
            "subject": "The register",
            "predicate": "shall be maintained",
            "object": None,
        }
    ]


# =============================================================================
# T04 — Coordinated subject expansion
# =============================================================================

def test_coordinated_subject_is_expanded():
    """
    A coordinated subject should be expanded into separate assertions.
    """

    assertion = {
        "subject": "the authority and the applicant",
        "predicate": "shall cooperate",
        "object": None,
    }

    result = expand_assertion(assertion)

    assert len(result) == 2

    assert result[0]["subject"] == "the authority"
    assert result[1]["subject"] == "the applicant"

    assert all(
        item["predicate"] == "shall cooperate"
        for item in result
    )

    assert all(
        item["object"] is None
        for item in result
    )


# =============================================================================
# T05 — Coordinated object expansion
# =============================================================================

def test_coordinated_object_is_expanded():
    """
    A coordinated object should be expanded into separate assertions.
    """

    assertion = {
        "subject": "the authority",
        "predicate": "shall verify",
        "object": "the application and the supporting documents",
    }

    result = expand_assertion(assertion)

    assert len(result) == 2

    assert result[0]["object"] == "the application"
    assert result[1]["object"] == "the supporting documents"

    assert all(
        item["subject"] == "the authority"
        for item in result
    )


# =============================================================================
# T06 — Paired subject/object expansion
# =============================================================================

def test_equal_length_subject_and_object_lists_are_paired():
    """
    When coordinated subjects and objects have equal length, they should be
    paired positionally rather than expanded as a Cartesian product.
    """

    assertion = {
        "subject": "authority and applicant",
        "predicate": "shall notify",
        "object": "Commission and Council",
    }

    result = expand_assertion(assertion)

    assert len(result) == 2

    assert result[0] == {
        "subject": "authority",
        "predicate": "shall notify",
        "object": "Commission",
    }

    assert result[1] == {
        "subject": "applicant",
        "predicate": "shall notify",
        "object": "Council",
    }


# =============================================================================
# T07 — Complex entity protection
# =============================================================================

def test_complex_entity_is_not_aggressively_split():
    """
    Entities containing relative clauses should not be incorrectly expanded
    merely because they contain conjunctions or other syntactic complexity.
    """

    text = (
        "undertakings established within the territory and operating "
        "under the applicable authorisation"
    )

    result = split_entity(text)

    assert result is None


# =============================================================================
# T08 — Legal reference splitting
# =============================================================================

def test_coordinated_legal_references_are_split():
    """
    Explicitly coordinated legal references should be separated safely.
    """

    text = (
        "Article 5 and Article 7 and Article 9"
    )

    result = split_legal_reference(text)

    assert result == [
        "Article 5",
        "Article 7",
        "Article 9",
    ]


# =============================================================================
# T09 — Malformed assertion handling
# =============================================================================

def test_malformed_assertion_is_skipped():
    """
    An extracted assertion missing required fields should be skipped rather
    than causing normalization to fail.
    """

    extracted_chunks = [
        {
            "doc_id": "doc_001",
            "chunk_id": "chunk_001",
            "assertions": [
                {
                    "assertion": {
                        "subject": "authority",
                        "predicate": "shall verify",
                        # Missing "object"
                    },
                    "modifiers": [],
                },
                {
                    "assertion": {
                        "subject": "applicant",
                        "predicate": "must provide",
                        "object": "information",
                    },
                    "modifiers": [],
                },
            ],
        }
    ]

    result = normalize_assertions(extracted_chunks)

    assert len(result) == 1

    assert result[0]["assertion"] == {
        "subject": "applicant",
        "predicate": "must provide",
        "object": "information",
    }


# =============================================================================
# T10 — Metadata and modifiers are preserved
# =============================================================================

def test_metadata_and_modifiers_are_preserved():
    """
    Document/chunk metadata and assertion modifiers should survive
    normalization.
    """

    extracted_chunks = [
        {
            "doc_id": "doc_123",
            "chunk_id": "chunk_456",
            "assertions": [
                {
                    "assertion": {
                        "subject": "authority",
                        "predicate": "shall notify",
                        "object": "applicant",
                    },
                    "modifiers": [
                        "within thirty days",
                        "where the application is incomplete",
                    ],
                }
            ],
        }
    ]

    result = normalize_assertions(extracted_chunks)

    assert len(result) == 1

    assert result[0]["doc_id"] == "doc_123"
    assert result[0]["chunk_id"] == "chunk_456"
    assert result[0]["assertion_id"] == 0

    assert result[0]["modifiers"] == [
        "within thirty days",
        "where the application is incomplete",
    ]


# =============================================================================
# T11 - "OR" coordination
# =============================================================================

def test_or_coordinated_subject_is_expanded():
    assertion = {
        "subject": "the authority or the applicant",
        "predicate": "shall cooperate",
        "object": None,
    }

    result = expand_assertion(assertion)

    assert len(result) == 2
    assert result[0]["subject"] == "the authority"
    assert result[1]["subject"] == "the applicant"


# =============================================================================
# T12 - Three-way coordination
# =============================================================================

def test_three_way_coordinated_subject_is_expanded():
    assertion = {
        "subject": "the authority, the applicant and the representative",
        "predicate": "shall cooperate",
        "object": None,
    }

    result = expand_assertion(assertion)

    assert len(result) == 3
    assert [item["subject"] for item in result] == [
        "the authority",
        "the applicant",
        "the representative",
    ]


# =============================================================================
# T13 - Cartesian product expansion
# =============================================================================

def test_unequal_subject_and_object_lists_use_cartesian_product():
    assertion = {
        "subject": "authority and applicant",
        "predicate": "shall notify",
        "object": "Commission, Council and Parliament",
    }

    result = expand_assertion(assertion)

    assert len(result) == 6

    expected_pairs = {
        ("authority", "Commission"),
        ("authority", "Council"),
        ("authority", "Parliament"),
        ("applicant", "Commission"),
        ("applicant", "Council"),
        ("applicant", "Parliament"),
    }

    actual_pairs = {
        (item["subject"], item["object"])
        for item in result
    }

    assert actual_pairs == expected_pairs


# =============================================================================
# T14 - Legal reference "OR" cases
# =============================================================================

def test_coordinated_legal_references_using_or_are_split():
    text = "Article 5 or Article 7"

    result = split_legal_reference(text)

    assert result == [
        "Article 5",
        "Article 7",
    ]


# =============================================================================
# T15 - Case-insensitive predicate normalization
# =============================================================================

def test_coordinated_legal_references_using_or_are_split():
    text = "Article 5 or Article 7"

    result = split_legal_reference(text)

    assert result == [
        "Article 5",
        "Article 7",
    ]


# =============================================================================
# T16 - Whitespace and punctuation
# =============================================================================

@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "   undertaking   established within the territory   ",
            "undertaking established within the territory",
        ),
        (
            "authority,",
            "authority",
        ),
        (
            "applicant;",
            "applicant",
        ),
        (
            "document:",
            "document",
        ),
        (
            "   Article 5.   ",
            "Article 5",
        ),
    ],
)
def test_entity_normalization_handles_whitespace_and_trailing_punctuation(
    value,
    expected,
):
    assert normalize_entity(value) == expected

