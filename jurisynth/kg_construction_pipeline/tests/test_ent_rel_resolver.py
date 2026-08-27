from unittest.mock import AsyncMock, patch
import pytest

import asyncio

import numpy as np
from rdflib import URIRef

from ent_rel_resolver import (
    UnionFind,
    normalize_key,
    has_identifier,
    extract_uri_label,
    prepare_document_resources,
    attach_resource_embeddings,
    build_candidate_clusters,
    build_document_clusters,
    release_resource_embeddings,
    filter_resolution_clusters,
    build_resolution_query,
    collect_resolution_queries,
    build_resolution_batches,
    validate_resolution_output,
    attach_lookup_metadata,
    build_resolution_map,
    apply_resolution,
    resolution_worker,
    resolve_batches,
    resolve_entities_and_relations,
)


# =====================================================================
# Test doubles
# =====================================================================


class FakeEmbeddingModel:
    """Deterministic embedding model for unit tests."""

    def encode(
        self,
        texts,
        batch_size=128,
        normalize_embeddings=True,
        convert_to_numpy=True,
    ):
        vectors = []

        for text in texts:
            text = text.casefold()

            if "animal" in text:
                vector = [1.0, 0.0]
            elif "animals" in text:
                vector = [0.99, 0.01]
            elif "plant" in text:
                vector = [0.0, 1.0]
            elif "has value" in text:
                vector = [1.0, 0.0]
            elif "contains value" in text:
                vector = [0.99, 0.01]
            else:
                vector = [0.0, 0.0]

            vectors.append(vector)

        return np.asarray(vectors, dtype=np.float32)


# =====================================================================
# Union-Find
# =====================================================================


def test_union_find_initializes_each_element_separately():
    uf = UnionFind(3)

    assert uf.find(0) == 0
    assert uf.find(1) == 1
    assert uf.find(2) == 2


def test_union_find_merges_sets():
    uf = UnionFind(3)

    uf.union(0, 1)

    assert uf.find(0) == uf.find(1)
    assert uf.find(2) != uf.find(0)


def test_union_find_supports_transitive_merges():
    uf = UnionFind(3)

    uf.union(0, 1)
    uf.union(1, 2)

    assert uf.find(0) == uf.find(2)


# =====================================================================
# Label normalization / identifier detection
# =====================================================================


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Animal", "animal"),
        ("  The   Animal  ", "the animal"),
        ("Article 12 ( 2 )", "article 12(2)"),
        ("Article 12 (a)", "article 12(a)"),
        ("foo\u00a0bar", "foo bar"),
        ("foo\u202fbar", "foo bar"),
        ("foo\u200bbar", "foobar"),
        ("foo–bar", "foo-bar"),
    ],
)
def test_normalize_key(raw, expected):
    assert normalize_key(raw) == expected


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("", ""),
        ("   ", ""),
        ("\t\n  animal  \t", "animal"),
    ],
)
def test_normalize_key_handles_empty_and_whitespace(raw, expected):
    assert normalize_key(raw) == expected


@pytest.mark.parametrize(
    "text",
    [
        "Article 12",
        "Art. 5",
        "paragraph 3",
        "para. 4",
        "point (a)",
        "section 2",
        "chapter IV",
        "title II",
        "annex III",
        "recital 10",
        "No. 123",
        "123/456",
        "2024/123",
        "2024",
        "(a)",
        "(2)",
    ],
)
def test_has_identifier_detects_legal_identifiers(text):
    assert has_identifier(text)


@pytest.mark.parametrize(
    "text",
    [
        "",
        "animal",
        "the undertaking",
        "applicable authorisation",
    ],
)
def test_has_identifier_rejects_non_identifiers(text):
    assert not has_identifier(text)


@pytest.mark.parametrize(
    "text",
    [
        "animal 123",
        "sectional analysis",
        "article",
        "paragraph",
        "version 2",
    ],
)
def test_has_identifier_rejects_non_legal_identifier_patterns(text):
    assert not has_identifier(text)


# =====================================================================
# URI helpers
# =====================================================================


def test_extract_uri_label():
    uri = URIRef(
        "http://jurisynth/data/the_applicable_authorisation"
    )

    assert extract_uri_label(uri) == (
        "the applicable authorisation"
    )


