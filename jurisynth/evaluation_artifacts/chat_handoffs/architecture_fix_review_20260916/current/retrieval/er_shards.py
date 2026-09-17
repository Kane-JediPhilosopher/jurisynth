"""Exact, disk-backed shards for large persisted FAISS E-R indices.

``IndexFlatIP`` is exact but must normally be fully resident.  This module
stores contiguous vector-id ranges as separate flat indices and searches one
shard at a time.  Its global ids therefore continue to align with the SQLite
E-R metadata sidecar, while peak index residency is bounded by the largest
individual shard rather than the complete index.
"""

from __future__ import annotations

import gc
import json
import os
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

try:
    import faiss
except ModuleNotFoundError:  # pragma: no cover - exercised by the loader
    faiss = None


MANIFEST_NAME = "manifest.json"
_COPY_BATCH_ROWS = 10_000


@dataclass(frozen=True, slots=True)
class IndexShard:
    path: Path
    offset: int
    count: int
    bytes: int


class LazyShardedFlatIndex:
    """An exact index facade that opens and releases one FAISS shard per search.

    The lock is intentional: concurrent leaf retrieval must not independently
    load the same multi-GB shard and defeat the memory budget.
    """

    def __init__(self, shards: tuple[IndexShard, ...], dimension: int) -> None:
        if not shards:
            raise ValueError("a sharded E-R index needs at least one shard")
        self.shards = shards
        self.d = dimension
        self.ntotal = sum(shard.count for shard in shards)
        self._search_lock = threading.RLock()
        self.last_search_peak_rss_bytes: int | None = None

    def search(self, vectors: np.ndarray, top_k: int) -> tuple[np.ndarray, np.ndarray]:
        if faiss is None:
            raise RuntimeError("FAISS is required to search persisted E-R shards.")
        vectors = np.asarray(vectors, dtype=np.float32)
        if vectors.ndim != 2 or vectors.shape[1] != self.d:
            raise ValueError("query vectors are incompatible with the sharded E-R index")
        requested_k = min(max(int(top_k), 0), self.ntotal)
        scores = np.full((vectors.shape[0], requested_k), -np.inf, dtype=np.float32)
        identifiers = np.full((vectors.shape[0], requested_k), -1, dtype=np.int64)
        if requested_k == 0:
            return scores, identifiers

        with self._search_lock:
            peak_rss = _process_rss_bytes()
            for shard in self.shards:
                index: Any = faiss.read_index(str(shard.path))
                try:
                    peak_rss = max(peak_rss or 0, _process_rss_bytes() or 0)
                    local_scores, local_ids = index.search(vectors, min(requested_k, shard.count))
                    local_ids = local_ids.astype(np.int64, copy=False)
                    valid = local_ids >= 0
                    local_ids = local_ids.copy()
                    local_ids[valid] += shard.offset
                    scores, identifiers = _merge_top_k(scores, identifiers, local_scores, local_ids, requested_k)
                finally:
                    del index
                    gc.collect()
            self.last_search_peak_rss_bytes = peak_rss
        return scores, identifiers


def _merge_top_k(
    existing_scores: np.ndarray,
    existing_ids: np.ndarray,
    candidate_scores: np.ndarray,
    candidate_ids: np.ndarray,
    top_k: int,
) -> tuple[np.ndarray, np.ndarray]:
    merged_scores = np.concatenate((existing_scores, candidate_scores.astype(np.float32, copy=False)), axis=1)
    merged_ids = np.concatenate((existing_ids, candidate_ids.astype(np.int64, copy=False)), axis=1)
    result_scores = np.full((merged_scores.shape[0], top_k), -np.inf, dtype=np.float32)
    result_ids = np.full((merged_ids.shape[0], top_k), -1, dtype=np.int64)
    for row in range(merged_scores.shape[0]):
        valid = merged_ids[row] >= 0
        # Deterministic global-id tie-breaking keeps output stable across shards.
        order = np.lexsort((merged_ids[row, valid], -merged_scores[row, valid]))[:top_k]
        selected_scores = merged_scores[row, valid][order]
        selected_ids = merged_ids[row, valid][order]
        result_scores[row, : len(selected_scores)] = selected_scores
        result_ids[row, : len(selected_ids)] = selected_ids
    return result_scores, result_ids


