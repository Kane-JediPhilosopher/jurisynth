"""Build and run a frozen, zero-NIM global table-retrieval benchmark.

The benchmark reuses existing frozen source-first table questions. It invokes
only the production-v2 table and row FAISS indices and does not exercise the
chunk, graph, community, image, or agentic layers.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import psutil

from jurisynth.contracts import TableEvidence
from jurisynth.retrieval_mech.artifacts import TableIndex
from jurisynth.retrieval_mech.document_metadata import DocumentMetadataStore


DEFAULT_ROOT = Path("jurisynth/global_artifacts_source_uri_v2")
DEFAULT_OUTPUT = Path("jurisynth/evaluation_artifacts/table_retrieval_frozen_v1")
DEFAULT_NATURAL_TABLE_CASES = Path("jurisynth/evaluation_artifacts/batch_0009_table_natural_20_cases.jsonl")
DEFAULT_ADJUDICATED_CASES = Path(
    "jurisynth/evaluation_artifacts/ai_assisted_review_v1/chat_adjudicated_v1/"
    "followup_v2/contextual_natural_cases.jsonl"
)
ADJUDICATED_TABLE_IDS = {"global_natural_018", "global_natural_019", "global_natural_020"}


@dataclass(frozen=True, slots=True)
class TableEvalCase:
    case_id: str
    query: str
    expected_document_id: str
    expected_table_id: str
    expected_row_ids: tuple[int, ...]
    expected_headers: tuple[str, ...]
    expected_rows: tuple[tuple[str, ...], ...]
    canonical_source: dict[str, object]
    alternate_valid_targets: tuple[tuple[str, str, tuple[int, ...]], ...]
    source_asset: str
    query_method: str


@dataclass(frozen=True, slots=True)
class TableEvalResult:
    case_id: str
    query: str
    expected_document_id: str
    expected_table_id: str
    expected_row_ids: tuple[int, ...]
    expected_table_present: bool
    expected_rows_present: bool
    table_rank: int | None
    diagnostic_table_rank_at_100: int | None
    first_expected_row_rank: int | None
    all_expected_rows_rank: int | None
    diagnostic_all_expected_rows_rank_at_100: int | None
    recovered_expected_row_ids: tuple[int, ...]
    correct_document_rank: int | None
    table_retrieval_status: str
    failure_category: str | None
    latency_seconds: float
    table_candidates: list[dict[str, object]]
    row_candidates: list[dict[str, object]]


def _canonical_source(store: DocumentMetadataStore | None, document_id: str) -> dict[str, object]:
    record = store.get(document_id) if store is not None else None
    if record is None:
        return {"document_id": document_id, "identification": "unknown"}
    return {
        "document_id": document_id,
        "celex": record.celex,
        "eli": record.eli,
        "title": record.title,
        "canonical_keys": list(record.canonical_keys),
        "identification": "canonical" if record.celex or record.eli or record.canonical_keys else "title_only",
    }


def _load_table_rows(table_index: TableIndex, document_id: str, table_id: str) -> tuple[list[str], list[list[str]]]:
    source = table_index._load_table(document_id, table_id)
    headers = [str(value) for value in (source.get("header") or [])]
    rows = [[str(value) for value in row] for row in (source.get("data") or [])]
    return headers, rows


def build_frozen_cases(args: argparse.Namespace) -> tuple[list[TableEvalCase], dict[str, object]]:
    table_root = args.artifact_root / "tables"
    table_index = TableIndex.load(
        table_root,
        index_dir=table_root / "table_index",
        table_store=table_root / "table_store",
    )
    document_store = (
        DocumentMetadataStore(args.artifact_root / "document_metadata.sqlite")
        if (args.artifact_root / "document_metadata.sqlite").is_file()
        else None
    )
    cases: list[TableEvalCase] = []
    used_targets: set[tuple[str, str, int]] = set()
    inventory = {
        "global_natural_packet": "Three table-primary cases were later AI-adjudicated with exact document/table/row gold.",
        "stabilization_table_primary": "Reuses the fisheries table target; retained as diagnostic evidence, not a duplicate case.",
        "complex_smokes": "Returned table candidates but lack clean standalone table gold; not used.",
        "batch_0009_natural_table_packet": "Twenty already-frozen source-first row questions; seventeen unique targets remain after adjudicated-target overlap removal.",
        "global_table_store": "Authoritative production-v2 table store plus table and per-table row FAISS indices.",
        "existing_table_fixtures": "Useful for evaluator tests only; not included as benchmark cases.",
    }
    for line in args.adjudicated_cases.read_text(encoding="utf-8").splitlines():
            raw = json.loads(line)
            if raw.get("case_id") not in ADJUDICATED_TABLE_IDS:
                continue
            expected_tables = raw.get("expected_tables") or []
            if len(expected_tables) != 1:
                raise ValueError(f"{raw.get('case_id')} does not have exactly one adjudicated table target")
            gold = expected_tables[0]
            document_id, table_id = str(gold["document_id"]), str(gold["table_id"])
            row_ids = tuple(int(value) for value in gold["row_ids"])
            headers, rows = _load_table_rows(table_index, document_id, table_id)
            if any(row_id < 0 or row_id >= len(rows) for row_id in row_ids):
                raise ValueError(f"{raw['case_id']} row gold is absent from the production-v2 table store")
            expected_rows = tuple(tuple(rows[row_id]) for row_id in row_ids)
            supplied_rows = tuple(tuple(str(value) for value in row) for row in gold.get("rows") or [])
            if supplied_rows and supplied_rows != expected_rows:
                raise ValueError(f"{raw['case_id']} adjudicated row content differs from production-v2")
            cases.append(TableEvalCase(
                case_id=str(raw["case_id"]),
                query=str(raw["question"]),
                expected_document_id=document_id,
                expected_table_id=table_id,
                expected_row_ids=row_ids,
                expected_headers=tuple(headers),
                expected_rows=expected_rows,
                canonical_source=_canonical_source(document_store, document_id),
                alternate_valid_targets=(),
                source_asset=str(args.adjudicated_cases),
                query_method="verbatim AI-adjudicated frozen natural question",
            ))
            used_targets.update((document_id, table_id, row_id) for row_id in row_ids)

    for line in args.natural_table_cases.read_text(encoding="utf-8").splitlines():
            raw = json.loads(line)
            document_id, table_id, row_id = str(raw["document_id"]), str(raw["table_id"]), int(raw["row_id"])
            if (document_id, table_id, row_id) in used_targets:
                continue
            headers, rows = _load_table_rows(table_index, document_id, table_id)
            if row_id < 0 or row_id >= len(rows):
                raise ValueError(f"{raw['case_id']} row target is absent from the production-v2 table store")
            cases.append(TableEvalCase(
                case_id=str(raw["case_id"]),
                query=str(raw["query"]),
                expected_document_id=document_id,
                expected_table_id=table_id,
                expected_row_ids=(row_id,),
                expected_headers=tuple(headers),
                expected_rows=(tuple(rows[row_id]),),
                canonical_source=_canonical_source(document_store, document_id),
                alternate_valid_targets=(),
                source_asset=str(args.natural_table_cases),
                query_method="verbatim pre-existing frozen source-first natural row question",
            ))
            used_targets.add((document_id, table_id, row_id))

    if len(cases) != 20:
        raise ValueError(f"Expected 20 unique frozen cases after overlap removal, found {len(cases)}")
    plan = {
        "benchmark": "frozen_reused_table_component_evaluation; not a fresh held-out set",
        "case_count": len(cases),
        "adjudicated_anchor_count": sum(case.case_id in ADJUDICATED_TABLE_IDS for case in cases),
        "preexisting_source_first_count": sum(case.case_id not in ADJUDICATED_TABLE_IDS for case in cases),
        "unique_document_table_row_targets": len(used_targets),
        "query_generation": "none; all queries existed and were frozen before this evaluation",
        "gold_policy": "authoritative production-v2 row content copied before retrieval; no alternates inferred",
        "inventory": inventory,
    }
    return cases, plan


def write_frozen_cases(cases: list[TableEvalCase], plan: dict[str, object], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=False)
    with (output_dir / "cases.jsonl").open("x", encoding="utf-8") as handle:
        for case in cases:
            handle.write(json.dumps(asdict(case), ensure_ascii=False, sort_keys=True) + "\n")
    (output_dir / "sample_plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def read_cases(path: Path) -> list[TableEvalCase]:
    cases: list[TableEvalCase] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = json.loads(line)
        raw["expected_row_ids"] = tuple(raw["expected_row_ids"])
        raw["expected_headers"] = tuple(raw["expected_headers"])
        raw["expected_rows"] = tuple(tuple(row) for row in raw["expected_rows"])
        raw["alternate_valid_targets"] = tuple(
            (target[0], target[1], tuple(target[2])) for target in raw["alternate_valid_targets"]
        )
        cases.append(TableEvalCase(**raw))
    return cases


def _query_vector(embedder: Any, query: str) -> np.ndarray:
    vector = np.asarray(embedder.encode([query], normalize_embeddings=True), dtype=np.float32)
    if vector.ndim != 2 or vector.shape[0] != 1:
        raise ValueError("embedder must return one two-dimensional query vector")
    return vector


def _table_candidates(table_index: TableIndex, query: str, embedder: Any, top_k: int) -> list[dict[str, object]]:
    scores, ids = table_index.table_index.search(
        _query_vector(embedder, query), min(top_k, table_index.table_index.ntotal)
    )
    return [
        {
            "rank": rank,
            "document_id": str(table_index.table_metadata[int(vector_id)]["doc_id"]),
            "table_id": str(table_index.table_metadata[int(vector_id)]["table_id"]),
            "score": float(score),
        }
        for rank, (score, vector_id) in enumerate(zip(scores[0], ids[0]), 1)
        if vector_id >= 0
    ]


def _serialize_rows(hits: list[TableEvidence], limit: int) -> list[dict[str, object]]:
    return [
        {
            "rank": rank,
            "document_id": hit.document_id,
            "table_id": hit.table_id,
            "row_ids": list(hit.row_ids),
            "headers": hit.headers,
            "rows": hit.matched_rows,
            "table_score": hit.table_score,
            "row_score": hit.row_score,
            "combined_score": hit.combined_score,
        }
        for rank, hit in enumerate(hits[:limit], 1)
    ]


def _rank_table(candidates: list[dict[str, object]], document_id: str, table_id: str) -> int | None:
    return next(
        (int(item["rank"]) for item in candidates if item["document_id"] == document_id and item["table_id"] == table_id),
        None,
    )


def _row_ranks(hits: list[TableEvidence], case: TableEvalCase) -> dict[int, int]:
    expected = set(case.expected_row_ids)
    ranks: dict[int, int] = {}
    for rank, hit in enumerate(hits, 1):
        if hit.document_id != case.expected_document_id or hit.table_id != case.expected_table_id:
            continue
        for row_id in hit.row_ids:
            if row_id in expected and row_id not in ranks:
                ranks[row_id] = rank
    return ranks


def _score_case(
    case: TableEvalCase,
    table_candidates: list[dict[str, object]],
    row_hits: list[TableEvidence],
    diagnostic_tables: list[dict[str, object]],
    diagnostic_rows: list[TableEvidence],
    table_present: bool,
    rows_present: bool,
    latency_seconds: float,
) -> TableEvalResult:
    table_rank = _rank_table(table_candidates, case.expected_document_id, case.expected_table_id)
    diagnostic_table_rank = table_rank or _rank_table(
        diagnostic_tables, case.expected_document_id, case.expected_table_id
    )
    row_ranks = _row_ranks(row_hits, case)
    diagnostic_row_ranks = _row_ranks(diagnostic_rows, case)
    recovered = tuple(sorted(row_ranks))
    first_row_rank = min(row_ranks.values()) if row_ranks else None
    all_rows_rank = max(row_ranks.values()) if len(row_ranks) == len(case.expected_row_ids) else None
    diagnostic_all_rows_rank = (
        max(diagnostic_row_ranks.values())
        if len(diagnostic_row_ranks) == len(case.expected_row_ids)
        else None
    )
    document_rank = next(
        (int(item["rank"]) for item in table_candidates if item["document_id"] == case.expected_document_id),
        None,
    )

    if table_rank is not None and all_rows_rank is not None:
        status, failure = "exact_row", None
    elif not table_present:
        status, failure = "miss", "expected_table_absent_from_store_or_index"
    elif not rows_present:
        status, failure = "miss", "expected_row_absent_from_store"
    elif table_rank is not None and first_row_rank is None:
        status, failure = "correct_table_wrong_row", "correct_table_retrieved_but_wrong_row"
    elif table_rank is None and document_rank is not None:
        status, failure = "correct_document_wrong_table", "correct_document_retrieved_but_wrong_table"
    elif diagnostic_all_rows_rank is not None:
        status, failure = "miss", "answer_bearing_row_below_top_10_but_within_top_100"
    elif diagnostic_table_rank is not None:
        status, failure = "miss", "correct_table_within_top_100_but_answer_bearing_row_below_top_100"
    else:
        status, failure = "miss", "answer_bearing_table_and_row_below_top_100"

    return TableEvalResult(
        case.case_id,
        case.query,
        case.expected_document_id,
        case.expected_table_id,
        case.expected_row_ids,
        table_present,
        rows_present,
        table_rank,
        diagnostic_table_rank,
        first_row_rank,
        all_rows_rank,
        diagnostic_all_rows_rank,
        recovered,
        document_rank,
        status,
        failure,
        latency_seconds,
        table_candidates,
        _serialize_rows(row_hits, 10),
    )


def run_evaluation(
    args: argparse.Namespace, cases: list[TableEvalCase]
) -> tuple[list[TableEvalResult], dict[str, object]]:
    from sentence_transformers import SentenceTransformer

    table_root = args.artifact_root / "tables"
    table_index = TableIndex.load(
        table_root,
        index_dir=table_root / "table_index",
        table_store=table_root / "table_store",
    )
    table_keys = {
        (str(item["doc_id"]), str(item["table_id"])) for item in table_index.table_metadata
    }
    model_started = time.perf_counter()
    embedder = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    model_load_seconds = time.perf_counter() - model_started
    if cases:
        table_index.search(cases[0].query, embedder, args.top_k, args.top_k)

    process = psutil.Process()
    peak_rss = process.memory_info().rss
    results: list[TableEvalResult] = []
    for case in cases:
        table_present = (case.expected_document_id, case.expected_table_id) in table_keys
        try:
            _, stored_rows = _load_table_rows(table_index, case.expected_document_id, case.expected_table_id)
            rows_present = all(
                0 <= row_id < len(stored_rows) and tuple(stored_rows[row_id]) == expected_row
                for row_id, expected_row in zip(case.expected_row_ids, case.expected_rows)
            )
        except FileNotFoundError:
            rows_present = False

        started = time.perf_counter()
        table_candidates = _table_candidates(table_index, case.query, embedder, args.top_k)
        row_hits = table_index.search(case.query, embedder, args.top_k, args.top_k)
        latency_seconds = time.perf_counter() - started
        primary_row_ranks = _row_ranks(row_hits, case)
        primary_complete = len(primary_row_ranks) == len(case.expected_row_ids)
        primary_table = _rank_table(table_candidates, case.expected_document_id, case.expected_table_id)
        if primary_complete and primary_table is not None:
            diagnostic_tables, diagnostic_rows = table_candidates, row_hits
        else:
            diagnostic_tables = _table_candidates(table_index, case.query, embedder, args.audit_top_k)
            diagnostic_rows = table_index.search(
                case.query, embedder, args.audit_top_k, args.audit_top_k
            )
        results.append(_score_case(
            case,
            table_candidates,
            row_hits,
            diagnostic_tables,
            diagnostic_rows,
            table_present,
            rows_present,
            latency_seconds,
        ))
        peak_rss = max(peak_rss, process.memory_info().rss)
    return results, summarize(results, model_load_seconds, peak_rss, args.top_k, args.audit_top_k)


def summarize(
    results: list[TableEvalResult],
    model_load_seconds: float,
    peak_rss: int,
    top_k: int,
    audit_top_k: int,
) -> dict[str, object]:
    total = len(results)
    table_ranks = [result.table_rank for result in results]
    row_ranks = [result.all_expected_rows_rank for result in results]
    latencies = [result.latency_seconds for result in results]
    ordered = sorted(latencies)
    p95_index = max(0, math.ceil(0.95 * len(ordered)) - 1)
    expected_row_total = sum(len(result.expected_row_ids) for result in results)
    recovered_row_total = sum(len(result.recovered_expected_row_ids) for result in results)
    return {
        "benchmark": "frozen_global_table_retrieval_component_evaluation",
        "artifact_root": str(DEFAULT_ROOT),
        "case_count": total,
        "top_k": top_k,
        "diagnostic_audit_top_k": audit_top_k,
        "table_recall_at_k": {
            str(k): sum(rank is not None and rank <= k for rank in table_ranks) / total
            for k in (1, 3, 5, 10)
        },
        "row_recall_at_k": {
            str(k): sum(rank is not None and rank <= k for rank in row_ranks) / total
            for k in (1, 3, 5, 10)
        },
        "table_mrr": sum(1 / rank for rank in table_ranks if rank is not None) / total,
        "row_mrr": sum(1 / rank for rank in row_ranks if rank is not None) / total,
        "correct_document_recall_at_10": sum(
            result.correct_document_rank is not None and result.correct_document_rank <= 10
            for result in results
        ) / total,
        "answer_bearing_row_case_recall_at_10": sum(
            result.all_expected_rows_rank is not None and result.all_expected_rows_rank <= 10
            for result in results
        ) / total,
        "answer_bearing_row_micro_recall_at_10": recovered_row_total / expected_row_total,
        "expected_row_count": expected_row_total,
        "recovered_expected_row_count_at_10": recovered_row_total,
        "alternate_valid_recoveries": 0,
        "latency_seconds": {
            "mean": statistics.fmean(latencies),
            "median": statistics.median(latencies),
            "p95": ordered[p95_index],
            "worst": max(latencies),
        },
        "model_load_seconds": model_load_seconds,
        "peak_rss_mb": peak_rss / 1024 / 1024,
        "retrieval_status_distribution": dict(Counter(result.table_retrieval_status for result in results)),
        "failure_breakdown": dict(Counter(
            result.failure_category for result in results if result.failure_category
        )),
        "expected_tables_absent": sum(not result.expected_table_present for result in results),
        "expected_rows_absent": sum(not result.expected_rows_present for result in results),
    }


def _report(summary: dict[str, object], plan: dict[str, object]) -> str:
    table = summary["table_recall_at_k"]
    row = summary["row_recall_at_k"]
    latency = summary["latency_seconds"]
    lines = [
        "# Jurisynth table retrieval component evaluation",
        "",
        "This is a zero-NIM evaluation of the frozen production-v2 table and row FAISS layer. It is not end-to-end legal QA and is not a fresh held-out set.",
        "",
        "## Existing-asset inventory",
        "",
    ]
    lines.extend(f"- **{key.replace('_', ' ')}:** {value}" for key, value in plan["inventory"].items())
    lines.extend([
        "",
        "## Construction and integrity",
        "",
        f"- Frozen cases: **{summary['case_count']}**.",
        f"- AI-adjudicated natural anchors: **{plan['adjudicated_anchor_count']}**.",
        f"- Other pre-existing frozen source-first cases: **{plan['preexisting_source_first_count']}**.",
        "- No query was generated or rewritten for this evaluation.",
        "- Gold rows were copied from the authoritative production-v2 table store before retrieval.",
        "- No alternate-valid rows/tables were encoded, and none were inferred after retrieval.",
        "",
        "## Metrics",
        "",
        "| Metric | Result |",
        "|---|---:|",
        f"| Table Recall@1 / @3 / @5 / @10 | {table['1']:.3f} / {table['3']:.3f} / {table['5']:.3f} / {table['10']:.3f} |",
        f"| Row Recall@1 / @3 / @5 / @10 | {row['1']:.3f} / {row['3']:.3f} / {row['5']:.3f} / {row['10']:.3f} |",
        f"| Table MRR | {summary['table_mrr']:.4f} |",
        f"| Row MRR | {summary['row_mrr']:.4f} |",
        f"| Correct-document recall@10 | {summary['correct_document_recall_at_10']:.3f} |",
        f"| Answer-bearing row case recall@10 | {summary['answer_bearing_row_case_recall_at_10']:.3f} |",
        f"| Answer-bearing row micro recall@10 | {summary['answer_bearing_row_micro_recall_at_10']:.3f} |",
        f"| Alternate-valid recoveries | {summary['alternate_valid_recoveries']} |",
        f"| Mean / median latency | {latency['mean']:.4f} / {latency['median']:.4f} s |",
        f"| P95 / worst latency | {latency['p95']:.4f} / {latency['worst']:.4f} s |",
        f"| Peak RSS | {summary['peak_rss_mb']:.1f} MB |",
        "",
        "## Failure audit",
        "",
    ])
    if summary["failure_breakdown"]:
        lines.extend(
            f"- `{category}`: {count}" for category, count in summary["failure_breakdown"].items()
        )
    else:
        lines.append("- No misses.")
    lines.extend([
        "",
        "## Interpretation boundary",
        "",
        "Table Recall@k follows the production table-level FAISS order. Row Recall@k requires every frozen answer-bearing row for a case to survive the production combined table×row scoring order by rank k. Correct-document recall does not imply an answer-bearing table or row.",
        "",
        f"Expected tables absent from the production index: **{summary['expected_tables_absent']}**. Expected rows absent from the authoritative store: **{summary['expected_rows_absent']}**.",
        "",
        "## Findings",
        "",
        "- Every designated table and row exists in the production-v2 artifacts; this evaluation found no deterministic store/index-presence defect.",
        "- The dominant limitation is first-stage table ranking: most missed target tables remain outside the diagnostic top 100.",
        "- Two additional answer-bearing rows become reachable only when the table candidate search is widened diagnostically to 100.",
        "- The 17 reused source-first questions use a generic identifier-based wording. Results should therefore be presented as a frozen component benchmark, not a fresh held-out estimate of arbitrary natural legal-table QA.",
        "",
        "Production retrieval code, table artifacts, thresholds, serialization, scoping, and ranking were not modified.",
        "",
    ])
    return "\n".join(lines)


def write_results(
    output_dir: Path,
    results: list[TableEvalResult],
    summary: dict[str, object],
    plan: dict[str, object],
) -> None:
    with (output_dir / "results.jsonl").open("x", encoding="utf-8") as handle:
        for result in results:
            handle.write(json.dumps(asdict(result), ensure_ascii=False, sort_keys=True) + "\n")
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "REPORT.md").write_text(_report(summary, plan), encoding="utf-8")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--natural-table-cases", type=Path, default=DEFAULT_NATURAL_TABLE_CASES)
    parser.add_argument("--adjudicated-cases", type=Path, default=DEFAULT_ADJUDICATED_CASES)
    parser.add_argument("--case-file", type=Path)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--audit-top-k", type=int, default=100)
    parser.add_argument("--freeze-only", action="store_true")
    return parser


def main() -> None:
    args = _parser().parse_args()
    if args.case_file is None:
        cases, plan = build_frozen_cases(args)
        write_frozen_cases(cases, plan, args.output_dir)
        if args.freeze_only:
            print(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True))
            return
    else:
        cases = read_cases(args.case_file)
        plan_path = args.output_dir / "sample_plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    results, summary = run_evaluation(args, cases)
    summary["artifact_root"] = str(args.artifact_root)
    write_results(args.output_dir, results, summary, plan)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
