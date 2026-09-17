from __future__ import annotations

from jurisynth.prepare_global_candidate_packet import candidates


def test_global_candidate_allocation_is_complete_and_review_only() -> None:
    values = candidates()
    assert len(values) == 20
    assert {value["case_id"] for value in values} == {f"global_natural_{number:03d}" for number in range(1, 21)}
    assert sum(value["category"] == "obligation_prohibition" for value in values) == 3
    assert sum(value["category"] == "definition_scope" for value in values) == 4
    assert sum(value["category"] == "procedure_deadline" for value in values) == 4
    assert sum(value["category"] == "cross_document_dependent" for value in values) == 6
    assert sum(value["category"] == "table" for value in values) == 3
    assert sum(value["review_status"] == "excluded_pending_replacement" for value in values) == 6
    assert values[-1]["table"][2] == (0, 1, 2)
