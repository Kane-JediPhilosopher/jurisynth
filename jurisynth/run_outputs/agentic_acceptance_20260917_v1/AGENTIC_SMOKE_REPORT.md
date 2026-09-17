# Bounded end-to-end agentic smoke report

Date: 2026-09-17

## Outcome

The live suite was **blocked before Jurisynth's local pipeline began**.

The first case, `simple_ai_act`, spent its complete 900-second case budget in
the initial `request_analysis` NIM call. Nemotron Ultra returned 28 consecutive
HTTP 404 responses; none completed. Each provider response arrived in
approximately 0.25–1.17 seconds, followed by the configured 30–35 second 404
backoff. The bounded cancellation occurred correctly.

The next case immediately received the same 404 response. The remaining queue
was stopped to avoid repeating the same provider-wide failure seven more
times.

## Smoke outcomes

| Smoke | Outcome | Earliest failed stage |
| --- | --- | --- |
| Simple AI Act | blocked / timed out | upstream NIM request analysis |
| Frozen q003 | not run after provider circuit break | upstream service unavailable |
| Dependent multi-leaf | not run | upstream service unavailable |
| Parallel multi-issue | not run | upstream service unavailable |
| AI Act + IVDR | not run | upstream service unavailable |
| Table-primary | not run | upstream service unavailable |
| Image-primary | not run | upstream service unavailable |
| Negative/no-answer | not run | upstream service unavailable |

## Stage localization

The run did not reach:

- task analysis completion;
- QCompiler or AST construction;
- dependency scheduling;
- leaf Query Interpreter calls;
- E-R matching or candidate generation;
- chunk, assertion, table, or image retrieval;
- community selection or lazy summarization;
- leaf answer generation;
- contradiction detection;
- final synthesis.

Consequently there are no claims, EvidenceBundles, retrieved sources,
contradictions, or answers to adjudicate. This must not be classified as a
retrieval failure or a reasoning/synthesis failure.

## Latency and API telemetry

- First-case wall time: **900.016 seconds**
- NIM logical calls: **1**
- HTTP attempts: **28**
- Successful attempts: **0**
- Retries scheduled: **28**
- Status on every attempt: **404 Not Found**
- Schema requested: `request_analysis`
- Request timeout: disabled; the outer case watchdog supplied the bound
- Local retrieval time: **0 seconds / not entered**

## Retrieval freeze decision

Keep Retrieval Mech **permanently frozen**. This run exposed no retrieval
correctness failure and provides no justification for reopening thresholds,
E-R matching, ranking, Query Interpreter semantics, candidate generation,
instrument scoping, communities, or modality behavior.

## QA readiness

The deterministic retrieval layer remains ready for the next stage based on
its completed stabilization gates and 200-case benchmark. The complete
agentic system is **not yet cleared for formal end-to-end QA evaluation**
because the live acceptance suite could not cross the upstream NIM boundary.

Re-run this exact frozen suite when the configured Nemotron Ultra endpoint is
available. Do not tune Jurisynth in response to this incident.

## Artifacts

- `summary.json` — bounded-suite status and stop reason
- `simple_ai_act.json` — complete first-case retry trace
- `reasoning.jsonl` — timestamped NIM attempts, retry decisions, and errors
- `retrieval_trace.jsonl` — absent/empty because retrieval was never entered
