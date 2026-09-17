# Source-first natural-query candidate pool — Batch 0009

## Selection rules

Build the 20-case formative set from separate source documents before writing a
question. Each candidate must retain its source document, expected chunk(s),
one quoted source excerpt, category, and a plain-language question written
without copying an RDF triple or whole table row into the question.

Exclude the legacy `fallback_50` assertion fixture from category sampling: it
is dominated by national-allocation-table material from one document.

## Already source-reviewed candidates

- `natural_001` — `L_2011065EN.01000101`, `chunk_6`: organisers' handling of
  citizens' initiative personal data. Candidate category: obligations.
- `natural_002` — `L_2011065EN.01000101`, `chunk_6`: use of support data for
  unrelated purposes. Candidate category: prohibition/scope.
- `natural_003` — `L_2018268EN.01005301`, `chunk_3`: European Vehicle Register
  data-management functions. Candidate category: definitions/scope.

## Table candidate pool

The following existing natural table probes are candidates for the three table
slots, subject to source inspection. Prefer three different documents and
human-readable row keys:

- `table_row_00001` — `C_2022160EN.01002701`, Installation ID BE000000000000158.
- `table_row_00002` — `C_2022236EN.01000501`, Installation ID IE000000000000027.
- `table_row_00009` — `L_2007342EN.01000101`, fisheries hygiene indicators.
- `table_row_00012` — `L_2010041EN.01000801`, fleet-segment/metier row.
- `table_row_00016` — `L_2011065EN.01000101`, Member State table row.

## Remaining candidate quotas

- obligations/prohibitions: 2 more candidates
- definitions/scope: 3 more candidates
- procedures/deadlines: 4 candidates
- cross-document/dependent reasoning: 6 candidates
- tables: select 3 from the pool above

## Construction method

1. Search Batch-0009 chunks for explicit legal modality (`shall`, `must`,
   `may not`), definition language (`means`, `for the purposes`), and procedural
   anchors (`within`, `submit`, `notify`, article/annex references).
2. Select one primary source excerpt per candidate; use a second document only
   where the question genuinely requires it.
3. Write a natural research question from the source meaning, then manually
   verify the expected document/chunk before running retrieval.
4. Record unavailable categories as a corpus limitation rather than filling
   them with synthetic RDF relation questions.
