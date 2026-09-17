# Adopted evaluation and calibration protocol

Approved by the project owner on 2026-09-13 from ChatGPT's calibration handoff,
with corrections below. Adjudication is AI-assisted, not independent expert
validation. This closes planning decisions, not empirical evaluation tasks.

## Separate outcomes

Record execution completion, exact-target recovery, reviewed answer-bearing
retrieval and reviewed legal answer quality separately. A completed leaf or a
nonempty retrieval result cannot establish any of the latter outcomes.

## Baseline and denominators

The controlled run has 200 attempted cases, 77 exact assertion hits and 17
direct-chunk hits. Every existing aggregate divides by all 200 attempts; misses
contribute zero to MRR. These are unvalidated-gold controlled diagnostics, not
legal-QA accuracy. The 20-case review file intentionally prioritizes misses.
It is not a representative subsample or a new 20-case population.

Direct-chunk matching uses document_id + chunk_id from the separate FAISS chunk
channel, not the five assertion previews. Assertion ranks are computed from the
returned ranked assertion list, not necessarily Recall@60. Do not claim a K
without serializing and recording the actual scoring pool and output limit.

The legacy `provenance_validity` measures exact expected assertions recovered
with their expected source. It is not general provenance correctness. Report
separately: resolvable source pointers / retrieved evidence items; reviewed
source-supported claims / substantive verifiable claims; and expected-assertion
hits with expected provenance / attempted controlled queries.

For reviewed QA, record invalid-gold exclusions with reasons before scoring.
Publish attempted, eligible and excluded counts. Infrastructure failures remain
visible in attempted system-level results; any completed-only diagnostic must
be named explicitly. Report raw x/n alongside all proportions. Report sufficient
and partial retrieval individually, even when a combined target is used.

## Legal-QA rubric and acceptance criteria

Score each applicable dimension 0 (materially deficient), 1 (partial), or 2
(good): legal correctness, evidence support, completeness, qualification,
temporal applicability, provenance correctness, contradiction handling and
abstention appropriateness. Temporal applicability, contradiction handling and
abstention may be N/A with a reason. Preserve actor, scope, instrument, date,
exceptions, conditional duties and uncertainty in review notes.

PASS requires no material legal error, no unsupported material legal conclusion
and at least 75% of applicable points. PARTIAL is useful but incomplete or
underqualified without a severe unsupported conclusion. FAIL includes material
legal error, severe provenance mismatch or failure to abstain on inadequate
evidence. Separately label retrieval sufficient, partial, insufficient or
irrelevant; label each material claim supported, partially supported,
unsupported or contradicted.

Project-specific provisional gates: retrieval execution >=99%; reviewed
claim-to-source support >=95%; zero severe unsupported legal claims in the
reviewed set. Representative QA goals: sufficient or meaningfully answerable
partial retrieval >=80%, PASS >=70%, PASS+PARTIAL >=85%. These are engineering
criteria, not literature-derived constants or population guarantees.

## Bounded retrieval ablation

Keep live retrieval behavior unchanged. `path_expansion=false` was the controlled
assertion probe setting only, not an approved global production default.
For that probe compare A: expansion off/cap50; B: on/cap50; C: off/cap100;
optional D: on/cap100. Use the same fixed 30–50 development cases across runs,
stratified into exact hits, component-only misses and complete misses. Record
case selection and actual configuration. Do not use the miss-heavy review queue
as the sole sample. Keep an independent test set locked before tuning.

Measure exact hits, rank, latency, evidence volume and reviewed answer-bearing
quality/noise. A >=5 percentage-point absolute improvement is a provisional
materiality threshold, not statistical significance. Do not change live
defaults unless improved useful retrieval justifies latency/noise costs.

## Legal-domain NLI validation

Construct 60–100 source-grounded proposition pairs with entailment,
contradiction and neutral labels, including exceptions, actor/object mismatch,
time, modality, numeric conditions and cross-instrument uncertainty. Label
synthetic transformations and AI-generated labels explicitly; these cannot be
represented as expert legal validation. Separate development and locked test
sets before tuning. Keep the existing synthetic 20-pair holdout untuned.

Store pair_id, premise, hypothesis, label, source provision, phenomenon tag,
label origin, review status and notes. Evaluate both pair orders and disclose
the aggregation rule. Report three-class macro F1, per-class precision/recall/F1,
confusion matrix and contradiction precision/recall. Provisional gates are
macro F1 >=0.70 and contradiction precision >=0.80, with qualitative rejection
for systematic scope/time/exception false positives even if aggregates pass.

NLI stays opt-in/advisory. A score is a possible-conflict candidate, not a legal
contradiction determination. Explanation prose cannot override scores or certify
legal correctness.

## Live smoke interpretation

Organized global smoke v5 reached eight leaves, but every retrieval failed on
invalid Query Interpreter JSON; all answers abstained with zero claims. It is
an upstream formatting failure, not a successful legal-QA or NLI evaluation.
Messy v5 failed QCompiler dependency validation before retrieval. Fix and rerun
both before adjudicating substantive quality. Preserve failed artifacts.
