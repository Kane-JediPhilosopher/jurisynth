"""FastAPI boundary for the Jurisynth research interface.

The API exposes report/evidence data only; the React client never receives API
keys or controls retrieval internals such as SPARQL construction.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field


WorkflowRunner = Callable[[str], Awaitable[object]]


class LocalImageResolver:
    """Resolve only manifest-indexed images within explicitly approved roots."""

    def __init__(self, locations: list[tuple[Path, Path]]) -> None:
        self._images: dict[str, tuple[Path, str]] = {}
        for root, index_dir in locations:
            self._load_index(root, index_dir)

    def _load_index(self, root: Path, index_dir: Path) -> None:
        try:
            payload = json.loads((index_dir / "metadata.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        records = payload.get("metadata") if isinstance(payload, dict) else None
        if not isinstance(records, list):
            return
        approved_root = root.resolve()
        for record in records:
            if not isinstance(record, dict):
                continue
            image_id, relative_path, mime_type = record.get("image_id"), record.get("relative_path"), record.get("mime_type")
            if not all(isinstance(value, str) for value in (image_id, relative_path, mime_type)):
                continue
            path = (approved_root / relative_path).resolve()
            if approved_root in path.parents and path.is_file():
                self._images.setdefault(image_id, (path, mime_type))

    def resolve(self, image_id: str) -> tuple[Path, str] | None:
        return self._images.get(image_id)


class QuerySubmission(BaseModel):
    query: str = Field(min_length=3, max_length=8_000)


def create_app(*, runner: WorkflowRunner | None = None, image_resolver: LocalImageResolver | None = None) -> FastAPI:
    app = FastAPI(title="Jurisynth API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @app.get("/api/v1/health")
    async def health() -> dict[str, object]:
        return {"status": "ok", "live_query_enabled": runner is not None}

    @app.get("/api/v1/demo-dossier")
    async def demo_dossier() -> dict[str, object]:
        return _empty_dossier()

    @app.get("/api/v1/images/{image_id:path}")
    async def image(image_id: str) -> FileResponse:
        resolved = image_resolver.resolve(image_id) if image_resolver is not None else None
        if resolved is None:
            raise HTTPException(status_code=404, detail="Image is unavailable.")
        path, media_type = resolved
        return FileResponse(path, media_type=media_type, filename=path.name)

    @app.post("/api/v1/query")
    async def query(submission: QuerySubmission) -> dict[str, object]:
        if runner is None:
            raise HTTPException(status_code=503, detail="Live Jurisynth workflow is not configured on this server.")
        try:
            result = await runner(submission.query)
        except Exception:
            # Keep model/provider failures out of browser traces and preserve a
            # usable UI; detailed diagnostics remain in the server-side log.
            raise HTTPException(status_code=502, detail="Jurisynth could not complete this research run. Please retry shortly.") from None
        return dossier_from_workflow(result, submission.query)

    return app


def dossier_from_workflow(result: object, query: str) -> dict[str, object]:
    """Normalize the stable progressive-disclosure payload for the frontend."""
    presentation = getattr(result, "presentation", None) or {}
    report = getattr(result, "report", None)
    overview = presentation.get("overview") if isinstance(presentation, dict) else None
    if not isinstance(overview, str):
        overview = getattr(report, "overview", "No report was generated.")
    sections = presentation.get("sections", []) if isinstance(presentation, dict) else []
    return {
        "query": query,
        "overview": overview,
        "sections": sections if isinstance(sections, list) else [],
        "contradiction_refs": presentation.get("contradiction_refs", []) if isinstance(presentation, dict) else [],
        "auxiliary_images": presentation.get("auxiliary_images", []) if isinstance(presentation, dict) else [],
        "ast": getattr(result, "ast", None),
        "status": "complete" if report is not None or bool(presentation) else "partial",
        "disclaimer": "Informational legal research support only; verify primary sources before relying on any result.",
    }


def _empty_dossier() -> dict[str, object]:
    return {
        "query": None,
        "overview": "Submit a question to generate an evidence-grounded Jurisynth research report.",
        "sections": [],
        "contradiction_refs": [],
        "auxiliary_images": [],
        "ast": None,
        "status": "ready",
        "disclaimer": "Informational legal research support only; verify primary sources before relying on any result.",
    }


app = create_app()
