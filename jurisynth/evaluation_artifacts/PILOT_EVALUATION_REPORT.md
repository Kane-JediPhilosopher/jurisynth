# Jurisynth batch_0009 pilot evaluation report

**Report version:** 1.0  
**Corpus scope:** `batch_0009` only — 100 processed EU-legislation documents and 2,910 indexed chunks.  
**Embedding model:** `all-MiniLM-L6-v2` (local).  
**Purpose:** record reproducible retrieval diagnostics for the pilot implementation. This is not a legal-QA benchmark, a LexGLUE result, or a claim of legal correctness.

## Reproducibility

The secret-free, hash-backed pre-run manifest is [pilot_manifest.json](pilot_manifest.json). It records the pilot source artifacts, command templates, and model identifiers. The measurements below use persisted `batch_0009` graph, chunk, table, and E-R-index artifacts.

## Results

### Assertion-provenance retrieval integrity

- 50 deterministic known-assertion probes.
- Assertion recall: **49/50 (0.98)**.
- Assertion-to-source-chunk provenance validity: **49/50 (0.98)**.
- Direct chunk-FAISS recall: **33/50 (0.66)**.
- Empty/error results: **0/50**.

The single retained assertion miss is `assertion_00021` (`the central administrator — shall enter — belgium`). This set is generated from the same pilot graph it tests. It checks retrieval plumbing and provenance preservation, not generalisation to unseen legal questions.

Source artifacts: `batch_0009_fallback_50_cases.jsonl`, `batch_0009_fallback_50_results.jsonl`, and `batch_0009_fallback_50_summary.json`.

### Table retrieval diagnostics

| Diagnostic | Cases | Table recall | Row recall | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Natural identifier/context questions | 20 | 0.35 | 0.35 | Current practical baseline; weak supervision from known rows. |
| Stratified row-echo integrity probes | 20 | 0.55 | 0.55 | Shows strong sensitivity to table type and sample composition. |

The natural-question run produced one `success` and nineteen `weak` results; neither run had runtime errors. These are retrieval diagnostics, not a TableRAG comparison or a user-study result. The variance reinforces the need for a larger, manually reviewed, stratified table set before selecting a reranker or threshold.

Source artifacts: `batch_0009_table_natural_20_summary.json`, `table_stratified/`, and `batch_0009_table_fallback_20_summary.json` (legacy sequential integrity baseline).

### Natural, source-aligned seed questions

- Three reviewed natural-language questions with a designated document/chunk.
- Expected-document recall: **3/3 (1.00)**.
- Expected-chunk recall: **3/3 (1.00)**.
- Empty/error results: **0/3**.

The source review recorded in `natural_query_pilot/REVIEW_DRAFT.md` retained the two citizens'-initiative cases, rewrote the Vehicle Register case to its directly supported `chunk_3`, and excluded the invalid Serbia case. This remains a tiny, source-aligned pilot set rather than a benchmark score.

## Evidence and answer-quality denominators

The pilot can already report the following denominators without overstating its evidence:

- **Assertion recall:** known target assertion retrieved / known assertion cases.
- **Provenance validity:** retrieved target assertion with a valid linked source chunk / known assertion cases.
- **Direct chunk recall:** expected source chunk retrieved by chunk search / known assertion cases.
- **Table and row recall:** expected table or row retrieved / table diagnostic cases.
- **Natural source alignment:** expected document or chunk retrieved / manually source-checked natural cases.
- **System reliability:** successful, weak, empty, and error results / all cases.

Answer faithfulness, contradiction quality, latency, cost, and calibrated acceptance thresholds remain intentionally unreported. They require a reviewed legal-QA set, labelled contradiction examples, and stable live-NIM service measurements.

## Operational validation

- Offline complex-workflow regression: passed. It verifies a realistic multiline consumer scenario with parallel and dependent leaves, fact/jurisdiction preservation, and dependency-output substitution.
- Live multiline QCompiler/NIM translation: passed in 35.08 seconds under a bounded two-attempt smoke configuration.
- Full live NIM workflow remains a service-bound validation: it should be rerun when the NVIDIA endpoint returns stable structured responses. The CLI now supports `JURISYNTH_NIM_TIMEOUT_SECONDS` and optional `JURISYNTH_NIM_MAX_ATTEMPTS` for bounded validation without changing the default infinite-retry production policy.

## Limitations and next valid claims

The pilot demonstrates an auditable retrieval-and-reasoning architecture over one 100-document batch. It does **not** yet demonstrate full-corpus coverage, calibrated ranking, comparative table performance, legally correct advice, or performance on a held-out legal benchmark. The next defensible evaluation step is to complete the source review, expand a labelled source-first natural-query set, and then select thresholds/rerankers from those labels.
