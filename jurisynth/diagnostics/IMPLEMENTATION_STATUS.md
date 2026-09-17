# Diagnostic implementation status — 14 September 2026

Scope: standalone latency capture/replay tooling and a launcher for the existing UI. No production prompts, retry rules, retrieval defaults, dependency policy or community behavior changed in this implementation. Existing unrelated worktree changes were preserved.

## Verification

- Targeted offline suite: **46 passed**, three FAISS/SWIG deprecation warnings, 1.59 seconds. Command: `.venv-py312\Scripts\python.exe -m pytest jurisynth/tests/test_latency_probe.py jurisynth/agentic_reasoner/tests/test_llm.py jurisynth/retrieval_mech/tests/test_image_expander.py -q`. Includes restoration after partially failed instrumentation setup, preservation of lock-acquisition errors without releasing an unacquired lock, and distinct run-clock versus API-attempt-duration fields.
- New Python files passed syntax checks; PowerShell launcher passed parser checks.
- Launcher startup smoke passed: existing FastAPI health endpoint and React frontend both returned HTTP 200 at localhost. No question POST, NIM call, or graph/model query was submitted. Owned services stopped; ports 8000 and 3000 were free afterwards.
- Environment-only installation: the already pinned `uvicorn==0.52.4` was missing from `.venv-py312` and was installed there with `--no-deps`. No requirements pins or other packages were changed.
- Global replay tooling check **did not run retrieval**: free memory was 4.800 GiB, below its 5.5 GiB safety guard. Failure checkpoints are in `jurisynth/run_outputs/latency_probe_tool_baseline_v1`. The guard was not lowered and user processes were not stopped.

The tiny synthetic FAISS tests validate instrumentation and ablation behavior, not global performance or legal correctness. The supplied local fixture is hand-authored and is not a live interpretation or evaluation gold.

## Deliverables

- `jurisynth/diagnostics/latency_probe.py`: explicitly gated live interpretation capture, followed by zero-NIM replay on fixed captured concepts.
- `jurisynth/diagnostics/tracing.py`: checkpointed nested timings, shard/lock/path/modal/community/escalation instrumentation and diagnostic-only ablations.
- `jurisynth/tests/test_latency_probe.py`: offline tests including synthetic capture, checkpoint failures and shard tracing.
- `RUN_JURISYNTH_UI.bat` and `.ps1`: localhost-only startup, readiness checks and owned-service cleanup.
- `LATENCY_DIAGNOSTIC_README.md`: commands, interpretation limits and approval boundary.
- `PROMPT_AND_ARCHITECTURE_CHANGE_PLAN.md`: proposed production changes, **not applied**.

## Next boundary

The owner subsequently approved one real NIM capture. It started at 22:12 Singapore time, with checkpoints in `jurisynth/run_outputs/latency_capture_q003_live_20260914_v1`. This retains the existing Nemotron Ultra configuration and runs planning plus one selected leaf interpretation, not leaf answers or a broad global smoke. Refer to that run's `result.json` and `events.jsonl` for current status. Replay follows only if capture completes and the RAM guard permits it. Production changes remain proposals until approved; the existing checklist counter is unchanged.

A sequential local replay queue was started while capture was pending. It waits for `status=captured`, then runs baseline and `no_three_hop` in separate processes with the same four-shard layout and fixed captured concepts. Both use the diagnostic RAM guard and five-minute local watchdog, not an API timeout. A non-running/non-captured capture status stops the queue; unsuccessful baseline stops the comparison. Planned output directories: `jurisynth/run_outputs/latency_replay_q003_baseline_live_20260914_v1` and `jurisynth/run_outputs/latency_replay_q003_no_three_hop_live_20260914_v1`. Directory names do not imply those replays have started or completed; check their result files.
