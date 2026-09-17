import asyncio
from types import SimpleNamespace

from jurisynth.contracts import Assertion, EvidenceItem, RetrievalRequest, SourceChunk, TableEvidence
from jurisynth.retrieval_mech.mechanism import RetrievalMechanism
from jurisynth.retrieval_mech.config import RetrievalSettings
from jurisynth.retrieval_mech.document_metadata import InstrumentScopeContext
from jurisynth.retrieval_mech.rdf_retriever import StructuredRetrievalResult
from jurisynth.retrieval_mech.community_hierarchy import CommunityHierarchy, CommunityNode, CommunityOrientationBuilder
from jurisynth.retrieval_mech.community_summary import CommunitySummaryInput


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
        self.document_ids = []

    def search(self, query, embedder, table_top_k, row_top_k, *, document_ids=None):
        self.document_ids.append(document_ids)
        return []


class StaticScopeMetadata:
    def __init__(self, scopes):
        self.scopes = scopes

    def resolve_request_scope(self, request):
        return InstrumentScopeContext(
            frozenset({"citation:regulation:2024:1689"}), ("ai act",), "leaf_query"
        )

    def classify_document(self, document_id, context):
        return self.scopes.get(document_id, "unknown")

    def get(self, document_id):
        keys = {
            "ai-act": ("citation:regulation:2024:1689",),
            "gdpr": ("citation:regulation:2016:679",),
            "other-act": ("citation:regulation:2000:1",),
            "other": ("citation:regulation:2000:1",),
        }.get(document_id, ())
        return SimpleNamespace(canonical_keys=keys) if keys else None

    def document_ids_for_keys(self, keys):
        return {key: () for key in keys}


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


def test_table_pass_one_is_global_and_pass_two_receives_explicit_documents():
    table_index = RecordingTableIndex()
    mechanism = RetrievalMechanism(object(), table_indices=[table_index])
    request = RetrievalRequest("q4", "question", constraints={"document_ids": ["doc_a", "doc_b"]})

    assert asyncio.run(mechanism.retrieve_evidence(request)).status == "empty"
    assert table_index.document_ids == [None, {"doc_a", "doc_b"}]


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


def test_source_scoped_second_pass_is_deduplicated_and_records_origin():
    class ScopedTableIndex:
        def search(self, query, embedder, table_top_k, row_top_k, *, document_ids=None):
            if document_ids is None:
                return [TableEvidence("t-global", "unrelated", None, [["noise"]], [0], combined_score=0.2)]
            assert document_ids == {"d1"}
            return [TableEvidence("t-scoped", "d1", None, [["answer"]], [0], combined_score=0.9)]

    chunk = SourceChunk("c1", "d1", "answer-bearing text", similarity=0.8)
    mechanism = RetrievalMechanism(object(), chunk_indices=[FakeIndex([chunk])], table_indices=[ScopedTableIndex()])

    bundle = asyncio.run(mechanism.retrieve_evidence(_request()))

    assert [item.table_id for item in bundle.table_evidence] == ["t-scoped", "t-global"]
    assert bundle.table_evidence[0].retrieval_origins == ["source_document"]
    assert bundle.retrieval_metadata["modality_retrieval"]["source_document_ids"] == ["d1"]
    assert bundle.retrieval_metadata["modality_retrieval"]["table_pass_two_count"] == 1
    assert bundle.retrieval_metadata["modality_retrieval"]["table_pass_one_raw_count"] == 1
    assert bundle.retrieval_metadata["modality_retrieval"]["table_pass_two_raw_count"] == 1
    assert bundle.retrieval_metadata["modality_retrieval"]["table_merged_reranked_count"] == 2


def test_table_candidates_are_merged_deduplicated_and_reranked_once():
    class TwoPassTableIndex:
        def search(self, query, embedder, table_top_k, row_top_k, *, document_ids=None):
            if document_ids is None:
                return [
                    TableEvidence("t1", "d1", None, [["old"]], [0], combined_score=0.6),
                    TableEvidence("t2", "d2", None, [["global"]], [0], combined_score=0.7),
                ]
            return [TableEvidence("t1", "d1", None, [["better"]], [0], combined_score=0.95)]

    chunk = SourceChunk("c1", "d1", "answer", similarity=0.8)
    bundle = asyncio.run(RetrievalMechanism(
        object(), chunk_indices=[FakeIndex([chunk])], table_indices=[TwoPassTableIndex()],
    ).retrieve_evidence(_request()))

    assert [(item.table_id, item.combined_score) for item in bundle.table_evidence] == [
        ("t1", 0.95), ("t2", 0.7),
    ]
    assert bundle.table_evidence[0].retrieval_origins == ["global", "source_document"]


