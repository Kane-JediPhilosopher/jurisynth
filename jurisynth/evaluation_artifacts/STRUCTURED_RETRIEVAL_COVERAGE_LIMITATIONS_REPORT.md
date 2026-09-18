# Structured Retrieval Coverage Limitations

## Scope

Read-only diagnosis using the pre-existing 200-case development artifacts and the repaired production-v2 Oxigraph/E-R artifacts. The completed held-out 100-case evaluation was not rerun, sampled, or used for tuning.

Relevant evidence:

- `assertion_candidate_diagnosis_corrected_interpreter.json`
- `global_batch_stratified_subject-predicate_200_production_conjunctive_cases.jsonl`
- `global_batch_stratified_subject-predicate_200_production_conjunctive_results.jsonl`
- `DEVELOPMENT_STRUCTURED_RETRIEVAL_COVERAGE_DIAGNOSIS.json`

## Main finding

The 66 exact-recall misses in the frozen 200-case development run separate cleanly into two deterministic representation/candidate-generation mechanisms. No miss in this diagnostic set reached final ranking or provenance materialization with the target still present.

| Earliest failure stage | Count | Share of 66 development misses | Classification |
|---|---:|---:|---|
| Literal-object exclusion in E-R index construction | 22 | 33.3% | Representation/index coverage |
| Capped direct subject+predicate conjunction omits target | 44 | 66.7% | Candidate generation and implementation control-flow |
| Final ranking/truncation after target entered evidence | 0 | 0.0% | Not observed |
| Provenance/materialization after target entered evidence | 0 | 0.0% | Not observed |

These are development-set diagnostics, not corrections to the held-out result.

## A. E-R metadata coverage failures

### Cause: URI-object-only construction rule

`build_resource_records()` adds both entities and predicates only inside a guard requiring **both subject and object to be URIRefs**. Therefore, if an assertion has a literal object and the same subject/predicate has no URI-object assertion elsewhere, its required E-R component is absent from metadata.

Observed development evidence:

- 22/22 missing-component cases have a literal/non-URI object.
- 13 have a missing subject; 14 have a missing predicate; several have both.
- All 22 targets exist in the expected source graph in the repaired-v2 KG.
- None has an explicit `rdfs:label` in the KG. Their readable form is nevertheless deterministically derivable from the URI slug, e.g. `is_specified` -> `is specified`.
- This is construction-time representation loss, not a FAISS/query-time matching failure and not evidence of a stale v2 index.

Representative examples:

1. `lower size for green salted fish` — `is specified` — `true`: subject absent.
2. `aid` — `can therefore be authorised` — `true`: predicate absent.
3. `competitors` — `would not substantially differ` — `true`: predicate absent.
4. `direct debits ... cards` — `are included` — `true`: subject absent.
5. `anti-dumping duty ...` — `is hereby re-imposed` — `true`: both components absent.

### Smallest defensible future fix

Build entity records from URI subjects and URI objects independently, and build relation records from every URI predicate regardless of whether the object is a URI or literal. Do not index literal values as entities merely to fix this benchmark.

This requires an E-R index rebuild and a **new** held-out benchmark; the completed held-out set must not be reused for tuning.

## B. Candidate-generation failures

### Cause: direct conjunction cap suppresses the independent fallback

For all 44 remaining development misses:

- target subject and predicate exist in E-R metadata;
- the earlier controlled diagnostic recorded an exact target seed hit;
- the target exists in its expected source graph;
- the current indexed `subject + predicate` Oxigraph lookup returned exactly its 50-item limit;
- the exact target was not among those first 50 graph-qualified rows.

The production `_matching_quads()` implementation returns immediately whenever the conjunctive path has *any* matches. Consequently, when the 50-row conjunction window is full, the independent per-seed fallback is not reached. This is bounded-window censorship, not an Oxigraph failure: the target is present in the KG but excluded before evidence construction.

Representative high-cardinality pairs:

1. `commission` — `cdm:received` — proposed-concentration notification.
2. `commission` — `has decided to declare` — compatibility with common market/EEA.
3. `Emilia-Romagna Region` — `cdm:includes` — Piacenza.
4. `commission` — `cdm:initiates` — formal investigation.
5. `this decision` — `shall enter into force` — `true`.

No current diagnostic case shows target loss in later provenance materialization, deduplication, quality filtering, or final ranking. Those stages were not reached by the target because the direct conjunction window had already censored it.

### Smallest defensible future fix

When the direct subject+predicate lookup reaches its 50-row cap, retain the direct rows but run the already-designed independent per-seed scan as a bounded fallback/union rather than returning early. A more targeted alternative is deterministic, bounded pagination of the exact pair. Either option changes candidate semantics and must be validated on development data, followed by a new untouched held-out sample.

## C. Development-set ceiling estimate

Within the 200 development cases:

- 22/200 (11.0%) are theoretically unrecoverable under the current E-R construction because a required subject or predicate is missing.
- 44/200 (22.0%) have correct exact seeds but are lost at the capped conjunction candidate-generation stage.
- 0/200 are demonstrated ranking-only/truncation losses after target entry.
- 0/200 are demonstrated provenance/materialization losses after target entry.
- 0/200 are demonstrated execution errors in this development run.

These percentages characterize the development diagnostic only. They are not a statistical decomposition of the held-out benchmark and should not be presented as one.

## D. Held-out direct-chunk bookkeeping reconciliation

There is no contradiction:

- `direct_chunk_recall = 0.10` counts **all** 10/100 cases whose expected chunk appeared in direct chunk retrieval, whether or not their exact assertion was recovered.
- `direct_chunk_recoveries = 7` in the failure audit counts only cases that had **both** direct expected-chunk retrieval and exact assertion recovery.
- The remaining three direct-chunk matches did not yield the exact target assertion.

The held-out summary's `sample_mode: source-pool` field is a reporting-label artifact of replaying an already-frozen case file. The immutable replacement sample plan correctly records the actual batch-stratified selection.

## Separate latency note

The conjunction cap is related to high-cardinality behavior, but this report does not diagnose latency. The held-out P95/worst-case latency must remain a separate implementation/storage investigation, not be folded into the correctness interpretation.
