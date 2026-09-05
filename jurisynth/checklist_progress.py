"""Print the current full-spec checklist progress from its Markdown source."""

from __future__ import annotations

import re
from pathlib import Path


_ITEM = re.compile(r"^\s*- \[([ x])\]", re.MULTILINE)


def progress(checklist: Path | None = None) -> dict[str, int | float]:
    source = checklist or Path(__file__).with_name("CHECKLIST.md")
    marks = _ITEM.findall(source.read_text(encoding="utf-8"))
    complete = marks.count("x")
    total = len(marks)
    return {"complete": complete, "remaining": total - complete, "total": total, "percent": round(100 * complete / total, 1) if total else 0.0}


def main() -> None:
    current = progress()
    print(f"{current['complete']} / {current['total']} complete ({current['percent']}%); {current['remaining']} remaining")


if __name__ == "__main__":
    main()
