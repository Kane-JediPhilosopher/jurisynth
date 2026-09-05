"""Configuration kept separate from retrieval policy for evaluation tuning."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RetrievalSettings:
    chunk_top_k: int = 8
    table_top_k: int = 5
    row_top_k: int = 5
    similarity_threshold: float = 0.55
    internal_concurrency_limit: int = 4
    operation_timeout_seconds: float | None = 30.0

    def __post_init__(self) -> None:
        if min(self.chunk_top_k, self.table_top_k, self.row_top_k) < 1:
            raise ValueError("top-k settings must be positive")
        if self.internal_concurrency_limit < 1:
            raise ValueError("internal_concurrency_limit must be positive")
        if self.operation_timeout_seconds is not None and self.operation_timeout_seconds <= 0:
            raise ValueError("operation_timeout_seconds must be positive or None")
