from pathlib import Path
from importlib.util import find_spec

import pytest
from rdflib import Dataset, Literal, Namespace

from jurisynth.retrieval_mech.er_index_builder import (
    build_er_indices,
    build_resource_records,
    save_er_indices,
)
from jurisynth.retrieval_mech.er_matcher import Concept, ERMatcher, PersistedERIndices


EX = Namespace("http://example.org/")
CHUNK = Namespace("http://jurisynth/source/chunk/")


class FakeEmbedder:
    def encode(self, texts, **_kwargs):
        return [[float(index + 1), 1.0] for index, _ in enumerate(texts)]


def make_dataset():
    dataset = Dataset()
    graph = dataset.graph(CHUNK["doc_1_chunk_1"])
    graph.add((EX.alice, EX.knows, EX.bob))
    graph.add((EX.alice, EX.knows, EX.bob))
    return dataset


def hierarchy():
    return {0: {0: {"uri": EX.community_0, "members": [EX.alice, EX.bob]}}}


def test_records_are_stable_and_keep_direct_community_membership():
    entities, relations = build_resource_records(make_dataset(), hierarchy())
    assert [record.uri for record in entities] == [str(EX.alice), str(EX.bob)]
    assert relations[0].uri == str(EX.knows)
    assert entities[0].community_ids == (str(EX.community_0),)
    assert relations[0].community_ids == (str(EX.community_0),)


def test_literals_do_not_create_entity_or_relation_records():
    dataset = Dataset()
    dataset.graph(CHUNK["doc_1_chunk_1"]).add((EX.alice, EX.age, Literal(42)))
    assert build_resource_records(dataset, hierarchy()) == ([], [])


@pytest.mark.skipif(find_spec("faiss") is None, reason="faiss-cpu is required")
def test_indices_and_persistence_keep_metadata_in_sync(tmp_path: Path):
    artifacts = build_er_indices(make_dataset(), hierarchy(), FakeEmbedder())
    assert artifacts.entity_index.ntotal == len(artifacts.entity_records) == 2
    assert artifacts.relation_index.ntotal == len(artifacts.relation_records) == 1
    save_er_indices(artifacts, tmp_path, manifest={"source": "test"})
    assert (tmp_path / "entity.index").exists()
    assert (tmp_path / "relation.index").exists()
    assert (tmp_path / "metadata.json").exists()


@pytest.mark.skipif(find_spec("faiss") is None, reason="faiss-cpu is required")
def test_query_matches_keep_scores_and_are_grouped_by_concept():
    artifacts = build_er_indices(make_dataset(), hierarchy(), FakeEmbedder())
    matcher = ERMatcher(
        PersistedERIndices(
            artifacts.entity_index,
            artifacts.relation_index,
            artifacts.entity_records,
            artifacts.relation_records,
        ),
        FakeEmbedder(),
    )

    matches = matcher.match([Concept("entity_a", "alice"), Concept("entity_b", "bob")], [])

    assert {match.concept_id for match in matches.entity_matches} == {"entity_a", "entity_b"}
    assert all(isinstance(match.similarity, float) for match in matches.entity_matches)


@pytest.mark.skipif(find_spec("faiss") is None, reason="faiss-cpu is required")
def test_exact_entity_label_takes_precedence_over_semantic_country_neighbours():
    artifacts = build_er_indices(make_dataset(), hierarchy(), FakeEmbedder())
    matcher = ERMatcher(
        PersistedERIndices(
            artifacts.entity_index,
            artifacts.relation_index,
            artifacts.entity_records,
            artifacts.relation_records,
        ),
        FakeEmbedder(),
    )

    # `alice` is a lexical entity lookup. It must not be diluted by the
    # embedding index's adjacent resources merely because they are top-k hits.
    matches = matcher.match([Concept("entity_1", "alice")], [], entity_top_k=5)

    assert [(match.label, match.similarity) for match in matches.entity_matches] == [("alice", 1.0)]
