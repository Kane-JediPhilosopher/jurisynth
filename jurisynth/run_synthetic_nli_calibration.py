"""Calibrate a provisional NLI contradiction threshold on disclosed synthetic data.

The result is a component smoke/calibration aid only. It is not evidence that
the NLI model detects legal contradictions in Jurisynth outputs.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from jurisynth.agentic_reasoner.contradiction import ContradictionCandidate, NLIContradictionScorer, RetrievedAssertion


@dataclass(frozen=True, slots=True)
class LabelledPair:
    case_id: str
    claim_a: str
    claim_b: str
    contradiction: bool


def read_pairs(path: Path) -> list[LabelledPair]:
    values: list[LabelledPair] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        values.append(LabelledPair(str(payload["case_id"]), str(payload["claim_a"]), str(payload["claim_b"]), payload["label"] == "contradiction"))
    if not values or not any(value.contradiction for value in values) or all(value.contradiction for value in values):
        raise ValueError("Synthetic NLI calibration needs both contradiction and non-contradiction cases.")
    return values


def metrics(labels: list[bool], scores: list[float], threshold: float) -> dict[str, float | int]:
    predictions = [score >= threshold for score in scores]
    true_positive = sum(label and prediction for label, prediction in zip(labels, predictions))
    false_positive = sum(not label and prediction for label, prediction in zip(labels, predictions))
    false_negative = sum(label and not prediction for label, prediction in zip(labels, predictions))
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"threshold": threshold, "true_positive": true_positive, "false_positive": false_positive, "false_negative": false_negative, "precision": precision, "recall": recall, "f1": f1}


def calibrate(pairs: list[LabelledPair], scorer: NLIContradictionScorer, *, fixed_threshold: float | None = None) -> dict[str, object]:
    candidates = [ContradictionCandidate(
        RetrievedAssertion(pair.case_id, pair.case_id, "synthetic", "a", pair.claim_a, (), (), ()),
        RetrievedAssertion(f"{pair.case_id}_b", pair.case_id, "synthetic", "b", pair.claim_b, (), (), ()),
    ) for pair in pairs]
    scores = scorer.score(candidates)
    labels = [pair.contradiction for pair in pairs]
    if fixed_threshold is not None and not 0 <= fixed_threshold <= 1:
        raise ValueError("Fixed threshold must be between 0 and 1.")
    candidates_metrics = [metrics(labels, scores, fixed_threshold)] if fixed_threshold is not None else [metrics(labels, scores, round(value / 100, 2)) for value in range(50, 100, 5)]
    selected = max(candidates_metrics, key=lambda value: (float(value["f1"]), float(value["precision"]), float(value["threshold"])))
    return {
        "dataset_kind": "synthetic; hand-authored component calibration only",
        "measurement_kind": "fixed_threshold_holdout" if fixed_threshold is not None else "in_sample_threshold_selection",
        "model": scorer.model_name,
        "case_count": len(pairs),
        "contradiction_count": sum(labels),
        "non_contradiction_count": len(labels) - sum(labels),
        "threshold_candidates": candidates_metrics,
        "provisional_threshold": selected["threshold"],
        "provisional_metrics": selected,
        "scores": [{"case_id": pair.case_id, "label": "contradiction" if pair.contradiction else "non_contradiction", "score": score} for pair, score in zip(pairs, scores)],
        "limitation": "Do not treat this synthetic result as legal-domain validation or enable it as the default contradiction detector without a reviewed evidence-linked set.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=Path("jurisynth/evaluation_artifacts/synthetic_contradiction_nli.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("jurisynth/evaluation_artifacts/synthetic_nli_calibration.json"))
    parser.add_argument("--model", default="cross-encoder/nli-deberta-v3-base")
    parser.add_argument("--fixed-threshold", type=float, help="Evaluate a previously selected threshold without tuning on these labels.")
    args = parser.parse_args()
    result = calibrate(read_pairs(args.cases), NLIContradictionScorer(model_name=args.model, device="cpu"), fixed_threshold=args.fixed_threshold)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("model", "case_count", "contradiction_count", "provisional_threshold", "provisional_metrics")}, indent=2))


if __name__ == "__main__":
    main()
