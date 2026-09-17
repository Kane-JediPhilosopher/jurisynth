# Compiler boundary and smoke-runner review

The last bounded retry logged two APITimeoutError failures at approximately 180 seconds each, then another request start without a recorded response. No matching smoke process remained at inspection. That does not establish the reason the process disappeared.

The request stalled at the NVIDIA NIM client boundary, before the local QCompiler-compatible parser could receive or parse a response. Jurisynth uses its own schema-backed translator and a minimal compatible vendored parser, not a QCompiler-hosted API. Upstream QCompiler is therefore not established as the cause. The parser regression suite passed, but this is not proof of correctness for every generated AST.

Local fixes:

- An explicit HTTP status now takes precedence over status-like digits in an error payload. A 400 mentioning 404/503 is not retried indefinitely. Genuine transient statuses retain the existing retry policy.
- The bounded smoke runner creates its output directory, checks format-output collisions before marking itself running, normalizes malformed/stale child outputs, records child exit codes, and attempts owned-process cleanup and summary finalization on runner exceptions/interruption.

Verification: 26 local tests passed across test_llm.py, test_bounded_global_smokes.py and test_qcompiler_translator.py. No live API calls were made. No production timeout, AST prompt, extraction prompt or retrieval-selection policy was changed. The overall live-smoke gates remain open; these regression tests do not close them.

Prepared CHAT_FOLLOWUP_SOURCE_COMPLETE.md under evaluation_artifacts/ai_assisted_review_v1/chat_adjudicated_v1: six pending natural-question revisions and two NLI families requiring corrected-premise label confirmation. Original imported review and labels remain unchanged. Empirical evaluation of the corrected NLI set remains pending that confirmation.