# =====================================================================
# Resource preparation
# =====================================================================


def test_prepare_document_resources_collects_entities_and_relations():
    scored_assertions = [
        {
            "doc_id": "doc1",
            "chunk_id": "chunk1",
            "assertion_id": 0,
            "assertion": {
                "subject": URIRef(
                    "http://jurisynth/data/animal"
                ),
                "predicate": URIRef(
                    "http://jurisynth/data/has_value"
                ),
                "object": URIRef(
                    "http://jurisynth/data/plant"
                ),
            },
        }
    ]

    entities, relations = prepare_document_resources(
        scored_assertions
    )

    assert "doc1" in entities
    assert "doc1" in relations

    assert (
        "http://jurisynth/data/animal"
        in entities["doc1"]
    )

    assert (
        "http://jurisynth/data/plant"
        in entities["doc1"]
    )

    assert (
        "http://jurisynth/data/has_value"
        in relations["doc1"]
    )


def test_prepare_document_resources_ignores_external_uris():
    scored_assertions = [
        {
            "doc_id": "doc1",
            "chunk_id": "chunk1",
            "assertion_id": 0,
            "assertion": {
                "subject": URIRef(
                    "http://example.org/Animal"
                ),
                "predicate": URIRef(
                    "http://jurisynth/data/has_value"
                ),
                "object": None,
            },
        }
    ]

    entities, relations = prepare_document_resources(
        scored_assertions
    )

    assert not entities["doc1"]
    assert (
        "http://jurisynth/data/has_value"
        in relations["doc1"]
    )


def test_prepare_document_resources_tracks_occurrences():
    uri = URIRef("http://jurisynth/data/animal")

    scored_assertions = [
        {
            "doc_id": "doc1",
            "chunk_id": "chunk1",
            "assertion_id": 0,
            "assertion": {
                "subject": uri,
                "predicate": URIRef(
                    "http://jurisynth/data/has_value"
                ),
                "object": None,
            },
        },
        {
            "doc_id": "doc1",
            "chunk_id": "chunk2",
            "assertion_id": 1,
            "assertion": {
                "subject": uri,
                "predicate": URIRef(
                    "http://jurisynth/data/has_value"
                ),
                "object": None,
            },
        },
    ]

    entities, _ = prepare_document_resources(
        scored_assertions
    )

    occurrences = entities["doc1"][str(uri)][
        "occurrences"
    ]

    assert len(occurrences) == 2
    assert occurrences[0]["assertion_id"] == 0
    assert occurrences[1]["assertion_id"] == 1


def test_prepare_document_resources_ignores_literal_objects():
    scored_assertions = [
        {
            "doc_id": "doc1",
            "chunk_id": "chunk1",
            "assertion_id": 0,
            "assertion": {
                "subject": URIRef(
                    "http://jurisynth/data/animal"
                ),
                "predicate": URIRef(
                    "http://jurisynth/data/has_value"
                ),
                "object": "42",
            },
        }
    ]

    entities, relations = prepare_document_resources(
        scored_assertions
    )

    assert (
        "http://jurisynth/data/animal"
        in entities["doc1"]
    )
    assert "42" not in entities["doc1"]


# =====================================================================
# Embeddings
# =====================================================================


def test_attach_resource_embeddings():
    resources = {
        "doc1": {
            "http://jurisynth/data/animal": {
                "label": "animal"
            },
            "http://jurisynth/data/plant": {
                "label": "plant"
            },
        }
    }

    attach_resource_embeddings(
        resources,
        FakeEmbeddingModel(),
    )

    assert "embedding" in resources["doc1"][
        "http://jurisynth/data/animal"
    ]

    assert "embedding" in resources["doc1"][
        "http://jurisynth/data/plant"
    ]


def test_attach_resource_embeddings_handles_empty_resources():
    resources = {}

    attach_resource_embeddings(
        resources,
        FakeEmbeddingModel(),
    )

    assert resources == {}


# =====================================================================
# Candidate clustering
# =====================================================================


