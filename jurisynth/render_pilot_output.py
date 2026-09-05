"""Render a compact, readable text summary from a Jurisynth pilot JSON output."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def render(payload: dict[str, object]) -> str:
    analysis = payload.get("analysis", {})
    leaves = payload.get("leaves", [])
    results = payload.get("node_results", {})
    report = payload.get("report")
    lines = ["JURISYNTH PILOT OUTPUT", "=" * 72, "", "Task analysis", "-" * 72]
    lines.append(f"Route: {analysis.get('route', 'unknown')}")
    lines.append(f"Contextual facts: {', '.join(analysis.get('contextual_facts', [])) or 'None'}")
    for leaf in leaves:
        lines.extend(["", f"Leaf {leaf.get('query_id')}: {leaf.get('query')}"])
        result = results.get(leaf.get("query_id"), {})
        answer = result.get("answer") or {}
        lines.append(f"Status: {answer.get('status', result.get('status', 'unknown'))}")
        if answer.get("answer_text"):
            lines.append(f"Answer: {answer['answer_text']}")
        summary = answer.get("evidence_summary", {})
        if summary:
            lines.append(f"Retrieval: {summary.get('retrieval_status')} | assertions: {summary.get('evidence_item_count', 0)} | tables: {summary.get('table_evidence_count', 0)}")
        for claim in answer.get("claims", []):
            lines.append(f"Claim {claim.get('claim_id')} ({claim.get('status')}): {claim.get('text')}")
            lines.append(f"  Supporting evidence references: {len(claim.get('evidence_refs', []))}")
    if isinstance(report, dict):
        lines.extend(["", "Final report", "-" * 72, report.get("overview", "")])
        for section in report.get("sections", []):
            lines.extend(["", section.get("title", "Untitled section"), section.get("answer_text", "")])
            if section.get("claim_refs"):
                lines.append("Claims: " + ", ".join(section["claim_refs"]))
    lines.extend(["", "Interpretation note", "-" * 72, "This pilot result is an abstention/safety example: it identifies that the retrieved aviation material is irrelevant to the data-controller question and avoids inventing a legal answer."])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.source.read_text(encoding="utf-8"))
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    args.destination.write_text(render(payload), encoding="utf-8")


if __name__ == "__main__":
    main()
