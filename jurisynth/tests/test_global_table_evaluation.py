from __future__ import annotations

import json
from pathlib import Path

from jurisynth.contracts import TableEvidence
from jurisynth.run_global_table_evaluation import (
    TableEvalCase,
    _rank_table,
    _row_ranks,
    _score_case,
    read_cases,
    summarize,
)


def _case(row_ids: tuple[int, ...] = (1,)) -> TableEvalCase:
    return TableEvalCase(
        "case", "query", "doc", "table", row_ids, (), tuple((str(row),) for row in row_ids),
        {"document_id": "doc"}, (), "fixture", "frozen",
    )


def _hit(document: str, table: str, row: int, score: float = 0.8) -> TableEvidence:
    return TableEvidence(table, document, None, [[str(row)]], [row], score, score, score * score)


def test_table_and_row_ranks_are_separate() -> None:
    case = _case((1, 2))
    tables = [
        {"rank": 1, "document_id": "other", "table_id": "x", "score": 0.9},
        {"rank": 2, "document_id": "doc", "table_id": "table", "score": 0.8},
    ]
    rows = [_hit("doc", "table", 1), _hit("other", "x", 0), _hit("doc", "table", 2)]
    assert _rank_table(tables, "doc", "table") == 2
    assert _row_ranks(rows, case) == {1: 1, 2: 3}


def test_correct_table_wrong_row_is_not_answer_bearing() -> None:
    case = _case()
    tables = [{"rank": 1, "document_id": "doc", "table_id": "table", "score": 0.9}]
    result = _score_case(case, tables, [_hit("doc", "table", 3)], tables, [_hit("doc", "table", 3)], True, True, 0.1)
    assert result.table_rank == 1
    assert result.all_expected_rows_rank is None
    assert result.failure_category == "correct_table_retrieved_but_wrong_row"


def test_summary_uses_all_rows_for_case_recall() -> None:
    case = _case((1, 2))
    tables = [{"rank": 1, "document_id": "doc", "table_id": "table", "score": 0.9}]
    result = _score_case(case, tables, [_hit("doc", "table", 1)], tables, [_hit("doc", "table", 1)], True, True, 0.1)
    summary = summarize([result], 1.0, 1024, 10, 100)
    assert summary["table_recall_at_k"]["1"] == 1.0
    assert summary["row_recall_at_k"]["10"] == 0.0
    assert summary["answer_bearing_row_micro_recall_at_10"] == 0.5


def test_frozen_case_round_trip(tmp_path: Path) -> None:
    raw = as_json = {
        "case_id": "case",
        "query": "query",
        "expected_document_id": "doc",
        "expected_table_id": "table",
        "expected_row_ids": [1],
        "expected_headers": ["h"],
        "expected_rows": [["v"]],
        "canonical_source": {"document_id": "doc"},
        "alternate_valid_targets": [],
        "source_asset": "asset",
        "query_method": "frozen",
    }
    path = tmp_path / "cases.jsonl"
    path.write_text(json.dumps(raw) + "\n", encoding="utf-8")
    case = read_cases(path)[0]
    assert case.expected_row_ids == (1,)
    assert case.expected_rows == (("v",),)
