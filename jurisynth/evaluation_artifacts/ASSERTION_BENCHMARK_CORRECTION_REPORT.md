# Controlled Assertion Benchmark Correction

Production Retrieval Mech remained frozen. The only behavioral change was an
explicit benchmark flag that deterministically parses the quoted subject label
as one entity concept and the quoted predicate label as one relation concept.
No NIM call was used. The repaired v2 artifacts, 200 fixed cases, E-R settings,
quad limits, ranking, and evidence limits were unchanged.

## Before / after (200 fixed cases)

| Metric | Previous raw-leaf benchmark | Corrected benchmark |
|---|---:|---:|
| Exact assertion recall | 38.5% | 55.0% |
| Provenance validity | 38.5% | 55.0% |
| Direct source/chunk recall | 8.5% | 8.5% |
| Subject recovery | 45.5% | 83.0% |
| Predicate recovery | 43.5% | 82.5% |
| Object recovery | 46.0% | 57.0% |
| MRR | 0.2017 | 0.3918 |
| Recall@1 | 14.5% | 33.0% |
| Recall@3 | 22.0% | 43.5% |
| Recall@5 | 27.5% | 47.0% |
| Recall@10 | 33.0% | 50.5% |
| Recall@20 | 36.5% | 54.5% |
| Recall@40 | 38.5% | 55.0% |
| Mean latency | 4.053 s | 8.119 s |
| Median latency | 4.024 s | 0.704 s |
| P95 latency | 4.451 s | 61.454 s |

The corrected interpreter greatly improves typical latency, but exact common
labels expose a long tail in the fixed per-seed graph scan. One case took
182.021 seconds.

## Residual exact-assertion misses (90)

| Earliest failure stage | Count | Share |
|---|---:|---:|
| Graph expansion / candidate generation | 68 | 75.6% |
| Subject and/or predicate absent from E-R metadata | 22 | 24.4% |
| E-R grounding despite indexed target | 0 | 0.0% |
| Pruning/filtering | 0 | 0.0% |
| Ranking cutoff | 0 | 0.0% |
| Representation mismatch | 0 | 0.0% |

All 68 candidate-generation misses had both subject and predicate indexed and
matched as target seeds, but the exact assertion did not enter the candidate
pool. This is consistent with the unchanged 50-quads-per-seed bound censoring
the target for high-degree subjects or predicates.

Among the 22 index-representation limitations, eight lack the subject, nine
lack the predicate, and five lack both. The previously identified 16 cases are
all still visible within this group; none were hidden by threshold changes.

## Decision

Do not implement lexical + FAISS hybrid seeding: indexed grounding is not the
dominant residual failure. Keep production retrieval frozen. The smallest next
experiment, if retrieval is reopened, is a bounded conjunctive subject+predicate
candidate lookup when both matched seeds are available, compared against the
current independent 50-quads-per-seed scan. Do not lift the global cap or change
ranking until that isolated comparison is measured.

