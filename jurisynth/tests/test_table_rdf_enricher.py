import json

import pytest
from rdflib import Dataset, RDF

from jurisynth.table_rdf_enricher import (
    CHUNK,
    JS_SOURCE,
    chunk_uri,
    chunk_uri_candidates,
    document_uri,
    enrich_dataset_from_table_store,
    enrich_dataset_with_tables,
    legacy_chunk_uri,
    table_uri,
)


def test_minimal_table_provenance_does_not_serialize_contents():
    dataset = Dataset()
    enrich_dataset_with_tables(
        dataset,
        [
            {
                "doc_id": "GDPR Regulation.pdf",
                "table_id": "table_1",
                "header": ["Country", "Code"],
                "data": [["France", "FR"]],
            }
        ],
    )

    document = document_uri("GDPR Regulation.pdf")
    table = table_uri("GDPR Regulation.pdf", "table_1")
    graph = dataset.graph(document)
    assert (table, RDF.type, JS_SOURCE.Table) in graph
    assert (document, JS_SOURCE.has_table, table) in graph
    assert (table, JS_SOURCE.source_document, document) in graph
    assert not list(graph.objects(table, JS_SOURCE.source_chunk))
    assert "France" not in dataset.serialize(format="nquads")
    assert "Country" not in dataset.serialize(format="nquads")


def test_optional_source_chunk_is_linked_only_when_explicitly_given():
    dataset = Dataset()
    enrich_dataset_with_tables(
        dataset,
        [{"doc_id": "doc-1", "table_id": "table_3", "source_chunk_id": "chunk-07"}],
    )

    graph = dataset.graph(document_uri("doc-1"))
    table = table_uri("doc-1", "table_3")
    assert (table, JS_SOURCE.source_chunk, chunk_uri("doc-1", "chunk-07")) in graph


def test_table_source_uris_match_graph_serializer_and_keep_dotted_ids():
    from jurisynth.kg_construction_pipeline.src.source_uri import decode_fragment

    first = "C_2012219EN.01000101"
    second = "C_2012219EN.01000501"
    assert document_uri(first) != document_uri(second)
    assert chunk_uri(first, "chunk_1") != chunk_uri(second, "chunk_1")
    assert table_uri(first, "table_1") != table_uri(second, "table_1")
    assert decode_fragment(str(chunk_uri(first, "chunk_1")).removeprefix(str(CHUNK))) == (first, "chunk_1")


def test_transitional_lookup_keeps_existing_batch_graph_uris():
    doc_id = "C_2012219EN.01000101"
    assert legacy_chunk_uri(doc_id, "chunk_1") == CHUNK["c_2012219en_chunk_1"]
    assert chunk_uri_candidates(doc_id, "chunk_1") == (
        chunk_uri(doc_id, "chunk_1"), legacy_chunk_uri(doc_id, "chunk_1"),
    )


def test_table_store_loader_is_deterministic_and_rejects_incomplete_records(tmp_path):
    (tmp_path / "z.json").write_text(json.dumps({"doc_id": "Z", "table_id": "2"}), encoding="utf-8")
    (tmp_path / "a.json").write_text(json.dumps({"doc_id": "A", "table_id": "1"}), encoding="utf-8")
    dataset = enrich_dataset_from_table_store(Dataset(), tmp_path)
    assert (table_uri("A", "1"), RDF.type, JS_SOURCE.Table) in dataset.graph(document_uri("A"))
    assert (table_uri("Z", "2"), RDF.type, JS_SOURCE.Table) in dataset.graph(document_uri("Z"))

    with pytest.raises(ValueError, match="table_id"):
        enrich_dataset_with_tables(Dataset(), [{"doc_id": "A"}])
