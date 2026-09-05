"""Lazy, non-authoritative community orientation summaries."""

from __future__ import annotations

import json
from dataclasses import dataclass

from jurisynth.agentic_reasoner.llm import ChatModel
from dataclasses import field


@dataclass(slots=True)
class LazyCommunitySummarizer:
    model: ChatModel
    max_child_summaries: int = 12
    max_summaries_per_batch: int = 4
    max_batches: int = 3
    max_summary_characters: int = 1_000
    max_tokens: int = 500

    async def summarize(self, community_id: str, child_summaries: list["CommunitySummaryInput"]) -> str | None:
        """Greedily merge persisted child/community summaries, never raw evidence."""
        if not community_id or not child_summaries:
            return None
        summaries = [item.to_payload(self.max_summary_characters) for item in child_summaries[:self.max_child_summaries]]
        batches = [summaries[index:index + self.max_summaries_per_batch] for index in range(0, len(summaries), self.max_summaries_per_batch)][:self.max_batches]
        batch_outputs = [await self._complete(community_id, batch, "batch") for batch in batches]
        return batch_outputs[0] if len(batch_outputs) == 1 else await self._complete(community_id, batch_outputs, "merge")

    async def _complete(self, community_id: str, summaries: list[object], stage: str) -> str | None:
        response = await self.model.complete(
            system="Merge supplied community summaries for orientation only. Preserve distinct regions when dispersion is high. Do not state legal conclusions, invent support, or replace underlying evidence.",
            user=json.dumps({"community_id": community_id, "stage": stage, "community_summaries": summaries}),
            max_tokens=self.max_tokens,
        )
        return response.strip() or None


@dataclass(frozen=True, slots=True)
class CommunitySummaryInput:
    community_id: str
    summary: str
    level: int | None = None
    branch_distance: int | None = None
    provenance: dict[str, object] = field(default_factory=dict)

    def to_payload(self, max_characters: int) -> dict[str, object]:
        return {
            "community_id": self.community_id,
            "summary": self.summary[:max_characters],
            "level": self.level,
            "branch_distance": self.branch_distance,
            "provenance": self.provenance,
        }