def build_er_shards(
    source_directory: str | Path,
    destination: str | Path,
    *,
    shard_count: int,
    minimum_available_gb: float = 0.0,
) -> dict[str, object]:
    """Build exact entity and relation IndexFlatIP shards without touching source files."""
    if faiss is None:
        raise RuntimeError("FAISS is required to build E-R shards.")
    if shard_count < 2:
        raise ValueError("shard_count must be at least 2")
    source_directory = Path(source_directory)
    destination = Path(destination)
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing E-R shard directory: {destination}")
    _check_available_memory(minimum_available_gb)
    destination.mkdir(parents=True)
    started = time.perf_counter()
    try:
        manifest = {
            "artifact_version": "1.0",
            "index_kind": "exact_index_flat_ip",
            "shard_count": shard_count,
            "entity": _split_index(source_directory / "entity.index", destination / "entity", shard_count),
            "relation": _split_index(source_directory / "relation.index", destination / "relation", shard_count),
        }
        manifest["build_seconds"] = round(time.perf_counter() - started, 3)
        (destination / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return manifest
    except Exception:
        # Keep the partial directory for diagnosis; it is never treated as valid
        # because a manifest is only written after every index is complete.
        raise


def load_lazy_sharded_index(directory: str | Path, kind: str) -> LazyShardedFlatIndex:
    directory = Path(directory)
    manifest = json.loads((directory / MANIFEST_NAME).read_text(encoding="utf-8"))
    payload = manifest.get(kind)
    if not isinstance(payload, dict):
        raise ValueError(f"E-R shard manifest has no {kind!r} index description")
    shards = tuple(
        IndexShard(directory / item["path"], int(item["offset"]), int(item["count"]), int(item["bytes"]))
        for item in payload.get("shards", [])
    )
    return LazyShardedFlatIndex(shards, int(payload["dimension"]))


def available_shard_manifests(directory: str | Path) -> dict[int, Path]:
    root = Path(directory) / "shards"
    if not root.is_dir():
        return {}
    found: dict[int, Path] = {}
    for candidate in root.iterdir():
        manifest = candidate / MANIFEST_NAME
        if not candidate.is_dir() or not manifest.is_file():
            continue
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            count = int(payload["shard_count"])
            if count >= 2:
                found[count] = candidate
        except (OSError, ValueError, KeyError, json.JSONDecodeError):
            continue
    return found


def shard_required_gb(directory: str | Path) -> float:
    """Return the largest sequentially loaded index shard in GiB."""
    payload = json.loads((Path(directory) / MANIFEST_NAME).read_text(encoding="utf-8"))
    largest = max(
        item["bytes"]
        for kind in ("entity", "relation")
        for item in payload[kind]["shards"]
    )
    return int(largest) / 1024 ** 3


def _split_index(source: Path, destination: Path, shard_count: int) -> dict[str, object]:
    index: Any = faiss.read_index(str(source))
    try:
        if type(index).__name__ != "IndexFlatIP":
            raise ValueError(f"only IndexFlatIP is supported for exact sharding; got {type(index).__name__}")
        total = int(index.ntotal)
        base, remainder = divmod(total, shard_count)
        destination.mkdir(parents=True)
        entries: list[dict[str, int | str]] = []
        offset = 0
        for number in range(shard_count):
            count = base + (1 if number < remainder else 0)
            shard: Any = faiss.IndexFlatIP(index.d)
            try:
                for start in range(offset, offset + count, _COPY_BATCH_ROWS):
                    rows = min(_COPY_BATCH_ROWS, offset + count - start)
                    shard.add(index.reconstruct_n(start, rows))
                name = f"shard_{number:02d}.index"
                target = destination / name
                faiss.write_index(shard, str(target))
                entries.append({"path": str(Path(destination.name) / name), "offset": offset, "count": count, "bytes": target.stat().st_size})
            finally:
                del shard
                gc.collect()
            offset += count
        return {"dimension": int(index.d), "total": total, "shards": entries}
    finally:
        del index
        gc.collect()


def _check_available_memory(minimum_available_gb: float) -> None:
    if minimum_available_gb <= 0:
        return
    try:
        import psutil
    except ModuleNotFoundError:
        return
    available = psutil.virtual_memory().available / 1024 ** 3
    if available < minimum_available_gb:
        raise RuntimeError(
            f"Refusing E-R shard build: {available:.2f} GB available, "
            f"but {minimum_available_gb:.2f} GB is required."
        )


def _process_rss_bytes() -> int | None:
    try:
        import psutil
    except ModuleNotFoundError:
        return None
    return psutil.Process(os.getpid()).memory_info().rss
