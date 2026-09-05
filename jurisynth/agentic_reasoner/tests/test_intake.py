import pytest
import asyncio

from jurisynth.agentic_reasoner.intake import NIMConversationIntake, parse_decision


def test_intake_preserves_context_and_proceeds_without_unnecessary_question():
    decision = parse_decision('{"action":"proceed","contextual_facts":["John bought a laptop in Berlin."],"constraints":{"jurisdiction":"Germany"},"clarification_question":null}')
    assert decision.action == "proceed" and decision.contextual_facts == ("John bought a laptop in Berlin.",)


def test_intake_requires_a_question_only_when_clarification_is_needed():
    with pytest.raises(ValueError, match="requires one question"):
        parse_decision('{"action":"clarify","contextual_facts":[],"constraints":{},"clarification_question":null}')


def test_clarification_payload_preserves_only_user_relevant_context():
    decision = parse_decision('{"action":"clarify","contextual_facts":["The purchase was in Berlin."],"constraints":{"jurisdiction":"Germany"},"clarification_question":"When was it purchased?"}')
    assert decision.user_response() == {
        "type": "clarification_required",
        "question": "When was it purchased?",
        "preserved_context": ["The purchase was in Berlin."],
        "constraints": {"jurisdiction": "Germany"},
    }


def test_intake_retries_once_after_malformed_structured_output():
    class Model:
        def __init__(self):
            self.responses = iter([
                "not json",
                '{"action":"proceed","contextual_facts":["A purchase occurred."],"constraints":{},"clarification_question":null}',
            ])
            self.calls = 0

        async def complete(self, **kwargs):
            self.calls += 1
            return next(self.responses)

    model = Model()
    decision = asyncio.run(NIMConversationIntake(model).decide("What are my rights?"))

    assert decision.action == "proceed"
    assert model.calls == 2


def test_intake_accepts_json_wrapped_in_a_code_fence():
    decision = parse_decision('```json\n{"action":"proceed","contextual_facts":[],"constraints":{},"clarification_question":null}\n```')

    assert decision.action == "proceed"
