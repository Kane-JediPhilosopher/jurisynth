import asyncio
import pickle

import faiss
import numpy as np
from pyoxigraph import NamedNode, Quad, Store

from jurisynth.build_global_oxigraph import build
from jurisynth.contracts import RetrievalRequest, SourceChunk
from jurisynth.retrieval_mech.er_index_builder import ResourceRecord
from jurisynth.retrieval_mech.er_matcher import Concept, ERMatcher, PersistedERIndices
from jurisynth.retrieval_mech.lazy_chunk_metadata import SQLiteChunkMetadata, build_sqlite_chunk_metadata
from jurisynth.retrieval_mech.global_artifacts import load_global_artifacts
from jurisynth.retrieval_mech.rdf_retriever import DirectRDFRetriever
from jurisynth.retrieval_mech.rdf_store import OxigraphQuadStore
from jurisynth.table_rdf_enricher import chunk_uri


class Embedder:
    def encode(self, texts, *, normalize_embeddings=True, **kwargs):
        return np.asarray([[1.0, 0.0] for _ in texts], dtype=np.float32)


class Interpreter:
    async def interpret(self, request):
        return [Concept("controller", "controller")], []


def test_oxigraph_backend_returns_the_same_provenance_bounded_evidence(tmp_path):
    controller = "https://example.test/controller"
    processor = "https://example.test/processor"
    predicate = "https://example.test/must_provide"
    graph = str(chunk_uri("doc", "chunk_1"))
    store_path = tmp_path / "store"
    store = Store(str(store_path))
    store.add(Quad(NamedNode(controller), NamedNode(predicate), NamedNode(processor), NamedNode(graph)))
    store.flush()

    index = faiss.IndexFlatIP(2)
    index.add(np.asarray([[1.0, 0.0]], dtype=np.float32))
    indices = PersistedERIndices(index, None, [ResourceRecord(controller, "controller")], [])
    source = SourceChunk("chunk_1", "doc", "A controller must provide information.")
    retriever = DirectRDFRetriever(
        OxigraphQuadStore(store), ERMatcher(indices, Embedder()),
        chunk_resolver=lambda graph_id: source if graph_id == graph else None,
        interpreter=Interpreter(),
    )

    result = asyncio.run(retriever.retrieve(RetrievalRequest("q", "controller duty")))

    assert [(item.assertion.subject, item.assertion.predicate, item.assertion.object) for item in result.evidence_items] == [
        (controller, predicate, processor),
    ]
    assert result.evidence_items[0].source_chunks == [source]


def test_sqlite_chunk_sidecar_resolves_only_requested_faiss_or_graph_records(tmp_path):
    source = tmp_path / "chunk_metadata.pkl"
    with source.open("wb") as file:
        pickle.dump({0: {"chunk_id": "chunk_1", "doc_id": "doc", "content": "excerpt"}}, file)
    destination = tmp_path / "chunk_metadata.sqlite"

    result = build_sqlite_chunk_metadata(source, destination)
    metadata = SQLiteChunkMetadata(destination)
    try:
        assert result["records"] == 1
        assert metadata[0] == {"chunk_id": "chunk_1", "doc_id": "doc", "content": "excerpt"}
        assert metadata.resolve_graph(str(chunk_uri("doc", "chunk_1"))) == SourceChunk("chunk_1", "doc", "excerpt")
        assert metadata.resolve_graph("http://jurisynth/source/chunk/missing") is None
        assert not metadata.has_ambiguous_provenance(str(chunk_uri("doc", "chunk_1")))
        metadata._connection.execute("INSERT INTO chunks VALUES (?, ?, ?, ?, ?)",
                                     (1, str(chunk_uri("doc", "chunk_1")), "chunk_1", "other_doc", "other excerpt"))
        metadata._connection.commit()
        assert metadata.has_ambiguous_provenance(str(chunk_uri("doc", "chunk_1")))
    finally:
        metadata.close()


def test_global_loader_opens_oxigraph_and_sqlite_sidecars_without_rdf_dataset_parse(tmp_path):
    root = tmp_path / "global"
    graph = root / "graph" / "jurisynth_graph.nq"
    graph.parent.mkdir(parents=True)
    graph.write_text(
        "<https://example.test/controller> <https://example.test/duty> <https://example.test/processor> "
        f"<{chunk_uri('doc', 'chunk_1')}> .\n", encoding="utf-8",
    )
    build(graph, root / "oxigraph")
    chunk_dir = root / "chunk_index"
    chunk_dir.mkdir()
    index = faiss.IndexFlatIP(2)
    index.add(np.asarray([[1.0, 0.0]], dtype=np.float32))
    faiss.write_index(index, str(chunk_dir / "chunk_index.faiss"))
    with (chunk_dir / "chunk_metadata.pkl").open("wb") as file:
        pickle.dump({0: {"chunk_id": "chunk_1", "doc_id": "doc", "content": "excerpt"}}, file)
    build_sqlite_chunk_metadata(chunk_dir / "chunk_metadata.pkl", chunk_dir / "chunk_metadata.sqlite")

    artifacts = load_global_artifacts(root)

    assert artifacts.resolve_chunk(str(chunk_uri("doc", "chunk_1"))) == SourceChunk("chunk_1", "doc", "excerpt")
    assert artifacts.chunk_index.search("controller", Embedder(), 1)[0].text == "excerpt"
    assert "Oxigraph" in artifacts.warnings[0]
