"""Small RDF-query boundary supporting in-memory RDFLib and disk-backed Oxigraph.

RDFLib remains the construction and pilot backend.  The global retrieval path
uses :class:`OxigraphQuadStore`, which opens an already-built RocksDB store in
read-only mode and never materialises the N-Quads file as Python objects.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


QuadRow = tuple[str, str, str, str]


class QuadStore(Protocol):
    """Only the bounded operations needed by DirectRDFRetriever."""

    def matching_quads(
        self, entities: set[str], relations: set[str], *, max_per_seed: int | None,
    ) -> Iterator[QuadRow]: ...

    def matching_subject_predicate_quads(
        self, subject: str, predicate: str, *, limit: int | None,
    ) -> Iterator[QuadRow]: ...

    def select_rows(self, query: str) -> Iterable[QuadRow]: ...


def _term_text(value: object) -> str:
    """Normalize RDFLib/PyOxigraph named nodes to their raw URI strings."""
    raw = getattr(value, "value", value)
    return str(raw)


@dataclass(slots=True)
class RDFLibQuadStore:
    """Compatibility adapter for existing pilot datasets and unit fixtures."""

    dataset: object

    def matching_quads(self, entities: set[str], relations: set[str], *, max_per_seed: int | None) -> Iterator[QuadRow]:
        from rdflib import URIRef

        seen: set[QuadRow] = set()
        patterns = [
            *((URIRef(entity), None, None, None) for entity in entities),
            *((None, None, URIRef(entity), None) for entity in entities),
            *((None, URIRef(relation), None, None) for relation in relations),
        ]
        for pattern in patterns:
            emitted = 0
            for subject, predicate, obj, graph in self.dataset.quads(pattern):
                graph_id = getattr(graph, "identifier", graph)
                row = (_term_text(subject), _term_text(predicate), _term_text(obj), _term_text(graph_id))
                if row in seen:
                    continue
                seen.add(row)
                yield row
                emitted += 1
                if max_per_seed is not None and emitted >= max_per_seed:
                    break

    def matching_subject_predicate_quads(
        self, subject: str, predicate: str, *, limit: int | None,
    ) -> Iterator[QuadRow]:
        from rdflib import URIRef

        emitted = 0
        for quad_subject, quad_predicate, obj, graph in self.dataset.quads(
            (URIRef(subject), URIRef(predicate), None, None)
        ):
            graph_id = getattr(graph, "identifier", graph)
            yield (
                _term_text(quad_subject), _term_text(quad_predicate),
                _term_text(obj), _term_text(graph_id),
            )
            emitted += 1
            if limit is not None and emitted >= limit:
                break

    def select_rows(self, query: str) -> Iterable[QuadRow]:
        for row in self.dataset.query(query):
            yield tuple(_term_text(getattr(row, name)) for name in ("s", "p", "o", "g"))  # type: ignore[misc]


@dataclass(slots=True)
class OxigraphQuadStore:
    """Read-only embedded Oxigraph store for consumer-device global retrieval."""

    store: object

    @classmethod
    def open_read_only(cls, path: str | Path) -> "OxigraphQuadStore":
        try:
            from pyoxigraph import Store
        except ModuleNotFoundError as exc:
            raise RuntimeError("Install pyoxigraph to use disk-backed global RDF retrieval.") from exc
        return cls(Store.read_only(str(path)))

    def matching_quads(self, entities: set[str], relations: set[str], *, max_per_seed: int | None) -> Iterator[QuadRow]:
        try:
            from pyoxigraph import NamedNode
        except ModuleNotFoundError as exc:  # pragma: no cover - guarded at open time
            raise RuntimeError("Install pyoxigraph to use disk-backed global RDF retrieval.") from exc

        seen: set[QuadRow] = set()
        patterns = [
            *((NamedNode(entity), None, None, None) for entity in entities),
            *((None, None, NamedNode(entity), None) for entity in entities),
            *((None, NamedNode(relation), None, None) for relation in relations),
        ]
        for pattern in patterns:
            emitted = 0
            for quad in self.store.quads_for_pattern(*pattern):
                row = (
                    _term_text(quad.subject), _term_text(quad.predicate),
                    _term_text(quad.object), _term_text(quad.graph_name),
                )
                if row in seen:
                    continue
                seen.add(row)
                yield row
                emitted += 1
                if max_per_seed is not None and emitted >= max_per_seed:
                    break

    def matching_subject_predicate_quads(
        self, subject: str, predicate: str, *, limit: int | None,
    ) -> Iterator[QuadRow]:
        try:
            from pyoxigraph import NamedNode
        except ModuleNotFoundError as exc:  # pragma: no cover - guarded at open time
            raise RuntimeError("Install pyoxigraph to use disk-backed global RDF retrieval.") from exc

        emitted = 0
        for quad in self.store.quads_for_pattern(
            NamedNode(subject), NamedNode(predicate), None, None,
        ):
            yield (
                _term_text(quad.subject), _term_text(quad.predicate),
                _term_text(quad.object), _term_text(quad.graph_name),
            )
            emitted += 1
            if limit is not None and emitted >= limit:
                break

    def select_rows(self, query: str) -> Iterable[QuadRow]:
        rows = self.store.query(query)
        for row in rows:
            yield tuple(_term_text(row[name]) for name in ("s", "p", "o", "g"))  # type: ignore[index,misc]


def is_iri(value: str) -> bool:
    """Recognise URI-like RDF terms without accepting literals as path vertices."""
    return value.startswith(("http://", "https://", "urn:"))
