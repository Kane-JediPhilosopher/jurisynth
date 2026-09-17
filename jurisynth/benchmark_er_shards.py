"""Benchmark exact global E-R shard configurations against a monolithic baseline.

Run the baseline once, then each sharded mode in a new Python process.  This
keeps the monolithic 4-GiB FAISS index out of the sharded RSS measurement.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import numpy as np
import psutil

import faiss

from jurisynth.retrieval_mech.er_shards import load_lazy_sharded_index


def _queries(dimension: int, count: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    vectors = rng.normal(size=(count, dimension)).astype(np.float32)
    faiss.normalize_L2(vectors)
    return vectors


def _records(scores: np.ndarray, identifiers: np.ndarray) -> dict[str, object]:
    return {"scores": scores.tolist(), "ids": identifiers.tolist()}


def _agreement(expected: dict[str, object], actual: dict[str, object]) -> dict[str, bool]:
    expected_scores = np.asarray(expected["scores"], dtype=np.float32)
    actual_scores = np.asarray(actual["scores"], dtype=np.float32)
    return {
        "ids_exact": expected["ids"] == actual["ids"],
        "scores_allclose": bool(np.allclose(expected_scores, actual_scores, rtol=1e-6, atol=1e-6)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("baseline", "sharded"))
    parser.add_argument("--source", type=Path, default=Path("jurisynth/global_artifacts/community/er_index"))
    parser.add_argument("--shard-count", type=int)
    parser.add_argument("--expected", type=Path, default=Path("jurisynth/run_outputs/er_shard_baseline.json"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--queries", type=int, default=8)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--seed", type=int, default=20260912)
    args = parser.parse_args()
    process = psutil.Process(os.getpid())
    started = time.perf_counter()

    if args.mode == "baseline":
        entity = faiss.read_index(str(args.source / "entity.index"))
        relation = faiss.read_index(str(args.source / "relation.index"))
        entity_queries = _queries(entity.d, args.queries, args.seed)
        relation_queries = _queries(relation.d, args.queries, args.seed + 1)
        entity_result = _records(*entity.search(entity_queries, min(args.top_k, entity.ntotal)))
        relation_result = _records(*relation.search(relation_queries, min(args.top_k, relation.ntotal)))
        payload = {
            "mode": "baseline",
            "elapsed_seconds": round(time.perf_counter() - started, 3),
            "rss_mb": round(process.memory_info().rss / 1024 ** 2, 1),
            "queries": args.queries,
            "top_k": args.top_k,
            "seed": args.seed,
            "entity": entity_result,
            "relation": relation_result,
        }
    else:
        if args.shard_count is None:
            parser.error("--shard-count is required in sharded mode")
        expected = json.loads(args.expected.read_text(encoding="utf-8"))
        shard_dir = args.source / "shards" / str(args.shard_count)
        entity = load_lazy_sharded_index(shard_dir, "entity")
        relation = load_lazy_sharded_index(shard_dir, "relation")
        entity_queries = _queries(entity.d, args.queries, args.seed)
        relation_queries = _queries(relation.d, args.queries, args.seed + 1)
        entity_started = time.perf_counter()
        entity_result = _records(*entity.search(entity_queries, args.top_k))
        entity_seconds = time.perf_counter() - entity_started
        relation_started = time.perf_counter()
        relation_result = _records(*relation.search(relation_queries, args.top_k))
        relation_seconds = time.perf_counter() - relation_started
        payload = {
            "mode": "sharded",
            "shard_count": args.shard_count,
            "elapsed_seconds": round(time.perf_counter() - started, 3),
            "rss_mb_after_search": round(process.memory_info().rss / 1024 ** 2, 1),
            "peak_rss_mb_during_entity_search": round((entity.last_search_peak_rss_bytes or 0) / 1024 ** 2, 1),
            "peak_rss_mb_during_relation_search": round((relation.last_search_peak_rss_bytes or 0) / 1024 ** 2, 1),
            "entity_search_seconds": round(entity_seconds, 3),
            "relation_search_seconds": round(relation_seconds, 3),
            "queries": args.queries,
            "top_k": args.top_k,
            "entity_agreement": _agreement(expected["entity"], entity_result),
            "relation_agreement": _agreement(expected["relation"], relation_result),
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
