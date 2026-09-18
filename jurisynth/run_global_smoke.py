"""Run and time one NIM-backed query against local disk-backed global artifacts.

The graph is opened from an embedded read-only Oxigraph store, not materialized
through RDFLib. The output is created immediately as ``running`` so an
interrupted run remains auditable, then replaced with elapsed time and result.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import time
from datetime import datetime, timezone
from dataclasses import replace
from pathlib import Path

import psutil

from jurisynth.agentic_reasoner.llm import NIMConfig, OpenAICompatibleNIM
from jurisynth.main import _compact_result, build_global_workflow
from jurisynth.reasoning_log import ReasoningLog


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, default=str, indent=2) + "\n", encoding="utf-8")


async def run(args: argparse.Namespace, started: float) -> dict[str, object]:
    try:
        from sentence_transformers import SentenceTransformer
    except ModuleNotFoundError as exc:
        raise RuntimeError("Install sentence-transformers in the documented Python 3.12 environment.") from exc
    reasoning_log = ReasoningLog(args.reasoning_log / f"global_smoke_{int(started)}.jsonl", "global_smoke")
    config = NIMConfig.from_environment()
    if args.model is not None:
        config = replace(config, model=args.model)
    if args.api_key_env is not None:
        key = os.environ.get(args.api_key_env, "")
        if not key:
            raise RuntimeError(f"Environment variable {args.api_key_env!r} is not set.")
        config = replace(config, api_key=key)
    config = replace(config, request_timeout_seconds=args.request_timeout_seconds or None)
    model = OpenAICompatibleNIM(config, reasoning_log=reasoning_log)
    try:
        workflow = build_global_workflow(
            artifact_root=args.artifact_root,
            community_dir=args.community_dir,
            model=model,
            embedder=SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True),
            reasoning_log=reasoning_log,
        )
        result = await workflow.run(args.query)
    finally:
        await model.aclose()
    compact = _compact_result(result)
    execution = _execution_summary(compact)
    return {
        "status": "completed_with_errors" if execution["failed_leaf_count"] or execution["retrieval_error_count"] else "success",
        "call_status": "completed",
        "quality_adjudicated": False,
        "execution": execution,
        "scope": "global",
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "result": compact,
    }


def _execution_summary(result: dict[str, object]) -> dict[str, int]:
    nodes = result.get("node_results", {})
    failed, retrieval_errors, claims = 0, 0, 0
    for node in nodes.values():
        failed += node.get("status") == "failed"
        answer = node.get("answer") or {}
        retrieval_errors += answer.get("evidence_summary", {}).get("retrieval_status") == "error"
        claims += len(answer.get("claims", []))
    return {"leaf_count": len(nodes), "failed_leaf_count": failed,
            "retrieval_error_count": retrieval_errors, "claim_count": claims}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="?", help="Inline query text (use --query-file for multi-paragraph prompts).")
    parser.add_argument("--query-file", type=Path, help="UTF-8 text file containing one multi-line query.")
    parser.add_argument("--artifact-root", type=Path, default=Path("jurisynth/global_artifacts"))
    parser.add_argument("--community-dir", type=Path, default=Path("jurisynth/global_artifacts/community"))
    parser.add_argument("--reasoning-log", type=Path, default=Path("jurisynth/reasoning_logs"))
    parser.add_argument("--minimum-available-gb", type=float, default=8.0)
    parser.add_argument("--request-timeout-seconds", type=float, default=0,
                        help="0 disables the HTTP timeout; transient retries remain bounded by the overall query deadline.")
    parser.add_argument("--query-timeout-seconds", type=float, default=900,
                        help="Overall async smoke deadline; 0 disables it.")
    parser.add_argument("--output", type=Path, default=Path("jurisynth/run_outputs/global_smoke.json"))
    parser.add_argument("--model", help="Process-local NIM model override.")
    parser.add_argument("--api-key-env", help="Environment variable holding the API key for --model.")
    args = parser.parse_args()
    if args.request_timeout_seconds < 0 or args.query_timeout_seconds < 0:
        parser.error("Smoke deadlines must be nonnegative; 0 disables them.")
    if args.query_file is not None:
        if args.query is not None:
            parser.error("Provide either an inline query or --query-file, not both.")
        args.query = args.query_file.read_text(encoding="utf-8").strip()
    if not args.query:
        parser.error("Provide an inline query or --query-file.")
    available_gb = psutil.virtual_memory().available / (1024 ** 3)
    if available_gb < args.minimum_available_gb:
        raise RuntimeError(
            f"Global smoke needs at least {args.minimum_available_gb:g} GB available RAM; only {available_gb:.1f} GB is available. "
            "Close memory-heavy applications or run on a machine with more available RAM."
        )
    started = time.monotonic()
    _write(args.output, {
        "status": "running", "scope": "global", "started_at": datetime.now(timezone.utc).isoformat(),
        "available_memory_gb": round(available_gb, 2), "query": args.query,
        "request_timeout_seconds": args.request_timeout_seconds or None, "query_timeout_seconds": args.query_timeout_seconds or None,
    })
    try:
        async def bounded_run():
            return await asyncio.wait_for(run(args, started), timeout=args.query_timeout_seconds or None)
        payload = asyncio.run(bounded_run())
    except TimeoutError:
        payload = {"status": "timed_out", "call_status": "timed_out", "scope": "global",
                   "elapsed_seconds": round(time.monotonic() - started, 3),
                   "error": "Overall query deadline exceeded; no legal-quality conclusion.",
                   "query_timeout_seconds": args.query_timeout_seconds}
    except Exception as exc:
        payload = {"status": "failed", "scope": "global", "elapsed_seconds": round(time.monotonic() - started, 3), "error": repr(exc)}
    _write(args.output, payload)
    print(json.dumps({"output": str(args.output), "status": payload["status"]}))


if __name__ == "__main__":
    main()
