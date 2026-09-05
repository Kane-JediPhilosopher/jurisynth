import asyncio

import faiss
import numpy as np
from rdflib import Dataset, Literal, Namespace, URIRef

from jurisynth.contracts import RetrievalRequest, SourceChunk
from jurisynth.retrieval_mech.er_index_builder import ResourceRecord
from jurisynth.retrieval_mech.er_matcher import Concept, ERMatcher, PersistedERIndices
from jurisynth.retrieval_mech.rdf_retriever import DirectRDFRetriever


EX = Namespace("https://example.test/")
CHUNK = Namespace("http://jurisynth/source/chunk/")


class FakeEmbedder:
    def encode(self, texts, *, normalize_embeddings=True, **kwargs):
        vectors = []
        for text in texts:
            lowered = text.lower()
            vectors.append([1.0, 0.0] if "controller" in lowered else [0.0, 1.0])
        return np.asarray(vectors, dtype=np.float32)


def _index(*vectors):
    index = faiss.IndexFlatIP(2)
    index.add(np.asarray(vectors, dtype=np.float32))
    return index


def test_direct_retrieval_keeps_assertion_and_chunk_provenance_together():
    controller = URIRef(EX.controller)
    processor = URIRef(EX.processor)
    obligation = URIRef(EX.must_provide)
    source_graph = CHUNK["gdpr_chunk_1"]
    dataset = Dataset()
    dataset.graph(source_graph).add((controller, obligation, processor))
    dataset.graph(source_graph).add((controller, obligation, Literal("information")))

    indices = PersistedERIndices(
        entity_index=_index([1.0, 0.0], [0.0, 1.0]),
        relation_index=_index([0.0, 1.0]),
        entity_records=[ResourceRecord(str(controller), "controller"), ResourceRecord(str(processor), "processor")],
        relation_records=[ResourceRecord(str(obligation), "must provide")],
    )
    source = SourceChunk("chunk_1", "gdpr", "A controller must provide information.")
    retriever = DirectRDFRetriever(
        dataset,
        ERMatcher(indices, FakeEmbedder()),
        chunk_resolver=lambda graph_id: source if graph_id == source_graph else None,
    )

    result = asyncio.run(retriever.retrieve(RetrievalRequest("q1", "controller obligations")))

    assert len(result.evidence_items) == 2
    assert all(item.source_chunks == [source] for item in result.evidence_items)
    assert all(item.retrieval_origins == ["direct"] for item in result.evidence_items)
    assert result.metadata["matched_entities"][0]["concept_id"] == "entity_1"
    assert result.warnings


def test_direct_retrieval_excludes_non_chunk_graphs_and_empty_candidate_results():
    dataset = Dataset()
    dataset.graph(URIRef("https://example.test/provenance")).add((EX.controller, EX.predicate, EX.processor))
    indices = PersistedERIndices(None, None, [], [])
    retriever = DirectRDFRetriever(dataset, ERMatcher(indices, FakeEmbedder()), lambda graph_id: None)

    result = asyncio.run(retriever.retrieve(RetrievalRequest("q2", "controller")))

    assert result.evidence_items == []
    assert {key: value for key, value in result.metadata.items() if key != "retrieval_budget"} == {
        "matched_entities": [],
        "matched_relations": [],
        "bounded_path_count": 0,
        "three_hop_path_count": 0,
        "conjunctive_match_count": 0,
        "relevant_communities": [],
    }
    assert result.metadata["retrieval_budget"]["selected_evidence_count"] == 0


