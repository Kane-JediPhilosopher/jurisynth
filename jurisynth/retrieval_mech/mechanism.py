"""The Retrieval Mech's single opaque callable boundary."""

from __future__ import annotations

import asyncio
import hashlib
from dataclasses import asdict, dataclass, field, replace
from typing import Protocol

from jurisynth.contracts import Assertion, EvidenceBundle, EvidenceItem, ImageEvidence, RetrievalRequest, SourceChunk, TableEvidence
from jurisynth.retrieval_mech.artifacts import ChunkIndex, Embedder, ImageIndex, TableIndex
from jurisynth.retrieval_mech.config import RetrievalSettings
from jurisynth.retrieval_mech.community_hierarchy import CommunityOrientationBuilder
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
    structured_retriever: StructuredRetriever | None = None
    settings: RetrievalSettings = field(default_factory=RetrievalSettings)
    community_orientation_builder: CommunityOrientationBuilder | None = None
    _operation_semaphore: asyncio.Semaphore = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Bound internal work shared by all concurrent leaf retrievals."""
        self._operation_semaphore = asyncio.Semaphore(self.settings.internal_concurrency_limit)

    async def retrieve_evidence(self, request: RetrievalRequest) -> EvidenceBundle:
        """Perform one logical retrieval operation for one AST leaf."""
        try:
            chunks_task = self._run_operation(asyncio.to_thread(self._search_chunks, request.leaf_query))
            tables_task = self._run_operation(asyncio.to_thread(self._search_tables, request.leaf_query, request.constraints))
            images_task = self._run_operation(asyncio.to_thread(self._search_images, request.leaf_query, request.constraints))
            structured_task = self._run_operation(self._search_structured(request))
            chunk_hits, table_hits, image_hits, structured_result = await asyncio.gather(
                chunks_task, tables_task, images_task, structured_task
            )
        except Exception as exc:
            return EvidenceBundle(
                query_id=request.query_id, status="error",
                retrieval_metadata={"warnings": [f"retrieval failed: {exc!r}"]},
            )

        warnings = list(structured_result.warnings)
        if self.structured_retriever is None:
            warnings.append("Structured KG retrieval is unavailable until E-R indices and communities are persisted.")

        structured_items = list(structured_result.evidence_items)
        coherence = _attach_coherence(structured_items, chunk_hits)
        evidence_items = structured_items + _chunk_evidence_items(request, chunk_hits, structured_items)
        status = self._status_for(evidence_items, chunk_hits, table_hits)
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
            status = self._status_for(evidence_items, chunk_hits, table_hits)
            structured_result.metadata = {**structured_result.metadata, "broaden_candidates": escalated.metadata}
        community_summary, community_metadata = self._community_orientation(structured_result.metadata)
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
                **structured_result.metadata,
                "coherence": coherence,
                "escalation_stages": stages,
                "warnings": warnings,
                **community_metadata,
            },
        )

    def _community_orientation(self, metadata: dict[str, object]) -> tuple[str | None, dict[str, object]]:
        if self.community_orientation_builder is None:
            return None, {}
        raw = metadata.get("relevant_communities", [])
        if not isinstance(raw, list):
            return None, {"community_orientation_warning": "Malformed relevant-community metadata."}
        ordered = sorted(
            (item for item in raw if isinstance(item, dict) and isinstance(item.get("community_id"), str)),
            key=lambda item: (-float(item.get("score", 0.0)), str(item["community_id"])),
        )
        orientation = self.community_orientation_builder.build([str(item["community_id"]) for item in ordered])
        if orientation is None:
            return None, {}
        return orientation.text, {"community_orientation": orientation.provenance}

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

    def _search_tables(self, query: str, constraints: dict[str, object]) -> list[TableEvidence]:
        document_ids = _document_ids(constraints)
        if document_ids is None:
            hits = [
                hit
                for index in self.table_indices
                for hit in index.search(query, self.embedder, self.settings.table_top_k, self.settings.row_top_k)
            ]
        else:
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

    @staticmethod
    def _chunk_metadata(hit: SourceChunk) -> dict[str, object]:
        return {"chunk_id": hit.chunk_id, "document_id": hit.document_id, "similarity": hit.similarity, "text": hit.text}

    def _status_for(self, evidence_items: list, chunk_hits: list[SourceChunk], table_hits: list[TableEvidence]) -> str:
        """Classify one completed retrieval deterministically without hiding weak support."""
        strong_structured = any(
            "chunk" not in item.retrieval_origins
            and
            item.relevance_score is not None and item.relevance_score >= self.settings.similarity_threshold
            for item in evidence_items
        )
        strong_table = any(
            hit.combined_score is not None and hit.combined_score >= self.settings.similarity_threshold
            for hit in table_hits
        )
        if (evidence_items or table_hits) and (strong_structured or strong_table):
            return "success"
        if evidence_items or table_hits or chunk_hits:
            return "weak"
        return "empty"


async def retrieve_evidence(request: RetrievalRequest, mechanism: RetrievalMechanism) -> EvidenceBundle:
    """Convenience function matching the public Retrieval Mech contract."""
    return await mechanism.retrieve_evidence(request)


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
