from rdflib import Dataset, Namespace

from jurisynth.contracts import Assertion, EvidenceBundle, EvidenceItem, SourceChunk, TableEvidence
import asyncio

from jurisynth.retrieval_evaluation import NaturalRetrievalEvalCase, TableRetrievalEvalCase, RetrievalEvalCase, RetrievalEvalResult, build_assertion_cases, build_stratified_table_cases, build_table_cases, evaluate_bundle, evaluate_table_bundle, read_natural_cases, run_evaluation, run_natural_evaluation, run_table_evaluation, select_review_items, summarize_natural_results, summarize_results, summarize_table_results, write_results_jsonl, write_review_items_jsonl, write_summary_json, write_table_results_jsonl, write_table_summary_json


EX = Namespace("https://example.test/")
CHUNK = Namespace("http://jurisynth/source/chunk/")


def test_natural_cases_measure_expected_source_recovery_without_claiming_answer_quality(tmp_path):
    source = tmp_path / "natural.jsonl"
    source.write_text('{"case_id":"n1","query":"natural question","expected_document_id":"doc","expected_chunk_ids":["chunk-1"]}\n', encoding="utf-8")
    case = read_natural_cases(source)[0]

    class Mechanism:
        async def retrieve_evidence(self, request):
            return EvidenceBundle("n1", "weak", [
                EvidenceItem("E1", Assertion("s", "p", "o"), [SourceChunk("chunk-1", "doc", "excerpt")])
            ])

    result = asyncio.run(run_natural_evaluation([case], Mechanism()))[0]
    assert result.expected_document_recalled and result.expected_chunk_recalled
    assert summarize_natural_results([result])["expected_chunk_recall"] == 1.0


def test_cases_use_only_semantic_chunk_graphs_and_score_provenance_separately():
    dataset = Dataset()
    graph_id = CHUNK["doc_chunk_1"]
    dataset.graph(graph_id).add((EX.controller, EX.must_provide, EX.information))
    dataset.graph(EX.provenance).add((EX.controller, EX.ignored, EX.information))
    source = SourceChunk("chunk_1", "doc", "A controller must provide information.")
    cases = build_assertion_cases(dataset, lambda identifier: source if identifier == graph_id else None)
    assert len(cases) == 1
    assert "https://example.test/" not in cases[0].query
    assert "must provide" in cases[0].query

    bundle = EvidenceBundle(
        "q1",
        "success",
        [EvidenceItem("E1", Assertion(*cases[0].expected_assertion), [source])],
        retrieval_metadata={"direct_chunk_matches": [{"chunk_id": "chunk_1"}]},
    )
    result = evaluate_bundle(cases[0], bundle)
    assert result.assertion_recalled and result.provenance_valid and result.direct_chunk_recalled
    assert result.subject_entity_recalled and result.object_entity_recalled and result.predicate_recalled
    assert result.expected_assertion_rank == 1
    assert result.retrieved_evidence[0]["source_chunks"][0]["text_excerpt"] == source.text
    assert summarize_results([result])["assertion_recall"] == 1.0
    assert summarize_results([result])["assertion_mrr"] == 1.0


def test_legacy_subject_object_query_style_is_explicit_and_reproducible():
    dataset = Dataset()
    graph_id = CHUNK["doc_chunk_1"]
    dataset.graph(graph_id).add((EX.controller, EX.must_provide, EX.information))
    source = SourceChunk("chunk_1", "doc", "text")

    case = build_assertion_cases(
        dataset,
        lambda identifier: source if identifier == graph_id else None,
        query_style="legacy_subject_object",
    )[0]

    assert "relationship is stated between" in case.query
    assert "must provide" not in case.query


def test_provenance_failure_does_not_hide_assertion_recall():
    case = build_assertion_cases(
        (dataset := Dataset()), lambda _: SourceChunk("expected", "doc", "text"), limit=0
    )
    # Construct directly because an empty limit intentionally produces no cases.
    from jurisynth.retrieval_evaluation import RetrievalEvalCase
    case = RetrievalEvalCase("c1", "q", ("s", "p", "o"), ("expected",))
    bundle = EvidenceBundle("q", "weak", [EvidenceItem("E1", Assertion("s", "p", "o"), [SourceChunk("other", "doc", "text")])])
    result = evaluate_bundle(case, bundle)
    assert result.assertion_recalled and not result.provenance_valid


def test_direct_chunk_recall_is_scored_separately_from_rdf_provenance():
    case = RetrievalEvalCase("c1", "q", ("s", "p", "o"), ("expected",))
    bundle = EvidenceBundle(
        "q",
        "weak",
        [EvidenceItem("E1", Assertion("s", "p", "o"), [SourceChunk("other", "doc", "text")])],
        retrieval_metadata={"direct_chunk_matches": [{"chunk_id": "expected"}]},
    )

    result = evaluate_bundle(case, bundle)

    assert result.assertion_recalled and not result.provenance_valid and result.direct_chunk_recalled


