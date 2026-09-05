from pathlib import Path

import numpy as np

import pytest
from rdflib import Dataset, URIRef

from jurisynth.retrieval_mech.pilot_artifacts import load_pilot_batch
from jurisynth.table_rdf_enricher import chunk_uri


@pytest.mark.integration
@pytest.mark.skipif(
    not (Path(__file__).resolve().parents[2] / "kg_construction_pipeline" / "output" / "batch_0009" / "graph" / "jurisynth_graph.nq").exists(),
    reason="batch_0009 pilot output is unavailable",
)
def test_batch_0009_loader_links_real_chunk_metadata_and_raw_tables():
    root = Path(__file__).resolve().parents[2]
    artifacts = load_pilot_batch(
        root / "kg_construction_pipeline" / "output" / "batch_0009",
        raw_batch_dir=root.parent / "eu_legislation" / "batch_0009",
    )

    first = next(iter(artifacts.chunk_index.metadata.values()))
    resolved = artifacts.resolve_chunk(chunk_uri(first["doc_id"], first["chunk_id"]))
    assert resolved is not None
    assert resolved.text == first["content"]
    assert artifacts.dataset
    assert artifacts.table_store is not None
    assert artifacts.table_index is not None
    assert not artifacts.warnings

    class StoredVectorEmbedder:
        def encode(self, texts, *, normalize_embeddings=True, **kwargs):
            vector = artifacts.table_index.table_index.reconstruct(0)
            return np.asarray([vector for _ in texts], dtype=np.float32)

    table_hits = artifacts.table_index.search("any query", StoredVectorEmbedder(), table_top_k=1, row_top_k=1)
    assert table_hits
    assert table_hits[0].matched_rows

    constrained_hits = artifacts.table_index.search(
        "any query",
        StoredVectorEmbedder(),
        table_top_k=1,
        row_top_k=1,
        document_ids={artifacts.table_index.table_metadata[0]["doc_id"]},
    )
    assert constrained_hits
    assert {hit.document_id for hit in constrained_hits} == {artifacts.table_index.table_metadata[0]["doc_id"]}
