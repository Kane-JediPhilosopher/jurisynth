from pathlib import Path
from importlib.util import find_spec

import pytest
from rdflib import Dataset, Literal, Namespace

from jurisynth.retrieval_mech.er_index_builder import (
    build_er_indices,
    build_resource_records,
    save_er_indices,
)
from jurisynth.retrieval_mech.er_matcher import Concept, ERMatcher, PersistedERIndices, _is_flat_index, _select_index_mode


EX = Namespace("http://example.org/")
CHUNK = Namespace("http://jurisynth/source/chunk/")


class FakeEmbedder:
    def encode(self, texts, **_kwargs):
        return [[float(index + 1), 1.0] for index, _ in enumerate(texts)]


def test_auto_index_mode_uses_mmap_only_when_memory_is_below_the_load_threshold():
    assert _select_index_mode("auto", 10.0, 6.0) == "memory"
    assert _select_index_mode("auto", 5.0, 6.0) == "mmap"
    assert _select_index_mode("auto", None, 6.0) == "memory"
    assert _select_index_mode("mmap", 10.0, 6.0) == "mmap"


def test_flat_index_header_is_detected_without_loading_the_vectors(tmp_path):
    flat = tmp_path / "flat.index"
    flat.write_bytes(b"IxFI" + b"rest")
    other = tmp_path / "other.index"
    other.write_bytes(b"IxIV" + b"rest")
    assert _is_flat_index(flat) is True
    assert _is_flat_index(other) is False


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
def test_index_building_embeds_records_in_bounded_batches():
    calls = []

    class RecordingEmbedder(FakeEmbedder):
        def encode(self, texts, **kwargs):
            calls.append((list(texts), kwargs["batch_size"]))
            return super().encode(texts, **kwargs)

    artifacts = build_er_indices(make_dataset(), hierarchy(), RecordingEmbedder(), batch_size=1)

    assert artifacts.entity_index.ntotal == 2
    assert all(len(texts) <= 1 and batch_size == 1 for texts, batch_size in calls)


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
    assert matches.metadata["entity"]["index_search_calls"] == 0
    assert matches.metadata["entity"]["exact_concept_count"] == 2


@pytest.mark.skipif(find_spec("faiss") is None, reason="faiss-cpu is required")
def test_unmatched_concepts_share_one_vector_index_search_without_reordering():
    artifacts = build_er_indices(make_dataset(), hierarchy(), FakeEmbedder())

    class CountingIndex:
        def __init__(self, wrapped):
            self.wrapped = wrapped
            self.ntotal = wrapped.ntotal
            self.calls = 0

        def search(self, vectors, top_k):
            self.calls += 1
            return self.wrapped.search(vectors, top_k)

    entity_index = CountingIndex(artifacts.entity_index)
    matcher = ERMatcher(
        PersistedERIndices(
            entity_index,
            artifacts.relation_index,
            artifacts.entity_records,
            artifacts.relation_records,
        ),
        FakeEmbedder(),
    )

    matches = matcher.match([
        Concept("entity_a", "unknown A", ("variant A",)),
        Concept("entity_b", "unknown B", ("variant B",)),
    ], [])

    assert entity_index.calls == 1
    assert [match.concept_id for match in matches.entity_matches[:2]] == ["entity_a", "entity_a"]
    assert matches.metadata["entity"]["vector_term_count"] == 4


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
