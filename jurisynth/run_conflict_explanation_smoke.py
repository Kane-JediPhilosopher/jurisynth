"""Live component smoke: cached CPU NLI followed by one NIM explanation batch.

The two claim pairs are synthetic: one contradiction and one temporal
non-conflict known to trigger a false positive in the synthetic NLI holdout.
This tests warning explanation and structured output, not legal accuracy.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import time
from dataclasses import asdict
from pathlib import Path

from jurisynth.agentic_reasoner.conflict_explanation import BatchedConflictExplainer
from jurisynth.agentic_reasoner.contradiction import ContradictionDetector, NLIContradictionScorer
from jurisynth.agentic_reasoner.llm import NIMConfig, OpenAICompatibleNIM
from jurisynth.agentic_reasoner.models import Claim, LeafAnswer
from jurisynth.contracts import Assertion, EvidenceBundle, EvidenceItem, SourceChunk
from jurisynth.run_nim_model_smokes import MODELS, REASONING_EFFORTS
from jurisynth.reasoning_log import ReasoningLog


def _write(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


async def run(args) -> dict[str, object]:
    config = NIMConfig.from_environment()
    if args.key_env:
        key = os.environ.get(args.key_env, "")
        if not key:
            raise RuntimeError(f"Missing API key variable {args.key_env}.")
        config = NIMConfig(key, config.base_url, MODELS[args.key_env], reasoning_effort=REASONING_EFFORTS.get(args.key_env, "none"))
    pairs = [item for item in (json.loads(line) for line in args.cases.read_text(encoding="utf-8").splitlines()) if item["case_id"] in {"hold_001", "hold_014"}]
    if len(pairs) != 2:
        raise ValueError("Expected synthetic holdout cases hold_001 and hold_014.")
    answers = []
    for pair in pairs:
        for suffix in ("a", "b"):
            identifier = pair["case_id"] + "_" + suffix
            text = pair["claim_" + suffix]
            evidence = EvidenceItem(identifier + "_E1", Assertion(pair["case_id"], "synthetic_rule", pair["case_id"] + "_object"), [SourceChunk(identifier, "synthetic_holdout", text)])
            answers.append(LeafAnswer(identifier, "supported", text, [Claim(identifier + ":C1", text, [evidence.evidence_id])], EvidenceBundle(identifier, "success", [evidence])))
    started = time.perf_counter()
    conflicts = await ContradictionDetector(NLIContradictionScorer(device="cpu"), threshold=0.95).detect(answers)
    nli_seconds = time.perf_counter() - started
    _write(args.output, {"status": "running", "phase": "nim_explanation", "model": config.model, "synthetic_pairs": pairs, "conflicts": [asdict(item) for item in conflicts], "nli_seconds": round(nli_seconds, 3)})
    if not conflicts:
        raise RuntimeError("NLI generated no warnings for the selected synthetic smoke pairs.")
    model = OpenAICompatibleNIM(config, reasoning_log=ReasoningLog(args.output.with_suffix(".events.jsonl"), "conflict_explanation_smoke"))
    try:
        explanation_started = time.perf_counter()
        explained = await BatchedConflictExplainer(model).explain(conflicts, answers)
    finally:
        await model.aclose()
    return {"status": "success", "kind": "synthetic component smoke; prose needs inspection", "model": config.model,
            "nli_seconds": round(nli_seconds, 3), "explanation_seconds": round(time.perf_counter() - explanation_started, 3),
            "synthetic_pairs": pairs, "conflicts": [asdict(item) for item in explained]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--key-env", choices=list(MODELS), help="Use this previously configured comparison-model key; default is the Reasoner model.")
    parser.add_argument("--cases", type=Path, default=Path("jurisynth/evaluation_artifacts/synthetic_contradiction_nli_holdout.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("jurisynth/run_outputs/conflict_explanation_smoke.json"))
    args = parser.parse_args()
    _write(args.output, {"status": "running", "phase": "nli", "kind": "synthetic component smoke"})
    try:
        result = asyncio.run(run(args))
    except Exception as exc:
        result = {"status": "failed", "error_type": type(exc).__name__, "status_code": getattr(exc, "status_code", None)}
    _write(args.output, result)
    print(json.dumps({"output": str(args.output), "status": result["status"]}))


if __name__ == "__main__":
    main()
