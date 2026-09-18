"""Benchmark CPU-only NLI contradiction scoring on captured, local claim text.

This script never calls NVIDIA NIM or the retrieval pipeline.  It scores the
37 claims captured in the organized smoke as all unique unordered pairs.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from itertools import combinations
from pathlib import Path

import psutil

from jurisynth.agentic_reasoner.contradiction import ContradictionCandidate, NLIContradictionScorer, RetrievedAssertion


_STOPWORDS = {
    "about", "also", "and", "are", "been", "being", "could", "does", "each", "for", "from", "has", "have",
    "into", "may", "must", "not", "only", "should", "shall", "such", "than", "that", "the", "their", "there",
    "these", "they", "this", "those", "under", "were", "what", "when", "where", "whether", "which", "with", "would",
}


def _experimental_high_recall_gate(candidate: ContradictionCandidate) -> bool:
    """Benchmark-only gate. It is never enabled in production without passing comparison."""
    if set(candidate.assertion_a.evidence_refs) & set(candidate.assertion_b.evidence_refs):
        return True
    tokens = lambda text: {item for item in text.casefold().split() if len(item) >= 4 and item.isalnum() and item not in _STOPWORDS}
    return len(tokens(candidate.assertion_a.text) & tokens(candidate.assertion_b.text)) >= 4


def _claims(path: Path) -> list[tuple[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    claims: list[tuple[str, str]] = []
    for node in payload["result"]["node_results"].values():
        for claim in (node.get("answer") or {}).get("claims", []):
            if claim.get("claim_id") and claim.get("text"):
                claims.append((claim["claim_id"], claim["text"]))
    return claims


def _pairs(claims: list[tuple[str, str]]) -> list[ContradictionCandidate]:
    return [
        ContradictionCandidate(
            RetrievedAssertion(a_id, a_id, "captured_claim", "a", a_text, (), (), ()),
            RetrievedAssertion(b_id, b_id, "captured_claim", "b", b_text, (), (), ()),
        )
        for (a_id, a_text), (b_id, b_text) in combinations(claims, 2)
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=Path("jurisynth/run_outputs/global_complex_ai_medical_organized_super_20260917.json"))
    parser.add_argument("--output", type=Path, default=Path("jurisynth/evaluation_artifacts/cpu_nli_contradiction_benchmark.json"))
    parser.add_argument("--batch-sizes", type=int, nargs="+", default=[8, 16, 32])
    parser.add_argument("--threshold", type=float, default=0.95)
    parser.add_argument("--compare-gate", action="store_true", help="Compare the bounded evidence-or-lexical gate with exhaustive NLI.")
    args = parser.parse_args()
    claims = _claims(args.fixture)
    if len(claims) != 37:
        raise ValueError(f"Expected the captured organized-smoke fixture to contain 37 claims; found {len(claims)}.")
    pairs_started = time.perf_counter()
    candidates = _pairs(claims)
    pair_construction_seconds = time.perf_counter() - pairs_started
    if len(candidates) != 666:
        raise AssertionError(f"Expected 666 unique unordered pairs; found {len(candidates)}.")
    process = psutil.Process(os.getpid())
    scorer = NLIContradictionScorer(batch_size=args.batch_sizes[0], device="cpu", local_files_only=True)
    results: list[dict[str, object]] = []
    for batch_size in args.batch_sizes:
        scorer.batch_size = batch_size
        cpu_before = process.cpu_times()
        rss_before = process.memory_info().rss
        scores = scorer.score(candidates)
        cpu_after = process.cpu_times()
        metrics = dict(scorer.last_metrics)
        elapsed = float(metrics["total_seconds"])
        results.append({
            **metrics,
            "pair_construction_seconds": round(pair_construction_seconds, 6),
            "pairs_per_second": round(len(candidates) / elapsed, 3) if elapsed else None,
            "threshold_passing_pairs": sum(score >= args.threshold for score in scores),
            "rss_before_bytes": rss_before,
            "rss_after_bytes": process.memory_info().rss,
            "cpu_seconds": round((cpu_after.user + cpu_after.system) - (cpu_before.user + cpu_before.system), 6),
        })
    exhaustive_positive_pairs = [
        [candidate.assertion_a.assertion_id, candidate.assertion_b.assertion_id]
        for candidate, score in zip(candidates, scores)
        if score >= args.threshold
    ]
    gate_result = None
    if args.compare_gate:
        gated = [candidate for candidate in candidates if _experimental_high_recall_gate(candidate)]
        scorer.batch_size = min(32, max(args.batch_sizes))
        gated_scores = scorer.score(gated)
        gated_positive_pairs = {
            (candidate.assertion_a.assertion_id, candidate.assertion_b.assertion_id)
            for candidate, score in zip(gated, gated_scores)
            if score >= args.threshold
        }
        exhaustive_positive_set = {tuple(pair) for pair in exhaustive_positive_pairs}
        gate_result = {
            "strategy": "shared evidence/resource OR at least four shared substantive tokens",
            "gated_pair_count": len(gated),
            "reduction_percent": round((1 - len(gated) / len(candidates)) * 100, 3),
            "batch_size": scorer.batch_size,
            "metrics": dict(scorer.last_metrics),
            "threshold_passing_pairs": len(gated_positive_pairs),
            "exhaustive_positive_pairs_preserved": len(exhaustive_positive_set & gated_positive_pairs),
            "exhaustive_positive_pairs_missed": [list(pair) for pair in sorted(exhaustive_positive_set - gated_positive_pairs)],
        }
    output = {
        "fixture": str(args.fixture), "claim_count": len(claims), "raw_pair_count": len(candidates),
        "pair_identity": "unique unordered (A,B); no self-pairs or reverse duplicates",
        "model": scorer.model_name, "device": scorer.device, "max_length": scorer.max_length,
        "threshold": args.threshold, "label_mapping": list(scorer.LABELS), "results": results,
        "exhaustive_positive_pairs": exhaustive_positive_pairs, "gate_comparison": gate_result,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "pairs": len(candidates), "runs": len(results)}))


if __name__ == "__main__":
    main()
