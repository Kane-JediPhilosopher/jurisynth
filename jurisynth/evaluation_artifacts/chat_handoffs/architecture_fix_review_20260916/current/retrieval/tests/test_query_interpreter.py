import asyncio

import pytest

from jurisynth.contracts import RetrievalRequest
from jurisynth.retrieval_mech.query_interpreter import NIMQueryInterpreter


class FakeModel:
    def __init__(self, response):
        self.response = response

    async def complete(self, **kwargs):
        return self.response


class RecordingModel(FakeModel):
    def __init__(self, response):
        super().__init__(response)
        self.kwargs = None

    async def complete(self, **kwargs):
        self.kwargs = kwargs
        return await super().complete(**kwargs)


def test_interpreter_keeps_concept_groups_and_bounds_variants():
    response = '{"entity_concepts":[{"concept":"data controller","variants":["controller","controller","responsible party","operator"]}],"relation_concepts":[{"concept":"must provide","variants":["is required to provide"]}]}'
    entities, relations = asyncio.run(NIMQueryInterpreter(FakeModel(response), max_variants=2).interpret(RetrievalRequest("q1", "What must a controller provide?")))
    assert entities[0].concept_id == "entity_1"
    assert entities[0].variants == ("controller", "responsible party")
    assert relations[0].concept_id == "relation_1"


def test_interpreter_rejects_malformed_json():
    with pytest.raises(ValueError, match="valid JSON"):
        asyncio.run(NIMQueryInterpreter(FakeModel("not json")).interpret(RetrievalRequest("q1", "question")))


def test_interpreter_prompt_requires_verbatim_named_entity_grounding():
    model = RecordingModel('{"entity_concepts":[{"concept":"Belgium","variants":[]}],"relation_concepts":[]}')

    entities, relations = asyncio.run(
        NIMQueryInterpreter(model).interpret(RetrievalRequest("q1", "What did Belgium notify to the Commission?"))
    )

    assert entities[0].text == "Belgium"
    assert relations == []
    assert "preserve it verbatim" in model.kwargs["system"]
    assert "THIS leaf only" in model.kwargs["system"]
    assert "not an invitation to perform broad legal issue spotting" in model.kwargs["system"]
    assert "do not predict or enumerate the legal" in model.kwargs["system"]
    assert model.kwargs["response_schema"]["name"] == "retrieval_concepts"


def test_interpreter_accepts_a_json_code_fence_despite_the_schema_request():
    response = '```json\n{"entity_concepts":[{"concept":"Regulation (EU) 2024/1689","variants":[]}],"relation_concepts":[]}\n```'
    entities, relations = asyncio.run(NIMQueryInterpreter(FakeModel(response)).interpret(RetrievalRequest("q1", "AI Act")))
    assert entities[0].text == "Regulation (EU) 2024/1689"
    assert relations == []


def test_interpreter_retries_truncated_json_with_schema_and_feedback():
    import json
    class Model:
        calls = 0
        async def complete(self, **kwargs):
            self.calls += 1
            assert kwargs["max_tokens"] == 2048
            assert kwargs["response_schema"]["name"] == "retrieval_concepts"
            if self.calls == 1:
                return '{"entity_concepts":['
            assert "validation_error" in json.loads(kwargs["user"])
            return '{"entity_concepts":[{"concept":"hospital","variants":[]}],"relation_concepts":[]}'
    model = Model()
    entities, _ = asyncio.run(NIMQueryInterpreter(model).interpret(RetrievalRequest("q", "hospital obligations")))
    assert model.calls == 2 and entities[0].text == "hospital"


def test_interpreter_rejects_missing_arrays_after_finite_attempts():
    with pytest.raises(ValueError, match="requires exactly"):
        asyncio.run(NIMQueryInterpreter(FakeModel('{}')).interpret(RetrievalRequest("q", "question")))
