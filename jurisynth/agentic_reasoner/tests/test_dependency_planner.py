import asyncio

import pytest

from jurisynth.agentic_reasoner.dependency_planner import SemanticDependencyPlanner
from jurisynth.agentic_reasoner.models import LeafNode


class Model:
    def __init__(self, response): self.response = response
    async def complete(self, **kwargs): return self.response


def test_semantic_planner_can_remove_a_qcompiler_structural_dependency():
    leaves = (LeafNode("q001", "identify directive"), LeafNode("q002", "independent remedy", ("q001",)))
    planned = asyncio.run(SemanticDependencyPlanner(Model('{"dependencies":{"q001":[],"q002":[]}}')).plan(leaves))
    assert planned[1].dependency_ids == ()


def test_semantic_planner_rejects_unknown_or_self_dependency():
    leaves = (LeafNode("q001", "question"),)
    with pytest.raises(ValueError, match="invalid dependency"):
        asyncio.run(SemanticDependencyPlanner(Model('{"dependencies":{"q001":["q001"]}}')).plan(leaves))
