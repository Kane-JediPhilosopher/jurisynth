"""Minimal Claim-referencing final-report synthesis for the Reasoner MVP."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from jurisynth.agentic_reasoner.llm import ChatModel
from jurisynth.agentic_reasoner.models import LeafAnswer
from jurisynth.contracts import EvidenceItem, SourceChunk


@dataclass(slots=True)
class ReportSection:
    section_id: str
    title: str
    answer_text: str
    claim_refs: list[str]
    child_sections: list["ReportSection"] = field(default_factory=list)


@dataclass(slots=True)
class FinalReport:
    overview: str
    sections: list[ReportSection]
    contradiction_refs: list[str]


def progressive_disclosure_payload(report: FinalReport, answers: list[LeafAnswer]) -> dict[str, object]:
    """Return a UI-ready report → claim → evidence → source tree."""
    claims = {
        claim.claim_id: {
            "claim_id": claim.claim_id,
            "text": claim.text,
            "status": claim.status,
            "evidence": [
                _evidence_payload(item)
                for item in answer.evidence_bundle.evidence_items
                if item.evidence_id in claim.evidence_refs
            ],
        }
        for answer in answers
        for claim in answer.claims
        if claim.claim_id
    }
    return {
        "overview": report.overview,
        "sections": [
            {
                "section_id": section.section_id,
                "title": section.title,
                "answer_text": section.answer_text,
                "claims": [claims[claim_id] for claim_id in section.claim_refs],
                "child_sections": [_section_payload(child, claims) for child in section.child_sections],
            }
            for section in report.sections
        ],
        "contradiction_refs": list(report.contradiction_refs),
    }


def _section_payload(section: ReportSection, claims: dict[str, dict[str, object]]) -> dict[str, object]:
    return {
        "section_id": section.section_id,
        "title": section.title,
        "answer_text": section.answer_text,
        "claims": [claims[claim_id] for claim_id in section.claim_refs],
        "child_sections": [_section_payload(child, claims) for child in section.child_sections],
    }


def _evidence_payload(item: EvidenceItem) -> dict[str, object]:
    return {
        "evidence_id": item.evidence_id,
        "assertion": {
            "subject": item.assertion.subject,
            "predicate": item.assertion.predicate,
            "object": item.assertion.object,
        },
        "sources": [_source_payload(source) for source in item.source_chunks],
        "retrieval_origins": list(item.retrieval_origins),
        "community_ids": list(item.community_ids),
    }


def _source_payload(source: SourceChunk) -> dict[str, object]:
    return {
        "chunk_id": source.chunk_id,
        "document_id": source.document_id,
        "excerpt": source.text,
        "similarity": source.similarity,
    }


@dataclass(slots=True)
class FinalReportSynthesizer:
    model: ChatModel
    max_tokens: int = 1400

    async def synthesize(self, original_query: str, answers: list[LeafAnswer], *, contradictions: list[object] | None = None, structural_guidance: list[dict[str, object]] | None = None) -> FinalReport:
        claim_ids = {claim.claim_id for answer in answers for claim in answer.claims if claim.claim_id}
        contradictions = contradictions or []
        contradiction_ids = {item.contradiction_id for item in contradictions}
        payload = {
            "original_query": original_query,
            "leaf_answers": [
                {
                    "query_id": answer.query_id,
                    "status": answer.status,
                    "answer_text": answer.answer_text,
                    "claims": [{"claim_id": claim.claim_id, "text": claim.text, "status": claim.status} for claim in answer.claims],
                }
                for answer in answers
            ],
            "potential_contradictions": [
                {
                    "contradiction_id": item.contradiction_id,
                    "claim_a_id": item.claim_a_id,
                    "claim_b_id": item.claim_b_id,
                    "score": item.score,
                    "explanation": item.explanation,
                }
                for item in contradictions
            ],
            "structural_guidance": structural_guidance or [],
        }
        response = await self.model.complete(system=_REPORT_SYSTEM_PROMPT, user=json.dumps(payload), max_tokens=self.max_tokens)
        return _parse_report(response, claim_ids, contradiction_ids)


_REPORT_SYSTEM_PROMPT = """Synthesize supplied Jurisynth leaf answers into a cautious report.
Return JSON only: {"overview":"...","sections":[{"section_id":"s1","title":"...","answer_text":"...","claim_refs":["C..."],"child_sections":[]}],"contradiction_refs":[]}.
Use structural_guidance to preserve meaningful dependencies, but do not mechanically mirror its depth. Every claim reference must be an existing supplied claim ID. Do not invent legal support or contradiction IDs."""


def _parse_report(response: str, valid_claim_ids: set[str], valid_contradiction_ids: set[str] | None = None) -> FinalReport:
    try:
        payload = json.loads(response)
    except json.JSONDecodeError as exc:
        raise ValueError("Final report model response is not valid JSON.") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("overview"), str) or not isinstance(payload.get("sections"), list):
        raise ValueError("Final report model response does not match the required shape.")
    sections = [_parse_section(entry, valid_claim_ids) for entry in payload["sections"]]
    contradictions = payload.get("contradiction_refs", [])
    if not isinstance(contradictions, list) or not all(isinstance(ref, str) for ref in contradictions):
        raise ValueError("Final report contains malformed contradiction references.")
    if valid_contradiction_ids is not None and not set(contradictions).issubset(valid_contradiction_ids):
        raise ValueError("Final report references an unknown contradiction ID.")
    return FinalReport(payload["overview"], sections, contradictions)


def _parse_section(entry: object, valid_claim_ids: set[str]) -> ReportSection:
    if not isinstance(entry, dict) or not all(isinstance(entry.get(key), str) for key in ("section_id", "title", "answer_text")):
        raise ValueError("Final report contains a malformed section.")
    refs = entry.get("claim_refs", [])
    if not isinstance(refs, list) or not all(isinstance(ref, str) for ref in refs) or not set(refs).issubset(valid_claim_ids):
        raise ValueError("Final report references an unknown Claim ID.")
    children = entry.get("child_sections", [])
    if not isinstance(children, list):
        raise ValueError("Final report contains malformed child sections.")
    return ReportSection(entry["section_id"], entry["title"], entry["answer_text"], refs, [_parse_section(child, valid_claim_ids) for child in children])
