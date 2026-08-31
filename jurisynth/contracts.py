"""Stable component contracts shared by the Reasoner and Retrieval Mech."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


RetrievalStatus = Literal["success", "weak", "empty", "error"]


@dataclass(slots=True)
class RetrievalRequest:
    """One dependency-ready AST leaf request; never an entire conversation."""

    query_id: str
    leaf_query: str
    contextual_facts: list[str] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)
    dependency_claims: list[dict[str, Any]] = field(default_factory=list)
    retrieval_config: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.query_id.strip():
            raise ValueError("query_id must not be empty")
        if not self.leaf_query.strip():
            raise ValueError("leaf_query must not be empty")


@dataclass(slots=True)
class SourceChunk:
    chunk_id: str
    document_id: str
    text: str
    similarity: float | None = None


@dataclass(slots=True)
class Assertion:
    subject: str
    predicate: str
    object: str


@dataclass(slots=True)
class EvidenceItem:
    evidence_id: str
    assertion: Assertion
    source_chunks: list[SourceChunk]
    modifiers: list[dict[str, Any]] = field(default_factory=list)
    retrieval_origins: list[str] = field(default_factory=list)
    community_ids: list[str] = field(default_factory=list)
    relevance_score: float | None = None
    structural_score: float | None = None
    coherence_score: float | None = None


@dataclass(slots=True)
class TableEvidence:
    table_id: str
    document_id: str
    headers: list[str] | None
    matched_rows: list[list[str]]
    row_ids: list[int]
    table_score: float | None = None
    row_score: float | None = None
    combined_score: float | None = None


@dataclass(slots=True)
class EvidenceBundle:
    query_id: str
    status: RetrievalStatus
    evidence_items: list[EvidenceItem] = field(default_factory=list)
    table_evidence: list[TableEvidence] = field(default_factory=list)
    community_summary: str | None = None
    retrieval_metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready representation for logs and downstream LLM calls."""
        return asdict(self)
