"""LLM-backed, parser-validated QCompiler expression translation."""

from __future__ import annotations

from dataclasses import dataclass
import json

from jurisynth.agentic_reasoner.llm import ChatModel
from jurisynth.agentic_reasoner.qcompiler_adapter import parse_and_adapt
from jurisynth.agentic_reasoner.schemas import QCOMPILER_AST_SCHEMA
from jurisynth.vendor.qcompiler_parser import Node, Parser


_SYSTEM_PROMPT = """Compile the user's question into a QCompiler-compatible JSON AST.
Return exactly {"ast": NODE}. NODE is one of:
{"type":"query","query":"one factual question"},
{"type":"parallel","children":[NODE,NODE]},
{"type":"dependent","left":NODE,"right":NODE}.
Use dependent only when answering right requires the answer to left, not merely
for related topics or narrative order. The adapter inserts a reference to the
upstream result for dependent queries; you need not invent placeholder syntax.
Do not include '+' or '*' operators or braced placeholders in query text.
Retain the user's distinct questions, relevant scenario facts, temporal scope
and uncertainty. Return JSON only, without explanations or answers.

Most related legal issues can be retrieved independently and should use parallel.
Use dependent only for an explicit information-flow need, such as first resolving
an ambiguous instrument reference and then querying that resolved instrument.
For a sequence of three dependent steps, prefer dependent(dependent(A,B),C).
The adapter preserves explicitly nested dependency edges."""


@dataclass(frozen=True, slots=True)
class QCompilerCompilation:
    expression: str
    leaves: tuple[object, ...]
    ast: dict[str, object]
    attempts: int = 1


@dataclass(slots=True)
class QCompilerTranslator:
    model: ChatModel
    max_tokens: int = 2048
    invalid_output_attempts: int = 2

    async def compile(self, query: str, *, contextual_facts: tuple[str, ...] = ()) -> QCompilerCompilation:
        if not query.strip():
            raise ValueError("Cannot compile an empty user query.")
        if min(self.max_tokens, self.invalid_output_attempts) < 1:
            raise ValueError("QCompiler output and validation budgets must be positive.")
        request = f"question = {query}"
        for attempt in range(1, self.invalid_output_attempts + 1):
            response = await self.model.complete(system=_SYSTEM_PROMPT, user=request, max_tokens=self.max_tokens, response_schema=QCOMPILER_AST_SCHEMA)
            try:
                return self._parse_response(response, contextual_facts, attempt)
            except ValueError as exc:
                if attempt == self.invalid_output_attempts:
                    raise
                request = json.dumps({"question": query, "validation_error": str(exc), "instruction": "Return a complete schema-valid JSON AST using query, parallel and dependent nodes. No expression field or operator syntax."})
        raise RuntimeError("QCompiler validation loop did not return a compilation.")

    @staticmethod
    def _parse_response(response: str, contextual_facts: tuple[str, ...], attempt: int) -> QCompilerCompilation:
        try:
            payload = json.loads(response)
            if isinstance(payload, dict) and set(payload) == {"ast"}:
                expression = _ast_expression(payload["ast"])
            else:
                # Preserve legacy persisted expressions and offline fixtures.
                expression = payload.get("expression") if isinstance(payload, dict) else None
        except json.JSONDecodeError:
            # Legacy offline parser fixtures and a previously persisted QCompiler
            # run store only the expression. Live NIM calls always request the
            # strict QCOMPILER_SCHEMA above.
            expression = response
        if not isinstance(expression, str) or not expression.strip():
            raise ValueError("QCompiler translator response requires a non-empty expression.")
        expression = expression.strip()
        tree = Parser().parse_complex_query(expression)
        _validate_qcompiler_tree(tree)
        leaves = tuple(parse_and_adapt(expression, contextual_facts=contextual_facts))
        return QCompilerCompilation(expression, leaves, _serialize_tree(tree), attempts=attempt)


def _ast_expression(node: object, dependent: bool = False, depth: int = 0) -> str:
    """Deterministically compile schema nodes; never repair model-chosen edges."""
    if depth > 24 or not isinstance(node, dict):
        raise ValueError("QCompiler AST must contain bounded object nodes.")
    kind = node.get("type")
    if kind == "query" and set(node) == {"type", "query"}:
        query = node["query"]
        if not isinstance(query, str) or not query.strip() or any(char in query for char in "+*{}"):
            raise ValueError("AST query must be nonempty text without expression operators/placeholders.")
        # This is an explicit input reference, not an inferred legal answer.
        return ("Using {upstream_result}, " if dependent else "") + query.strip()
    if kind == "parallel" and set(node) == {"type", "children"}:
        children = node["children"]
        if not isinstance(children, list) or not 2 <= len(children) <= 32:
            raise ValueError("Parallel AST requires 2–32 children.")
        return "(" + " + ".join(_ast_expression(child, dependent, depth + 1) for child in children) + ")"
    if kind == "dependent" and set(node) == {"type", "left", "right"}:
        return "(" + _ast_expression(node["left"], dependent, depth + 1) + " * " + _ast_expression(node["right"], True, depth + 1) + ")"
    raise ValueError("Invalid QCompiler AST node fields or type.")


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
        _validate_qcompiler_tree(node.children[0], dependent_position)
        _validate_qcompiler_tree(node.children[1], True)
        return
    raise ValueError("Malformed QCompiler AST.")
