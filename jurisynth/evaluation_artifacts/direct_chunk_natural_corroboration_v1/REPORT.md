# Jurisynth natural-query direct chunk corroboration

This zero-NIM corroboration isolates the frozen production-v2 FAISS chunk retriever. It is not end-to-end legal QA and does not replace the 40-case controlled probe.

## Frozen source and scoring boundary

- Packet: `jurisynth\evaluation_artifacts\global_natural_candidate_packet.json` (version 1.1).
- Adjudicated eligible questions executed verbatim: **14**.
- Cases with document-qualified expected-chunk gold: **11**.
- Unscored table questions without chunk gold: **3**.
- The packet encodes one expected chunk per scored case and no explicit alternate-valid chunk IDs.
- Therefore, answer-bearing source-document recall is deliberately strict: only the designated expected chunk counts. A merely same-document chunk is reported separately.
- Queries were neither generated nor changed, and no alternate was inferred after retrieval.

## Natural-query metrics

| Metric | Result |
|---|---:|
| Exact expected-chunk recall | 0.636 |
| Strict answer-bearing source-document recall | 0.636 |
| Any-candidate correct-document recall | 0.727 |
| Alternate-valid recoveries | 0 |
| Recall@1 | 0.091 |
| Recall@3 | 0.091 |
| Recall@5 | 0.182 |
| Recall@10 | 0.636 |
| MRR | 0.1813 |
| Mean latency (all 14 queries) | 0.0430 s |
| Median latency | 0.0429 s |
| P95 latency | 0.0452 s |
| Worst latency | 0.0452 s |
| Peak RSS | 897.0 MB |

## Failure audit

- `expected_source_below_top_10_but_within_top_100`: 3
- `correct_document_retrieved_but_wrong_non_answer_bearing_chunk`: 1
- `gold_annotation_insufficient_for_chunk_scoring`: 3

## Side-by-side interpretation

### Controlled S/P chunk probe

- 40 cases
- exact Recall@10: 0.100
- MRR: 0.0615
- deterministic subject-predicate query style

### Natural-query corroboration

- 11 scored cases (14 executed)
- exact Recall@10: 0.636
- MRR: 0.1813
- frozen source-first natural questions

**Descriptive comparison:** Natural questions performed substantially better than the controlled subject-predicate probes.

**Interpretation:** The result supports a strong query-formulation effect, while still measuring imperfect chunk retrieval.

The datasets remain separate. This small corroboration set is not a new formal accuracy estimate, and no production tuning is justified from it.

Production code, thresholds, embeddings, ranking, chunking, gold annotations, and artifacts were not modified.
