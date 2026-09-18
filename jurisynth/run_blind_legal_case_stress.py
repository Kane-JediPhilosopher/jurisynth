"""Run one frozen blind legal-case packet through production Jurisynth.

The runner deliberately reads only the blind packet.  It never opens the
sealed reference or rubric, which are evaluated after inference.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import time
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import psutil

from jurisynth.agentic_reasoner.llm import NIMConfig, OpenAICompatibleNIM
from jurisynth.main import build_global_workflow
from jurisynth.reasoning_log import ReasoningLog
from jurisynth.run_agentic_acceptance_smokes import (
    TraceSink,
    TracingInterpreter,
    TracingRetrievalMechanism,
    _nim_summary,
    _read_jsonl,
)


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, default=str, indent=2) + "\n",
        encoding="utf-8",
    )


class TracingLeafGenerator:
    """Record the deterministic prompt selection without changing it."""

    def __init__(self, inner: object, sink: TraceSink) -> None:
        self.inner = inner
        self.sink = sink

    async def __call__(self, node, dependency_answers, evidence):
        selected = self.inner._bounded_evidence(evidence)
        by_id = {item.evidence_id: item for item in evidence.evidence_items}
        selected_rows: list[dict[str, object]] = []
        for item in selected:
            source = by_id.get(str(item["evidence_id"]))
            origins = list(source.retrieval_origins) if source is not None else []
            selected_rows.append(
                {
                    "evidence_id": item["evidence_id"],
                    "modality": "chunk" if "chunk" in origins else "assertion",
                    "retrieval_origins": origins,
                    "source_documents": sorted(
                        {chunk.document_id for chunk in (source.source_chunks if source else [])}
                    ),
                }
            )
        self.sink.append(
            {
                "event": "leaf_prompt_evidence_selected",
                "query_id": node.query_id,
                "bundle_status": evidence.status,
                "bundle_evidence_count": len(evidence.evidence_items),
                "selected_count": len(selected_rows),
                "selected": selected_rows,
            }
        )
        return await self.inner(node, dependency_answers, evidence)


async def run(args: argparse.Namespace) -> dict[str, object]:
    from sentence_transformers import SentenceTransformer

    packet = json.loads(args.blind_packet.read_text(encoding="utf-8"))
    query = str(packet["inference_query"])
    args.output_dir.mkdir(parents=True, exist_ok=True)
    reasoning_path = args.output_dir / "reasoning.jsonl"
    trace_path = args.output_dir / "system_trace.jsonl"
    result_path = args.output_dir / "complete_run.json"
    manifest_path = args.output_dir / "run_manifest.json"
    if any(path.exists() for path in (reasoning_path, trace_path, result_path, manifest_path)):
        raise FileExistsError(f"Refusing to overwrite an existing run: {args.output_dir}")

    reasoning_log = ReasoningLog(reasoning_path, args.run_id)
    sink = TraceSink(trace_path)
    config = NIMConfig.from_environment()
    model = OpenAICompatibleNIM(config, reasoning_log=reasoning_log)
    manifest: dict[str, object] = {
        "status": "running",
        "run_id": args.run_id,
        "case_id": packet["case_id"],
        "started_at": datetime.now(UTC).isoformat(),
        "blind_packet": str(args.blind_packet),
        "sealed_reference_read_by_runner": False,
        "artifact_root": str(args.artifact_root),
        "community_dir": str(args.community_dir),
        "provider": config.base_url,
        "model": config.model,
        "decoding": {
            "temperature": 0,
            "top_p": 0.000001,
            "reasoning_effort": config.reasoning_effort,
            "output_token_limit": "provider_default",
            "request_timeout_seconds": config.request_timeout_seconds,
        },
        "retrieval_semantics_frozen": True,
        "production_code_changed": False,
        "contradiction_detector_status": (
            "disabled_for_case_study_after_cpu_cost_gate"
            if args.skip_contradiction_detection
            else "production_default"
        ),
    }
    _write(manifest_path, manifest)
    workflow = None
    try:
        workflow = build_global_workflow(
            artifact_root=args.artifact_root,
            community_dir=args.community_dir,
            model=model,
            embedder=SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True),
            reasoning_log=reasoning_log,
        )
        if args.skip_contradiction_detection:
            workflow.contradiction_detector = None
        mechanism = workflow.reasoner.retrieval_mech
        structured = mechanism.structured_retriever
        structured.interpreter = TracingInterpreter(structured.interpreter, sink, str(packet["case_id"]))
        workflow.reasoner.retrieval_mech = TracingRetrievalMechanism(
            mechanism, sink, str(packet["case_id"])
        )
        workflow.reasoner.leaf_answer_generator = TracingLeafGenerator(
            workflow.reasoner.leaf_answer_generator, sink
        )
        started = time.perf_counter()
        result = await workflow.run(query)
        wall = time.perf_counter() - started
        events = _read_jsonl(reasoning_path)
        traces = _read_jsonl(trace_path)
        payload: dict[str, object] = {
            "case_id": packet["case_id"],
            "original_query": query,
            "analysis": asdict(result.analysis),
            "ast": result.ast,
            "leaves": [asdict(item) for item in result.leaves],
            "dependency_edges": [
                {"from": dependency, "to": leaf.query_id}
                for leaf in result.leaves
                for dependency in leaf.dependency_ids
            ],
            "node_results": {
                query_id: {
                    "status": str(node.status),
                    "error": node.error,
                    "answer": asdict(node.answer) if node.answer is not None else None,
                }
                for query_id, node in result.node_results.items()
            },
            "contradictions": [asdict(item) for item in result.contradictions],
            "final_report": asdict(result.report) if result.report is not None else None,
            "presentation": result.presentation,
            "interpreter_traces": [
                item for item in traces if item.get("event") == "query_interpreted"
            ],
            "retrieval_traces": [
                item for item in traces if item.get("event") == "retrieval_completed_full"
            ],
            "prompt_selection_traces": [
                item for item in traces if item.get("event") == "leaf_prompt_evidence_selected"
            ],
            "nim": _nim_summary(events),
            "total_wall_seconds": round(wall, 3),
            "peak_rss_bytes": psutil.Process().memory_info().rss,
        }
        _write(result_path, payload)
        manifest.update(
            {
                "status": "completed",
                "finished_at": datetime.now(UTC).isoformat(),
                "total_wall_seconds": round(wall, 3),
                "nim": payload["nim"],
                "complete_run": str(result_path),
            }
        )
        _write(manifest_path, manifest)
        return manifest
    except Exception as exc:
        manifest.update(
            {
                "status": "failed",
                "finished_at": datetime.now(UTC).isoformat(),
                "error_type": type(exc).__name__,
                "error": repr(exc),
                "nim": _nim_summary(_read_jsonl(reasoning_path)),
            }
        )
        _write(manifest_path, manifest)
        raise
    finally:
        await model.aclose()
        if workflow is not None:
            expander = getattr(
                getattr(workflow.reasoner.retrieval_mech, "inner", workflow.reasoner.retrieval_mech),
                "image_expander",
                None,
            )
            if expander is not None:
                await expander.aclose()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--blind-packet",
        type=Path,
        default=Path(
            "jurisynth/evaluation_artifacts/blind_legal_case_stress_20260918/blind_case_packet.json"
        ),
    )
    parser.add_argument(
        "--artifact-root",
        type=Path,
        default=Path("jurisynth/global_artifacts_source_uri_v2"),
    )
    parser.add_argument(
        "--community-dir",
        type=Path,
        default=Path("jurisynth/global_artifacts_source_uri_v2/community"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(
            "jurisynth/evaluation_artifacts/blind_legal_case_stress_20260918/live_run"
        ),
    )
    parser.add_argument("--run-id", default="blind_legal_case_stress_20260918")
    parser.add_argument("--minimum-available-gb", type=float, default=5.5)
    parser.add_argument(
        "--skip-contradiction-detection",
        action="store_true",
        help=(
            "Evaluation-only CPU cost gate. It does not alter the production "
            "contradiction implementation."
        ),
    )
    args = parser.parse_args()
    available = psutil.virtual_memory().available / 1024**3
    if available < args.minimum_available_gb:
        raise RuntimeError(
            f"Need {args.minimum_available_gb:g} GB available RAM; found {available:.2f} GB."
        )
    result = asyncio.run(run(args))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
