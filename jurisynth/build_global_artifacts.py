"""Materialize selected global Jurisynth artifacts from a validated manifest.

Targets are intentionally explicit.  RDF can be safely streamed on a laptop;
the FAISS and table targets can require substantially more memory and disk.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from jurisynth.resource_aggregator import (
    BatchArtifacts,
    EmbeddingSpec,
    merge_chunk_indices,
    merge_image_stores,
    merge_image_indices,
    merge_nquads,
    merge_table_artifacts,
    validate_batches,
)


def _resolve(value: str | None, workspace_root: Path) -> Path | None:
    if value is None:
        return None
    path = Path(value)
    return path if path.is_absolute() else workspace_root / path


def load_manifest_batches(manifest_path: str | Path, *, workspace_root: str | Path) -> list[BatchArtifacts]:
    """Rehydrate validated batch artifacts from the portable JSON manifest."""
    payload = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    if payload.get("manifest_version") != "1.0":
        raise ValueError("Unsupported aggregation manifest version")
    root = Path(workspace_root).resolve()
    batches = []
    for entry in payload.get("batches", []):
        chunk_spec = entry.get("chunk_embedding")
        table_spec = entry.get("table_embedding")
        batches.append(BatchArtifacts(
            batch_id=str(entry["batch_id"]),
            graph_nquads=_resolve(entry["graph_nquads"], root),
            chunk_index=_resolve(entry["chunk_index"], root),
            chunk_metadata=_resolve(entry["chunk_metadata"], root),
            table_store=_resolve(entry.get("table_store"), root),
            table_index=_resolve(entry.get("table_index"), root),
            table_metadata=_resolve(entry.get("table_metadata"), root),
            row_metadata=_resolve(entry.get("row_metadata"), root),
            row_indices=_resolve(entry.get("row_indices"), root),
            image_store=_resolve(entry.get("image_store"), root),
            image_index=_resolve(entry.get("image_index"), root),
            image_metadata=_resolve(entry.get("image_metadata"), root),
            chunk_embedding=EmbeddingSpec(**chunk_spec) if chunk_spec else None,
            table_embedding=EmbeddingSpec(**table_spec) if table_spec else None,
            image_embedding=EmbeddingSpec(**entry["image_embedding"]) if entry.get("image_embedding") else None,
        ))
    return validate_batches(batches)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", choices=("rdf", "chunks", "tables", "images"))
    parser.add_argument("--manifest", type=Path, default=Path("jurisynth/global_artifacts/manifest.json"))
    parser.add_argument("--workspace-root", type=Path, default=Path.cwd())
    parser.add_argument("--destination", type=Path, default=Path("jurisynth/global_artifacts"))
    args = parser.parse_args()

    batches = load_manifest_batches(args.manifest, workspace_root=args.workspace_root)
    destination = args.destination
    if args.target == "rdf":
        result = merge_nquads(batches, destination / "graph" / "jurisynth_graph.nq")
    elif args.target == "chunks":
        result = merge_chunk_indices(
            batches,
            destination_index=destination / "chunk_index" / "chunk_index.faiss",
            destination_metadata=destination / "chunk_index" / "chunk_metadata.pkl",
        )
    elif args.target == "tables":
        table_batches = [batch for batch in batches if batch.table_index is not None]
        result = merge_table_artifacts(table_batches, destination / "tables")
    else:
        image_batches = [batch for batch in batches if batch.image_index is not None]
        store = merge_image_stores(image_batches, destination / "images" / "image_store")
        index, metadata = merge_image_indices(image_batches, destination_index=destination / "images" / "image_index" / "image.index", destination_metadata=destination / "images" / "image_index" / "metadata.json")
        result = {"image_store": str(store), "image_index": str(index), "image_metadata": str(metadata)}
    print({"target": args.target, "batch_count": len(batches), "result": str(result)})


if __name__ == "__main__":
    main()
