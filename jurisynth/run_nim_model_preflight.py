"""Run one bounded structured-output preflight against a configured NIM model.

This utility deliberately does not edit dotenv files or production settings.
It selects an alternate model and its credential only in the current process.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import time
from dataclasses import replace

from jurisynth.agentic_reasoner.llm import NIMConfig, OpenAICompatibleNIM
from jurisynth.agentic_reasoner.schemas import REQUEST_ANALYSIS_SCHEMA


SYSTEM = """Read the current legal-information request. Return JSON only:
{"action":"proceed|clarify","route":"direct|complex","contextual_facts":[...],"constraints":{},"clarification_question":null}.
Do not answer the question."""
USER = "Under Regulation (EU) 2024/1689, what obligations apply to providers of high-risk AI systems?"


async def run(args: argparse.Namespace) -> dict[str, object]:
    base = NIMConfig.from_environment()
    api_key = os.environ.get(args.api_key_env, "")
    if not api_key:
        raise RuntimeError(f"Environment variable {args.api_key_env!r} is not set.")
    config = replace(base, model=args.model, api_key=api_key, request_timeout_seconds=None)
    model = OpenAICompatibleNIM(config)
    started = time.perf_counter()
    try:
        raw = await asyncio.wait_for(
            model.complete(system=SYSTEM, user=USER, response_schema=REQUEST_ANALYSIS_SCHEMA),
            timeout=args.deadline_seconds,
        )
        parsed = json.loads(raw)
        valid = (
            isinstance(parsed, dict)
            and parsed.get("action") in {"proceed", "clarify"}
            and parsed.get("route") in {"direct", "complex"}
            and isinstance(parsed.get("contextual_facts"), list)
            and isinstance(parsed.get("constraints"), dict)
            and "clarification_question" in parsed
        )
        return {
            "model": args.model,
            "api_key_environment_variable": args.api_key_env,
            "status": "operational" if valid else "schema_invalid",
            "structured_output_valid": valid,
            "elapsed_seconds": round(time.perf_counter() - started, 3),
            "response_fields": sorted(parsed) if isinstance(parsed, dict) else [],
        }
    except TimeoutError:
        return {
            "model": args.model,
            "api_key_environment_variable": args.api_key_env,
            "status": "timed_out",
            "structured_output_valid": False,
            "elapsed_seconds": round(time.perf_counter() - started, 3),
        }
    except Exception as exc:
        return {
            "model": args.model,
            "api_key_environment_variable": args.api_key_env,
            "status": "failed",
            "structured_output_valid": False,
            "error_type": type(exc).__name__,
            "elapsed_seconds": round(time.perf_counter() - started, 3),
        }
    finally:
        await model.aclose()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--api-key-env", required=True)
    parser.add_argument("--deadline-seconds", type=float, default=120.0)
    args = parser.parse_args()
    if args.deadline_seconds <= 0:
        parser.error("--deadline-seconds must be positive")
    print(json.dumps(asyncio.run(run(args)), indent=2))


if __name__ == "__main__":
    main()
