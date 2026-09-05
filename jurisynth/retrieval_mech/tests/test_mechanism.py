import asyncio

from jurisynth.contracts import Assertion, EvidenceItem, RetrievalRequest, SourceChunk, TableEvidence
from jurisynth.retrieval_mech.mechanism import RetrievalMechanism
from jurisynth.retrieval_mech.config import RetrievalSettings
from jurisynth.retrieval_mech.rdf_retriever import StructuredRetrievalResult
from jurisynth.retrieval_mech.community_hierarchy import CommunityHierarchy, CommunityNode, CommunityOrientationBuilder


class FakeIndex:
    def __init__(self, hits):
        self.hits = hits

    def search(self, *args):
        return self.hits


class StaticStructuredRetriever:
    def __init__(self, items):
        self.items = items

    async def retrieve(self, request):
        return StructuredRetrievalResult(evidence_items=self.items)


class EscalatingStructuredRetriever:
    def __init__(self):
        self.stages = []

    async def retrieve(self, request):
        stage = request.retrieval_config.get("escalation_stage", "normal")
        self.stages.append(stage)
        if stage == "broaden_candidates":
            return StructuredRetrievalResult(evidence_items=[EvidenceItem("E2", Assertion("s", "p", "o"), [], relevance_score=0.9)])
        return StructuredRetrievalResult(evidence_items=[])


class RecordingTableIndex:
    def __init__(self):
        self.document_ids = None

    def search(self, query, embedder, table_top_k, row_top_k, *, document_ids=None):
        self.document_ids = document_ids
        return []


def _request():
    return RetrievalRequest("q1", "question")


def test_status_success_requires_strong_structured_or_table_evidence():
    item = EvidenceItem("E1", Assertion("s", "p", "o"), [], relevance_score=0.9)
    mechanism = RetrievalMechanism(object(), structured_retriever=StaticStructuredRetriever([item]))
    assert asyncio.run(mechanism.retrieve_evidence(_request())).status == "success"

    table = TableEvidence("t1", "d1", None, [["value"]], [0], combined_score=0.9)
    mechanism = RetrievalMechanism(object(), table_indices=[FakeIndex([table])])
    assert asyncio.run(mechanism.retrieve_evidence(_request())).status == "success"


def test_status_weak_preserves_marginal_or_chunk_only_results():
    weak_item = EvidenceItem("E1", Assertion("s", "p", "o"), [], relevance_score=0.2)
    mechanism = RetrievalMechanism(object(), structured_retriever=StaticStructuredRetriever([weak_item]))
    assert asyncio.run(mechanism.retrieve_evidence(_request())).status == "weak"

    chunk = SourceChunk("c1", "d1", "text", similarity=0.9)
    mechanism = RetrievalMechanism(object(), chunk_indices=[FakeIndex([chunk])])
    bundle = asyncio.run(mechanism.retrieve_evidence(_request()))
    assert bundle.status == "weak"
    assert bundle.evidence_items[0].evidence_id.startswith("C_")
    assert bundle.evidence_items[0].source_chunks == [chunk]
    assert bundle.evidence_items[0].retrieval_origins == ["chunk"]


def test_status_empty_and_error_are_distinguished():
    mechanism = RetrievalMechanism(object())
    assert asyncio.run(mechanism.retrieve_evidence(_request())).status == "empty"

    class BrokenIndex:
        def search(self, *args):
            raise RuntimeError("broken index")

    mechanism = RetrievalMechanism(object(), chunk_indices=[BrokenIndex()])
    assert asyncio.run(mechanism.retrieve_evidence(_request())).status == "error"


def test_table_retrieval_receives_explicit_document_constraints_only():
    table_index = RecordingTableIndex()
    mechanism = RetrievalMechanism(object(), table_indices=[table_index])
    request = RetrievalRequest("q4", "question", constraints={"document_ids": ["doc_a", "doc_b"]})

    assert asyncio.run(mechanism.retrieve_evidence(request)).status == "empty"
    assert table_index.document_ids == {"doc_a", "doc_b"}


def test_coherence_keeps_provenance_and_faiss_agreement_separate():
    item = EvidenceItem("E1", Assertion("s", "p", "o"), [SourceChunk("c1", "d1", "source")], relevance_score=0.9)
    chunk = SourceChunk("c1", "d1", "source", similarity=0.8)
    mechanism = RetrievalMechanism(
        object(),
        chunk_indices=[FakeIndex([chunk])],
        structured_retriever=StaticStructuredRetriever([item]),
    )

    bundle = asyncio.run(mechanism.retrieve_evidence(_request()))

    assert item.coherence_score == 1.0
    assert bundle.retrieval_metadata["coherence"] == {"quad_support_coverage": 1.0, "faiss_agreement": 1.0}


def test_weak_normal_retrieval_runs_one_bounded_broaden_candidates_attempt():
    retriever = EscalatingStructuredRetriever()
    bundle = asyncio.run(RetrievalMechanism(object(), structured_retriever=retriever).retrieve_evidence(_request()))

    assert bundle.status == "success"
    assert retriever.stages == ["normal", "broaden_candidates"]
    assert bundle.retrieval_metadata["escalation_stages"] == ["normal", "broaden_candidates"]
    assert [item.evidence_id for item in bundle.evidence_items] == ["E2"]


def test_internal_operation_timeout_becomes_a_retrieval_error():
    class HangingStructuredRetriever:
        async def retrieve(self, request):
            await asyncio.Event().wait()

    mechanism = RetrievalMechanism(
        object(),
        structured_retriever=HangingStructuredRetriever(),
        settings=RetrievalSettings(operation_timeout_seconds=0.01),
    )

    bundle = asyncio.run(mechanism.retrieve_evidence(_request()))
    assert bundle.status == "error"
    assert "TimeoutError" in bundle.retrieval_metadata["warnings"][0]


def test_community_orientation_is_separate_from_citable_evidence():
    hierarchy = CommunityHierarchy({"c1": CommunityNode("c1", 0, member_ids=("e1",))}, "fixture")

    class CommunityRetriever:
        async def retrieve(self, request):
            return StructuredRetrievalResult(
                evidence_items=[EvidenceItem("E1", Assertion("s", "p", "o"), [], relevance_score=0.9)],
                metadata={"relevant_communities": [{"community_id": "c1", "score": 0.9}]},
            )

    mechanism = RetrievalMechanism(
        object(),
        structured_retriever=CommunityRetriever(),
        community_orientation_builder=CommunityOrientationBuilder(hierarchy, {"e1": "data controller"}),
    )
    bundle = asyncio.run(mechanism.retrieve_evidence(_request()))

    assert bundle.community_summary is not None
    assert "data controller" in bundle.community_summary
    assert [item.evidence_id for item in bundle.evidence_items] == ["E1"]
    assert bundle.retrieval_metadata["community_orientation"]["authoritative"] is False
