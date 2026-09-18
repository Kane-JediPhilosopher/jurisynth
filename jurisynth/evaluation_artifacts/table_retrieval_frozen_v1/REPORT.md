# Jurisynth table retrieval component evaluation

This is a zero-NIM evaluation of the frozen production-v2 table and row FAISS layer. It is not end-to-end legal QA and is not a fresh held-out set.

## Existing-asset inventory

- **batch 0009 natural table packet:** Twenty already-frozen source-first row questions; seventeen unique targets remain after adjudicated-target overlap removal.
- **complex smokes:** Returned table candidates but lack clean standalone table gold; not used.
- **existing table fixtures:** Useful for evaluator tests only; not included as benchmark cases.
- **global natural packet:** Three table-primary cases were later AI-adjudicated with exact document/table/row gold.
- **global table store:** Authoritative production-v2 table store plus table and per-table row FAISS indices.
- **stabilization table primary:** Reuses the fisheries table target; retained as diagnostic evidence, not a duplicate case.

## Construction and integrity

- Frozen cases: **20**.
- AI-adjudicated natural anchors: **3**.
- Other pre-existing frozen source-first cases: **17**.
- No query was generated or rewritten for this evaluation.
- Gold rows were copied from the authoritative production-v2 table store before retrieval.
- No alternate-valid rows/tables were encoded, and none were inferred after retrieval.

## Metrics

| Metric | Result |
|---|---:|
| Table Recall@1 / @3 / @5 / @10 | 0.150 / 0.250 / 0.250 / 0.300 |
| Row Recall@1 / @3 / @5 / @10 | 0.100 / 0.250 / 0.250 / 0.300 |
| Table MRR | 0.2000 |
| Row MRR | 0.1667 |
| Correct-document recall@10 | 0.300 |
| Answer-bearing row case recall@10 | 0.300 |
| Answer-bearing row micro recall@10 | 0.364 |
| Alternate-valid recoveries | 0 |
| Mean / median latency | 0.0728 / 0.0711 s |
| P95 / worst latency | 0.0936 / 0.1142 s |
| Peak RSS | 1834.7 MB |

## Failure audit

- `answer_bearing_row_below_top_10_but_within_top_100`: 2
- `answer_bearing_table_and_row_below_top_100`: 12

## Interpretation boundary

Table Recall@k follows the production table-level FAISS order. Row Recall@k requires every frozen answer-bearing row for a case to survive the production combined table×row scoring order by rank k. Correct-document recall does not imply an answer-bearing table or row.

Expected tables absent from the production index: **0**. Expected rows absent from the authoritative store: **0**.

## Findings

- Every designated table and row exists in the production-v2 artifacts; this evaluation found no deterministic store/index-presence defect.
- The dominant limitation is first-stage table ranking: most missed target tables remain outside the diagnostic top 100.
- Two additional answer-bearing rows become reachable only when the table candidate search is widened diagnostically to 100.
- The 17 reused source-first questions use a generic identifier-based wording. Results should therefore be presented as a frozen component benchmark, not a fresh held-out estimate of arbitrary natural legal-table QA.

Production retrieval code, table artifacts, thresholds, serialization, scoping, and ranking were not modified.
