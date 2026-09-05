"""Auxiliary, evidence-linked contradiction warnings for compiled claims.

The pilot deliberately flags only explicit potential conflicts.  A calibrated
CrossEncoder can replace the scorer without changing workflow/report contracts.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from itertools import combinations
from typing import Protocol

import numpy as np

from jurisynth.agentic_reasoner.models import Claim, LeafAnswer


@dataclass(frozen=True, slots=True)
class ContradictionCandidate:
    claim_a_id: str
    claim_a_text: str
    claim_a_evidence_refs: tuple[str, ...]
    claim_b_id: str
    claim_b_text: str
    claim_b_evidence_refs: tuple[str, ...]
    shared_resources: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Contradiction:
    contradiction_id: str
    claim_a_id: str
    claim_b_id: str
    score: float
    explanation: str
    shared_resources: tuple[str, ...]
    scorer: str


class ContradictionScorer(Protocol):
    """Replace with a calibrated CrossEncoder after model/threshold selection."""

    def score(self, candidates: list[ContradictionCandidate]) -> list[float]: ...


@dataclass(slots=True)
class ExplicitNegationScorer:
    """High-precision fallback; it is not a legal contradiction adjudicator."""

    name: str = "explicit_negation_heuristic"

    def score(self, candidates: list[ContradictionCandidate]) -> list[float]:
        return [self._score(candidate) for candidate in candidates]

    @staticmethod
    def _score(candidate: ContradictionCandidate) -> float:
        tokens_a = _tokens(candidate.claim_a_text)
        tokens_b = _tokens(candidate.claim_b_text)
        negated_a = bool(tokens_a & _NEGATION_TERMS)
        negated_b = bool(tokens_b & _NEGATION_TERMS)
        shared_terms = (tokens_a & tokens_b) - _NEGATION_TERMS
        if negated_a != negated_b and len(shared_terms) >= 2:
            return 0.95
        return 0.0


@dataclass(slots=True)
class NLIContradictionScorer:
    """Lazy NLI CrossEncoder scorer for the already-pruned local candidate pairs.

    The model card's label order is contradiction, entailment, neutral.  We use
    the normalized contradiction probability, never the argmax label alone, so
    the detector threshold remains auditable and calibration-friendly.
    """

    model_name: str = "cross-encoder/nli-deberta-v3-base"
    device: str | None = None
    _model: object | None = None
    name: str = "nli_cross_encoder"

    def score(self, candidates: list[ContradictionCandidate]) -> list[float]:
        if not candidates:
            return []
        model = self._load_model()
        pairs = [(candidate.claim_a_text, candidate.claim_b_text) for candidate in candidates]
        raw = np.asarray(model.predict(pairs), dtype=np.float64)
        if raw.ndim != 2 or raw.shape != (len(candidates), 3):
            raise ValueError("NLI CrossEncoder must return three logits per candidate pair")
        probabilities = _softmax(raw)
        return [float(value) for value in probabilities[:, 0]]

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder
            except ModuleNotFoundError as exc:
                raise RuntimeError("Install sentence-transformers to enable NLI contradiction scoring.") from exc
            kwargs = {"device": self.device} if self.device else {}
            self._model = CrossEncoder(self.model_name, **kwargs)
        return self._model


@dataclass(slots=True)
class ContradictionDetector:
    """Generate local E-R candidates and emit non-blocking conflict warnings."""

    scorer: ContradictionScorer
    threshold: float = 0.8
    min_shared_resources: int = 2

    async def detect(self, answers: list[LeafAnswer]) -> list[Contradiction]:
        if not 0.0 <= self.threshold <= 1.0:
            raise ValueError("contradiction threshold must be between 0 and 1")
        candidates = self.candidates(answers)
        scores = self.scorer.score(candidates)
        if len(scores) != len(candidates):
            raise ValueError("contradiction scorer returned an inconsistent number of scores")
        conflicts: list[Contradiction] = []
        scorer_name = getattr(self.scorer, "name", type(self.scorer).__name__)
        for index, (candidate, score) in enumerate(zip(candidates, scores), start=1):
            if not 0.0 <= score <= 1.0:
                raise ValueError("contradiction scores must be between 0 and 1")
            if score < self.threshold:
                continue
            conflicts.append(Contradiction(
                contradiction_id=f"X{index:03d}",
                claim_a_id=candidate.claim_a_id,
                claim_b_id=candidate.claim_b_id,
                score=score,
                explanation=(
                    "Potential conflict: the evidence-linked claims concern the same "
                    "resources and use opposing explicit polarity. This is a warning, not a legal adjudication."
                ),
                shared_resources=candidate.shared_resources,
                scorer=scorer_name,
            ))
        return conflicts

    def candidates(self, answers: list[LeafAnswer]) -> list[ContradictionCandidate]:
        claims = [
            (claim, _claim_resources(answer, claim))
            for answer in answers
            for claim in answer.claims
            if claim.claim_id
        ]
        candidates: list[ContradictionCandidate] = []
        for (claim_a, resources_a), (claim_b, resources_b) in combinations(claims, 2):
            shared = tuple(sorted(resources_a & resources_b))
            if len(shared) < self.min_shared_resources:
                continue
            candidates.append(ContradictionCandidate(
                claim_a.claim_id or "",
                claim_a.text,
                tuple(claim_a.evidence_refs),
                claim_b.claim_id or "",
                claim_b.text,
                tuple(claim_b.evidence_refs),
                shared,
            ))
        return candidates


def _claim_resources(answer: LeafAnswer, claim: Claim) -> set[str]:
    evidence_by_id = {item.evidence_id: item for item in answer.evidence_bundle.evidence_items}
    return {
        value
        for reference in claim.evidence_refs
        for item in [evidence_by_id.get(reference)]
        if item is not None
        for value in (item.assertion.subject, item.assertion.predicate, item.assertion.object)
    }


_NEGATION_TERMS = {"no", "not", "never", "neither", "nor", "without", "prohibited", "prohibit"}


def _tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", value.casefold()))


def _softmax(logits: np.ndarray) -> np.ndarray:
    shifted = logits - logits.max(axis=1, keepdims=True)
    exp = np.exp(shifted)
    return exp / exp.sum(axis=1, keepdims=True)
