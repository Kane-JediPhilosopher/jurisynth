"""Run the frozen natural-query corroboration for direct chunk retrieval.

This is a zero-NIM component evaluation. It reuses only adjudicated eligible
queries and pre-existing gold annotations from the frozen global-natural
candidate packet, and invokes only the production-v2 FAISS chunk index.
"""

from __future__ import annotations

import argparse
import json
import math
import sqlite3
import statistics
import time
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

import psutil

from jurisynth.contracts import SourceChunk
from jurisynth.retrieval_mech.artifacts import ChunkIndex
from jurisynth.retrieval_mech.lazy_chunk_metadata import SQLiteChunkMetadata


DEFAULT_ROOT = Path("jurisynth/global_artifacts_source_uri_v2")
DEFAULT_PACKET = Path("jurisynth/evaluation_artifacts/global_natural_candidate_packet.json")
DEFAULT_OUTPUT = Path("jurisynth/evaluation_artifacts/direct_chunk_natural_corroboration_v1")
EXCLUDED_REVIEW_STATUS = "excluded_pending_replacement"


@dataclass(frozen=True, slots=True)
class NaturalChunkCase:
    case_id: str
    query: str
    adjudication_verdict: str
    expected_document_id: str | None
    expected_chunk_id: str | None
    expected_excerpt: str | None
    gold_scope: str


@dataclass(frozen=True, slots=True)
class NaturalChunkResult:
    case_id: str
    query: str
    score_eligible: bool
    gold_scope: str
    expected_document_id: str | None
    expected_chunk_id: str | None
    expected_chunk_present_in_index: bool | None
    exact_rank: int | None
    diagnostic_exact_rank_at_100: int | None
    correct_document_rank: int | None
    exact_recalled: bool | None
    answer_bearing_source_recalled: bool | None
    any_candidate_correct_document_recalled: bool | None
    alternate_valid_recovery: bool | None
    retrieval_status: str
    failure_category: str | None
    latency_seconds: float
    hits: list[dict[str, object]]


def load_eligible_cases(packet_path: Path) -> tuple[list[NaturalChunkCase], dict[str, object]]:
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    cases: list[NaturalChunkCase] = []
    for raw in packet.get("cases", []):
        if raw.get("review_status") == EXCLUDED_REVIEW_STATUS:
            continue
        expected = list(raw.get("expected_chunks") or [])
        if len(expected) == 1:
            gold = expected[0]
            expected_document_id = str(gold["document_id"])
            expected_chunk_id = str(gold["chunk_id"])
            expected_excerpt = str(gold.get("excerpt") or "")
            gold_scope = "one_designated_document_qualified_chunk; no frozen alternates"
        elif not expected:
            expected_document_id = None
            expected_chunk_id = None
            expected_excerpt = None
            gold_scope = "no chunk gold; packet case is not chunk-scoreable"
        else:
            raise ValueError(
                f"{raw.get('case_id')} has {len(expected)} expected chunks; "
                "this evaluator requires an explicit scoring policy before use"
            )
        cases.append(
            NaturalChunkCase(
                case_id=str(raw["case_id"]),
                query=str(raw["question"]),
                adjudication_verdict=str((raw.get("external_adjudication") or {}).get("verdict") or "unknown"),
                expected_document_id=expected_document_id,
                expected_chunk_id=expected_chunk_id,
                expected_excerpt=expected_excerpt,
                gold_scope=gold_scope,
            )
        )
    metadata = {
        "packet_path": str(packet_path),
        "packet_version": packet.get("packet_version"),
        "packet_case_count": packet.get("case_count"),
        "packet_eligible_after_adjudication": packet.get("eligible_after_adjudication"),
        "selected_eligible_count": len(cases),
        "chunk_scoreable_count": sum(case.expected_chunk_id is not None for case in cases),
        "unscored_no_chunk_gold_count": sum(case.expected_chunk_id is None for case in cases),
        "selection_rule": f"review_status != {EXCLUDED_REVIEW_STATUS!r}",
        "query_policy": "verbatim frozen question; no generation, rewriting, or augmentation",
        "alternate_policy": "no alternate chunk/source is scored because none is encoded in expected_chunks",
    }
    return cases, metadata


def _rank_exact(hits: list[SourceChunk], document_id: str, chunk_id: str) -> int | None:
    return next(
        (
            rank
            for rank, hit in enumerate(hits, 1)
            if hit.document_id == document_id and hit.chunk_id == chunk_id
        ),
        None,
    )


