# Jurisynth retrieval-stabilization review hand-off

Date: 2026-09-17

## Review request

Please review the final retrieval-stabilization pass described below. Treat the
linked code and captured results as evidence. Do not redesign the entire
Retrieval Mechanism. The immediate question is whether the narrowly proposed
follow-up is justified by the failed cross-instrument gate, and whether there
is a smaller deterministic correction.

Please answer:

1. Is the document-identity and instrument-scope logic faithful to the stated
   policy, especially its treatment of ambiguous/title-only documents?
2. Is the retrieval-status rule safe, or should a multi-instrument leaf require
   evidence coverage for every explicitly named, unambiguously resolved
   instrument before it can return `success`?
3. Does the failed AI Act + IVDR check justify a bounded explicit-instrument
   source-scoped candidate pass?
4. If yes, what is the smallest implementation that improves recall without
   turning instrument names into a hard evidence filter or suppressing useful
   cross-instrument evidence?
5. Is there any defect in the two-pass table merge/dedup/rerank logic?
6. Based on the evidence, should retrieval be frozen after that bounded fix, or
   is the failure better documented for retrieval-quality evaluation?

## Intended policy

### Document identity

- `document_id` is a lookup key, not an instrument identifier.
- Prefer CELEX/ELI identity when available, then primary title/heading.
- Do not infer identity from filenames.
- Corrigenda and modern document-ID variants must not be decoded heuristically.
- Ambiguous identity remains `unknown`.

### Leaf scope

- Resolve scope from the leaf query first.
- Use clearly leaf-local contextual facts only when the leaf itself names no
  instrument.
- Global/inherited constraints are contextual candidates and do not
  automatically become primary scope.
- Evidence classifications are `in_scope`, `cross_instrument`, or `unknown`.
- Preserve every evidence item; scope changes ranking and status, not deletion.

### Retrieval and tables

- In-scope evidence receives deterministic priority.
- Cross-instrument evidence remains available at lower scope priority.
- Out-of-scope similarity alone cannot establish strong retrieval success.
- Table Pass 1 is global FAISS retrieval.
- Table Pass 2 is source-document-scoped FAISS retrieval.
- Merge both pools, deduplicate, then rerank once and apply the existing limit.
- No new LLM verifier, scoring model, top-p truncation, or separately calibrated
  pass thresholds.
- The repaired Community Graph is frozen.

## What was implemented

1. A read-only SQLite document-metadata sidecar keyed by `document_id`.
2. Deterministic CELEX, ELI, citation, title, and conservative alias parsing.
3. Leaf-first scope resolution and per-evidence/table/image classification.
4. Stable scope-priority ordering while preserving existing relevance order.
5. Retrieval-status protection against cross-instrument evidence producing
   success by itself.
6. Corrected table Pass 1 so it is always global, followed by source-scoped
   Pass 2, merge, deduplication, and one reranking step.
7. Scope and table-pass diagnostics in retrieval metadata.
8. Loading the sidecar in global workflow, benchmark, tracing, candidate-packet,
   assertion-evaluation, and latency-diagnostic entry points.
9. Focused unit/regression tests and a five-case local validation runner.

The Community Graph, Leiden configuration, community hierarchy, and lazy
summarizer were not modified.

## Sidecar audit

- Documents: 43,694
- Identified by canonical metadata or title: 43,101
- CELEX: 12,835
- ELI: 5,123
- Primary titles: 43,034
- Persisted aliases: 93,656
- Sidecar path:
  `jurisynth/global_artifacts_source_uri_v2/document_metadata.sqlite`

The final ambiguity correction classifies a title-only document with no
canonical identity as `unknown`, rather than assuming it is a different
instrument.

## Validation results

The validation was local-only with fixed concepts. It made no NIM calls and did
not rebuild any global artifact.

### q003 — AI Act

- Gate: pass
- Retrieval status: `success`
- Latency: 22.672 seconds
- Evidence: 33
- Scope: 14 in-scope, 19 cross-instrument, 0 unknown
- Expected-source coverage: 1/1 (`L_202401689EN`)
- Tables: Pass 1 = 5, Pass 2 = 0, merged/reranked = 5
- All table hits were cross-instrument and did not determine success.

### Simple single-instrument AI Act leaf

