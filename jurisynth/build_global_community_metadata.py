"""Create lazy Community Graph query metadata for global retrieval."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from jurisynth.retrieval_mech.lazy_community_metadata import build_sqlite_community_metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hierarchy", type=Path, default=Path("jurisynth/global_artifacts/community/community_hierarchy.json"))
    parser.add_argument("--descriptors", type=Path, default=Path("jurisynth/global_artifacts/community/community_descriptors.json"))
    parser.add_argument("--destination", type=Path, default=Path("jurisynth/global_artifacts/community/community_metadata.sqlite"))
    args = parser.parse_args()
    print(json.dumps(build_sqlite_community_metadata(args.hierarchy, args.descriptors, args.destination), indent=2))


if __name__ == "__main__":
    main()