def _rank_document(hits: list[SourceChunk], document_id: str) -> int | None:
    return next((rank for rank, hit in enumerate(hits, 1) if hit.document_id == document_id), None)


def _serialize_hits(hits: list[SourceChunk]) -> list[dict[str, object]]:
    return [
        {
            "rank": rank,
            "document_id": hit.document_id,
            "chunk_id": hit.chunk_id,
            "similarity": hit.similarity,
            "text_excerpt": " ".join(hit.text.split())[:800],
        }
        for rank, hit in enumerate(hits, 1)
    ]


def _score_case(
    case: NaturalChunkCase,
    primary_hits: list[SourceChunk],
    diagnostic_hits: list[SourceChunk],
    latency_seconds: float,
    expected_present: bool | None,
) -> NaturalChunkResult:
    if case.expected_document_id is None or case.expected_chunk_id is None:
        return NaturalChunkResult(
            case.case_id,
            case.query,
            False,
            case.gold_scope,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            "unscored",
            "gold_annotation_insufficient_for_chunk_scoring",
            latency_seconds,
            _serialize_hits(primary_hits),
        )

    exact_rank = _rank_exact(primary_hits, case.expected_document_id, case.expected_chunk_id)
    diagnostic_rank = exact_rank or _rank_exact(
        diagnostic_hits, case.expected_document_id, case.expected_chunk_id
    )
    document_rank = _rank_document(primary_hits, case.expected_document_id)
    if exact_rank is not None:
        status, failure = "exact", None
    elif expected_present is False:
        status, failure = "miss", "gold_chunk_absent_from_index"
    elif document_rank is not None:
        status, failure = "correct_document_wrong_chunk", "correct_document_retrieved_but_wrong_non_answer_bearing_chunk"
    elif diagnostic_rank is not None:
        status, failure = "miss", "expected_source_below_top_10_but_within_top_100"
    else:
        status, failure = "miss", "expected_source_below_top_100"
    return NaturalChunkResult(
        case.case_id,
        case.query,
        True,
        case.gold_scope,
        case.expected_document_id,
        case.expected_chunk_id,
        expected_present,
        exact_rank,
        diagnostic_rank,
        document_rank,
        exact_rank is not None,
        exact_rank is not None,
        document_rank is not None,
        False,
        status,
        failure,
        latency_seconds,
        _serialize_hits(primary_hits),
    )


def run_evaluation(
    artifact_root: Path,
    cases: list[NaturalChunkCase],
    top_k: int,
    audit_top_k: int,
) -> tuple[list[NaturalChunkResult], dict[str, object]]:
    from sentence_transformers import SentenceTransformer

    sidecar_path = artifact_root / "chunk_index" / "chunk_metadata.sqlite"
    lazy_metadata = SQLiteChunkMetadata(sidecar_path)
    index = ChunkIndex.load(
        artifact_root / "chunk_index" / "chunk_index.faiss",
        artifact_root / "chunk_index" / "chunk_metadata.pkl",
        lazy_metadata=lazy_metadata,
    )
    model_started = time.perf_counter()
    embedder = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    model_load_seconds = time.perf_counter() - model_started
    if cases:
        index.search(cases[0].query, embedder, top_k)

    process = psutil.Process()
    peak_rss = process.memory_info().rss
    connection = sqlite3.connect(f"file:{sidecar_path.as_posix()}?mode=ro", uri=True)
    results: list[NaturalChunkResult] = []
    try:
        for case in cases:
            if case.expected_document_id is not None and case.expected_chunk_id is not None:
                row = connection.execute(
                    "SELECT vector_id FROM chunks WHERE doc_id = ? AND chunk_id = ? LIMIT 1",
                    (case.expected_document_id, case.expected_chunk_id),
                ).fetchone()
                expected_present: bool | None = row is not None and int(row[0]) < int(index.index.ntotal)
            else:
                expected_present = None

            started = time.perf_counter()
            primary_hits = index.search(case.query, embedder, top_k)
            latency_seconds = time.perf_counter() - started
            if case.expected_document_id is not None and case.expected_chunk_id is not None:
                exact_rank = _rank_exact(primary_hits, case.expected_document_id, case.expected_chunk_id)
                diagnostic_hits = (
                    primary_hits
                    if exact_rank is not None
                    else index.search(case.query, embedder, audit_top_k)
                )
            else:
                diagnostic_hits = primary_hits
            results.append(
                _score_case(case, primary_hits, diagnostic_hits, latency_seconds, expected_present)
            )
            peak_rss = max(peak_rss, process.memory_info().rss)
    finally:
        connection.close()
        lazy_metadata.close()

    return results, summarize(results, model_load_seconds, peak_rss, top_k, audit_top_k)


