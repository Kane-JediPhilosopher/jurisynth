from __future__ import annotations

from jurisynth.summarize_image_processing_log import summarise


def test_summarise_image_processing_log(tmp_path) -> None:
    log = tmp_path / "images.log"
    log.write_text(
        "\n".join((
            "[Image Processor] Loading image manifests from eu_legislation/batch_0009/image_store",
            "[Image Processor] Eligible image assets loaded: 3",
            "[Image Processor] Progress 3/3 (100.0%) | success=3 error=0 | avg=1.50 images/s | elapsed=0.1 min",
            "[Image Processor] Artifacts complete | indexed=3 | errors=0",
            "[Image Processor] Loading image manifests from eu_legislation/batch_0010/image_store",
            "[Image Processor] Eligible image assets loaded: 0",
            "[Image Processor] Artifacts complete | indexed=0 | errors=0",
        )),
        encoding="utf-8",
    )
    summary = summarise(log)
    assert summary["completed_batch_runs"] == 2
    assert summary["batches_with_eligible_images"] == 1
    assert summary["eligible_images"] == 3
    assert summary["indexed_images"] == 3
    assert summary["recorded_processing_errors"] == 0
