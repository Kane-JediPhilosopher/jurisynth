"""Batched, evidence-grounded explanations of potential claim conflicts."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace

from jurisynth.agentic_reasoner.contradiction import Contradiction
from jurisynth.agentic_reasoner.llm import ChatModel
from jurisynth.agentic_reasoner.models import LeafAnswer
from jurisynth.agentic_reasoner.schemas import CONTRADICTION_EXPLANATION_SCHEMA


_PROMPT = """Explain the supplied potential conflicts between evidence-linked claims.
Describe incompatible propositions and any differences in actor, scope, time,
conditions or source that may explain an apparent conflict. Do not select a
legally correct winner or invent provisions. State when the supplied excerpts
cannot establish a genuine conflict. Excerpts may be truncated. Return JSON
containing explanations, each with contradiction_id and explanation. Return
exactly one explanation for every supplied conflict ID and no other IDs."""


@dataclass(slots=True)
class BatchedConflictExplainer:
    model: ChatModel
    batch_size: int = 10
    max_tokens: int = 2000
    invalid_output_attempts: int = 2
    excerpt_chars: int = 1200

    async def explain(self, conflicts: list[Contradiction], answers: list[LeafAnswer]) -> list[Contradiction]:
        if min(self.batch_size, self.max_tokens, self.invalid_output_attempts, self.excerpt_chars) < 1:
            raise ValueError("Conflict explanation budgets must be positive.")
        claims = {claim.claim_id: (claim, answer) for answer in answers for claim in answer.claims if claim.claim_id}
        explained: list[Contradiction] = []
        for offset in range(0, len(conflicts), self.batch_size):
            batch = conflicts[offset:offset + self.batch_size]
            payload = []
            for conflict in batch:
                payload.append({
                    "contradiction_id": conflict.contradiction_id,
                    "score": conflict.score,
                    "claim_a": self._claim_payload(*claims[conflict.claim_a_id]),
                    "claim_b": self._claim_payload(*claims[conflict.claim_b_id]),
                })
            request = json.dumps({"conflicts": payload}, ensure_ascii=False)
            expected = {conflict.contradiction_id for conflict in batch}
            for attempt in range(self.invalid_output_attempts):
                raw = await self.model.complete(
                    system=_PROMPT, user=request, max_tokens=self.max_tokens,
                    response_schema=CONTRADICTION_EXPLANATION_SCHEMA,
                )
                try:
                    values = self._validate(raw, expected)
                    break
                except (ValueError, TypeError) as exc:
                    if attempt + 1 == self.invalid_output_attempts:
                        raise ValueError("Conflict explanation failed structured-output validation.") from exc
                    request = json.dumps({"conflicts": payload, "validation_error": str(exc)}, ensure_ascii=False)
            explained.extend(replace(conflict, explanation=values[conflict.contradiction_id]) for conflict in batch)
        return explained

    def _claim_payload(self, claim, answer: LeafAnswer) -> dict[str, object]:
        evidence_by_id = {item.evidence_id: item for item in answer.evidence_bundle.evidence_items}
        evidence = []
        for reference in claim.evidence_refs[:4]:
            item = evidence_by_id.get(reference)
            if item is None:
                raise ValueError(f"Claim references unavailable evidence {reference!r}.")
            evidence.append({
                "evidence_id": reference,
                "assertion": {"subject": item.assertion.subject, "predicate": item.assertion.predicate, "object": item.assertion.object},
                "source_chunks": [{
                    "document_id": source.document_id, "chunk_id": source.chunk_id,
                    "excerpt": source.text[:self.excerpt_chars], "truncated": len(source.text) > self.excerpt_chars,
                } for source in item.source_chunks[:2]],
            })
        return {"claim_id": claim.claim_id, "text": claim.text[:2000], "evidence": evidence,
                "evidence_omitted": max(0, len(claim.evidence_refs) - len(evidence))}

    @staticmethod
    def _validate(raw: str, expected: set[str]) -> dict[str, str]:
        payload = json.loads(raw)
        if not isinstance(payload, dict) or set(payload) != {"explanations"} or not isinstance(payload["explanations"], list):
            raise ValueError("Expected an object containing an explanations array.")
        values: dict[str, str] = {}
        for item in payload["explanations"]:
            if not isinstance(item, dict) or set(item) != {"contradiction_id", "explanation"}:
                raise ValueError("Malformed conflict explanation record.")
            identifier, explanation = item["contradiction_id"], item["explanation"]
            if not isinstance(identifier, str) or identifier not in expected or identifier in values:
                raise ValueError("Unknown or duplicate contradiction ID.")
            if not isinstance(explanation, str) or not explanation.strip():
                raise ValueError("Conflict explanation must be a nonempty string.")
            values[identifier] = explanation.strip()
        if set(values) != expected:
            raise ValueError("Missing contradiction explanations.")
        return values
