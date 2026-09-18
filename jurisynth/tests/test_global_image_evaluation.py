from __future__ import annotations

import asyncio
import json
from pathlib import Path

from jurisynth.contracts import ImageEvidence
from jurisynth.run_global_image_evaluation import (
    ImageEvalCase,
    _RecordingVisionClient,
    _rank_document,
    _rank_image,
    read_cases,
    summarize,
)


def _image(image_id: str, document_id: str) -> ImageEvidence:
    return ImageEvidence(image_id, document_id, "batch/image.jpg", "image/jpeg", "caption", "", similarity=0.8)


def test_image_and_document_ranks_are_distinct() -> None:
    hits = [_image("other", "doc"), _image("target", "doc")]
    assert _rank_document(hits, "doc") == 1
    assert _rank_image(hits, "target") == 2


def test_recording_client_confirms_image_bytes() -> None:
    client = _RecordingVisionClient()
    response = asyncio.run(client.chat.completions.create(messages=[
        {"role": "user", "content": [{
            "type": "image_url", "image_url": {"url": "data:image/png;base64," + "A" * 40}
        }]}
    ]))
    assert response.choices[0].message.content
    assert client.completions.received_image_bytes is True


def test_summary_keeps_retrieval_and_expansion_metrics_separate() -> None:
    from jurisynth.run_global_image_evaluation import ImageEvalResult

    result = ImageEvalResult(
        "case", "query", "doc", "target", True, True, 1, 1, 1, "exact", None, 0.1,
        True, True, "path", True, True, True, True, True, False, False, False,
        [],
    )
    summary = summarize([result], 1.0, 1024, 10, 100)
    assert summary["image_recall_at_k"]["1"] == 1.0
    assert summary["local_expansion_contract_successes"] == 1
    assert summary["live_provider_attempts"] == 0


def test_frozen_case_round_trip(tmp_path: Path) -> None:
    raw = {
        "case_id": "case",
        "query": "query",
        "expected_document_id": "doc",
        "expected_image_id": "doc:image:001",
        "expected_relative_path": "batch/image.jpg",
        "stored_caption": "caption",
        "image_local_context": {},
        "canonical_source": {"document_id": "doc"},
        "alternate_valid_image_ids": [],
        "source_asset": "asset",
        "construction_method": "frozen",
    }
    path = tmp_path / "cases.jsonl"
    path.write_text(json.dumps(raw) + "\n", encoding="utf-8")
    case = read_cases(path)[0]
    assert isinstance(case, ImageEvalCase)
    assert case.alternate_valid_image_ids == ()
