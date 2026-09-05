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