- Gate: pass
- Retrieval status: `success`
- Latency: 8.032 seconds
- Evidence: 14
- Scope: 14 in-scope, 0 cross-instrument, 0 unknown
- Expected-source coverage: 1/1 (`L_202401689EN`)
- Tables: 5 / 0 / 5

### Genuine cross-instrument AI Act + IVDR leaf

Query:

> How do provider obligations under Regulation (EU) 2024/1689 (AI Act)
> interact with manufacturer obligations under Regulation (EU) 2017/746
> (IVDR) for an AI-enabled in vitro diagnostic device?

- Gate: fail
- Retrieval status: `success`
- Latency: 85.785 seconds
- Evidence: 12
- Scope: 5 in-scope, 7 cross-instrument, 0 unknown
- Expected-source coverage: 1/2
- AI Act source survived: `L_202401689EN`
- IVDR source missing: `L_2017117EN.01017601`
- Tables: 5 / 5 / 5

Interpretation: scope ranking did not remove the IVDR source; the underlying
candidate generation never returned it. The status is also arguably too coarse
because one of two named instruments was enough to produce `success`.

### Known table-primary case

- Gate: pass
- Retrieval status: `success`
- Latency: 7.514 seconds
- Expected-source coverage: 1/1 (`L_2010041EN.01000801`)
- Rows 0, 1, and 2 of `table_10` survived the final merged pool.
- Tables: 5 / 5 / 5

### Non-table GDPR safety control

- Gate: pass as a safety control
- Retrieval status: `weak`
- Latency: 7.219 seconds
- Evidence: 8
- Scope: 0 in-scope, 8 cross-instrument, 0 unknown
- Expected GDPR source was not retrieved.
- Unrelated high-similarity material did not falsely produce `success`.
- This remains a genuine recall miss for later retrieval-quality evaluation.
- Tables: 5 / 5 / 5

## Automated checks

- Focused regression suite: 33 passed, 1 skipped.
- Final scope/mechanism rerun: 18 passed.
- No known regression in provenance preservation.
- The runtime cross-instrument gate is the only failed stabilization gate.

## Proposed bounded follow-up — not yet implemented

The current proposal is:

1. Resolve explicitly named instruments through the sidecar.
2. When an unambiguous named instrument is absent from the ordinary candidate
   pool, run one bounded source-document-scoped candidate pass for that
   instrument.
3. Merge those candidates into the ordinary pool, preserving provenance and
   existing relevance/channel signals.
4. Do not delete or hard-filter evidence from other instruments.
5. For a multi-instrument leaf, return strong `success` only when every
   explicitly named and unambiguously resolved instrument has at least one
   qualifying supporting item; otherwise return `weak`.
6. Apply strict bounds and diagnostics, then rerun only the same five gates.

Please challenge this proposal if it is unnecessary, likely to bias retrieval,
or can be replaced by a smaller deterministic correction.

## Files to review

Core implementation:

- `jurisynth/retrieval_mech/document_metadata.py`
- `jurisynth/build_document_metadata.py`
- `jurisynth/retrieval_mech/mechanism.py`
- `jurisynth/retrieval_mech/global_artifacts.py`
- `jurisynth/contracts.py`
- `jurisynth/main.py`

Integration points:

- `jurisynth/benchmark_global_retrieval.py`
- `jurisynth/prepare_global_candidate_packet.py`
- `jurisynth/run_global_assertion_evaluation.py`
- `jurisynth/diagnostics/tracing.py`
- `jurisynth/diagnose_local_retrieval_latency.py`

Tests and captured results:

- `jurisynth/retrieval_mech/tests/test_document_metadata.py`
- `jurisynth/retrieval_mech/tests/test_mechanism.py`
- `jurisynth/run_retrieval_stabilization_validation.py`
- `jurisynth/run_outputs/retrieval_stabilization_validation.json`
- `jurisynth/run_outputs/RETRIEVAL_STABILIZATION_REPORT.md`

## Requested response format

Please return:

- `APPROVE`, `APPROVE WITH CHANGES`, or `DO NOT APPROVE`;
- any correctness defect, with the relevant file/function;
- whether full named-instrument coverage should be required for `success`;
- whether the bounded source-scoped pass is justified;
- the smallest recommended change set;
- the exact focused tests that should be rerun;
- any reason retrieval should not be frozen after those tests.
