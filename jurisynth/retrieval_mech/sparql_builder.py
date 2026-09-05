"""Deterministic, bounded SPARQL templates for RDF retrieval.

This module deliberately accepts only URI candidates produced by the E-R matcher;
no LLM-generated SPARQL is accepted anywhere in the public API.
"""

from __future__ import annotations

from rdflib import URIRef


class SparqlQueryBuilder:
    def direct(self, *, entities: set[str], relations: set[str], limit: int) -> str:
        if limit < 1:
            raise ValueError("limit must be positive")
        if not entities and not relations:
            return "SELECT ?s ?p ?o ?g WHERE { FILTER(false) } LIMIT 0"
        clauses: list[str] = []
        if entities:
            values = _values(entities)
            clauses.append(f"{{ VALUES ?entity {{ {values} }} GRAPH ?g {{ {{ BIND(?entity AS ?s) ?s ?p ?o }} UNION {{ ?s ?p ?entity BIND(?entity AS ?o) }} }} }}")
        if relations:
            values = _values(relations)
            clauses.append(f"{{ VALUES ?p {{ {values} }} GRAPH ?g {{ ?s ?p ?o }} }}")
        return f"SELECT DISTINCT ?s ?p ?o ?g WHERE {{ {' UNION '.join(clauses)} }} LIMIT {limit}"

    def bounded_path(self, *, entities: set[str], max_hops: int, limit: int) -> str:
        if max_hops not in {2, 3}:
            raise ValueError("max_hops must be 2 or 3")
        if limit < 1:
            raise ValueError("limit must be positive")
        if len(entities) < 2:
            return "SELECT ?s ?p ?o ?g WHERE { FILTER(false) } LIMIT 0"
        values = _values(entities)
        nodes = ["?start", *(f"?n{index}" for index in range(1, max_hops)), "?end"]
        patterns = " ".join(
            f"{nodes[index]} ?p{index + 1} {nodes[index + 1]} ."
            for index in range(max_hops)
        )
        return (
            "SELECT DISTINCT ?start ?end ?g WHERE { "
            f"VALUES ?start {{ {values} }} VALUES ?end {{ {values} }} "
            f"FILTER(?start != ?end) GRAPH ?g {{ {patterns} }} "
            f"}} LIMIT {limit}"
        )


def _values(uris: set[str]) -> str:
    return " ".join(URIRef(uri).n3() for uri in sorted(uris))
