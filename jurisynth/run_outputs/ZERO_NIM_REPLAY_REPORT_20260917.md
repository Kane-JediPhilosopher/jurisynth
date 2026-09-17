# Zero-NIM downstream replay smoke

Date: 2026-09-17

## Scope and evidence boundary

This is a contract replay, not a new legal-QA result. It used only persisted
Jurisynth artifacts:

- the successful captured QCompiler expression/AST from
  `structured_output_smoke_v4.json`;
- captured complex-run leaves, leaf outputs, and final report from
  `global_complex_ai_medical_organized.json`;
- captured live interpretation concepts from the structured-output smoke.

It made **zero NIM/API calls**. The replay executed current local global
artifact loading, E-R grounding, Oxigraph retrieval, FAISS modalities,
community orientation, `RetrievalRequest` construction, the real dependency
scheduler, claim-reference validation, explicit-negation contradiction
detection, and report/presentation validation.

## Stage results

| Stage | Result | Observation |
| --- | --- | --- |
| Captured QCompiler AST → parser/adapter | pass | Re-parsed deterministically: 4 leaves, `q001` root and `q002/q003/q004` dependent on it |
| Replay dependency schedule | pass | Current replay graph: `q001 → q002/q004`, then `q001+q002 → q003` |
| Per-leaf RetrievalRequest construction | pass | Real requests included inherited constraints and dependency context according to the captured plan |
| Frozen Retrieval Mech | pass | All four real local retrievals returned `success`; no NIM activity |
| EvidenceBundle propagation | pass | Assertions, chunks, tables, images, source scopes, timing, and community orientation reached each completed leaf |
| Captured zero-claim leaf outputs | pass | `q001`, `q002`, and `q003` completed and preserved their real EvidenceBundles |
| Captured positive-claim replay | correctly rejected | `q004` referenced 12 historical evidence IDs absent from its repaired-v2 bundle; deterministic validation raised a dangling-reference error |
| Contradiction handling | pass, empty case | Detector executed over completed claims and returned no candidates; positive contradiction detection was not exercised |
| Captured final-report plumbing | correctly rejected | Historical report referenced `q004:C1`, which had been rejected; report validator blocked the dangling claim reference |

The validation rejections are desirable integrity behavior, not a retrieval
semantics defect: the historical positive claim was paired with an older,
non-self-contained evidence snapshot, while this replay used repaired v2
artifacts.

## Scheduling and local latency

The scheduler behaved as intended:

1. `q001` ran first.
2. `q002` and `q004` became runnable together.
3. `q003` became runnable as soon as `q002` completed, overlapping the tail of
   `q004`.

Total wall time was **60.825 s**, versus **82.621 s** if all four retrievals
had run serially.

| Leaf | Retrieval wall time | Status |
| --- | ---: | --- |
| q001 | 25.079 s | success |
| q002 | 13.077 s | success |
| q003 | 21.813 s | success |
| q004 | 22.652 s | success at retrieval; captured claim rejected afterwards |

## Retrieval, sources, and modalities

All four bundles covered `citation:regulation:2024:1689`; the AI Act source
`L_202401689EN` appeared in each retrieval's source set. The bundles contained
50–51 assertion/chunk evidence items and five table candidates per leaf.
Image candidates also propagated for q001 (five) and q002 (one).

Community orientation ran for every leaf. It selected four contributing
communities with average tree distance 3.0, below the production lazy-summary
trigger thresholds (six communities or average distance 4.0). Therefore no
lazy community summary would have been generated in this replay even with NIM
available.

## What remains untestable without a valid NIM response

- live intake and task analysis;
- live QCompiler generation/repair, as distinct from replaying its captured
  parser-validated AST;
- live leaf-answer generation against the current bundle;
- successful positive claim-to-current-evidence provenance wiring;
- live final report synthesis and its semantic groundedness;
- image vision expansion when a high-relevance visual candidate requires it;
- lazy community summarization when its trigger condition is met;
- a positive contradiction-detection case from a real end-to-end answer set.

## Retrieval freeze decision

Keep Retrieval Mech **permanently frozen**. The zero-NIM replay found no
retrieval correctness or deterministic retrieval-plumbing defect. The only
failure was strict rejection of stale historical claim IDs, which protects
provenance rather than weakening it.

Local scheduler, QCompiler-translation, and report-plumbing regression tests
also passed: **15 passed, 0 failed**.

## Artifacts

- `zero_nim_replay_20260917.json` — full replay trace and bundles
- `run_zero_nim_replay_smoke.py` — repeatable zero-NIM harness
- `agentic_acceptance_20260917_v1/` — unchanged live-suite provider incident
