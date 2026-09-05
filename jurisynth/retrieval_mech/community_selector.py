"""Deterministic, soft community ranking from E-R matcher seed candidates."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from jurisynth.retrieval_mech.er_matcher import ERMatch, ERMatchResult
from jurisynth.retrieval_mech.community_hierarchy import CommunityHierarchy


@dataclass(frozen=True, slots=True)
class CommunityCandidate:
    community_id: str
    score: float
    semantic_relevance: float
    concept_coverage: float
    structural_support: float
    dispersion_bonus: float
    supporting_concept_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CommunitySelector:
    """Rank E-R-seeded communities without using them as a retrieval hard filter."""

    top_n: int = 3
    semantic_weight: float = 0.6
    coverage_weight: float = 0.4
    novelty_weight: float = 0.10
    minimum_semantic_relevance: float = 0.50
    hierarchy: CommunityHierarchy | None = None

    def __post_init__(self) -> None:
        if self.top_n < 1:
            raise ValueError("top_n must be positive")
        if min(self.semantic_weight, self.coverage_weight, self.novelty_weight) < 0:
            raise ValueError("community weights must be non-negative")
        if self.semantic_weight + self.coverage_weight == 0:
            raise ValueError("at least one community weight must be positive")

    def select(self, matches: ERMatchResult) -> list[CommunityCandidate]:
        all_matches = (*matches.entity_matches, *matches.relation_matches)
        all_concepts = {match.concept_id for match in all_matches}
        if not all_concepts:
            return []
        scores: dict[str, dict[str, float]] = defaultdict(dict)
        for match in all_matches:
            for community_id in match.community_ids:
                previous = scores[community_id].get(match.concept_id)
                if previous is None or match.similarity > previous:
                    scores[community_id][match.concept_id] = match.similarity
        weight_total = self.semantic_weight + self.coverage_weight
        candidates = []
        for community_id, by_concept in scores.items():
            semantic = sum(by_concept.values()) / len(by_concept)
            coverage = len(by_concept) / len(all_concepts)
            score = (self.semantic_weight * semantic + self.coverage_weight * coverage) / weight_total
            if semantic >= self.minimum_semantic_relevance:
                candidates.append((community_id, score, semantic, coverage, tuple(sorted(by_concept))))
        selected: list[CommunityCandidate] = []
        while candidates and len(selected) < self.top_n:
            scored: list[CommunityCandidate] = []
            for community_id, base_score, semantic, coverage, concepts in candidates:
                novelty = self._novelty(community_id, selected)
                scored.append(CommunityCandidate(
                    community_id=community_id,
                    score=base_score + self.novelty_weight * novelty,
                    semantic_relevance=semantic,
                    concept_coverage=coverage,
                    structural_support=0.0,
                    dispersion_bonus=novelty,
                    supporting_concept_ids=concepts,
                ))
            chosen = min(scored, key=lambda item: (-item.score, item.community_id))
            selected.append(chosen)
            candidates = [item for item in candidates if item[0] != chosen.community_id]
        return selected

    def _novelty(self, community_id: str, selected: list[CommunityCandidate]) -> float:
        """Bounded MMR-like diversity after the semantic relevance gate."""
        if not selected or self.hierarchy is None or community_id not in self.hierarchy.nodes:
            return 0.0
        distances = [
            self.hierarchy.distance(community_id, item.community_id)
            for item in selected
            if item.community_id in self.hierarchy.nodes
        ]
        valid = [distance for distance in distances if distance is not None]
        if not valid:
            return 0.0
        return min(1.0, min(valid) / 4.0)
