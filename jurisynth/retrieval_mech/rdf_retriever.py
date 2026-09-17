"""Deterministic direct RDF retrieval with chunk-graph provenance."""

from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass, field
from time import perf_counter
from typing import Callable, Protocol

from rdflib import URIRef

from jurisynth.contracts import Assertion, EvidenceItem, RetrievalRequest, SourceChunk
from jurisynth.retrieval_mech.community_selector import CommunitySelector
from jurisynth.retrieval_mech.er_matcher import Concept, ERMatch, ERMatcher
from jurisynth.retrieval_mech.rdf_store import QuadStore, RDFLibQuadStore, is_iri
from jurisynth.retrieval_mech.sparql_builder import SparqlQueryBuilder


class QueryInterpreter(Protocol):
    """Replaceable internal interpretation step; production use is LLM-backed."""

    async def interpret(self, request: RetrievalRequest) -> tuple[list[Concept], list[Concept]]: ...


class LeafQueryInterpreter:
    """Safe MVP fallback until an NIM-backed Query Interpreter is configured."""

    async def interpret(self, request: RetrievalRequest) -> tuple[list[Concept], list[Concept]]:
        return [Concept("entity_1", request.leaf_query)], []


ChunkResolver = Callable[[str | URIRef], SourceChunk | None]


