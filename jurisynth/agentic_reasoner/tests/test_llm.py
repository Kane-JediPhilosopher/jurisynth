import asyncio
from types import SimpleNamespace

from jurisynth.agentic_reasoner.llm import EvidenceGroundedLeafGenerator, NIMConfig, NIMRetryPolicy, OpenAICompatibleNIM
from jurisynth.agentic_reasoner.models import LeafNode
from jurisynth.contracts import Assertion, EvidenceBundle, EvidenceItem, SourceChunk


class FakeModel:
    async def complete(self, *, system, user, max_tokens):
        return '{"status":"supported","answer_text":"A duty exists.","claims":[{"text":"A duty exists.","evidence_refs":["E1"],"status":"supported"}]}'


class SequenceModel:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = 0

    async def complete(self, **kwargs):
        self.calls += 1
        return next(self.responses)


def test_leaf_generator_requires_model_claims_to_reference_bundle_evidence():
    evidence = EvidenceBundle("q1", "success", [EvidenceItem("E1", Assertion("s", "p", "o"), [SourceChunk("c1", "d1", "text")])])
    answer = asyncio.run(EvidenceGroundedLeafGenerator(FakeModel())(LeafNode("q1", "question"), [], evidence))
    assert answer.claims[0].evidence_refs == ["E1"]


def test_empty_retrieval_does_not_call_model_or_force_an_answer():
    answer = asyncio.run(EvidenceGroundedLeafGenerator(FakeModel())(LeafNode("q2", "question"), [], EvidenceBundle("q2", "empty")))
    assert answer.status == "insufficient_evidence"
    assert answer.claims == []


def test_leaf_generator_retries_once_after_malformed_structured_output():
    model = SequenceModel([
        "not json",
        '{"status":"supported","answer_text":"A duty exists.","claims":[{"text":"A duty exists.","evidence_refs":["E1"]}]}',
    ])
    evidence = EvidenceBundle("q3", "success", [EvidenceItem("E1", Assertion("s", "p", "o"), [])])

    answer = asyncio.run(EvidenceGroundedLeafGenerator(model)(LeafNode("q3", "question"), [], evidence))

    assert answer.claims[0].evidence_refs == ["E1"]
    assert model.calls == 2


def test_leaf_generator_accepts_json_wrapped_in_a_markdown_fence():
    model = SequenceModel([
        '```json\n{"status":"supported","answer_text":"A duty exists.","claims":[{"text":"A duty exists.","evidence_refs":["E1"]}]}\n```',
    ])
    evidence = EvidenceBundle("q3", "success", [EvidenceItem("E1", Assertion("s", "p", "o"), [])])

    answer = asyncio.run(EvidenceGroundedLeafGenerator(model)(LeafNode("q3", "question"), [], evidence))

    assert answer.claims[0].evidence_refs == ["E1"]
    assert model.calls == 1


def test_leaf_generator_bounds_serialized_evidence_without_mutating_the_bundle():
    evidence = EvidenceBundle(
        "q4",
        "success",
        [
            EvidenceItem(
                f"E{index}",
                Assertion("subject-" + "x" * 200, "predicate", "object-" + "y" * 200),
                [SourceChunk(f"c{index}", "d1", "source-" + "z" * 1_000)],
                relevance_score=float(index),
            )
            for index in range(20)
        ],
    )
    generator = EvidenceGroundedLeafGenerator(
        FakeModel(),
        max_evidence_items=3,
        max_sources_per_item=1,
        max_source_characters=80,
        max_assertion_field_characters=50,
        max_evidence_payload_characters=900,
    )

    payload = generator._bounded_evidence(evidence)

    assert 1 <= len(payload) <= 3
    assert all(len(item["source_chunks"][0]["text"]) <= 80 for item in payload)
    assert all(item["source_chunks"][0]["text"].endswith("…") for item in payload)
    assert all(item["source_chunks"][0]["text_truncated"] for item in payload)
    assert len(evidence.evidence_items) == 20


def test_nim_config_defaults_to_requested_model_but_requires_credentials(monkeypatch, tmp_path):
    monkeypatch.setenv("JURISYNTH_NIM_API_KEY", "key")
    monkeypatch.setenv("JURISYNTH_NIM_BASE_URL", "https://example.test/v1")
    monkeypatch.delenv("JURISYNTH_NIM_MODEL", raising=False)
    assert NIMConfig.from_environment(dotenv_path=tmp_path / "empty.env").model == "nemotron-3-ultra"


def test_nim_config_uses_a_positive_configurable_request_timeout(monkeypatch, tmp_path):
    monkeypatch.setenv("JURISYNTH_NIM_API_KEY", "key")
    monkeypatch.setenv("JURISYNTH_NIM_BASE_URL", "https://example.test/v1")
    monkeypatch.setenv("JURISYNTH_NIM_TIMEOUT_SECONDS", "12.5")

    assert NIMConfig.from_environment(dotenv_path=tmp_path / "empty.env").request_timeout_seconds == 12.5


def test_nim_config_accepts_an_opt_in_retry_cap(monkeypatch, tmp_path):
    monkeypatch.setenv("JURISYNTH_NIM_API_KEY", "key")
    monkeypatch.setenv("JURISYNTH_NIM_BASE_URL", "https://example.test/v1")
    monkeypatch.setenv("JURISYNTH_NIM_MAX_ATTEMPTS", "2")

    assert NIMConfig.from_environment(dotenv_path=tmp_path / "empty.env").max_attempts == 2


def test_nim_config_rejects_non_positive_request_timeout(monkeypatch, tmp_path):
    monkeypatch.setenv("JURISYNTH_NIM_API_KEY", "key")
    monkeypatch.setenv("JURISYNTH_NIM_BASE_URL", "https://example.test/v1")
    monkeypatch.setenv("JURISYNTH_NIM_TIMEOUT_SECONDS", "0")

    import pytest

    with pytest.raises(RuntimeError, match="positive number"):
        NIMConfig.from_environment(dotenv_path=tmp_path / "empty.env")


def test_nim_client_retries_a_503_then_returns_completion():
    class Completions:
        def __init__(self):
            self.calls = 0

        async def create(self, **kwargs):
            self.calls += 1
            if self.calls == 1:
                raise RuntimeError("503 Service Unavailable")
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))])

    completions = Completions()
    client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    model = OpenAICompatibleNIM(
        NIMConfig("key", "https://example.test/v1"),
        client=client,
        retry_policy=NIMRetryPolicy(requests_per_second=1000, max_backoff_seconds=0, jitter_seconds=0, max_attempts=2),
    )
    assert asyncio.run(model.complete(system="system", user="user", max_tokens=10)) == "ok"
    assert completions.calls == 2
