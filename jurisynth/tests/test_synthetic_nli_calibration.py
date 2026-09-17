from __future__ import annotations

from jurisynth.run_synthetic_nli_calibration import LabelledPair, calibrate, metrics


class FakeScorer:
    model_name = "fake"

    def score(self, candidates):
        return [0.95 if candidate.claim_a_id == "c1" else 0.05 for candidate in candidates]


def test_metrics_and_calibration_select_a_high_precision_threshold() -> None:
    pairs = [LabelledPair("c1", "A", "not A", True), LabelledPair("c2", "A", "B", False)]
    result = calibrate(pairs, FakeScorer())
    assert result["provisional_metrics"]["precision"] == 1.0
    assert result["provisional_metrics"]["recall"] == 1.0
    assert metrics([True, False], [0.9, 0.1], 0.8)["true_positive"] == 1
