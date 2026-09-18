import asyncio
from types import SimpleNamespace

from jurisynth.agentic_reasoner.llm import EvidenceGroundedLeafGenerator, NIMConfig, NIMRetryPolicy, OpenAICompatibleNIM
from jurisynth.agentic_reasoner.models import LeafNode
from jurisynth.contracts import Assertion, EvidenceBundle, EvidenceItem, SourceChunk


class FakeModel:
    async def complete(self, *, system, user, max_tokens, **_kwargs):
        return '{"status":"supported","answer_text":"A duty exists.","claims":[{"text":"A duty exists.","evidence_refs":["E1"],"status":"supported"}]}'


def test_output_token_limit_is_not_transmitted_even_for_legacy_callers():
    requests = []
    async def create(**kwargs):
        requests.append(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='ok'))])
    model = OpenAICompatibleNIM(NIMConfig('test', 'https://example.test'),
        client=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create))))
    assert asyncio.run(model.complete(system='test', user='test', max_tokens=800)) == 'ok'
    assert 'max_tokens' not in requests[0] and 'max_completion_tokens' not in requests[0]
    assert requests[0]['temperature'] == 0 and requests[0]['top_p'] == .000001


def test_disabled_transport_timeout_is_passed_as_none(monkeypatch):
    import openai
    captured = {}
    def create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace()
    monkeypatch.setattr(openai, 'AsyncOpenAI', create)
    OpenAICompatibleNIM(NIMConfig('test', 'https://example.test', request_timeout_seconds=None))
    assert captured['timeout'] is None
    assert captured['max_retries'] == 0


def test_timeout_chain_logging_keeps_type_and_elapsed_but_not_messages(tmp_path):
    import json
    import httpx
    from jurisynth.reasoning_log import ReasoningLog
    class APITimeoutError(Exception):
        pass
    async def create(**kwargs):
        try:
            raise httpx.ReadTimeout('secret transport details')
        except httpx.ReadTimeout as cause:
            raise APITimeoutError('secret wrapper details') from cause
    path = tmp_path/'events.jsonl'
    model = OpenAICompatibleNIM(NIMConfig('secret_key', 'https://example.test'),
        client=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create))),
        retry_policy=NIMRetryPolicy(max_attempts=1), reasoning_log=ReasoningLog(path, 'test'))
    import pytest
    with pytest.raises(APITimeoutError):
        asyncio.run(model.complete(system='secret system', user='secret user', max_tokens=10))
    text = path.read_text(encoding='utf-8')
    event = json.loads(text.splitlines()[-1])
    assert event['transport_exception_chain'][0]['type'] == 'ReadTimeout'
    assert event['elapsed_seconds'] >= 0
    assert 'secret' not in text


def test_real_400_status_is_not_retried_when_payload_mentions_503():
    import pytest
    calls = []
    async def failing(**kwargs):
        calls.append(kwargs)
        error = RuntimeError('Error code: 400; invalid field 503 or 404')
        error.status_code = 400
        raise error
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=failing)))
    model = OpenAICompatibleNIM(NIMConfig('test', 'https://example.test'), client=client)
    with pytest.raises(RuntimeError):
        asyncio.run(model.complete(system='test', user='test', max_tokens=10))
    assert len(calls) == 1


def test_query_cancellation_interrupts_hanging_request_and_is_logged():
    from unittest.mock import AsyncMock
    from jurisynth.reasoning_log import ReasoningLog
    import tempfile
    from pathlib import Path
    async def hanging(**kwargs):
        await asyncio.sleep(60)
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=hanging)), close=AsyncMock())
    async def exercise(log):
        model = OpenAICompatibleNIM(NIMConfig('test', 'https://example.test'), client=client, reasoning_log=log)
        try:
            await asyncio.wait_for(model.complete(system='system', user='question', max_tokens=100), timeout=0.01)
        except TimeoutError:
            pass
        else:
            raise AssertionError('Request was not cancelled by the overall deadline.')
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory)/'events.jsonl'
        asyncio.run(exercise(ReasoningLog(path, 'test')))
        assert 'nim_request_cancelled' in path.read_text(encoding='utf-8')


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


def _prompt_item(evidence_id, score, *, chunk=False, document_id=None):
    return EvidenceItem(
        evidence_id,
        Assertion(f"subject-{evidence_id}", "predicate", f"object-{evidence_id}"),
        [SourceChunk(f"chunk-{evidence_id}", document_id or f"doc-{evidence_id}", f"text-{evidence_id}")],
        retrieval_origins=["chunk"] if chunk else ["direct"],
        relevance_score=score,
        structural_score=0.0 if chunk else 1.0,
    )


def _selected_ids(generator, items):
    bundle = EvidenceBundle("q-selection", "success", items)
    return [item["evidence_id"] for item in generator._bounded_evidence(bundle)]


def test_leaf_prompt_selection_preserves_chunks_in_assertion_heavy_hybrid_bundle():
    assertions = [_prompt_item(f"E{index}", 1.0 - index / 1000) for index in range(20)]
    chunks = [_prompt_item(f"C{index}", 0.7 - index / 1000, chunk=True) for index in range(8)]

    selected = _selected_ids(EvidenceGroundedLeafGenerator(FakeModel()), assertions + chunks)

    assert len(selected) == 12
    assert any(item.startswith("E") for item in selected)
    assert any(item.startswith("C") for item in selected)
    assert sum(item.startswith("C") for item in selected) >= 4


