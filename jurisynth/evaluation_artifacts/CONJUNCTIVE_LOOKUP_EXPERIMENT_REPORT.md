# Experimental Conjunctive Subject + Predicate Lookup

This experiment was enabled only by a controlled-benchmark command-line flag.
Production retrieval remains unchanged. The existing independent per-seed scan
was retained as fallback when the bounded conjunction returned no candidates.

## Corrected baseline vs experiment (200 fixed cases)

| Metric | Corrected baseline | Conjunctive experiment |
|---|---:|---:|
| Exact assertion recall | 55.0% | 67.0% |
| MRR | 0.3918 | 0.4373 |
| Recall@1 | 33.0% | 35.5% |
| Recall@3 | 43.5% | 48.5% |
| Recall@5 | 47.0% | 55.5% |
| Recall@10 | 50.5% | 59.5% |
| Recall@20 | 54.5% | 66.0% |
| Recall@40 | 55.0% | 67.0% |
| Candidate-generation misses | 68 | 44 |
| Mean latency | 8.119 s | 7.960 s |
| Median latency | 0.704 s | 0.774 s |
| P95 latency | 61.454 s | 61.863 s |
| Worst-case latency | 182.021 s | 116.127 s |
| Designated-gold provenance validity | 55.0% | 65.0% |

The conjunction recovered 24 of the 68 diagnosed candidate-generation misses.
No previously successful exact-assertion case regressed. Four newly recovered
exact assertions were supported by an alternate source chunk rather than the
benchmark's designated expected chunk, explaining the two-point gap between
67% exact recall and 65% designated-gold provenance validity.

## Recommendation: refine once

The recall improvement is clear and has no exact-recall regressions, but the
experiment did not materially improve P95 latency and the designated-source
provenance result needs review. Do not merge this version into production.

Run one isolated refinement using the Oxigraph indexed subject+predicate pattern
directly instead of issuing per-pair SPARQL queries, while retaining all matching
source graphs for deduplication/provenance. Re-run the same 200 cases once. Adopt
only if recall is preserved, the four alternate-source cases remain traceable,
and P95 improves without regressions.

