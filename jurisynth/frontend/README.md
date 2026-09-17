# Jurisynth frontend integration

`stitch_research_dossier/` is the imported Google Stitch Vite/React design.
It is a presentation client, not an authority or a separate legal-research
engine. Its original Delaware/Gemini mock is being replaced incrementally with
Jurisynth report and evidence data.

## Local development

Start the live, server-side pilot API from the workspace root:

```powershell
& $JurisynthPython -m uvicorn jurisynth.server:app --reload --port 8000
```

Then, in `stitch_research_dossier/`, install the exported frontend's Node
dependencies and start Vite. The client defaults to `http://127.0.0.1:8000`;
set `VITE_JURISYNTH_API_BASE` only when using another API origin.

## Current endpoints

- `GET /api/v1/health` — local service readiness.
- `GET /api/v1/demo-dossier` — a transparent ready-state payload.
- `POST /api/v1/query` — accepts a user question and returns a normalized
  report → section → claim → evidence payload when a live workflow runner is
  configured.

`jurisynth.server:app` builds an isolated Batch-0009 workflow on each submitted
query. NIM keys remain only in the local server process. The browser receives
the final report, evidence-disclosure payload, and a QCompiler AST once
decomposition has completed; it does not receive retrieval internals or keys.

The older `jurisynth.api:app` endpoint remains a safe no-live-query boundary
and intentionally returns `503` for POSTed queries.
