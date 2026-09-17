"""Minimal Claim-referencing final-report synthesis for the Reasoner MVP."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from jurisynth.agentic_reasoner.llm import ChatModel
from jurisynth.agentic_reasoner.schemas import REPORT_SCHEMA
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
    potential_contradictions: list["PotentialContradiction"] = field(default_factory=list)


@dataclass(slots=True)
class PotentialContradiction:
    """A non-adjudicative, claim- and provenance-linked detector flag."""

    contradiction_id: str
    score: float
    scorer: str
    scorer_model: str
    explanation: str
    claim_a_id: str
    claim_a_text: str
    claim_a_evidence_refs: list[str]
    claim_b_id: str
    claim_b_text: str
    claim_b_evidence_refs: list[str]
    shared_resources: list[str]


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
    potential_contradictions = [
        {
            "contradiction_id": item.contradiction_id,
            "score": item.score,
            "scorer": item.scorer,
            "scorer_model": item.scorer_model,
            "explanation": item.explanation,
            "claim_a": _contradiction_claim_payload(item.claim_a_id, item.claim_a_text, item.claim_a_evidence_refs, claims),
            "claim_b": _contradiction_claim_payload(item.claim_b_id, item.claim_b_text, item.claim_b_evidence_refs, claims),
            "shared_resources": list(item.shared_resources),
            "non_adjudicative": True,
        }
        for item in report.potential_contradictions
    ]
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
        "potential_contradictions_heading": "Potential Contradictions Identified" if potential_contradictions else None,
        "potential_contradictions": potential_contradictions,
        # Images remain explicitly separate from claim evidence: visual
        # descriptions may help a reader inspect a form or diagram, but never
        # independently establish a legal proposition.
        "auxiliary_images": [
            _image_payload(image)
            for answer in answers
            for image in answer.evidence_bundle.image_evidence
        ],
    }


def _contradiction_claim_payload(
    claim_id: str,
    claim_text: str,
    evidence_refs: list[str],
    claims: dict[str, dict[str, object]],
) -> dict[str, object]:
    """Resolve a flag through the existing claim/evidence tree when possible."""
    resolved = claims.get(claim_id)
    if resolved is not None:
        return resolved
    # A report must never create untraceable free-floating contradiction text.
    # This guarded fallback is retained only for backwards-compatible callers.
    return {"claim_id": claim_id, "text": claim_text, "evidence_refs": list(evidence_refs), "evidence": []}


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


def _image_payload(image: object) -> dict[str, object]:
    """Expose safe visual metadata, never an internal filesystem path."""
    return {
        "image_id": image.image_id,
        "document_id": image.document_id,
        "description": image.description,
        "expanded_description": image.expanded_description,
        "visual_findings": list(image.visual_findings),
        "similarity": image.similarity,
        "expansion_relevance": image.expansion_relevance,
        "source_url": image.source_url,
        "alt": image.alt,
        "auxiliary_only": True,
    }


@dataclass(slots=True)
class FinalReportSynthesizer:
    model: ChatModel
    max_tokens: int = 1400

    async def synthesize(self, original_query: str, answers: list[LeafAnswer], *, contradictions: list[object] | None = None, structural_guidance: list[dict[str, object]] | None = None) -> FinalReport:
        claim_ids = {claim.claim_id for answer in answers for claim in answer.claims if claim.claim_id}
        contradictions = contradictions or []
        # Heuristic flags are available to diagnostic callers, but only NLI
        # scores are allowed into a user-facing potential-conflict section.
        reportable_contradictions = [
            item for item in contradictions
            if getattr(item, "scorer", "") == "nli_cross_encoder"
        ]
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
                for item in reportable_contradictions
            ],
            "structural_guidance": structural_guidance or [],
        }
        response = await self.model.complete(system=_REPORT_SYSTEM_PROMPT, user=json.dumps(payload), max_tokens=self.max_tokens, response_schema=REPORT_SCHEMA)
        report = _parse_report(response, claim_ids, contradiction_ids)
        report.potential_contradictions = _validated_potential_contradictions(reportable_contradictions, answers, claim_ids)
        return report


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


def _validated_potential_contradictions(
    contradictions: list[object],
    answers: list[LeafAnswer],
    valid_claim_ids: set[str],
) -> list[PotentialContradiction]:
    """Attach valid detector flags deterministically; the report model cannot drop them."""
    claims = {
        claim.claim_id: claim
        for answer in answers
        for claim in answer.claims
        if claim.claim_id
    }
    flags: list[PotentialContradiction] = []
    seen_pairs: set[tuple[str, str]] = set()
    for item in contradictions:
        claim_a_id = getattr(item, "claim_a_id", "")
        claim_b_id = getattr(item, "claim_b_id", "")
        pair = tuple(sorted((claim_a_id, claim_b_id)))
        if not claim_a_id or not claim_b_id or claim_a_id not in valid_claim_ids or claim_b_id not in valid_claim_ids or pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        claim_a = claims[claim_a_id]
        claim_b = claims[claim_b_id]
        flags.append(PotentialContradiction(
            contradiction_id=str(getattr(item, "contradiction_id", "")),
            score=float(getattr(item, "score", 0.0)),
            scorer=str(getattr(item, "scorer", "unknown")),
            scorer_model=str(getattr(item, "scorer_model", "")),
            explanation=str(getattr(item, "explanation", "Potential contradiction flag.")),
            claim_a_id=claim_a_id,
            claim_a_text=claim_a.text,
            claim_a_evidence_refs=list(claim_a.evidence_refs),
            claim_b_id=claim_b_id,
            claim_b_text=claim_b.text,
            claim_b_evidence_refs=list(claim_b.evidence_refs),
            shared_resources=list(getattr(item, "shared_resources", ())),
        ))
    return flags


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
