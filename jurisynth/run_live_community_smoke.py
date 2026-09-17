"""Bounded live-NIM smoke test for non-authoritative community orientation."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from jurisynth.agentic_reasoner.llm import NIMConfig, OpenAICompatibleNIM
from jurisynth.contracts import RetrievalRequest
from jurisynth.retrieval_mech.community_hierarchy import CommunityHierarchy, CommunityNode, CommunityOrientationBuilder
from jurisynth.retrieval_mech.community_summary import CommunitySummaryInput, LazyCommunitySummarizer
from jurisynth.retrieval_mech.mechanism import RetrievalMechanism
from jurisynth.retrieval_mech.rdf_retriever import StructuredRetrievalResult


class StaticCommunityRetriever:
    """Supplies a deterministic dispersed selection without graph evidence."""

    async def retrieve(self, _request: RetrievalRequest) -> StructuredRetrievalResult:
        return StructuredRetrievalResult(metadata={
            "orientation_communities": [
                {"community_id": "left", "source": "seed"},
                {"community_id": "right", "source": "seed"},
                {"community_id": "root", "source": "shared_lca"},
            ],
        })


async def run(timeout_seconds: float) -> dict[str, object]:
    hierarchy = CommunityHierarchy(
        {
            "left": CommunityNode("left", 0, "root", member_ids=("controller",)),
            "right": CommunityNode("right", 0, "root", member_ids=("consumer",)),
            "root": CommunityNode("root", 1, child_ids=("left", "right")),
        },
        "live-smoke-fixture-v1",
    )
    model = OpenAICompatibleNIM(NIMConfig.from_environment())
    try:
        mechanism = RetrievalMechanism(
            embedder=object(),
            structured_retriever=StaticCommunityRetriever(),
            community_orientation_builder=CommunityOrientationBuilder(
                hierarchy, {"controller": "data controller", "consumer": "consumer rights"},
            ),
            community_descriptors={
                "left": CommunitySummaryInput("left", "A graph region anchored by data-controller concepts.", 0),
                "right": CommunitySummaryInput("right", "A graph region anchored by consumer-rights concepts.", 0),
            },
            community_summarizer=LazyCommunitySummarizer(model),
            community_summary_min_average_distance=1.0,
        )
        bundle = await asyncio.wait_for(
            mechanism.retrieve_evidence(RetrievalRequest("live_community", "Provide orientation for these graph regions.")),
            timeout=timeout_seconds,
        )
    finally:
        await model.aclose()
    if not bundle.community_summary or "not legal evidence" not in bundle.community_summary:
        raise RuntimeError("Live community smoke did not return a labelled non-authoritative orientation.")
    lazy = bundle.retrieval_metadata.get("lazy_community_summary")
    if not isinstance(lazy, dict) or lazy.get("source") != "persisted_deterministic_orientation_descriptors":
        raise RuntimeError("Live community smoke did not preserve descriptor-only provenance.")
    return {
        "status": "success",
        "community_summary": bundle.community_summary[:2_000],
        "lazy_community_summary": lazy,
        "orientation": bundle.retrieval_metadata.get("community_orientation"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout-seconds", type=float, default=180.0)
    parser.add_argument("--output", type=Path, default=Path("jurisynth/run_outputs/live_community_smoke.json"))
    args = parser.parse_args()
    if args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be positive")
    payload = asyncio.run(run(args.timeout_seconds))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "status": payload["status"]}))


if __name__ == "__main__":
    main()
