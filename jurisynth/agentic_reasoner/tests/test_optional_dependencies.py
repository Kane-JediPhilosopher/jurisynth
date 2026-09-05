import asyncio

from jurisynth.agentic_reasoner.models import LeafNode, NodeStatus
from jurisynth.agentic_reasoner.scheduler import execute_dependency_plan


def test_failed_optional_dependency_does_not_block_leaf_execution():
    nodes = [LeafNode("q1", "fails"), LeafNode("q2", "continues", optional_dependency_ids=("q1",))]

    async def execute(node, answers):
        if node.query_id == "q1":
            raise RuntimeError("failure")
        return "answer"

    results = asyncio.run(execute_dependency_plan(nodes, execute))
    assert results["q1"].status == NodeStatus.FAILED
    assert results["q2"].status == NodeStatus.COMPLETE
