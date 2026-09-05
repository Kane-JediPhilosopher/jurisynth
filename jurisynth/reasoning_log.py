"""Append-only, JSONL observability records for Jurisynth runs."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class ReasoningLog:
    """Write one structured event per line without retaining secrets or raw prompts."""

    def __init__(self, path: str | Path, run_id: str) -> None:
        if not run_id.strip():
            raise ValueError("run_id must not be empty")
        self.path = Path(path)
        self.run_id = run_id

    def record(self, event: str, **payload: Any) -> dict[str, Any]:
        """Append an event and return its JSON-ready representation for callers/tests."""
        if not event.strip():
            raise ValueError("event must not be empty")
        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "run_id": self.run_id,
            "event": event,
            **{key: _json_value(value) for key, value in payload.items()},
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        return record


def _json_value(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    return value
