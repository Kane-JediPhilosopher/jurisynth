"""Reproducible non-LLM retrieval smoke evaluation for one Jurisynth pilot batch."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from jurisynth.retrieval_evaluation import (
    build_assertion_cases,
    run_evaluation,
    select_review_items,
    write_cases_jsonl,
    write_review_items_jsonl,
    write_results_jsonl,
    write_summary_json,
)
from jurisynth.retrieval_mech.er_matcher import ERMatcher, PersistedERIndices
from jurisynth.retrieval_mech.mechanism import RetrievalMechanism
from jurisynth.retrieval_mech.pilot_artifacts import load_pilot_batch
from jurisynth.retrieval_mech.rdf_retriever import DirectRDFRetriever


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the URI-free batch_0009 retrieval smoke evaluation.")
    parser.add_argument("--processed-batch", type=Path, default=Path("jurisynth/kg_construction_pipeline/output/batch_0009"))
    parser.add_argument("--raw-batch", type=Path, default=Path("eu_legislation/batch_0009"))
    parser.add_argument("--er-index", type=Path, default=Path("jurisynth/pilot_artifacts/batch_0009/er_index"))
    parser.add_argument("--output-dir", type=Path, default=Path("jurisynth/evaluation_artifacts"))
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument(
        "--query-style",
        choices=("subject-predicate", "legacy-subject-object"),
        default="subject-predicate",
        help="Use subject/predicate controlled probes (default) or reproduce the legacy subject/object probes.",
    )
    return parser


async def _run(args: argparse.Namespace) -> dict[str, float | int]:
    if args.limit < 1:
        raise ValueError("limit must be positive")
    try:
        from sentence_transformers import SentenceTransformer
    except ModuleNotFoundError as exc:
        raise RuntimeError("Install sentence-transformers in the documented Python 3.12 environment.") from exc
    artifacts = load_pilot_batch(args.processed_batch, raw_batch_dir=args.raw_batch)
    embedder = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    retriever = DirectRDFRetriever(
        artifacts.dataset,
        ERMatcher(PersistedERIndices.load(args.er_index), embedder),
        artifacts.resolve_chunk,
    )
    mechanism = RetrievalMechanism(
        embedder,
        chunk_indices=[artifacts.chunk_index],
        table_indices=[artifacts.table_index] if artifacts.table_index is not None else [],
        structured_retriever=retriever,
    )
    query_style = args.query_style.replace("-", "_")
    cases = build_assertion_cases(
        artifacts.dataset,
        artifacts.resolve_chunk,
        limit=args.limit,
        query_style=query_style,
    )
    results = await run_evaluation(cases, mechanism, max_concurrency=1)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"batch_0009_{args.query_style}_{len(cases)}"
    write_cases_jsonl(cases, args.output_dir / f"{prefix}_cases.jsonl")
    write_results_jsonl(results, args.output_dir / f"{prefix}_results.jsonl")
    write_review_items_jsonl(select_review_items(cases, results), args.output_dir / f"{prefix}_review_set.jsonl")
    return write_summary_json(results, args.output_dir / f"{prefix}_summary.json")


def main() -> None:
    print(json.dumps(asyncio.run(_run(_parser().parse_args())), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
