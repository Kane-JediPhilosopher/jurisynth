"""Create the lazy E-R metadata sidecar for global FAISS matching."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from jurisynth.retrieval_mech.lazy_er_metadata import build_sqlite_er_metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("jurisynth/global_artifacts/community/er_index/metadata.json"))
    parser.add_argument("--destination", type=Path, default=Path("jurisynth/global_artifacts/community/er_index/er_metadata.sqlite"))
    args = parser.parse_args()
    print(json.dumps(build_sqlite_er_metadata(args.source, args.destination), indent=2))


if __name__ == "__main__":
    main()
