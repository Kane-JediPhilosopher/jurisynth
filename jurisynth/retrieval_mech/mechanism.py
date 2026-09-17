"""The Retrieval Mech's single opaque callable boundary."""

from __future__ import annotations

import asyncio
import hashlib
import time
from dataclasses import asdict, dataclass, field, replace
from typing import Protocol

from jurisynth.contracts import Assertion, EvidenceBundle, EvidenceItem, ImageEvidence, RetrievalRequest, SourceChunk, TableEvidence
from jurisynth.retrieval_mech.artifacts import ChunkIndex, Embedder, ImageIndex, TableIndex
from jurisynth.retrieval_mech.config import RetrievalSettings
from jurisynth.retrieval_mech.community_hierarchy import CommunityOrientationBuilder
from jurisynth.retrieval_mech.community_summary import CommunitySummaryInput, LazyCommunitySummarizer
from jurisynth.retrieval_mech.document_metadata import DocumentMetadataStore, InstrumentScopeContext
from jurisynth.retrieval_mech.image_expander import ImageExpander
from jurisynth.retrieval_mech.rdf_retriever import StructuredRetrievalResult


class StructuredRetriever(Protocol):
    """Future E-R/community/SPARQL implementation behind the opaque boundary."""
    async def retrieve(self, request: RetrievalRequest) -> StructuredRetrievalResult: ...


