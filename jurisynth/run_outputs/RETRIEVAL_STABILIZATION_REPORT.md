# Retrieval stabilization report

Date: 2026-09-17

## Outcome

The deterministic metadata, scope-ranking, retrieval-status safety rule, and
two-pass table merge are implemented. Four of the five focused gates pass. The
architecture is **not frozen yet** because the positive cross-instrument case
retrieved the AI Act source but missed the IVDR source.

No Community Graph, Leiden, hierarchy, or summarizer artifact was changed.

## Metadata sidecar

- Source records: 43,694
- Records with a title or canonical identity: 43,101
- CELEX records: 12,835
- ELI records: 5,123
- Records with a primary title: 43,034
- Persisted aliases: 93,656
- Location: `jurisynth/global_artifacts_source_uri_v2/document_metadata.sqlite`
- `document_id` is used only as a lookup key; filename identity inference is
  not used.

## Focused cases

- `q003` AI Act: **pass**; status `success`; 22.672 s; 33 evidence items
  (`14 in_scope`, `19 cross_instrument`, `0 unknown`); expected source coverage
  `1/1`. The five table hits were all cross-instrument and did not determine
  success. Table counts were Pass 1 `5`, Pass 2 `0`, merged/reranked `5`.
- Simple AI Act leaf: **pass**; status `success`; 8.032 s; 14 evidence items
  (`14 in_scope`, `0 cross_instrument`, `0 unknown`); expected source coverage
  `1/1`. Table counts were `5 / 0 / 5`.
- AI Act + IVDR leaf: **fail**; status currently `success`; 85.785 s; 12
  evidence items (`5 in_scope`, `7 cross_instrument`, `0 unknown`); expected
  source coverage `1/2`. The AI Act source survived, but the IVDR source was
  absent from the candidate set. Scope reranking did not remove it; candidate
  generation never supplied it. Table counts were `5 / 5 / 5`.
- Known table-primary case: **pass**; status `success`; 7.514 s; expected source
  coverage `1/1`. Rows 0, 1, and 2 of `table_10` survived the merged pool.
  Table counts were `5 / 5 / 5`.
- Non-table GDPR control: **pass as a safety control**; status `weak`; 7.219 s;
  no in-scope evidence and no false success from unrelated high-similarity
  evidence. This also records a genuine GDPR recall miss for later quality
  evaluation. Table counts were `5 / 5 / 5`.

The full machine-readable result is in
`jurisynth/run_outputs/retrieval_stabilization_validation.json`.

## Automated checks

- Focused regression suite: 33 passed, 1 skipped.
- Scope/mechanism rerun after the final ambiguity correction: 18 passed.
- Ambiguous title-only records are classified `unknown`, not guessed as a
  different instrument.

## Remaining gate

The only stabilization blocker is cross-instrument candidate recall. Fixing it
would require an owner-approved, bounded retrieval change (for example, an
explicit-instrument source-scoped candidate pass). It was not added silently in
this pass.