def test_corroborated_strong_chunk_avoids_unnecessary_structured_escalation():
    class Retriever:
        def __init__(self): self.stages = []
        async def retrieve(self, request):
            self.stages.append(request.retrieval_config.get("escalation_stage", "normal"))
            return StructuredRetrievalResult(evidence_items=[EvidenceItem(
                "E1", Assertion("s", "p", "o"),
                [SourceChunk("c1", "d1", "answer-bearing text")], relevance_score=0.2,
            )])

    retriever = Retriever()
    chunk = SourceChunk("c1", "d1", "answer-bearing text", similarity=0.8)
    bundle = asyncio.run(RetrievalMechanism(
        object(), chunk_indices=[FakeIndex([chunk])], structured_retriever=retriever,
    ).retrieve_evidence(_request()))

    assert bundle.status == "success"
    assert retriever.stages == ["normal"]
    assert bundle.retrieval_metadata["escalation_stages"] == ["normal"]


def test_weak_normal_retrieval_runs_one_bounded_broaden_candidates_attempt():
    retriever = EscalatingStructuredRetriever()
    bundle = asyncio.run(RetrievalMechanism(object(), structured_retriever=retriever).retrieve_evidence(_request()))

    assert bundle.status == "success"
    assert retriever.stages == ["normal", "broaden_candidates"]
    assert bundle.retrieval_metadata["escalation_stages"] == ["normal", "broaden_candidates"]
    assert [item.evidence_id for item in bundle.evidence_items] == ["E2"]


def test_out_of_scope_similarity_alone_cannot_establish_success():
    item = EvidenceItem(
        "E-cross", Assertion("s", "p", "o"),
        [SourceChunk("c", "other-act", "similar but legally out of scope")],
        relevance_score=0.99,
    )
    mechanism = RetrievalMechanism(
        object(), structured_retriever=StaticStructuredRetriever([item]),
        document_metadata=StaticScopeMetadata({"other-act": "cross_instrument"}),
    )

    bundle = asyncio.run(mechanism.retrieve_evidence(RetrievalRequest("q", "Duties under the AI Act")))

    assert bundle.status == "weak"
    assert bundle.evidence_items[0].instrument_scope == "cross_instrument"
    assert bundle.retrieval_metadata["instrument_scope"]["evidence_counts"] == {
        "in_scope": 0, "cross_instrument": 1, "unknown": 0,
    }


def test_two_instrument_scope_preserves_both_sources_and_provenance():
    class TwoInstrumentScope(StaticScopeMetadata):
        def resolve_request_scope(self, request):
            return InstrumentScopeContext(
                frozenset({
                    "citation:regulation:2024:1689",
                    "citation:regulation:2016:679",
                }),
                ("ai act", "gdpr"),
                "leaf_query",
            )

    ai_source = SourceChunk("ai-c", "ai-act", "AI Act duty")
    gdpr_source = SourceChunk("gdpr-c", "gdpr", "GDPR lawful basis")
    spill_source = SourceChunk("other-c", "other", "Other regulation")
    items = [
        EvidenceItem("E-ai", Assertion("provider", "must", "document"), [ai_source], relevance_score=0.8),
        EvidenceItem("E-gdpr", Assertion("controller", "must", "justify"), [gdpr_source], relevance_score=0.79),
        EvidenceItem("E-other", Assertion("actor", "may", "act"), [spill_source], relevance_score=0.99),
    ]
    mechanism = RetrievalMechanism(
        object(), structured_retriever=StaticStructuredRetriever(items),
        document_metadata=TwoInstrumentScope({
            "ai-act": "in_scope", "gdpr": "in_scope", "other": "cross_instrument",
        }),
    )

    bundle = asyncio.run(mechanism.retrieve_evidence(RetrievalRequest(
        "q", "How do the AI Act and GDPR interact?"
    )))

    assert bundle.status == "success"
    assert [item.evidence_id for item in bundle.evidence_items] == ["E-ai", "E-gdpr", "E-other"]
    assert bundle.evidence_items[0].source_chunks == [ai_source]
    assert bundle.evidence_items[1].source_chunks == [gdpr_source]
    assert bundle.retrieval_metadata["instrument_scope"]["evidence_counts"] == {
        "in_scope": 2, "cross_instrument": 1, "unknown": 0,
    }


