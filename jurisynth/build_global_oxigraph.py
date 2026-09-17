"""Materialise the global N-Quads graph as a local, disk-backed Oxigraph store.

This is a one-time, local preparation step.  It uses Oxigraph's streaming bulk
loader, then opens read-only at query time; it does not start a network server.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path


def _directory_size(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def _sha256(path: Path, *, block_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(block_size), b""):
            digest.update(block)
    return digest.hexdigest()


def build(graph: Path, destination: Path) -> dict[str, object]:
    """Bulk-load one immutable N-Quads file into a new persistent store."""
    try:
        from pyoxigraph import RdfFormat, Store
    except ModuleNotFoundError as exc:
        raise RuntimeError("Install pyoxigraph==0.5.11 before building the local RDF store.") from exc
    if not graph.is_file():
        raise FileNotFoundError(f"Global N-Quads graph does not exist: {graph}")
    if destination.exists() and any(destination.iterdir()):
        raise FileExistsError(f"Refusing to overwrite existing Oxigraph store: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    store = Store(str(destination))
    store.bulk_load(path=str(graph), format=RdfFormat.N_QUADS)
    store.optimize()
    store.flush()
    elapsed = time.monotonic() - started
    manifest = {
        "schema_version": 1,
        "backend": "pyoxigraph",
        "storage": "rocksdb",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_graph": str(graph),
        "source_bytes": graph.stat().st_size,
        "source_sha256": _sha256(graph),
        "store_bytes": _directory_size(destination),
        "build_seconds": round(elapsed, 3),
        "read_only_query_contract": True,
    }
    (destination / "jurisynth_oxigraph_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, default=Path("jurisynth/global_artifacts/graph/jurisynth_graph.nq"))
    parser.add_argument("--destination", type=Path, default=Path("jurisynth/global_artifacts/oxigraph"))
    args = parser.parse_args()
    result = build(args.graph, args.destination)
    print(json.dumps({
        "destination": str(args.destination),
        "source_bytes": result["source_bytes"],
        "store_bytes": result["store_bytes"],
        "build_seconds": result["build_seconds"],
    }, indent=2))


if __name__ == "__main__":
    main()