def test_build_candidate_clusters_groups_similar_resources():
    resources = {
        "uri1": {
            "label": "animal",
            "embedding": np.array([1.0, 0.0]),
        },
        "uri2": {
            "label": "animals",
            "embedding": np.array([0.99, 0.01]),
        },
        "uri3": {
            "label": "plant",
            "embedding": np.array([0.0, 1.0]),
        },
    }

    clusters = build_candidate_clusters(
        resources,
        similarity_threshold=0.9,
    )

    assert len(clusters) == 1
    assert set(clusters[0]["resources"]) == {
        "uri1",
        "uri2",
    }


def test_build_candidate_clusters_returns_no_singletons():
    resources = {
        "uri1": {
            "label": "animal",
            "embedding": np.array([1.0, 0.0]),
        }
    }

    clusters = build_candidate_clusters(
        resources,
        similarity_threshold=0.9,
    )

    assert clusters == []


def test_build_candidate_clusters_handles_empty_resources():
    assert build_candidate_clusters({}) == []


def test_build_document_clusters_is_per_document():
    resources = {
        "doc1": {
            "uri1": {
                "label": "animal",
                "embedding": np.array([1.0, 0.0]),
            },
            "uri2": {
                "label": "animals",
                "embedding": np.array([0.99, 0.01]),
            },
        },
        "doc2": {
            "uri3": {
                "label": "plant",
                "embedding": np.array([0.0, 1.0]),
            }
        },
    }

    result = build_document_clusters(
        resources,
        similarity_threshold=0.9,
    )

    assert len(result["doc1"]) == 1
    assert result["doc2"] == []


def test_build_candidate_clusters_supports_transitive_merges():
    resources = {
        "uri1": {
            "label": "animal",
            "embedding": np.array([1.0, 0.0]),
        },
        "uri2": {
            "label": "animals",
            "embedding": np.array([0.99, 0.01]),
        },
        "uri3": {
            "label": "animal species",
            "embedding": np.array([0.98, 0.02]),
        },
    }

    clusters = build_candidate_clusters(
        resources,
        similarity_threshold=0.9,
    )

    assert len(clusters) == 1
    assert set(clusters[0]["resources"]) == {
        "uri1",
        "uri2",
        "uri3",
    }


def test_build_candidate_clusters_respects_similarity_threshold():
    resources = {
        "uri1": {
            "label": "animal",
            "embedding": np.array([1.0, 0.0]),
        },
        "uri2": {
            "label": "animals",
            "embedding": np.array([0.0, 1.0]),
        },
    }

    clusters = build_candidate_clusters(
        resources,
        similarity_threshold=1.0,
    )

    assert clusters == []
    

# =====================================================================
# Temporary embedding cleanup
# =====================================================================


def test_release_resource_embeddings_removes_embeddings():
    resources = {
        "doc1": {
            "uri1": {
                "label": "animal",
                "embedding": np.array([1.0, 0.0]),
            }
        }
    }

    release_resource_embeddings(resources)

    assert "embedding" not in resources["doc1"]["uri1"]


# =====================================================================
# Cluster filtering
# =====================================================================


def test_filter_resolution_clusters_skips_identifier_only_cluster():
    clusters = [
        {
            "cluster_id": 1,
            "resources": {
                "uri1": {"label": "Article 12"},
                "uri2": {"label": "article 12"},
            },
        }
    ]

    review, skipped = filter_resolution_clusters(
        clusters
    )

    assert review == []
    assert len(skipped) == 1


def test_filter_resolution_clusters_keeps_normal_cluster():
    clusters = [
        {
            "cluster_id": 1,
            "resources": {
                "uri1": {"label": "animal"},
                "uri2": {"label": "animals"},
            },
        }
    ]

    review, skipped = filter_resolution_clusters(
        clusters
    )

    assert len(review) == 1
    assert skipped == []


# =====================================================================
# Resolution query construction
# =====================================================================


