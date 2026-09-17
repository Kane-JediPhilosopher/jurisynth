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


def test_translator_retries_incomplete_expression_with_parser_feedback():
    import json
    class Model:
        calls = 0
        async def complete(self, **kwargs):
            self.calls += 1
            assert kwargs["max_tokens"] == 2048
            assert kwargs["response_schema"]["name"] == "qcompiler_ast"
            if self.calls == 1:
                return json.dumps({"expression": "(find the rule + explain the scope"})
            feedback = json.loads(kwargs["user"])
            assert "RPAREN" in feedback["validation_error"]
            return json.dumps({"expression": "find the rule * explain {rule}"})
    model = Model()
    result = asyncio.run(QCompilerTranslator(model).compile("complex question"))
    assert model.calls == 2
    assert result.attempts == 2
    assert result.leaves[1].dependency_ids == ("q001",)


def test_json_ast_compiles_grouped_dependencies_without_model_placeholders():
    import json
    payload = {"ast": {"type": "dependent", "left": {"type": "query", "query": "Identify regulated actors"},
                       "right": {"type": "parallel", "children": [
                           {"type": "query", "query": "Identify pre-market duties"},
                           {"type": "query", "query": "Identify post-market duties"}]}}}
    result = asyncio.run(QCompilerTranslator(FakeModel(json.dumps(payload))).compile("scenario"))
    assert len(result.leaves) == 3
    assert result.leaves[1].dependency_ids == ("q001",)
    assert result.leaves[2].dependency_ids == ("q001",)
    assert result.leaves[1].constraints["qcompiler_placeholders"] == ("upstream_result",)


def test_json_ast_rejects_unknown_fields_and_unbounded_or_invalid_nodes():
    import json
    for ast in [{"type": "query", "query": "", "extra": True},
                {"type": "parallel", "children": []},
                {"type": "query", "query": "A * B"}]:
        with pytest.raises(ValueError):
            asyncio.run(QCompilerTranslator(FakeModel(json.dumps({"ast": ast}))).compile("scenario"))


def test_nested_rhs_ast_preserves_inherited_dependency_edges():
    import json
    atom = lambda text: {"type": "query", "query": text}
    ast = {"type": "dependent", "left": atom("Identify the applicable law"),
           "right": {"type": "dependent", "left": atom("Identify regulated actors"),
                     "right": atom("Identify their obligations")}}
    result = asyncio.run(QCompilerTranslator(FakeModel(json.dumps({"ast": ast}))).compile("scenario"))
    assert result.leaves[1].dependency_ids == ("q001",)
    assert result.leaves[2].dependency_ids == ("q001", "q002")
