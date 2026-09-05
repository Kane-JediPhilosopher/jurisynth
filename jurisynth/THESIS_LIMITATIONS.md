# Jurisynth pilot: limitations and safe claims

This document states what the current Jurisynth pilot can and cannot support in
a thesis. It should be cited alongside the evaluation results rather than
treated as an afterthought.

## Scope

The evaluated system uses `batch_0009`: 100 EU-law documents and 2,910 source
chunks. It is a reproducible pilot corpus, not the planned complete 437-batch
knowledge graph. The Community Graph and E-R indexes used at query time are
therefore pilot artifacts; they do not establish cross-corpus coverage or
global retrieval quality.

## What the retrieval figures mean

The 50-case assertion evaluation is generated from known persisted KG
assertions. Its 0.98 assertion recall and 0.98 provenance-validity figures are
retrieval plumbing and provenance checks, not held-out legal question-answering
accuracy. The 0.66 direct-chunk recall measures a different thing: whether the
expected source chunk was retrieved directly. Neither measure assesses whether
an answer is legally correct, complete, current, or suitable as legal advice.

Table results are weaker and sample-sensitive. The original deterministic
20-row smoke sample recorded 0.15 table/row recall, while a stratified
diagnostic recorded 0.55. The natural-question table diagnostic recorded 0.35.
These are diagnostic baselines from known rows, not a benchmark and not a claim
of general table-question-answering performance.

## Model and decomposition limits

The Agentic Reasoner translates user questions through the QCompiler adapter
and NVIDIA NIM's Nemotron-3-Ultra model. The adapter's AST conversion and a
small live validation set have been tested, but model output remains
probabilistic. Ambiguous questions can yield broad concepts, and a sound
execution trace cannot make unsupported source evidence relevant. Structured
output validation, bounded evidence, and `weak` / `empty` statuses mitigate
this risk; they do not eliminate it.

The pilot contradiction layer is an auxiliary warning mechanism. It currently
uses explicit-negation heuristics by default. A lazy integration for the
`cross-encoder/nli-deberta-v3-base` NLI model is available but not enabled or
threshold-calibrated until a reviewed conflict set exists. No contradiction
warning determines which legal position is correct.

## Deferred work

The full resource aggregation, global community graph, global E-R indexes,
community-expansion strategies, contradiction detector, LexGLUE adapter, and
GUI remain deferred. They must not be represented as evaluated capabilities.
The 20-item human evidence review has been completed. Its labels provide useful
qualitative diagnostics, but the current annotated JSONL has one malformed
record that must be normalized before publishing aggregate human-label rates.
The review remains evidence-retrieval assessment, not legal-correctness review.

## Safe thesis wording

Describe Jurisynth as an evidence-grounded KG retrieval-and-reasoning pilot.
State that it returns traceable source evidence and calibrated retrieval
statuses within a bounded pilot corpus. Do not describe it as a legal advisor,
a complete EU-law system, or a validated legal-QA benchmark.
