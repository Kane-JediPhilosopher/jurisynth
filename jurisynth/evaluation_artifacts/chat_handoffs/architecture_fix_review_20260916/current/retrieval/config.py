"""Configuration kept separate from retrieval policy for evaluation tuning."""

from __future__ import annotations

from dataclasses import dataclass


# Global Oxigraph retrieval must bound candidate graph scans before evidence
# selection. This limits work per matched E-R seed; it does not cap community
# selection or discard the top-level evidence budget.
GLOBAL_MAX_QUADS_PER_SEED = 50


@dataclass(frozen=True, slots=True)
class RetrievalSettings:
    chunk_top_k: int = 8
    table_top_k: int = 5
    row_top_k: int = 5
    image_expansion_top_k: int = 2
    similarity_threshold: float = 0.55
    internal_concurrency_limit: int = 4
    # Retrieval combines local FAISS work, RDF traversal, and optional live
    # providers.  Do not silently discard otherwise valid evidence merely
    # because a large corpus traversal exceeds an arbitrary wall-clock limit.
    # Callers that need a bounded interactive request can still opt in by
    # supplying a positive value.
    operation_timeout_seconds: float | None = None

    def __post_init__(self) -> None:
        if min(self.chunk_top_k, self.table_top_k, self.row_top_k, self.image_expansion_top_k) < 1:
            raise ValueError("top-k settings must be positive")
        if self.internal_concurrency_limit < 1:
            raise ValueError("internal_concurrency_limit must be positive")
        if self.operation_timeout_seconds is not None and self.operation_timeout_seconds <= 0:
            raise ValueError("operation_timeout_seconds must be positive or None")