def test_build_resolution_query_uses_temporary_resource_ids():
    cluster = {
        "cluster_type": "entity",
        "cluster_id": 5,
        "resources": {
            "uri1": {"label": "animal"},
            "uri2": {"label": "animals"},
        },
    }

    resource_map = {
        "c5_r1": "uri1",
        "c5_r2": "uri2",
    }

    query = build_resolution_query(
        cluster,
        resource_map,
        "d1",
    )

    assert "Document ID: d1" in query
    assert "Resource type: entity" in query
    assert "Cluster ID: 5" in query
    assert "Resource ID: c5_r1" in query
    assert "Resource ID: c5_r2" in query
    assert "Label: animal" in query
    assert "Label: animals" in query


def test_collect_resolution_queries_separates_reviewable_and_skipped():
    entity_clusters = {
        "doc1": [
            {
                "cluster_id": 1,
                "resources": {
                    "uri1": {"label": "animal"},
                    "uri2": {"label": "animals"},
                },
            },
            {
                "cluster_id": 2,
                "resources": {
                    "uri3": {"label": "Article 12"},
                    "uri4": {"label": "article 12"},
                },
            },
        ]
    }

    relation_clusters = {}

    queries, skipped = collect_resolution_queries(
        entity_clusters,
        relation_clusters,
    )

    assert len(queries) == 1
    assert queries[0]["doc_id"] == "doc1"
    assert queries[0]["cluster_type"] == "entity"
    assert queries[0]["cluster_id"] == 1

    assert len(skipped) == 1


# =====================================================================
# Resolution batching
# =====================================================================


def test_build_resolution_batches_assigns_batch_local_ids():
    queries = [
        {
            "doc_id": "doc1",
            "cluster_type": "entity",
            "cluster_id": 1,
            "resources": {
                "uri1": {"label": "animal"},
                "uri2": {"label": "animals"},
            },
        }
    ]

    batches = build_resolution_batches(
        queries,
        batch_size=10,
    )

    assert len(batches) == 1

    batch = batches[0]

    assert "d1" in batch["query"]
    assert "c1_r1" in batch["query"]
    assert "c1_r2" in batch["query"]

    assert (
        ("d1", "entity", 1)
        in batch["lookup"]
    )


def test_build_resolution_batches_respects_batch_size():
    queries = [
        {
            "doc_id": "doc1",
            "cluster_type": "entity",
            "cluster_id": i,
            "resources": {
                f"uri{i}a": {"label": "animal"},
                f"uri{i}b": {"label": "animals"},
            },
        }
        for i in range(1, 4)
    ]

    batches = build_resolution_batches(
        queries,
        batch_size=2,
    )

    assert len(batches) == 2


# =====================================================================
# Resolution output validation
# =====================================================================


def _make_lookup():
    return {
        ("d1", "entity", 1): {
            "resource_map": {
                "c1_r1": "uri1",
                "c1_r2": "uri2",
            },
            "doc_id": "doc1",
            "cluster_type": "entity",
        }
    }


def test_validate_resolution_output_accepts_valid_partition():
    clusters = [
        {
            "document_id": "d1",
            "cluster_id": 1,
            "resolutions": [
                {
                    "canonical_id": "c1_r1",
                    "members": [
                        "c1_r1",
                        "c1_r2",
                    ],
                }
            ],
        }
    ]

    assert validate_resolution_output(
        clusters,
        _make_lookup(),
    )


def test_validate_resolution_output_rejects_unknown_canonical():
    clusters = [
        {
            "document_id": "d1",
            "cluster_id": 1,
            "resolutions": [
                {
                    "canonical_id": "unknown",
                    "members": [
                        "c1_r1",
                        "c1_r2",
                    ],
                }
            ],
        }
    ]

    with pytest.raises(ValueError):
        validate_resolution_output(
            clusters,
            _make_lookup(),
        )


def test_validate_resolution_output_rejects_duplicate_members():
    clusters = [
        {
            "document_id": "d1",
            "cluster_id": 1,
            "resolutions": [
                {
                    "canonical_id": "c1_r1",
                    "members": ["c1_r1"],
                },
                {
                    "canonical_id": "c1_r2",
                    "members": [
                        "c1_r1",
                        "c1_r2",
                    ],
                },
            ],
        }
    ]

    with pytest.raises(ValueError):
        validate_resolution_output(
            clusters,
            _make_lookup(),
        )


