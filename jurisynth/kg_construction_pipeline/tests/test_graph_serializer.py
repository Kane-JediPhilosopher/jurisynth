import pytest

from rdflib import Literal, Namespace, RDF, RDFS, URIRef, XSD

from graph_serializer import (
    normalize_identifier,
    document_uri,
    chunk_uri,
    assertion_uri,
    modifier_uri,
    serialize_modifier,
    build_quad_dataset,
    serialize_dataset,
    serialize_graph,
    JS_SOURCE,
    JS_DATA,
    DOCUMENT,
    CHUNK,
    ASSERTION,
)


# =====================================================================
# Namespace and test helper
# =====================================================================

EX = Namespace("http://example.org/")

def make_assertion(
    doc_id="doc1",
    chunk_id="chunk1",
    assertion_id=1,
    subject=None,
    predicate=None,
    obj=None,
    modifiers=None,
):
    return {
        "doc_id": doc_id,
        "chunk_id": chunk_id,
        "assertion_id": assertion_id,
        "assertion": {
            "subject": subject or EX.Alice,
            "predicate": predicate or EX.knows,
            "object": obj or EX.Bob,
        },
        "modifiers": modifiers or [],
    }


# =====================================================================
# URI helper tests
# =====================================================================

def test_normalize_identifier():
    assert normalize_identifier("DOC-123.PDF") == "doc_123"


def test_normalize_identifier_collapses_underscores():
    assert normalize_identifier("hello---world___test") == "hello_world_test"


def test_document_uri():
    assert document_uri("DOC-123.PDF") == DOCUMENT["doc_123"]


def test_chunk_uri():
    assert chunk_uri("DOC-123.PDF", "chunk_1") == CHUNK["doc_123_chunk_1"]


def test_assertion_uri():
    assert assertion_uri("DOC-123.PDF", "chunk_1", 42) == (
        ASSERTION["doc_123_chunk_1_42"]
    )


def test_modifier_uri():
    uri = modifier_uri("DOC-123.PDF", "chunk_1", 42, 1)

    assert uri == JS_DATA["modifier_doc_123_chunk_1_42_1"]


# =====================================================================
# Core triple serialization
# =====================================================================

def test_build_dataset_serializes_core_triple():
    assertion = make_assertion()

    dataset = build_quad_dataset([assertion])

    graph = dataset.graph(
        chunk_uri("doc1", "chunk1")
    )

    assert (
        EX.Alice,
        EX.knows,
        EX.Bob,
    ) in graph


# =====================================================================
# Document provenance
# =====================================================================

def test_build_dataset_creates_document_provenance():
    assertion = make_assertion()

    dataset = build_quad_dataset([assertion])

    doc = document_uri("doc1")
    chunk = chunk_uri("doc1", "chunk1")

    graph = dataset.graph(doc)

    assert (doc, RDF.type, JS_SOURCE.Document) in graph
    assert (doc, RDFS.label, Literal("doc1")) in graph
    assert (doc, JS_SOURCE.has_chunk, chunk) in graph


# =====================================================================
# Chunk provenance
# =====================================================================

def test_build_dataset_types_chunk():
    assertion = make_assertion()

    dataset = build_quad_dataset([assertion])

    doc = document_uri("doc1")
    chunk = chunk_uri("doc1", "chunk1")

    graph = dataset.graph(doc)

    assert (chunk, RDF.type, JS_SOURCE.Chunk) in graph


# =====================================================================
# Modifier serialization
# =====================================================================

def test_modifier_creates_assertion_structure():
    assertion = make_assertion(
        modifiers=["according to Article 5"]
    )

    dataset = build_quad_dataset([assertion])

    assertion_resource = assertion_uri(
        "doc1",
        "chunk1",
        1,
    )

    graph = dataset.graph(ASSERTION)

    assert (
        assertion_resource,
        RDF.type,
        JS_SOURCE.Assertion,
    ) in graph

    assert (
        assertion_resource,
        JS_SOURCE.subject,
        EX.Alice,
    ) in graph

    assert (
        assertion_resource,
        JS_SOURCE.predicate,
        EX.knows,
    ) in graph

    assert (
        assertion_resource,
        JS_SOURCE.object,
        EX.Bob,
    ) in graph


# =====================================================================
# Modifier resource
# =====================================================================

def test_modifier_is_serialized():
    assertion = make_assertion(
        modifiers=["according to Article 5"]
    )

    dataset = build_quad_dataset([assertion])

    modifier_resource = modifier_uri(
        "doc1",
        "chunk1",
        1,
        1,
    )

    graph = dataset.graph(ASSERTION)

    assert (
        modifier_resource,
        RDF.type,
        JS_SOURCE.Modifier,
    ) in graph

    assert (
        modifier_resource,
        JS_SOURCE.value,
        Literal("according to Article 5"),
    ) in graph


# =====================================================================
# Assertion-source chunk provenance
# =====================================================================

