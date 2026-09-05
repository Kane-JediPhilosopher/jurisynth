"""FastAPI boundary for the Jurisynth research interface.

The API exposes report/evidence data only; the React client never receives API
keys or controls retrieval internals such as SPARQL construction.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


WorkflowRunner = Callable[[str], Awaitable[object]]


class QuerySubmission(BaseModel):
    query: str = Field(min_length=3, max_length=8_000)


def create_app(*, runner: WorkflowRunner | None = None) -> FastAPI:
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

    @app.post("/api/v1/query")
    async def query(submission: QuerySubmission) -> dict[str, object]:
        if runner is None:
            raise HTTPException(status_code=503, detail="Live Jurisynth workflow is not configured on this server.")
        return dossier_from_workflow(await runner(submission.query), submission.query)

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
        "status": "complete",
        "disclaimer": "Informational legal research support only; verify primary sources before relying on any result.",
    }


def _empty_dossier() -> dict[str, object]:
    return {
        "query": None,
        "overview": "Submit a question to generate an evidence-grounded Jurisynth research report.",
        "sections": [],
        "contradiction_refs": [],
        "status": "ready",
        "disclaimer": "Informational legal research support only; verify primary sources before relying on any result.",
    }


app = create_app()
