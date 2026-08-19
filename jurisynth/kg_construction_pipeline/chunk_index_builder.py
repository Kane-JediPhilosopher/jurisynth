import faiss
import numpy as np
import pickle

# ---------------------------------------------------------------------
# Build FAISS chunk vector store
# ---------------------------------------------------------------------

def build_chunk_vector_store(
    processed_chunks,
    embedding_model,
    batch_size=64,
):
    """
    Build a FAISS vector store over document chunks.

    Parameters
    ----------
    processed_chunks : list[dict]

        Expected format:

        {
            "doc_id": str,
            "chunk_id": str,
            "chunk": str
        }

    embedding_model : SentenceTransformer
    batch_size : int

    Returns
    -------
    index : faiss.Index
        FAISS similarity index.

    chunk_lookup : dict
        Maps FAISS ids to chunk metadata.
    """

    if not processed_chunks:
        raise ValueError("processed_chunks is empty.")

    # -------------------------------------------------------------
    # Extract chunk texts
    # -------------------------------------------------------------

    texts = [
        chunk["chunk"].text
        for chunk in processed_chunks
    ]


    # -------------------------------------------------------------
    # Generate embeddings
    # -------------------------------------------------------------

    embeddings = embedding_model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    embeddings = np.asarray(embeddings, dtype=np.float32)


    # -------------------------------------------------------------
    # Build FAISS index
    #
    # Inner product on normalized vectors
    # = cosine similarity
    # -------------------------------------------------------------

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)


    # -------------------------------------------------------------
    # Metadata lookup
    # -------------------------------------------------------------

    chunk_lookup = dict()

    for idx, chunk in enumerate(processed_chunks):
        chunk_lookup[idx] = {
            "doc_id": chunk["doc_id"],
            "chunk_id": chunk["chunk_id"],
            "content": chunk["chunk"].text
        }

    return index, chunk_lookup


# ---------------------------------------------------------------------
# Query FAISS chunk store
# ---------------------------------------------------------------------

def search_chunk_vector_store(
    query,
    embedding_model,
    index,
    chunk_lookup,
    top_k=5,
):
    """
    Retrieve the most similar chunks.

    Parameters
    ----------
    query : str
    embedding_model : SentenceTransformer
    index : faiss.Index
    chunk_lookup : dict
    top_k : int

    Returns
    -------
    list[dict]
        Retrieved chunks with similarity scores.
    """


    query_embedding = embedding_model.encode(
        [query],
        normalize_embeddings=True,
    )

    query_embedding = np.asarray(query_embedding, dtype=np.float32)
    scores, indices = index.search(query_embedding, top_k)

    results = list()

    for score, idx in zip(scores[0], indices[0]):

        # FAISS returns -1 when no result exists
        if idx == -1:
            continue

        result = chunk_lookup[idx].copy()
        result["score"] = float(score)
        results.append(result)

    return results


# ---------------------------------------------------------------------
# Save / load FAISS index
# ---------------------------------------------------------------------

def save_chunk_vector_store(
    index,
    chunk_lookup,
    index_path,
    metadata_path,
):
    """
    Save FAISS index and metadata.
    """

    faiss.write_index(index, index_path)

    with open(metadata_path, "wb") as f:
        pickle.dump(chunk_lookup, f)


def load_chunk_vector_store(index_path, metadata_path):
    """
    Load FAISS index and metadata.
    """

    index = faiss.read_index(index_path)

    with open(metadata_path, "rb") as f:
        chunk_lookup = pickle.load(f)

    return index, chunk_lookup