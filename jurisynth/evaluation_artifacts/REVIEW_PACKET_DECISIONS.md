# Review-packet decision record — Batch 0009

## Decisions received

- Natural seed decisions are confirmed.
- The source/retrieval/answer/notes annotation scheme is approved.
- Reporting policy is exploratory: answer-label proportions may be shown only
  as a single-reviewer pilot diagnostic, with raw counts and denominators.
- An `insufficient_evidence` answer is preferable to an unsupported answer.

## Case mix

The entered mix was `3 / 4 / 4 / 7 / 3`, which totals 21. It is interpreted
as the intended 20-case formative allocation:

- obligations/prohibitions — 3
- definitions/scope — 4
- procedures/deadlines — 4
- cross-document/dependent reasoning — 6
- table questions — 3

This keeps the intended emphasis on cross-document reasoning and reduced table
weight while table representation is still being developed. It is a
debugging/pilot allocation; it must not support stable per-category estimates.

## Metric interpretation

For authored natural questions, expected-document recovery is the primary
retrieval measure. Expected-chunk recovery is a stricter secondary measure:
one legal question can reasonably have support spread over multiple chunks.
Keep both measures separate from assertion-probe recall.

## Reporting guardrails

Provenance and cautious Reasoner language make exploratory reporting more
auditable; they do not establish legal correctness or independently validate
answer faithfulness. Report the four labels, raw counts, corpus scope, and the
single-reviewer limitation. Do not set thresholds from this sample while
source-validity and harmful-failure targets remain unknown.

## Source-first construction constraint

The existing 50 assertion fixture is dominated by a single national-allocation
table document, so it cannot honestly supply this five-class natural-question
set. The next review batch must be assembled from source-validated examples
across documents, rather than mechanically relabelling the old fixture.
