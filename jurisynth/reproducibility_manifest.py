"""Write a hash-backed manifest for a Jurisynth pilot run."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_manifest(destination: Path, *, artifacts: dict[str, Path], commands: list[str], models: dict[str, str], config: dict[str, object]) -> None:
    """Persist reproducibility metadata; callers choose only non-secret identifiers."""
    payload = {
        "schema_version": 1,
        "artifacts": {
            name: {"path": str(path), "sha256": file_sha256(path)}
            for name, path in sorted(artifacts.items())
        },
        "commands": commands,
        "models": models,
        "config": config,
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
