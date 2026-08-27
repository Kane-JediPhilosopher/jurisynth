import json
import pytest

import assertion_extractor
from assertion_extractor import extract_assertions
from llm_utils import create_client


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sample_chunk():
    return {
        "doc_id": "test_doc",
        "chunk_id": "chunk_1",
        "content": (
            "Any undertaking established within the territory "
            "must maintain records relating to goods supplied."
        ),
    }


@pytest.fixture
def fake_client():
    """
    The extractor passes the client through to get_completion().
    The client itself is unused because get_completion is mocked.
    """
    return object()


# =============================================================================
# Mock helper
# =============================================================================

def mock_completion(monkeypatch, response):
    """
    Replace get_completion() with a deterministic async response.
    """

    async def fake_get_completion(
        client,
        query,
        system_prompt,
        schema,
    ):
        return json.dumps(response)

    monkeypatch.setattr(
        assertion_extractor,
        "get_completion",
        fake_get_completion,
    )


# =============================================================================
# T01 — Basic extraction
# =============================================================================

@pytest.mark.asyncio
async def test_basic_assertion_extraction(
    sample_chunk,
    fake_client,
    monkeypatch,
):
    """
    A valid LLM response should be converted into the expected
    document/chunk/assertion structure.
    """

    mock_completion(
        monkeypatch,
        {
            "assertions": [
                {
                    "assertion": {
                        "subject": "undertaking established within the territory",
                        "predicate": "must maintain",
                        "object": "records relating to goods supplied",
                    },
                    "modifiers": [],
                }
            ]
        },
    )

    extracted, errors = await assertion_extractor.extract_assertions(
        fake_client,
        [sample_chunk],
        requests_per_second=100,
    )

    assert errors == []
    assert len(extracted) == 1

    result = extracted[0]

    assert result["doc_id"] == "test_doc"
    assert result["chunk_id"] == "chunk_1"

    assert result["assertions"] == [
        {
            "assertion": {
                "subject": "undertaking established within the territory",
                "predicate": "must maintain",
                "object": "records relating to goods supplied",
            },
            "modifiers": [],
        }
    ]


# =============================================================================
# T02 — Multiple assertions
# =============================================================================

@pytest.mark.asyncio
async def test_multiple_assertions_are_preserved(
    sample_chunk,
    fake_client,
    monkeypatch,
):
    """
    Multiple independent assertions returned by the LLM should all be
    preserved rather than collapsed or discarded.
    """

    mock_completion(
        monkeypatch,
        {
            "assertions": [
                {
                    "assertion": {
                        "subject": "authority",
                        "predicate": "shall verify",
                        "object": "documents",
                    },
                    "modifiers": [],
                },
                {
                    "assertion": {
                        "subject": "authority",
                        "predicate": "may reject",
                        "object": "applications",
                    },
                    "modifiers": [],
                },
            ]
        },
    )

    extracted, errors = await assertion_extractor.extract_assertions(
        fake_client,
        [sample_chunk],
        requests_per_second=100,
    )

    assert errors == []
    assert len(extracted) == 1
    assert len(extracted[0]["assertions"]) == 2


# =============================================================================
# T03 — Modifiers
# =============================================================================

@pytest.mark.asyncio
async def test_assertion_modifiers_are_preserved(
    sample_chunk,
    fake_client,
    monkeypatch,
):
    """
    Legal conditions and temporal restrictions represented as modifiers
    should survive extraction unchanged.
    """

    mock_completion(
        monkeypatch,
        {
            "assertions": [
                {
                    "assertion": {
                        "subject": "applicant",
                        "predicate": "must provide",
                        "object": "missing information",
                    },
                    "modifiers": [
                        "Where the authority considers that the application is incomplete",
                        "within thirty days",
                    ],
                }
            ]
        },
    )

    extracted, errors = await assertion_extractor.extract_assertions(
        fake_client,
        [sample_chunk],
        requests_per_second=100,
    )

    assert errors == []

    assertion = extracted[0]["assertions"][0]

    assert assertion["modifiers"] == [
        "Where the authority considers that the application is incomplete",
        "within thirty days",
    ]


# =============================================================================
# T04 — Objectless assertions
# =============================================================================

@pytest.mark.asyncio
async def test_objectless_assertion_preserves_null_object(
    sample_chunk,
    fake_client,
    monkeypatch,
):
    """
    Naturally objectless legal propositions must preserve object=null.
    """

    mock_completion(
        monkeypatch,
        {
            "assertions": [
                {
                    "assertion": {
                        "subject": "register",
                        "predicate": "shall be maintained",
                        "object": None,
                    },
                    "modifiers": [],
                }
            ]
        },
    )

    extracted, errors = await assertion_extractor.extract_assertions(
        fake_client,
        [sample_chunk],
        requests_per_second=100,
    )

    assert errors == []

    assertion = extracted[0]["assertions"][0]

    assert assertion["assertion"]["object"] is None


# =============================================================================
# T05 — Unresolved references remain conservative
# =============================================================================

@pytest.mark.asyncio
async def test_unresolved_reference_is_not_invented(
    sample_chunk,
    fake_client,
    monkeypatch,
):
    """
    The extractor should preserve an unresolved reference rather than
    inventing an antecedent.
    """

    mock_completion(
        monkeypatch,
        {
            "assertions": [
                {
                    "assertion": {
                        "subject": "the holder",
                        "predicate": "must comply with",
                        "object": "the applicable requirements",
                    },
                    "modifiers": [],
                }
            ]
        },
    )

    extracted, errors = await assertion_extractor.extract_assertions(
        fake_client,
        [sample_chunk],
        requests_per_second=100,
    )

    assert errors == []

    assertion = extracted[0]["assertions"][0]["assertion"]

    assert assertion["subject"] == "the holder"
    assert assertion["object"] == "the applicable requirements"


