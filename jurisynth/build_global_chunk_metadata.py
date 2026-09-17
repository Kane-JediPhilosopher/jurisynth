"""Create the SQLite lazy-metadata sidecar used by local global retrieval."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from jurisynth.retrieval_mech.lazy_chunk_metadata import build_sqlite_chunk_metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("jurisynth/global_artifacts/chunk_index/chunk_metadata.pkl"))
    parser.add_argument("--destination", type=Path, default=Path("jurisynth/global_artifacts/chunk_index/chunk_metadata.sqlite"))
    args = parser.parse_args()
    print(json.dumps(build_sqlite_chunk_metadata(args.source, args.destination), indent=2))


if __name__ == "__main__":
    main()
