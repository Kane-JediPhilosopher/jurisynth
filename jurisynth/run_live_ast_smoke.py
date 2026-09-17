"""Persist one live NIM QCompiler decomposition for inspection.

This is intentionally narrower than an end-to-end retrieval run: it proves
that the live model emits a parser-valid, multi-leaf QCompiler AST without
making a corpus-coverage claim.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import asdict
from pathlib import Path

from jurisynth.agentic_reasoner.llm import NIMConfig, OpenAICompatibleNIM
from jurisynth.agentic_reasoner.qcompiler_translator import QCompilerTranslator


DEFAULT_QUERY = """For a consumer who bought a defective laptop from a retailer in Germany,
answer these four independent questions separately: (1) identify the relevant
EU consumer-sale remedies; (2) identify evidence the consumer should retain;
(3) identify the respective roles of seller and manufacturer; and (4) identify
practical escalation or complaint routes. Do not make any answer depend on
another answer."""


async def run(query: str) -> dict[str, object]:
    model = OpenAICompatibleNIM(NIMConfig.from_environment())
    try:
        compilation = await QCompilerTranslator(model).compile(query)
    finally:
        await model.aclose()
    return {
        "status": "success",
        "query": query,
        "expression": compilation.expression,
        "ast": compilation.ast,
        "leaves": [asdict(leaf) for leaf in compilation.leaves],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default=DEFAULT_QUERY)
    parser.add_argument("--output", type=Path, default=Path("jurisynth/run_outputs/live_ast_smoke.json"))
    args = parser.parse_args()
    try:
        payload = asyncio.run(run(args.query))
    except Exception as exc:
        payload = {
            "status": "failed",
            "query": args.query,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "status": payload["status"], "leaf_count": len(payload.get("leaves", []))}))


if __name__ == "__main__":
    main()
