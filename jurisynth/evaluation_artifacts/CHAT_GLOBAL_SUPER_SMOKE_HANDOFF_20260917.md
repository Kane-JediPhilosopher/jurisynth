# Jurisynth Global Super Compatibility Smoke — Handoff

## Scope and integrity

This is a temporary compatibility run using `nvidia/nemotron-3-super-120b-a12b`, not a Nemotron Ultra accuracy comparison. Retrieval Mech semantics, prompts, schemas, thresholds, ranking, communities, modality logic, scheduling, and retry policy were held frozen. The run used the eight fixed acceptance cases plus 20 AI-reviewed corpus-derived natural questions from `global_natural_candidate_packet.json`.

## Aggregate run facts

- Completed: 28/28; no case timeout or crash.
- Sum of case wall time: 2,758.07 seconds (~46.0 minutes).
- Median / P95 / worst case: 56.12s / 241.56s / 371.89s.
- Mean expected-source coverage: 0.786; 20/28 cases had full expected-document coverage.
- Provider retries: 53; terminal provider failures: 0.
- Every case produced a final report. These traces are suitable for inspecting structured-output and orchestration compatibility, but are not an accuracy benchmark.

## Coverage misses / partial coverage

- `parallel_ai_act_gdpr`: 0.5
- `image_primary`: 0.0
- `global_natural_001`: 0.0
- `global_natural_005`: 0.0
- `global_natural_013`: 0.5
- `global_natural_015`: 0.5
- `global_natural_016`: 0.0
- `global_natural_017`: 0.5

These are coverage observations only. Some natural cases deliberately require source/version precision, so alternate-instrument textual similarity must not be treated as gold-source success.

## Messy AI-medical smoke

Artifact: `run_outputs/global_complex_ai_medical_messy_super_20260917.json`

- Status: success; 281.5s total.
- QCompiler generated four independent leaf queries: provider/role, high-risk classification, AI Act–GDPR interaction, and degraded-update incident responsibilities.
- All four leaves completed; none had retrieval errors.
- All four leaf answers correctly returned `insufficient_evidence` with no claims, rather than inventing legal conclusions.
- Retrieval statuses were `success`, with assertion/chunk evidence plus table candidates, but the answer-bearing provisions required by the leaves did not reach their EvidenceBundles. The final report preserved this uncertainty.
- This is evidence of a source-coverage/grounding limitation for this broad scenario, not a provider/schema failure. No retrieval change was made.

## Provider behavior

Nemotron Super accepted the strict structured-output contracts for intake, QCompiler AST, retrieval concepts, leaf answers, and final reports. The recurring operational issue was transient `503` and occasional `504` behavior, recovered by the existing retry policy. Provider delays must remain separate from local retrieval latency in later analysis.

## Artifacts for review

- `run_outputs/global_agentic_temporary_super_20260917/summary.json`
- per-case JSON and `reasoning.jsonl` / `retrieval_trace.jsonl` in that directory
- `run_outputs/global_complex_ai_medical_messy_super_20260917.json`
- `reasoning_logs/global_smoke_844.jsonl`

## Questions for review

1. Does the messy smoke's faithful `insufficient_evidence` behavior count as an acceptable grounded abstention for a deliberately broad legal scenario?
2. Are the eight coverage-miss cases best classified as expected retrieval limitations, source-version controls, or evidence of one systematic grounding defect?
3. Should formal grounded-QA evaluation proceed without reopening frozen Retrieval Mech semantics?
