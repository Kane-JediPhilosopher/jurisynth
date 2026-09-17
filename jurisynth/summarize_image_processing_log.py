"""Summarise a corpus Image Processor log without exposing credentials or captions."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


_BATCH = re.compile(r"Loading image manifests from .*?/(batch_\d+)/image_store")
_ELIGIBLE = re.compile(r"Eligible image assets loaded: ([\d,]+)")
_PROGRESS = re.compile(
    r"Progress ([\d,]+)/([\d,]+).*?success=([\d,]+) error=([\d,]+).*?avg=([\d.]+) images/s \| elapsed=([\d.]+) min"
)
_COMPLETE = re.compile(r"Artifacts complete \| indexed=([\d,]+) \| errors=([\d,]+)")


def summarise(log_path: Path) -> dict[str, object]:
    runs: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    provider_error_lines = 0
    for raw_line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if re.search(r"\b(?:429|503|404)\b", line) or "caption failed" in line.lower():
            provider_error_lines += 1
        match = _BATCH.search(line)
        if match:
            current = {"batch": match.group(1), "eligible": None, "indexed": None, "errors": None}
            continue
        if current is None:
            continue
        if (match := _ELIGIBLE.search(line)):
            current["eligible"] = int(match.group(1).replace(",", ""))
        elif (match := _PROGRESS.search(line)):
            current.update({
                "last_progress": int(match.group(1).replace(",", "")),
                "last_total": int(match.group(2).replace(",", "")),
                "last_success": int(match.group(3).replace(",", "")),
                "last_errors": int(match.group(4).replace(",", "")),
                "images_per_second": float(match.group(5)),
                "elapsed_minutes": float(match.group(6)),
            })
        elif (match := _COMPLETE.search(line)):
            current["indexed"] = int(match.group(1).replace(",", ""))
            current["errors"] = int(match.group(2).replace(",", ""))
            runs.append(current)
            current = None

    eligible_runs = [run for run in runs if isinstance(run.get("eligible"), int) and run["eligible"] > 0]
    total_eligible = sum(int(run["eligible"]) for run in eligible_runs)
    total_indexed = sum(int(run["indexed"] or 0) for run in eligible_runs)
    total_errors = sum(int(run["errors"] or 0) for run in eligible_runs)
    elapsed_minutes = sum(float(run.get("elapsed_minutes") or 0) for run in eligible_runs)
    return {
        "source_log": str(log_path),
        "completed_batch_runs": len(runs),
        "batches_with_eligible_images": len(eligible_runs),
        "eligible_images": total_eligible,
        "indexed_images": total_indexed,
        "recorded_processing_errors": total_errors,
        "provider_error_log_lines": provider_error_lines,
        "reported_elapsed_minutes_sum": round(elapsed_minutes, 3),
        "mean_reported_images_per_second": round(total_indexed / (elapsed_minutes * 60), 4) if elapsed_minutes else None,
        "completed_runs": runs,
        "note": "Elapsed minutes are per-batch cumulative values logged by the processor. The run used a zero-provider-budget configuration, so completion time and reliability—not provider billing—are the reportable metrics; any external GPU rental is outside this log.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, default=Path("jurisynth/image_processing.log"))
    parser.add_argument("--output", type=Path, default=Path("jurisynth/evaluation_artifacts/image_processing_corpus_summary.json"))
    args = parser.parse_args()
    payload = summarise(args.log)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in payload.items() if key != "completed_runs"}, indent=2))


if __name__ == "__main__":
    main()