@dataclass(slots=True)
class StructuredRetrievalResult:
    evidence_items: list[EvidenceItem] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DirectRDFRetriever:
    dataset: object
    matcher: ERMatcher
    chunk_resolver: ChunkResolver
    interpreter: QueryInterpreter = field(default_factory=LeafQueryInterpreter)
    chunk_namespace: str = "http://jurisynth/source/chunk/"
    path_expansion_limit: int = 20
    entity_match_top_k: int = 5
    relation_match_top_k: int = 5
    minimum_match_similarity: float | None = None
    max_quads_per_seed: int | None = None
    max_evidence_items: int = 60
    allow_three_hop_escalation: bool = True
    community_selector: CommunitySelector = field(default_factory=CommunitySelector)
    sparql_builder: SparqlQueryBuilder = field(default_factory=SparqlQueryBuilder)
    quad_store: QuadStore = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Accept a bounded-store protocol while retaining RDFLib pilot inputs."""
        candidate = self.dataset
        if callable(getattr(candidate, "matching_quads", None)) and callable(getattr(candidate, "select_rows", None)):
            self.quad_store = candidate
        else:
            self.quad_store = RDFLibQuadStore(candidate)

    async def retrieve(self, request: RetrievalRequest) -> StructuredRetrievalResult:
        entity_concepts, relation_concepts = await self.interpreter.interpret(request)
        broaden = request.retrieval_config.get("escalation_stage") == "broaden_candidates"
        return await asyncio.to_thread(self._retrieve_sync, entity_concepts, relation_concepts, broaden)

    def _retrieve_sync(self, entity_concepts: list[Concept], relation_concepts: list[Concept], broaden: bool = False) -> StructuredRetrievalResult:
        timings: dict[str, float] = {}
        entity_top_k = self.entity_match_top_k + 3 if broaden else self.entity_match_top_k
        relation_top_k = self.relation_match_top_k + 3 if broaden else self.relation_match_top_k
        started = perf_counter()
        matches = self.matcher.match(
            entity_concepts,
            relation_concepts,
            entity_top_k=entity_top_k,
            relation_top_k=relation_top_k,
            minimum_similarity=self.minimum_match_similarity,
        )
        timings["er_match_ms"] = round((perf_counter() - started) * 1000, 3)
        started = perf_counter()
        selected_communities = self.community_selector.select(matches)
        orientation_communities = self.community_selector.expand_for_orientation(selected_communities)
        timings["community_selection_ms"] = round((perf_counter() - started) * 1000, 3)
        entities = {match.uri for match in matches.entity_matches}
        relations = {match.uri for match in matches.relation_matches}
        started = perf_counter()
        sparql_comparison = self._compare_direct_sparql(entities, relations) if broaden else None
        evidence: dict[tuple[str, str, str], EvidenceItem] = {}
        seed_edges: dict[str, list[tuple[str, str, str, SourceChunk]]] = {}

        for subject, predicate, obj, graph_id in self._matching_quads(entities, relations):
            source_chunk = self._resolve_chunk(graph_id)
            if source_chunk is None:
                continue
            if is_iri(subject) and is_iri(obj):
                edge = (subject, predicate, obj, source_chunk)
                if subject in entities and len(seed_edges.setdefault(subject, [])) < self.path_expansion_limit:
                    seed_edges[subject].append(edge)
                if obj in entities and len(seed_edges.setdefault(obj, [])) < self.path_expansion_limit:
                    seed_edges[obj].append(edge)
            self._add_evidence(evidence, subject, predicate, obj, source_chunk, matches, "direct", 1.0)
        timings["direct_quad_scan_ms"] = round((perf_counter() - started) * 1000, 3)

        started = perf_counter()
        path_count = self._add_bounded_paths(evidence, seed_edges, entities, matches)
        timings["two_hop_expansion_ms"] = round((perf_counter() - started) * 1000, 3)
        started = perf_counter()
        three_hop_count = self._add_three_hop_paths(evidence, seed_edges, entities, matches) if broaden and self.allow_three_hop_escalation else 0
        timings["three_hop_expansion_ms"] = round((perf_counter() - started) * 1000, 3)
        started = perf_counter()
        conjunctive_count = self._mark_conjunctive_matches(evidence, entities, relations) if broaden else 0

        selected_evidence, selection_metadata = self._select_evidence(
            evidence.values(),
            concept_count=len({match.concept_id for match in (*matches.entity_matches, *matches.relation_matches)}),
        )
        timings["evidence_selection_ms"] = round((perf_counter() - started) * 1000, 3)
        return StructuredRetrievalResult(
            evidence_items=selected_evidence,
            metadata={
                "matched_entities": [_match_metadata(match) for match in matches.entity_matches],
                "matched_relations": [_match_metadata(match) for match in matches.relation_matches],
                "bounded_path_count": path_count,
                "three_hop_path_count": three_hop_count,
                "conjunctive_match_count": conjunctive_count,
                "er_matching": matches.metadata,
                "timings_ms": timings,
                **({"sparql_comparison": sparql_comparison} if sparql_comparison is not None else {}),
                "relevant_communities": [
                    {
                        "community_id": candidate.community_id,
                        "score": candidate.score,
                        "semantic_relevance": candidate.semantic_relevance,
                        "concept_coverage": candidate.concept_coverage,
                        "structural_support": candidate.structural_support,
                        "dispersion_bonus": candidate.dispersion_bonus,
                        "supporting_concept_ids": list(candidate.supporting_concept_ids),
                    }
                    for candidate in selected_communities
                ],
                **({
                    "orientation_communities": [
                        {
                            "community_id": community_id,
                            "source": "seed" if community_id in {item.community_id for item in selected_communities} else "shared_lca",
                        }
                        for community_id in orientation_communities
                    ],
                } if orientation_communities else {}),
                **selection_metadata,
            },
            warnings=["Query interpretation is using the temporary raw-leaf fallback; configure the NIM interpreter for controlled variants."] if isinstance(self.interpreter, LeafQueryInterpreter) else [],
        )

    def _add_bounded_paths(
        self,
        evidence: dict[tuple[str, str, str], EvidenceItem],
        seed_edges: dict[str, list[tuple[str, str, str, SourceChunk]]],
        entities: set[str],
        matches,
    ) -> int:
        """Add underlying assertions from bounded two-hop paths between E-R seeds."""
        if len(entities) < 2 or not seed_edges:
            return 0
        intermediates = {
            obj if subject == start else subject
            for start, edges in seed_edges.items()
            for subject, _predicate, obj, _source in edges
            if (obj if subject == start else subject) not in entities
        }
        if not intermediates:
            return 0
        intermediate_edges: dict[str, list[tuple[str, str, str, SourceChunk]]] = {}
        for subject, predicate, obj, graph_id in self._matching_quads(intermediates, set()):
            source_chunk = self._resolve_chunk(graph_id)
            if source_chunk is None:
                continue
            if not is_iri(subject) or not is_iri(obj):
                continue
            edge = (subject, predicate, obj, source_chunk)
            if subject in intermediates and len(intermediate_edges.setdefault(subject, [])) < self.path_expansion_limit:
                intermediate_edges[subject].append(edge)
            if obj in intermediates and len(intermediate_edges.setdefault(obj, [])) < self.path_expansion_limit:
                intermediate_edges[obj].append(edge)

        path_count = 0
        seen_paths: set[tuple[tuple[str, str, str], tuple[str, str, str]]] = set()
        for start in sorted(entities):
            for first in seed_edges.get(start, []):
                first_subject, _first_predicate, first_object, _first_source = first
                intermediate = first_object if first_subject == start else first_subject
                if intermediate in entities:
                    continue
                for second in intermediate_edges.get(intermediate, []):
                    second_subject, _second_predicate, second_object, _second_source = second
                    terminal = second_object if second_subject == intermediate else second_subject
                    if terminal not in entities or terminal == start:
                        continue
                    first_key = tuple(map(str, first[:3]))
                    second_key = tuple(map(str, second[:3]))
                    path_key = tuple(sorted((first_key, second_key)))
                    if path_key in seen_paths:
                        continue
                    seen_paths.add(path_key)
                    self._add_evidence(evidence, *first, matches, "path", 0.5)
                    self._add_evidence(evidence, *second, matches, "path", 0.5)
                    path_count += 1
        return path_count

    def _add_three_hop_paths(self, evidence, seed_edges, entities, matches) -> int:
        """Escalation-only three-hop paths, bounded by the same per-seed limit."""
        if len(entities) < 2 or not seed_edges:
            return 0
        count = 0
        seen: set[tuple[str, str, str]] = set()
        for start in sorted(entities):
            for first in seed_edges.get(start, []):
                first_subject, _first_predicate, first_object, _first_source = first
                middle_one = first_object if first_subject == start else first_subject
                if middle_one in entities or not is_iri(middle_one):
                    continue
                for second_subject, second_predicate, second_object, second_graph in self._matching_quads({middle_one}, set()):
                    second_source = self._resolve_chunk(second_graph)
                    if second_source is None or not is_iri(second_subject) or not is_iri(second_object):
                        continue
                    middle_two = second_object if second_subject == middle_one else second_subject
                    if middle_two in entities:
                        continue
                    second = (second_subject, second_predicate, second_object, second_source)
                    for third_subject, third_predicate, third_object, third_graph in self._matching_quads({middle_two}, set()):
                        third_source = self._resolve_chunk(third_graph)
                        if third_source is None or not is_iri(third_subject) or not is_iri(third_object):
                            continue
                        terminal = third_object if third_subject == middle_two else third_subject
                        if terminal not in entities or terminal == start:
                            continue
                        key = tuple(sorted((str(start), str(terminal))))
                        if key in seen:
                            continue
                        seen.add(key)
                        third = (third_subject, third_predicate, third_object, third_source)
                        for edge in (first, second, third):
                            self._add_evidence(evidence, *edge, matches, "path3", 1 / 3)
                        count += 1
        return count

    @staticmethod
    def _mark_conjunctive_matches(evidence, entities: set[str], relations: set[str]) -> int:
        """Mark only direct assertions satisfying two independently matched constraints.

        This is the safe V1 conjunctive fallback: one assertion must contain an
        entity candidate and a matched predicate, or both matched endpoint entities.
        It never performs a Cartesian product of candidate sets.
        """
        count = 0
        for item in evidence.values():
            assertion = item.assertion
            endpoint_hits = sum(value in entities for value in (assertion.subject, assertion.object))
            relation_hit = assertion.predicate in relations
            if endpoint_hits >= 2 or (endpoint_hits >= 1 and relation_hit):
                if "conjunctive" not in item.retrieval_origins:
                    item.retrieval_origins.append("conjunctive")
                count += 1
        return count

    def _matching_quads(self, entities: set[str], relations: set[str]):
        """Use the backend's indexed patterns; never scan the global graph."""
        conjunctive_match = getattr(self.quad_store, "matching_subject_predicate_quads", None)
        if entities and relations and callable(conjunctive_match):
            seen: set[tuple[str, str, str, str]] = set()
            matched: list[tuple[str, str, str, str]] = []
            # Normal retrieval grounds at most five entity and five relation
            # seeds. Preserve the validated 25-pair bound during escalation.
            pairs = [
                (subject, predicate)
                for subject in sorted(entities)
                for predicate in sorted(relations)
            ][:25]
            for subject, predicate in pairs:
                for row in conjunctive_match(
                    subject, predicate, limit=self.max_quads_per_seed,
                ):
                    normalized = tuple(str(value) for value in row)
                    if normalized in seen or not normalized[3].startswith(self.chunk_namespace):
                        continue
                    seen.add(normalized)
                    matched.append(normalized)
            if matched:
                yield from matched
                return
        for subject, predicate, obj, graph_id in self.quad_store.matching_quads(
            entities, relations, max_per_seed=self.max_quads_per_seed,
        ):
            if graph_id.startswith(self.chunk_namespace):
                yield subject, predicate, obj, graph_id

    def _compare_direct_sparql(self, entities: set[str], relations: set[str]) -> dict[str, object]:
        """Compare deterministic SPARQL with indexed patterns; never alter evidence."""
        query = self.sparql_builder.direct(
            entities={str(value) for value in entities},
            relations={str(value) for value in relations},
            limit=self.max_evidence_items,
        )
        try:
            rows = self.quad_store.select_rows(query)
            sparql = {
                (subject, predicate, obj, graph_id)
                for subject, predicate, obj, graph_id in rows
                if graph_id.startswith(self.chunk_namespace)
            }
            indexed = {
                (str(subject), str(predicate), str(obj), str(graph))
                for subject, predicate, obj, graph in self._matching_quads(entities, relations)
            }
            overlap = sparql & indexed
            return {
                "query": query,
                "sparql_count": len(sparql),
                "indexed_count": len(indexed),
                "agreement": len(overlap) / len(indexed | sparql) if indexed or sparql else 1.0,
            }
        except Exception as exc:
            return {"query": query, "error": repr(exc)}

    def _resolve_chunk(self, graph_id: str) -> SourceChunk | None:
        """Bridge existing RDFLib URI-keyed pilot maps and string-keyed stores."""
        source = self.chunk_resolver(graph_id)
        if source is not None:
            return source
        return self.chunk_resolver(URIRef(graph_id))

    @staticmethod
    def _add_evidence(
        evidence: dict[tuple[str, str, str], EvidenceItem],
        subject,
        predicate,
        obj,
        source_chunk: SourceChunk,
        matches,
        origin: str,
        structural_score: float,
    ) -> None:
        key = (str(subject), str(predicate), str(obj))
        item = evidence.get(key)
        if item is None:
            all_matches = (*matches.entity_matches, *matches.relation_matches)
            matched = [match for match in all_matches if match.uri in key]
            matched_scores = [match.similarity for match in matched]
            item = EvidenceItem(
                evidence_id="E_" + hashlib.sha256("\u241f".join(key).encode()).hexdigest()[:16],
                assertion=Assertion(*key),
                source_chunks=[],
                retrieval_origins=[origin],
                community_ids=sorted({community for match in all_matches if match.uri in key for community in match.community_ids}),
                relevance_score=max(matched_scores) if matched_scores else None,
                structural_score=structural_score,
                matched_concept_ids=sorted({match.concept_id for match in matched}),
            )
            evidence[key] = item
        elif origin not in item.retrieval_origins:
            item.retrieval_origins.append(origin)
            item.structural_score = max(item.structural_score or 0.0, structural_score)
        if (source_chunk.document_id, source_chunk.chunk_id) not in {(chunk.document_id, chunk.chunk_id) for chunk in item.source_chunks}:
            item.source_chunks.append(source_chunk)

    def _select_evidence(self, values, *, concept_count: int) -> tuple[list[EvidenceItem], dict[str, object]]:
        """Keep a bounded, coverage-aware set instead of forwarding broad OR matches."""
        items = list(values)
        minimum_coverage = 2 if concept_count > 1 else 1
        coverage_filtered = [
            item for item in items
            if len(item.matched_concept_ids) >= minimum_coverage or "path" in item.retrieval_origins
        ]
        ranked = sorted(
            coverage_filtered,
            key=lambda item: (
                -len(item.matched_concept_ids),
                -(item.relevance_score if item.relevance_score is not None else -1.0),
                -(item.structural_score if item.structural_score is not None else -1.0),
                item.evidence_id,
            ),
        )
        selected = ranked[: self.max_evidence_items]
        return selected, {
            "retrieval_budget": {
                "minimum_similarity": self.minimum_match_similarity,
                "max_quads_per_seed": self.max_quads_per_seed,
                "max_evidence_items": self.max_evidence_items,
                "minimum_concept_coverage": minimum_coverage,
                "pre_filter_evidence_count": len(items),
                "coverage_filtered_count": len(coverage_filtered),
                "selected_evidence_count": len(selected),
            }
        }


def _match_metadata(match: ERMatch) -> dict[str, object]:
    return {"concept_id": match.concept_id, "input_term": match.input_term, "uri": match.uri, "label": match.label, "similarity": match.similarity, "community_ids": list(match.community_ids)}
