"""Lossless URI components for source-local Jurisynth resources.

Source document IDs frequently contain dotted OJ page identifiers.  Treating
their final dotted segment as a file extension merged separate documents.
Percent encoding retains the complete original ID while a slash separates
scoped components unambiguously.
"""

from __future__ import annotations

from urllib.parse import quote, unquote


def encode_component(value: object) -> str:
    """Encode one identifier without lowercasing or removing any suffix."""
    text = str(value)
    if not text:
        raise ValueError("A source URI component cannot be empty")
    return quote(text, safe="")


def scoped_fragment(*values: object) -> str:
    """Encode an ordered identifier tuple without separator ambiguity."""
    if not values:
        raise ValueError("A scoped source URI needs at least one component")
    return "/".join(encode_component(value) for value in values)


def decode_fragment(fragment: str) -> tuple[str, ...]:
    """Recover original components from a fragment produced above."""
    return tuple(unquote(part) for part in fragment.split("/"))
