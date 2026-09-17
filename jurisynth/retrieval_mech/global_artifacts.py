"""Loader for local-first, corpus-wide retrieval artifacts.

The global graph is opened from an embedded read-only Oxigraph store rather
than parsed into RDFLib/Python memory. RDFLib remains the KG-construction and
small-pilot backend.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from rdflib import URIRef

from jurisynth.contracts import SourceChunk
from jurisynth.retrieval_mech.artifacts import ChunkIndex, ImageIndex, TableIndex
from jurisynth.retrieval_mech.document_metadata import DocumentMetadataStore
from jurisynth.retrieval_mech.lazy_chunk_metadata import SQLiteChunkMetadata
from jurisynth.retrieval_mech.rdf_store import OxigraphQuadStore


@dataclass(slots=True)
class GlobalArtifacts:
    dataset: object
    chunk_index: ChunkIndex
    table_index: TableIndex | None
    image_index: ImageIndex | None
    warnings: list[str]
    chunk_lookup: SQLiteChunkMetadata
    document_metadata: DocumentMetadataStore | None

    def resolve_chunk(self, graph_id: str | URIRef) -> SourceChunk | None:
        return self.chunk_lookup.resolve_graph(str(graph_id))


def load_global_artifacts(root: str | Path) -> GlobalArtifacts:
    """Load corpus-wide artifacts after explicit physical aggregation."""
    root = Path(root)
    chunk_dir = root / "chunk_index"
    store_dir = root / "oxigraph"
    metadata_store = chunk_dir / "chunk_metadata.sqlite"
    required = (
        store_dir / "jurisynth_oxigraph_manifest.json",
        chunk_dir / "chunk_index.faiss",
        metadata_store,
    )
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "Global retrieval requires the local Oxigraph store and SQLite chunk sidecar; missing: "
            + ", ".join(missing)
            + ". Run `python -m jurisynth.build_global_oxigraph` and "
            + "`python -m jurisynth.build_global_chunk_metadata` once."
        )
    chunk_lookup = SQLiteChunkMetadata(metadata_store)
    dataset = OxigraphQuadStore.open_read_only(store_dir)
    chunks = ChunkIndex.load(
        chunk_dir / "chunk_index.faiss", chunk_dir / "chunk_metadata.pkl", lazy_metadata=chunk_lookup,
    )
    warnings: list[str] = ["Global RDF retrieval uses a local read-only Oxigraph store; no RDFLib global graph is materialized."]
    table_root = root / "tables"
    index_dir = table_root / "table_index"
    table_files = (index_dir / "table.index", index_dir / "table_metadata.json", index_dir / "row_metadata.json")
    table_index = None
    if all(path.is_file() for path in table_files):
        table_index = TableIndex.load(table_root, index_dir=index_dir, table_store=table_root / "table_store")
    else:
        warnings.append("Global table artifacts are not materialized; table retrieval is unavailable.")
    image_root = root / "images"
    image_index = ImageIndex.load(image_root) if (image_root / "image_index" / "image.index").is_file() else None
    if image_index is None:
        warnings.append("Global image artifacts are not materialized; visual retrieval is unavailable.")
    document_metadata_path = root / "document_metadata.sqlite"
    document_metadata = (
        DocumentMetadataStore(document_metadata_path)
        if document_metadata_path.is_file()
        else None
    )
    if document_metadata is None:
        warnings.append(
            "Document metadata sidecar is unavailable; instrument-scope classification is disabled."
        )
    return GlobalArtifacts(
        dataset, chunks, table_index, image_index, warnings, chunk_lookup, document_metadata
    )