def test_validate_resolution_output_rejects_missing_members():
    clusters = [
        {
            "document_id": "d1",
            "cluster_id": 1,
            "resolutions": [
                {
                    "canonical_id": "c1_r1",
                    "members": ["c1_r1"],
                }
            ],
        }
    ]

    with pytest.raises(ValueError):
        validate_resolution_output(
            clusters,
            _make_lookup(),
        )


def test_validate_resolution_output_requires_canonical_to_be_member():
    clusters = [
        {
            "document_id": "d1",
            "cluster_id": 1,
            "resolutions": [
                {
                    "canonical_id": "c1_r1",
                    "members": ["c1_r2"],
                }
            ],
        }
    ]

    with pytest.raises(ValueError):
        validate_resolution_output(
            clusters,
            _make_lookup(),
        )


def test_validate_resolution_output_rejects_unknown_cluster():
    clusters = [
        {
            "document_id": "d1",
            "cluster_id": 999,
            "resolutions": [
                {
                    "canonical_id": "c1_r1",
                    "members": [
                        "c1_r1",
                        "c1_r2",
                    ],
                }
            ],
        }
    ]

    with pytest.raises(ValueError):
        validate_resolution_output(
            clusters,
            _make_lookup(),
        )


def test_validate_resolution_output_rejects_unknown_document():
    clusters = [
        {
            "document_id": "unknown",
            "cluster_id": 1,
            "resolutions": [
                {
                    "canonical_id": "c1_r1",
                    "members": [
                        "c1_r1",
                        "c1_r2",
                    ],
                }
            ],
        }
    ]

    with pytest.raises(ValueError):
        validate_resolution_output(
            clusters,
            _make_lookup(),
        )


def test_validate_resolution_output_rejects_missing_resolutions():
    clusters = [
        {
            "document_id": "d1",
            "cluster_id": 1,
        }
    ]

    with pytest.raises(ValueError):
        validate_resolution_output(
            clusters,
            _make_lookup(),
        )


# =====================================================================
# Metadata attachment
# =====================================================================


def test_attach_lookup_metadata_restores_authoritative_metadata():
    clusters = [
        {
            "document_id": "d1",
            "cluster_id": 1,
            "resolutions": [],
        }
    ]

    lookup = _make_lookup()

    result = attach_lookup_metadata(
        clusters,
        lookup,
    )

    assert result[0]["doc_id"] == "doc1"
    assert result[0]["cluster_type"] == "entity"
    assert result[0]["resource_map"] == {
        "c1_r1": "uri1",
        "c1_r2": "uri2",
    }


def test_attach_lookup_metadata_rejects_missing_lookup():
    clusters = [
        {
            "document_id": "unknown",
            "cluster_id": 1,
            "resolutions": [],
        }
    ]

    with pytest.raises(KeyError):
        attach_lookup_metadata(
            clusters,
            _make_lookup(),
        )


# =====================================================================
# Resolution map
# =====================================================================


def test_build_resolution_map_maps_members_to_canonical_uri():
    resolved_clusters = [
        {
            "resource_map": {
                "c1_r1": "uri1",
                "c1_r2": "uri2",
            },
            "resolutions": [
                {
                    "canonical_id": "c1_r1",
                    "members": [
                        "c1_r1",
                        "c1_r2",
                    ],
                }
            ],
        }
    ]

    result = build_resolution_map(
        resolved_clusters
    )

    assert result == {
        URIRef("uri1"): URIRef("uri1"),
        URIRef("uri2"): URIRef("uri1"),
    }


def test_build_resolution_map_rejects_unknown_member():
    resolved_clusters = [
        {
            "resource_map": {
                "c1_r1": "uri1",
            },
            "resolutions": [
                {
                    "canonical_id": "c1_r1",
                    "members": [
                        "c1_r1",
                        "unknown",
                    ],
                }
            ],
        }
    ]

    with pytest.raises(KeyError):
        build_resolution_map(
            resolved_clusters
        )


# =====================================================================
# Applying resolutions
# =====================================================================


