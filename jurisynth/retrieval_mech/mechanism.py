"""The Retrieval Mech's single opaque callable boundary."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Protocol

from jurisynth.contracts import EvidenceBundle, RetrievalRequest, SourceChunk, TableEvidence
from jurisynth.retrieval_mech.artifacts import ChunkIndex, Embedder, TableIndex
from jurisynth.retrieval_mech.config import RetrievalSettings


class StructuredRetriever(Protocol):
    """Future E-R/community/SPARQL implementation behind the opaque boundary."""
    async def retrieve(self, request: RetrievalRequest) -> list: ...


@dataclass(slots=True)
class RetrievalMechanism:
    """Retrieve auxiliary text/table evidence now, with a replaceable structured path."""

    embedder: Embedder
    chunk_indices: list[ChunkIndex] = field(default_factory=list)
    table_indices: list[TableIndex] = field(default_factory=list)
    structured_retriever: StructuredRetriever | None = None
    settings: RetrievalSettings = field(default_factory=RetrievalSettings)

    async def retrieve_evidence(self, request: RetrievalRequest) -> EvidenceBundle:
        """Perform one logical retrieval operation for one AST leaf."""
        try:
            chunks_task = asyncio.to_thread(self._search_chunks, request.leaf_query)
            tables_task = asyncio.to_thread(self._search_tables, request.leaf_query)
            structured_task = self._search_structured(request)
            chunk_hits, table_hits, evidence_items = await asyncio.gather(
                chunks_task, tables_task, structured_task
            )
        except Exception as exc:
            return EvidenceBundle(
                query_id=request.query_id, status="error",
                retrieval_metadata={"warnings": [f"retrieval failed: {exc!r}"]},
            )

        warnings: list[str] = []
        if self.structured_retriever is None:
            warnings.append("Structured KG retrieval is unavailable until E-R indices and communities are persisted.")

        status = "success" if evidence_items else "weak" if (chunk_hits or table_hits) else "empty"
        return EvidenceBundle(
            query_id=request.query_id,
            status=status,
            evidence_items=evidence_items,
            table_evidence=table_hits,
            retrieval_metadata={
                "direct_chunk_matches": [self._chunk_metadata(hit) for hit in chunk_hits],
                "warnings": warnings,
            },
        )

    async def _search_structured(self, request: RetrievalRequest) -> list:
        if self.structured_retriever is None:
            return []
        return await self.structured_retriever.retrieve(request)

    def _search_chunks(self, query: str) -> list[SourceChunk]:
        hits = [hit for index in self.chunk_indices for hit in index.search(query, self.embedder, self.settings.chunk_top_k)]
        return sorted(hits, key=lambda item: item.similarity or 0.0, reverse=True)[:self.settings.chunk_top_k]

    def _search_tables(self, query: str) -> list[TableEvidence]:
        hits = [hit for index in self.table_indices for hit in index.search(query, self.embedder, self.settings.table_top_k, self.settings.row_top_k)]
        return sorted(hits, key=lambda item: item.combined_score or 0.0, reverse=True)[:self.settings.row_top_k]

    @staticmethod
    def _chunk_metadata(hit: SourceChunk) -> dict[str, object]:
        return {"chunk_id": hit.chunk_id, "document_id": hit.document_id, "similarity": hit.similarity, "text": hit.text}


async def retrieve_evidence(request: RetrievalRequest, mechanism: RetrievalMechanism) -> EvidenceBundle:
    """Convenience function matching the public Retrieval Mech contract."""
    return await mechanism.retrieve_evidence(request)
