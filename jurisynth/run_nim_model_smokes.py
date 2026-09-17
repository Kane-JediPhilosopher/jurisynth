"""Sequential, schema-validated Agentic Reasoner smoke checks for NIM models.

The output is deliberately limited to model IDs, timings, and validation
outcomes. It never writes API keys, request headers, or model prose.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from jurisynth.agentic_reasoner.llm import EvidenceGroundedLeafGenerator, NIMConfig, NIMRetryPolicy, OpenAICompatibleNIM
from jurisynth.agentic_reasoner.models import LeafNode
from jurisynth.agentic_reasoner.qcompiler_translator import QCompilerTranslator
from jurisynth.contracts import Assertion, EvidenceBundle, EvidenceItem, SourceChunk


MODELS = {
    "KIMI_K3": "moonshotai/kimi-k3",
    "DEEPSEEK_V4_PRO": "deepseek-ai/deepseek-v4-pro-0813",
    "DEEPSEEK_V4_FLASH": "deepseek-ai/deepseek-v4-flash-0731",
    "NEMOTRON_SUPER": "nvidia/nemotron-3-super-120b-a12b",
    "NEMOTRON_LIGHTNING": "nvidia/nemotron-3.5-lightning-30b-a3b",
    "NEMOTRON_NANO": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
    "DIFFUSION_GEMMA": "google/diffusiongemma-26b-a4b-it",
    "GEMMA_4_31B": "google/gemma-4-31b-it",
    "GPT_OSS_20B": "openai/gpt-oss-20b",
    "MISTRAL_NEMOTRON": "mistralai/mistral-nemotron",
}

# Some provider endpoints expose a different reasoning-effort enum. Keep the
# default compatible with Nemotron Ultra and override only known exceptions.
REASONING_EFFORTS = {"GPT_OSS_20B": None}


def _safe_error(exc: Exception) -> dict[str, object]:
    return {
        "error_type": type(exc).__name__,
        "status_code": getattr(exc, "status_code", None),
        "error": str(exc)[:500],
    }


async def _await(coroutine, timeout_seconds: float | None):
    return await coroutine if timeout_seconds is None else await asyncio.wait_for(coroutine, timeout=timeout_seconds)


async def _one(env_name: str, model_name: str, *, timeout_seconds: float | None, reasoning_effort: str | None = "none") -> dict[str, object]:
    api_key = os.getenv(env_name)
    if not api_key:
        return {"key_env": env_name, "model": model_name, "status": "missing_key"}
    base_url = os.getenv("JURISYNTH_NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")
    client = OpenAICompatibleNIM(
        NIMConfig(api_key, base_url, model_name, request_timeout_seconds=timeout_seconds, reasoning_effort=reasoning_effort),
        retry_policy=NIMRetryPolicy(max_attempts=1, max_backoff_seconds=0, jitter_seconds=0),
    )
    result: dict[str, object] = {"key_env": env_name, "model": model_name, "reasoning_effort": reasoning_effort}
    try:
        q_started = time.perf_counter()
        compilation = await _await(QCompilerTranslator(client).compile("What is the scope of Regulation (EU) 2016/679?"), timeout_seconds)
        result.update({"qcompiler_seconds": round(time.perf_counter() - q_started, 3), "ast_valid": bool(compilation.expression and compilation.leaves)})
        evidence = EvidenceBundle("smoke", "success", [EvidenceItem("E1", Assertion("Regulation (EU) 2016/679", "has scope", "processing of personal data"), [SourceChunk("smoke", "smoke", "The Regulation concerns processing of personal data.")])])
        a_started = time.perf_counter()
        answer = await _await(EvidenceGroundedLeafGenerator(client)(LeafNode("smoke", "What does the supplied regulation concern?"), [], evidence), timeout_seconds)
        result.update({
            "leaf_seconds": round(time.perf_counter() - a_started, 3),
            "answer_status": answer.status,
            "claim_refs_valid": all(ref == "E1" for claim in answer.claims for ref in claim.evidence_refs),
            "status": "success",
        })
    except Exception as exc:
        result.update({"status": "failed", **_safe_error(exc)})
    finally:
        await client.aclose()
    return result


def _write(payload: dict[str, object], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


async def run(timeout_seconds: float | None, *, output: Path, selected: set[str] | None = None) -> dict[str, object]:
    load_dotenv(Path("jurisynth/agentic_reasoner/.env"), override=False)
    payload: dict[str, object] = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "timeout_seconds": timeout_seconds, "results": []}
    _write(payload, output)
    # Deliberately sequential: this measures compatibility, not provider
    # throughput, and avoids conflating a model failure with account capacity.
    for env_name, model_name in MODELS.items():
        if selected is not None and env_name not in selected:
            continue
        payload["results"].append(await _one(env_name, model_name, timeout_seconds=timeout_seconds, reasoning_effort=REASONING_EFFORTS.get(env_name, "none")))
        _write(payload, output)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout-seconds", type=float, default=0, help="Per-step limit; 0 disables it (Ctrl-C remains available).")
    parser.add_argument("--only", help="Comma-separated key environment names to test.")
    parser.add_argument("--output", type=Path, default=Path("jurisynth/run_outputs/nim_model_smokes.json"))
    args = parser.parse_args()
    if args.timeout_seconds < 0:
        parser.error("--timeout-seconds cannot be negative")
    selected = {item.strip() for item in args.only.split(",") if item.strip()} if args.only else None
    unknown = (selected or set()) - MODELS.keys()
    if unknown:
        parser.error(f"Unknown --only entries: {', '.join(sorted(unknown))}")
    timeout_seconds = args.timeout_seconds or None
    payload = asyncio.run(run(timeout_seconds, output=args.output, selected=selected))
    counts = {status: sum(item.get("status") == status for item in payload["results"]) for status in ("success", "failed", "missing_key")}
    print(json.dumps({"output": str(args.output), **counts}))


if __name__ == "__main__":
    main()
