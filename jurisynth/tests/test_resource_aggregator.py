import pytest
from pathlib import Path
import pickle
import json

import numpy as np

faiss = pytest.importorskip("faiss")

from jurisynth.resource_aggregator import (
    BatchArtifacts,
    EmbeddingSpec,
    build_manifest,
    require_compatible_embeddings,
    validate_batches,
    discover_batch,
    merge_nquads,
    merge_chunk_indices,
    merge_table_artifacts,
    merge_image_stores,
    write_manifest,
)


def _batch(tmp_path, batch_id="batch_0009", *, embedding=None):
    processed = tmp_path / batch_id / "processed"
    source = tmp_path / batch_id / "source"
    (processed / "graph").mkdir(parents=True)
    (processed / "chunk_index").mkdir()
    (source / "table_store").mkdir(parents=True)
    (source / "table_index" / "rows").mkdir(parents=True)
    (source / "image_store").mkdir()
    for path in (
        processed / "graph" / "jurisynth_graph.nq",
        processed / "chunk_index" / "chunk_index.faiss",
        processed / "chunk_index" / "chunk_metadata.pkl",
        source / "table_index" / "table.index",
        source / "table_index" / "table_metadata.json",
        source / "table_index" / "row_metadata.json",
    ):
        path.write_text("", encoding="utf-8")
    return BatchArtifacts(
        batch_id, processed / "graph" / "jurisynth_graph.nq", processed / "chunk_index" / "chunk_index.faiss", processed / "chunk_index" / "chunk_metadata.pkl",
        source / "table_store", source / "table_index" / "table.index", source / "table_index" / "table_metadata.json", source / "table_index" / "row_metadata.json", source / "table_index" / "rows", source / "image_store", embedding, embedding,
    )


def test_manifest_is_sorted_portable_and_requires_complete_artifact_groups(tmp_path):
    second = _batch(tmp_path, "batch_0010")
    first = _batch(tmp_path, "batch_0009")
    manifest = build_manifest([second, first], workspace_root=tmp_path)
    assert [batch["batch_id"] for batch in manifest["batches"]] == ["batch_0009", "batch_0010"]
    assert manifest["batches"][0]["table_index"].endswith("source/table_index/table.index")

    incomplete = BatchArtifacts("broken", first.graph_nquads, first.chunk_index, first.chunk_metadata, table_store=first.table_store)
    with pytest.raises(ValueError, match="complete"):
        validate_batches([incomplete])


def test_manifest_writer_creates_its_destination_directory(tmp_path):
    destination = tmp_path / "nested" / "aggregate" / "manifest.json"

    write_manifest({"manifest_version": "1.0", "batches": []}, destination)

    assert destination.is_file()


def test_faiss_merges_require_identical_explicit_embedding_specs(tmp_path):
    spec = EmbeddingSpec("model-a", 768)
    compatible = [_batch(tmp_path, "batch_0009", embedding=spec), _batch(tmp_path, "batch_0010", embedding=spec)]
    assert require_compatible_embeddings(compatible, "chunk") == spec

    with pytest.raises(ValueError, match="without embedding metadata"):
        require_compatible_embeddings([_batch(tmp_path, "batch_0011")], "chunk")


def test_nquad_merge_preserves_named_graphs_and_refuses_overwrite(tmp_path):
    first = _batch(tmp_path, "batch_0009")
    second = _batch(tmp_path, "batch_0010")
    first.graph_nquads.write_text('<https://example.test/a> <https://example.test/p> <https://example.test/b> <https://example.test/graph-a> .\n', encoding="utf-8")
    second.graph_nquads.write_text('<https://example.test/c> <https://example.test/p> <https://example.test/d> <https://example.test/graph-b> .\n', encoding="utf-8")
    destination = tmp_path / "aggregate" / "jurisynth_graph.nq"

    assert merge_nquads([second, first], destination) == destination

    from rdflib import Dataset, URIRef
    merged = Dataset()
    merged.parse(destination, format="nquads")
    assert (URIRef("https://example.test/a"), URIRef("https://example.test/p"), URIRef("https://example.test/b"), URIRef("https://example.test/graph-a")) in merged.quads((None, None, None, None))
    with pytest.raises(FileExistsError, match="overwrite"):
        merge_nquads([first, second], destination)


def _write_chunk_artifacts(batch, vector, *, doc_id, chunk_id):
    index = faiss.IndexFlatIP(2)
    index.add(np.asarray([vector], dtype=np.float32))
    faiss.write_index(index, str(batch.chunk_index))
    with batch.chunk_metadata.open("wb") as handle:
        pickle.dump({0: {"doc_id": doc_id, "chunk_id": chunk_id, "content": f"{doc_id} text"}}, handle)