def test_bounded_two_hop_path_returns_underlying_assertions_with_path_origin():
    bridge = URIRef(EX.bridge)
    source_graph = CHUNK["doc_1_chunk_2"]
    dataset = Dataset()
    dataset.graph(source_graph).add((EX.controller, EX.connects_to, bridge))
    dataset.graph(source_graph).add((bridge, EX.connects_to, EX.processor))
    indices = PersistedERIndices(
        entity_index=_index([1.0, 0.0], [0.0, 1.0]),
        relation_index=None,
        entity_records=[ResourceRecord(str(EX.controller), "controller"), ResourceRecord(str(EX.processor), "processor")],
        relation_records=[],
    )

    class TwoEntityInterpreter:
        async def interpret(self, request):
            return [Concept("controller", "controller"), Concept("processor", "processor")], []

    source = SourceChunk("chunk_2", "doc_1", "A two-hop relationship.")
    retriever = DirectRDFRetriever(
        dataset,
        ERMatcher(indices, FakeEmbedder()),
        chunk_resolver=lambda graph_id: source if graph_id == source_graph else None,
        interpreter=TwoEntityInterpreter(),
    )

    result = asyncio.run(retriever.retrieve(RetrievalRequest("q3", "controller and processor")))

    assert result.metadata["bounded_path_count"] == 1
    assert len(result.evidence_items) == 2
    assert all(set(item.retrieval_origins) == {"direct", "path"} for item in result.evidence_items)
    assert all(item.source_chunks == [source] for item in result.evidence_items)


def test_three_hop_path_is_only_used_during_bounded_escalation():
    source_graph = CHUNK["doc_1_chunk_3hop"]
    dataset = Dataset()
    dataset.graph(source_graph).add((EX.controller, EX.connects_to, EX.bridge_one))
    dataset.graph(source_graph).add((EX.bridge_one, EX.connects_to, EX.bridge_two))
    dataset.graph(source_graph).add((EX.bridge_two, EX.connects_to, EX.processor))
    indices = PersistedERIndices(
        entity_index=_index([1.0, 0.0], [0.0, 1.0]), relation_index=None,
        entity_records=[ResourceRecord(str(EX.controller), "controller"), ResourceRecord(str(EX.processor), "processor")], relation_records=[],
    )

    class Interpreter:
        async def interpret(self, request): return [Concept("controller", "controller"), Concept("processor", "processor")], []

    retriever = DirectRDFRetriever(dataset, ERMatcher(indices, FakeEmbedder()), lambda graph_id: SourceChunk("chunk", "doc", "path") if graph_id == source_graph else None, interpreter=Interpreter())
    normal = asyncio.run(retriever.retrieve(RetrievalRequest("normal", "question")))
    escalated = asyncio.run(retriever.retrieve(RetrievalRequest("escalated", "question", retrieval_config={"escalation_stage": "broaden_candidates"})))
    assert normal.metadata["three_hop_path_count"] == 0
    assert escalated.metadata["three_hop_path_count"] == 1
    assert all("path3" in item.retrieval_origins for item in escalated.evidence_items)


def test_conjunctive_fallback_marks_only_assertions_where_matched_entity_and_relation_cooccur():
    source_graph = CHUNK["doc_conjunctive"]
    dataset = Dataset()
    dataset.graph(source_graph).add((EX.controller, EX.must_provide, EX.processor))
    dataset.graph(source_graph).add((EX.controller, EX.unrelated, EX.air_traffic))
    indices = PersistedERIndices(
        entity_index=_index([1.0, 0.0], [0.0, 1.0]), relation_index=_index([0.0, 1.0]),
        entity_records=[ResourceRecord(str(EX.controller), "controller"), ResourceRecord(str(EX.processor), "processor")],
        relation_records=[ResourceRecord(str(EX.must_provide), "must provide")],
    )

    class Interpreter:
        async def interpret(self, request): return [Concept("controller", "controller")], [Concept("duty", "must provide")]

    retriever = DirectRDFRetriever(dataset, ERMatcher(indices, FakeEmbedder()), lambda graph_id: SourceChunk("chunk", "doc", "source") if graph_id == source_graph else None, interpreter=Interpreter())
    result = asyncio.run(retriever.retrieve(RetrievalRequest("q", "controller obligation", retrieval_config={"escalation_stage": "broaden_candidates"})))
    assert result.metadata["conjunctive_match_count"] == 1
    assert len(result.evidence_items) == 1
    assert result.evidence_items[0].assertion.predicate == str(EX.must_provide)
    assert "conjunctive" in result.evidence_items[0].retrieval_origins