@dataclass(slots=True)
class RetrievalMechanism:
    """Retrieve auxiliary text/table evidence now, with a replaceable structured path."""

    embedder: Embedder
    chunk_indices: list[ChunkIndex] = field(default_factory=list)
    table_indices: list[TableIndex] = field(default_factory=list)
    image_indices: list[ImageIndex] = field(default_factory=list)
    image_expander: ImageExpander | None = None
    structured_retriever: StructuredRetriever | None = None
    settings: RetrievalSettings = field(default_factory=RetrievalSettings)
    community_orientation_builder: CommunityOrientationBuilder | None = None
    community_descriptors: dict[str, CommunitySummaryInput] = field(default_factory=dict)
    community_summarizer: LazyCommunitySummarizer | None = None
    document_metadata: DocumentMetadataStore | None = None
    community_summary_min_communities: int = 6
    community_summary_min_average_distance: float = 4.0
    _operation_semaphore: asyncio.Semaphore = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Bound internal work shared by all concurrent leaf retrievals."""
        if self.community_summary_min_communities < 2:
            raise ValueError("community_summary_min_communities must be at least two")
        if self.community_summary_min_average_distance < 0:
            raise ValueError("community_summary_min_average_distance must be non-negative")
        self._operation_semaphore = asyncio.Semaphore(self.settings.internal_concurrency_limit)

    async def retrieve_evidence(self, request: RetrievalRequest) -> EvidenceBundle:
        """Perform one logical retrieval operation for one AST leaf."""
        retrieval_started = time.perf_counter()
        pass_timings: dict[str, float] = {}
        scope_context = (
            self.document_metadata.resolve_request_scope(request)
            if self.document_metadata is not None
            else InstrumentScopeContext()
        )
        try:
            pass_one_started = time.perf_counter()
            chunks_task = self._run_operation(asyncio.to_thread(self._search_chunks, request.leaf_query))
            tables_task = self._run_operation(asyncio.to_thread(self._search_tables, request.leaf_query))
            images_task = self._run_operation(asyncio.to_thread(self._search_images, request.leaf_query, request.constraints))
            structured_task = self._run_operation(self._search_structured(request))
            chunk_hits, table_hits, image_hits, structured_result = await asyncio.gather(
                chunks_task, tables_task, images_task, structured_task
            )
            pass_timings["pass_one"] = round((time.perf_counter() - pass_one_started) * 1000, 3)
        except Exception as exc:
            return EvidenceBundle(
                query_id=request.query_id, status="error",
                retrieval_metadata={"warnings": [f"retrieval failed: {exc!r}"]},
            )

        warnings = list(structured_result.warnings)
        table_hits = _tag_table_hits(table_hits, "global")
        image_hits = _tag_image_hits(image_hits, "global")
        structured_items = list(structured_result.evidence_items)
        normal_chunk_items = _chunk_evidence_items(request, chunk_hits, structured_items)
        normal_evidence = structured_items + normal_chunk_items
        _classify_evidence_items(normal_evidence, self.document_metadata, scope_context)
        covered_before = self._covered_instrument_keys(normal_evidence, [], scope_context)
        missing_before = set(scope_context.target_keys).difference(covered_before)
        recovery_chunks: list[SourceChunk] = []
        recovery_documents: dict[str, tuple[str, ...]] = {}
        # This is deliberately leaf-explicit and multi-instrument only.  It is
        # not driven by inherited/global constraints and runs at most once.
        if (
            self.document_metadata is not None
            and len(scope_context.target_keys) > 1
            and missing_before
        ):
            recovery_documents = self.document_metadata.document_ids_for_keys(missing_before)
            selected_documents = {
                document_id
                for values in recovery_documents.values()
                for document_id in values
            }
            if selected_documents:
                recovery_started = time.perf_counter()
                recovery_chunks = await self._run_operation(asyncio.to_thread(
                    self._search_chunks_for_documents,
                    request.leaf_query,
                    selected_documents,
                ))
                pass_timings["instrument_source_recovery"] = round(
                    (time.perf_counter() - recovery_started) * 1000, 3
                )
                chunk_hits = _merge_chunk_hits(chunk_hits, recovery_chunks)
        scoped_document_ids = _relevant_document_ids(
            chunk_hits,
            structured_items,
            similarity_threshold=self.settings.similarity_threshold,
        )
        explicit_document_ids = _document_ids(request.constraints)
        if explicit_document_ids:
            scoped_document_ids.update(explicit_document_ids)

        scoped_table_hits: list[TableEvidence] = []
        scoped_image_hits: list[ImageEvidence] = []
        if scoped_document_ids:
            try:
                pass_two_started = time.perf_counter()
                scoped_table_task = self._run_operation(asyncio.to_thread(
                    self._search_tables_for_documents,
                    request.leaf_query,
                    scoped_document_ids,
                ))
                scoped_image_task = self._run_operation(asyncio.to_thread(
                    self._search_images_for_documents,
                    request.leaf_query,
                    scoped_document_ids,
                ))
                scoped_table_hits, scoped_image_hits = await asyncio.gather(scoped_table_task, scoped_image_task)
                pass_timings["pass_two"] = round((time.perf_counter() - pass_two_started) * 1000, 3)
            except Exception as exc:
                warnings.append(f"source-document modality retrieval failed: {exc!r}")
        table_pass_one_raw_count = len(table_hits)
        table_pass_two_raw_count = len(scoped_table_hits)
        image_pass_one_raw_count = len(image_hits)
        image_pass_two_raw_count = len(scoped_image_hits)
        _classify_table_hits(table_hits, self.document_metadata, scope_context)
        _classify_table_hits(scoped_table_hits, self.document_metadata, scope_context)
        _classify_image_hits(image_hits, self.document_metadata, scope_context)
        _classify_image_hits(scoped_image_hits, self.document_metadata, scope_context)
        table_hits = _merge_table_hits(
            table_hits, _tag_table_hits(scoped_table_hits, "source_document"), self.settings.row_top_k
        )
        image_hits = _merge_image_hits(
            image_hits, _tag_image_hits(scoped_image_hits, "source_document"), self.settings.table_top_k
        )

        expanded_count = 0
        if image_hits and self.image_expander is not None:
            try:
                expansion_started = time.perf_counter()
                candidates = sorted(
                    [
                        item for item in image_hits
                        if (item.similarity or 0.0) >= self.settings.similarity_threshold
                    ],
                    key=lambda item: item.similarity or 0.0,
                    reverse=True,
                )[:self.settings.image_expansion_top_k]
                if candidates:
                    expanded = await self._run_operation(self.image_expander.expand(candidates, request.leaf_query))
                    image_hits = _replace_expanded_images(image_hits, expanded)
                    expanded_count = len(expanded)
                    pass_timings["image_expansion"] = round((time.perf_counter() - expansion_started) * 1000, 3)
            except Exception as exc:
                warnings.append(f"image expansion failed; using canonical caption: {exc!r}")
        if self.structured_retriever is None:
            warnings.append("Structured KG retrieval is unavailable until E-R indices and communities are persisted.")

        coherence = _attach_coherence(structured_items, chunk_hits)
        evidence_items = structured_items + _chunk_evidence_items(request, chunk_hits, structured_items)
        _mark_recovery_origins(evidence_items, recovery_chunks)
        _classify_evidence_items(evidence_items, self.document_metadata, scope_context)
        evidence_items = _rank_evidence_by_scope(evidence_items)
        status = self._status_for(evidence_items, chunk_hits, table_hits, scope_context)
        stages = ["normal"]
        if status in {"weak", "empty"} and self.structured_retriever is not None:
            escalated = await self._run_operation(self._search_structured(replace(
                request,
                retrieval_config={**request.retrieval_config, "escalation_stage": "broaden_candidates"},
            )))
            stages.append("broaden_candidates")
            warnings.extend(escalated.warnings)
            structured_items = _merge_evidence_items(structured_items, escalated.evidence_items)
            coherence = _attach_coherence(structured_items, chunk_hits)
            evidence_items = structured_items + _chunk_evidence_items(request, chunk_hits, structured_items)
            _mark_recovery_origins(evidence_items, recovery_chunks)
            _classify_evidence_items(evidence_items, self.document_metadata, scope_context)
            evidence_items = _rank_evidence_by_scope(evidence_items)
            status = self._status_for(evidence_items, chunk_hits, table_hits, scope_context)
            structured_result.metadata = {**structured_result.metadata, "broaden_candidates": escalated.metadata}
        community_summary, community_metadata = await self._community_orientation(structured_result.metadata)
        return EvidenceBundle(
            query_id=request.query_id,
            status=status,
            evidence_items=evidence_items,
            table_evidence=table_hits,
            image_evidence=image_hits,
            community_summary=community_summary,
            retrieval_metadata={
                "direct_chunk_matches": [self._chunk_metadata(hit) for hit in chunk_hits],
                "image_matches": [asdict(hit) for hit in image_hits],
                "modality_retrieval": {
                    "source_document_ids": sorted(scoped_document_ids),
                    "table_pass_one_count": sum("global" in hit.retrieval_origins for hit in table_hits),
                    "table_pass_two_count": sum("source_document" in hit.retrieval_origins for hit in table_hits),
                    "table_pass_one_raw_count": table_pass_one_raw_count,
                    "table_pass_two_raw_count": table_pass_two_raw_count,
                    "table_merged_reranked_count": len(table_hits),
                    "image_pass_one_count": sum("global" in hit.retrieval_origins for hit in image_hits),
                    "image_pass_two_count": sum("source_document" in hit.retrieval_origins for hit in image_hits),
                    "image_pass_one_raw_count": image_pass_one_raw_count,
                    "image_pass_two_raw_count": image_pass_two_raw_count,
                    "image_expanded_count": expanded_count,
                    "timings_ms": {
                        **pass_timings,
                        "total": round((time.perf_counter() - retrieval_started) * 1000, 3),
                    },
                },
                **structured_result.metadata,
                "coherence": coherence,
                "instrument_scope": {
                    "explicitly_scoped": scope_context.explicitly_scoped,
                    "source": scope_context.source,
                    "matched_terms": list(scope_context.matched_terms),
                    "target_keys": sorted(scope_context.target_keys),
                    "evidence_counts": _scope_counts(evidence_items),
                    "table_counts": _scope_counts(table_hits),
                    "image_counts": _scope_counts(image_hits),
                    "covered_target_keys": sorted(
                        self._covered_instrument_keys(evidence_items, table_hits, scope_context)
                    ),
                    "missing_target_keys": sorted(
                        set(scope_context.target_keys).difference(
                            self._covered_instrument_keys(evidence_items, table_hits, scope_context)
                        )
                    ),
                    "source_recovery": {
                        "triggered": bool(recovery_chunks),
                        "missing_before": sorted(missing_before),
                        "documents_by_key": {
                            key: list(values) for key, values in recovery_documents.items()
                        },
                        "chunk_count": len(recovery_chunks),
                    },
                },
                "escalation_stages": stages,
                "warnings": warnings,
                **community_metadata,
            },
        )

    async def _community_orientation(self, metadata: dict[str, object]) -> tuple[str | None, dict[str, object]]:
        if self.community_orientation_builder is None:
            return None, {}
        raw = metadata.get("orientation_communities", metadata.get("relevant_communities", []))
        if not isinstance(raw, list):
            return None, {"community_orientation_warning": "Malformed relevant-community metadata."}
        ordered = [item for item in raw if isinstance(item, dict) and isinstance(item.get("community_id"), str)]
        if any("score" in item for item in ordered):
            ordered = sorted(
                enumerate(ordered),
                key=lambda pair: (-float(pair[1].get("score", 0.0)), pair[0]),
            )
            ordered = [item for _, item in ordered]
        orientation = self.community_orientation_builder.build([str(item["community_id"]) for item in ordered])
        if orientation is None:
            return None, {}
        context_metadata: dict[str, object] = {"community_orientation": orientation.provenance}
        selected_ids = list(orientation.provenance["contributing_communities"])
        average_distance = float(orientation.provenance["average_tree_distance"])
        trigger_reason: str | None = None
        if len(selected_ids) >= self.community_summary_min_communities:
            trigger_reason = "community_count"
        elif average_distance >= self.community_summary_min_average_distance:
            trigger_reason = "tree_dispersion"
        if self.community_summarizer is None or trigger_reason is None:
            return orientation.text, context_metadata
        inputs = [self.community_descriptors[item] for item in selected_ids if item in self.community_descriptors]
        if len(inputs) < 2:
            context_metadata["community_summary_warning"] = "No sufficient persisted descriptors for lazy summary."
            return orientation.text, context_metadata
        lca = orientation.provenance.get("lca")
        summary_id = str(lca) if isinstance(lca, str) else "selected_communities"
        lazy_summary = await self._run_operation(self.community_summarizer.summarize(summary_id, inputs))
        if not lazy_summary:
            context_metadata["community_summary_warning"] = "Lazy community summary returned no content."
            return orientation.text, context_metadata
        context_metadata["lazy_community_summary"] = {
            "trigger": trigger_reason,
            "input_community_count": len(inputs),
            "authoritative": False,
            "source": "persisted_deterministic_orientation_descriptors",
        }
        return "Community orientation only — not legal evidence.\n" + lazy_summary, context_metadata

    async def _search_structured(self, request: RetrievalRequest) -> StructuredRetrievalResult:
        if self.structured_retriever is None:
            return StructuredRetrievalResult()
        result = await self.structured_retriever.retrieve(request)
        if isinstance(result, StructuredRetrievalResult):
            return result
        # Compatibility with early test doubles while the structured interface matures.
        return StructuredRetrievalResult(evidence_items=result)

    async def _run_operation(self, operation) -> object:
        """Apply the configured internal concurrency and timeout policy."""
        async with self._operation_semaphore:
            if self.settings.operation_timeout_seconds is None:
                return await operation
            return await asyncio.wait_for(operation, timeout=self.settings.operation_timeout_seconds)

    def _search_chunks(self, query: str) -> list[SourceChunk]:
        hits = [hit for index in self.chunk_indices for hit in index.search(query, self.embedder, self.settings.chunk_top_k)]
        return sorted(hits, key=lambda item: item.similarity or 0.0, reverse=True)[:self.settings.chunk_top_k]

    def _search_chunks_for_documents(
        self, query: str, document_ids: set[str]
    ) -> list[SourceChunk]:
        hits = [
            hit
            for index in self.chunk_indices
            for hit in index.search_documents(
                query, self.embedder, self.settings.chunk_top_k,
                document_ids=document_ids,
            )
        ]
        return sorted(
            hits, key=lambda item: item.similarity or 0.0, reverse=True
        )[:self.settings.chunk_top_k]

    def _search_tables(self, query: str) -> list[TableEvidence]:
        """Pass one is always corpus-wide; source scoping belongs to pass two."""
        hits = [
            hit
            for index in self.table_indices
            for hit in index.search(query, self.embedder, self.settings.table_top_k, self.settings.row_top_k)
        ]
        return sorted(hits, key=lambda item: item.combined_score or 0.0, reverse=True)[:self.settings.row_top_k]

    def _search_tables_for_documents(self, query: str, document_ids: set[str]) -> list[TableEvidence]:
        hits = [
            hit
            for index in self.table_indices
            for hit in index.search(
                query,
                self.embedder,
                self.settings.table_top_k,
                self.settings.row_top_k,
                document_ids=document_ids,
            )
        ]
        return sorted(hits, key=lambda item: item.combined_score or 0.0, reverse=True)[:self.settings.row_top_k]

    def _search_images(self, query: str, constraints: dict[str, object]) -> list[ImageEvidence]:
        if not self.image_indices or not _should_search_images(query, constraints):
            return []
        hits = [hit for index in self.image_indices for hit in index.search(query, self.embedder, self.settings.table_top_k)]
        return sorted(hits, key=lambda item: item.similarity or 0.0, reverse=True)[:self.settings.table_top_k]

    def _search_images_for_documents(self, query: str, document_ids: set[str]) -> list[ImageEvidence]:
        hits = [
            hit
            for index in self.image_indices
            for hit in index.search(
                query,
                self.embedder,
                self.settings.table_top_k,
                document_ids=document_ids,
            )
        ]
        return sorted(hits, key=lambda item: item.similarity or 0.0, reverse=True)[:self.settings.table_top_k]

    @staticmethod
    def _chunk_metadata(hit: SourceChunk) -> dict[str, object]:
        return {"chunk_id": hit.chunk_id, "document_id": hit.document_id, "similarity": hit.similarity, "text": hit.text}

    def _status_for(
        self,
        evidence_items: list,
        chunk_hits: list[SourceChunk],
        table_hits: list[TableEvidence],
        scope_context: InstrumentScopeContext,
    ) -> str:
        """Classify one completed retrieval deterministically without hiding weak support."""
        strong_structured = any(
            "chunk" not in item.retrieval_origins
            and
            (not scope_context.explicitly_scoped or item.instrument_scope == "in_scope")
            and
            item.relevance_score is not None and item.relevance_score >= self.settings.similarity_threshold
            for item in evidence_items
        )
        strong_table = any(
            (not scope_context.explicitly_scoped or hit.instrument_scope == "in_scope")
            and hit.combined_score is not None and hit.combined_score >= self.settings.similarity_threshold
            for hit in table_hits
        )
        structured_sources = {
            (chunk.document_id, chunk.chunk_id)
            for item in evidence_items
            if "chunk" not in item.retrieval_origins
            and (not scope_context.explicitly_scoped or item.instrument_scope == "in_scope")
            for chunk in item.source_chunks
        }
        corroborated_chunk = any(
            (chunk.similarity or 0.0) >= self.settings.similarity_threshold
            and (chunk.document_id, chunk.chunk_id) in structured_sources
            for chunk in chunk_hits
        )
        covered_keys = self._covered_instrument_keys(evidence_items, table_hits, scope_context)
        scope_complete = (
            not scope_context.explicitly_scoped
            or set(scope_context.target_keys).issubset(covered_keys)
        )
        if (
            (evidence_items or table_hits)
            and scope_complete
            and (strong_structured or strong_table or corroborated_chunk)
        ):
            return "success"
        if evidence_items or table_hits or chunk_hits:
            return "weak"
        return "empty"

    def _covered_instrument_keys(
        self,
        evidence_items: list[EvidenceItem],
        table_hits: list[TableEvidence],
        scope_context: InstrumentScopeContext,
    ) -> set[str]:
        if self.document_metadata is None or not scope_context.target_keys:
            return set()
        documents = {
            chunk.document_id
            for item in evidence_items
            if item.source_chunks
            and (item.relevance_score or 0.0) >= self.settings.similarity_threshold
            for chunk in item.source_chunks
        }
        documents.update(
            hit.document_id
            for hit in table_hits
            if (hit.combined_score or 0.0) >= self.settings.similarity_threshold
        )
        covered: set[str] = set()
        for document_id in documents:
            record = self.document_metadata.get(document_id)
            if record is not None:
                covered.update(set(record.canonical_keys).intersection(scope_context.target_keys))
        return covered


async def retrieve_evidence(request: RetrievalRequest, mechanism: RetrievalMechanism) -> EvidenceBundle:
    """Convenience function matching the public Retrieval Mech contract."""
    return await mechanism.retrieve_evidence(request)


def _relevant_document_ids(
    chunk_hits: list[SourceChunk],
    structured_items: list[EvidenceItem],
    *,
    similarity_threshold: float,
) -> set[str]:
    """Anchor pass two to direct chunks, with structured-only fallback."""
    chunk_documents = {
        chunk.document_id
        for chunk in chunk_hits
        if chunk.document_id
        and (chunk.similarity or 0.0) >= similarity_threshold
    }
    if chunk_documents:
        return chunk_documents
    return {
        chunk.document_id
        for item in structured_items
        if (item.relevance_score or 0.0) >= similarity_threshold
        for chunk in item.source_chunks
        if chunk.document_id
    }


def _tag_table_hits(hits: list[TableEvidence], origin: str) -> list[TableEvidence]:
    for hit in hits:
        if origin not in hit.retrieval_origins:
            hit.retrieval_origins.append(origin)
    return hits


def _tag_image_hits(hits: list[ImageEvidence], origin: str) -> list[ImageEvidence]:
    for hit in hits:
        if origin not in hit.retrieval_origins:
            hit.retrieval_origins.append(origin)
    return hits


def _classify_evidence_items(
    items: list[EvidenceItem],
    metadata: DocumentMetadataStore | None,
    context: InstrumentScopeContext,
) -> None:
    for item in items:
        scopes = {
            metadata.classify_document(chunk.document_id, context)
            for chunk in item.source_chunks
        } if metadata is not None else {"unknown"}
        if "in_scope" in scopes:
            item.instrument_scope = "in_scope"
        elif "cross_instrument" in scopes:
            item.instrument_scope = "cross_instrument"
        else:
            item.instrument_scope = "unknown"


def _classify_table_hits(
    hits: list[TableEvidence],
    metadata: DocumentMetadataStore | None,
    context: InstrumentScopeContext,
) -> None:
    if metadata is None:
        return
    for hit in hits:
        hit.instrument_scope = metadata.classify_document(hit.document_id, context)


def _classify_image_hits(
    hits: list[ImageEvidence],
    metadata: DocumentMetadataStore | None,
    context: InstrumentScopeContext,
) -> None:
    if metadata is None:
        return
    for hit in hits:
        hit.instrument_scope = metadata.classify_document(hit.document_id, context)


def _scope_priority(item: object) -> int:
    return {"in_scope": 2, "unknown": 1, "cross_instrument": 0}.get(
        str(getattr(item, "instrument_scope", "unknown")), 1
    )


def _rank_evidence_by_scope(items: list[EvidenceItem]) -> list[EvidenceItem]:
    """Stable scope ordering preserves the retrievers' existing relevance order."""
    return sorted(items, key=_scope_priority, reverse=True)


