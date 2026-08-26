from pathlib import Path
import pickle

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


EMBEDDING_MODEL_ID = "all-MiniLM-L6-v2"

def build_chunk_vector_store(
    raw_chunks: list[dict],
    embedding_model: SentenceTransformer | None = None,
    batch_size: int = 64,
):
    """Build a FAISS vector store over document chunks."""

    if embedding_model is None:
        embedding_model = SentenceTransformer(EMBEDDING_MODEL_ID)
    
    if not raw_chunks:
        raise ValueError("raw_chunks is empty.")

    texts = [
        chunk["content"].text
        for chunk in raw_chunks
    ]

    embeddings = embedding_model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    embeddings = np.asarray(embeddings, dtype=np.float32)

    dimension = embeddings.shape[1]

    # Normalized embeddings + inner product = cosine similarity.
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    chunk_lookup = {
        idx: {
            "doc_id": chunk["doc_id"],
            "chunk_id": chunk["chunk_id"],
            "content": chunk["content"].text,
        }
        for idx, chunk in enumerate(raw_chunks)
    }

    return index, chunk_lookup


def save_chunk_vector_store(
    index: faiss.Index,
    chunk_lookup: dict,
    index_path: Path,
    metadata_path: Path,
):
    """Save the FAISS index and chunk metadata."""

    faiss.write_index(index, str(index_path))

    with metadata_path.open("wb") as file:
        pickle.dump(chunk_lookup, file)