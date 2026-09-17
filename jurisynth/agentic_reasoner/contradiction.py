"""Auxiliary, evidence-linked contradiction warnings for compiled claims.

The pilot deliberately flags only explicit potential conflicts.  A calibrated
CrossEncoder can replace the scorer without changing workflow/report contracts.
"""

from __future__ import annotations

import re
import asyncio
import time
from dataclasses import dataclass, field
from itertools import combinations
from typing import Callable, Literal, Protocol

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
    scorer_model: str = ""
    # These fields make a detector flag independently traceable.  They are
    # copied from the evidence-linked candidate rather than generated later.
    claim_a_text: str = ""
    claim_a_evidence_refs: tuple[str, ...] = ()
    claim_b_text: str = ""
    claim_b_evidence_refs: tuple[str, ...] = ()


class ContradictionScorer(Protocol):
    """Score candidate claim pairs without making a legal adjudication."""

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
    """CPU-only batched NLI CrossEncoder scorer.

    The model card's label order is contradiction, entailment, neutral.  We use
    the normalized contradiction probability, never the argmax label alone, so
    the detector threshold remains auditable and calibration-friendly.
    """

    model_name: str = "cross-encoder/nli-deberta-v3-base"
    device: str = "cpu"
    batch_size: int = 16
    max_length: int = 512
    local_files_only: bool = True
    _model: object | None = None
    model_loader: Callable[..., object] | None = None
    load_count: int = field(default=0, init=False)
    last_metrics: dict[str, float | int] = field(default_factory=dict, init=False)
    name: str = "nli_cross_encoder"

    # Verified against the model card/configuration used by this project.
    LABELS: tuple[str, str, str] = ("contradiction", "entailment", "neutral")

    def score(self, candidates: list[ContradictionCandidate]) -> list[float]:
        if not candidates:
            self.last_metrics = {"pair_count": 0, "model_load_seconds": 0.0, "tokenization_seconds": 0.0, "forward_seconds": 0.0, "total_seconds": 0.0, "batch_size": self.batch_size}
            return []
        if self.batch_size < 1:
            raise ValueError("NLI batch_size must be positive")
        total_started = time.perf_counter()
        model_load_started = time.perf_counter()
        encoder = self._load_model()
        model_load_seconds = time.perf_counter() - model_load_started
        pairs = [(candidate.claim_a_text, candidate.claim_b_text) for candidate in candidates]
        raw, tokenization_seconds, forward_seconds = self._batched_logits(encoder, pairs)
        if raw.ndim != 2 or raw.shape != (len(candidates), len(self.LABELS)):
            raise ValueError("NLI CrossEncoder must return three logits per candidate pair")
        probabilities = _softmax(raw)
        self.last_metrics = {
            "pair_count": len(candidates),
            "model_load_seconds": round(model_load_seconds, 6),
            "pair_construction_seconds": 0.0,
            "tokenization_seconds": round(tokenization_seconds, 6),
            "forward_seconds": round(forward_seconds, 6),
            "total_seconds": round(time.perf_counter() - total_started, 6),
            "batch_size": self.batch_size,
            "max_length": self.max_length,
        }
        return [float(value) for value in probabilities[:, 0]]

    def _batched_logits(self, encoder: object, pairs: list[tuple[str, str]]) -> tuple[np.ndarray, float, float]:
        """Tokenize and score one bounded CPU batch at a time.

        The narrow ``predict`` fallback exists only for lightweight test doubles;
        the production CrossEncoder path always uses tokenizer/model batches
        under torch.inference_mode().
        """
        if not hasattr(encoder, "tokenizer") or not hasattr(encoder, "model"):
            return self._predict_batches(encoder, pairs)
        try:
            import torch
        except ModuleNotFoundError as exc:
            raise RuntimeError("PyTorch is required for CPU NLI contradiction scoring.") from exc
        tokenizer = encoder.tokenizer
        model = encoder.model
        model.eval()
        try:
            device = next(model.parameters()).device
        except StopIteration:
            device = torch.device(self.device)
        logits: list[np.ndarray] = []
        tokenization_seconds = 0.0
        forward_seconds = 0.0
        for start in range(0, len(pairs), self.batch_size):
            batch = pairs[start:start + self.batch_size]
            token_started = time.perf_counter()
            encoded = tokenizer(batch, padding=True, truncation=True, max_length=self.max_length, return_tensors="pt")
            encoded = {key: value.to(device) for key, value in encoded.items()}
            tokenization_seconds += time.perf_counter() - token_started
            forward_started = time.perf_counter()
            with torch.inference_mode():
                output = model(**encoded)
                batch_logits = output.logits.detach().to("cpu").float().numpy()
            forward_seconds += time.perf_counter() - forward_started
            logits.append(batch_logits)
            del encoded, output, batch_logits
        return np.concatenate(logits, axis=0), tokenization_seconds, forward_seconds

    def _predict_batches(self, encoder: object, pairs: list[tuple[str, str]]) -> tuple[np.ndarray, float, float]:
        """Test-double path; production models use ``_batched_logits`` above."""
        batches: list[np.ndarray] = []
        started = time.perf_counter()
        for start in range(0, len(pairs), self.batch_size):
            batches.append(np.asarray(encoder.predict(pairs[start:start + self.batch_size]), dtype=np.float64))
        elapsed = time.perf_counter() - started
        return np.concatenate(batches, axis=0), 0.0, elapsed

    def _load_model(self):
        if self._model is None:
            if self.model_loader is not None:
                self._model = self.model_loader(
                    self.model_name, device=self.device, max_length=self.max_length, local_files_only=self.local_files_only,
                )
            else:
                try:
                    from sentence_transformers import CrossEncoder
                except ModuleNotFoundError as exc:
                    raise RuntimeError("Install sentence-transformers to enable NLI contradiction scoring.") from exc
                self._model = CrossEncoder(
                    self.model_name,
                    device=self.device,
                    max_length=self.max_length,
                    local_files_only=self.local_files_only,
                )
            self.load_count += 1
        return self._model


