"""Manifest-first aggregation for per-batch Jurisynth artifacts.

The collector records batch artifacts before any irreversible global merge.
Physical FAISS and RDF merges remain explicit follow-on operations because they
must validate embedding compatibility and named-graph identity first.
"""

from __future__ import annotations

import json
import pickle
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import numpy as np

try:
    import faiss
except ModuleNotFoundError:
    faiss = None


MANIFEST_VERSION = "1.0"


@dataclass(frozen=True, slots=True)
class EmbeddingSpec:
    model_id: str
    dimension: int
    normalized: bool = True

    def __post_init__(self) -> None:
        if not self.model_id.strip() or self.dimension < 1:
            raise ValueError("EmbeddingSpec requires a model ID and positive dimension.")


@dataclass(frozen=True, slots=True)
class BatchArtifacts:
    batch_id: str
    graph_nquads: Path
    chunk_index: Path
    chunk_metadata: Path
    table_store: Path | None = None
    table_index: Path | None = None
    table_metadata: Path | None = None
    row_metadata: Path | None = None
    row_indices: Path | None = None
    image_store: Path | None = None
    chunk_embedding: EmbeddingSpec | None = None
    table_embedding: EmbeddingSpec | None = None

    def __post_init__(self) -> None:
        if not self.batch_id.strip():
            raise ValueError("batch_id must not be empty")


def discover_batch(
    batch_id: str,
    *,
    processed_batch_dir: str | Path,
    source_batch_dir: str | Path,
    chunk_embedding: EmbeddingSpec | None = None,
    table_embedding: EmbeddingSpec | None = None,
) -> BatchArtifacts:
    """Describe one batch using Jurisynth's current split artifact layout."""
    processed = Path(processed_batch_dir)
    source = Path(source_batch_dir)
    index_dir = source / "table_index"
    return BatchArtifacts(
        batch_id=batch_id,
        graph_nquads=processed / "graph" / "jurisynth_graph.nq",
        chunk_index=processed / "chunk_index" / "chunk_index.faiss",
        chunk_metadata=processed / "chunk_index" / "chunk_metadata.pkl",
        table_store=source / "table_store" if (source / "table_store").is_dir() else None,
        table_index=index_dir / "table.index" if (index_dir / "table.index").is_file() else None,
        table_metadata=index_dir / "table_metadata.json" if (index_dir / "table_metadata.json").is_file() else None,
        row_metadata=index_dir / "row_metadata.json" if (index_dir / "row_metadata.json").is_file() else None,
        row_indices=index_dir / "rows" if (index_dir / "rows").is_dir() else None,
        image_store=source / "image_store" if (source / "image_store").is_dir() else None,
        chunk_embedding=chunk_embedding,
        table_embedding=table_embedding,
    )


def validate_batches(batches: Iterable[BatchArtifacts]) -> list[BatchArtifacts]:
    """Return sorted batches only when their files and index groups are coherent."""
    ordered = sorted(batches, key=lambda batch: batch.batch_id)
    if len({batch.batch_id for batch in ordered}) != len(ordered):
        raise ValueError("Duplicate batch IDs are not allowed in an aggregation manifest.")
    for batch in ordered:
        for path in (batch.graph_nquads, batch.chunk_index, batch.chunk_metadata):
            if not path.is_file():
                raise FileNotFoundError(f"Required artifact is missing for {batch.batch_id}: {path}")
        table_paths = (batch.table_store, batch.table_index, batch.table_metadata, batch.row_metadata, batch.row_indices)
        if any(path is not None for path in table_paths):
            if not all(path is not None for path in table_paths):
                raise ValueError(f"Table artifacts for {batch.batch_id} must be complete or all absent.")
            for path in table_paths:
                if not path.exists():
                    raise FileNotFoundError(f"Table artifact is missing for {batch.batch_id}: {path}")
        if batch.image_store is not None and not batch.image_store.is_dir():
            raise FileNotFoundError(f"Image store is missing for {batch.batch_id}: {batch.image_store}")
    return ordered


def require_compatible_embeddings(batches: Iterable[BatchArtifacts], artifact_type: str) -> EmbeddingSpec:
    """Verify that a future physical FAISS merge is mathematically meaningful."""
    if artifact_type not in {"chunk", "table"}:
        raise ValueError("artifact_type must be 'chunk' or 'table'")
    attribute = f"{artifact_type}_embedding"
    specs = {getattr(batch, attribute) for batch in batches}
    if None in specs:
        raise ValueError(f"Cannot merge {artifact_type} FAISS indexes without embedding metadata for every batch.")
    if len(specs) != 1:
        raise ValueError(f"Cannot merge {artifact_type} FAISS indexes with incompatible embedding specifications.")
    return next(iter(specs))


