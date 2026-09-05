"""Thin zero-shot evaluation adapter for completed Jurisynth reports."""

from __future__ import annotations

from dataclasses import dataclass

from jurisynth.agentic_reasoner.reporting import FinalReport


@dataclass(frozen=True, slots=True)
class LexGLUEAnswer:
    """Task-neutral payload; benchmark-specific label selection stays external."""

    answer_text: str
    claim_ids: tuple[str, ...]
    contradiction_ids: tuple[str, ...]


def adapt_report(report: FinalReport | None) -> LexGLUEAnswer:
    """Flatten a validated report into a reproducible zero-shot answer string."""
    if report is None:
        return LexGLUEAnswer("Insufficient evidence to answer the question.", (), ())
    parts = [report.overview.strip()]
    claim_ids: list[str] = []

    def visit(section) -> None:
        if section.answer_text.strip():
            parts.append(section.answer_text.strip())
        claim_ids.extend(section.claim_refs)
        for child in section.child_sections:
            visit(child)

    for section in report.sections:
        visit(section)
    return LexGLUEAnswer(
        "\n\n".join(part for part in parts if part),
        tuple(dict.fromkeys(claim_ids)),
        tuple(report.contradiction_refs),
    )
