# Direct Indexed Conjunctive Lookup Refinement

The refinement replaces benchmark-only per-pair SPARQL with Oxigraph's indexed
`quads_for_pattern(subject, predicate, *, *)` operation. Full graph-qualified
quad rows are retained and deduplicated; the unchanged independent scan remains
the fallback. Production retrieval has not been modified.

## First conjunction experiment vs indexed refinement

| Metric | Per-pair SPARQL | Direct indexed pattern |
|---|---:|---:|
| Exact assertion recall | 67.0% | 67.0% |
| MRR | 0.4373 | 0.4373 |
| Recall@1 | 35.5% | 35.5% |
| Recall@3 | 48.5% | 48.5% |
| Recall@5 | 55.5% | 55.5% |
| Recall@10 | 59.5% | 59.5% |
| Recall@20 | 66.0% | 66.0% |
| Recall@40 | 67.0% | 67.0% |
| Candidate-generation misses | 44 | 44 |
| Mean latency | 7.960 s | 6.116 s |
| Median latency | 0.774 s | 0.628 s |
| P95 latency | 61.863 s | 51.534 s |
| Worst-case latency | 116.127 s | 57.761 s |
| Designated-gold provenance | 65.0% | 65.0% |

All 134 exact recoveries remain graph-provenanced. Of those, 130 match the
benchmark's designated source and four are traceable alternate-source matches:
`global_assertion_00036`, `global_assertion_00105`,
`global_assertion_00180`, and `global_assertion_00190`.

No previously successful case regressed. No case-level recall, rank, or
provenance result changed relative to the first conjunction experiment. The
indexed refinement still recovers 24 of the original 68 candidate-generation
misses.

## Adoption decision

Recommend adopting the direct indexed conjunctive lookup, then freezing
retrieval semantics. It preserves 67% recall with zero regressions while
reducing mean latency by 23.2%, P95 by 16.7%, and worst-case latency by 50.3%
relative to the per-pair SPARQL experiment.

P95 remains pathological at 51.534 seconds. Do not attempt another retrieval-
semantics change to address it. Treat the remaining tail as a separate storage,
seed-cardinality, and fallback-performance diagnostic before permanent freeze.