def test_leaf_prompt_selection_preserves_assertions_in_chunk_heavy_hybrid_bundle():
    assertions = [_prompt_item(f"E{index}", 0.6 - index / 1000) for index in range(5)]
    chunks = [_prompt_item(f"C{index}", 0.99 - index / 1000, chunk=True) for index in range(20)]

    selected = _selected_ids(EvidenceGroundedLeafGenerator(FakeModel()), assertions + chunks)

    assert len(selected) == 12
    assert sum(item.startswith("E") for item in selected) >= 4
    assert any(item.startswith("C") for item in selected)


def test_leaf_prompt_selection_keeps_legacy_order_for_single_modality():
    generator = EvidenceGroundedLeafGenerator(FakeModel(), max_evidence_items=4)
    assertions = [_prompt_item(f"E{index}", score) for index, score in enumerate((0.2, 0.9, 0.5, 0.7, 0.1))]
    chunks = [_prompt_item(f"C{index}", score, chunk=True) for index, score in enumerate((0.2, 0.9, 0.5, 0.7, 0.1))]

    assert _selected_ids(generator, assertions) == ["E1", "E3", "E2", "E0"]
    assert _selected_ids(generator, chunks) == ["C1", "C3", "C2", "C0"]


def test_leaf_prompt_selection_recycles_unused_modality_capacity():
    generator = EvidenceGroundedLeafGenerator(FakeModel(), max_evidence_items=12)
    assertions = [_prompt_item(f"E{index}", 1.0 - index / 1000) for index in range(20)]
    chunks = [_prompt_item("C0", 0.5, chunk=True)]

    selected = _selected_ids(generator, assertions + chunks)

    assert len(selected) == 12
    assert "C0" in selected
    assert sum(item.startswith("E") for item in selected) == 11


def test_leaf_prompt_selection_is_deterministic_and_preserves_provenance():
    generator = EvidenceGroundedLeafGenerator(FakeModel(), max_evidence_items=6)
    items = [
        _prompt_item("E1", 1.0, document_id="assertion-doc"),
        _prompt_item("E2", 0.9, document_id="assertion-doc-2"),
        _prompt_item("C1", 0.8, chunk=True, document_id="chunk-doc"),
        _prompt_item("C2", 0.7, chunk=True, document_id="chunk-doc-2"),
    ]
    bundle = EvidenceBundle("q-selection", "success", items)

    first = generator._bounded_evidence(bundle)
    second = generator._bounded_evidence(bundle)

    assert first == second
    assert len(first) <= generator.max_evidence_items
    source_by_id = {item["evidence_id"]: item["source_chunks"][0] for item in first}
    assert source_by_id["E1"]["document_id"] == "assertion-doc"
    assert source_by_id["C1"]["document_id"] == "chunk-doc"
    assert source_by_id["C1"]["chunk_id"] == "chunk-C1"


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


def test_nim_config_accepts_zero_timeout_as_no_client_timeout(monkeypatch, tmp_path):
    monkeypatch.setenv("JURISYNTH_NIM_API_KEY", "key")
    monkeypatch.setenv("JURISYNTH_NIM_BASE_URL", "https://example.test/v1")
    monkeypatch.setenv("JURISYNTH_NIM_TIMEOUT_SECONDS", "0")

    import pytest

    assert NIMConfig.from_environment(dotenv_path=tmp_path / "empty.env").request_timeout_seconds is None


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


def test_connection_retries_have_secret_free_observability(tmp_path):
    from jurisynth.reasoning_log import ReasoningLog
    class Completions:
        calls = 0
        async def create(self, **kwargs):
            self.calls += 1
            if self.calls == 1:
                raise ConnectionError("connection lost")
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))])
    completions = Completions()
    path = tmp_path / "events.jsonl"
    model = OpenAICompatibleNIM(NIMConfig("secret_key", "https://example.test/v1"),
        client=SimpleNamespace(chat=SimpleNamespace(completions=completions)),
        retry_policy=NIMRetryPolicy(requests_per_second=1000, max_backoff_seconds=0, jitter_seconds=0),
        reasoning_log=ReasoningLog(path, "test"))
    assert asyncio.run(model.complete(system="secret_system", user="secret_user", max_tokens=10)) == "ok"
    recorded = path.read_text(encoding="utf-8")
    assert "nim_retry_scheduled" in recorded
    assert "nim_request_completed" in recorded
    assert "secret_key" not in recorded and "secret_system" not in recorded and "secret_user" not in recorded


def test_nim_client_uses_explicit_deterministic_sampling_controls():
    class Completions:
        def __init__(self):
            self.request = None

        async def create(self, **kwargs):
            self.request = kwargs
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))])

    completions = Completions()
    model = OpenAICompatibleNIM(NIMConfig("key", "https://example.test/v1"), client=SimpleNamespace(chat=SimpleNamespace(completions=completions)))
    asyncio.run(model.complete(system="system", user="user", max_tokens=10))
    assert completions.request["temperature"] == 0
    assert completions.request["top_p"] == 0.000001
    assert completions.request["reasoning_effort"] == "none"


def test_nim_client_allows_a_provider_specific_reasoning_effort():
    class Completions:
        async def create(self, **kwargs):
            self.request = kwargs
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))])

    completions = Completions()
    model = OpenAICompatibleNIM(NIMConfig("key", "https://example.test/v1", reasoning_effort="low"), client=SimpleNamespace(chat=SimpleNamespace(completions=completions)))
    asyncio.run(model.complete(system="system", user="user", max_tokens=10))
    assert completions.request["reasoning_effort"] == "low"
