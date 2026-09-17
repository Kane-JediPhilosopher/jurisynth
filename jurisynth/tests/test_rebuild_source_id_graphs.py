import hashlib
import json
import pickle

import pytest
from rdflib import Dataset, Literal, RDFS, URIRef

from jurisynth.kg_construction_pipeline.src.source_uri import decode_fragment, scoped_fragment
from jurisynth.rebuild_source_id_graphs import _verify_loaded_store, check_inputs, merge_graphs


def test_scoped_source_uris_are_reversible_and_injective():
    first = "C_2012219EN.01000101"
    second = "C_2012219EN.01000501"
    assert scoped_fragment(first) != scoped_fragment(second)
    assert scoped_fragment(first, "chunk_1") != scoped_fragment(second, "chunk_1")
    assert scoped_fragment("A/B", "C") != scoped_fragment("A", "B/C")
    assert decode_fragment(scoped_fragment("A/B", "C%", "é")) == ("A/B", "C%", "é")


def test_check_inputs_counts_original_ids_without_merging(tmp_path):
    root = tmp_path / "output"
    batch = root / "batch_0001"
    (batch / "checkpoints").mkdir(parents=True)
    (batch / "chunk_index").mkdir()
    (batch / ".success").touch()
    (batch / "checkpoints" / "resolved_assertions.pkl").write_bytes(b"checkpoint")
    metadata = {
        0: {"doc_id": "C_2012219EN.01000101", "chunk_id": "chunk_1", "content": "a"},
        1: {"doc_id": "C_2012219EN.01000501", "chunk_id": "chunk_1", "content": "b"},
    }
    with (batch / "chunk_index" / "chunk_metadata.pkl").open("wb") as handle:
        pickle.dump(metadata, handle)
    assert check_inputs(root) == {
        "batches": 1,
        "source_document_ids": 2,
        "source_chunk_pairs": 2,
        "chunk_records": 2,
        "document_uri_collisions": 0,
        "chunk_uri_collisions": 0,
    }


def test_merge_refuses_missing_rebuilt_batch(tmp_path):
    root = tmp_path / "output"
    batch = root / "batch_0001"
    batch.mkdir(parents=True)
    (batch / ".success").touch()
    destination = tmp_path / "new_global"
    with pytest.raises(FileNotFoundError, match="Missing rebuilt"):
        merge_graphs(root, destination)
    assert not (destination / "graph" / "jurisynth_graph.nq").exists()


def test_merge_streams_only_hash_verified_rebuilt_batches(tmp_path):
    root = tmp_path / "output"
    batch = root / "batch_0001"
    checkpoint = batch / "checkpoints" / "resolved_assertions.pkl"
    checkpoint.parent.mkdir(parents=True)
    checkpoint.write_bytes(b"resolved")
    (batch / ".success").touch()
    destination = tmp_path / "new_global"
    source = destination / "batches" / batch.name / "graph" / "jurisynth_graph.nq"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"<http://example/s> <http://example/p> <http://example/o> <http://example/g> .\n")
    metadata = {
        "resolved_sha256": hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
        "graph_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    }
    source.with_name("rebuild_metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    result = merge_graphs(root, destination)
    assert result["batches"] == 1
    assert (destination / "graph" / "jurisynth_graph.nq").read_bytes() == source.read_bytes() + b"\n"

    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        merge_graphs(root, destination)


def test_in_memory_store_verifier_checks_stored_labels_and_components(tmp_path):
    pyoxigraph = pytest.importorskip("pyoxigraph")
    dataset = Dataset()
    doc = URIRef("http://jurisynth/source/document/C_2012219EN.01000101")
    document_graph = dataset.graph(doc)
    document_graph.add((doc, RDFS.label, Literal("C_2012219EN.01000101")))
    assertion_graph = dataset.graph(URIRef("http://jurisynth/source/assertion/"))
    assertion = URIRef("http://jurisynth/source/assertion/C_2012219EN.01000101/chunk_1/1")
    for property_name, value in (
        ("subject", URIRef("http://jurisynth/data/a")),
        ("predicate", URIRef("http://jurisynth/data/means")),
        ("object", URIRef("http://jurisynth/data/b")),
        ("source_chunk", URIRef("http://jurisynth/source/chunk/C_2012219EN.01000101/chunk_1")),
    ):
        assertion_graph.add((assertion, URIRef("http://jurisynth/source/" + property_name), value))
    source = tmp_path / "pilot.nq"
    dataset.serialize(destination=source, format="nquads")
    store = pyoxigraph.Store()
    store.bulk_load(path=str(source), format=pyoxigraph.RdfFormat.N_QUADS)
    assert _verify_loaded_store(store)["shared_document_uris"] == 0

    document_graph.add((doc, RDFS.label, Literal("C_2012219EN.01000501")))
    dataset.serialize(destination=source, format="nquads")
    colliding_store = pyoxigraph.Store()
    colliding_store.bulk_load(path=str(source), format=pyoxigraph.RdfFormat.N_QUADS)
    with pytest.raises(RuntimeError, match="shared document URIs"):
        _verify_loaded_store(colliding_store)
