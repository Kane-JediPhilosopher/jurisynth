from __future__ import annotations

import numpy as np
import pytest

faiss = pytest.importorskip("faiss")

from jurisynth.retrieval_mech.er_shards import build_er_shards, load_lazy_sharded_index


def _write_flat(path, vectors: np.ndarray) -> None:
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    faiss.write_index(index, str(path))


@pytest.mark.parametrize("shard_count", [2, 3, 4])
def test_exact_shards_match_monolithic_index(tmp_path, shard_count: int) -> None:
    vectors = np.asarray([[1.0, 0.0], [0.9, 0.1], [0.3, 0.7], [0.0, 1.0], [-1.0, 0.0], [0.1, -0.9]], dtype=np.float32)
    _write_flat(tmp_path / "entity.index", vectors)
    _write_flat(tmp_path / "relation.index", vectors[:3])
    shard_dir = tmp_path / "shards" / str(shard_count)
    build_er_shards(tmp_path, shard_dir, shard_count=shard_count)
    expected_scores, expected_ids = faiss.read_index(str(tmp_path / "entity.index")).search(vectors[:2], 4)
    actual_scores, actual_ids = load_lazy_sharded_index(shard_dir, "entity").search(vectors[:2], 4)
    assert actual_scores == pytest.approx(expected_scores)
    assert actual_ids.tolist() == expected_ids.tolist()


def test_shards_refuse_overwrite(tmp_path) -> None:
    vectors = np.asarray([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    _write_flat(tmp_path / "entity.index", vectors)
    _write_flat(tmp_path / "relation.index", vectors)
    destination = tmp_path / "shards" / "2"
    build_er_shards(tmp_path, destination, shard_count=2)
    with pytest.raises(FileExistsError):
        build_er_shards(tmp_path, destination, shard_count=2)
