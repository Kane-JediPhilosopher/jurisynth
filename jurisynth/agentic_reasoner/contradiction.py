"""CPU NLI warnings over the bounded retrieved evidence for one workflow run."""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
import time
import unicodedata
from dataclasses import dataclass, field
from itertools import combinations
from typing import Callable, Protocol

import numpy as np

from jurisynth.contracts import EvidenceBundle, EvidenceItem


@dataclass(frozen=True, slots=True)
class AssertionSource:
    """One traceable source occurrence of a retrieved assertion."""

    evidence_id: str
    leaf_id: str
    document_id: str
    chunk_id: str
    excerpt: str
    similarity: float | None = None


@dataclass(frozen=True, slots=True)
class RetrievedAssertion:
    """A semantic assertion deduplicated across leaf-local evidence bundles."""

    assertion_id: str
    subject: str
    predicate: str
    object: str
    text: str
    evidence_refs: tuple[str, ...]
    leaf_ids: tuple[str, ...]
    provenance: tuple[AssertionSource, ...]
    modifiers: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ContradictionCandidate:
    assertion_a: RetrievedAssertion
    assertion_b: RetrievedAssertion


@dataclass(frozen=True, slots=True)
class Contradiction:
    contradiction_id: str
    assertion_a_id: str
    assertion_b_id: str
    score: float
    explanation: str
    scorer: str
    scorer_model: str = ""
    assertion_a_text: str = ""
    assertion_a_evidence_refs: tuple[str, ...] = ()
    assertion_a_leaf_ids: tuple[str, ...] = ()
    assertion_a_provenance: tuple[AssertionSource, ...] = ()
    assertion_b_text: str = ""
    assertion_b_evidence_refs: tuple[str, ...] = ()
    assertion_b_leaf_ids: tuple[str, ...] = ()
    assertion_b_provenance: tuple[AssertionSource, ...] = ()


class ContradictionScorer(Protocol):
    """Score assertion pairs without making a legal adjudication."""

    def score(self, candidates: list[ContradictionCandidate]) -> list[float]: ...


@dataclass(slots=True)
class ExplicitNegationScorer:
    """Diagnostic-only heuristic; never a production/user-facing scorer."""

    name: str = "explicit_negation_heuristic"

    def score(self, candidates: list[ContradictionCandidate]) -> list[float]:
        return [self._score(candidate) for candidate in candidates]

    @staticmethod
    def _score(candidate: ContradictionCandidate) -> float:
        tokens_a = _tokens(candidate.assertion_a.text)
        tokens_b = _tokens(candidate.assertion_b.text)
        negated_a = bool(tokens_a & _NEGATION_TERMS)
        negated_b = bool(tokens_b & _NEGATION_TERMS)
        shared_terms = (tokens_a & tokens_b) - _NEGATION_TERMS
        return 0.95 if negated_a != negated_b and len(shared_terms) >= 2 else 0.0


