import asyncio

import pytest

from jurisynth.agentic_reasoner.models import LeafNode, NodeStatus
from jurisynth.agentic_reasoner.scheduler import execute_dependency_plan


def test_dependent_starts_when_its_upstream_finishes_not_after_unrelated_leaf():
    nodes = [
        LeafNode("q001", "fast prerequisite"),
        LeafNode("q002", "dependent", dependency_ids=("q001",)),
        LeafNode("q003", "unrelated slow leaf"),
    ]

    async def scenario():
        slow_release = asyncio.Event()
        dependent_started = asyncio.Event()

        async def execute(node, _answers):
            if node.query_id == "q003":
                await slow_release.wait()
            elif node.query_id == "q002":
                dependent_started.set()
                slow_release.set()
            return node.query_id

        results = await asyncio.wait_for(
            execute_dependency_plan(nodes, execute, max_concurrency=3),
            timeout=1,
        )
        return dependent_started.is_set(), results

    started, results = asyncio.run(scenario())
    assert started
    assert all(result.status == NodeStatus.COMPLETE for result in results.values())


def test_scheduler_rejects_dependency_cycles_deterministically():
    nodes = [
        LeafNode("q001", "first", dependency_ids=("q002",)),
        LeafNode("q002", "second", dependency_ids=("q001",)),
    ]

    async def execute(_node, _answers):
        raise AssertionError("cycle must fail before execution")

    with pytest.raises(ValueError, match="Dependency cycle"):
        asyncio.run(execute_dependency_plan(nodes, execute))
