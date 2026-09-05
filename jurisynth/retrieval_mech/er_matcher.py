"""Query-time matching over persisted entity and relation FAISS indices."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import numpy as np

try:
    import faiss
except ModuleNotFoundError:
    faiss = None

from jurisynth.retrieval_mech.er_index_builder import ResourceRecord


class Embedder(Protocol):
    def encode(self, texts: list[str], *, normalize_embeddings: bool = True, **kwargs: object) -> object: ...


@dataclass(frozen=True, slots=True)
class Concept:
    concept_id: str
    text: str
    variants: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ERMatch:
    concept_id: str
    input_term: str
    uri: str
    label: str
    similarity: float
    community_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ERMatchResult:
    entity_matches: tuple[ERMatch, ...]
    relation_matches: tuple[ERMatch, ...]


@dataclass(slots=True)
class PersistedERIndices:
    entity_index: Any
    relation_index: Any
    entity_records: list[ResourceRecord]
    relation_records: list[ResourceRecord]

    @classmethod
    def load(cls, directory: str | Path) -> "PersistedERIndices":
        if faiss is None:
            raise RuntimeError("FAISS is required to load persisted E-R indices.")
        directory = Path(directory)
        metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
        entities = [ResourceRecord(**record) for record in metadata["entities"]]
        relations = [ResourceRecord(**record) for record in metadata["relations"]]
        return cls(
            faiss.read_index(str(directory / "entity.index")) if entities else None,
            faiss.read_index(str(directory / "relation.index")) if relations else None,
            entities,
            relations,
        )


class ERMatcher:
    """Return scored candidates grouped by their originating input concept."""

    def __init__(self, indices: PersistedERIndices, embedder: Embedder) -> None:
        self.indices = indices
        self.embedder = embedder

    def match(
        self,
        entity_concepts: list[Concept],
        relation_concepts: list[Concept],
        *,
        entity_top_k: int = 5,
        relation_top_k: int = 5,
        minimum_similarity: float | None = None,
        exact_label_priority: bool = True,
    ) -> ERMatchResult:
        return ERMatchResult(
            entity_matches=tuple(self._match(entity_concepts, self.indices.entity_index, self.indices.entity_records, entity_top_k, minimum_similarity, exact_label_priority)),
            relation_matches=tuple(self._match(relation_concepts, self.indices.relation_index, self.indices.relation_records, relation_top_k, minimum_similarity, exact_label_priority)),
        )

    def _match(
        self,
        concepts: list[Concept],
        index: Any,
        records: list[ResourceRecord],
        top_k: int,
        minimum_similarity: float | None,
        exact_label_priority: bool,
    ) -> list[ERMatch]:
        if index is None or not concepts or top_k < 1:
            return []
        matches: list[ERMatch] = []
        for concept in concepts:
            terms = (concept.text, *concept.variants)
            exact_matches = self._exact_label_matches(concept, terms, records) if exact_label_priority else []
            if exact_matches:
                matches.extend(exact_matches)
                continue
            vectors = np.asarray(self.embedder.encode(list(terms), normalize_embeddings=True), dtype=np.float32)
            if vectors.ndim != 2 or vectors.shape[0] != len(terms):
                raise ValueError("embedder returned vectors inconsistent with E-R matcher input")
            scores, ids = index.search(vectors, min(top_k, index.ntotal))
            best_per_uri: dict[str, ERMatch] = {}
            for term, term_scores, term_ids in zip(terms, scores, ids):
                for score, vector_id in zip(term_scores, term_ids):
                    if vector_id < 0:
                        continue
                    if minimum_similarity is not None and score < minimum_similarity:
                        continue
                    record = records[int(vector_id)]
                    match = ERMatch(concept.concept_id, term, record.uri, record.label, float(score), record.community_ids)
                    previous = best_per_uri.get(record.uri)
                    if previous is None or match.similarity > previous.similarity:
                        best_per_uri[record.uri] = match
            matches.extend(sorted(best_per_uri.values(), key=lambda item: (-item.similarity, item.uri)))
        return matches

    @staticmethod
    def _exact_label_matches(concept: Concept, terms: tuple[str, ...], records: list[ResourceRecord]) -> list[ERMatch]:
        """Prefer an unambiguous normalized label match over approximate vector neighbours.

        FAISS similarity is semantic and can make country/entity neighbours look
        interchangeable.  A normalized label equality is a stronger grounding
        signal; it is deliberately not inferred from a floating-point score of
        1.0, which is neither stable nor a reliable indicator of lexical identity.
        """
        normalized_terms = {_normalize_label(term): term for term in terms if _normalize_label(term)}
        matches = [
            ERMatch(concept.concept_id, normalized_terms[_normalize_label(record.label)], record.uri, record.label, 1.0, record.community_ids)
            for record in records
            if _normalize_label(record.label) in normalized_terms
        ]
        return sorted(matches, key=lambda item: item.uri)


def _normalize_label(value: str) -> str:
    """Normalize superficial punctuation/spacing without conflating lexical variants."""
    return " ".join(value.replace("_", " ").casefold().split())
