"""Run the bounded live-NIM follow-up to the frozen retrieval ablation.

This harness replays the frozen direct-route analysis and Query Interpreter
concepts, varies only the enabled retrieval channels, and invokes the normal
leaf-answer and final-report generators. It does not mutate production code or
the formal eight-case retrieval ablation.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import statistics
import time
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any

from jurisynth.agentic_reasoner.llm import (
    EvidenceGroundedLeafGenerator,
    NIMConfig,
    OpenAICompatibleNIM,
)
from jurisynth.agentic_reasoner.reasoner import AgenticReasoner
from jurisynth.agentic_reasoner.reporting import FinalReportSynthesizer
from jurisynth.agentic_reasoner.workflow import AgenticWorkflow, TaskAnalysis
from jurisynth.main import _load_community_guidance
from jurisynth.reasoning_log import ReasoningLog
from jurisynth.retrieval_mech.config import GLOBAL_MAX_QUADS_PER_SEED
from jurisynth.retrieval_mech.er_matcher import ERMatcher, PersistedERIndices
from jurisynth.retrieval_mech.global_artifacts import load_global_artifacts
from jurisynth.retrieval_mech.mechanism import RetrievalMechanism
from jurisynth.retrieval_mech.rdf_retriever import DirectRDFRetriever
from jurisynth.run_retrieval_ablation import CapturedConceptInterpreter


ARMS = ("kg_only", "chunk_only", "hybrid")
SELECTED_CASES: dict[str, str] = {
    "global_natural_002": (
        "Chunk-only recovered the strict gold; hybrid added assertions and "
        "changed retrieval status from weak to success."
    ),
    "global_natural_010": (
        "Strong corroboration stress case: strict chunk recovery plus 24 "
        "structured assertions and a weak-to-success status change."
    ),
    "global_natural_011": (
        "Both channels recovered the correct document and the KG supplied a "
        "road-load assertion although no arm recovered the exact gold chunk."
    ),
    "global_natural_005": (
        "Difficult all-arm strict miss used to test abstention and fabrication."
    ),
}


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, default=str, indent=2) + "\n", encoding="utf-8")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


@dataclass(slots=True)
class CapturedAnalyzer:
    contextual_facts: tuple[str, ...]
    constraints: dict[str, object]

    async def analyze(self, _user_query: str) -> TaskAnalysis:
        return TaskAnalysis("direct", self.contextual_facts, self.constraints)


@dataclass(slots=True)
class TracingRetrieval:
    inner: RetrievalMechanism
    last_bundle: object | None = None
    elapsed_seconds: float | None = None

    async def retrieve_evidence(self, request):
        started = time.perf_counter()
        self.last_bundle = await self.inner.retrieve_evidence(request)
        self.elapsed_seconds = time.perf_counter() - started
        return self.last_bundle


def _arm_order(index: int) -> tuple[str, str, str]:
    offset = index % 3
    return ARMS[offset:] + ARMS[:offset]


def _nim_summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    starts = [item for item in events if item.get("event") == "nim_request_started"]
    completions = [item for item in events if item.get("event") == "nim_request_completed"]
    retries = [item for item in events if item.get("event") == "nim_retry_scheduled"]
    failures = [
        item for item in events
        if item.get("event") in {"nim_request_failed", "nim_retries_exhausted", "nim_request_cancelled"}
    ]
    by_schema: dict[str, dict[str, float | int]] = {}
    for item in completions:
        schema = str(item.get("schema_name") or "unknown")
        record = by_schema.setdefault(schema, {"count": 0, "seconds": 0.0})
        record["count"] = int(record["count"]) + 1
        record["seconds"] = round(float(record["seconds"]) + float(item.get("elapsed_seconds", 0.0)), 3)
    return {
        "attempt_count": len(starts),
        "completed_count": len(completions),
        "retry_count": len(retries),
        "failure_count": len(failures),
        "completed_seconds": round(sum(float(item.get("elapsed_seconds", 0.0)) for item in completions), 3),
        "by_schema": by_schema,
        "retries": retries,
        "failures": failures,
    }


def _bundle_summary(bundle: object, case: dict[str, Any]) -> dict[str, Any]:
    expected_chunks = {
        (str(item["document_id"]), str(item["chunk_id"]))
        for item in case["expected_chunks"]
    }
    expected_docs = set(map(str, case["expected_document_ids"]))
    evidence = list(bundle.evidence_items)
    structured = [item for item in evidence if "chunk" not in item.retrieval_origins]
    chunks = [item for item in evidence if "chunk" in item.retrieval_origins]
    sources = {
        (source.document_id, source.chunk_id)
        for item in evidence
        for source in item.source_chunks
    }
    docs = {doc for doc, _ in sources}
    traceable = sum(bool(item.source_chunks) for item in evidence)
    return {
        "status": bundle.status,
        "evidence_count": len(evidence),
        "structured_assertion_count": len(structured),
        "direct_chunk_evidence_count": len(chunks),
        "expected_source_recovered": bool(docs.intersection(expected_docs)),
        "expected_answer_bearing_chunk_recovered": bool(sources.intersection(expected_chunks)),
        "provenance_complete": traceable == len(evidence),
        "retrieved_document_ids": sorted(docs),
        "evidence": [
            {
                "evidence_id": item.evidence_id,
                "assertion": asdict(item.assertion),
                "retrieval_origins": list(item.retrieval_origins),
                "instrument_scope": item.instrument_scope,
                "relevance_score": item.relevance_score,
                "sources": [asdict(source) for source in item.source_chunks],
            }
            for item in evidence
        ],
        "community_summary": bundle.community_summary,
        "community_selection": bundle.retrieval_metadata.get("relevant_communities", []),
        "warnings": bundle.retrieval_metadata.get("warnings", []),
    }


def _result_summary(
    result: object,
    case: dict[str, Any],
    retrieval: TracingRetrieval,
    generator: EvidenceGroundedLeafGenerator,
    wall: float,
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    node = result.node_results.get("q001")
    answer = node.answer if node is not None else None
    bundle = answer.evidence_bundle if answer is not None else retrieval.last_bundle
    retrieval_summary = _bundle_summary(bundle, case) if bundle is not None else None
    claims = list(answer.claims) if answer is not None else []
    evidence_by_id = {
        item.evidence_id: item
        for item in (bundle.evidence_items if bundle is not None else [])
    }
    prompt_evidence = generator._bounded_evidence(bundle) if bundle is not None else []
    prompt_ids = [str(item["evidence_id"]) for item in prompt_evidence]
    prompt_assertion_count = sum(
        "chunk" not in evidence_by_id[item_id].retrieval_origins
        for item_id in prompt_ids if item_id in evidence_by_id
    )
    prompt_chunk_count = sum(
        "chunk" in evidence_by_id[item_id].retrieval_origins
        for item_id in prompt_ids if item_id in evidence_by_id
    )
    expected_chunks = {
        (str(item["document_id"]), str(item["chunk_id"]))
        for item in case["expected_chunks"]
    }
    prompt_sources = {
        (str(source["document_id"]), str(source["chunk_id"]))
        for item in prompt_evidence
        for source in item.get("source_chunks", [])
    }
    unsupported = [
        claim for claim in claims
        if claim.status != "insufficient_evidence"
        and (not claim.evidence_refs or any(ref not in evidence_by_id for ref in claim.evidence_refs))
    ]
    claims_using_both = []
    for claim in claims:
        origins = {
            "chunk" if "chunk" in evidence_by_id[ref].retrieval_origins else "structured"
            for ref in claim.evidence_refs if ref in evidence_by_id
        }
        if origins == {"chunk", "structured"}:
            claims_using_both.append(claim.claim_id)
    report_claim_refs = {
        ref
        for section in (result.report.sections if result.report is not None else [])
        for ref in section.claim_refs
    }
    report_claims = [claim for claim in claims if claim.claim_id in report_claim_refs]
    report_origins = {
        "chunk" if "chunk" in evidence_by_id[ref].retrieval_origins else "structured"
        for claim in report_claims
        for ref in claim.evidence_refs if ref in evidence_by_id
    }
    return {
        "status": "completed",
        "analysis": asdict(result.analysis),
        "ast": result.ast,
        "leaves": [asdict(item) for item in result.leaves],
        "dependency_edges": [
            {"from": dep, "to": leaf.query_id}
            for leaf in result.leaves for dep in leaf.dependency_ids
        ],
        "retrieval": retrieval_summary,
        "retrieval_latency_seconds": round(float(retrieval.elapsed_seconds or 0.0), 3),
        "leaf": {
            "node_status": str(node.status) if node is not None else None,
            "answer_status": answer.status if answer is not None else None,
            "answer_text": answer.answer_text if answer is not None else None,
            "claim_count": len(claims),
            "supported_claim_count": sum(bool(claim.evidence_refs) and claim.status == "supported" for claim in claims),
            "partially_supported_claim_count": sum(claim.status == "partially_supported" for claim in claims),
            "insufficient_claim_count": sum(claim.status == "insufficient_evidence" for claim in claims),
            "unsupported_claim_count": len(unsupported),
            "abstained": answer is None or answer.status == "insufficient_evidence",
            "claims_using_both_representations": claims_using_both,
            "claims": [asdict(claim) for claim in claims],
            "prompt_evidence": prompt_evidence,
            "prompt_evidence_ids": prompt_ids,
            "prompt_assertion_count": prompt_assertion_count,
            "prompt_chunk_count": prompt_chunk_count,
            "expected_gold_chunk_in_prompt": bool(prompt_sources.intersection(expected_chunks)),
            "raw_output": answer.raw_output if answer is not None else None,
        },
        "final": {
            "produced": result.report is not None,
            "abstained": result.report is None or (answer is not None and answer.status == "insufficient_evidence"),
            "report": asdict(result.report) if result.report is not None else None,
            "citations_attached": bool(report_claims) and all(claim.evidence_refs for claim in report_claims),
            "relied_on_both_representations": report_origins == {"chunk", "structured"},
            "report_claim_refs": sorted(report_claim_refs),
        },
        "contradiction_detector": "disabled identically across arms",
        "nim": _nim_summary(events),
        "total_wall_seconds": round(wall, 3),
    }


def _failure_summary(exc: Exception, retrieval: TracingRetrieval, wall: float, events: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "status": "failed",
        "error_type": type(exc).__name__,
        "error": repr(exc),
        "retrieval_latency_seconds": round(float(retrieval.elapsed_seconds or 0.0), 3),
        "nim": _nim_summary(events),
        "total_wall_seconds": round(wall, 3),
    }


def _aggregate(records: list[dict[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for arm in ARMS:
        rows = [item["arms"][arm] for item in records]
        completed = [item for item in rows if item.get("status") == "completed"]
        latencies = [float(item["total_wall_seconds"]) for item in completed]
        claims = [int(item["leaf"]["claim_count"]) for item in completed]
        unsupported = [int(item["leaf"]["unsupported_claim_count"]) for item in completed]
        output[arm] = {
            "case_count": len(rows),
            "completed_count": len(completed),
            "final_answer_completion_count": sum(bool(item["final"]["produced"]) for item in completed),
            "abstention_count": sum(bool(item["leaf"]["abstained"]) for item in completed),
            "mean_claim_count": round(statistics.mean(claims), 3) if claims else None,
            "mean_unsupported_claim_count": round(statistics.mean(unsupported), 3) if unsupported else None,
            "provenance_complete_count": sum(bool(item["retrieval"]["provenance_complete"]) for item in completed),
            "total_wall_seconds": round(sum(latencies), 3),
            "median_wall_seconds": round(statistics.median(latencies), 3) if latencies else None,
            "provider_attempts": sum(int(item["nim"]["attempt_count"]) for item in rows),
            "provider_retries": sum(int(item["nim"]["retry_count"]) for item in rows),
            "provider_failures": sum(int(item["nim"]["failure_count"]) for item in rows),
        }
    return output


def _markdown(manifest: dict[str, Any], records: list[dict[str, Any]], aggregate: dict[str, Any]) -> str:
    lines = [
        "# Jurisynth live-NIM end-to-end retrieval-ablation follow-up",
        "",
        "## Boundaries",
        "",
        "- Qualitative follow-up only; the formal zero-NIM eight-case ablation was not rerun.",
        "- Frozen direct-route analysis and Query Interpreter concepts were replayed identically across arms.",
        "- Live NIM was used only for leaf-answer generation and final synthesis.",
        "- Tables, images, lazy community summarization, and contradiction detection were disabled identically.",
        f"- Provider model: `{manifest['model']}`; temperature 0; top-p 0.000001; reasoning effort `{manifest['reasoning_effort']}`.",
        "",
        "## Aggregate",
        "",
        "| Arm | Completed | Final answers | Abstentions | Mean claims | Mean unsupported | Provenance complete | Median wall (s) | Retries/failures |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for arm in ARMS:
        item = aggregate[arm]
        lines.append(
            f"| {arm} | {item['completed_count']}/{item['case_count']} | {item['final_answer_completion_count']} | "
            f"{item['abstention_count']} | {item['mean_claim_count']} | {item['mean_unsupported_claim_count']} | "
            f"{item['provenance_complete_count']} | {item['median_wall_seconds']} | "
            f"{item['provider_retries']}/{item['provider_failures']} |"
        )
    lines.extend(["", "## Case comparison", ""])
    for case in records:
        lines.append(f"### `{case['case_id']}`")
        lines.append("")
        lines.append(case["selection_reason"])
        lines.append("")
        for arm in ARMS:
            item = case["arms"][arm]
            if item.get("status") != "completed":
                lines.append(f"- **{arm}:** failed — `{item.get('error_type')}`.")
                continue
            retrieval = item["retrieval"]
            leaf = item["leaf"]
            lines.append(
                f"- **{arm}:** retrieval `{retrieval['status']}`; source/gold "
                f"{retrieval['expected_source_recovered']}/{retrieval['expected_answer_bearing_chunk_recovered']}; "
                f"{retrieval['structured_assertion_count']} assertions + {retrieval['direct_chunk_evidence_count']} chunks; "
                f"leaf `{leaf['answer_status']}` with {leaf['claim_count']} claims "
                f"({leaf['unsupported_claim_count']} mechanically unsupported); final={item['final']['produced']}; "
                f"both-representations={item['final']['relied_on_both_representations']}; wall={item['total_wall_seconds']}s."
            )
        lines.append("")
    lines.extend([
        "## Integrity",
        "",
        "- Production code changed: no.",
        "- Prompts, gold, thresholds, ranking, scoping, communities, and retrieval semantics changed: no.",
        "- Prior formal ablation rerun: no.",
    ])
    return "\n".join(lines) + "\n"


async def run(args: argparse.Namespace) -> None:
    from sentence_transformers import SentenceTransformer

    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        raise FileExistsError(f"Refusing to overwrite non-empty output directory: {args.output_dir}")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    frozen = _read_json(args.frozen_cases)
    by_id = {item["case_id"]: item for item in frozen["cases"]}
    cases = [by_id[case_id] for case_id in SELECTED_CASES]
    formal_cases = {
        item["case_id"]: item
        for item in _read_json(args.formal_results)["cases"]
    }
    base_config = NIMConfig.from_environment()
    alternate_key = os.environ.get(args.api_key_env, "")
    if not alternate_key:
        raise RuntimeError(f"Environment variable {args.api_key_env!r} is not set")
    config = replace(base_config, model=args.model, api_key=alternate_key, request_timeout_seconds=None)
    manifest = {
        "evaluation": "jurisynth_end_to_end_reasoner_validation_v1",
        "relationship_to_formal_ablation": "Qualitative follow-up; formal eight-case zero-NIM ablation remains primary and was not rerun.",
        "case_count": len(cases),
        "case_ids": list(SELECTED_CASES),
        "selection_reasons": SELECTED_CASES,
        "model": config.model,
        "provider_base_url": config.base_url,
        "temperature": 0,
        "top_p": 0.000001,
        "reasoning_effort": config.reasoning_effort,
        "request_timeout_seconds": config.request_timeout_seconds,
        "upstream_replay": "Frozen direct route, contextual facts, constraints, leaf query, and Query Interpreter concepts.",
        "qcompiler": "Not invoked because all four frozen cases are valid one-leaf direct routes.",
        "contradiction_detector": "Disabled identically across arms due unrelated exhaustive CPU cost.",
        "community_handling": "Deterministic community selection/orientation in KG-containing arms; absent in chunk-only; lazy NIM summaries disabled.",
        "arms": {
            "kg_only": "Structured assertions/E-R/communities only; no chunks/tables/images.",
            "chunk_only": "Direct chunk FAISS only; no structured KG/communities/tables/images.",
            "hybrid": "Structured assertions/E-R/communities plus direct chunk FAISS; no tables/images.",
        },
        "cases": [
            {
                "case_id": item["case_id"],
                "query": item["query"],
                "selection_reason": SELECTED_CASES[item["case_id"]],
                "expected_document_ids": item["expected_document_ids"],
                "expected_chunks": item["expected_chunks"],
                "captured_interpretations": item["captured_interpretations"],
            }
            for item in cases
        ],
    }
    _write_json(args.output_dir / "selected_cases_manifest.json", manifest)

    artifacts = load_global_artifacts(args.artifact_root)
    indices = PersistedERIndices.load(args.community_dir / "er_index")
    embedder = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    matcher = ERMatcher(indices, embedder)
    selector, orientation, descriptors = _load_community_guidance(
        args.community_dir / "er_index",
        indices,
        hierarchy_path=args.community_dir / "community_hierarchy.json",
        descriptor_path=args.community_dir / "community_descriptors.json",
    )
    records: list[dict[str, Any]] = []
    for case_index, case in enumerate(cases):
        arm_results: dict[str, Any] = {}
        for arm in _arm_order(case_index):
            run_id = f"{case['case_id']}__{arm}"
            log_path = args.output_dir / "logs" / f"{run_id}.jsonl"
            result_path = args.output_dir / "runs" / f"{run_id}.json"
            reasoning_log = ReasoningLog(log_path, run_id)
            model = OpenAICompatibleNIM(config, reasoning_log=reasoning_log)
            try:
                interpreter = CapturedConceptInterpreter(case["captured_interpretations"]["traces"])
                structured = DirectRDFRetriever(
                    artifacts.dataset,
                    matcher,
                    artifacts.resolve_chunk,
                    interpreter=interpreter,
                    community_selector=selector,
                    max_quads_per_seed=GLOBAL_MAX_QUADS_PER_SEED,
                )
                mechanism = RetrievalMechanism(
                    embedder,
                    chunk_indices=[artifacts.chunk_index] if arm in {"chunk_only", "hybrid"} else [],
                    table_indices=[],
                    image_indices=[],
                    image_expander=None,
                    structured_retriever=structured if arm in {"kg_only", "hybrid"} else None,
                    community_orientation_builder=orientation if arm in {"kg_only", "hybrid"} else None,
                    community_descriptors=descriptors if arm in {"kg_only", "hybrid"} else {},
                    community_summarizer=None,
                    document_metadata=artifacts.document_metadata,
                )
                tracing_retrieval = TracingRetrieval(mechanism)
                request = case["retrieval_request"]
                analyzer = CapturedAnalyzer(
                    tuple(request.get("contextual_facts", [])),
                    dict(request.get("constraints", {})),
                )
                leaf_generator = EvidenceGroundedLeafGenerator(model)
                workflow = AgenticWorkflow(
                    analyzer=analyzer,
                    reasoner=AgenticReasoner(
                        tracing_retrieval,
                        leaf_generator,
                        reasoning_log=reasoning_log,
                    ),
                    translator=None,
                    synthesizer=FinalReportSynthesizer(model),
                    contradiction_detector=None,
                    intake=None,
                    reasoning_log=reasoning_log,
                )
                started = time.perf_counter()
                try:
                    result = await workflow.run(case["query"])
                    wall = time.perf_counter() - started
                    arm_payload = _result_summary(
                        result, case, tracing_retrieval, leaf_generator, wall, _read_jsonl(log_path)
                    )
                except Exception as exc:
                    wall = time.perf_counter() - started
                    arm_payload = _failure_summary(exc, tracing_retrieval, wall, _read_jsonl(log_path))
            finally:
                await model.aclose()
            _write_json(result_path, {
                "case_id": case["case_id"],
                "query": case["query"],
                "arm": arm,
                "selection_reason": SELECTED_CASES[case["case_id"]],
                "model": config.model,
                "result": arm_payload,
            })
            arm_results[arm] = arm_payload
            print(
                f"{case['case_id']} {arm}: {arm_payload['status']} "
                f"wall={arm_payload['total_wall_seconds']}s retries={arm_payload['nim']['retry_count']}",
                flush=True,
            )
        records.append({
            "case_id": case["case_id"],
            "query": case["query"],
            "selection_reason": SELECTED_CASES[case["case_id"]],
            "prior_ablation": {
                arm: {
                    "retrieval_status": formal_cases[case["case_id"]]["arms"][arm]["retrieval_status"],
                    "expected_source_recovered": formal_cases[case["case_id"]]["arms"][arm]["expected_source_recovered"],
                    "answer_bearing_evidence_recovered": formal_cases[case["case_id"]]["arms"][arm]["answer_bearing_evidence_recovered"],
                    "structured_assertion_count": formal_cases[case["case_id"]]["arms"][arm]["structured_assertion_count"],
                    "direct_chunk_count": formal_cases[case["case_id"]]["arms"][arm]["direct_chunk_count"],
                }
                for arm in ARMS
            },
            "arms": arm_results,
        })

    aggregate = _aggregate(records)
    output = {
        "manifest": manifest,
        "aggregate": aggregate,
        "cases": records,
        "integrity": {
            "production_code_changed": False,
            "prompts_changed": False,
            "gold_changed": False,
            "retrieval_thresholds_changed": False,
            "formal_ablation_rerun": False,
        },
    }
    _write_json(args.output_dir / "structured_comparison.json", output)
    (args.output_dir / "JURISYNTH_END_TO_END_REASONER_VALIDATION.md").write_text(
        _markdown(manifest, records, aggregate), encoding="utf-8"
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--frozen-cases", type=Path,
        default=Path("jurisynth/evaluation_artifacts/retrieval_ablation_20260918/frozen_cases.json"),
    )
    parser.add_argument(
        "--formal-results", type=Path,
        default=Path("jurisynth/evaluation_artifacts/retrieval_ablation_20260918/per_case_results.json"),
    )
    parser.add_argument("--artifact-root", type=Path, default=Path("jurisynth/global_artifacts_source_uri_v2"))
    parser.add_argument("--community-dir", type=Path, default=Path("jurisynth/global_artifacts_source_uri_v2/community"))
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path("jurisynth/evaluation_artifacts/reasoner_ablation_live_nim_20260918"),
    )
    parser.add_argument("--model", default="nvidia/nemotron-3-super-120b-a12b")
    parser.add_argument("--api-key-env", default="NEMOTRON_SUPER")
    return parser


def main() -> None:
    asyncio.run(run(_parser().parse_args()))


if __name__ == "__main__":
    main()