@dataclass(slots=True)
class ContradictionDetector:
    """Generate unordered claim-pair candidates and emit non-blocking warnings."""

    scorer: ContradictionScorer
    threshold: float = 0.8
    min_shared_resources: int = 2
    candidate_strategy: Literal["exhaustive", "shared_resources"] = "exhaustive"
    # Operational diagnostics only; they do not affect detector semantics.
    last_candidate_count: int = field(default=0, init=False)
    last_flagged_count: int = field(default=0, init=False)

    async def detect(self, answers: list[LeafAnswer]) -> list[Contradiction]:
        if not 0.0 <= self.threshold <= 1.0:
            raise ValueError("contradiction threshold must be between 0 and 1")
        candidates = self.candidates(answers)
        self.last_candidate_count = len(candidates)
        scores = await asyncio.to_thread(self.scorer.score, candidates)
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
                    "resources and contain potentially incompatible statements. This is a warning, not a legal adjudication."
                ),
                shared_resources=candidate.shared_resources,
                scorer=scorer_name,
                scorer_model=str(getattr(self.scorer, "model_name", "")),
                claim_a_text=candidate.claim_a_text,
                claim_a_evidence_refs=candidate.claim_a_evidence_refs,
                claim_b_text=candidate.claim_b_text,
                claim_b_evidence_refs=candidate.claim_b_evidence_refs,
            ))
        self.last_flagged_count = len(conflicts)
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
            if self.candidate_strategy == "shared_resources" and len(shared) < self.min_shared_resources:
                continue
            candidate = ContradictionCandidate(
                claim_a.claim_id or "",
                claim_a.text,
                tuple(claim_a.evidence_refs),
                claim_b.claim_id or "",
                claim_b.text,
                tuple(claim_b.evidence_refs),
                shared,
            )
            candidates.append(candidate)
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
