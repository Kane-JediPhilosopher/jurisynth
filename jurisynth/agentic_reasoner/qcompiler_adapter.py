"""Adapt QCompiler ASTs into Jurisynth dependency-scheduled leaf nodes.

This deliberately does not use QCompiler's RecursiveDescentProcessor: Jurisynth
owns retrieval, provenance, and concurrency.  The adapter only consumes the
public Node shape produced by QCompiler's Parser (``type``, ``value``, and
``children``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from jurisynth.agentic_reasoner.models import LeafNode


@dataclass(slots=True)
class QCompilerAdapter:
    """Convert a parsed QCompiler tree into deterministic Jurisynth leaves."""

    query_prefix: str = "q"
    _counter: int = field(default=0, init=False)
    _leaves: list[LeafNode] = field(default_factory=list, init=False)

    def adapt(self, root: Any, *, contextual_facts: tuple[str, ...] = ()) -> list[LeafNode]:
        self._counter = 0
        self._leaves = []
        self._walk(root, (), contextual_facts)
        return list(self._leaves)

    def _walk(
        self,
        node: Any,
        inherited_dependencies: tuple[str, ...],
        contextual_facts: tuple[str, ...],
    ) -> tuple[str, ...]:
        node_type = getattr(node, "type", None)
        if node_type == "AtomicQuery":
            query = getattr(node, "value", None)
            if not isinstance(query, str) or not query.strip():
                raise ValueError("QCompiler AtomicQuery must contain a non-empty string value.")
            self._counter += 1
            query_id = f"{self.query_prefix}{self._counter:03d}"
            placeholders = tuple(getattr(node, "placeholder", None) or ())
            self._leaves.append(
                LeafNode(
                    query_id=query_id,
                    query=query,
                    dependency_ids=inherited_dependencies,
                    contextual_facts=contextual_facts,
                    constraints={"qcompiler_placeholders": placeholders} if placeholders else {},
                )
            )
            return (query_id,)

        children = getattr(node, "children", None)
        if node_type not in {"ListQuery", "DependentQuery"}:
            raise ValueError(f"Unsupported QCompiler node type: {node_type!r}")
        if not isinstance(children, (list, tuple)) or not children:
            raise ValueError(f"QCompiler {node_type} requires one or more children.")

        if node_type == "ListQuery":
            terminals: list[str] = []
            for child in children:
                terminals.extend(self._walk(child, inherited_dependencies, contextual_facts))
            return tuple(terminals)

        if len(children) != 2:
            raise ValueError("QCompiler DependentQuery must have exactly two children.")
        left_terminals = self._walk(children[0], inherited_dependencies, contextual_facts)
        return self._walk(children[1], tuple(dict.fromkeys((*inherited_dependencies, *left_terminals))), contextual_facts)


def parse_and_adapt(expression: str, *, contextual_facts: tuple[str, ...] = ()) -> list[LeafNode]:
    """Parse a QCompiler expression with Jurisynth's pinned compatible parser."""
    from jurisynth.vendor.qcompiler_parser import Parser

    return QCompilerAdapter().adapt(Parser().parse_complex_query(expression), contextual_facts=contextual_facts)
