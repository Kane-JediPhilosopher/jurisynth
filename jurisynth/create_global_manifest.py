"""Create a validated manifest for every completed KG-construction batch.

The manifest records artifact identities and embedding provenance before a
costly physical merge is attempted.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from jurisynth.resource_aggregator import (
    EmbeddingSpec,
    build_manifest,
    discover_batch,
    validate_batches,
    write_manifest,
)


DEFAULT_EMBEDDING = EmbeddingSpec("all-MiniLM-L6-v2", 384)


def _batch_number(path: Path) -> int:
    """Return the numeric identity of a ``batch_`` directory name."""
    try:
        return int(path.name.removeprefix("batch_"))
    except ValueError as exc:
        raise ValueError(f"Invalid batch directory name: {path.name}") from exc


def discover_completed_batches(
    processed_root: str | Path,
    source_root: str | Path,
) -> list:
    """Discover successful batches with matching source directories."""
    processed_root = Path(processed_root)
    source_root = Path(source_root)
    source_by_number: dict[int, Path] = {}
    for source in source_root.glob("batch_*"):
        if not source.is_dir():
            continue
        number = _batch_number(source)
        if number in source_by_number:
            raise ValueError(
                "Multiple source directories have the same batch identity: "
                f"{source_by_number[number].name!r}, {source.name!r}"
            )
        source_by_number[number] = source

    batches = []
    for processed in sorted(processed_root.glob("batch_*")):
        if not processed.is_dir() or not (processed / ".success").is_file():
            continue
        source = source_by_number.get(_batch_number(processed))
        if source is None:
            raise FileNotFoundError(f"No source batch matches {processed.name}")
        batches.append(
            discover_batch(
                processed.name,
                processed_batch_dir=processed,
                source_batch_dir=source,
                chunk_embedding=DEFAULT_EMBEDDING,
                table_embedding=DEFAULT_EMBEDDING,
            )
        )
    return validate_batches(batches)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--processed-root", type=Path, default=Path("jurisynth/kg_construction_pipeline/output"))
    parser.add_argument("--source-root", type=Path, default=Path("eu_legislation"))
    parser.add_argument("--destination", type=Path, default=Path("jurisynth/global_artifacts/manifest.json"))
    args = parser.parse_args()

    batches = discover_completed_batches(args.processed_root, args.source_root)
    manifest = build_manifest(batches, workspace_root=Path.cwd())
    write_manifest(manifest, args.destination)
    table_batches = sum(batch.table_index is not None for batch in batches)
    print({"batches": len(batches), "table_batches": table_batches, "destination": str(args.destination)})


if __name__ == "__main__":
    main()
