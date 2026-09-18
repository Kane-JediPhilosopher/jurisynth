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
    """A non-adjudicative, assertion- and provenance-linked detector flag."""

    contradiction_id: str
    score: float
    scorer: str
    scorer_model: str
    explanation: str
    assertion_a_id: str
    assertion_a_text: str
    assertion_a_evidence_refs: list[str]
    assertion_a_leaf_ids: list[str]
    assertion_a_provenance: list[dict[str, object]]
    assertion_b_id: str
    assertion_b_text: str
    assertion_b_evidence_refs: list[str]
    assertion_b_leaf_ids: list[str]
    assertion_b_provenance: list[dict[str, object]]


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
            "assertion_a": _contradiction_assertion_payload(item, "a"),
            "assertion_b": _contradiction_assertion_payload(item, "b"),
            "classification": "machine-flagged potentially contradictory retrieved evidence assertions",
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


def _contradiction_assertion_payload(item: PotentialContradiction, side: str) -> dict[str, object]:
    return {
        "assertion_id": getattr(item, f"assertion_{side}_id"),
        "text": getattr(item, f"assertion_{side}_text"),
        "evidence_refs": list(getattr(item, f"assertion_{side}_evidence_refs")),
        "leaf_ids": list(getattr(item, f"assertion_{side}_leaf_ids")),
        "provenance": list(getattr(item, f"assertion_{side}_provenance")),
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
        # Contradiction flags are attached deterministically after synthesis.
        # The report model does not adjudicate or silently discard them.
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
            "structural_guidance": structural_guidance or [],
        }
        response = await self.model.complete(system=_REPORT_SYSTEM_PROMPT, user=json.dumps(payload), max_tokens=self.max_tokens, response_schema=REPORT_SCHEMA)
        report = _parse_report(response, claim_ids, set())
        report.potential_contradictions = _validated_potential_contradictions(reportable_contradictions, answers)
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
) -> list[PotentialContradiction]:
    """Attach valid detector flags deterministically; the report model cannot drop them."""
    valid_evidence_ids = {
        item.evidence_id
        for answer in answers
        for item in answer.evidence_bundle.evidence_items
    }
    flags: list[PotentialContradiction] = []
    seen_pairs: set[tuple[str, str]] = set()
    for item in contradictions:
        assertion_a_id = getattr(item, "assertion_a_id", "")
        assertion_b_id = getattr(item, "assertion_b_id", "")
        refs_a = tuple(getattr(item, "assertion_a_evidence_refs", ()))
        refs_b = tuple(getattr(item, "assertion_b_evidence_refs", ()))
        pair = tuple(sorted((assertion_a_id, assertion_b_id)))
        if (
            not assertion_a_id or not assertion_b_id or pair in seen_pairs
            or not refs_a or not refs_b
            or not set(refs_a).issubset(valid_evidence_ids)
            or not set(refs_b).issubset(valid_evidence_ids)
        ):
            continue
        seen_pairs.add(pair)
        flags.append(PotentialContradiction(
            contradiction_id=str(getattr(item, "contradiction_id", "")),
            score=float(getattr(item, "score", 0.0)),
            scorer=str(getattr(item, "scorer", "unknown")),
            scorer_model=str(getattr(item, "scorer_model", "")),
            explanation=str(getattr(item, "explanation", "Potential contradiction flag.")),
            assertion_a_id=assertion_a_id,
            assertion_a_text=str(getattr(item, "assertion_a_text", "")),
            assertion_a_evidence_refs=list(refs_a),
            assertion_a_leaf_ids=list(getattr(item, "assertion_a_leaf_ids", ())),
            assertion_a_provenance=[_source_record(source) for source in getattr(item, "assertion_a_provenance", ())],
            assertion_b_id=assertion_b_id,
            assertion_b_text=str(getattr(item, "assertion_b_text", "")),
            assertion_b_evidence_refs=list(refs_b),
            assertion_b_leaf_ids=list(getattr(item, "assertion_b_leaf_ids", ())),
            assertion_b_provenance=[_source_record(source) for source in getattr(item, "assertion_b_provenance", ())],
        ))
    return flags


def _source_record(source: object) -> dict[str, object]:
    return {
        "evidence_id": getattr(source, "evidence_id", ""),
        "leaf_id": getattr(source, "leaf_id", ""),
        "document_id": getattr(source, "document_id", ""),
        "chunk_id": getattr(source, "chunk_id", ""),
        "excerpt": getattr(source, "excerpt", ""),
        "similarity": getattr(source, "similarity", None),
    }


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
