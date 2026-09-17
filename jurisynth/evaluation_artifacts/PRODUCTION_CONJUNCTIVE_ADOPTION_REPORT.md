# Production conjunction adoption and retrieval-freeze report

Date: 2026-09-17

## Outcome

The direct indexed subject+predicate lookup is now part of the production
`DirectRDFRetriever`. When grounded subject and predicate seeds are both
available, retrieval uses Oxigraph's indexed
`quads_for_pattern(subject, predicate, *, *)` access first. Every matching
named graph is retained so duplicate assertions from distinct chunks keep all
provenance. If the bounded conjunction produces no candidates, the existing
independent per-seed scan remains the fallback.

No retrieval thresholds, E-R matching, Query Interpreter behavior, ranking,
instrument scoping, table/image logic, community logic, or retrieval-status
semantics were changed in this adoption pass.

## Files changed

- `jurisynth/retrieval_mech/rdf_store.py`
- `jurisynth/retrieval_mech/rdf_retriever.py`
- `jurisynth/run_global_assertion_evaluation.py`
- `jurisynth/retrieval_mech/tests/test_direct_rdf_retriever.py`
- `jurisynth/tests/test_global_assertion_sampling.py`
- `jurisynth/diagnose_production_assertion_latency_tail.py`

## Regression tests

Focused retrieval/store/benchmark suite: **32 passed, 0 failed**.

The tests cover the Oxigraph store, direct RDF retrieval, mechanism behavior,
production conjunction, fallback behavior, and preservation of multiple
graph-qualified provenance sources for the same assertion.

## Five production stabilization gates

| Gate | Intended result | Status | Source coverage | Latency | Key observation |
| --- | --- | --- | ---: | ---: | --- |
| q003 AI Act | strong grounded result | success | 1.0 | 23.268 s | AI Act source recovered; unrelated similarity did not determine success |
| Simple AI Act | strong single-instrument result | success | 1.0 | 5.234 s | only in-scope evidence determined the result |
| AI Act + IVDR | both instruments survive | success | 1.0 | 89.540 s | both sources recovered; useful cross-instrument evidence retained |
| Table-primary | expected table rows survive | success | 1.0 | 7.816 s | table 10 rows 0, 1, and 2 survived merged reranking |
| GDPR negative control | no false strong success | weak | 0.0 | 6.842 s | unrelated high-similarity evidence did not establish success |

All five gates passed their intended acceptance condition.

## Corrected 200-case production assertion benchmark

The benchmark ran through the production retriever with the controlled
subject/predicate interpreter, repaired v2 artifacts, fixed ranking and
candidate limits, and no NIM calls.

- Exact assertion recall: **0.670 (134/200)**
- MRR: **0.4373038825**
- Recall@1: **0.355**
- Recall@3: **0.485**
- Recall@5: **0.555**
- Recall@10: **0.595**
- Recall@20: **0.660**
- Recall@40: **0.670**
- Subject recovery: **0.900**
- Predicate recovery: **0.895**
- Object recovery: **0.690**
- Designated-gold-source match: **0.650 (130/200)**
- Direct source/chunk recall: **0.085**
- Mean latency: **5.921 s**
- Median latency: **0.607 s**
- P95 latency: **47.604 s**
- Worst-case latency: **60.496 s**
- Peak observed RSS: **3399.7 MB**

Case-level comparison against the prior direct-indexed experimental run found
**zero regressions and zero metric changes across all 200 cases**. All 134
exact recoveries retain traceable document/chunk provenance. Of these, 130
match the designated benchmark source and four are exact assertions supported
by valid alternate sources (`00036`, `00105`, `00180`, and `00190`).

## Read-only latency-tail diagnostic

The five slow cases were profiled twice without changing candidate semantics.
The first-pass mean was 52.190 s and the immediate-repeat mean was 49.254 s,
only a 5.6% reduction; cold-versus-warm storage effects are therefore not the
primary explanation.

| Case | First / repeat | Raw Oxigraph access | Main cost |
| --- | ---: | ---: | --- |
| 00033 | 45.235 / 50.605 s | 2.3 / 0.2 ms | community selection: 45.081 / 50.467 s |
| 00084 | 48.125 / 46.635 s | 5.4 / 0.2 ms | community selection: 47.974 / 46.493 s |
| 00096 | 57.933 / 50.116 s | 55 / 3 ms | fallback/broaden candidate materialization: 42.650 / 36.327 s; E-R: 15.117 / 13.709 s |
| 00102 | 57.661 / 49.429 s | 9.1 / 0.45 ms | community selection: 57.384 / 49.229 s |
| 00124 | 51.996 / 49.487 s | 2.4 / 0.15 ms | community selection: 51.881 / 49.385 s |

Four cases have predicates with at least 1,001 graph matches, but their direct
subject+predicate pairs are small (1, 1, 18, and 1 matches). The indexed store
answers those conjunctions in milliseconds. Thus high global predicate
cardinality is correlated with the slow cases but raw Oxigraph access is not
the bottleneck.

In four of five cases, deterministic community selection accounts for roughly
99% of wall time. Their target subject and predicate records each have only one
recorded community membership, so the cost is not explained by those target
records alone; it occurs while processing the broader matched-seed/community
set. The remaining case (`00096`) has no conjunction hits, invokes the
independent fallback during normal and broadened stages, and spends most time
repeatedly materializing/resolving candidates and provenance. Deduplication and
materialization are negligible in the four conjunction-hit cases.

## Recommendation

**Adopt the conjunction and permanently freeze Retrieval Mech semantics.**

Correctness and ranking metrics are identical to the validated experiment,
all recovered assertions remain traceable, and no successful case regressed.
The remaining tail is an implementation/performance concern centered on
community selection and one fallback-materialization path, not a retrieval
correctness blocker or an Oxigraph lookup problem. Those may be profiled later
as strictly semantics-preserving performance work. The next validation stage
should be bounded end-to-end agentic smokes.

## Artifacts

- `jurisynth/run_outputs/retrieval_stabilization_validation_production_conjunctive.json`
- `jurisynth/evaluation_artifacts/global_batch_stratified_subject-predicate_200_production_conjunctive_summary.json`
- `jurisynth/evaluation_artifacts/global_batch_stratified_subject-predicate_200_production_conjunctive_results.jsonl`
- `jurisynth/evaluation_artifacts/global_batch_stratified_subject-predicate_200_production_conjunctive_ranked_pool.jsonl`
- `jurisynth/evaluation_artifacts/production_assertion_latency_tail_v2.json`