@dataclass(slots=True)
class NLIContradictionScorer:
    """CPU-only, cached, batched NLI CrossEncoder scorer."""

    model_name: str = "cross-encoder/nli-deberta-v3-base"
    device: str = "cpu"
    batch_size: int = 32
    max_length: int = 512
    local_files_only: bool = True
    _model: object | None = None
    model_loader: Callable[..., object] | None = None
    load_count: int = field(default=0, init=False)
    last_metrics: dict[str, float | int | None] = field(default_factory=dict, init=False)
    name: str = "nli_cross_encoder"

    LABELS: tuple[str, str, str] = ("contradiction", "entailment", "neutral")

    def score(self, candidates: list[ContradictionCandidate]) -> list[float]:
        if not candidates:
            self.last_metrics = {
                "pair_count": 0, "model_load_seconds": 0.0,
                "tokenization_seconds": 0.0, "forward_seconds": 0.0,
                "total_seconds": 0.0, "batch_size": self.batch_size,
                "peak_rss_bytes": _rss_bytes(),
            }
            return []
        if self.batch_size < 1:
            raise ValueError("NLI batch_size must be positive")
        total_started = time.perf_counter()
        model_load_started = time.perf_counter()
        encoder = self._load_model()
        model_load_seconds = time.perf_counter() - model_load_started
        pair_started = time.perf_counter()
        pairs = [(candidate.assertion_a.text, candidate.assertion_b.text) for candidate in candidates]
        pair_construction_seconds = time.perf_counter() - pair_started
        raw, tokenization_seconds, forward_seconds, peak_rss_bytes = self._batched_logits(encoder, pairs)
        if raw.ndim != 2 or raw.shape != (len(candidates), len(self.LABELS)):
            raise ValueError("NLI CrossEncoder must return three logits per candidate pair")
        probabilities = _softmax(raw)
        total_seconds = time.perf_counter() - total_started
        self.last_metrics = {
            "pair_count": len(candidates),
            "model_load_seconds": round(model_load_seconds, 6),
            "pair_construction_seconds": round(pair_construction_seconds, 6),
            "tokenization_seconds": round(tokenization_seconds, 6),
            "forward_seconds": round(forward_seconds, 6),
            "total_seconds": round(total_seconds, 6),
            "pairs_per_second": round(len(candidates) / total_seconds, 6) if total_seconds else None,
            "batch_size": self.batch_size,
            "max_length": self.max_length,
            "peak_rss_bytes": peak_rss_bytes,
        }
        return [float(value) for value in probabilities[:, 0]]

    def _batched_logits(
        self, encoder: object, pairs: list[tuple[str, str]],
    ) -> tuple[np.ndarray, float, float, int | None]:
        if not hasattr(encoder, "tokenizer") or not hasattr(encoder, "model"):
            raw, tokenization_seconds, forward_seconds = self._predict_batches(encoder, pairs)
            return raw, tokenization_seconds, forward_seconds, _rss_bytes()
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
        peak_rss_bytes = _rss_bytes()
        for start in range(0, len(pairs), self.batch_size):
            batch = pairs[start:start + self.batch_size]
            token_started = time.perf_counter()
            encoded = tokenizer(
                batch, padding=True, truncation=True,
                max_length=self.max_length, return_tensors="pt",
            )
            encoded = {key: value.to(device) for key, value in encoded.items()}
            tokenization_seconds += time.perf_counter() - token_started
            forward_started = time.perf_counter()
            with torch.inference_mode():
                output = model(**encoded)
                batch_logits = output.logits.detach().to("cpu").float().numpy()
            forward_seconds += time.perf_counter() - forward_started
            logits.append(batch_logits)
            peak_rss_bytes = _max_optional(peak_rss_bytes, _rss_bytes())
            del encoded, output, batch_logits
        return np.concatenate(logits, axis=0), tokenization_seconds, forward_seconds, peak_rss_bytes

    def _predict_batches(self, encoder: object, pairs: list[tuple[str, str]]) -> tuple[np.ndarray, float, float]:
        batches: list[np.ndarray] = []
        started = time.perf_counter()
        for start in range(0, len(pairs), self.batch_size):
            batches.append(np.asarray(encoder.predict(pairs[start:start + self.batch_size]), dtype=np.float64))
        return np.concatenate(batches, axis=0), 0.0, time.perf_counter() - started

    def _load_model(self):
        if self._model is None:
            if self.model_loader is not None:
                self._model = self.model_loader(
                    self.model_name, device=self.device, max_length=self.max_length,
                    local_files_only=self.local_files_only,
                )
            else:
                try:
                    from sentence_transformers import CrossEncoder
                except ModuleNotFoundError as exc:
                    raise RuntimeError("Install sentence-transformers to enable NLI contradiction scoring.") from exc
                self._model = CrossEncoder(
                    self.model_name, device=self.device,
                    max_length=self.max_length, local_files_only=self.local_files_only,
                )
            self.load_count += 1
        return self._model


