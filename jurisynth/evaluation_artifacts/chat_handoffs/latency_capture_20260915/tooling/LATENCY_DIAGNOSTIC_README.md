# Jurisynth checkpointed latency diagnostic

Run from Project_Space using `.venv-py312\Scripts\python.exe`. No production source/defaults were changed. The capture/replay tools and instrumentation are diagnostic-only. The owner separately approved one live NIM capture on 14 September; see `jurisynth/diagnostics/IMPLEMENTATION_STATUS.md` for its run directory. This does not authorize further live runs or production changes automatically.

## 1. Safe local verification (no NIM)

The supplied fixture is explicitly HAND-AUTHORED, not a real interpretation or legal evaluation case:

```powershell
& '.\.venv-py312\Scripts\python.exe' -m jurisynth.diagnostics.latency_probe replay --capture jurisynth/diagnostics/fixtures/local_probe.json --mode baseline --index-mode sharded --shard-count 4
```

Each invocation creates a new dated replay directory beside its capture unless `--output` names a new directory. Existing directories are refused. The default five-minute watchdog and 5.5 GiB free-RAM preflight apply ONLY to this diagnostic process; `--maximum-seconds 0` disables that watchdog. They do not change production query/request timeouts or retry policy. No index rebuilding occurs.

## 2. Real interpretation capture — requires separate approval

After the owner authorizes live NIM calls:

```powershell
& '.\.venv-py312\Scripts\python.exe' -m jurisynth.diagnostics.latency_probe capture --query-file jurisynth/evaluation_artifacts/complex_ai_medical_organized.txt --leaf-id q003 --output jurisynth/run_outputs/latency_capture_q003 --allow-live-nim
```

This runs the current intake, router, compiler and semantic planner using the existing model/config, but stops before ANY leaf execution, graph/index load, answer generation or final report. A live interpreter invocation follows for the selected leaf. Normal invalid-output repair and transient retry behavior can issue multiple HTTP requests; this is not a promise of one HTTP request or low latency. No request deadline or output cap is added. Ctrl+C preserves completed checkpoints.

An already saved complete materialized request can avoid repeating planning:

```powershell
& '.\.venv-py312\Scripts\python.exe' -m jurisynth.diagnostics.latency_probe capture --request-file jurisynth/run_outputs/prior_capture/request.json --output jurisynth/run_outputs/latency_capture_reused_request --allow-live-nim
```

Do not invent upstream results to avoid dependencies. A planned leaf with unresolved placeholders is rejected; use its previously materialized request instead. If intake asks for clarification or the target leaf does not exist, the tool checkpoints what it obtained and stops. Live capture itself does not load the full KG.

Checkpoints: `original_query.json` when applicable, `planned_leaves.json`, `request.json`, raw interpreter response files, `capture.json` on successful interpretation, `events.jsonl`, and explicit running/finished/failed/interrupted status. Capture includes exact concept text/variants, facts/constraints, model, request durations, token counts and finish reasons where returned by the provider. No key values or .env contents are serialized. These local files can include user-supplied personal/scenario text; review before sharing.

## 3. Replay identical captured concepts

```powershell
& '.\.venv-py312\Scripts\python.exe' -m jurisynth.diagnostics.latency_probe replay --capture jurisynth/run_outputs/latency_capture_q003/capture.json --mode baseline --index-mode sharded --shard-count 4
& '.\.venv-py312\Scripts\python.exe' -m jurisynth.diagnostics.latency_probe replay --capture jurisynth/run_outputs/latency_capture_q003/capture.json --mode no_three_hop --index-mode sharded --shard-count 4
```

Modes:

- `baseline`: existing local retrieval policy with frozen captured concepts.
- `no_three_hop`: skips only three-hop traversal; retains two-hop and conditional broadening.
- `no_escalation`: skips broaden-candidate fallback; returned weak/empty status is retained, not disguised as success.
- `one_hop`: skips two/three-hop traversal; retains the current conditional broadening policy. This is a path-depth ablation, not a simultaneous top-k change.
- `structured_only`: no chunk/table/image search channels.
- `auxiliary_only`: no structured KG/community work.
- `no_community`: skips community ranking/orientation but retains structured evidence retrieval.
- `cold`: first retrieval in a new process, NOT guaranteed cold OS disk caches.
- `warm`: at least two baseline retrievals in the same process. `--repeat N` adds repetitions.

All replays make ZERO NIM calls. LLM community merging and image expansion are explicitly suppressed in EVERY mode; canonical image-caption search still follows the existing opt-in gate. Thus baseline is a LOCAL baseline, not full provider-backed behavior when those optional providers would trigger. Trigger/skip events identify the suppressed LLM merge. This limitation is present in result.json; it must not be reported as a fully equivalent end-to-end baseline.

Seeds/concept variants and configured retrieval budgets are unchanged. Conditional weak-evidence broadening may activate differently when channels/path depth change; inspect its events rather than assuming every mode explored the same candidates. Pin the same sharded index layout for ablations as shown above; leaving `--index-mode auto` retains the existing adaptive policy but available RAM can choose different layouts. No production adaptive behavior is changed.

## 4. What to read

- `configuration.json`: full request/concepts, local settings and selected index layout.
- `events.jsonl`: query_id/call_id/parent_call_id, nested spans and explicit decisions.
- `bundle_00.json` etc.: full returned evidence bundle, saved after EACH retrieval, before any later failure.
- `result.json`: timings, evidence/source/table/image IDs, community metadata, status, capture hash and RSS (not peak RSS).
- `failure.json` or `deadline.json`: failure information; earlier checkpoints remain.

Spans cover operation-semaphore wait, embeddings, exact-label lookup, matcher, shard lock/load/search, community selection/descriptor build, quad enumeration, chunk resolution, 2/3-hop paths, direct SPARQL comparison, evidence normalization/selection, status, escalation, modal channels, orientation and total retrieval. Non-sharded layouts emit an explicit not-applicable event. Quad-enumeration spans include consumer wall time; `quad_enumeration_work.active_seconds` measures iterator work separately. Nested spans overlap: DO NOT sum them as total runtime. Instrumentation/JSON logging itself adds overhead.

Timing fields: the existing NIM wrapper supplies `elapsed_seconds` as the individual attempt duration on completion/retry events; other events use time since probe start. New recorder events also contain an unambiguous `run_elapsed_seconds` clock. The first live capture was already running before that extra clock field was added: use its `stage_started`/`stage_finished` events for the run timeline, not NIM attempt-duration fields as absolute timestamps. Its model settings and running process were not altered.

## Decision rule

Compare latency AND evidence/source coverage on identical captures. Neither a returned success status nor unchanged IDs proves legal correctness. Inspect answer-bearing excerpts from full bundles, allowing equivalent alternate sources and temporal distinctions. Only repeat promising comparisons on 3–5 representative captures before considering a production change; do not tune on held-out locked test cases.

The original global multi-minute delays remain unresolved until a REAL interpretation is captured/replayed. The hand-authored fixture verifies the tool, not that problem's complete cause.

## UI

Double-click `RUN_JURISYNTH_UI.bat` from the workspace. It starts the existing FastAPI/React services on 127.0.0.1, checks readiness, then opens http://127.0.0.1:3000. Keep its window open; Ctrl+C stops only its owned services. It does not submit questions/evals or preload the full KG. Submitting a question DOES invoke NIM through the existing pilot default. Global is opt-in via the existing JURISYNTH_WORKFLOW_SCOPE variable.

Check without starting services: `.\RUN_JURISYNTH_UI.ps1 -CheckOnly`. Startup-only test: `.\RUN_JURISYNTH_UI.ps1 -SmokeTest -NoBrowser`. The launcher does not install dependencies; it reports missing venv/Node/frontend modules/.env/server dependencies before starting. Backend/frontend startup logs go to a new `jurisynth/run_outputs/ui_launcher_*` directory.