def test_missing_named_instrument_runs_one_source_scoped_chunk_pass():
    class TwoInstrumentScope(StaticScopeMetadata):
        def resolve_request_scope(self, request):
            return InstrumentScopeContext(
                frozenset({
                    "citation:regulation:2024:1689",
                    "citation:regulation:2016:679",
                }),
                ("ai act", "gdpr"),
                "leaf_query",
            )

        def document_ids_for_keys(self, keys):
            return {
                key: (("gdpr",) if key == "citation:regulation:2016:679" else ())
                for key in keys
            }

    class ScopedChunkIndex:
        def __init__(self): self.document_calls = []
        def search(self, *_args): return []
        def search_documents(self, _query, _embedder, _top_k, *, document_ids):
            self.document_calls.append(document_ids)
            return [SourceChunk("gdpr-c", "gdpr", "GDPR grounded duty", similarity=0.9)]

    ai_item = EvidenceItem(
        "E-ai", Assertion("provider", "must", "document"),
        [SourceChunk("ai-c", "ai-act", "AI Act duty")], relevance_score=0.8,
    )
    chunk_index = ScopedChunkIndex()
    bundle = asyncio.run(RetrievalMechanism(
        object(), chunk_indices=[chunk_index],
        structured_retriever=StaticStructuredRetriever([ai_item]),
        document_metadata=TwoInstrumentScope({"ai-act": "in_scope", "gdpr": "in_scope"}),
    ).retrieve_evidence(RetrievalRequest("q", "How do the AI Act and GDPR interact?")))

    assert bundle.status == "success"
    assert chunk_index.document_calls == [{"gdpr"}]
    recovered = next(item for item in bundle.evidence_items if item.source_chunks[0].document_id == "gdpr")
    assert "instrument_source_scoped" in recovered.retrieval_origins
    scope = bundle.retrieval_metadata["instrument_scope"]
    assert scope["missing_target_keys"] == []
    assert scope["source_recovery"]["triggered"] is True


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


def test_dispersed_communities_use_only_persisted_descriptors_for_lazy_orientation():
    hierarchy = CommunityHierarchy(
        {
            "left": CommunityNode("left", 0, "root", member_ids=("e1",)),
            "right": CommunityNode("right", 0, "root", member_ids=("e2",)),
            "root": CommunityNode("root", 1, child_ids=("left", "right")),
        },
        "fixture",
    )

    class CommunityRetriever:
        async def retrieve(self, request):
            return StructuredRetrievalResult(
                metadata={"relevant_communities": [
                    {"community_id": "left", "score": 0.9},
                    {"community_id": "right", "score": 0.8},
                ]},
            )

    class Summarizer:
        def __init__(self): self.inputs = None
        async def summarize(self, community_id, inputs):
            self.inputs = (community_id, inputs)
            return "The selected graph regions concern two distinct topics."

    summarizer = Summarizer()
    mechanism = RetrievalMechanism(
        object(),
        structured_retriever=CommunityRetriever(),
        community_orientation_builder=CommunityOrientationBuilder(hierarchy, {"e1": "first", "e2": "second"}),
        community_descriptors={
            "left": CommunitySummaryInput("left", "Persisted left descriptor."),
            "right": CommunitySummaryInput("right", "Persisted right descriptor."),
        },
        community_summarizer=summarizer,
        community_summary_min_average_distance=2.0,
    )

    bundle = asyncio.run(mechanism.retrieve_evidence(_request()))

    assert bundle.community_summary == "Community orientation only — not legal evidence.\nThe selected graph regions concern two distinct topics."
    assert summarizer.inputs[0] == "root"
    assert [item.summary for item in summarizer.inputs[1]] == ["Persisted left descriptor.", "Persisted right descriptor."]
    assert bundle.retrieval_metadata["lazy_community_summary"]["trigger"] == "tree_dispersion"