@dataclass(slots=True)
class ContradictionDetector:
    """Score all unique assertion pairs in supplied leaf EvidenceBundles only."""

    scorer: ContradictionScorer
    threshold: float = 0.95
    last_raw_assertion_count: int = field(default=0, init=False)
    last_unique_assertion_count: int = field(default=0, init=False)
    last_candidate_count: int = field(default=0, init=False)
    last_flagged_count: int = field(default=0, init=False)
    last_metrics: dict[str, object] = field(default_factory=dict, init=False)

    async def detect(self, bundles: list[EvidenceBundle]) -> list[Contradiction]:
        if not 0.0 <= self.threshold <= 1.0:
            raise ValueError("contradiction threshold must be between 0 and 1")
        started = time.perf_counter()
        assertions = self.collect_assertions(bundles)
        candidates = self.candidates(assertions)
        self.last_candidate_count = len(candidates)
        scores = await asyncio.to_thread(self.scorer.score, candidates) if candidates else []
        if len(scores) != len(candidates):
            raise ValueError("contradiction scorer returned an inconsistent number of scores")
        conflicts: list[Contradiction] = []
        scorer_name = getattr(self.scorer, "name", type(self.scorer).__name__)
        for index, (candidate, score) in enumerate(zip(candidates, scores), start=1):
            if not 0.0 <= score <= 1.0:
                raise ValueError("contradiction scores must be between 0 and 1")
            if score < self.threshold:
                continue
            a, b = candidate.assertion_a, candidate.assertion_b
            conflicts.append(Contradiction(
                contradiction_id=f"X{index:06d}",
                assertion_a_id=a.assertion_id,
                assertion_b_id=b.assertion_id,
                score=score,
                explanation=(
                    "Machine-flagged potentially contradictory retrieved evidence assertions. "
                    "This is a semantic warning, not a legal adjudication."
                ),
                scorer=scorer_name,
                scorer_model=str(getattr(self.scorer, "model_name", "")),
                assertion_a_text=a.text,
                assertion_a_evidence_refs=a.evidence_refs,
                assertion_a_leaf_ids=a.leaf_ids,
                assertion_a_provenance=a.provenance,
                assertion_b_text=b.text,
                assertion_b_evidence_refs=b.evidence_refs,
                assertion_b_leaf_ids=b.leaf_ids,
                assertion_b_provenance=b.provenance,
            ))
        self.last_flagged_count = len(conflicts)
        self.last_metrics = {
            "raw_retrieved_assertion_count": self.last_raw_assertion_count,
            "unique_assertion_count": self.last_unique_assertion_count,
            "pair_count": self.last_candidate_count,
            "threshold_positive_pair_count": self.last_flagged_count,
            "total_stage_seconds": round(time.perf_counter() - started, 6),
            "scorer": scorer_name,
            "scorer_model": str(getattr(self.scorer, "model_name", "")),
            "scorer_metrics": dict(getattr(self.scorer, "last_metrics", {})),
        }
        return conflicts

    def collect_assertions(self, bundles: list[EvidenceBundle]) -> list[RetrievedAssertion]:
        """Normalize/deduplicate bounded retrieved assertions and merge provenance."""
        self.last_raw_assertion_count = sum(len(bundle.evidence_items) for bundle in bundles)
        grouped: dict[tuple[str, str, str, tuple[str, ...]], list[tuple[str, EvidenceItem]]] = {}
        for bundle in bundles:
            for item in bundle.evidence_items:
                modifiers = tuple(sorted(_canonical_json(value) for value in item.modifiers))
                key = (
                    _normalize_field(item.assertion.subject),
                    _normalize_field(item.assertion.predicate),
                    _normalize_field(item.assertion.object),
                    modifiers,
                )
                grouped.setdefault(key, []).append((bundle.query_id, item))

        assertions: list[RetrievedAssertion] = []
        for key in sorted(grouped):
            subject, predicate, object_, modifiers = key
            occurrences = grouped[key]
            assertion_id = "A_" + hashlib.sha256(
                _canonical_json([subject, predicate, object_, list(modifiers)]).encode("utf-8")
            ).hexdigest()[:16]
            sources = {
                (item.evidence_id, leaf_id, source.document_id, source.chunk_id, source.text, source.similarity): AssertionSource(
                    item.evidence_id, leaf_id, source.document_id, source.chunk_id,
                    source.text, source.similarity,
                )
                for leaf_id, item in occurrences
                for source in item.source_chunks
            }
            assertions.append(RetrievedAssertion(
                assertion_id=assertion_id,
                subject=subject,
                predicate=predicate,
                object=object_,
                text=_render_assertion(subject, predicate, object_, modifiers),
                evidence_refs=tuple(sorted({item.evidence_id for _, item in occurrences})),
                leaf_ids=tuple(sorted({leaf_id for leaf_id, _ in occurrences})),
                provenance=tuple(sources[value] for value in sorted(sources, key=lambda value: tuple(str(part) for part in value))),
                modifiers=modifiers,
            ))
        self.last_unique_assertion_count = len(assertions)
        return assertions

    @staticmethod
    def candidates(assertions: list[RetrievedAssertion]) -> list[ContradictionCandidate]:
        return [ContradictionCandidate(a, b) for a, b in combinations(assertions, 2)]


def _render_assertion(subject: str, predicate: str, object_: str, modifiers: tuple[str, ...]) -> str:
    text = f"{subject} {predicate} {object_}"
    return f"{text} [qualifiers: {'; '.join(modifiers)}]" if modifiers else text


def _normalize_field(value: str) -> str:
    # Preserve URI/string case: RDF identifiers and literal values may be case-sensitive.
    return " ".join(unicodedata.normalize("NFKC", value).split())


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _rss_bytes() -> int | None:
    try:
        import os
        import psutil
        return int(psutil.Process(os.getpid()).memory_info().rss)
    except (ImportError, OSError):
        return None


def _max_optional(left: int | None, right: int | None) -> int | None:
    values = [value for value in (left, right) if value is not None]
    return max(values) if values else None


_NEGATION_TERMS = {"no", "not", "never", "neither", "nor", "without", "prohibited", "prohibit"}


def _tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", value.casefold()))


def _softmax(logits: np.ndarray) -> np.ndarray:
    shifted = logits - logits.max(axis=1, keepdims=True)
    exp = np.exp(shifted)
    return exp / exp.sum(axis=1, keepdims=True)
