import asyncio

from jurisynth.retrieval_mech.community_summary import CommunitySummaryInput, LazyCommunitySummarizer


class Model:
    def __init__(self): self.users = []
    async def complete(self, **kwargs): self.users.append(kwargs["user"]); return f"Orientation {len(self.users)}."


def test_lazy_summary_is_bounded_and_returns_none_without_community_summaries():
    model = Model()
    summarizer = LazyCommunitySummarizer(model, max_child_summaries=1, max_summary_characters=4)
    assert asyncio.run(summarizer.summarize("community", [])) is None
    result = asyncio.run(summarizer.summarize("community", [CommunitySummaryInput("child", "abcdef")]))
    assert result == "Orientation 1."
    assert "abcd" in model.users[0] and "abcdef" not in model.users[0]


def test_large_leaf_selection_uses_summary_of_summaries_without_raw_evidence():
    model = Model()
    summarizer = LazyCommunitySummarizer(model, max_child_summaries=5, max_summaries_per_batch=2, max_batches=3)
    inputs = [CommunitySummaryInput(f"c{index}", f"summary {index}", branch_distance=index) for index in range(5)]
    result = asyncio.run(summarizer.summarize("parent", inputs))
    assert result == "Orientation 4."
    assert len(model.users) == 4
    assert '"stage": "merge"' in model.users[-1]
