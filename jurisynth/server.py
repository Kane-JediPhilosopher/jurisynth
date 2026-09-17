"""Opt-in local server for the Batch-0009 Jurisynth pilot interface."""

from __future__ import annotations

import os
from pathlib import Path

from jurisynth.agentic_reasoner.llm import NIMConfig, OpenAICompatibleNIM
from jurisynth.api import LocalImageResolver, create_app
from jurisynth.main import build_global_workflow, build_pilot_workflow


class PilotWorkflowRunner:
    """Build one isolated workflow per browser request; secrets stay server-side."""

    async def __call__(self, query: str) -> object:
        from sentence_transformers import SentenceTransformer

        model = OpenAICompatibleNIM(NIMConfig.from_environment())
        try:
            workflow = build_pilot_workflow(
                processed_batch_dir=Path("jurisynth/kg_construction_pipeline/output/batch_0009"),
                raw_batch_dir=Path("eu_legislation/batch_0009"),
                er_index_dir=Path("jurisynth/pilot_artifacts/batch_0009/er_index"),
                model=model,
                embedder=SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True),
            )
            return await workflow.run(query)
        finally:
            await model.aclose()


class GlobalWorkflowRunner:
    """Optional localhost UI runner over prepared embedded global artifacts."""

    async def __call__(self, query: str) -> object:
        from sentence_transformers import SentenceTransformer

        model = OpenAICompatibleNIM(NIMConfig.from_environment())
        try:
            workflow = build_global_workflow(
                artifact_root=Path(os.environ.get("JURISYNTH_GLOBAL_ARTIFACT_ROOT", "jurisynth/global_artifacts")),
                community_dir=Path(os.environ.get("JURISYNTH_GLOBAL_COMMUNITY_DIR", "jurisynth/global_artifacts/community")),
                model=model,
                embedder=SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True),
            )
            return await workflow.run(query)
        finally:
            await model.aclose()


def _configured_runner() -> object:
    scope = os.environ.get("JURISYNTH_WORKFLOW_SCOPE", "pilot").strip().lower()
    if scope == "pilot":
        return PilotWorkflowRunner()
    if scope == "global":
        return GlobalWorkflowRunner()
    raise RuntimeError("JURISYNTH_WORKFLOW_SCOPE must be 'pilot' or 'global'.")


def _configured_image_resolver() -> LocalImageResolver:
    scope = os.environ.get("JURISYNTH_WORKFLOW_SCOPE", "pilot").strip().lower()
    if scope == "pilot":
        root = Path("eu_legislation/batch_0009")
        return LocalImageResolver([(root, root / "image_index")])
    root = Path(os.environ.get("JURISYNTH_GLOBAL_ARTIFACT_ROOT", "jurisynth/global_artifacts")) / "images"
    # If materialization has not happened yet this is safely empty; never fall
    # back to arbitrary corpus paths.
    return LocalImageResolver([(root / "image_store", root / "image_index")])


app = create_app(runner=_configured_runner(), image_resolver=_configured_image_resolver())
