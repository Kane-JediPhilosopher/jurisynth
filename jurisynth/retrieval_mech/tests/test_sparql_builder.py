import pytest

from jurisynth.retrieval_mech.sparql_builder import SparqlQueryBuilder


def test_direct_template_uses_values_and_bounded_limit_without_arbitrary_input():
    query = SparqlQueryBuilder().direct(
        entities={"https://example.test/controller"},
        relations={"https://example.test/must-provide"},
        limit=20,
    )
    assert "VALUES ?entity" in query and "VALUES ?p" in query
    assert "LIMIT 20" in query and "controller" in query


def test_path_template_only_allows_specified_hop_bounds():
    query = SparqlQueryBuilder().bounded_path(
        entities={"https://example.test/a", "https://example.test/b"}, max_hops=3, limit=5
    )
    assert "?start ?p1 ?n1" in query and "?n2 ?p3 ?end" in query
    with pytest.raises(ValueError):
        SparqlQueryBuilder().bounded_path(entities={"https://example.test/a", "https://example.test/b"}, max_hops=4, limit=5)
