"""Composable Agentic Reasoner core, deliberately separate from LLM/QCompiler adapters."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

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

    async def execute_leaves(self, leaves: list[LeafNode]) -> dict[str, NodeResult]:
        async def execute_leaf(node: LeafNode, dependency_answers: list[LeafAnswer]):
            request = RetrievalRequest(
                query_id=node.query_id,
                leaf_query=node.query,
                contextual_facts=list(node.contextual_facts),
                constraints=node.constraints,
                dependency_claims=[
                    {"claim_id": claim.claim_id, "text": claim.text, "status": claim.status}
                    for answer in dependency_answers
                    for claim in answer.claims
                ],
            )
            evidence = await self.retrieval_mech.retrieve_evidence(request)
            answer = await self.leaf_answer_generator(node, dependency_answers, evidence)
            if answer.query_id != node.query_id:
                raise ValueError("Leaf answer query_id does not match its scheduled node")
            return validate_leaf_answer(answer)

        return await execute_dependency_plan(
            leaves, execute_leaf, max_concurrency=self.max_concurrency
        )