# =============================================================================
# T06 — Chunk failure isolation
# =============================================================================

@pytest.mark.asyncio
async def test_failed_chunk_isolated_from_successful_chunk(
    fake_client,
    monkeypatch,
):
    """
    A failed chunk should be recorded as an extraction error while other
    chunks continue to produce successful results.
    """

    chunks = [
        {
            "doc_id": "doc_1",
            "chunk_id": "chunk_1",
            "content": "The authority shall verify the documents.",
        },
        {
            "doc_id": "doc_1",
            "chunk_id": "chunk_2",
            "content": "The applicant must provide the information.",
        },
    ]

    async def fake_get_completion(
        client,
        query,
        system_prompt,
        schema,
    ):
        if "verify" in query:
            raise ValueError("synthetic extraction failure")

        return json.dumps(
            {
                "assertions": [
                    {
                        "assertion": {
                            "subject": "applicant",
                            "predicate": "must provide",
                            "object": "information",
                        },
                        "modifiers": [],
                    }
                ]
            }
        )

    monkeypatch.setattr(
        assertion_extractor,
        "get_completion",
        fake_get_completion,
    )

    extracted, errors = await assertion_extractor.extract_assertions(
        fake_client,
        chunks,
        requests_per_second=100,
    )

    assert len(extracted) == 1
    assert extracted[0]["chunk_id"] == "chunk_2"

    assert len(errors) == 1
    assert errors[0]["chunk_id"] == "chunk_1"
    assert errors[0]["reason"] == "extraction_failed"


# =============================================================================
# T07 — Invalid assertions type
# =============================================================================

@pytest.mark.asyncio
async def test_invalid_assertions_type_is_recorded_as_error(
    sample_chunk,
    fake_client,
    monkeypatch,
):
    """
    A malformed but JSON-valid LLM response should be rejected when
    'assertions' is not a list.
    """

    mock_completion(
        monkeypatch,
        {
            "assertions": {
                "unexpected": "object",
            }
        },
    )

    extracted, errors = await assertion_extractor.extract_assertions(
        fake_client,
        [sample_chunk],
        requests_per_second=100,
    )

    assert extracted == []

    assert len(errors) == 1
    assert errors[0]["doc_id"] == "test_doc"
    assert errors[0]["chunk_id"] == "chunk_1"
    assert errors[0]["reason"] == "invalid_assertions_type:dict"


# =============================================================================
# T08 — Transient API failure is retried
# =============================================================================

@pytest.mark.asyncio
async def test_transient_api_failure_is_retried(
    sample_chunk,
    fake_client,
    monkeypatch,
):
    """
    A transient 429 response should trigger retry logic and eventually
    succeed when the subsequent request succeeds.
    """

    calls = 0

    async def fake_get_completion(
        client,
        query,
        system_prompt,
        schema,
    ):
        nonlocal calls
        calls += 1

        if calls == 1:
            raise RuntimeError("429 Too Many Requests")

        return json.dumps(
            {
                "assertions": [
                    {
                        "assertion": {
                            "subject": "undertaking",
                            "predicate": "must maintain",
                            "object": "records",
                        },
                        "modifiers": [],
                    }
                ]
            }
        )

    monkeypatch.setattr(
        assertion_extractor,
        "get_completion",
        fake_get_completion,
    )

    extracted, errors = await assertion_extractor.extract_assertions(
        fake_client,
        [sample_chunk],
        requests_per_second=100,
    )

    assert errors == []
    assert calls == 2

    assert len(extracted) == 1
    assert len(extracted[0]["assertions"]) == 1

# =============================================================================
# T09 — Live client creation
# =============================================================================

def test_live_client_creation():
    """
    The configured NVIDIA API client should be created successfully.

    This test verifies that the API key/environment configuration is available
    and that the client can be constructed without mocking.
    """
    client = create_client()

    assert client is not None
    assert client.base_url is not None


# =============================================================================
# T10 — Live assertion extraction
# =============================================================================

@pytest.mark.asyncio
async def test_live_assertion_extraction():
    """
    Perform a genuine end-to-end assertion extraction against the configured
    LLM.

    This deliberately does not mock get_completion().
    """

    client = create_client()

    processed_chunks = [
        {
            "doc_id": "live_test",
            "chunk_id": "chunk_1",
            "content": (
                "Any undertaking established within the territory must "
                "maintain records relating to goods supplied to its customers."
            ),
        }
    ]

    extracted, errors = await extract_assertions(
        client,
        processed_chunks,
        requests_per_second=0.25,
    )

    assert errors == []
    assert len(extracted) == 1

    result = extracted[0]

    assert result["doc_id"] == "live_test"
    assert result["chunk_id"] == "chunk_1"
    assert isinstance(result["assertions"], list)
    assert len(result["assertions"]) >= 1

    assertion = result["assertions"][0]

    assert "assertion" in assertion
    assert "modifiers" in assertion

    triple = assertion["assertion"]

    assert isinstance(triple["subject"], str)
    assert isinstance(triple["predicate"], str)
    assert triple["object"] is None or isinstance(
        triple["object"],
        (str, dict),
    )

    assert isinstance(assertion["modifiers"], list)

    await client.close()