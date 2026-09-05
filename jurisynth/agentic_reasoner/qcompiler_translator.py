"""LLM-backed, parser-validated QCompiler expression translation."""

from __future__ import annotations

from dataclasses import dataclass

from jurisynth.agentic_reasoner.llm import ChatModel
from jurisynth.agentic_reasoner.qcompiler_adapter import parse_and_adapt
from jurisynth.vendor.qcompiler_parser import Node, Parser


_SYSTEM_PROMPT = """Compile the user's question into a QCompiler expression only.
Use atomic factual queries; '+' only for independent parallel queries; '*' only
when the right query depends on the left and contains a {placeholder}; use
parentheses only for grouping. Output no Markdown or explanation."""


@dataclass(frozen=True, slots=True)
class QCompilerCompilation:
    expression: str
    leaves: tuple[object, ...]
    ast: dict[str, object]


@dataclass(slots=True)
class QCompilerTranslator:
    model: ChatModel
    max_tokens: int = 500

    async def compile(self, query: str, *, contextual_facts: tuple[str, ...] = ()) -> QCompilerCompilation:
        if not query.strip():
            raise ValueError("Cannot compile an empty user query.")
        expression = (await self.model.complete(system=_SYSTEM_PROMPT, user=f"question = {query}", max_tokens=self.max_tokens)).strip()
        if expression.startswith("```"):
            expression = expression.strip("`").removeprefix("text").strip()
        tree = Parser().parse_complex_query(expression)
        _validate_qcompiler_tree(tree)
        leaves = tuple(parse_and_adapt(expression, contextual_facts=contextual_facts))
        return QCompilerCompilation(expression, leaves, _serialize_tree(tree))


def _serialize_tree(node: Node) -> dict[str, object]:
    """Retain validated intermediate QCompiler structure for final synthesis only."""
    value = getattr(node, "value", None)
    return {
        "type": node.type,
        **({"query": value} if isinstance(value, str) else {}),
        "children": [_serialize_tree(child) for child in (node.children or [])],
    }


def _validate_qcompiler_tree(node: Node, dependent_position: bool = False) -> None:
    if node.type == "AtomicQuery":
        placeholders = node.placeholder or []
        if dependent_position and not placeholders:
            raise ValueError("A dependent QCompiler right-hand query requires a placeholder.")
        if not dependent_position and placeholders:
            raise ValueError("An independent QCompiler query cannot contain a placeholder.")
        return
    if node.type == "ListQuery":
        for child in node.children or []:
            _validate_qcompiler_tree(child, dependent_position)
        return
    if node.type == "DependentQuery" and node.children and len(node.children) == 2:
        _validate_qcompiler_tree(node.children[0], False)
        _validate_qcompiler_tree(node.children[1], True)
        return
    raise ValueError("Malformed QCompiler AST.")
