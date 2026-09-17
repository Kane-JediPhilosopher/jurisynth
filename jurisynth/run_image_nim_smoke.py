"""Run one bounded Nano Omni caption + expansion check and persist a safe log."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

from jurisynth.contracts import ImageEvidence
from jurisynth.retrieval_mech.image_expander import ImageExpander


PIPELINE_SRC = Path(__file__).resolve().parent / "kg_construction_pipeline" / "src"
if str(PIPELINE_SRC) not in sys.path:
    sys.path.insert(0, str(PIPELINE_SRC))

from image_processor import NIMImageDescriber, load_image_assets  # noqa: E402
from vision_llm_utils import VisionNIMConfig, create_vision_client  # noqa: E402


async def run(batch_dir: Path, timeout_seconds: float, *, skip_caption: bool = False, asset_index: int = 0) -> dict[str, object]:
    config = VisionNIMConfig.from_environment()
    assets = load_image_assets(batch_dir / "image_store")
    if not assets:
        raise RuntimeError(f"No eligible images in {batch_dir / 'image_store'}.")
    if asset_index >= len(assets):
        raise RuntimeError(f"Only {len(assets)} eligible images are available.")
    asset = assets[asset_index]
    total_started = time.perf_counter()
    client = create_vision_client(config)
    try:
        if skip_caption:
            caption = {"description": "An extracted EU legal-document image.", "image_type": "other", "legible_text": ""}
            caption_seconds = None
        else:
            describer = NIMImageDescriber(client, model_id=config.model_id)
            started = time.perf_counter()
            caption = await asyncio.wait_for(describer.describe(asset), timeout=timeout_seconds)
            caption_seconds = round(time.perf_counter() - started, 3)
        evidence = ImageEvidence(
            asset.image_id, asset.document_id, str(asset.path.resolve().relative_to(batch_dir.resolve())).replace("\\", "/"),
            asset.mime_type, caption["description"], caption["legible_text"], sha256=asset.sha256,
            source_url=asset.source_url, alt=asset.alt,
        )
        expander = ImageExpander(batch_dir, config=config, client=client)
        started = time.perf_counter()
        expanded = (await asyncio.wait_for(expander.expand([evidence], "What visible structure or labels does this image contain?"), timeout=timeout_seconds))[0]
        expansion_seconds = round(time.perf_counter() - started, 3)
        return {
            "status": "success", "model": config.model_id,
            "image_id": asset.image_id, "document_id": asset.document_id,
            "caption_status": "not_run" if skip_caption else "success",
            "caption_seconds": caption_seconds, "expansion_seconds": expansion_seconds,
            "total_seconds": round(time.perf_counter() - total_started, 3),
            "caption": caption["description"], "image_type": caption["image_type"],
            "expanded_description": expanded.expanded_description,
            "visual_findings": expanded.visual_findings,
            "expansion_relevance": expanded.expansion_relevance,
        }
    finally:
        await client.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=Path, default=Path("eu_legislation/batch_0009"))
    parser.add_argument("--timeout-seconds", type=float, default=120)
    parser.add_argument("--skip-caption", action="store_true", help="Test the Expander alone with a neutral local caption.")
    parser.add_argument("--parallel", type=int, default=1, help="Concurrent distinct-image smoke calls (bounded; default 1).")
    parser.add_argument("--output", type=Path, default=Path("jurisynth/run_outputs/image_nim_smoke.json"))
    args = parser.parse_args()
    if args.parallel < 1:
        parser.error("--parallel must be positive")

    async def _parallel() -> dict[str, object]:
        async def one(index: int) -> dict[str, object]:
            try:
                return await run(args.batch, args.timeout_seconds, skip_caption=args.skip_caption, asset_index=index)
            except Exception as exc:
                return {"status": "failed", "asset_index": index, "error_type": type(exc).__name__, "error": str(exc)[:500]}
        results = await asyncio.gather(*(one(index) for index in range(args.parallel)))
        return {"status": "success" if all(item["status"] == "success" for item in results) else "partial", "parallelism": args.parallel, "results": results}

    try:
        payload = asyncio.run(_parallel())
    except Exception as exc:
        payload = {"status": "failed", "error_type": type(exc).__name__, "error": str(exc)[:500]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
