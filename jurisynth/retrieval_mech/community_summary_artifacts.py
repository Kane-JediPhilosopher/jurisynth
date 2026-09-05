"""Persisted, versioned community orientation summaries for greedy retrieval."""

from __future__ import annotations

import json
from pathlib import Path

from jurisynth.retrieval_mech.community_summary import CommunitySummaryInput


SCHEMA_VERSION = 1


def write_summary_artifacts(destination: Path, summaries: list[CommunitySummaryInput], *, source_graph: str) -> None:
    """Write graph-construction summaries separately from retrieval evidence."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "source_graph": source_graph,
        "summaries": [
            {"community_id": item.community_id, "summary": item.summary, "level": item.level, "branch_distance": item.branch_distance, "provenance": item.provenance}
            for item in summaries
        ],
    }
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_summary_artifacts(source: Path) -> dict[str, CommunitySummaryInput]:
    payload = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema_version") != SCHEMA_VERSION or not isinstance(payload.get("summaries"), list):
        raise ValueError("Unsupported community summary artifact.")
    results: dict[str, CommunitySummaryInput] = {}
    for raw in payload["summaries"]:
        if not isinstance(raw, dict) or not isinstance(raw.get("community_id"), str) or not isinstance(raw.get("summary"), str):
            raise ValueError("Malformed community summary record.")
        item = CommunitySummaryInput(raw["community_id"], raw["summary"], raw.get("level"), raw.get("branch_distance"), raw.get("provenance", {}))
        if item.community_id in results:
            raise ValueError(f"Duplicate community summary ID: {item.community_id}")
        results[item.community_id] = item
    return results
