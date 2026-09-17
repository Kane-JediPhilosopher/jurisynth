"""Build exact 2/3/4-way disk-backed E-R shard configurations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from jurisynth.retrieval_mech.er_shards import build_er_shards


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("jurisynth/global_artifacts/community/er_index"),
        help="Directory containing entity.index and relation.index.",
    )
    parser.add_argument("--shards", type=int, nargs="+", default=[2, 3, 4])
    parser.add_argument(
        "--minimum-available-gb",
        type=float,
        default=7.0,
        help="Safety floor checked before each configuration build.",
    )
    args = parser.parse_args()
    results: dict[str, object] = {}
    for count in args.shards:
        destination = args.source / "shards" / str(count)
        results[str(count)] = build_er_shards(
            args.source,
            destination,
            shard_count=count,
            minimum_available_gb=args.minimum_available_gb,
        )
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
