# Controlled architecture-fix report

Date: 2026-09-16  
Artifact root: `jurisynth/global_artifacts_source_uri_v2`  
Graph fingerprint: `6166222635c5fbc55001f1f763a4196c0ef7f917a54c5da068164e82ad301c84`

## Outcome

The controlled changes passed the bounded acceptance suite. QCompiler is now
the only LLM that defines hard AST dependencies; execution is an event-driven,
bottom-up DAG. Intake and task analysis use one structured call. Query
interpretation is leaf-scoped, E-R vector searches are batched by index kind,
and table/image retrieval records global versus source-document-scoped origins.

## Files changed

- Reasoner: `main.py`; `agentic_reasoner/intake.py`, `qcompiler_translator.py`,
  `scheduler.py`, `schemas.py`, and `workflow.py`.
- Retrieval: `contracts.py`; `retrieval_mech/artifacts.py`, `config.py`,
  `er_matcher.py`, `mechanism.py`, `query_interpreter.py`, and
  `rdf_retriever.py`.
- Diagnostics/docs: `diagnostics/latency_probe.py`,
  `diagnostics/community_diagnostics.py`, `CHECKLIST.md`, this report, and the
  controlled-plan document.
- Tests: reasoner intake/QCompiler/scheduler/workflow tests; retrieval
  E-R/RDF/mechanism/image/interpreter tests; latency-probe tests.
- Generated, versioned local evidence: repaired-v2 four-way E-R shards; the
  architecture-fix request fixtures and `run_outputs/architecture_fix_*`
  captures/replays. Existing monolithic indices and v2 KG artifacts were not
  overwritten.

## Measurements

- Complex-query planning calls before leaf execution: **4 logical LLM calls → 2**
  (Intake + Task Analysis + QCompiler + Semantic Dependency Planner becomes
  combined Intake/Analysis + QCompiler). Physical transport retries remain
  separately logged and are not counted as logical calls.
- Frozen-concept q003 local retrieval: **53.360 s → 33.046 s**. The same 67
  evidence IDs and 69 source-chunk identities were retained during the
  code-only batching/two-pass comparison.
- Final leaf-scoped q003 interpretation: **23 concepts → 12** (14 entity + 9
  relation becomes 8 entity + 4 relation). The accepted live call took 34.085 s,
  one provider request, no retry.
- q003 E-R matches: **185 → 101**; pre-filter structured candidates:
  **1,595 → 860**; selected structured evidence: **60 → 26**.
- q003 final local retrieval with the new concepts: **22.790 s**, 33 total
  evidence items, 32 unique source chunks, and 14 evidence items supported by
  the AI Act document. The eight direct chunk hits were unchanged; seven remain
  AI Act excerpts.
- The final q003 modality pass scoped itself to two chunk-surfaced documents and
  added about **116 ms**. It found no source-local table/image evidence. Five
  low-scoring global table rows remain visible as direct candidates.
- Companion interpreter checks: simple importer leaf, 5 concepts in 11.019 s;
  named Article 25 leaf, 9 concepts in 32.687 s. Both preserved the named
  instrument/article and completed in one provider request without retry.

## Community diagnostics

- 1,263,436 hierarchy/descriptor nodes; four levels; zero missing parents.
- q003 selected three leaf communities plus one LCA. All exist in the repaired
  v2 hierarchy; average tree distance was 3.0 and maximum distance was 4.
- Lazy summarisation did not trigger. With selector `top_n=3`, orientation can
  contain at most four communities, so the six-community trigger is unreachable;
  q003 also remained below the separate average-distance trigger of 4.0.
- The hierarchy has weak compression (315,599 roots for 316,635 level-0 nodes).
  This is a measured topology property, not evidence of file corruption. Per the
  controlled plan, no community threshold or Leiden setting was changed.

## Tests

- Final bounded suite: **152 passed, 6 optional skips, 0 failures**.
- Covered combined intake/analysis, QCompiler AST validation, event-driven DAG
  scheduling, genuine dependencies, parallel leaves, batched E-R matching,
  retrieval status, source-scoped table/image retrieval, modality provenance,
  community orientation, and diagnostic replay contracts.

## Remaining calibrated decision

Global table candidates cannot yet be safely filtered with the shared 0.55
threshold. q003's irrelevant rows scored 0.26–0.33, but a reviewed correct
Lakeland Dairies table row scored only 0.376. Applying 0.55 would remove both
noise and valid evidence. A small labelled table-relevance calibration is
therefore required before changing the production inclusion/reranking rule.
The existing direct candidates and their provenance were retained.

Community trigger/LCA defaults also remain an explicit deferred decision after
topology review; they do not block the current deterministic orientation path.

## Validation limits

These are controlled component and retrieval measurements, not a legal-answer
evaluation or a broad LexGLUE/global report smoke. No extraction prompt, model,
provider, retry policy, output-token policy, KG artifact, or provenance graph
was changed.
