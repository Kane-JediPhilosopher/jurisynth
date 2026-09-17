"""Run a bounded, observation-only end-to-end Jurisynth acceptance suite.

This harness does not alter Retrieval Mech configuration or semantics.  It
wraps the production Query Interpreter and retrieval boundary only to persist
their inputs and outputs for post-run adjudication.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import time
from dataclasses import asdict, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import psutil

from jurisynth.agentic_reasoner.llm import NIMConfig, OpenAICompatibleNIM
from jurisynth.main import build_global_workflow
from jurisynth.reasoning_log import ReasoningLog


CASES: tuple[dict[str, Any], ...] = (
    {
        "case_id": "simple_ai_act",
        "kind": "simple_single_instrument",
        "query": "Under Regulation (EU) 2024/1689 (AI Act), what obligations apply to providers of high-risk AI systems?",
        "expected_documents": ["L_202401689EN"],
    },
    {
        "case_id": "frozen_q003",
        "kind": "frozen_q003",
        "query": (
            "What are the specific pre-market and post-market obligations under the AI Act for the non-EU "
            "manufacturer/provider, the EU importer, the EU distributor, and the healthcare organisation "
            "deploying an AI-enabled medical device, distinguishing obligations before placement on the "
            "market from those continuing after deployment?"
        ),
        "expected_documents": ["L_202401689EN"],
    },
    {
        "case_id": "dependent_role_then_duties",
        "kind": "dependent_multi_leaf",
        "query": (
            "First determine which regulated role an EU hospital assumes under Regulation (EU) 2024/1689 "
            "when it substantially modifies an imported high-risk AI medical system. Then, using that "
            "identified role, determine which obligations under the AI Act apply to the hospital. Cite the "
            "supporting provisions and distinguish direct rules from inference."
        ),
        "expected_documents": ["L_202401689EN"],
        "requires_dependency_edge": True,
    },
    {
        "case_id": "parallel_ai_act_gdpr",
        "kind": "parallel_multi_issue",
        "query": (
            "Answer these independent questions separately: (1) Under Regulation (EU) 2024/1689, what "
            "obligations apply to providers of high-risk AI systems? (2) Under Regulation (EU) 2016/679 "
            "Article 13, what information must a controller provide to a data subject?"
        ),
        "expected_documents": ["L_202401689EN", "L_2016119EN.01000101"],
        "requires_parallel_roots": True,
    },
    {
        "case_id": "cross_ai_act_ivdr",
        "kind": "cross_instrument",
        "query": (
            "How do provider obligations under Regulation (EU) 2024/1689 (AI Act) interact with manufacturer "
            "obligations under Regulation (EU) 2017/746 (IVDR) for an AI-enabled in vitro diagnostic device? "
            "Do not imply that compliance with one instrument establishes compliance with the other."
        ),
        "expected_documents": ["L_202401689EN", "L_2017117EN.01017601"],
    },
    {
        "case_id": "table_primary",
        "kind": "table_primary",
        "query": (
            "In document L_2010041EN.01000801, what does table 10 show for 'Metier*Fleet segment (Cell)', "
            "'Metier', and 'Fleet segment' across the displayed geographic aggregation levels? Base the answer "
            "on the table and say if the rows do not establish a legal conclusion."
        ),
        "expected_documents": ["L_2010041EN.01000801"],
        "expected_table": ["L_2010041EN.01000801", "table_10"],
    },
    {
        "case_id": "image_primary",
        "kind": "image_primary",
        "query": (
            "What is visibly shown in Image 1 of document L_1994001EN.01000101? Treat the image only as "
            "auxiliary visual material and do not infer any legal effect or identity that is not visible."
        ),
        "expected_documents": ["L_1994001EN.01000101"],
        "expected_image": "L_1994001EN.01000101:image:001",
    },
    {
        "case_id": "negative_nonexistent_instrument",
        "kind": "negative_no_answer",
        "query": (
            "Under the fictional Regulation (EU) 2099/9999, what does Article 999 require every lunar-data "
            "controller to report? If the retrieved corpus does not establish this, explicitly say so and do "
            "not construct an answer from other instruments."
        ),
        "expected_documents": [],
        "expects_weak_or_insufficient": True,
    },
)


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, default=str, indent=2) + "\n", encoding="utf-8")


class TraceSink:
    def __init__(self, path: Path) -> None:
        self.path = path

    def append(self, record: dict[str, object]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


class TracingInterpreter:
    def __init__(self, inner: object, sink: TraceSink, case_id: str) -> None:
        self.inner = inner
        self.sink = sink
        self.case_id = case_id

    async def interpret(self, request):
        started = time.perf_counter()
        entities, relations = await self.inner.interpret(request)
        self.sink.append({
            "event": "query_interpreted",
            "case_id": self.case_id,
            "query_id": request.query_id,
            "leaf_query": request.leaf_query,
            "elapsed_seconds": round(time.perf_counter() - started, 3),
            "entity_concepts": [asdict(item) for item in entities],
            "relation_concepts": [asdict(item) for item in relations],
            "retrieval_config": request.retrieval_config,
        })
        return entities, relations


class TracingRetrievalMechanism:
    def __init__(self, inner: object, sink: TraceSink, case_id: str) -> None:
        self.inner = inner
        self.sink = sink
        self.case_id = case_id

    async def retrieve_evidence(self, request):
        started = time.perf_counter()
        bundle = await self.inner.retrieve_evidence(request)
        self.sink.append({
            "event": "retrieval_completed_full",
            "case_id": self.case_id,
            "elapsed_seconds": round(time.perf_counter() - started, 3),
            "request": asdict(request),
            "bundle": asdict(bundle),
        })
        return bundle


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _nim_summary(events: list[dict[str, object]]) -> dict[str, object]:
    starts = [item for item in events if item.get("event") == "nim_request_started"]
    completed = [item for item in events if item.get("event") == "nim_request_completed"]
    retries = [item for item in events if item.get("event") == "nim_retry_scheduled"]
    failures = [item for item in events if item.get("event") in {"nim_request_failed", "nim_retries_exhausted"}]
    return {
        "attempt_count": len(starts),
        "completed_attempts": len(completed),
        "retry_count": len(retries),
        "failure_count": len(failures),
        "completed_seconds": round(sum(float(item.get("elapsed_seconds", 0.0)) for item in completed), 3),
        "retries": retries,
        "failures": failures,
    }


def _case_summary(case: dict[str, Any], result: object, traces: list[dict[str, object]], events: list[dict[str, object]], wall: float) -> dict[str, object]:
    node_results = result.node_results
    leaves = [asdict(item) for item in result.leaves]
    retrieval_traces = [item for item in traces if item.get("event") == "retrieval_completed_full"]
    evidence_documents = sorted({
        chunk["document_id"]
        for trace in retrieval_traces
        for item in trace["bundle"].get("evidence_items", [])
        for chunk in item.get("source_chunks", [])
    })
    table_documents = sorted({
        item["document_id"]
        for trace in retrieval_traces
        for item in trace["bundle"].get("table_evidence", [])
    })
    image_documents = sorted({
        item["document_id"]
        for trace in retrieval_traces
        for item in trace["bundle"].get("image_evidence", [])
    })
    expected = set(case.get("expected_documents", []))
    covered = expected.intersection(evidence_documents + table_documents + image_documents)
    node_payload: dict[str, object] = {}
    unsupported_claims: list[dict[str, str]] = []
    for query_id, node in node_results.items():
        answer = node.answer
        if answer is None:
            node_payload[query_id] = {"status": str(node.status), "error": node.error}
            continue
        evidence_ids = {item.evidence_id for item in answer.evidence_bundle.evidence_items}
        claims = [asdict(item) for item in answer.claims]
        for claim in answer.claims:
            missing = [ref for ref in claim.evidence_refs if ref not in evidence_ids]
            if missing or (claim.status == "supported" and not claim.evidence_refs):
                unsupported_claims.append({"query_id": query_id, "claim_id": claim.claim_id or "", "reason": "missing evidence reference"})
        node_payload[query_id] = {
            "status": str(node.status),
            "error": node.error,
            "answer_status": answer.status,
            "answer_text": answer.answer_text,
            "claims": claims,
            "retrieval_status": answer.evidence_bundle.status,
            "community_summary": answer.evidence_bundle.community_summary,
        }
    node_started = [item for item in events if item.get("event") == "node_started"]
    return {
        "case_id": case["case_id"],
        "kind": case["kind"],
        "original_query": case["query"],
        "analysis": asdict(result.analysis),
        "ast": result.ast,
        "leaves": leaves,
        "dependency_edges": [
            {"from": dep, "to": leaf["query_id"]}
            for leaf in leaves for dep in leaf.get("dependency_ids", [])
        ],
        "scheduling_order": [
            {"query_id": item.get("query_id"), "timestamp": item.get("timestamp")}
            for item in node_started
        ],
        "interpreter_traces": [item for item in traces if item.get("event") == "query_interpreted"],
        "retrieval_traces": retrieval_traces,
        "node_results": node_payload,
        "contradictions": [asdict(item) for item in result.contradictions],
        "final_report": asdict(result.report) if result.report is not None else None,
        "expected_documents": sorted(expected),
        "covered_expected_documents": sorted(covered),
        "source_coverage": 1.0 if not expected else len(covered) / len(expected),
        "retrieved_documents_by_modality": {
            "assertion_or_chunk": evidence_documents,
            "table": table_documents,
            "image": image_documents,
        },
        "mechanical_unsupported_claims": unsupported_claims,
        "nim": _nim_summary(events),
        "total_wall_seconds": round(wall, 3),
    }


async def run_suite(args: argparse.Namespace) -> dict[str, object]:
    from sentence_transformers import SentenceTransformer

    args.output_dir.mkdir(parents=True, exist_ok=True)
    reasoning_path = args.output_dir / "reasoning.jsonl"
    trace_path = args.output_dir / "retrieval_trace.jsonl"
    if any(path.exists() for path in (reasoning_path, trace_path, args.output_dir / "summary.json")):
        raise FileExistsError(f"Refusing to overwrite an existing smoke run: {args.output_dir}")
    reasoning_log = ReasoningLog(reasoning_path, args.run_id)
    sink = TraceSink(trace_path)
    config = NIMConfig.from_environment()
    # Compatibility runs are deliberately process-local.  They never update the
    # frozen Ultra dotenv configuration or any retrieval configuration.
    if args.model is not None:
        config = replace(config, model=args.model)
    if args.api_key_env is not None:
        alternate_key = os.environ.get(args.api_key_env, "")
        if not alternate_key:
            raise RuntimeError(f"Environment variable {args.api_key_env!r} is not set.")
        config = replace(config, api_key=alternate_key)
    config = replace(config, request_timeout_seconds=None)
    model = OpenAICompatibleNIM(config, reasoning_log=reasoning_log)
    suite: dict[str, object] = {
        "status": "running",
        "run_id": args.run_id,
        "started_at": datetime.now(UTC).isoformat(),
        "artifact_root": str(args.artifact_root),
        "per_case_timeout_seconds": args.case_timeout_seconds,
        "model": config.model,
        "api_key_environment_variable": args.api_key_env or "JURISYNTH_NIM_API_KEY",
        "temporary_compatibility_run": bool(args.temporary_compatibility),
        "retrieval_semantics_frozen": True,
        "cases": [],
    }
    _write(args.output_dir / "summary.json", suite)
    try:
        workflow = build_global_workflow(
            artifact_root=args.artifact_root,
            community_dir=args.community_dir,
            model=model,
            embedder=SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True),
            reasoning_log=reasoning_log,
        )
        mechanism = workflow.reasoner.retrieval_mech
        structured = mechanism.structured_retriever
        production_interpreter = structured.interpreter
        for case in CASES:
            case_id = str(case["case_id"])
            structured.interpreter = TracingInterpreter(production_interpreter, sink, case_id)
            workflow.reasoner.retrieval_mech = TracingRetrievalMechanism(mechanism, sink, case_id)
            before_events = len(_read_jsonl(reasoning_path))
            before_traces = len(_read_jsonl(trace_path))
            started = time.perf_counter()
            try:
                result = await asyncio.wait_for(workflow.run(str(case["query"])), timeout=args.case_timeout_seconds)
                status = "completed"
                error = None
            except TimeoutError:
                result = None
                status = "timed_out"
                error = f"Per-case deadline of {args.case_timeout_seconds:g}s exceeded."
            except Exception as exc:
                result = None
                status = "failed"
                error = repr(exc)
            wall = time.perf_counter() - started
            current_events = _read_jsonl(reasoning_path)[before_events:]
            current_traces = _read_jsonl(trace_path)[before_traces:]
            if result is None:
                case_result = {
                    "case_id": case_id,
                    "kind": case["kind"],
                    "original_query": case["query"],
                    "status": status,
                    "error": error,
                    "partial_traces": current_traces,
                    "events": current_events,
                    "nim": _nim_summary(current_events),
                    "total_wall_seconds": round(wall, 3),
                }
            else:
                case_result = _case_summary(case, result, current_traces, current_events, wall)
                case_result["status"] = status
            _write(args.output_dir / f"{case_id}.json", case_result)
            suite["cases"].append({
                "case_id": case_id,
                "kind": case["kind"],
                "status": status,
                "wall_seconds": round(wall, 3),
                "output": str(args.output_dir / f"{case_id}.json"),
            })
            _write(args.output_dir / "summary.json", suite)
            workflow.reasoner.retrieval_mech = mechanism
            structured.interpreter = production_interpreter
            nim = case_result["nim"]
            if (
                status == "timed_out"
                and not current_traces
                and int(nim["completed_attempts"]) == 0
                and int(nim["retry_count"]) > 0
            ):
                suite["status"] = "halted_provider_unavailable"
                suite["halt_reason"] = (
                    "A case exhausted its watchdog before any NIM completion or retrieval trace; "
                    "remaining cases were skipped to avoid duplicating an upstream failure."
                )
                break
        if suite["status"] == "running":
            suite["status"] = "completed"
        suite["finished_at"] = datetime.now(UTC).isoformat()
        return suite
    finally:
        await model.aclose()
        expander = getattr(mechanism, "image_expander", None) if "mechanism" in locals() else None
        if expander is not None:
            await expander.aclose()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, default=Path("jurisynth/global_artifacts_source_uri_v2"))
    parser.add_argument("--community-dir", type=Path, default=Path("jurisynth/global_artifacts_source_uri_v2/community"))
    parser.add_argument("--output-dir", type=Path, default=Path("jurisynth/run_outputs/agentic_acceptance_20260917"))
    parser.add_argument("--run-id", default="agentic_acceptance_20260917")
    parser.add_argument("--case-timeout-seconds", type=float, default=900.0)
    parser.add_argument("--minimum-available-gb", type=float, default=5.5)
    parser.add_argument("--model", help="Process-local NIM model override; does not alter the frozen Ultra configuration.")
    parser.add_argument("--api-key-env", help="Environment variable holding the API key for --model; the value is never logged.")
    parser.add_argument("--temporary-compatibility", action="store_true", help="Label this run as a non-benchmark alternate-model compatibility check.")
    args = parser.parse_args()
    if args.case_timeout_seconds <= 0:
        parser.error("--case-timeout-seconds must be positive")
    available = psutil.virtual_memory().available / 1024**3
    if available < args.minimum_available_gb:
        raise RuntimeError(f"Need {args.minimum_available_gb:g} GB available RAM; found {available:.2f} GB.")
    suite = asyncio.run(run_suite(args))
    _write(args.output_dir / "summary.json", suite)
    print(json.dumps({"output": str(args.output_dir), "status": suite["status"]}, indent=2))


if __name__ == "__main__":
    main()