def summarize(
    results: list[NaturalChunkResult],
    model_load_seconds: float,
    peak_rss: int,
    top_k: int,
    audit_top_k: int,
) -> dict[str, object]:
    scored = [result for result in results if result.score_eligible]
    if not scored:
        raise ValueError("No eligible case has document-qualified chunk gold")
    ranks = [result.exact_rank for result in scored]
    latencies = [result.latency_seconds for result in results]
    ordered = sorted(latencies)
    p95_index = max(0, math.ceil(0.95 * len(ordered)) - 1)
    failures = Counter(result.failure_category for result in results if result.failure_category)
    statuses = Counter(result.retrieval_status for result in results)
    return {
        "benchmark": "natural_query_direct_chunk_corroboration",
        "artifact_root": str(DEFAULT_ROOT),
        "retriever": "production-v2 direct chunk FAISS only",
        "embedding_model": "all-MiniLM-L6-v2",
        "eligible_case_count": len(results),
        "scored_case_count": len(scored),
        "unscored_case_count": len(results) - len(scored),
        "top_k": top_k,
        "diagnostic_audit_top_k": audit_top_k,
        "gold_definition": "one designated document-qualified expected chunk per scored case; no frozen alternates",
        "exact_expected_chunk_recall": sum(result.exact_recalled is True for result in scored) / len(scored),
        "answer_bearing_source_document_recall": sum(
            result.answer_bearing_source_recalled is True for result in scored
        ) / len(scored),
        "any_candidate_correct_document_recall": sum(
            result.any_candidate_correct_document_recalled is True for result in scored
        ) / len(scored),
        "alternate_valid_recoveries": sum(result.alternate_valid_recovery is True for result in scored),
        "recall_at_k": {
            str(k): sum(rank is not None and rank <= k for rank in ranks) / len(scored)
            for k in (1, 3, 5, 10)
        },
        "mrr": sum(1 / rank for rank in ranks if rank is not None) / len(scored),
        "latency_seconds_all_eligible_queries": {
            "mean": statistics.fmean(latencies),
            "median": statistics.median(latencies),
            "p95": ordered[p95_index],
            "worst": max(latencies),
        },
        "model_load_seconds": model_load_seconds,
        "peak_rss_mb": peak_rss / 1024 / 1024,
        "retrieval_status_distribution": dict(statuses),
        "failure_breakdown": dict(failures),
        "gold_chunks_absent_from_index": sum(
            result.expected_chunk_present_in_index is False for result in scored
        ),
    }


