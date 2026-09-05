import asyncio

import pytest

from jurisynth.agentic_reasoner.qcompiler_translator import QCompilerTranslator


class FakeModel:
    def __init__(self, expression):
        self.expression = expression

    async def complete(self, **kwargs):
        return self.expression


def test_translator_validates_and_adapts_a_dependent_expression():
    result = asyncio.run(QCompilerTranslator(FakeModel("find the Directive * what does {Directive} require")).compile("question"))
    assert result.expression.startswith("find")
    assert result.leaves[1].dependency_ids == ("q001",)
    dependent = result.ast["children"][0]
    assert dependent["type"] == "DependentQuery"
    assert dependent["children"][1]["query"] == "what does {Directive} require"


def test_translator_rejects_dependent_rhs_without_placeholder():
    with pytest.raises(ValueError, match="requires a placeholder"):
        asyncio.run(QCompilerTranslator(FakeModel("find the Directive * what does it require")).compile("question"))