def test_assertion_links_to_modifier():
    assertion = make_assertion(
        modifiers=["according to Article 5"]
    )

    dataset = build_quad_dataset([assertion])

    assertion_resource = assertion_uri(
        "doc1",
        "chunk1",
        1,
    )

    modifier_resource = modifier_uri(
        "doc1",
        "chunk1",
        1,
        1,
    )

    graph = dataset.graph(ASSERTION)

    assert (
        assertion_resource,
        JS_SOURCE.has_modifier,
        modifier_resource,
    ) in graph


# =====================================================================
# Document-assertion provenance
# =====================================================================

def test_document_links_to_assertion():
    assertion = make_assertion(
        modifiers=["modifier"]
    )

    dataset = build_quad_dataset([assertion])

    doc = document_uri("doc1")

    assertion_resource = assertion_uri(
        "doc1",
        "chunk1",
        1,
    )

    graph = dataset.graph(doc)

    assert (
        doc,
        JS_SOURCE.has_assertion,
        assertion_resource,
    ) in graph


# =====================================================================
# Multiple modifiers
# =====================================================================

def test_multiple_modifiers_are_serialized():
    assertion = make_assertion(
        modifiers=[
            "according to Article 5",
            "subject to Article 10",
            "from the Commission",
        ]
    )

    dataset = build_quad_dataset([assertion])

    graph = dataset.graph(ASSERTION)

    assertion_resource = assertion_uri(
        "doc1",
        "chunk1",
        1,
    )

    for modifier_id, value in enumerate(
        assertion["modifiers"],
        start=1,
    ):
        modifier_resource = modifier_uri(
            "doc1",
            "chunk1",
            1,
            modifier_id,
        )

        assert (
            assertion_resource,
            JS_SOURCE.has_modifier,
            modifier_resource,
        ) in graph

        assert (
            modifier_resource,
            JS_SOURCE.value,
            Literal(value),
        ) in graph


# =====================================================================
# Literal objects
# =====================================================================

def test_literal_object_is_preserved():
    assertion = make_assertion(
        predicate=EX.age,
        obj=Literal(
            25,
            datatype=XSD.integer,
        ),
    )

    dataset = build_quad_dataset([assertion])

    graph = dataset.graph(
        chunk_uri("doc1", "chunk1")
    )

    assert (
        EX.Alice,
        EX.age,
        Literal(25, datatype=XSD.integer),
    ) in graph


# =====================================================================
# Multiple documents/chunks
# =====================================================================

def test_multiple_documents_and_chunks_are_separated():
    assertions = [
        make_assertion(
            doc_id="doc1",
            chunk_id="chunk1",
            assertion_id=1,
        ),
        make_assertion(
            doc_id="doc1",
            chunk_id="chunk2",
            assertion_id=2,
            subject=EX.Bob,
        ),
        make_assertion(
            doc_id="doc2",
            chunk_id="chunk1",
            assertion_id=1,
            subject=EX.Charlie,
        ),
    ]

    dataset = build_quad_dataset(assertions)

    graph1 = dataset.graph(
        chunk_uri("doc1", "chunk1")
    )
    graph2 = dataset.graph(
        chunk_uri("doc1", "chunk2")
    )
    graph3 = dataset.graph(
        chunk_uri("doc2", "chunk1")
    )

    assert (EX.Alice, EX.knows, EX.Bob) in graph1
    assert (EX.Bob, EX.knows, EX.Bob) in graph2
    assert (EX.Charlie, EX.knows, EX.Bob) in graph3


# =====================================================================
# Empty input
# =====================================================================

def test_empty_input_creates_empty_dataset():
    dataset = build_quad_dataset([])

    assert len(dataset) == 0


# =====================================================================
# Absence of modifiers
# =====================================================================

def test_assertion_resource_not_created_without_modifiers():
    assertion = make_assertion()

    dataset = build_quad_dataset([assertion])

    graph = dataset.graph(ASSERTION)

    assertion_resource = assertion_uri(
        "doc1",
        "chunk1",
        1,
    )

    assert (
        assertion_resource,
        RDF.type,
        JS_SOURCE.Assertion,
    ) not in graph


# =====================================================================
# Named graph serialization
# =====================================================================

def test_serialize_dataset(tmp_path):
    assertion = make_assertion(
        modifiers=["modifier"]
    )

    dataset = build_quad_dataset([assertion])

    output_file = tmp_path / "test.nq"

    serialize_dataset(
        dataset,
        str(output_file),
    )

    assert output_file.exists()
    assert output_file.stat().st_size > 0


# =====================================================================
# Serialization integration test
# =====================================================================

def test_serialize_graph(tmp_path):
    assertion = make_assertion()

    output_file = tmp_path / "jurisynth_graph.nq"

    dataset = serialize_graph(
        [assertion],
        output_file=str(output_file),
    )

    assert output_file.exists()
    assert output_file.stat().st_size > 0

    graph = dataset.graph(
        chunk_uri("doc1", "chunk1")
    )

    assert (
        EX.Alice,
        EX.knows,
        EX.Bob,
    ) in graph