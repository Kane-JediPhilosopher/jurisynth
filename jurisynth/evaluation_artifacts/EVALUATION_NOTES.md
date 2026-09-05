# batch_0009 retrieval smoke baseline

Run configuration: URI-free assertion queries generated from the persisted
`batch_0009` RDF graph; local `all-MiniLM-L6-v2` embeddings; persisted pilot
E-R indexes; direct and bounded-path RDF retrieval; no NVIDIA NIM call.

Artifacts:

- `batch_0009_fallback_50_cases.jsonl`
- `batch_0009_fallback_50_results.jsonl`
- `batch_0009_fallback_50_summary.json`

Observed result: 49/50 exact assertion recall and 49/50 valid assertion-to-
source-chunk provenance (0.98 for each). Direct chunk-FAISS recall was 33/50
(0.66). All 50 calls returned `success`; no runtime errors occurred.

The retained miss is `assertion_00021`:

```text
the central administrator --shall enter--> belgium
```

This is a retrieval plumbing/provenance smoke baseline derived from known KG
assertions. It is not held out, does not measure legal-answer correctness, and
must not be presented as a LexGLUE or legal-QA benchmark score. The miss should
be included in the manual evidence review set.

The direct-chunk measure is intentionally reported separately: it asks whether
the expected source chunk is returned by chunk retrieval, whereas provenance
validity asks whether a retrieved assertion maps to a valid source chunk. These
are complementary retrieval diagnostics, not measures of answer correctness.

## Table-row retrieval smoke baseline

Run configuration: the first 20 deterministic non-empty rows from persisted
`batch_0009` table JSON, queried against the batch table/row FAISS indexes with
the local `all-MiniLM-L6-v2` embeddings. No NVIDIA NIM call was made.

Artifacts:

- `batch_0009_table_fallback_20_cases.jsonl`
- `batch_0009_table_fallback_20_results.jsonl`
- `batch_0009_table_fallback_20_summary.json`

Observed result: 3/20 table recall and 3/20 row recall (0.15 for each). All
calls returned `weak`; there were no runtime errors. The first deterministic
cases concentrate in dense numeric tables, and their query template includes
the known full row text. Therefore this is a diagnostic of current table index
retrieval, not a representative quality estimate. Do not tune or make thesis
quality claims from this sample alone; stratify later by table type, row text
density, and document.

## Stratified table-row diagnostic

To reduce the sequential sample's concentration in one numeric document, a
second deterministic 20-case run selected one row at a time across numeric,
mixed, and text-heavy profiles while preferring distinct documents.

Artifacts are under `table_stratified/`. Observed table and row recall were
11/20 (0.55), with 2 `success` and 18 `weak` outcomes. This difference confirms
that table retrieval is strongly sample-dependent. Preserve both runs; neither
is a representative benchmark or a basis for tuning thresholds without a
larger stratified review set.
# Updated evaluation protocol

## Retrieval-budget regression check

The direct RDF retriever previously returned 1,457 evidence assertions for a
single ambiguous live query. The model-facing layer was protected by a prompt
budget, but broad RDF candidate generation remained a precision and observability
problem.

The retained policy keeps the original top-5 E-R candidate completeness for
single-concept provenance probes, applies multi-concept corroboration when more
than one distinct concept is available, and retains at most 60 ranked evidence
items for a completed bundle. The 50-case assertion regression result after this
change was **0.98 assertion recall** and **0.98 provenance validity**, identical
to the prior baseline.

An earlier, more aggressive setting (top-3 candidates, 0.60 similarity cutoff,
and 80 quads per seed) reduced both measures to 0.80. It was rejected rather
than reported as an improvement.

For the live question “What obligations apply to a data controller?”, the
observed failure is layered: NIM query interpretation can generate broad terms;
the former E-R/RDF OR expansion amplified them into irrelevant aviation
evidence; and direct chunk-FAISS results were initially retained only as
metadata rather than supplied to the leaf model. The latter is corrected: direct
chunk hits are now citable `C_...` EvidenceItems but remain explicitly weak
unless structured/table support independently justifies success.

The pilot coverage inspector found 2,910 chunks across 100 documents. It found
an explicit data-controller passage in `L_2011065EN.01000101`, `chunk_6`, and
multiple GDPR / Regulation (EU) 2016/679 passages. Thus the prior live miss is
not evidence that this pilot lacks all relevant material.

The original table-row cases used full-row echo queries (for example, “Find the
table row containing: …”). They are retained only as deterministic
**retrieval-integrity probes**. They do not represent realistic user questions.

The default table evaluation now uses a short question built from one row
identifier and table context, such as “What information is recorded … for Code
‘BE0001’?”. It remains weak supervision because the questions are derived from
known rows, so its result must not be reported as held-out legal-QA quality.

The recorded 20-case natural-question run returned 0.35 table recall and 0.35
row recall, with one `success`, nineteen `weak` outcomes, and no runtime
errors. This is the current practical table-retrieval baseline to improve, but
it is still a diagnostic rather than a comparative TableRAG-style evaluation.

Assertion-review JSONL records generated after this update contain up to five
retrieved assertion/source excerpts and blank `human_review` fields. A reviewer
should label relevance, whether the excerpt supports the assertion, and whether
the returned retrieval status was appropriate.

## Entity-grounding and ranking follow-up

The human review correctly identified that the legacy assertion probes were
machine-generated subject/object questions, often omitted the predicate, and
could surface neighbouring country assertions sharing a predicate and object.
They remain reproducible legacy regression artifacts, not a natural-question
evaluation set.

New controlled probes include the subject and predicate. Their case-level
results separately record subject-entity recall, object-entity recall,
predicate recall, and the rank of the expected assertion. The existing review
excerpt is only the top five of the complete bounded bundle; the new rank field
prevents an assertion retrieved below that preview from being mistaken for a
top-ranked answer.

At query time, exact normalized labels (for example, `Belgium`) now take
precedence over FAISS semantic neighbours for that individual concept. This is
not a floating-point “perfect similarity” cutoff: exact vector scores are not
stable lexical-identity tests, and such a cutoff would discard valid semantic
matches. NIM query interpretation is also instructed to preserve named entities
verbatim. Approximate FAISS matching remains the fallback where no exact label
exists.

The Retrieval Mech now performs one bounded `broaden_candidates` escalation
attempt after a `weak` or `empty` normal result. It expands only structured E-R
candidates, retains the original evidence, records the attempted stages, and
does not invoke a second query-interpretation LLM call. Deeper path and
conjunctive fallbacks are intentionally not enabled until their stop conditions
can be evaluated independently.

`batch_0009_natural_query_seeds.jsonl` contains four human-readable,
source-aligned questions with expected document/chunk targets. These are the
next live evaluation seeds once NIM capacity permits. They are deliberately
separate from synthetic assertion probes and are not a held-out benchmark.
