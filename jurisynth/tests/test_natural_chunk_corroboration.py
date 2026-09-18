from __future__ import annotations

import json
from pathlib import Path

from jurisynth.contracts import SourceChunk
from jurisynth.run_natural_chunk_corroboration import (
    NaturalChunkCase,
    _score_case,
    load_eligible_cases,
    summarize,
)


def _hit(document_id: str, chunk_id: str) -> SourceChunk:
    return SourceChunk(chunk_id=chunk_id, document_id=document_id, text="text", similarity=0.8)


def test_packet_selection_preserves_queries_and_marks_missing_chunk_gold(tmp_path: Path) -> None:
    packet = {
        "packet_version": "test",
        "case_count": 3,
        "eligible_after_adjudication": 2,
        "cases": [
            {
                "case_id": "a",
                "question": "Original natural question?",
                "review_status": "reviewed_pending_finalization",
                "external_adjudication": {"verdict": "strong_pass"},
                "expected_chunks": [{"document_id": "doc", "chunk_id": "chunk_1", "excerpt": "gold"}],
            },
            {
                "case_id": "b",
                "question": "Table-only question?",
                "review_status": "reviewed_pending_finalization",
                "external_adjudication": {"verdict": "revised"},
                "expected_chunks": [],
            },
            {
                "case_id": "c",
                "question": "Excluded?",
                "review_status": "excluded_pending_replacement",
                "external_adjudication": {"verdict": "exclude"},
                "expected_chunks": [{"document_id": "x", "chunk_id": "y"}],
            },
        ],
    }
    path = tmp_path / "packet.json"
    path.write_text(json.dumps(packet), encoding="utf-8")
    cases, metadata = load_eligible_cases(path)
    assert [case.query for case in cases] == ["Original natural question?", "Table-only question?"]
    assert metadata["selected_eligible_count"] == 2
    assert metadata["chunk_scoreable_count"] == 1
    assert cases[1].expected_chunk_id is None


def test_exact_and_same_document_wrong_chunk_are_distinct() -> None:
    case = NaturalChunkCase("a", "q", "pass", "doc", "chunk_1", "gold", "exact only")
    exact = _score_case(case, [_hit("doc", "chunk_1")], [_hit("doc", "chunk_1")], 0.1, True)
    wrong = _score_case(case, [_hit("doc", "chunk_2")], [_hit("doc", "chunk_2")], 0.1, True)
    assert exact.answer_bearing_source_recalled is True
    assert wrong.any_candidate_correct_document_recalled is True
    assert wrong.answer_bearing_source_recalled is False
    assert wrong.failure_category == "correct_document_retrieved_but_wrong_non_answer_bearing_chunk"


def test_unscored_case_does_not_inflate_metrics() -> None:
    scored_case = NaturalChunkCase("a", "q", "pass", "doc", "chunk_1", "gold", "exact only")
    unscored_case = NaturalChunkCase("b", "q2", "revised", None, None, None, "no chunk gold")
    scored = _score_case(scored_case, [_hit("doc", "chunk_1")], [_hit("doc", "chunk_1")], 0.1, True)
    unscored = _score_case(unscored_case, [_hit("other", "chunk_1")], [_hit("other", "chunk_1")], 0.2, None)
    summary = summarize([scored, unscored], 1.0, 1024, 10, 100)
    assert summary["scored_case_count"] == 1
    assert summary["eligible_case_count"] == 2
    assert summary["exact_expected_chunk_recall"] == 1.0
    assert summary["failure_breakdown"]["gold_annotation_insufficient_for_chunk_scoring"] == 1
