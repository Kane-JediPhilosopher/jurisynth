# Jurisynth direct chunk retrieval evaluation

This is a zero-NIM, controlled component benchmark of the frozen production-v2 FAISS chunk layer. It is not end-to-end legal QA.

## Existing-asset inventory

- **chunk sidecars:** Authoritative production-v2 FAISS index plus SQLite metadata used for targets, retrieval, and presence checks.
- **complex smokes:** Broad multi-leaf end-to-end traces; unsuitable for isolated direct-chunk scoring.
- **development assertion 200:** Reusable controlled query/gold structure and exclusion set; not reused as chunk cases because it is development data.
- **diagnostic fixtures:** Small or development-exposed fixtures retained for tests only.
- **global natural packet:** 20 source-first questions, 14 adjudicated eligible; useful for later natural-query corroboration but too small/heterogeneous for the primary held-out set.
- **heldout assertion 100:** Reusable frozen schema and exclusion set; not rerun or modified.
- **stabilization gates:** Focused hand-picked regression checks; unsuitable as a representative held-out set.

## Construction and integrity

- Cases: **40**, frozen before retrieval.
- Generation: zero-NIM deterministic subject+predicate query from a semantic triple in the gold chunk.
- Sampling: one candidate per shuffled batch, then round-robin across document family, object type, and chunk-position strata.
- Excluded existing gold source pairs: **311**.
- Queries contain readable subject and predicate labels, never the source chunk or retrieved candidate list.
- Alternate-valid chunks were frozen conservatively from normalized duplicate source text before retrieval.

## Metrics

| Metric | Result |
|---|---:|
| Exact expected-chunk recall | 0.100 |
| Answer-bearing source-document recall | 0.100 |
| Correct-document candidate recall | 0.175 |
| Alternate-valid recoveries | 0 |
| Recall@1 | 0.050 |
| Recall@3 | 0.075 |
| Recall@5 | 0.075 |
| Recall@10 | 0.100 |
| MRR | 0.0615 |
| Mean latency | 0.1545 s |
| Median latency | 0.1042 s |
| P95 latency | 0.2676 s |
| Worst latency | 0.3040 s |
| Peak RSS | 900.9 MB |

## Retrieval outcomes

- `correct_document_wrong_chunk`: 3
- `miss`: 33
- `exact`: 4

## Failure audit

- `correct_document_retrieved_but_wrong_chunk`: 3
- `chunk_present_but_query_embedding_failed_to_rank_it`: 32
- `unrelated_high_similarity_chunks_outranked_source`: 1

## Interpretation boundary

Exact Recall@k and MRR score the designated document-qualified chunk. Source-document recall accepts only that chunk or a pre-frozen duplicate-text alternate from the same document. A merely topically related chunk from the correct document is reported separately and is not counted as answer-bearing.

## Findings

- All 40 expected chunks were present in the production index; no corpus/index-presence or metadata-source defect was observed.
- The dominant limitation is semantic ranking: 32 targets did not enter even the diagnostic top 100 for their controlled subject+predicate query.
- Three correct-document/wrong-chunk outcomes show that document-level topical similarity occasionally works while chunk-level discrimination fails.
- One target appeared between ranks 11 and 100, where unrelated higher-similarity chunks displaced it from the production top 10.
- No result identifies a deterministic implementation bug. The low recall should be treated as a measured retrieval limitation and investigated later using development data only.
- Some controlled queries contain generic legal subjects such as “this regulation” or “the annex”. They remain frozen and scored, but this benchmark must not be presented as natural-language legal QA.
- Production retrieval code and artifacts were not modified by this evaluation.