def _scope_counts(items: list[object]) -> dict[str, int]:
    counts = {"in_scope": 0, "cross_instrument": 0, "unknown": 0}
    for item in items:
        scope = str(getattr(item, "instrument_scope", "unknown"))
        counts[scope if scope in counts else "unknown"] += 1
    return counts


def _merge_table_hits(
    broad: list[TableEvidence],
    scoped: list[TableEvidence],
    top_k: int,
) -> list[TableEvidence]:
    merged: dict[tuple[str, str, tuple[int, ...]], TableEvidence] = {}
    for hit in broad + scoped:
        key = (hit.document_id, hit.table_id, tuple(hit.row_ids))
        previous = merged.get(key)
        if previous is None:
            merged[key] = hit
            continue
        for origin in hit.retrieval_origins:
            if origin not in previous.retrieval_origins:
                previous.retrieval_origins.append(origin)
        if (hit.combined_score or 0.0) > (previous.combined_score or 0.0):
            hit.retrieval_origins = list(previous.retrieval_origins)
            merged[key] = hit
    return sorted(
        merged.values(),
        key=lambda item: (_scope_priority(item), item.combined_score or 0.0),
        reverse=True,
    )[:top_k]


def _merge_image_hits(
    broad: list[ImageEvidence],
    scoped: list[ImageEvidence],
    top_k: int,
) -> list[ImageEvidence]:
    merged: dict[tuple[str, str], ImageEvidence] = {}
    for hit in broad + scoped:
        key = (hit.document_id, hit.image_id)
        previous = merged.get(key)
        if previous is None:
            merged[key] = hit
            continue
        for origin in hit.retrieval_origins:
            if origin not in previous.retrieval_origins:
                previous.retrieval_origins.append(origin)
        if (hit.similarity or 0.0) > (previous.similarity or 0.0):
            hit.retrieval_origins = list(previous.retrieval_origins)
            merged[key] = hit
    return sorted(
        merged.values(),
        key=lambda item: (_scope_priority(item), item.similarity or 0.0),
        reverse=True,
    )[:top_k]