def _report(summary: dict[str, object], packet_metadata: dict[str, object]) -> str:
    recall = summary["recall_at_k"]
    latency = summary["latency_seconds_all_eligible_queries"]
    controlled = {
        "cases": 40,
        "recall_at_10": 0.10,
        "mrr": 0.0615,
        "query_style": "deterministic subject-predicate prompt",
    }
    natural_r10 = float(recall["10"])
    if natural_r10 > controlled["recall_at_10"] + 0.10:
        comparison = "Natural questions performed substantially better than the controlled subject-predicate probes."
        interpretation = "The result supports a strong query-formulation effect, while still measuring imperfect chunk retrieval."
    elif natural_r10 < controlled["recall_at_10"] - 0.05:
        comparison = "Natural questions performed worse than the controlled subject-predicate probes."
        interpretation = "The result supports a general direct-chunk retrieval weakness rather than a controlled-query artifact."
    else:
        comparison = "Natural questions performed similarly to the controlled subject-predicate probes."
        interpretation = "The result supports a general direct-chunk retrieval weakness; query formulation alone does not explain it."

    lines = [
        "# Jurisynth natural-query direct chunk corroboration",
        "",
        "This zero-NIM corroboration isolates the frozen production-v2 FAISS chunk retriever. It is not end-to-end legal QA and does not replace the 40-case controlled probe.",
        "",
        "## Frozen source and scoring boundary",
        "",
        f"- Packet: `{packet_metadata['packet_path']}` (version {packet_metadata['packet_version']}).",
        f"- Adjudicated eligible questions executed verbatim: **{summary['eligible_case_count']}**.",
        f"- Cases with document-qualified expected-chunk gold: **{summary['scored_case_count']}**.",
        f"- Unscored table questions without chunk gold: **{summary['unscored_case_count']}**.",
        "- The packet encodes one expected chunk per scored case and no explicit alternate-valid chunk IDs.",
        "- Therefore, answer-bearing source-document recall is deliberately strict: only the designated expected chunk counts. A merely same-document chunk is reported separately.",
        "- Queries were neither generated nor changed, and no alternate was inferred after retrieval.",
        "",
        "## Natural-query metrics",
        "",
        "| Metric | Result |",
        "|---|---:|",
        f"| Exact expected-chunk recall | {summary['exact_expected_chunk_recall']:.3f} |",
        f"| Strict answer-bearing source-document recall | {summary['answer_bearing_source_document_recall']:.3f} |",
        f"| Any-candidate correct-document recall | {summary['any_candidate_correct_document_recall']:.3f} |",
        f"| Alternate-valid recoveries | {summary['alternate_valid_recoveries']} |",
        f"| Recall@1 | {recall['1']:.3f} |",
        f"| Recall@3 | {recall['3']:.3f} |",
        f"| Recall@5 | {recall['5']:.3f} |",
        f"| Recall@10 | {recall['10']:.3f} |",
        f"| MRR | {summary['mrr']:.4f} |",
        f"| Mean latency (all 14 queries) | {latency['mean']:.4f} s |",
        f"| Median latency | {latency['median']:.4f} s |",
        f"| P95 latency | {latency['p95']:.4f} s |",
        f"| Worst latency | {latency['worst']:.4f} s |",
        f"| Peak RSS | {summary['peak_rss_mb']:.1f} MB |",
        "",
        "## Failure audit",
        "",
    ]
    lines.extend(
        f"- `{category}`: {count}" for category, count in summary["failure_breakdown"].items()
    )
    lines.extend([
        "",
        "## Side-by-side interpretation",
        "",
        "### Controlled S/P chunk probe",
        "",
        "- 40 cases",
        "- exact Recall@10: 0.100",
        "- MRR: 0.0615",
        "- deterministic subject-predicate query style",
        "",
        "### Natural-query corroboration",
        "",
        f"- {summary['scored_case_count']} scored cases ({summary['eligible_case_count']} executed)",
        f"- exact Recall@10: {recall['10']:.3f}",
        f"- MRR: {summary['mrr']:.4f}",
        "- frozen source-first natural questions",
        "",
        f"**Descriptive comparison:** {comparison}",
        "",
        f"**Interpretation:** {interpretation}",
        "",
        "The datasets remain separate. This small corroboration set is not a new formal accuracy estimate, and no production tuning is justified from it.",
        "",
        "Production code, thresholds, embeddings, ranking, chunking, gold annotations, and artifacts were not modified.",
        "",
    ])
    return "\n".join(lines)


def write_outputs(
    output_dir: Path,
    cases: list[NaturalChunkCase],
    packet_metadata: dict[str, object],
    results: list[NaturalChunkResult],
    summary: dict[str, object],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=False)
    with (output_dir / "frozen_cases.jsonl").open("x", encoding="utf-8") as handle:
        for case in cases:
            handle.write(json.dumps(asdict(case), ensure_ascii=False, sort_keys=True) + "\n")
    with (output_dir / "packet_metadata.json").open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(packet_metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    with (output_dir / "results.jsonl").open("x", encoding="utf-8") as handle:
        for result in results:
            handle.write(json.dumps(asdict(result), ensure_ascii=False, sort_keys=True) + "\n")
    with (output_dir / "summary.json").open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    (output_dir / "REPORT.md").write_text(_report(summary, packet_metadata), encoding="utf-8")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--audit-top-k", type=int, default=100)
    return parser


def main() -> None:
    args = _parser().parse_args()
    cases, packet_metadata = load_eligible_cases(args.packet)
    results, summary = run_evaluation(args.artifact_root, cases, args.top_k, args.audit_top_k)
    summary["artifact_root"] = str(args.artifact_root)
    write_outputs(args.output_dir, cases, packet_metadata, results, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
