"""Small parser compatible with QCompiler's public query-expression grammar.

Compatibility target: QCompiler commit a6a45021a8eab5435c8d5138929f34b1f1ea3133
(MIT License, https://github.com/YuyaoZhangQAQ/QCompiler).  This module is a
minimal Jurisynth implementation of the documented/public AST grammar only;
it deliberately excludes QCompiler's translator and recursive executor.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(slots=True)
class Node:
    type: str
    value: str | None = None
    children: list["Node"] | None = None
    placeholder: list[str] | None = None
    is_grouped: bool = False


class Parser:
    """Parse ``AtomicQuery``, ``DependentQuery`` (``*``), and ``ListQuery`` (``+``)."""

    def parse_complex_query(self, expression: str) -> Node:
        if not isinstance(expression, str) or not expression.strip():
            raise ValueError("QCompiler expression must be a non-empty string.")
        self._tokens = self._tokenize(self._protect_query_parentheses(expression))
        self._position = 0
        root = self._parse_list()
        if self._current()[0] != "EOF":
            raise ValueError(f"Unexpected token {self._current()[1]!r} in QCompiler expression.")
        return root

    @staticmethod
    def _protect_query_parentheses(expression: str) -> str:
        """Match QCompiler's convention: nested non-operator parentheses are query text."""
        pattern = re.compile(r"\(([^()+*]*)\)")
        while True:
            expression, replacements = pattern.subn(r"[\1]", expression)
            if replacements == 0:
                return expression

    @staticmethod
    def _tokenize(expression: str) -> list[tuple[str, str | None]]:
        tokens: list[tuple[str, str | None]] = []
        position = 0
        while position < len(expression):
            char = expression[position]
            if char.isspace():
                position += 1
            elif char == "+":
                tokens.append(("PLUS", char)); position += 1
            elif char == "*":
                tokens.append(("TIMES", char)); position += 1
            elif char == "(":
                tokens.append(("LPAREN", char)); position += 1
            elif char == ")":
                tokens.append(("RPAREN", char)); position += 1
            else:
                end = position
                while end < len(expression) and not expression[end].isspace() and expression[end] not in "+*()":
                    end += 1
                tokens.append(("WORD", expression[position:end]))
                position = end
        return [*tokens, ("EOF", None)]

    def _current(self) -> tuple[str, str | None]:
        return self._tokens[self._position]

    def _consume(self, kind: str) -> None:
        if self._current()[0] != kind:
            raise ValueError(f"Expected {kind}, found {self._current()!r}.")
        self._position += 1

    def _parse_list(self) -> Node:
        children = [self._parse_dependency()]
        while self._current()[0] == "PLUS":
            self._consume("PLUS")
            children.append(self._parse_dependency())
        return Node("ListQuery", " + ".join(child.value or "" for child in children), children)

    def _parse_dependency(self) -> Node:
        node = self._parse_atomic()
        while self._current()[0] == "TIMES":
            self._consume("TIMES")
            right = self._parse_atomic()
            node = Node("DependentQuery", f"{node.value} * {right.value}", [node, right])
        return node

    def _parse_atomic(self) -> Node:
        if self._current()[0] == "LPAREN":
            self._consume("LPAREN")
            node = self._parse_list()
            self._consume("RPAREN")
            node.value = f"({node.value})"
            node.is_grouped = True
            return node
        words: list[str] = []
        while self._current()[0] == "WORD":
            words.append(str(self._current()[1]))
            self._consume("WORD")
        if not words:
            raise ValueError(f"Expected an atomic query, found {self._current()!r}.")
        value = " ".join(words).replace("[", "(").replace("]", ")")
        return Node("AtomicQuery", value, placeholder=re.findall(r"\{(.*?)\}", value))
