# Jurisynth frontend integration

`stitch_research_dossier/` is the imported Google Stitch Vite/React design.
It is a presentation client, not an authority or a separate legal-research
engine. Its original Delaware/Gemini mock is being replaced incrementally with
Jurisynth report and evidence data.

## Local development

Start the API boundary from the workspace root:

```powershell
& $JurisynthPython -m uvicorn jurisynth.api:app --reload --port 8000
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

The default API intentionally returns `503` for live queries: no API key is
exposed to the browser and no NIM call occurs merely by starting the server.
The next integration step is a server-side runner that builds the pilot
workflow and converts its completed result through `dossier_from_workflow`.
