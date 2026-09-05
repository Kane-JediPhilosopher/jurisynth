import asyncio

from jurisynth.contracts import Assertion, EvidenceItem, RetrievalRequest, SourceChunk, TableEvidence
from jurisynth.retrieval_mech.mechanism import RetrievalMechanism
from jurisynth.retrieval_mech.rdf_retriever import StructuredRetrievalResult


class Index:
    def __init__(self, hits): self.hits = hits
    def search(self, *args, **kwargs): return self.hits


class Retriever:
    def __init__(self, items): self.items = items
    async def retrieve(self, request): return StructuredRetrievalResult(evidence_items=self.items, metadata={"branch": "direct"})


def test_public_bundle_contract_is_stable_for_direct_table_empty_and_error_branches():
    request = RetrievalRequest("q", "question")
    direct = RetrievalMechanism(object(), structured_retriever=Retriever([EvidenceItem("E1", Assertion("s", "p", "o"), [SourceChunk("c", "d", "text")], relevance_score=0.9)]))
    table = RetrievalMechanism(object(), table_indices=[Index([TableEvidence("t", "d", ["h"], [["v"]], [0], combined_score=0.9)])])
    empty = RetrievalMechanism(object())

    class Broken:
        def search(self, *args, **kwargs): raise RuntimeError("broken")
    error = RetrievalMechanism(object(), chunk_indices=[Broken()])

    for mechanism, expected in ((direct, "success"), (table, "success"), (empty, "empty"), (error, "error")):
        bundle = asyncio.run(mechanism.retrieve_evidence(request))
        assert bundle.status == expected
        assert bundle.query_id == "q"
        assert isinstance(bundle.evidence_items, list)
        assert isinstance(bundle.table_evidence, list)
        assert isinstance(bundle.retrieval_metadata, dict)


def test_escalation_contract_records_ordered_stages():
    class Escalator:
        async def retrieve(self, request):
            if request.retrieval_config.get("escalation_stage"):
                return StructuredRetrievalResult([EvidenceItem("E1", Assertion("s", "p", "o"), [], relevance_score=0.9)])
            return StructuredRetrievalResult()

    bundle = asyncio.run(RetrievalMechanism(object(), structured_retriever=Escalator()).retrieve_evidence(RetrievalRequest("q", "question")))
    assert bundle.status == "success"
    assert bundle.retrieval_metadata["escalation_stages"] == ["normal", "broaden_candidates"]
