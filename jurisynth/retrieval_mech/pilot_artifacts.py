"""Explicit loader for a single processed batch and its raw table store.

This is intentionally a pilot adapter, not the future global Resource
Aggregator. It permits the MVP to validate retrieval against one completed KG
batch while retaining the different locations of processed indexes and raw
table JSON artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from rdflib import Dataset, URIRef

from jurisynth.contracts import SourceChunk
from jurisynth.retrieval_mech.artifacts import ChunkIndex, TableIndex
from jurisynth.table_rdf_enricher import chunk_uri


@dataclass(slots=True)
class PilotBatchArtifacts:
    dataset: Dataset
    chunk_index: ChunkIndex
    table_index: TableIndex | None
    table_store: Path | None
    warnings: list[str]
    chunk_lookup: dict[URIRef, SourceChunk]

    def resolve_chunk(self, graph_id: URIRef) -> SourceChunk | None:
        """Resolve a semantic named-graph URI to its original chunk metadata."""
        return self.chunk_lookup.get(graph_id)


def load_pilot_batch(processed_batch_dir: str | Path, *, raw_batch_dir: str | Path | None = None) -> PilotBatchArtifacts:
    """Load a processed RDF/chunk batch and optionally its separately stored tables."""
    processed = Path(processed_batch_dir)
    graph_path = processed / "graph" / "jurisynth_graph.nq"
    chunk_dir = processed / "chunk_index"
    dataset = Dataset()
    dataset.parse(graph_path, format="nquads")
    chunks = ChunkIndex.load(chunk_dir / "chunk_index.faiss", chunk_dir / "chunk_metadata.pkl")

    raw = Path(raw_batch_dir) if raw_batch_dir is not None else processed
    table_store = raw / "table_store"
    warnings: list[str] = []
    table_index: TableIndex | None = None
    table_index_dir = raw / "table_index"
    table_index_files = (
        table_index_dir / "table.index",
        table_index_dir / "table_metadata.json",
        table_index_dir / "row_metadata.json",
    )
    if all(path.exists() for path in table_index_files):
        table_index = TableIndex.load(raw, index_dir=table_index_dir, table_store=table_store)
    elif table_store.is_dir():
        warnings.append("Persisted table JSON is available, but table/row FAISS artifacts are not yet available for search.")
    else:
        table_store = None
        warnings.append("No persisted table artifacts were found for this batch.")

    chunk_lookup = {
        chunk_uri(item["doc_id"], item["chunk_id"]): SourceChunk(
            chunk_id=item["chunk_id"], document_id=item["doc_id"], text=item["content"]
        )
        for item in chunks.metadata.values()
    }
    return PilotBatchArtifacts(dataset, chunks, table_index, table_store, warnings, chunk_lookup)
