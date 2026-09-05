# Batch-0009 human-review sampling guidance

## What the original 20-case cap means

Twenty cases divided across five categories gives four cases per category.
That is useful as a formative smoke review, but it is too small to make a
stable category-level comparison or to support a numerical quality claim. A
single changed judgement moves a four-case category by 25 percentage points.

## Recommended thesis-pilot design

Use **50 source-validated cases: 10 per category**.

- obligations/prohibitions — 10
- definitions/scope — 10
- procedures/deadlines — 10
- cross-document or dependent reasoning — 10
- table questions — 10

This is a pragmatic diagnostic sample, not a statistically representative
benchmark. Report every category count, the source-selection process, and
uncertainty plainly. At ten cases a changed judgment still moves a category by
10 points, so do not present small percentage differences as decisive.

If a category cannot supply ten source-valid examples in Batch-0009, record
the shortfall and replace only with a predeclared adjacent category. Do not
silently fill it with easier items.

## Effort-sensitive fallback

If 50 reviews would prevent you from finishing the thesis, use **30 cases: six
per category**. Report only pooled results and category-level examples; do not
claim comparative performance between categories. Twenty cases remains useful
only for debugging and should be described as a formative inspection set.

## When to use 100 cases

Use **100 cases: 20 per category** only if comparing two retrieval
configurations or models in the thesis. It gives a better descriptive basis,
but it still is not a substitute for a broad, independently sampled benchmark.
It is not the recommended immediate priority under the current deadline.

## Annotation discipline

Build the 50-case packet in one deterministic run, but review it in whatever
increments preserve attention. For every item retain the question, designated
source excerpt, expected document/chunk, retrieved excerpts, and the four
human labels already defined in the consolidated packet. Mark `UNKNOWN` rather
than guessing. Keep source validity separate from retrieval quality and answer
faithfulness.
