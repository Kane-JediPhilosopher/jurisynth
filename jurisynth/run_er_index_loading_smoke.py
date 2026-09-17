"""Measure adaptive global E-R index loading without NIM or full retrieval."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import psutil

from jurisynth.retrieval_mech.er_matcher import PersistedERIndices


def main() -> None:
    directory = Path("jurisynth/global_artifacts/community/er_index")
    process = psutil.Process(os.getpid())
    started = time.perf_counter()
    indices = PersistedERIndices.load(directory)
    print(json.dumps({
        "load": indices.load_metadata,
        "rss_mb": round(process.memory_info().rss / 1024 ** 2, 1),
        "load_seconds": round(time.perf_counter() - started, 3),
        "entity_records": len(indices.entity_records),
        "relation_records": len(indices.relation_records),
    }, indent=2))


if __name__ == "__main__":
    main()
