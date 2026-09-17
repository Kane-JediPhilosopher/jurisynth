"""Persist one bounded live NIM structured-output smoke result.

This command exists because hosted NIM calls can take longer than an interactive
terminal capture.  It records success or a sanitised transient failure without
ever writing an API key or raw request headers.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from jurisynth.agentic_reasoner.llm import (
    EvidenceGroundedLeafGenerator,
    NIMConfig,
    NIMRetryPolicy,
    OpenAICompatibleNIM,
)
from jurisynth.agentic_reasoner.models import LeafNode
from jurisynth.agentic_reasoner.qcompiler_translator import QCompilerTranslator
from jurisynth.contracts import Assertion, EvidenceBundle, EvidenceItem, SourceChunk


async def run_smoke(max_attempts: int) -> dict[str, object]:
    config = NIMConfig.from_environment()
    model = OpenAICompatibleNIM(
        config,
        retry_policy=NIMRetryPolicy(max_attempts=max_attempts, max_backoff_seconds=0, jitter_seconds=0),
    )
    payload: dict[str, object] = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model": config.model,
        "max_attempts": max_attempts,
    }
    try:
        compilation = await QCompilerTranslator(model).compile(
            "What is the scope of Regulation (EU) 2016/679?"
        )
        evidence = EvidenceBundle(
            "smoke_leaf", "success", [
                EvidenceItem(
                    "E1",
                    Assertion("Regulation (EU) 2016/679", "has scope", "processing of personal data"),
                    [SourceChunk("smoke_chunk", "smoke_document", "Regulation (EU) 2016/679 concerns processing of personal data.")],
                )
            ],
        )
        answer = await EvidenceGroundedLeafGenerator(model)(
            LeafNode("smoke_leaf", "What does the supplied regulation concern?"), [], evidence,
        )
        payload.update({
            "status": "success",
            "ast_expression": compilation.expression,
            "leaf_count": len(compilation.leaves),
            "answer_status": answer.status,
            "claim_count": len(answer.claims),
            "all_claim_refs_valid": all(
                reference == "E1" for claim in answer.claims for reference in claim.evidence_refs
            ),
        })
    except Exception as exc:
        payload.update({
            "status": "transient_or_service_error",
            "error_type": type(exc).__name__,
            "status_code": getattr(exc, "status_code", None),
            "error": str(exc)[:1_000],
        })
    finally:
        await model.aclose()
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-attempts", type=int, default=1)
    parser.add_argument("--output", type=Path, default=Path("jurisynth/run_outputs/nim_live_smoke.json"))
    args = parser.parse_args()
    if args.max_attempts < 1:
        raise ValueError("--max-attempts must be positive")
    payload = asyncio.run(run_smoke(args.max_attempts))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "output": str(args.output)}))


if __name__ == "__main__":
    main()
