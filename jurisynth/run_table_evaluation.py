"""Reproducible table-row retrieval smoke evaluation for batch_0009."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from jurisynth.retrieval_evaluation import (
    build_stratified_table_cases,
    run_table_evaluation,
    write_table_results_jsonl,
    write_table_summary_json,
)
from jurisynth.retrieval_mech.artifacts import TableIndex
from jurisynth.retrieval_mech.mechanism import RetrievalMechanism


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the batch_0009 table-row retrieval smoke evaluation.")
    parser.add_argument("--raw-batch", type=Path, default=Path("eu_legislation/batch_0009"))
    parser.add_argument("--output-dir", type=Path, default=Path("jurisynth/evaluation_artifacts"))
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument(
        "--query-style",
        choices=("natural", "integrity"),
        default="natural",
        help="Use natural identifier-based questions or deterministic row-echo integrity probes.",
    )
    return parser


async def _run(args: argparse.Namespace) -> dict[str, float | int]:
    if args.limit < 1:
        raise ValueError("limit must be positive")
    try:
        from sentence_transformers import SentenceTransformer
    except ModuleNotFoundError as exc:
        raise RuntimeError("Install sentence-transformers in the documented Python 3.12 environment.") from exc
    table_index = TableIndex.load(args.raw_batch)
    embedder = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    cases = build_stratified_table_cases(table_index, limit=args.limit, query_style=args.query_style)
    results = await run_table_evaluation(cases, RetrievalMechanism(embedder, table_indices=[table_index]), max_concurrency=1)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"batch_0009_table_{args.query_style}_{len(cases)}"
    from jurisynth.retrieval_evaluation import write_cases_jsonl
    write_cases_jsonl(cases, args.output_dir / f"{prefix}_cases.jsonl")
    write_table_results_jsonl(results, args.output_dir / f"{prefix}_results.jsonl")
    return write_table_summary_json(results, args.output_dir / f"{prefix}_summary.json")


def main() -> None:
    print(json.dumps(asyncio.run(_run(_parser().parse_args())), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