def test_chunk_merge_is_deterministic_and_rejects_duplicate_source_ids(tmp_path):
    spec = EmbeddingSpec("test-model", 2)
    first = _batch(tmp_path, "batch_0009", embedding=spec)
    second = _batch(tmp_path, "batch_0010", embedding=spec)
    _write_chunk_artifacts(first, [1.0, 0.0], doc_id="doc_a", chunk_id="chunk_1")
    _write_chunk_artifacts(second, [0.0, 1.0], doc_id="doc_b", chunk_id="chunk_1")
    destination_index = tmp_path / "aggregate" / "chunks.faiss"
    destination_metadata = tmp_path / "aggregate" / "chunks.pkl"

    merge_chunk_indices([second, first], destination_index=destination_index, destination_metadata=destination_metadata)

    assert faiss.read_index(str(destination_index)).ntotal == 2
    with destination_metadata.open("rb") as handle:
        metadata = pickle.load(handle)
    assert [(metadata[index]["doc_id"], metadata[index]["chunk_id"]) for index in sorted(metadata)] == [("doc_a", "chunk_1"), ("doc_b", "chunk_1")]

    duplicate = _batch(tmp_path, "batch_0011", embedding=spec)
    _write_chunk_artifacts(duplicate, [0.5, 0.5], doc_id="doc_a", chunk_id="chunk_1")
    with pytest.raises(ValueError, match="Duplicate chunk"):
        merge_chunk_indices([first, duplicate], destination_index=tmp_path / "duplicate.faiss", destination_metadata=tmp_path / "duplicate.pkl")


def _write_table_artifacts(batch, vector, *, doc_id, table_id, value):
    index = faiss.IndexFlatIP(2)
    index.add(np.asarray([vector], dtype=np.float32))
    faiss.write_index(index, str(batch.table_index))
    joined_key = f"{doc_id}__{table_id}"
    batch.table_metadata.write_text(json.dumps([{"doc_id": doc_id, "table_id": table_id}]), encoding="utf-8")
    batch.row_metadata.write_text(json.dumps({joined_key: [{"doc_id": doc_id, "table_id": table_id, "row_id": 0}]}), encoding="utf-8")
    row_index = faiss.IndexFlatIP(2)
    row_index.add(np.asarray([vector], dtype=np.float32))
    faiss.write_index(row_index, str(batch.row_indices / f"{joined_key}.index"))
    (batch.table_store / f"{doc_id}_{table_id}.json").write_text(json.dumps({"doc_id": doc_id, "table_id": table_id, "header": ["value"], "data": [[value]]}), encoding="utf-8")


def test_table_merge_materializes_existing_tableindex_layout(tmp_path):
    from jurisynth.retrieval_mech.artifacts import TableIndex

    spec = EmbeddingSpec("test-model", 2)
    first = _batch(tmp_path, "batch_0009", embedding=spec)
    second = _batch(tmp_path, "batch_0010", embedding=spec)
    _write_table_artifacts(first, [1.0, 0.0], doc_id="doc_a", table_id="table_1", value="alpha")
    _write_table_artifacts(second, [0.0, 1.0], doc_id="doc_b", table_id="table_1", value="beta")

    destination = merge_table_artifacts([second, first], tmp_path / "aggregate_tables")
    merged = TableIndex.load(destination)

    class Embedder:
        def encode(self, texts, **kwargs):
            return np.asarray([[1.0, 0.0] for _ in texts], dtype=np.float32)

    hits = merged.search("alpha", Embedder(), table_top_k=1, row_top_k=1)
    assert hits[0].document_id == "doc_a"
    assert hits[0].matched_rows == [["alpha"]]


def test_image_merge_preserves_batch_namespaces_and_refuses_overwrite(tmp_path):
    first = _batch(tmp_path, "batch_0009")
    second = _batch(tmp_path, "batch_0010")
    (first.image_store / "shared.png").write_text("first", encoding="utf-8")
    (second.image_store / "shared.png").write_text("second", encoding="utf-8")
    destination = tmp_path / "aggregate_images"

    merge_image_stores([second, first], destination)

    assert (destination / "batch_0009" / "shared.png").read_text(encoding="utf-8") == "first"
    assert (destination / "batch_0010" / "shared.png").read_text(encoding="utf-8") == "second"
    with pytest.raises(FileExistsError, match="overwrite"):
        merge_image_stores([first], destination)


@pytest.mark.integration
@pytest.mark.skipif(
    not (Path(__file__).resolve().parents[1] / "kg_construction_pipeline" / "output" / "batch_0009" / "graph" / "jurisynth_graph.nq").exists(),
    reason="batch_0009 pilot output is unavailable",
)
def test_batch_0009_manifest_discovers_split_processed_and_source_artifacts():
    jurisynth = Path(__file__).resolve().parents[1]
    batch = discover_batch(
        "batch_0009",
        processed_batch_dir=jurisynth / "kg_construction_pipeline" / "output" / "batch_0009",
        source_batch_dir=jurisynth.parent / "eu_legislation" / "batch_0009",
    )
    manifest = build_manifest([batch], workspace_root=jurisynth.parent)
    entry = manifest["batches"][0]
    assert entry["table_index"] == "eu_legislation/batch_0009/table_index/table.index"
    assert entry["image_store"] == "eu_legislation/batch_0009/image_store"
