"""Query-time matching over persisted entity and relation FAISS indices."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from collections.abc import Mapping
from typing import Any, Protocol
from time import perf_counter

import numpy as np

try:
    import faiss
except ModuleNotFoundError:
    faiss = None

from jurisynth.retrieval_mech.lazy_er_metadata import SQLiteResourceRecords, normalize_label
from jurisynth.retrieval_mech.resource_records import ResourceRecord
from jurisynth.retrieval_mech.er_shards import (
    available_shard_manifests,
    load_lazy_sharded_index,
    shard_required_gb,
)


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
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class PersistedERIndices:
    entity_index: Any
    relation_index: Any
    entity_records: Mapping[int, ResourceRecord]
    relation_records: Mapping[int, ResourceRecord]
    load_metadata: dict[str, object] | None = None

    def __post_init__(self) -> None:
        # Preserve the small-fixture/pilot constructor contract while global
        # loads use SQLite-backed mappings.
        if isinstance(self.entity_records, list):
            self.entity_records = dict(enumerate(self.entity_records))
        if isinstance(self.relation_records, list):
            self.relation_records = dict(enumerate(self.relation_records))

    @classmethod
    def load(
        cls,
        directory: str | Path,
        *,
        index_mode: str | None = None,
        reserve_memory_gb: float | None = None,
    ) -> "PersistedERIndices":
        if faiss is None:
            raise RuntimeError("FAISS is required to load persisted E-R indices.")
        directory = Path(directory)
        requested_mode = (index_mode or os.getenv("JURISYNTH_ER_INDEX_MODE", "auto")).strip().lower()
        if requested_mode not in {"auto", "memory", "mmap", "sharded"}:
            raise ValueError("E-R index mode must be 'auto', 'memory', 'mmap', or 'sharded'.")
        reserve_gb = reserve_memory_gb if reserve_memory_gb is not None else float(os.getenv("JURISYNTH_ER_INDEX_RESERVE_GB", "2"))
        if reserve_gb < 0:
            raise ValueError("E-R index reserve memory must be non-negative.")
        entity_path, relation_path = directory / "entity.index", directory / "relation.index"
        index_bytes = entity_path.stat().st_size + relation_path.stat().st_size
        available_gb = _available_memory_gb()
        required_gb = index_bytes / 1024 ** 3 + reserve_gb
        selected_mode = _select_index_mode(requested_mode, available_gb, required_gb)
        shard_directory: Path | None = None
        shard_count: int | None = None
        if selected_mode == "mmap" and requested_mode == "auto":
            shard_directory, shard_count = _choose_adaptive_shards(directory, available_gb, reserve_gb)
            if shard_directory is not None:
                selected_mode = "sharded"
        elif selected_mode == "sharded":
            shard_directory, shard_count = _choose_requested_shards(directory)
        if selected_mode == "mmap" and any(_is_flat_index(path) for path in (entity_path, relation_path)):
            raise RuntimeError(
                "The persisted E-R indices use FAISS IndexFlatIP. This layout's mmap flag does not reduce "
                "resident memory, so adaptive loading refuses to risk memory pressure. Free memory, or build "
                "a sharded/compressed ANN E-R index before querying this corpus."
            )
        sqlite_path = directory / "er_metadata.sqlite"
        if sqlite_path.is_file():
            entities: Mapping[int, ResourceRecord] = SQLiteResourceRecords(sqlite_path, "entity")
            relations: Mapping[int, ResourceRecord] = SQLiteResourceRecords(sqlite_path, "relation")
        else:
            metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
            entities = {index: ResourceRecord(**record) for index, record in enumerate(metadata["entities"])}
            relations = {index: ResourceRecord(**record) for index, record in enumerate(metadata["relations"])}
        try:
            if selected_mode == "sharded":
                assert shard_directory is not None
                entity_index = load_lazy_sharded_index(shard_directory, "entity") if entities else None
                relation_index = load_lazy_sharded_index(shard_directory, "relation") if relations else None
            else:
                entity_index = _read_index(entity_path, selected_mode) if entities else None
                relation_index = _read_index(relation_path, selected_mode) if relations else None
        except Exception:
            if selected_mode != "mmap" or requested_mode == "mmap":
                raise
            selected_mode = "memory"
            entity_index = _read_index(entity_path, selected_mode) if entities else None
            relation_index = _read_index(relation_path, selected_mode) if relations else None
        return cls(entity_index, relation_index, entities, relations, {
            "requested_mode": requested_mode,
            "selected_mode": selected_mode,
            "available_memory_gb_at_load": available_gb,
            "index_bytes": index_bytes,
            "memory_load_threshold_gb": round(required_gb, 3),
            "reserve_memory_gb": reserve_gb,
            "mmap_is_os_page_cache_backed": selected_mode == "mmap",
            "shard_count": shard_count,
            "shard_directory": str(shard_directory) if shard_directory else None,
        })


def _available_memory_gb() -> float | None:
    try:
        import psutil
    except ModuleNotFoundError:
        return None
    return psutil.virtual_memory().available / 1024 ** 3


def _select_index_mode(requested_mode: str, available_gb: float | None, required_gb: float) -> str:
    if requested_mode != "auto":
        return requested_mode
    return "mmap" if available_gb is not None and available_gb < required_gb else "memory"


def _choose_requested_shards(directory: Path) -> tuple[Path, int]:
    configured = os.getenv("JURISYNTH_ER_SHARD_COUNT", "auto").strip().lower()
    manifests = available_shard_manifests(directory)
    if configured != "auto":
        try:
            count = int(configured)
        except ValueError as error:
            raise ValueError("JURISYNTH_ER_SHARD_COUNT must be 'auto' or an integer shard count.") from error
        if count not in manifests:
            raise FileNotFoundError(f"No complete E-R shard configuration exists for {count} shards.")
        return manifests[count], count
    if not manifests:
        raise FileNotFoundError("No complete E-R shard configuration is available.")
    count = min(manifests)
    return manifests[count], count


def _choose_adaptive_shards(directory: Path, available_gb: float | None, reserve_gb: float) -> tuple[Path | None, int | None]:
    if available_gb is None:
        return None, None
    manifests = available_shard_manifests(directory)
    compatible = [
        (count, path)
        for count, path in manifests.items()
        if available_gb >= shard_required_gb(path) + reserve_gb
    ]
    if not compatible:
        return None, None
    count, path = min(compatible)
    return path, count


def _read_index(path: Path, mode: str):
    if mode == "memory":
        return faiss.read_index(str(path))
    return faiss.read_index(str(path), faiss.IO_FLAG_MMAP | faiss.IO_FLAG_READ_ONLY)


def _is_flat_index(path: Path) -> bool:
    """Recognize FAISS's persisted IndexFlat header without loading its vectors."""
    with path.open("rb") as file:
        return file.read(4) == b"IxFI"


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
        started = perf_counter()
        entity_matches, entity_metadata = self._match(
            entity_concepts,
            self.indices.entity_index,
            self.indices.entity_records,
            entity_top_k,
            minimum_similarity,
            exact_label_priority,
        )
        relation_matches, relation_metadata = self._match(
            relation_concepts,
            self.indices.relation_index,
            self.indices.relation_records,
            relation_top_k,
            minimum_similarity,
            exact_label_priority,
        )
        return ERMatchResult(
            entity_matches=tuple(entity_matches),
            relation_matches=tuple(relation_matches),
            metadata={
                "duration_ms": round((perf_counter() - started) * 1000, 3),
                "entity": entity_metadata,
                "relation": relation_metadata,
            },
        )

    def _match(
        self,
        concepts: list[Concept],
        index: Any,
        records: Mapping[int, ResourceRecord],
        top_k: int,
        minimum_similarity: float | None,
        exact_label_priority: bool,
    ) -> tuple[list[ERMatch], dict[str, int]]:
        if index is None or not concepts or top_k < 1:
            return [], {
                "concept_count": len(concepts),
                "exact_concept_count": 0,
                "vector_concept_count": 0,
                "vector_term_count": 0,
                "index_search_calls": 0,
            }
        matches_by_concept: list[list[ERMatch]] = [[] for _ in concepts]
        pending: list[tuple[int, Concept, tuple[str, ...]]] = []
        for concept_index, concept in enumerate(concepts):
            terms = (concept.text, *concept.variants)
            exact_matches = self._exact_label_matches(concept, terms, records) if exact_label_priority else []
            if exact_matches:
                matches_by_concept[concept_index] = exact_matches
                continue
            pending.append((concept_index, concept, terms))

        flattened_terms = [term for _index, _concept, terms in pending for term in terms]
        if flattened_terms:
            vectors = np.asarray(
                self.embedder.encode(flattened_terms, normalize_embeddings=True),
                dtype=np.float32,
            )
            if vectors.ndim != 2 or vectors.shape[0] != len(flattened_terms):
                raise ValueError("embedder returned vectors inconsistent with E-R matcher input")
            all_scores, all_ids = index.search(vectors, min(top_k, index.ntotal))
        else:
            all_scores = np.empty((0, 0), dtype=np.float32)
            all_ids = np.empty((0, 0), dtype=np.int64)

        row = 0
        for concept_index, concept, terms in pending:
            best_per_uri: dict[str, ERMatch] = {}
            concept_rows = len(terms)
            for term, term_scores, term_ids in zip(
                terms,
                all_scores[row:row + concept_rows],
                all_ids[row:row + concept_rows],
            ):
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
            matches_by_concept[concept_index] = sorted(
                best_per_uri.values(),
                key=lambda item: (-item.similarity, item.uri),
            )
            row += concept_rows

        return (
            [match for concept_matches in matches_by_concept for match in concept_matches],
            {
                "concept_count": len(concepts),
                "exact_concept_count": len(concepts) - len(pending),
                "vector_concept_count": len(pending),
                "vector_term_count": len(flattened_terms),
                "index_search_calls": 1 if flattened_terms else 0,
            },
        )

    @staticmethod
    def _exact_label_matches(concept: Concept, terms: tuple[str, ...], records: Mapping[int, ResourceRecord]) -> list[ERMatch]:
        """Prefer an unambiguous normalized label match over approximate vector neighbours.

        FAISS similarity is semantic and can make country/entity neighbours look
        interchangeable.  A normalized label equality is a stronger grounding
        signal; it is deliberately not inferred from a floating-point score of
        1.0, which is neither stable nor a reliable indicator of lexical identity.
        """
        normalized_terms = {_normalize_label(term): term for term in terms if _normalize_label(term)}
        exact_lookup = getattr(records, "exact_matches", None)
        if callable(exact_lookup):
            found = exact_lookup(normalized_terms)
            matches = [
                ERMatch(concept.concept_id, normalized_terms[normalized], record.uri, record.label, 1.0, record.community_ids)
                for normalized, record in found
            ]
        else:
            matches = [
                ERMatch(concept.concept_id, normalized_terms[_normalize_label(record.label)], record.uri, record.label, 1.0, record.community_ids)
                for record in records.values()
                if _normalize_label(record.label) in normalized_terms
            ]
        return sorted(matches, key=lambda item: item.uri)


def _normalize_label(value: str) -> str:
    """Normalize superficial punctuation/spacing without conflating lexical variants."""
    return normalize_label(value)