def _replace_expanded_images(
    original: list[ImageEvidence],
    expanded: list[ImageEvidence],
) -> list[ImageEvidence]:
    replacements = {(item.document_id, item.image_id): item for item in expanded}
    return [replacements.get((item.document_id, item.image_id), item) for item in original]


def _document_ids(constraints: dict[str, object]) -> set[str] | None:
    """Read only the explicit document filter supported by V1 table retrieval."""
    raw = constraints.get("document_ids", constraints.get("document_id"))
    if raw is None:
        return None
    if isinstance(raw, str):
        return {raw}
    if isinstance(raw, (list, tuple)) and all(isinstance(item, str) for item in raw):
        return set(raw)
    raise ValueError("constraints.document_id(s) must be a string or list of strings")


def _should_search_images(query: str, constraints: dict[str, object]) -> bool:
    """Images are opt-in auxiliary evidence, never a default legal-answer path."""
    if constraints.get("include_images") is True:
        return True
    visual_terms = {"image", "figure", "diagram", "chart", "map", "photo", "photograph", "scan", "logo", "visual"}
    return bool(visual_terms & set(query.lower().replace("?", " ").replace(",", " ").split()))


def _attach_coherence(evidence_items: list, chunk_hits: list[SourceChunk]) -> dict[str, float]:
    """Record directional agreement between KG-provenance and direct chunk retrieval."""
    faiss_chunks = {(chunk.document_id, chunk.chunk_id) for chunk in chunk_hits}
    provenance_chunks = {
        (chunk.document_id, chunk.chunk_id)
        for item in evidence_items
        for chunk in item.source_chunks
    }
    overlap = provenance_chunks & faiss_chunks
    for item in evidence_items:
        item_chunks = {(chunk.document_id, chunk.chunk_id) for chunk in item.source_chunks}
        item.coherence_score = len(item_chunks & faiss_chunks) / len(item_chunks) if item_chunks else None
    return {
        "quad_support_coverage": len(overlap) / len(provenance_chunks) if provenance_chunks else 0.0,
        "faiss_agreement": len(overlap) / len(faiss_chunks) if faiss_chunks else 0.0,
    }


