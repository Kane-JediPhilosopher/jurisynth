"""Replay assertion-level contradiction detection over one captured EvidenceBundle.

This is a local CPU-only validation utility. It never invokes NVIDIA NIM and
never reads the KG or reruns retrieval.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import asdict
from pathlib import Path

from jurisynth.agentic_reasoner.contradiction import ContradictionDetector, NLIContradictionScorer
from jurisynth.contracts import Assertion, EvidenceBundle, EvidenceItem, SourceChunk


def _load_bundle(path: Path, limit: int | None) -> EvidenceBundle:
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload.get("evidence_items", [])
    if limit is not None:
        records = records[:limit]
    items = [
        EvidenceItem(
            evidence_id=str(record["evidence_id"]),
            assertion=Assertion(**record["assertion"]),
            source_chunks=[SourceChunk(**source) for source in record.get("source_chunks", [])],
            modifiers=list(record.get("modifiers", [])),
            retrieval_origins=list(record.get("retrieval_origins", [])),
            community_ids=list(record.get("community_ids", [])),
            relevance_score=record.get("relevance_score"),
            structural_score=record.get("structural_score"),
            coherence_score=record.get("coherence_score"),
            matched_concept_ids=list(record.get("matched_concept_ids", [])),
            instrument_scope=record.get("instrument_scope", "unknown"),
        )
        for record in records
    ]
    return EvidenceBundle(str(payload.get("query_id", "captured")), str(payload.get("status", "success")), items)


async def run(source: Path, limit: int | None) -> dict[str, object]:
    bundle = _load_bundle(source, limit)
    detector = ContradictionDetector(NLIContradictionScorer(device="cpu", batch_size=32), threshold=0.95)
    conflicts = await detector.detect([bundle])
    valid_evidence_ids = {item.evidence_id for item in bundle.evidence_items}
    provenance_valid = all(
        conflict.assertion_a_provenance and conflict.assertion_b_provenance
        and set(conflict.assertion_a_evidence_refs).issubset(valid_evidence_ids)
        and set(conflict.assertion_b_evidence_refs).issubset(valid_evidence_ids)
        for conflict in conflicts
    )
    return {
        "kind": "captured EvidenceBundle replay; local CPU NLI; no NVIDIA NIM; no retrieval rerun",
        "source": str(source),
        "source_evidence_limit": limit,
        "metrics": detector.last_metrics,
        "all_surfaced_pairs_resolve_to_assertion_provenance": provenance_valid,
        "potential_contradictions": [asdict(conflict) for conflict in conflicts],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source", type=Path,
        default=Path("jurisynth/run_outputs/architecture_fix_v2_phase3_q003_batched/bundle_00.json"),
    )
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument(
        "--output", type=Path,
        default=Path("jurisynth/evaluation_artifacts/assertion_contradiction_replay.json"),
    )
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        raise ValueError("--limit must be positive")
    result = asyncio.run(run(args.source, args.limit))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "metrics": result["metrics"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
