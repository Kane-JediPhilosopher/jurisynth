"""Structured intake, routing, dependency planning, and report orchestration."""

from __future__ import annotations

import json
import asyncio
from dataclasses import dataclass
from typing import Literal, Protocol

from jurisynth.agentic_reasoner.llm import ChatModel
from jurisynth.agentic_reasoner.models import LeafNode, NodeResult, NodeStatus
from jurisynth.agentic_reasoner.qcompiler_translator import QCompilerTranslator
from jurisynth.agentic_reasoner.dependency_planner import SemanticDependencyPlanner
from jurisynth.agentic_reasoner.reporting import FinalReport, FinalReportSynthesizer, progressive_disclosure_payload
from jurisynth.agentic_reasoner.reasoner import AgenticReasoner
from jurisynth.agentic_reasoner.intake import ConversationTurn, NIMConversationIntake
from jurisynth.agentic_reasoner.schemas import TASK_ANALYSIS_SCHEMA


Route = Literal["direct", "complex"]


@dataclass(frozen=True, slots=True)
class TaskAnalysis:
    route: Route
    contextual_facts: tuple[str, ...]
    constraints: dict[str, object]


@dataclass(frozen=True, slots=True)
class WorkflowResult:
    analysis: TaskAnalysis
    leaves: tuple[LeafNode, ...]
    node_results: dict[str, NodeResult]
    report: FinalReport | None
    contradictions: tuple[object, ...] = ()
    presentation: dict[str, object] | None = None
    clarification_question: str | None = None
    clarification: dict[str, object] | None = None
    ast: dict[str, object] | None = None


@dataclass(slots=True)
class NIMTaskAnalyzer:
    model: ChatModel
    max_tokens: int = 400

    async def analyze(self, user_query: str) -> TaskAnalysis:
        response = await self.model.complete(system=_TASK_ANALYSIS_PROMPT, user=user_query, max_tokens=self.max_tokens, response_schema=TASK_ANALYSIS_SCHEMA)
        try:
            payload = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError("Task analysis response is not valid JSON.") from exc
        if not isinstance(payload, dict) or payload.get("route") not in {"direct", "complex"}:
            raise ValueError("Task analysis must declare route 'direct' or 'complex'.")
        facts = payload.get("contextual_facts", [])
        constraints = payload.get("constraints", {})
        if not isinstance(facts, list) or not all(isinstance(fact, str) for fact in facts) or not isinstance(constraints, dict):
            raise ValueError("Task analysis has malformed facts or constraints.")
        return TaskAnalysis(payload["route"], tuple(fact.strip() for fact in facts if fact.strip()), constraints)


_TASK_ANALYSIS_PROMPT = """Classify the user's legal-information request. Return JSON only:
{"route":"direct|complex","contextual_facts":["..."],"constraints":{}}.
Use direct for one independent information need; use complex only when it needs
multiple dependent or parallel subquestions. Extract stated facts/constraints
only. Do not answer the question or create retrieval terms."""


class TaskAnalyzer(Protocol):
    async def analyze(self, user_query: str) -> TaskAnalysis: ...


