"""Run the authored, source-aligned batch_0009 natural-query retrieval evaluation."""

from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import asdict
from pathlib import Path

from jurisynth.retrieval_evaluation import read_natural_cases, run_natural_evaluation, summarize_natural_results
from jurisynth.retrieval_mech.er_matcher import ERMatcher, PersistedERIndices
from jurisynth.retrieval_mech.mechanism import RetrievalMechanism
from jurisynth.retrieval_mech.pilot_artifacts import load_pilot_batch
from jurisynth.retrieval_mech.rdf_retriever import DirectRDFRetriever


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=Path("jurisynth/evaluation_artifacts/batch_0009_natural_query_seeds.jsonl"))
    parser.add_argument("--processed-batch", type=Path, default=Path("jurisynth/kg_construction_pipeline/output/batch_0009"))
    parser.add_argument("--raw-batch", type=Path, default=Path("eu_legislation/batch_0009"))
    parser.add_argument("--er-index", type=Path, default=Path("jurisynth/pilot_artifacts/batch_0009/er_index"))
    parser.add_argument("--output-dir", type=Path, default=Path("jurisynth/evaluation_artifacts/natural_query_pilot"))
    return parser


async def _run(args: argparse.Namespace) -> dict[str, float | int]:
    from sentence_transformers import SentenceTransformer

    artifacts = load_pilot_batch(args.processed_batch, raw_batch_dir=args.raw_batch)
    embedder = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    mechanism = RetrievalMechanism(
        embedder,
        chunk_indices=[artifacts.chunk_index],
        table_indices=[artifacts.table_index] if artifacts.table_index is not None else [],
        structured_retriever=DirectRDFRetriever(
            artifacts.dataset,
            ERMatcher(PersistedERIndices.load(args.er_index), embedder),
            artifacts.resolve_chunk,
        ),
    )
    cases = read_natural_cases(args.cases)
    results = await run_natural_evaluation(cases, mechanism)
    summary = summarize_natural_results(results)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "batch_0009_natural_results.jsonl").write_text(
        "\n".join(json.dumps(asdict(result), ensure_ascii=False, sort_keys=True) for result in results) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "batch_0009_natural_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    print(json.dumps(asyncio.run(_run(_parser().parse_args())), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
