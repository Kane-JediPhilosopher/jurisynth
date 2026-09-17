"""Measure global artifact load plus first and warm retrieval without NIM."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import time
from pathlib import Path

import psutil

from jurisynth.contracts import RetrievalRequest
from jurisynth.main import _load_community_guidance
from jurisynth.retrieval_mech.er_matcher import ERMatcher, PersistedERIndices
from jurisynth.retrieval_mech.config import GLOBAL_MAX_QUADS_PER_SEED
from jurisynth.retrieval_mech.global_artifacts import load_global_artifacts
from jurisynth.retrieval_mech.mechanism import RetrievalMechanism
from jurisynth.retrieval_mech.rdf_retriever import DirectRDFRetriever, LeafQueryInterpreter


async def benchmark(args: argparse.Namespace) -> dict[str, object]:
    from sentence_transformers import SentenceTransformer

    started = time.perf_counter()
    artifacts = load_global_artifacts(args.artifact_root)
    indices = PersistedERIndices.load(args.community_dir / "er_index")
    embedder = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    selector, orientation, descriptors = _load_community_guidance(
        args.community_dir / "er_index", indices,
        hierarchy_path=args.community_dir / "community_hierarchy.json",
        descriptor_path=args.community_dir / "community_descriptors.json",
    )
    mechanism = RetrievalMechanism(
        embedder,
        chunk_indices=[artifacts.chunk_index],
        table_indices=[artifacts.table_index] if artifacts.table_index is not None else [],
        structured_retriever=DirectRDFRetriever(
            artifacts.dataset, ERMatcher(indices, embedder), artifacts.resolve_chunk,
            interpreter=LeafQueryInterpreter(), community_selector=selector,
            max_quads_per_seed=GLOBAL_MAX_QUADS_PER_SEED,
        ),
        community_orientation_builder=orientation,
        community_descriptors=descriptors,
        community_summarizer=None,
        document_metadata=artifacts.document_metadata,
    )
    load_seconds = time.perf_counter() - started
    process = psutil.Process(os.getpid())
    first_started = time.perf_counter()
    first = await mechanism.retrieve_evidence(RetrievalRequest("benchmark_first", args.query))
    first_seconds = time.perf_counter() - first_started
    warm_started = time.perf_counter()
    warm = await mechanism.retrieve_evidence(RetrievalRequest("benchmark_warm", args.query))
    warm_seconds = time.perf_counter() - warm_started
    entity_index = indices.entity_index
    return {
        "backend": "pyoxigraph+sqlite-sidecars",
        "query_interpreter": "deterministic_leaf_fallback_no_nim",
        "query": args.query,
        "load_seconds": round(load_seconds, 3),
        "first_query_seconds": round(first_seconds, 3),
        "warm_query_seconds": round(warm_seconds, 3),
        "rss_mb_after_warm_query": round(process.memory_info().rss / 1024 ** 2, 1),
        "entity_search_peak_rss_mb": round((getattr(entity_index, "last_search_peak_rss_bytes", 0) or 0) / 1024 ** 2, 1),
        "first_status": first.status,
        "warm_status": warm.status,
        "first_evidence_count": len(first.evidence_items),
        "warm_evidence_count": len(warm.evidence_items),
        "load_metadata": indices.load_metadata,
        "caveat": "The first/warm distinction is process-local and cache-sensitive; it is not a portable hardware benchmark.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, default=Path("jurisynth/global_artifacts"))
    parser.add_argument("--community-dir", type=Path, default=Path("jurisynth/global_artifacts/community"))
    parser.add_argument("--query", default="When may customs authorities carry out a subsequent verification of a proof of origin?")
    parser.add_argument("--output", type=Path, default=Path("jurisynth/run_outputs/global_retrieval_benchmark.json"))
    args = parser.parse_args()
    result = asyncio.run(benchmark(args))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
