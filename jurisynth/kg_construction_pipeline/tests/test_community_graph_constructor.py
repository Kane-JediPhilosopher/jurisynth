"""Fast unit tests plus an opt-in batch_0009 Community Graph smoke test."""

from pathlib import Path
import os
import sys

import pytest
from rdflib import Dataset, Literal, Namespace, RDF


PIPELINE_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PIPELINE_SRC) not in sys.path:
    sys.path.insert(0, str(PIPELINE_SRC))

from community_graph_constructor import (
    CHUNK,
    JS_SOURCE,
    build_entity_graph,
    build_graph_communities,
    construct_communities,
    extract_entities_and_relations,
    extract_semantic_triples,
    hierarchical_leiden,
)


EX = Namespace("http://example.org/")
PROJECT_ROOT = Path(__file__).resolve().parents[3]
BATCH_0009_GRAPH = (
    PROJECT_ROOT
    / "jurisynth/kg_construction_pipeline/output/batch_0009/graph/jurisynth_graph.nq"
)


def make_dataset():
    dataset = Dataset()
    chunk = dataset.graph(CHUNK["doc_1_chunk_1"])
    chunk.add((EX.alice, EX.knows, EX.bob))
    chunk.add((EX.alice, EX.age, Literal(42)))
    # Provenance-like triples are intentionally outside chunk graphs.
    provenance = dataset.graph(JS_SOURCE.Assertions)
    provenance.add((EX.assertion_1, JS_SOURCE.subject, EX.alice))
    return dataset


def test_semantic_extraction_uses_chunk_graphs_only():
    triples = extract_semantic_triples(make_dataset())
    assert (EX.alice, EX.knows, EX.bob) in triples
    assert all(subject != EX.assertion_1 for subject, _, _ in triples)


def test_entity_and_relation_extraction_excludes_literals():
    entities, relations = extract_entities_and_relations(make_dataset())
    assert entities == {EX.alice, EX.bob}
    assert relations == {EX.knows}


def test_entity_graph_deduplicates_repeated_semantic_triples():
    dataset = make_dataset()
    dataset.graph(CHUNK["doc_1_chunk_2"]).add((EX.alice, EX.knows, EX.bob))
    graph = build_entity_graph(dataset)
    assert graph.vcount() == 2
    assert graph.ecount() == 1
    assert graph.es[0]["predicate"] == EX.knows


def test_hierarchy_is_deterministic_and_serializable():
    hierarchy_a, graph = build_graph_communities(
        make_dataset(), max_levels=2, resolution=1.0
    )
    hierarchy_b = hierarchical_leiden(graph, max_levels=2, resolution=1.0, seed=42)
    assert hierarchy_a == hierarchy_b

    _, _, enriched = construct_communities(make_dataset(), max_levels=2)
    community_graph = enriched.graph(JS_SOURCE.community)
    assert any(community_graph.triples((None, RDF.type, JS_SOURCE.Community)))


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("JURISYNTH_RUN_INTEGRATION") != "1",
    reason="Set JURISYNTH_RUN_INTEGRATION=1 to parse and construct communities for batch_0009.",
)
def test_batch_0009_graph_constructs_communities():
    assert BATCH_0009_GRAPH.exists(), "batch_0009 graph output is required for this smoke test"
    dataset = Dataset().parse(BATCH_0009_GRAPH, format="nquads")
    hierarchy, entity_graph, enriched = construct_communities(dataset, max_levels=2)
    assert entity_graph.vcount() > 0
    assert hierarchy
    assert any(enriched.graph(JS_SOURCE.community).triples((None, RDF.type, JS_SOURCE.Community)))