def build_manifest(batches: Iterable[BatchArtifacts], *, workspace_root: str | Path) -> dict[str, object]:
    """Build a deterministic, portable JSON-ready aggregation manifest."""
    root = Path(workspace_root).resolve()
    validated = validate_batches(batches)

    def portable(path: Path | None) -> str | None:
        if path is None:
            return None
        try:
            return path.resolve().relative_to(root).as_posix()
        except ValueError:
            return str(path.resolve())

    return {
        "manifest_version": MANIFEST_VERSION,
        "batches": [
            {
                "batch_id": batch.batch_id,
                "graph_nquads": portable(batch.graph_nquads),
                "chunk_index": portable(batch.chunk_index),
                "chunk_metadata": portable(batch.chunk_metadata),
                "table_store": portable(batch.table_store),
                "table_index": portable(batch.table_index),
                "table_metadata": portable(batch.table_metadata),
                "row_metadata": portable(batch.row_metadata),
                "row_indices": portable(batch.row_indices),
                "image_store": portable(batch.image_store),
                "chunk_embedding": asdict(batch.chunk_embedding) if batch.chunk_embedding else None,
                "table_embedding": asdict(batch.table_embedding) if batch.table_embedding else None,
            }
            for batch in validated
        ],
    }


def write_manifest(manifest: dict[str, object], destination: str | Path) -> None:
    """Write the manifest deterministically; callers choose when global state is saved."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def merge_nquads(batches: Iterable[BatchArtifacts], destination: str | Path) -> Path:
    """Merge validated per-batch RDF into one parseable Dataset without changing graph IDs.

    The destination must be new. This keeps the physical merge explicit and avoids
    silently replacing a costly global artifact.
    """
    try:
        from rdflib import Dataset
    except ModuleNotFoundError as exc:
        raise RuntimeError("RDF aggregation requires rdflib in the Python 3.12 environment.") from exc
    destination = Path(destination)
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing aggregate RDF: {destination}")
    dataset = Dataset()
    for batch in validate_batches(batches):
        dataset.parse(batch.graph_nquads, format="nquads")
    destination.parent.mkdir(parents=True, exist_ok=True)
    dataset.serialize(destination=destination, format="nquads")
    return destination


def merge_chunk_indices(
    batches: Iterable[BatchArtifacts],
    *,
    destination_index: str | Path,
    destination_metadata: str | Path,
) -> tuple[Path, Path]:
    """Concatenate compatible flat chunk vectors with deterministic global IDs."""
    if faiss is None:
        raise RuntimeError("Chunk-index aggregation requires faiss-cpu in the Python 3.12 environment.")
    ordered = validate_batches(batches)
    spec = require_compatible_embeddings(ordered, "chunk")
    destination_index = Path(destination_index)
    destination_metadata = Path(destination_metadata)
    if destination_index.exists() or destination_metadata.exists():
        raise FileExistsError("Refusing to overwrite existing aggregate chunk index or metadata.")
    output = (
        faiss.IndexFlatIP(spec.dimension)
        if spec.normalized
        else faiss.IndexFlatL2(spec.dimension)
    )
    merged_metadata: dict[int, dict[str, str]] = {}
    seen_chunks: set[tuple[str, str]] = set()
    for batch in ordered:
        index = faiss.read_index(str(batch.chunk_index))
        with batch.chunk_metadata.open("rb") as handle:
            metadata = {int(key): value for key, value in pickle.load(handle).items()}
        if index.ntotal != len(metadata):
            raise ValueError(f"Chunk index/metadata cardinality mismatch for {batch.batch_id}.")
        for vector_id in sorted(metadata):
            item = metadata[vector_id]
            try:
                chunk_key = (str(item["doc_id"]), str(item["chunk_id"]))
            except KeyError as exc:
                raise ValueError(f"Chunk metadata for {batch.batch_id} requires doc_id and chunk_id.") from exc
            if chunk_key in seen_chunks:
                raise ValueError(f"Duplicate chunk identity during aggregation: {chunk_key!r}")
            seen_chunks.add(chunk_key)
            output.add(np.asarray(index.reconstruct(vector_id), dtype=np.float32).reshape(1, -1))
            merged_metadata[len(merged_metadata)] = item
    destination_index.parent.mkdir(parents=True, exist_ok=True)
    destination_metadata.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(output, str(destination_index))
    with destination_metadata.open("wb") as handle:
        pickle.dump(merged_metadata, handle)
    return destination_index, destination_metadata


def merge_table_artifacts(batches: Iterable[BatchArtifacts], destination: str | Path) -> Path:
    """Materialize compatible table indexes, row indexes, metadata, and JSON stores.

    This retains the existing ``TableIndex`` layout under a new aggregate root;
    it does not rebuild embeddings or alter table/row identifiers.
    """
    if faiss is None:
        raise RuntimeError("Table aggregation requires faiss-cpu in the Python 3.12 environment.")
    ordered = validate_batches(batches)
    spec = require_compatible_embeddings(ordered, "table")
    destination = Path(destination)
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing aggregate table artifacts: {destination}")
    output_index = faiss.IndexFlatIP(spec.dimension) if spec.normalized else faiss.IndexFlatL2(spec.dimension)
    table_metadata: list[dict[str, str]] = []
    row_metadata: dict[str, list[dict[str, object]]] = {}
    seen_tables: set[tuple[str, str]] = set()
    for batch in ordered:
        if not all((batch.table_store, batch.table_index, batch.table_metadata, batch.row_metadata, batch.row_indices)):
            raise ValueError(f"Cannot materialize tables: {batch.batch_id} has no complete table artifact group.")
        index = faiss.read_index(str(batch.table_index))
        source_metadata = json.loads(batch.table_metadata.read_text(encoding="utf-8"))
        source_rows = json.loads(batch.row_metadata.read_text(encoding="utf-8"))
        if index.ntotal != len(source_metadata):
            raise ValueError(f"Table index/metadata cardinality mismatch for {batch.batch_id}.")
        for vector_id, table in enumerate(source_metadata):
            key = (str(table["doc_id"]), str(table["table_id"]))
            joined_key = f"{key[0]}__{key[1]}"
            if key in seen_tables:
                raise ValueError(f"Duplicate table identity during aggregation: {key!r}")
            if joined_key not in source_rows:
                raise ValueError(f"Missing row metadata for table {joined_key!r}")
            source_table = batch.table_store / f"{key[0]}_{key[1]}.json"
            source_row_index = batch.row_indices / f"{joined_key}.index"
            if not source_table.is_file() or not source_row_index.is_file():
                raise FileNotFoundError(f"Missing persisted table JSON or row index for {joined_key!r}")
            seen_tables.add(key)
            output_index.add(np.asarray(index.reconstruct(vector_id), dtype=np.float32).reshape(1, -1))
            table_metadata.append(table)
            row_metadata[joined_key] = source_rows[joined_key]
    (destination / "table_index" / "rows").mkdir(parents=True, exist_ok=False)
    (destination / "table_store").mkdir()
    faiss.write_index(output_index, str(destination / "table_index" / "table.index"))
    (destination / "table_index" / "table_metadata.json").write_text(json.dumps(table_metadata, indent=2), encoding="utf-8")
    (destination / "table_index" / "row_metadata.json").write_text(json.dumps(row_metadata, indent=2, sort_keys=True), encoding="utf-8")
    for batch in ordered:
        assert batch.table_store and batch.table_metadata and batch.row_indices
        for table in json.loads(batch.table_metadata.read_text(encoding="utf-8")):
            doc_id, table_id = table["doc_id"], table["table_id"]
            joined_key = f"{doc_id}__{table_id}"
            shutil.copy2(batch.table_store / f"{doc_id}_{table_id}.json", destination / "table_store" / f"{doc_id}_{table_id}.json")
            shutil.copy2(batch.row_indices / f"{joined_key}.index", destination / "table_index" / "rows" / f"{joined_key}.index")
    return destination


def merge_image_stores(batches: Iterable[BatchArtifacts], destination: str | Path) -> Path:
    """Copy batch image stores under stable batch-ID namespaces without rewriting files."""
    destination = Path(destination)
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing aggregate image store: {destination}")
    destination.mkdir(parents=True)
    for batch in validate_batches(batches):
        if batch.image_store is None:
            continue
        target_root = destination / batch.batch_id
        for source in batch.image_store.rglob("*"):
            if not source.is_file():
                continue
            target = target_root / source.relative_to(batch.image_store)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    return destination