def test_runner_uses_one_retrieval_call_per_case():
    case = RetrievalEvalCase("c1", "q", ("s", "p", "o"), ("chunk",))

    class Mechanism:
        async def retrieve_evidence(self, request):
            return EvidenceBundle(request.query_id, "success", [EvidenceItem("E1", Assertion("s", "p", "o"), [SourceChunk("chunk", "doc", "text")])])

    results = asyncio.run(run_evaluation([case], Mechanism()))
    assert results[0].assertion_recalled and results[0].provenance_valid


def test_results_are_written_as_auditable_jsonl(tmp_path):
    result = evaluate_bundle(
        RetrievalEvalCase("case_1", "q", ("s", "p", "o"), ("c1",)),
        EvidenceBundle("case_1", "empty"),
    )
    destination = tmp_path / "results.jsonl"

    write_results_jsonl([result], destination)

    assert '"case_id": "case_1"' in destination.read_text(encoding="utf-8")


def test_summary_is_written_as_json(tmp_path):
    result = evaluate_bundle(
        RetrievalEvalCase("case_1", "q", ("s", "p", "o"), ("c1",)),
        EvidenceBundle("case_1", "empty"),
    )

    summary = write_summary_json([result], tmp_path / "summary.json")

    assert summary["case_count"] == 1
    assert '"assertion_recall": 0.0' in (tmp_path / "summary.json").read_text(encoding="utf-8")


def test_review_selection_prioritizes_a_miss_and_writes_joined_records(tmp_path):
    cases = [
        RetrievalEvalCase("case_1", "q1", ("s1", "p", "o"), ("c1",)),
        RetrievalEvalCase("case_2", "q2", ("s2", "p", "o"), ("c2",)),
    ]
    results = [
        RetrievalEvalResult("case_1", "success", True, True),
        RetrievalEvalResult("case_2", "weak", False, False),
    ]

    items = select_review_items(cases, results, limit=2)
    destination = tmp_path / "review.jsonl"
    write_review_items_jsonl(items, destination)

    assert [item.case.case_id for item in items] == ["case_2", "case_1"]
    assert '"retrieval_status": "weak"' in destination.read_text(encoding="utf-8")
    assert '"human_review"' in destination.read_text(encoding="utf-8")


def test_table_cases_and_table_row_scoring_are_separate():
    class FakeTableIndex:
        table_metadata = [{"doc_id": "doc_1", "table_id": "table_1"}]

        def _load_table(self, document_id, table_id):
            return {"data": [["alpha", "beta"]]}

    case = build_table_cases(FakeTableIndex())[0]
    bundle = EvidenceBundle(
        "q1",
        "success",
        table_evidence=[TableEvidence("table_1", "doc_1", None, [["alpha", "beta"]], [0])],
    )
    result = evaluate_table_bundle(case, bundle)

    assert result.table_recalled and result.row_recalled
    assert summarize_table_results([result])["row_recall"] == 1.0


def test_stratified_table_cases_diversify_profiles_and_documents():
    class FakeTableIndex:
        table_metadata = [
            {"doc_id": "doc_numeric", "table_id": "table_1"},
            {"doc_id": "doc_mixed", "table_id": "table_2"},
            {"doc_id": "doc_text", "table_id": "table_3"},
        ]

        def _load_table(self, document_id, table_id):
            rows = {
                "doc_numeric": [["100", "200"]],
                "doc_mixed": [["Article", "12"]],
                "doc_text": [["data controller", "obligation"]],
            }
            return {"data": rows[document_id]}

    cases = build_stratified_table_cases(FakeTableIndex(), limit=3)

    assert {case.document_id for case in cases} == {"doc_numeric", "doc_mixed", "doc_text"}
    assert all(not case.query.startswith("Find the table row containing:") for case in cases)


def test_natural_table_case_does_not_repeat_the_entire_target_row():
    class FakeTableIndex:
        table_metadata = [{"doc_id": "doc_1", "table_id": "table_1"}]

        def _load_table(self, document_id, table_id):
            return {
                "context": "Approved installations",
                "header": ["Code", "Operator", "Reported value"],
                "data": [["BE0001", "Example Operator", "100 200 300"]],
            }

    case = build_stratified_table_cases(FakeTableIndex(), limit=1)[0]

    assert "BE0001" in case.query
    assert "100 200 300" not in case.query


def test_table_runner_and_persistence(tmp_path):
    case = TableRetrievalEvalCase("table_case", "q", "doc", "table", 0)

    class Mechanism:
        async def retrieve_evidence(self, request):
            return EvidenceBundle(request.query_id, "empty")

    results = asyncio.run(run_table_evaluation([case], Mechanism()))
    results_path = tmp_path / "table_results.jsonl"
    summary_path = tmp_path / "table_summary.json"
    write_table_results_jsonl(results, results_path)
    summary = write_table_summary_json(results, summary_path)

    assert results[0].retrieval_status == "empty"
    assert summary["row_recall"] == 0.0
    assert results_path.is_file() and summary_path.is_file()