@dataclass(slots=True)
class AgenticWorkflow:
    analyzer: TaskAnalyzer
    reasoner: AgenticReasoner
    translator: QCompilerTranslator | None = None
    dependency_planner: SemanticDependencyPlanner | None = None
    synthesizer: FinalReportSynthesizer | None = None
    contradiction_detector: object | None = None
    intake: NIMConversationIntake | None = None
    reasoning_log: object | None = None
    event_queue: asyncio.Queue[dict[str, object]] | None = None
    conflict_explainer: object | None = None

    def __post_init__(self) -> None:
        if self.event_queue is not None:
            self.reasoner.event_queue = self.event_queue

    async def stream(self, user_query: str):
        """Yield opt-in orchestration events without changing ``run`` semantics."""
        queue = self.event_queue or asyncio.Queue()
        previous = self.event_queue
        self.event_queue = queue
        self.reasoner.event_queue = queue
        task = asyncio.create_task(self.run(user_query))
        try:
            while not task.done():
                try:
                    yield await asyncio.wait_for(queue.get(), timeout=0.05)
                except TimeoutError:
                    pass
            while not queue.empty():
                yield queue.get_nowait()
            result = await task
            yield {"event": "SYNTHESIS_READY", "report_generated": result.report is not None}
        finally:
            self.event_queue = previous
            self.reasoner.event_queue = previous

    async def run(self, user_query: str, *, history: tuple[ConversationTurn, ...] = ()) -> WorkflowResult:
        intake_facts: tuple[str, ...] = ()
        intake_constraints: dict[str, object] = {}
        analysis: TaskAnalysis | None = None
        if self.intake is not None:
            combined = getattr(self.intake, "decide_and_analyze", None)
            if callable(combined):
                decision = await combined(user_query, history)
                analysis = TaskAnalysis(
                    decision.route,
                    decision.contextual_facts,
                    decision.constraints,
                )
            else:
                decision = await self.intake.decide(user_query, history)
            intake_facts, intake_constraints = decision.contextual_facts, decision.constraints
            if decision.action == "clarify":
                clarification_analysis = analysis or TaskAnalysis("direct", intake_facts, intake_constraints)
                self._record("clarification_requested")
                return WorkflowResult(
                    clarification_analysis, (), {}, None,
                    clarification_question=decision.clarification_question,
                    clarification=decision.user_response(), ast=None,
                )
        if analysis is None:
            analyzed = await self.analyzer.analyze(user_query)
            analysis = TaskAnalysis(
                analyzed.route,
                tuple(dict.fromkeys((*intake_facts, *analyzed.contextual_facts))),
                {**intake_constraints, **analyzed.constraints},
            )
        self._record("task_analyzed", route=analysis.route, contextual_fact_count=len(analysis.contextual_facts), constraints=analysis.constraints)
        if analysis.route == "direct":
            leaves = (LeafNode("q001", user_query, contextual_facts=analysis.contextual_facts, constraints=analysis.constraints),)
            ast_guidance: dict[str, object] = {"type": "AtomicQuery", "query": user_query, "children": []}
        else:
            if self.translator is None:
                raise RuntimeError("Complex task routing requires a QCompiler translator.")
            compilation = await self.translator.compile(user_query, contextual_facts=analysis.contextual_facts)
            leaves = tuple(
                LeafNode(
                    leaf.query_id,
                    leaf.query,
                    leaf.dependency_ids,
                    leaf.contextual_facts,
                    {**analysis.constraints, **leaf.constraints},
                    leaf.optional_dependency_ids,
                )
                for leaf in compilation.leaves
            )
            if self.dependency_planner is not None:
                leaves = await self.dependency_planner.plan(leaves)
            ast_guidance = compilation.ast
            self._record("qcompiler_compiled", expression=compilation.expression, validation_attempts=compilation.attempts)
        self._record(
            "leaf_plan_ready",
            leaves=[{"query_id": leaf.query_id, "dependency_ids": list(leaf.dependency_ids)} for leaf in leaves],
        )
        results = await self.reasoner.execute_leaves(list(leaves))
        completed = [results[leaf.query_id].answer for leaf in leaves if results[leaf.query_id].status == NodeStatus.COMPLETE]
        contradictions: tuple[object, ...] = ()
        if self.contradiction_detector is not None and completed:
            try:
                evidence_bundles = [answer.evidence_bundle for answer in completed]
                contradictions = tuple(await self.contradiction_detector.detect(evidence_bundles))
                self._record(
                    "contradiction_detection_completed",
                    contradiction_ids=[item.contradiction_id for item in contradictions],
                    raw_retrieved_assertion_count=getattr(self.contradiction_detector, "last_raw_assertion_count", None),
                    unique_assertion_count=getattr(self.contradiction_detector, "last_unique_assertion_count", None),
                    candidate_pair_count=getattr(self.contradiction_detector, "last_candidate_count", None),
                    flagged_pair_count=len(contradictions),
                    scorer=getattr(getattr(self.contradiction_detector, "scorer", None), "name", None),
                    metrics=getattr(self.contradiction_detector, "last_metrics", None),
                )
            except Exception as exc:
                self._record("contradiction_detection_failed", error=repr(exc))
        if self.conflict_explainer is not None and contradictions:
            try:
                contradictions = tuple(await self.conflict_explainer.explain(list(contradictions), completed))
                self._record("contradiction_explanation_completed", contradiction_ids=[item.contradiction_id for item in contradictions])
            except Exception as exc:
                self._record("contradiction_explanation_failed", error=repr(exc))
        report = await self.synthesizer.synthesize(
            user_query,
            completed,
            contradictions=list(contradictions),
            structural_guidance=[
                {"query_id": leaf.query_id, "query": leaf.query, "dependency_ids": list(leaf.dependency_ids)}
                for leaf in leaves
            ] + [{"qcompiler_ast": ast_guidance}],
        ) if self.synthesizer and completed else None
        presentation = progressive_disclosure_payload(report, completed) if isinstance(report, FinalReport) else None
        self._record(
            "workflow_completed",
            node_statuses={query_id: str(result.status) for query_id, result in results.items()},
            report_generated=report is not None,
        )
        return WorkflowResult(analysis, leaves, results, report, contradictions, presentation, ast=ast_guidance)

    def _record(self, event: str, **payload: object) -> None:
        if self.reasoning_log is not None:
            self.reasoning_log.record(event, **payload)
        if self.event_queue is not None:
            self.event_queue.put_nowait({"event": event.upper()})
