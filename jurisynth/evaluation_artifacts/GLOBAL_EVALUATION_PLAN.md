# Global Jurisynth evaluation plan

This is a compact, thesis-defensible plan.  It separates deterministic
retrieval checks from human legal judgement and NIM-dependent answer checks.
No metric from one layer should be presented as evidence for another layer.

The owner-approved [calibration protocol](CALIBRATION_PROTOCOL.md) supersedes
older metric/rubric/default wording below. Definitions, rubric and provisional
acceptance criteria are adopted; empirical QA, ablation and NLI validation
remain pending. Do not label AI-assisted adjudication as independent expert review.

## 1. Retrieval and provenance integrity — automatic

- **Sample:** 200 known RDF assertions, stratified across batches and source
  documents after the global E-R/chunk artifacts exist.
- **Question form:** transparent controlled probes generated from each known
  assertion.  These are not natural legal questions.
- **Measures:** exact assertion recall at the actual recorded output pool,
  expected-assertion/source recovery, subject/object/
  predicate recall, MRR, direct-chunk recall, status counts, latency.
- **Purpose:** probes recovery of sampled KG facts and sources. It needs no NIM
  calls; malformed or unsupported KG gold must be reviewed before interpreting
  this as validated fact-retrieval performance.

## 2. Natural legal-question retrieval — human review

- **Sample:** the already agreed 20-case formative set: 3 obligations or
  prohibitions, 4 definitions or scope, 4 procedures or deadlines, 6 genuine
  cross-document/dependent questions, and 3 table questions.
- **Construction:** source first.  For every question retain the intended
  document, expected chunk(s), short source excerpt, and why the question is
  natural.  Do not generate questions by echoing an RDF triple or whole row.
- **Measures:** expected-document recall (primary), expected-chunk recall
  (secondary), source/provenance label, retrieval relevance label, and notes.
- **Purpose:** evaluates whether the system finds the intended legal source.
  Report raw counts and the single-reviewer limitation; do not claim stable
  per-category estimates from 20 cases.

## 3. Complex end-to-end reasoning — NIM-dependent audit

- **Sample:** 10 source-grounded scenarios after the global artifacts are
  available: 6 positive questions and 4 deliberately unsupported or
  conflicting-scope questions.
- **Audit fields:** AST/decomposition plausible, required retrieval leaves
  executed, final claims cite supplied evidence, appropriate abstention, and
  no auxiliary table/image evidence treated as standalone legal authority.
- **Measures:** grounded-claim proportion, correct-abstention count,
  provenance coverage, malformed-output/retry count, latency, and NIM cost.
- **Purpose:** tests the integrated Reasoner.  It is an audited pilot, not a
  benchmark accuracy claim.

## 4. LexGLUE — separate zero-shot experiment

- Use the fixed adapter and a declared task split.  Do not tune retriever,
  prompts, or thresholds against the test labels.
- Compare the declared Jurisynth configuration against a clearly named plain
  NIM baseline only if both receive the same input and budget.
- Report task metric, model/version, prompt/version, corpus snapshot, and
  failures.  Keep this separate from provenance evaluation because LexGLUE
  does not supply Jurisynth chunk-level source gold labels.

## Minimal approvals needed from you

1. Confirm this three-layer core: automatic retrieval (200), reviewed natural
   questions (20), and audited complex reasoning (10).
2. For LexGLUE, choose the exact task(s), baseline model(s), and API keys.
3. Review the generated 20 natural questions only after the global candidate
   packet is prepared; I will keep each case self-contained with expected and
   retrieved chunks.

Everything else—case generation, runs, logs, summaries, and reproducibility
artifacts—is safe for me to handle once the global indexes are built.
