"""Deterministic validation of LLM-produced Claim references."""

from __future__ import annotations

from jurisynth.agentic_reasoner.models import Claim, LeafAnswer


def validate_leaf_answer(answer: LeafAnswer) -> LeafAnswer:
    """Assign stable IDs and reject dangling evidence references.

    This deliberately validates references only; it never tries to infer claims
    from answer prose, preserving the architecture in the reasoner specification.
    """
    valid_ids = {item.evidence_id for item in answer.evidence_bundle.evidence_items}
    valid_ids.update(
        f"table:{item.document_id}:{item.table_id}:{row_id}"
        for item in answer.evidence_bundle.table_evidence
        for row_id in item.row_ids
    )
    for index, claim in enumerate(answer.claims, start=1):
        if not claim.text.strip():
            raise ValueError(f"Claim {index} has no text")
        dangling = sorted(set(claim.evidence_refs) - valid_ids)
        if dangling:
            raise ValueError(f"Claim {index} references unknown evidence: {dangling}")
        claim.claim_id = claim.claim_id or f"{answer.query_id}:C{index}"
    return answer
