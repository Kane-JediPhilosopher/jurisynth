import json

import asyncio

from jurisynth.agentic_reasoner.models import Claim, LeafAnswer, LeafNode
from jurisynth.agentic_reasoner.reasoner import AgenticReasoner
from jurisynth.contracts import EvidenceBundle
from jurisynth.reasoning_log import ReasoningLog


def test_reasoning_log_is_append_only_jsonl_and_serializes_contracts(tmp_path):
    log = ReasoningLog(tmp_path / "run.jsonl", "run-001")
    log.record("node_started", query_id="q001", state="running")
    log.record("retrieval_completed", query_id="q001", bundle=EvidenceBundle("q001", "empty"), duration_ms=12)

    records = [json.loads(line) for line in (tmp_path / "run.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [record["event"] for record in records] == ["node_started", "retrieval_completed"]
    assert all(record["run_id"] == "run-001" for record in records)
    assert records[1]["bundle"]["status"] == "empty"


def test_reasoner_records_execution_events(tmp_path):
    class Retriever:
        async def retrieve_evidence(self, request):
            return EvidenceBundle(request.query_id, "empty")

    async def generate(node, dependencies, evidence):
        return LeafAnswer(node.query_id, "insufficient_evidence", "No support.", [Claim(None, "No support.", [], "insufficient_evidence")], evidence)

    path = tmp_path / "reasoner.jsonl"
    reasoner = AgenticReasoner(Retriever(), generate, reasoning_log=ReasoningLog(path, "run-002"))
    asyncio.run(reasoner.execute_leaves([LeafNode("q001", "test query")]))

    events = [json.loads(line)["event"] for line in path.read_text(encoding="utf-8").splitlines()]
    assert events == ["plan_started", "node_started", "retrieval_completed", "leaf_generation_completed", "node_completed", "plan_completed"]


def test_workflow_records_routing_and_leaf_plan(tmp_path):
    from jurisynth.agentic_reasoner.workflow import AgenticWorkflow, TaskAnalysis

    class Analyzer:
        async def analyze(self, query):
            return TaskAnalysis("direct", ("context",), {"jurisdiction": "EU"})

    class Retriever:
        async def retrieve_evidence(self, request):
            return EvidenceBundle(request.query_id, "empty")

    async def generate(node, dependencies, evidence):
        return LeafAnswer(node.query_id, "insufficient_evidence", "No support.", [], evidence)

    path = tmp_path / "workflow.jsonl"
    log = ReasoningLog(path, "run-003")
    workflow = AgenticWorkflow(Analyzer(), AgenticReasoner(Retriever(), generate, reasoning_log=log), reasoning_log=log)
    asyncio.run(workflow.run("question"))

    events = [json.loads(line)["event"] for line in path.read_text(encoding="utf-8").splitlines()]
    assert events == ["task_analyzed", "leaf_plan_ready", "plan_started", "node_started", "retrieval_completed", "leaf_generation_completed", "node_completed", "plan_completed", "workflow_completed"]
