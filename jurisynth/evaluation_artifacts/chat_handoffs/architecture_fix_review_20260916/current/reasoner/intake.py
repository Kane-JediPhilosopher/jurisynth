"""Conversation-state and necessary-only clarification contract."""

from __future__ import annotations

import json
from dataclasses import dataclass

from jurisynth.agentic_reasoner.llm import ChatModel
from jurisynth.agentic_reasoner.schemas import INTAKE_SCHEMA, REQUEST_ANALYSIS_SCHEMA


@dataclass(frozen=True, slots=True)
class ConversationTurn:
    role: str
    content: str


@dataclass(frozen=True, slots=True)
class IntakeDecision:
    action: str
    contextual_facts: tuple[str, ...]
    constraints: dict[str, object]
    clarification_question: str | None = None

    def user_response(self) -> dict[str, object] | None:
        """Return the only user-facing clarification payload; no internal plan leaks."""
        if self.action != "clarify" or self.clarification_question is None:
            return None
        return {
            "type": "clarification_required",
            "question": self.clarification_question,
            "preserved_context": list(self.contextual_facts),
            "constraints": self.constraints,
        }


@dataclass(frozen=True, slots=True)
class RequestAnalysisDecision:
    """One-call clarification, routing, and context decision."""

    action: str
    route: str
    contextual_facts: tuple[str, ...]
    constraints: dict[str, object]
    clarification_question: str | None = None

    def user_response(self) -> dict[str, object] | None:
        if self.action != "clarify" or self.clarification_question is None:
            return None
        return {
            "type": "clarification_required",
            "question": self.clarification_question,
            "preserved_context": list(self.contextual_facts),
            "constraints": self.constraints,
        }


_PROMPT = """Read the current user request with relevant conversation context. Return JSON only:
{"action":"proceed|clarify","contextual_facts":["..."],"constraints":{},"clarification_question":null}.
Ask one clarification only when ambiguity materially changes legal retrieval or interpretation. Otherwise proceed. Preserve stated facts without turning every fact into a separate question."""

_REQUEST_ANALYSIS_PROMPT = """Read the current legal-information request and relevant conversation history.
Return JSON only:
{"action":"proceed|clarify","route":"direct|complex","contextual_facts":["..."],"constraints":{},"clarification_question":null}.
Ask one clarification only when ambiguity materially changes legal retrieval or
interpretation; otherwise proceed. Use direct for one independent information
need and complex only for multiple parallel or genuinely dependent questions.
Preserve stated facts and constraints. Do not answer, decompose, create retrieval
terms, or infer facts the user did not provide."""


@dataclass(slots=True)
class NIMConversationIntake:
    model: ChatModel
    max_tokens: int = 400
    max_validation_attempts: int = 2

    async def decide_and_analyze(
        self,
        user_query: str,
        history: tuple[ConversationTurn, ...] = (),
    ) -> RequestAnalysisDecision:
        """Combine clarification, routing, and context extraction in one call."""
        payload = {"history": [{"role": turn.role, "content": turn.content} for turn in history], "user_query": user_query}
        prompt = json.dumps(payload)
        for attempt in range(self.max_validation_attempts):
            response = await self.model.complete(
                system=_REQUEST_ANALYSIS_PROMPT,
                user=prompt,
                max_tokens=self.max_tokens,
                response_schema=REQUEST_ANALYSIS_SCHEMA,
            )
            try:
                return parse_request_analysis(response)
            except ValueError as exc:
                if attempt + 1 == self.max_validation_attempts:
                    raise
                prompt = json.dumps({"original_input": payload, "validation_error": str(exc)})
        raise AssertionError("unreachable")

    async def decide(self, user_query: str, history: tuple[ConversationTurn, ...] = ()) -> IntakeDecision:
        payload = {"history": [{"role": turn.role, "content": turn.content} for turn in history], "user_query": user_query}
        if self.max_validation_attempts < 1:
            raise ValueError("max_validation_attempts must be positive")
        prompt = json.dumps(payload)
        for attempt in range(self.max_validation_attempts):
            response = await self.model.complete(system=_PROMPT, user=prompt, max_tokens=self.max_tokens, response_schema=INTAKE_SCHEMA)
            try:
                return parse_decision(response)
            except ValueError as exc:
                if attempt + 1 == self.max_validation_attempts:
                    raise
                prompt = json.dumps({"original_input": payload, "validation_error": str(exc)})
        raise AssertionError("unreachable")


def parse_decision(response: str) -> IntakeDecision:
    response = response.strip()
    if response.startswith("```json") and response.endswith("```"):
        response = response[7:-3].strip()
    elif response.startswith("```") and response.endswith("```"):
        response = response[3:-3].strip()
    try:
        payload = json.loads(response)
    except json.JSONDecodeError as exc:
        raise ValueError("Conversation intake response is not valid JSON.") from exc
    if not isinstance(payload, dict) or payload.get("action") not in {"proceed", "clarify"}:
        raise ValueError("Conversation intake must choose proceed or clarify.")
    facts = payload.get("contextual_facts", [])
    constraints = payload.get("constraints", {})
    question = payload.get("clarification_question")
    if not isinstance(facts, list) or not all(isinstance(value, str) for value in facts) or not isinstance(constraints, dict):
        raise ValueError("Conversation intake has malformed context.")
    if payload["action"] == "clarify" and (not isinstance(question, str) or not question.strip()):
        raise ValueError("Clarification action requires one question.")
    if payload["action"] == "proceed" and question is not None:
        raise ValueError("Proceed action must not contain a clarification question.")
    return IntakeDecision(payload["action"], tuple(value.strip() for value in facts if value.strip()), constraints, question)


def parse_request_analysis(response: str) -> RequestAnalysisDecision:
    response = response.strip()
    if response.startswith("```json") and response.endswith("```"):
        response = response[7:-3].strip()
    elif response.startswith("```") and response.endswith("```"):
        response = response[3:-3].strip()
    try:
        payload = json.loads(response)
    except json.JSONDecodeError as exc:
        raise ValueError("Request analysis response is not valid JSON.") from exc
    if not isinstance(payload, dict) or payload.get("action") not in {"proceed", "clarify"}:
        raise ValueError("Request analysis must choose proceed or clarify.")
    if payload.get("route") not in {"direct", "complex"}:
        raise ValueError("Request analysis must declare route direct or complex.")
    facts = payload.get("contextual_facts", [])
    constraints = payload.get("constraints", {})
    question = payload.get("clarification_question")
    if not isinstance(facts, list) or not all(isinstance(value, str) for value in facts) or not isinstance(constraints, dict):
        raise ValueError("Request analysis has malformed context.")
    if payload["action"] == "clarify" and (not isinstance(question, str) or not question.strip()):
        raise ValueError("Clarification action requires one question.")
    if payload["action"] == "proceed" and question is not None:
        raise ValueError("Proceed action must not contain a clarification question.")
    return RequestAnalysisDecision(
        payload["action"],
        payload["route"],
        tuple(value.strip() for value in facts if value.strip()),
        constraints,
        question,
    )
