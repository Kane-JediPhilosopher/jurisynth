from jurisynth.contracts import SourceChunk
from jurisynth.run_global_chunk_evaluation import (
    ChunkEvalCase,
    _controlled_query,
    _query_is_answerable,
    _score_case,
    _stratified_select,
)


def _case(**overrides):
    values = {
        "case_id": "c1",
        "query": "q",
        "expected_document_id": "doc",
        "expected_chunk_id": "chunk_2",
        "source_text_excerpt": "source",
        "expected_assertion": ("s", "p", "o"),
        "acceptable_alternate_chunk_ids": ("chunk_3",),
        "canonical_source": {"document_id": "doc"},
        "batch_id": "batch_1",
        "document_family": "official_journal_l",
        "object_type": "uri",
    }
    values.update(overrides)
    return ChunkEvalCase(**values)


def test_controlled_query_does_not_copy_source_text():
    query = _controlled_query(
        "http://jurisynth/data/the_provider",
        "http://jurisynth/data/shall_keep_records",
    )
    assert query == "According to the source, what is stated about 'the provider' in relation to 'shall keep records'?"
    assert _query_is_answerable(
        "http://jurisynth/data/the_provider",
        "http://jurisynth/data/shall_keep_records",
        "The provider shall keep records for ten years.",
    )


def test_exact_and_alternate_recovery_are_scored_separately():
    exact = SourceChunk("chunk_2", "doc", "gold", similarity=0.9)
    alternate = SourceChunk("chunk_3", "doc", "duplicate", similarity=0.8)
    other = SourceChunk("chunk_1", "other", "noise", similarity=0.99)

    exact_result = _score_case(_case(), [other, exact], [other, exact], 0.1, True)
    alternate_result = _score_case(_case(), [other, alternate], [other, alternate], 0.1, True)

    assert exact_result.exact_rank == 2 and exact_result.source_document_recalled
    assert not exact_result.alternate_valid_recovery
    assert alternate_result.exact_rank is None and alternate_result.source_document_recalled
    assert alternate_result.alternate_valid_recovery


def test_wrong_chunk_from_correct_document_is_not_answer_bearing():
    wrong = SourceChunk("chunk_9", "doc", "related", similarity=0.9)
    result = _score_case(_case(), [wrong], [wrong], 0.1, True)

    assert result.retrieval_status == "correct_document_wrong_chunk"
    assert result.correct_document_candidate_recalled
    assert not result.source_document_recalled


def test_stratified_selection_is_deterministic_and_bounded():
    candidates = [
        {
            "document_family": "official_journal_l" if index % 2 else "legacy_celex",
            "object_type": "uri" if index % 3 else "literal",
            "chunk_id": f"chunk_{index + 1}",
            "value": index,
        }
        for index in range(20)
    ]

    first = _stratified_select(candidates, 10, 7)
    second = _stratified_select(candidates, 10, 7)

    assert [item["value"] for item in first] == [item["value"] for item in second]
    assert len(first) == 10