def _merge_chunk_hits(
    normal: list[SourceChunk], recovered: list[SourceChunk]
) -> list[SourceChunk]:
    merged: dict[tuple[str, str], SourceChunk] = {
        (item.document_id, item.chunk_id): item for item in normal
    }
    for item in recovered:
        key = (item.document_id, item.chunk_id)
        if key not in merged or (item.similarity or 0.0) > (merged[key].similarity or 0.0):
            merged[key] = item
    return sorted(
        merged.values(), key=lambda item: item.similarity or 0.0, reverse=True
    )


def _mark_recovery_origins(
    items: list[EvidenceItem], recovered: list[SourceChunk]
) -> None:
    recovered_sources = {(item.document_id, item.chunk_id) for item in recovered}
    if not recovered_sources:
        return
    for item in items:
        if any(
            (chunk.document_id, chunk.chunk_id) in recovered_sources
            for chunk in item.source_chunks
        ) and "instrument_source_scoped" not in item.retrieval_origins:
            item.retrieval_origins.append("instrument_source_scoped")


def _chunk_evidence_items(
    request: RetrievalRequest,
    chunk_hits: list[SourceChunk],
    structured_items: list[EvidenceItem],
) -> list[EvidenceItem]:
    """Expose direct chunk retrieval to the Reasoner as citable, weak evidence."""
    represented = {
        (chunk.document_id, chunk.chunk_id)
        for item in structured_items
        for chunk in item.source_chunks
    }
    items: list[EvidenceItem] = []
    for chunk in chunk_hits:
        if (chunk.document_id, chunk.chunk_id) in represented:
            continue
        seed = f"{chunk.document_id}\u241f{chunk.chunk_id}".encode()
        items.append(EvidenceItem(
            evidence_id="C_" + hashlib.sha256(seed).hexdigest()[:16],
            assertion=Assertion(
                f"Source chunk {chunk.document_id}:{chunk.chunk_id}",
                "was retrieved for",
                request.leaf_query,
            ),
            source_chunks=[chunk],
            retrieval_origins=["chunk"],
            relevance_score=chunk.similarity,
            structural_score=0.0,
        ))
    return items


def _merge_evidence_items(existing: list[EvidenceItem], additional: list[EvidenceItem]) -> list[EvidenceItem]:
    """Keep escalation additive while preserving stable, unique evidence IDs."""
    merged = {item.evidence_id: item for item in existing}
    for item in additional:
        merged.setdefault(item.evidence_id, item)
    return list(merged.values())