def test_apply_resolution_updates_entity_and_relation_uris():
    old_subject = URIRef(
        "http://jurisynth/data/animal"
    )
    old_predicate = URIRef(
        "http://jurisynth/data/has_value"
    )
    old_object = URIRef(
        "http://jurisynth/data/plant"
    )

    new_subject = URIRef(
        "http://jurisynth/data/animals"
    )
    new_predicate = URIRef(
        "http://jurisynth/data/contains_value"
    )
    new_object = URIRef(
        "http://jurisynth/data/plants"
    )

    assertions = [
        {
            "doc_id": "doc1",
            "chunk_id": "chunk1",
            "assertion_id": 0,
            "assertion": {
                "subject": old_subject,
                "predicate": old_predicate,
                "object": old_object,
            },
            "modifiers": [
                {"type": "negation"}
            ],
        }
    ]

    result = apply_resolution(
        assertions,
        {
            old_subject: new_subject,
            old_object: new_object,
        },
        {
            old_predicate: new_predicate,
        },
    )

    assertion = result[0]["assertion"]

    assert assertion["subject"] == new_subject
    assert assertion["predicate"] == new_predicate
    assert assertion["object"] == new_object

    assert result[0]["modifiers"] == [
        {"type": "negation"}
    ]


def test_apply_resolution_preserves_unmapped_components():
    subject = URIRef(
        "http://jurisynth/data/animal"
    )

    assertions = [
        {
            "doc_id": "doc1",
            "chunk_id": "chunk1",
            "assertion_id": 0,
            "assertion": {
                "subject": subject,
                "predicate": URIRef(
                    "http://jurisynth/data/has_value"
                ),
                "object": None,
            },
            "modifiers": [],
        }
    ]

    result = apply_resolution(
        assertions,
        {},
        {},
    )

    assert result[0]["assertion"]["subject"] == subject
    assert result[0]["assertion"]["object"] is None


def test_apply_resolution_preserves_literal_objects():
    subject = URIRef(
        "http://jurisynth/data/animal"
    )

    assertions = [
        {
            "doc_id": "doc1",
            "chunk_id": "chunk1",
            "assertion_id": 0,
            "assertion": {
                "subject": subject,
                "predicate": URIRef(
                    "http://jurisynth/data/has_value"
                ),
                "object": "42",
            },
            "modifiers": [],
        }
    ]

    result = apply_resolution(
        assertions,
        {},
        {},
    )

    assert result[0]["assertion"]["object"] == "42"


# =====================================================================
# Integration-style tests
# =====================================================================


def test_prepare_to_cluster_pipeline():
    uri1 = URIRef(
        "http://jurisynth/data/animal"
    )
    uri2 = URIRef(
        "http://jurisynth/data/animals"
    )

    assertions = [
        {
            "doc_id": "doc1",
            "chunk_id": "chunk1",
            "assertion_id": 0,
            "assertion": {
                "subject": uri1,
                "predicate": URIRef(
                    "http://jurisynth/data/has_value"
                ),
                "object": None,
            },
        },
        {
            "doc_id": "doc1",
            "chunk_id": "chunk2",
            "assertion_id": 1,
            "assertion": {
                "subject": uri2,
                "predicate": URIRef(
                    "http://jurisynth/data/has_value"
                ),
                "object": None,
            },
        },
    ]

    entities, relations = prepare_resolution_resources_for_test(
        assertions
    )

    clusters = build_document_clusters(
        entities,
        similarity_threshold=0.9,
    )

    assert len(clusters["doc1"]) == 1


def prepare_resolution_resources_for_test(
    assertions,
):
    """
    Small test-local equivalent of the preparation helper.

    This keeps the integration test focused on:
        preparation -> embeddings -> clustering
    """
    from ent_rel_resolver import (
        prepare_resolution_resources,
    )

    return prepare_resolution_resources(
        assertions,
        FakeEmbeddingModel(),
    )


# =====================================================================
# Mocked LLM / asynchronous resolution
# =====================================================================


def _make_test_batch():
    return {
        "query": "resolve test cluster",
        "lookup": {
            ("d1", "entity", 1): {
                "resource_map": {
                    "c1_r1": "uri1",
                    "c1_r2": "uri2",
                },
                "doc_id": "doc1",
                "cluster_type": "entity",
            }
        },
    }