def test_escalation_records_sparql_and_indexed_pattern_agreement_without_changing_evidence():
    source_graph = CHUNK["doc_sparql"]
    dataset = Dataset()
    dataset.graph(source_graph).add((EX.controller, EX.must_provide, EX.processor))
    indices = PersistedERIndices(
        entity_index=_index([1.0, 0.0]), relation_index=None,
        entity_records=[ResourceRecord(str(EX.controller), "controller")], relation_records=[],
    )
    retriever = DirectRDFRetriever(dataset, ERMatcher(indices, FakeEmbedder()), lambda graph_id: SourceChunk("chunk", "doc", "source") if graph_id == source_graph else None)
    result = asyncio.run(retriever.retrieve(RetrievalRequest("q", "controller", retrieval_config={"escalation_stage": "broaden_candidates"})))
    comparison = result.metadata["sparql_comparison"]
    assert "SELECT DISTINCT" in comparison["query"]
    assert comparison["indexed_count"] == 1
    assert comparison["agreement"] == 1.0


def test_multi_concept_request_excludes_unconfirmed_one_concept_matches():
    source_graph = CHUNK["doc_1_chunk_3"]
    dataset = Dataset()
    dataset.graph(source_graph).add((EX.controller, EX.unrelated, URIRef(EX.air_traffic)))
    indices = PersistedERIndices(
        entity_index=_index([1.0, 0.0], [0.0, 1.0]),
        relation_index=None,
        entity_records=[ResourceRecord(str(EX.controller), "controller"), ResourceRecord(str(EX.processor), "processor")],
        relation_records=[],
    )

    class MultiConceptInterpreter:
        async def interpret(self, request):
            return [Concept("controller", "controller"), Concept("processor", "processor")], []

    retriever = DirectRDFRetriever(
        dataset,
        ERMatcher(indices, FakeEmbedder()),
        chunk_resolver=lambda graph_id: SourceChunk("chunk_3", "doc_1", "Aviation source.") if graph_id == source_graph else None,
        interpreter=MultiConceptInterpreter(),
        minimum_match_similarity=0.01,
    )

    result = asyncio.run(retriever.retrieve(RetrievalRequest("q4", "controller and processor")))

    assert result.evidence_items == []
    assert result.metadata["retrieval_budget"]["pre_filter_evidence_count"] == 1
    assert result.metadata["retrieval_budget"]["minimum_concept_coverage"] == 2


def test_exact_country_entity_does_not_return_other_countries_with_the_same_relation_and_object():
    belgium = URIRef(EX.belgium)
    bulgaria = URIRef(EX.bulgaria)
    change = URIRef(EX.allocation_change)
    source_graph = CHUNK["doc_1_chunk_4"]
    dataset = Dataset()
    dataset.graph(source_graph).add((belgium, EX.notified, change))
    dataset.graph(source_graph).add((bulgaria, EX.notified, change))
    indices = PersistedERIndices(
        entity_index=_index([1.0, 0.0], [0.99, 0.01], [0.0, 1.0]),
        relation_index=None,
        entity_records=[
            ResourceRecord(str(belgium), "belgium"),
            ResourceRecord(str(bulgaria), "bulgaria"),
            ResourceRecord(str(change), "allocation change"),
        ],
        relation_records=[],
    )

    class CountryInterpreter:
        async def interpret(self, request):
            return [Concept("entity_country", "Belgium")], []

    retriever = DirectRDFRetriever(
        dataset,
        ERMatcher(indices, FakeEmbedder()),
        chunk_resolver=lambda graph_id: SourceChunk("chunk_4", "doc_1", "Belgium notified an allocation change.") if graph_id == source_graph else None,
        interpreter=CountryInterpreter(),
    )

    result = asyncio.run(retriever.retrieve(RetrievalRequest("q5", "What did Belgium notify?")))

    assert [(item.assertion.subject, item.assertion.object) for item in result.evidence_items] == [
        (str(belgium), str(change)),
    ]
    assert result.metadata["matched_entities"] == [{
        "concept_id": "entity_country",
        "input_term": "Belgium",
        "uri": str(belgium),
        "label": "belgium",
        "similarity": 1.0,
        "community_ids": [],
    }]
