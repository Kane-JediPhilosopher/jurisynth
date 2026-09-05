"""Create a parseable review-queue copy without altering human annotations.

The initial batch_0009 manually annotated queue has one known mechanical defect:
the second JSONL record is missing the closing brace for ``human_review`` before
``result``.  This utility repairs only that exact shape and validates every line.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


_MISSING_HUMAN_REVIEW_CLOSE = ', "result":'
_REPAIRED_HUMAN_REVIEW_CLOSE = '}, "result":'


def normalise_queue(source: Path, destination: Path) -> int:
    records: list[str] = []
    repaired = 0
    for line_number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        candidate = line
        try:
            json.loads(candidate)
        except json.JSONDecodeError:
            candidate = line.replace(_MISSING_HUMAN_REVIEW_CLOSE, _REPAIRED_HUMAN_REVIEW_CLOSE, 1)
            try:
                json.loads(candidate)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Cannot normalise JSONL record {line_number}: {exc.msg}") from exc
            repaired += 1
        records.append(candidate)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(records) + "\n", encoding="utf-8")
    return repaired


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(json.dumps({"repaired_records": normalise_queue(args.source, args.destination), "destination": str(args.destination)}))


if __name__ == "__main__":
    main()