def _make_valid_llm_response():
    return """[
        {
            "document_id": "d1",
            "cluster_id": 1,
            "resolutions": [
                {
                    "canonical_id": "c1_r1",
                    "members": [
                        "c1_r1",
                        "c1_r2"
                    ]
                }
            ]
        }
    ]"""


@pytest.mark.asyncio
async def test_resolution_worker_accepts_valid_llm_response():
    batch = _make_test_batch()

    semaphore = asyncio.Semaphore(1)
    rate_lock = asyncio.Lock()

    last_request_time = [0.0]
    cooldown_until = [0.0]
    current_rps = [10.0]

    with patch(
        "ent_rel_resolver.get_completion",
        new=AsyncMock(
            return_value=_make_valid_llm_response()
        ),
    ) as mock_completion:

        result = await resolution_worker(
            client=object(),
            batch=batch,
            semaphore=semaphore,
            rate_lock=rate_lock,
            last_request_time=last_request_time,
            cooldown_until=cooldown_until,
            current_rps=current_rps,
            max_rps=10.0,
            max_attempts=1,
        )

    assert result["success"] is True
    assert len(result["clusters"]) == 1

    mock_completion.assert_awaited_once()


@pytest.mark.asyncio
async def test_resolution_worker_rejects_invalid_llm_response():
    batch = _make_test_batch()

    semaphore = asyncio.Semaphore(1)
    rate_lock = asyncio.Lock()

    last_request_time = [0.0]
    cooldown_until = [0.0]
    current_rps = [10.0]

    with patch(
        "ent_rel_resolver.get_completion",
        new=AsyncMock(
            return_value="""[
                {
                    "document_id": "d1",
                    "cluster_id": 1,
                    "resolutions": [
                        {
                            "canonical_id": "unknown",
                            "members": ["unknown"]
                        }
                    ]
                }
            ]"""
        ),
    ) as mock_completion:

        result = await resolution_worker(
            client=object(),
            batch=batch,
            semaphore=semaphore,
            rate_lock=rate_lock,
            last_request_time=last_request_time,
            cooldown_until=cooldown_until,
            current_rps=current_rps,
            max_rps=10.0,
            max_attempts=1,
        )

    assert result["success"] is False
    assert result["clusters"] == []

    mock_completion.assert_awaited_once()


@pytest.mark.asyncio
async def test_resolution_worker_retries_transient_error():
    batch = _make_test_batch()

    semaphore = asyncio.Semaphore(1)
    rate_lock = asyncio.Lock()

    last_request_time = [0.0]
    cooldown_until = [0.0]
    current_rps = [10.0]

    mock_completion = AsyncMock(
        side_effect=[
            Exception("429 Too Many Requests"),
            _make_valid_llm_response(),
        ]
    )

    with patch(
        "ent_rel_resolver.get_completion",
        new=mock_completion,
    ), patch(
        "ent_rel_resolver.wait_for_rate_limit",
        new=AsyncMock(),
    ):

        result = await resolution_worker(
            client=object(),
            batch=batch,
            semaphore=semaphore,
            rate_lock=rate_lock,
            last_request_time=last_request_time,
            cooldown_until=cooldown_until,
            current_rps=current_rps,
            max_rps=10.0,
            max_attempts=2,
        )

    assert result["success"] is True
    assert mock_completion.await_count == 2


@pytest.mark.asyncio
async def test_resolution_worker_fails_after_max_attempts():
    batch = _make_test_batch()

    semaphore = asyncio.Semaphore(1)
    rate_lock = asyncio.Lock()

    last_request_time = [0.0]
    cooldown_until = [0.0]
    current_rps = [10.0]

    mock_completion = AsyncMock(
        side_effect=Exception("503 Service Unavailable")
    )

    with patch(
        "ent_rel_resolver.get_completion",
        new=mock_completion,
    ):

        result = await resolution_worker(
            client=object(),
            batch=batch,
            semaphore=semaphore,
            rate_lock=rate_lock,
            cooldown_until=cooldown_until,
            current_rps=current_rps,
            max_rps=10.0,
            max_attempts=3,
            max_backoff=0,
            last_request_time=last_request_time
        )

    assert result["success"] is False
    assert mock_completion.await_count == 3


