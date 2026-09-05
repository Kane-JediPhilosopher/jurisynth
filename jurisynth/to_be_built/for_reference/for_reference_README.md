# Jurisynth Retrieval Mech — Reference Modules Guide

This folder contains existing Jurisynth modules and artifacts that the Retrieval Mech should **reuse or integrate with where appropriate**, without conflating components that belong to different pipeline stages.

## Important matcher distinction

Two different matcher concepts exist in Jurisynth:

### Semantic Matcher — KG Construction Pipeline

The existing **Semantic Matcher** belongs to the KG Construction Pipeline.

Its purpose is to map extracted KG components against schema/ontology resources during graph construction.

Do **not** treat this module as the Retrieval Mech's E-R Matcher.

### E-R Matcher — Retrieval Mech

The **E-R Matcher** is a new Retrieval Mech component.

Its role is query-time retrieval:

```text
Query Interpreter
    ↓
entity/relation concepts + limited variants
    ↓
E-R Matcher
    ↓
FAISS search over persisted KG entity/relation indices
    ↓
matched RDF entity/relation candidates + scores
```

The two matchers may reuse similar embedding/FAISS techniques or helper code, but they have **different purposes, interfaces, outputs, and lifecycle**. Codex should keep them logically separate and should not rename or repurpose the KG Semantic Matcher as the Retrieval E-R Matcher unless explicitly instructed.

---

## Table artifacts from `doc_preprocessor.py`

### Persisted table JSON

Each extracted semantic OJ table is stored as:

```text
<table_store>/<doc_id>_<table_id>.json
```

Persisted schema:

```json
{
  "doc_id": "...",
  "table_id": "table_1",
  "context": "...",
  "description": "...",
  "header": ["Column A", "Column B"],
  "data": [
    ["row1-col1", "row1-col2"],
    ["row2-col1", "row2-col2"]
  ]
}
```

Notes:
- `header` may be `null`.
- `data` is a list of rows; each row is a list of cell strings.
- `description` is built deterministically from available table title/header information, a few informative rows, and surrounding context.
- The persisted JSON file is the source of truth for exact structured table content.
- The in-memory extraction object may contain nesting fields such as `parent_table_id`, `parent_row`, `parent_cell`, and `children`, but these fields are **not currently persisted by `store_table()`**.

---

## Existing hierarchical table retrieval

`doc_preprocessor.py` already implements table retrieval as:

```text
query
  ↓
table-level FAISS
  ↓
top-k candidate tables
  ↓
row-level FAISS inside those tables
  ↓
ranked row hits
  ↓
resolve exact row from persisted JSON
```

### Table-level retrieval text

Built primarily from:

```text
description + context + header
```

One vector is stored per semantic table.

### Row-level retrieval text

Rows are made self-describing by prefixing cell values with headers when available, e.g.:

```text
Country: France | Code: FR | Value: 42
```

One row FAISS index is maintained per indexed table.

### Retrieval hit metadata

`search_table_rows()` returns ranked row hits containing at least:

```text
doc_id
table_id
row_id
type = "row"
row_score
table_score
combined_score
```

Current combination:

```text
combined_score = table_score * row_score
```

The same query embedding is reused at table and row level.

### Exact row reconstruction

`get_retrieved_row()` / `load_table_json()` resolve a hit back to:

```text
{
    "table": <full persisted table JSON>,
    "row_id": <int>,
    "row": <exact row list>
}
```

For the Retrieval Mech, normalize this into `TableEvidence` rather than returning the whole table by default.

Suggested shape:

```text
TableEvidence
├── table_id
├── document_id
├── headers
├── matched_rows / matched_cells
├── table_score
├── row_score
└── combined_score
```

Return only the relevant rows/cells plus enough source/header metadata to interpret them.

---

## Persisted table-retrieval artifacts

Per preprocessing batch:

```text
<batch_result_dir>/table_index/
├── table.index
├── table_metadata.json
├── row_metadata.json
└── rows/
    └── <doc_id>__<table_id>.index
```

Exact table JSON lives under:

```text
<batch_result_dir>/table_store/
```

The Retrieval Mech should load/reuse these artifacts rather than rebuild table embeddings at query time.

---

## Retrieval Mech table integration

For one `RetrievalRequest`:

- use the raw `leaf_query` directly for table retrieval;
- perform table-level search first;
- search rows only inside candidate tables;
- resolve hits against persisted JSON;
- return matched structured rows/cells in `EvidenceBundle.table_evidence`;
- treat table evidence as auxiliary unless the information need is specifically table-centric.

---

## General integration principles

Codex should:

- reuse existing IDs, persisted indices, metadata mappings, and provenance conventions;
- avoid rebuilding artifacts already produced by preprocessing/KG construction;
- keep KG-construction components separate from Retrieval Mech components;
- use small loader/adapter helpers where existing artifact formats need adaptation;
- avoid silently changing existing schemas or module semantics.

In particular, **do not confuse the KG Semantic Matcher with the Retrieval Mech E-R Matcher**.
