from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import faiss
import numpy as np
import pytest

from chunk_index_builder import (
    build_chunk_vector_store,
    save_chunk_vector_store,
)


class FakeEmbeddingModel:
    """Deterministic embedding model for unit tests."""

    def encode(
        self,
        texts,
        batch_size=64,
        normalize_embeddings=True,
        show_progress_bar=True,
    ):
        vectors = []

        for text in texts:
            text = text.casefold()

            if "animal" in text:
                vector = [1.0, 0.0]
            elif "plant" in text:
                vector = [0.0, 1.0]
            elif "vehicle" in text:
                vector = [0.7, 0.7]
            else:
                vector = [0.0, 0.0]

            vectors.append(vector)

        return np.asarray(vectors, dtype=np.float32)


# =====================================================================
# T01: Test doubles
# =====================================================================

def make_chunk(doc_id, chunk_id, text):
    return {
        "doc_id": doc_id,
        "chunk_id": chunk_id,
        "content": SimpleNamespace(text=text),
    }


# =====================================================================
# T02: FAISS index
# =====================================================================

def test_build_chunk_vector_store_creates_index():
    chunks = [
        make_chunk("doc1", "chunk_1", "animal"),
        make_chunk("doc1", "chunk_2", "plant"),
    ]

    index, lookup = build_chunk_vector_store(
        chunks,
        embedding_model=FakeEmbeddingModel(),
    )

    assert isinstance(index, faiss.IndexFlatIP)
    assert index.ntotal == 2
    assert index.d == 2


# =====================================================================
# T03: Lookup table creation
# =====================================================================

def test_build_chunk_vector_store_creates_chunk_lookup():
    chunks = [
        make_chunk("doc1", "chunk_1", "animal"),
        make_chunk("doc2", "chunk_1", "plant"),
    ]

    _, lookup = build_chunk_vector_store(
        chunks,
        embedding_model=FakeEmbeddingModel(),
    )

    assert lookup == {
        0: {
            "doc_id": "doc1",
            "chunk_id": "chunk_1",
            "content": "animal",
        },
        1: {
            "doc_id": "doc2",
            "chunk_id": "chunk_1",
            "content": "plant",
        },
    }


# =====================================================================
# T04: Index-lookup ordering
# =====================================================================

def test_build_chunk_vector_store_preserves_chunk_order():
    chunks = [
        make_chunk("doc1", "chunk_1", "animal"),
        make_chunk("doc1", "chunk_2", "plant"),
        make_chunk("doc2", "chunk_1", "vehicle"),
    ]

    index, lookup = build_chunk_vector_store(
        chunks,
        embedding_model=FakeEmbeddingModel(),
    )

    distances, indices = index.search(
        np.asarray([[1.0, 0.0]], dtype=np.float32),
        1,
    )

    nearest_index = int(indices[0][0])

    assert nearest_index == 0
    assert lookup[nearest_index]["doc_id"] == "doc1"
    assert lookup[nearest_index]["chunk_id"] == "chunk_1"


# =====================================================================
# T05: Passing in custom configurations
# =====================================================================

def test_build_chunk_vector_store_uses_expected_embedding_options():
    chunks = [
        make_chunk("doc1", "chunk_1", "animal"),
    ]

    model = FakeEmbeddingModel()

    with patch.object(
        model,
        "encode",
        wraps=model.encode,
    ) as mock_encode:

        build_chunk_vector_store(
            chunks,
            embedding_model=model,
            batch_size=32,
        )

    mock_encode.assert_called_once_with(
        ["animal"],
        batch_size=32,
        normalize_embeddings=True,
        show_progress_bar=True,
    )


# =====================================================================
# T06: Empty input
# =====================================================================

def test_build_chunk_vector_store_rejects_empty_input():
    with pytest.raises(ValueError, match="raw_chunks is empty"):
        build_chunk_vector_store(
            [],
            embedding_model=FakeEmbeddingModel(),
        )


# =====================================================================
# T07: Default configuration fallback
# =====================================================================

def test_build_chunk_vector_store_loads_default_model_when_needed():
    chunks = [
        make_chunk("doc1", "chunk_1", "animal"),
    ]

    fake_model = FakeEmbeddingModel()

    with patch(
        "chunk_index_builder.SentenceTransformer",
        return_value=fake_model,
    ) as mock_model:

        index, lookup = build_chunk_vector_store(chunks)

    mock_model.assert_called_once_with(
        "all-MiniLM-L6-v2"
    )

    assert index.ntotal == 1
    assert lookup[0]["chunk_id"] == "chunk_1"


# =====================================================================
# T08: FAISS index & metadata persistence
# =====================================================================

def test_save_chunk_vector_store_writes_index_and_metadata(
    tmp_path,
):
    chunks = [
        make_chunk("doc1", "chunk_1", "animal"),
        make_chunk("doc1", "chunk_2", "plant"),
    ]

    index, lookup = build_chunk_vector_store(
        chunks,
        embedding_model=FakeEmbeddingModel(),
    )

    index_path = tmp_path / "chunks.faiss"
    metadata_path = tmp_path / "chunks.pkl"

    save_chunk_vector_store(
        index,
        lookup,
        index_path,
        metadata_path,
    )

    assert index_path.exists()
    assert metadata_path.exists()

    loaded_index = faiss.read_index(str(index_path))

    assert loaded_index.ntotal == 2
    assert loaded_index.d == 2


# =====================================================================
# T09: Recovering metadata
# =====================================================================

def test_save_chunk_vector_store_preserves_metadata(
    tmp_path,
):
    chunks = [
        make_chunk("doc1", "chunk_1", "animal"),
        make_chunk("doc2", "chunk_1", "plant"),
    ]

    index, lookup = build_chunk_vector_store(
        chunks,
        embedding_model=FakeEmbeddingModel(),
    )

    index_path = tmp_path / "chunks.faiss"
    metadata_path = tmp_path / "chunks.pkl"

    save_chunk_vector_store(
        index,
        lookup,
        index_path,
        metadata_path,
    )

    import pickle

    with metadata_path.open("rb") as file:
        restored_lookup = pickle.load(file)

    assert restored_lookup == lookup