@pytest.mark.asyncio
async def test_resolve_batches_resolves_successful_batches():
    batches = [
        _make_test_batch(),
        _make_test_batch(),
    ]

    valid_response = _make_valid_llm_response()

    with patch(
        "ent_rel_resolver.get_completion",
        new=AsyncMock(
            return_value=valid_response
        ),
    ):

        result = await resolve_batches(
            client=object(),
            batches=batches,
            semaphore=asyncio.Semaphore(2),
            requests_per_second=100,
            max_backoff=0,
        )

    assert len(result) == 2

    for cluster in result:
        assert cluster["doc_id"] == "doc1"
        assert cluster["cluster_type"] == "entity"
        assert cluster["resource_map"] == {
            "c1_r1": "uri1",
            "c1_r2": "uri2",
        }


@pytest.mark.asyncio
async def test_resolve_batches_skips_failed_batches():
    batches = [
        _make_test_batch(),
        _make_test_batch(),
    ]

    mock_completion = AsyncMock(
        side_effect=[
            _make_valid_llm_response(),
            Exception("permanent failure"),
        ]
    )

    with patch(
        "ent_rel_resolver.get_completion",
        new=mock_completion,
    ):

        result = await resolve_batches(
            client=object(),
            batches=batches,
            semaphore=asyncio.Semaphore(2),
            requests_per_second=100,
            max_backoff=0,
        )

    assert len(result) == 1


@pytest.mark.asyncio
async def test_resolve_entities_and_relations_resolves_both():
    entity_batch = _make_test_batch()

    relation_batch = {
        "query": "resolve relation",
        "lookup": {
            ("d1", "relation", 2): {
                "resource_map": {
                    "c2_r1": "uri3",
                    "c2_r2": "uri4",
                },
                "doc_id": "doc1",
                "cluster_type": "relation",
            }
        },
    }

    entity_response = _make_valid_llm_response()

    relation_response = """[
        {
            "document_id": "d1",
            "cluster_id": 2,
            "resolutions": [
                {
                    "canonical_id": "c2_r1",
                    "members": [
                        "c2_r1",
                        "c2_r2"
                    ]
                }
            ]
        }
    ]"""

    mock_completion = AsyncMock(
        side_effect=[
            entity_response,
            relation_response,
        ]
    )

    with patch(
        "ent_rel_resolver.get_completion",
        new=mock_completion,
    ):

        entities, relations = (
            await resolve_entities_and_relations(
                client=object(),
                entity_batches=[entity_batch],
                relation_batches=[relation_batch],
                semaphore=asyncio.Semaphore(2),
                requests_per_second=100,
                max_backoff=0,
            )
        )

    assert len(entities) == 1
    assert len(relations) == 1

    assert entities[0]["cluster_type"] == "entity"
    assert relations[0]["cluster_type"] == "relation"

    assert mock_completion.await_count == 2


@pytest.mark.asyncio
async def test_resolve_batches_handles_empty_input():
    with patch(
        "ent_rel_resolver.get_completion",
        new=AsyncMock(),
    ) as mock_completion:
        result = await resolve_batches(
            client=object(),
            batches=[],
            semaphore=asyncio.Semaphore(1),
            requests_per_second=100,
            max_backoff=0,
        )

    assert result == []
    mock_completion.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolution_worker_sends_batch_query():
    batch = _make_test_batch()

    semaphore = asyncio.Semaphore(1)
    rate_lock = asyncio.Lock()
    last_request_time = [0.0]
    cooldown_until = [0.0]
    current_rps = [10.0]

    with patch(
        "ent_rel_resolver.get_completion",
        new=AsyncMock(
            return_value=_make_valid_llm_response()
        ),
    ) as mock_completion:

        await resolution_worker(
            client=object(),
            batch=batch,
            semaphore=semaphore,
            rate_lock=rate_lock,
            last_request_time=last_request_time,
            cooldown_until=cooldown_until,
            current_rps=current_rps,
            max_rps=10.0,
            max_attempts=1,
        )

    mock_completion.assert_awaited_once()

    call_kwargs = mock_completion.await_args.kwargs

    assert batch["query"] in str(call_kwargs)