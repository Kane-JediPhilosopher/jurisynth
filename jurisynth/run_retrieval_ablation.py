"""Run the frozen three-arm Jurisynth retrieval ablation without NIM calls.

The upstream Query Interpreter outputs are replayed from the temporary Super
global-suite traces.  Production retrieval code and settings are not changed.
Tables, images, lazy LLM community summaries, leaf generation, synthesis, and
contradiction detection are outside this component-level ablation.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import json
import math
import statistics
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from jurisynth.contracts import RetrievalRequest
from jurisynth.main import _load_community_guidance
from jurisynth.retrieval_mech.config import GLOBAL_MAX_QUADS_PER_SEED
from jurisynth.retrieval_mech.er_matcher import Concept, ERMatcher, PersistedERIndices
from jurisynth.retrieval_mech.global_artifacts import load_global_artifacts
from jurisynth.retrieval_mech.mechanism import RetrievalMechanism
from jurisynth.retrieval_mech.rdf_retriever import DirectRDFRetriever


ARMS = ("kg_only", "chunk_only", "hybrid")
VALID_TEXT_CASES = (
    "global_natural_001",
    "global_natural_002",
    "global_natural_005",
    "global_natural_006",
    "global_natural_007",
    "global_natural_009",
    "global_natural_010",
    "global_natural_011",
)
EXCLUSIONS = {
    "global_natural_003": "AI adjudication requires a query revision; no matching captured interpreter output for the revised query.",
    "global_natural_004": "AI adjudication requires a query revision; no matching captured interpreter output for the revised query.",
    "global_natural_008": "AI adjudication requires a query revision; no matching captured interpreter output for the revised query.",
    "global_natural_012": "Excluded by adjudication: incoherent cross-document join.",
    "global_natural_013": "Excluded by adjudication: temporal/source coherence unresolved.",
    "global_natural_014": "Excluded by adjudication: temporal/source coherence unresolved.",
    "global_natural_015": "Excluded by adjudication: incoherent cross-document join.",
    "global_natural_016": "Excluded by adjudication: unrelated instruments presented as one case.",
    "global_natural_017": "Excluded by adjudication: artificial multi-domain join.",
    "global_natural_018": "Table-primary case; tables are excluded from this ablation.",
    "global_natural_019": "Table-primary case; tables are excluded from this ablation.",
    "global_natural_020": "Table-primary case; tables are excluded from this ablation.",
}


class CapturedConceptInterpreter:
    """Return one previously captured structured Query Interpreter output."""

    def __init__(self, traces: list[dict[str, Any]]) -> None:
        self.by_stage = {
            str(item.get("retrieval_config", {}).get("escalation_stage", "normal")): (
                _concepts(item["entity_concepts"]),
                _concepts(item["relation_concepts"]),
            )
            for item in traces
        }
        if "normal" not in self.by_stage:
            raise ValueError("Captured interpretation requires a normal-stage trace")

    async def interpret(self, request: RetrievalRequest) -> tuple[list[Concept], list[Concept]]:
        stage = str(request.retrieval_config.get("escalation_stage", "normal"))
        return self.by_stage.get(stage, self.by_stage["normal"])


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _concepts(values: list[dict[str, Any]]) -> list[Concept]:
    return [
        Concept(str(item["concept_id"]), str(item["text"]), tuple(item.get("variants", [])))
        for item in values
    ]


def freeze_cases(args: argparse.Namespace) -> dict[str, Any]:
    """Freeze the adjudicated cases and captured upstream state before retrieval."""
    packet = _read_json(args.packet)
    packet_cases = {item["case_id"]: item for item in packet["cases"]}
    cases: list[dict[str, Any]] = []
    for case_id in VALID_TEXT_CASES:
        source = packet_cases[case_id]
        run_path = args.captured_runs / f"{case_id}.json"
        run = _read_json(run_path)
        traces = run.get("interpreter_traces", [])
        leaves = run.get("leaves", [])
        if not traces or len(leaves) != 1:
            raise RuntimeError(f"{case_id}: expected at least one captured interpreter trace and exactly one leaf")
        normal_traces = [item for item in traces if not item.get("retrieval_config", {}).get("escalation_stage")]
        if len(normal_traces) != 1:
            raise RuntimeError(f"{case_id}: expected exactly one normal-stage interpreter trace")
        trace = normal_traces[0]
        leaf = leaves[0]
        if trace["leaf_query"] != source["question"] or leaf["query"] != source["question"]:
            raise RuntimeError(f"{case_id}: captured query does not exactly match the frozen packet query")
        expected_chunks = [
            {
                "document_id": str(item["document_id"]),
                "chunk_id": str(item["chunk_id"]),
                "excerpt": str(item.get("excerpt", "")),
            }
            for item in source.get("expected_chunks", [])
        ]
        if not expected_chunks:
            raise RuntimeError(f"{case_id}: no text gold")
        cases.append({
            "case_id": case_id,
            "query": source["question"],
            "category": source.get("category"),
            "review_status": source.get("review_status"),
            "adjudication": "valid",
            "expected_chunks": expected_chunks,
            "expected_document_ids": sorted({item["document_id"] for item in expected_chunks}),
            "retrieval_request": {
                "query_id": str(trace["query_id"]),
                "leaf_query": str(trace["leaf_query"]),
                "contextual_facts": list(leaf.get("contextual_facts", [])),
                "constraints": dict(leaf.get("constraints", {})),
                "dependency_claims": [],
                "dependency_substitutions": [],
                "retrieval_config": dict(trace.get("retrieval_config", {})),
            },
            "captured_interpretations": {
                "traces": [
                    {
                        "entity_concepts": item["entity_concepts"],
                        "relation_concepts": item["relation_concepts"],
                        "retrieval_config": item.get("retrieval_config", {}),
                    }
                    for item in traces
                ],
                "source": str(run_path),
                "provider_model": "nvidia/nemotron-3-super-120b-a12b",
                "captured_elapsed_seconds": [item.get("elapsed_seconds") for item in traces],
                "missing_stage_policy": "Reuse the frozen normal-stage concepts if an arm triggers a stage absent from the captured run.",
            },
        })
    frozen = {
        "benchmark": "jurisynth_retrieval_ablation_v1",
        "frozen_at": "2026-09-18",
        "artifact_root": str(args.artifact_root),
        "community_dir": str(args.community_dir),
        "case_source": str(args.packet),
        "captured_run_root": str(args.captured_runs),
        "case_count": len(cases),
        "inclusion_rule": "AI-adjudicated valid, pre-existing natural text question with fixed expected chunk/document gold and one exact captured Query Interpreter trace.",
        "exclusion_rule": "Exclude revision-required questions, rejected/ambiguous cross-document joins, and table/image-primary cases.",
        "excluded_cases": EXCLUSIONS,
        "upstream_policy": "Replay one captured Super Query Interpreter output identically in all arms; no provider call.",
        "contradiction_detection": "Not invoked in any arm.",
        "answer_generation": "Not invoked; claim correctness and final-answer accuracy are not scored.",
        "gold_policy": "Expected-document coverage counts any retrieved evidence from a frozen expected document. Answer-bearing coverage conservatively requires the frozen expected chunk; no post-retrieval alternates are added.",
        "cases": cases,
    }
    if args.manifest.exists() and not args.force_freeze:
        existing = _read_json(args.manifest)
        if existing != frozen:
            raise RuntimeError("Frozen manifest already exists and differs; refusing to overwrite it")
        return existing
    _write_json(args.manifest, frozen)
    return frozen


def _wilson(successes: int, total: int, z: float = 1.959963984540054) -> list[float] | None:
    if total == 0:
        return None
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return [round(max(0.0, centre - margin), 4), round(min(1.0, centre + margin), 4)]


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def _arm_order(case_index: int) -> tuple[str, str, str]:
    """Rotate order across cases to reduce systematic cold-cache bias."""
    offset = case_index % len(ARMS)
    return ARMS[offset:] + ARMS[:offset]


def _compact_bundle(bundle: Any, expected_chunks: set[tuple[str, str]], expected_docs: set[str]) -> dict[str, Any]:
    structured = [item for item in bundle.evidence_items if "chunk" not in item.retrieval_origins]
    direct_chunks = [
        item for item in bundle.retrieval_metadata.get("direct_chunk_matches", [])
        if isinstance(item, dict)
    ]
    structured_sources = {
        (chunk.document_id, chunk.chunk_id)
        for item in structured
        for chunk in item.source_chunks
    }
    direct_sources = {
        (str(item.get("document_id", "")), str(item.get("chunk_id", "")))
        for item in direct_chunks
    }
    all_sources = structured_sources | direct_sources
    retrieved_docs = {doc for doc, _chunk in all_sources if doc}
    structured_traceable = sum(bool(item.source_chunks) for item in structured)
    direct_traceable = sum(bool(item.get("document_id")) and bool(item.get("chunk_id")) for item in direct_chunks)
    evidence_records = len(structured) + len(direct_chunks)
    exact_chunk_hit = bool(all_sources.intersection(expected_chunks))
    expected_doc_hit = bool(retrieved_docs.intersection(expected_docs))
    metadata = bundle.retrieval_metadata
    return {
        "retrieval_status": bundle.status,
        "expected_source_recovered": expected_doc_hit,
        "answer_bearing_evidence_recovered": exact_chunk_hit,
        "exact_expected_chunk_recovered": exact_chunk_hit,
        "structured_assertion_count": len(structured),
        "direct_chunk_count": len(direct_chunks),
        "evidence_count": evidence_records,
        "claims_generated": None,
        "answer_completed": None,
        "abstained_or_insufficient": bundle.status in {"weak", "empty", "error"},
        "provenance_complete": structured_traceable + direct_traceable == evidence_records,
        "provenance_traceable_records": structured_traceable + direct_traceable,
        "retrieved_document_ids": sorted(retrieved_docs),
        "expected_chunk_origins": {
            "structured": sorted([list(item) for item in structured_sources.intersection(expected_chunks)]),
            "chunk": sorted([list(item) for item in direct_sources.intersection(expected_chunks)]),
        },
        "structured_evidence": [
            {
                "evidence_id": item.evidence_id,
                "assertion": asdict(item.assertion),
                "sources": [
                    {"document_id": source.document_id, "chunk_id": source.chunk_id}
                    for source in item.source_chunks
                ],
                "score": item.relevance_score,
                "origins": item.retrieval_origins,
                "instrument_scope": item.instrument_scope,
            }
            for item in structured
        ],
        "direct_chunks": [
            {
                "document_id": str(item.get("document_id", "")),
                "chunk_id": str(item.get("chunk_id", "")),
                "similarity": item.get("similarity"),
            }
            for item in direct_chunks
        ],
        "instrument_scope": metadata.get("instrument_scope", {}),
        "relevant_communities": metadata.get("relevant_communities", []),
        "community_orientation": metadata.get("community_orientation"),
        "escalation_stages": metadata.get("escalation_stages", []),
        "warnings": metadata.get("warnings", []),
        "local_timings_ms": {
            "structured": metadata.get("timings_ms", {}),
            "mechanism": metadata.get("modality_retrieval", {}).get("timings_ms", {}),
        },
    }


async def evaluate(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    from sentence_transformers import SentenceTransformer

    frozen = _read_json(args.manifest)
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
    evaluation_started = time.perf_counter()
    for case_index, case in enumerate(frozen["cases"]):
        expected_chunks = {
            (item["document_id"], item["chunk_id"])
            for item in case["expected_chunks"]
        }
        expected_docs = set(case["expected_document_ids"])
        request = RetrievalRequest(**case["retrieval_request"])
        captured = case["captured_interpretations"]
        interpreter = CapturedConceptInterpreter(captured["traces"])
        structured = DirectRDFRetriever(
            artifacts.dataset,
            matcher,
            artifacts.resolve_chunk,
            interpreter=interpreter,
            community_selector=selector,
            max_quads_per_seed=GLOBAL_MAX_QUADS_PER_SEED,
        )
        arm_results: dict[str, Any] = {}
        order = _arm_order(case_index)
        for arm in order:
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
            started = time.perf_counter()
            bundle = await mechanism.retrieve_evidence(request)
            elapsed = time.perf_counter() - started
            compact = _compact_bundle(bundle, expected_chunks, expected_docs)
            compact["retrieval_latency_seconds"] = round(elapsed, 6)
            compact["provider_attempts"] = 0
            compact["provider_retries"] = 0
            arm_results[arm] = compact
            print(
                f"[{case_index + 1}/{len(frozen['cases'])}] {case['case_id']} {arm}: "
                f"status={bundle.status} source={compact['expected_source_recovered']} "
                f"gold_chunk={compact['answer_bearing_evidence_recovered']} latency={elapsed:.3f}s",
                flush=True,
            )
        records.append({
            "case_id": case["case_id"],
            "query": case["query"],
            "category": case.get("category"),
            "expected_document_ids": case["expected_document_ids"],
            "expected_chunks": case["expected_chunks"],
            "captured_interpretations": case["captured_interpretations"],
            "arm_execution_order": list(order),
            "arms": arm_results,
        })
    total_wall = time.perf_counter() - evaluation_started
    summary = aggregate(records, total_wall)
    summary["frozen_manifest_sha256"] = _sha256(args.manifest)
    return records, summary


def aggregate(records: list[dict[str, Any]], total_wall: float) -> dict[str, Any]:
    arm_summaries: dict[str, Any] = {}
    for arm in ARMS:
        values = [record["arms"][arm] for record in records]
        n = len(values)
        source_hits = sum(item["expected_source_recovered"] for item in values)
        answer_hits = sum(item["answer_bearing_evidence_recovered"] for item in values)
        provenance_hits = sum(item["provenance_complete"] for item in values)
        traceable_records = sum(item["provenance_traceable_records"] for item in values)
        evidence_records = sum(item["evidence_count"] for item in values)
        abstentions = sum(item["abstained_or_insufficient"] for item in values)
        latencies = [float(item["retrieval_latency_seconds"]) for item in values]
        statuses: dict[str, int] = {}
        for item in values:
            statuses[item["retrieval_status"]] = statuses.get(item["retrieval_status"], 0) + 1
        arm_summaries[arm] = {
            "case_count": n,
            "expected_source_coverage": source_hits / n if n else None,
            "expected_source_coverage_count": source_hits,
            "expected_source_coverage_wilson_95": _wilson(source_hits, n),
            "answer_bearing_evidence_coverage": answer_hits / n if n else None,
            "answer_bearing_evidence_count": answer_hits,
            "answer_bearing_evidence_wilson_95": _wilson(answer_hits, n),
            "mean_evidence_count": statistics.fmean(item["evidence_count"] for item in values) if values else None,
            "mean_structured_assertion_count": statistics.fmean(item["structured_assertion_count"] for item in values) if values else None,
            "mean_direct_chunk_count": statistics.fmean(item["direct_chunk_count"] for item in values) if values else None,
            "provenance_complete_rate": provenance_hits / n if n else None,
            "returned_evidence_provenance_rate": traceable_records / evidence_records if evidence_records else 1.0,
            "empty_evidence_case_count": sum(item["evidence_count"] == 0 for item in values),
            "abstention_or_insufficient_rate": abstentions / n if n else None,
            "retrieval_status_distribution": statuses,
            "claims_generated_rate": None,
            "answer_completion_rate": None,
            "latency_seconds": {
                "mean": statistics.fmean(latencies) if latencies else None,
                "median": statistics.median(latencies) if latencies else None,
                "p95": _percentile(latencies, 0.95),
                "worst": max(latencies) if latencies else None,
            },
            "provider_attempts": 0,
            "provider_retries": 0,
        }
    comparisons = {
        "kg_only_wins": [],
        "chunk_only_wins": [],
        "hybrid_strict_wins": [],
        "all_tie_success": [],
        "all_tie_miss": [],
        "hybrid_no_benefit": [],
        "hybrid_regressions": [],
        "complementary_source_union": [],
    }
    for record in records:
        hits = {arm: bool(record["arms"][arm]["answer_bearing_evidence_recovered"]) for arm in ARMS}
        source_hits = {arm: bool(record["arms"][arm]["expected_source_recovered"]) for arm in ARMS}
        case_id = record["case_id"]
        if hits["kg_only"] and not hits["chunk_only"]:
            comparisons["kg_only_wins"].append(case_id)
        if hits["chunk_only"] and not hits["kg_only"]:
            comparisons["chunk_only_wins"].append(case_id)
        if hits["hybrid"] and not hits["kg_only"] and not hits["chunk_only"]:
            comparisons["hybrid_strict_wins"].append(case_id)
        if all(hits.values()):
            comparisons["all_tie_success"].append(case_id)
        if not any(hits.values()):
            comparisons["all_tie_miss"].append(case_id)
        if hits["hybrid"] == (hits["kg_only"] or hits["chunk_only"]):
            comparisons["hybrid_no_benefit"].append(case_id)
        if (hits["kg_only"] or hits["chunk_only"]) and not hits["hybrid"]:
            comparisons["hybrid_regressions"].append(case_id)
        if source_hits["hybrid"] and (
            record["arms"]["hybrid"]["structured_assertion_count"] > 0
            and record["arms"]["hybrid"]["direct_chunk_count"] > 0
        ):
            comparisons["complementary_source_union"].append(case_id)
    return {
        "benchmark": "jurisynth_retrieval_ablation_v1",
        "case_count": len(records),
        "arms": arm_summaries,
        "comparisons": comparisons,
        "total_wall_seconds": round(total_wall, 6),
        "provider": "none (zero-NIM captured-interpreter replay)",
        "claims_and_answers": "not generated or scored; evidence coverage, provenance, status, and local latency only",
        "contradiction_detection": "not invoked identically in all arms",
        "community_handling": "deterministic community selection/orientation retained in KG-only and hybrid because it is part of structured retrieval; absent from chunk-only; lazy NIM summarization disabled.",
        "tables_images_used": False,
        "production_code_modified": False,
        "retrieval_thresholds_changed": False,
        "gold_changed": False,
        "prior_benchmarks_rerun": False,
    }


def _pct(value: float | None) -> str:
    return "n/a" if value is None else f"{100 * value:.1f}%"


def write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "case_id", "query", "arm", "expected_source_recovered",
            "answer_bearing_evidence", "evidence_count", "claims_generated",
            "abstained_or_insufficient", "retrieval_status", "retrieval_latency_seconds",
        ])
        for record in records:
            for arm in ARMS:
                item = record["arms"][arm]
                writer.writerow([
                    record["case_id"], record["query"], arm,
                    item["expected_source_recovered"], item["answer_bearing_evidence_recovered"],
                    item["evidence_count"], "not_measured", item["abstained_or_insufficient"],
                    item["retrieval_status"], item["retrieval_latency_seconds"],
                ])


def write_report(path: Path, records: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    lines = [
        "# Jurisynth retrieval ablation",
        "",
        "## Design",
        "",
        f"- Cases: {summary['case_count']} frozen, AI-adjudicated valid natural text questions.",
        "- Upstream state: previously captured Super Query Interpreter outputs replayed identically; zero NIM calls.",
        "- KG-only: structured Oxigraph assertions + E-R/community guidance; no chunks/tables/images.",
        "- Chunk-only: direct chunk FAISS only; no structured KG/tables/images.",
        "- Hybrid: structured assertions + direct chunks; no tables/images.",
        "- Contradiction detection, leaf answer generation, and final synthesis were not invoked.",
        "- Strict answer-bearing success requires the frozen expected chunk. Expected-source coverage requires any evidence from the frozen expected document.",
        f"- Frozen manifest SHA-256: `{summary['frozen_manifest_sha256']}`.",
        "",
        "## Aggregate results",
        "",
        "| Metric | KG-only | Chunk-only | Hybrid |",
        "| --- | ---: | ---: | ---: |",
    ]
    for label, key in (
        ("Expected-source coverage", "expected_source_coverage"),
        ("Strict answer-bearing coverage", "answer_bearing_evidence_coverage"),
        ("Provenance-complete cases", "provenance_complete_rate"),
        ("Weak/empty/error rate", "abstention_or_insufficient_rate"),
    ):
        lines.append("| " + label + " | " + " | ".join(_pct(summary["arms"][arm][key]) for arm in ARMS) + " |")
    for label, key in (("Mean retrieval latency (s)", "mean"), ("Median retrieval latency (s)", "median"), ("P95 retrieval latency (s)", "p95")):
        lines.append("| " + label + " | " + " | ".join(f"{summary['arms'][arm]['latency_seconds'][key]:.3f}" for arm in ARMS) + " |")
    lines.extend([
        "",
        "## Case-level comparison",
        "",
        "| Case | KG-only source / gold / evidence / status / s | Chunk-only source / gold / evidence / status / s | Hybrid source / gold / evidence / status / s |",
        "| --- | --- | --- | --- |",
    ])
    for record in records:
        cells = []
        for arm in ARMS:
            item = record["arms"][arm]
            cells.append(
                f"{int(item['expected_source_recovered'])} / {int(item['answer_bearing_evidence_recovered'])} / "
                f"{item['evidence_count']} / {item['retrieval_status']} / {item['retrieval_latency_seconds']:.3f}"
            )
        lines.append(f"| `{record['case_id']}` | " + " | ".join(cells) + " |")
    comparisons = summary["comparisons"]
    lines.extend([
        "",
        "## Complementarity",
        "",
        f"- KG-only strict wins over chunk-only: {comparisons['kg_only_wins'] or 'none'}.",
        f"- Chunk-only strict wins over KG-only: {comparisons['chunk_only_wins'] or 'none'}.",
        f"- Strict hybrid-only wins: {comparisons['hybrid_strict_wins'] or 'none'}.",
        f"- Hybrid regressions: {comparisons['hybrid_regressions'] or 'none'}.",
        f"- Hybrid had both evidence channels populated: {comparisons['complementary_source_union'] or 'none'}.",
        "",
        "## Statistical caution",
        "",
        f"- KG-only expected-source Wilson 95% CI: {summary['arms']['kg_only']['expected_source_coverage_wilson_95']}.",
        f"- Chunk-only expected-source Wilson 95% CI: {summary['arms']['chunk_only']['expected_source_coverage_wilson_95']}.",
        f"- Hybrid expected-source Wilson 95% CI: {summary['arms']['hybrid']['expected_source_coverage_wilson_95']}.",
        f"- Total measured retrieval wall time: {summary['total_wall_seconds']:.3f} seconds; provider attempts and retries: 0.",
        "",
        "## Interpretation boundaries",
        "",
        "This is a controlled retrieval ablation on a small, curated set. It measures source and strict frozen-chunk recovery, not legal-answer accuracy. Claims and final answers were deliberately not generated because doing so would require stochastic provider calls or an unfrozen judge, confounding the retrieval-only independent variable. Chunk-only weak statuses reflect the current production status contract, which requires structured/table strength or structured corroboration for `success`; this ablation did not change that behavior.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, default=Path("jurisynth/global_artifacts_source_uri_v2"))
    parser.add_argument("--community-dir", type=Path, default=Path("jurisynth/global_artifacts_source_uri_v2/community"))
    parser.add_argument("--packet", type=Path, default=Path("jurisynth/evaluation_artifacts/global_natural_candidate_packet.json"))
    parser.add_argument("--captured-runs", type=Path, default=Path("jurisynth/run_outputs/global_agentic_temporary_super_20260917"))
    parser.add_argument("--output-dir", type=Path, default=Path("jurisynth/evaluation_artifacts/retrieval_ablation_20260918"))
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--force-freeze", action="store_true")
    parser.add_argument("--summarize-existing", action="store_true")
    return parser


def main() -> None:
    args = _parser().parse_args()
    args.manifest = args.output_dir / "frozen_cases.json"
    frozen = freeze_cases(args)
    if args.prepare_only:
        print(json.dumps({"manifest": str(args.manifest), "case_count": frozen["case_count"]}, indent=2))
        return
    if args.summarize_existing:
        results_path = args.output_dir / "per_case_results.json"
        records = _read_json(results_path)["cases"]
        for record in records:
            for arm in ARMS:
                item = record["arms"][arm]
                item["provenance_complete"] = (
                    item["provenance_traceable_records"] == item["evidence_count"]
                )
        previous = _read_json(args.output_dir / "aggregate_summary.json")
        summary = aggregate(records, float(previous["total_wall_seconds"]))
        summary["frozen_manifest_sha256"] = _sha256(args.manifest)
        _write_json(results_path, {"cases": records})
        _write_json(args.output_dir / "aggregate_summary.json", summary)
        write_csv(args.output_dir / "side_by_side.csv", records)
        write_report(args.output_dir / "JURISYNTH_RETRIEVAL_ABLATION_20260918.md", records, summary)
        print(json.dumps({"summarized": str(args.output_dir), "case_count": len(records)}, indent=2))
        return
    if (args.output_dir / "per_case_results.json").exists():
        raise FileExistsError("Ablation results already exist; refusing to overwrite a completed evaluation")
    records, summary = asyncio.run(evaluate(args))
    _write_json(args.output_dir / "per_case_results.json", {"cases": records})
    _write_json(args.output_dir / "aggregate_summary.json", summary)
    write_csv(args.output_dir / "side_by_side.csv", records)
    write_report(args.output_dir / "JURISYNTH_RETRIEVAL_ABLATION_20260918.md", records, summary)
    print(json.dumps({
        "output_dir": str(args.output_dir),
        "case_count": summary["case_count"],
        "total_wall_seconds": summary["total_wall_seconds"],
    }, indent=2))


if __name__ == "__main__":
    main()
