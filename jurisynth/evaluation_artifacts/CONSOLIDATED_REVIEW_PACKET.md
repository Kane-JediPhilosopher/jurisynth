# Consolidated evaluation review packet

This is the complete set of human judgments needed before expanding the
Batch-0009 evaluation.  Reply in one message using the IDs below.  Honest
`UNKNOWN` is preferable to an invented judgement.

## A. Confirm the reviewed natural seed set

The source-validation decisions already recorded are:

- `natural_001`: KEEP
- `natural_002`: KEEP
- `natural_003`: REWRITE approved; replacement asks about European Vehicle
  Register data-management functions and targets `L_2018268EN.01005301`,
  `chunk_3`.
- `natural_004`: DROP.

Reply: `A: CONFIRM`.

## B. Choose the next reviewed-case mix

Assign a count totalling **20**.  Use `0` where Batch 0009 has too little
coverage.

- `B1 obligations/prohibitions:` 3
- `B2 definitions/scope:` 4
- `B3 procedures/deadlines:` 4
- `B4 cross-document or dependent reasoning:` 7
- `B5 table questions:` 3

NOTE: Are B1-B3 generalizable to other potential documents? The heuristic I'm going for is a stable knowledge base, slight emphasis on cross-doc analysis and less for tabular analysis due to potentially inadequate data representation for tabular data. 


## C. Annotation rules to approve

For each future case, you will receive the question, designated source excerpt,
and retrieved excerpts.  Record:

- `SOURCE`: valid / questionable / invalid
- `RETRIEVAL`: direct / partial / irrelevant / absent
- `ANSWER`: supported / partly_supported / insufficient_evidence / unsupported
- `NOTES`: one sentence identifying the reason.

Reply: `C: APPROVE`.

## D. Pilot reporting policy

- `D2: exploratory` — also report answer-label proportions, explicitly marked
  as a single-reviewer pilot diagnostic.

I believe the Agentic Reasoner already provides sufficient hedging and provenance to allow more expressiveness. Thoughts?

## E. Quality target for expansion

Fill in only values you can defend; `UNKNOWN` is valid.

- Minimum acceptable source-validity rate: 'UNKNOWN'
- Minimum acceptable expected-chunk recall for reviewed natural questions: 'UNKNOWN; However, I believe this can be lower than that for assertions.'
- Is an `insufficient_evidence` answer preferable to an unsupported answer?
  yes / no / depends: yes
- What failure is most damaging for your thesis use case? 'UNKNOWN'

## What I will do after one reply

I will generate one stratified, source-first 20-case review batch; preserve all
source excerpts and retrieved excerpts; compute only the approved denominators;
and add a thesis-safe interpretation.  I will not label legal correctness or
choose thresholds on your behalf.

