"""Record cold global-artifact load time and resident memory without NIM calls."""

from __future__ import annotations

import argparse
import gc
import json
import os
import time
from pathlib import Path

import psutil

from jurisynth.main import _load_community_guidance
from jurisynth.retrieval_mech.er_matcher import PersistedERIndices
from jurisynth.retrieval_mech.global_artifacts import load_global_artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, default=Path("jurisynth/global_artifacts"))
    parser.add_argument("--output", type=Path, default=Path("jurisynth/run_outputs/global_artifact_benchmark.json"))
    args = parser.parse_args()
    started = time.perf_counter()
    artifacts = load_global_artifacts(args.artifact_root)
    community_dir = args.artifact_root / "community"
    indices = PersistedERIndices.load(community_dir / "er_index")
    _, orientation_builder, descriptors = _load_community_guidance(
        community_dir / "er_index", indices,
        hierarchy_path=community_dir / "community_hierarchy.json",
        descriptor_path=community_dir / "community_descriptors.json",
    )
    gc.collect()
    process = psutil.Process(os.getpid())
    payload = {
        "backend": "pyoxigraph+sqlite-sidecars",
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "rss_mb": round(process.memory_info().rss / 1024 ** 2, 1),
        "chunk_records": len(artifacts.chunk_index.metadata),
        "entity_records": len(indices.entity_records),
        "relation_records": len(indices.relation_records),
        "community_descriptors": len(descriptors),
        "community_guidance_enabled": orientation_builder is not None,
        "warnings": artifacts.warnings,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
