"""Build the deterministic source-document metadata sidecar."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from jurisynth.retrieval_mech.document_metadata import build_document_metadata_sidecar


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("eu_legislation"))
    parser.add_argument(
        "--destination",
        type=Path,
        default=Path("jurisynth/global_artifacts/document_metadata.sqlite"),
    )
    args = parser.parse_args()
    result = build_document_metadata_sidecar(args.source, args.destination)
    print(json.dumps({**result, "destination": str(args.destination)}, indent=2))


if __name__ == "__main__":
    main()
