"""Composable Agentic Reasoner core, deliberately separate from LLM/QCompiler adapters."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
import re
import asyncio
from time import monotonic

from jurisynth.agentic_reasoner.claim_validation import validate_leaf_answer
from jurisynth.agentic_reasoner.models import LeafAnswer, LeafNode, NodeResult
from jurisynth.agentic_reasoner.scheduler import execute_dependency_plan
from jurisynth.contracts import RetrievalRequest


LeafAnswerGenerator = Callable[[LeafNode, list, object], Awaitable[LeafAnswer]]


@dataclass(slots=True)
class AgenticReasoner:
    """Schedules leaves and sees Retrieval Mech only through retrieve_evidence."""

    retrieval_mech: object
    leaf_answer_generator: LeafAnswerGenerator
    max_concurrency: int = 4
    reasoning_log: object | None = None
    event_queue: asyncio.Queue[dict[str, object]] | None = None

    async def execute_leaves(self, leaves: list[LeafNode]) -> dict[str, NodeResult]:
        self._record("plan_started", leaf_count=len(leaves), query_ids=[node.query_id for node in leaves])

        async def execute_leaf(node: LeafNode, dependency_answers: list[LeafAnswer]):
            self._record("node_started", query_id=node.query_id, dependency_ids=node.dependency_ids)
            try:
                materialized_query, substitutions = materialize_dependency_query(node, dependency_answers)
                if substitutions:
                    self._record(
                        "dependency_query_materialized",
                        query_id=node.query_id,
                        substitutions=substitutions,
                    )
                request = RetrievalRequest(
                    query_id=node.query_id,
                    leaf_query=materialized_query,
                    contextual_facts=list(node.contextual_facts),
                    constraints=node.constraints,
                    dependency_claims=[
                        {"claim_id": claim.claim_id, "text": claim.text, "status": claim.status}
                        for answer in dependency_answers
                        for claim in answer.claims
                    ],
                    dependency_substitutions=substitutions,
                )
                retrieval_started = monotonic()
                evidence = await self.retrieval_mech.retrieve_evidence(request)
                self._record(
                    "retrieval_completed",
                    query_id=node.query_id,
                    retrieval_status=evidence.status,
                    duration_ms=round((monotonic() - retrieval_started) * 1000, 2),
                    evidence_ids=[item.evidence_id for item in evidence.evidence_items],
                    table_ids=[item.table_id for item in evidence.table_evidence],
                )
                generation_started = monotonic()
                answer = await self.leaf_answer_generator(node, dependency_answers, evidence)
                self._record(
                    "leaf_generation_completed",
                    query_id=node.query_id,
                    duration_ms=round((monotonic() - generation_started) * 1000, 2),
                )
                if answer.query_id != node.query_id:
                    raise ValueError("Leaf answer query_id does not match its scheduled node")
                answer = validate_leaf_answer(answer)
            except Exception as exc:
                self._record("node_failed", query_id=node.query_id, error=repr(exc))
                raise
            self._record("node_completed", query_id=node.query_id, claim_ids=[claim.claim_id for claim in answer.claims])
            return answer

        results = await execute_dependency_plan(
            leaves, execute_leaf, max_concurrency=self.max_concurrency
        )
        self._record(
            "plan_completed",
            node_statuses={query_id: result.status for query_id, result in results.items()},
        )
        return results

    def _record(self, event: str, **payload: object) -> None:
        if self.reasoning_log is not None:
            self.reasoning_log.record(event, **payload)
        if self.event_queue is not None:
            self.event_queue.put_nowait({
                "event": event.upper(),
                **{key: payload[key] for key in ("query_id", "retrieval_status") if key in payload},
            })


_PLACEHOLDER = re.compile(r"\{[^{}]+\}")
_MAX_DEPENDENCY_CONTEXT_CHARS = 1_200


def materialize_dependency_query(node: LeafNode, answers: list[LeafAnswer]) -> tuple[str, list[dict[str, str]]]:
    """Replace QCompiler dependency placeholders with bounded completed answers.

    The original AST leaf remains unchanged for provenance. The retrieval request
    carries the substituted query and compact audit trail.
    """
    if not answers or not _PLACEHOLDER.search(node.query):
        return node.query, []
    context = " ".join(answer.answer_text.strip() for answer in answers if answer.answer_text.strip())
    context = context[:_MAX_DEPENDENCY_CONTEXT_CHARS]
    if not context:
        return node.query, []
    substitutions: list[dict[str, str]] = []

    def replace(match: re.Match[str]) -> str:
        placeholder = match.group(0)
        substitutions.append({"placeholder": placeholder, "replacement": context})
        return context

    return _PLACEHOLDER.sub(replace, node.query), substitutions
