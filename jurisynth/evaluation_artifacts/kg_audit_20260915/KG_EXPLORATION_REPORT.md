# Jurisynth Global Knowledge Graph Exploration

**Audit date:** 15 September 2026  
**Scope:** Global KG, provenance layer, E–R sidecars, community graph, chunk corpus, and aggregate artifact coverage  
**Mode:** Read-only structural and qualitative audit; no extraction, retrieval, or production behavior was changed

## Executive assessment

The global KG is useful, but it should currently be understood as a **large provenance-aware evidence store**, not as a clean, globally unified legal ontology.

Many sampled assertions are faithful and answer-bearing. The graph preserves the originating chunks, document links, statement modifiers, and ordinary RDF triples. The main problems are uneven rather than universal:

1. **A serializer identifier collision is merging distinct source documents and chunks.** This is a concrete provenance defect, not subjective annotation noise.
2. **The graph simultaneously over-merges and under-merges concepts.** Generic discourse entities such as `it`, `this regulation`, and `there` become global hubs, while obvious aliases such as `commission` and `the commission` remain separate.
3. **Faithfulness produces very long entity and predicate labels.** These often retain legally important wording, but weaken entity matching, relation matching, graph traversal, and community quality.
4. **Objectless propositions are represented as predicates with a Boolean `true` object.** This is intentional and loss-averse, but it makes 12.27% of all semantic triples invisible to the current URI-to-URI community graph.
5. **The community hierarchy provides little global compression.** A few giant, noisy communities coexist with hundreds of thousands of tiny components; higher levels are mostly one-child chains.

The KG is therefore salvageable without discarding the extraction work. The strongest immediate interpretation is: **source chunks remain the authoritative evidence; extracted triples are retrieval signals; community structure is auxiliary and must not be treated as a reliable topical taxonomy yet.**

## 1. What was inspected

The audit used the global Oxigraph store and its matching source artifacts:

- Oxigraph quads: **27,007,011**
- Source N-Quads size: **5,485,475,927 bytes**
- Oxigraph store size at build time: **9,529,609,003 bytes**
- Source fingerprint: `070eb02b6af2b21a75530dbc735a49f58dd932891342ad6b392893534d53a780`
- Source batches: **437**
- Chunk sidecar records: **251,532 chunks from 43,694 source document IDs**
- Community entity graph: **2,461,266 vertices and 3,842,904 unique URI-to-URI edges**
- E–R records: **2,461,266 entities and 358,503 relations**

The audit combined whole-store counts, SQLite sidecar analysis, deterministic reproduction of serializer identifier normalization, community-size analysis, and a bounded qualitative assertion sample. It did not attempt a complete expert adjudication of every assertion.

## 2. Physical graph structure

The 27.0 million quads are not 27.0 million independent legal facts. The **semantic core has two representations**: 5,374,731 ordinary semantic triples in chunk named graphs and 2,210,380 n-ary Assertion resources in the global assertion graph. The latter preserve statement-specific components and provenance for modifier-bearing assertions; they overlap ordinary triples and must not be added as independent facts.

| Partition | Quads | Share | Purpose |
|---|---:|---:|---|
| Chunk named graphs | 5,374,731 | 19.90% | Ordinary extracted semantic triples |
| Global assertion graph | 18,991,283 | 70.32% | N-ary semantic assertions, provenance links, and modifiers |
| Document named graphs | 2,640,997 | 9.78% | Document–chunk–assertion provenance |

This is a defensible provenance-oriented design. **The 19.90% chunk-triple share is not the full semantic-core share**, because n-ary assertions also encode semantics. Physical quads cannot cleanly be divided into "semantic" versus "metadata" by graph partition alone. The ordinary semantic-triple layer contains:

- **5,374,731** chunk-scoped triples
- **951,515** distinct subjects
- **565,123** distinct predicates
- **1,840,792** distinct objects
- **180,427** non-empty chunk named graphs

Each semantic triple lives in a chunk graph. Only assertions with extracted modifiers receive an additional n-ary assertion resource. There are:

- **2,210,380** modifier-bearing assertion resources
- The Assertion-resource count is **41.13%** of the ordinary-triple count; this ratio is **not** exact unique-proposition coverage because the two representations overlap and RDF triples can deduplicate occurrences

The remaining semantic triples still have chunk-level provenance through their named graph, but not an assertion resource of their own.

**Modifiers, counted after the semantic core:** 2,645,088 Modifier resources and 2,645,088 Assertion→Modifier links are stored, averaging 1.197 modifiers per modifier-bearing Assertion. Their `source:value` predicate has 2,646,145 quads, an excess of 1,057 values over Modifier-resource count. Modifier values are kept as opaque literals, which preserves them but limits structured modifier-aware filtering. As with the assertion-component excess discussed below, the exact affected resources and cause of the extra values require direct resource-level inspection.

## 3. What “faithful but noisy” looks like

The sample supports the user's expectation: much of the noise arises from preserving legal wording and document structure rather than inventing unsupported claims.

### Strong or useful patterns

Examples include:

- `collecting societies — are — bodies created by copyright law ...`
- `financial market infrastructure — means — a CCP ... or a CSD ...`
- `the head of mission — shall ensure — the protection of EU classified information ...`
- `CN code 2205 90 90 — has duty rate — 0.9 % vol/hl`

These are semantically useful and retain enough wording to lead a retriever back to the governing chunk.

### Faithful but structurally awkward patterns

When the extractor emits an assertion without an object, the validator deliberately treats a sufficiently complete predicate as a proposition and assigns typed Boolean `true`. This accounts for:

- **659,528 Boolean-true objects**
- **12.27% of all semantic triples**
- **96.38% of literal-object triples**

A clause such as “frogs' legs must be washed immediately with running potable water” can therefore become conceptually:

`frogs' legs — must be washed immediately with running potable water — true`

This representation is faithful and avoids fabricating an object, but it moves most of the proposition into the predicate. It creates a large number of unique relations and is excluded from the current community graph, which only admits URI subjects and URI objects.

### Clear extraction or parsing noise

The bounded sample also contains fragmentary assertions, for example:

- `ethanol price — is — only a resultant`
- month names such as `May` parsed as the object of `is` or `shall be`
- incomplete subjects such as `this` or objects such as `exceptions`
- table-derived numeric and punctuation fragments detached from their headings

These are genuine quality issues, but the sample does **not** support the conclusion that the whole graph is unusable. It supports treating triples as candidates whose source chunks must be checked.

## 4. Vocabulary quality and fragmentation

### Entities

There are **2,461,266** entity records. Their labels are unusually long:

- Mean length: **85.98 characters**
- Over 80 characters: **846,942 (34.41%)**
- Over 150 characters: **374,126 (15.20%)**
- Over 500 characters: **24,431 (0.993%)**
- Over 25 words: **343,112 (13.94%)**
- Start with `the`: **628,780 (25.55%)**
- Start with a demonstrative or pronoun: **123,087 (5.00%)**
- Contain a digit: **646,884 (26.28%)**

Long labels are not automatically wrong: many encode conditions that would otherwise be lost. They nevertheless blur the boundary between an entity and a clause, weaken exact entity matching, and inflate the FAISS candidate space.

### Relations

The semantic graph contains **565,123 distinct predicates**, of which:

- **564,704** are generated Jurisynth-data predicates
- only **419** are CDM ontology predicates

By occurrence, generated predicates account for **4,775,994 triples (88.86%)**, while CDM predicates account for **598,737 (11.14%)**.

The E–R relation sidecar contains **358,503 relation records**, 206,620 fewer than the semantic predicate count. This difference is consistent with the community/E–R construction path excluding literal-object assertions, especially Boolean propositions.

High-frequency generated relations include `is`, `means`, `are`, `has duty rate`, `classified under`, and several `shall ...` forms. `is` and `are` alone account for **188,672 triples (3.51%)**. At the other extreme, thousands of relations are clause-length strings. The KG therefore has two simultaneous relation problems:

- **coarse predicates** that carry little discriminative meaning; and
- **over-specific predicates** that preserve a full clause but rarely match another expression.

## 5. Entity resolution: over-merging and under-merging

The most connected subjects include:

- `the commission`: **178,055** triples
- `commission`: **151,189**
- `member states`: **84,168**
- `it`: **59,031**
- `this regulation`: **46,338**
- `this decision`: **33,416**
- `there`: **21,462**
- `this`: **18,951**
- `they`: **18,754**
- `the member states`: **16,953**

This shows both failure directions:

1. **Over-merging:** document-relative expressions such as `it`, `this regulation`, `this decision`, `this chapter`, and `there` become global resources shared across unrelated instruments. Traversal through these nodes can manufacture short paths between unrelated provisions.
2. **Under-merging:** variants such as `commission`/`the commission`, `member states`/`the member states`, and `parties`/`the parties` remain distinct despite likely coreference in many contexts.

This is a likely contributor to both poor multi-hop precision and giant communities. It also means shortest-path-style relevance is unsafe unless generic hubs are penalized or made document-scoped.

## 6. Provenance identity collision — high-priority defect

The serializer's identifier normalizer removes everything after the final period as though it were a file extension. For identifiers such as:

- `C_2012219EN.01000101`
- `C_2012219EN.01000501`
- `C_2012219EN.01000901`

this produces the same normalized identifier: `c_2012219en`.

Measured over the chunk sidecar:

| Measure | Result |
|---|---:|
| Source document IDs | 43,694 |
| Distinct normalized document IDs | 26,347 |
| Colliding normalized document keys | 4,934 |
| Source documents in collision groups | 22,281 (50.99%) |
| Largest document collision group | 28 source IDs |
| Source `(document, chunk)` pairs | 251,532 |
| Distinct normalized chunk graph URIs | 197,658 |
| Colliding chunk graph URIs | 24,369 |
| Source chunk pairs in collision groups | 78,243 (31.11%) |
| Largest chunk collision group | 28 source pairs |

This does not mean half the documents have identical text. It means distinct source IDs can resolve to the same RDF document resource, and chunks with the same local chunk number can resolve to the same named graph. Their triples and provenance links are consequently merged at the RDF identifier level.

The stored RDF graph gives the stricter, directly observed figure: **22,154 source documents represented by labels share an RDF document URI**, across **4,917 shared RDF document URIs**. The store contains **26,263 Document resources and 43,500 source-document labels**; the largest shared URI has 28 labels. Thus 22,154/43,500 labelled source documents (50.93%) share an RDF identifier. The 22,281 figure above is the broader chunk-sidecar population, not the exact graph-bearing count. The difference reflects source IDs in the sidecar that are not represented by document labels in the RDF graph. Assertion component counts also exceed assertion-resource counts by 997–1,056 for subject, predicate, and object, indicating a small population of nominal assertion resources with multiple component values. Identifier collision is a plausible cause, though that causal link needs a direct resource-level query before it is stated as proven.

This finding is more serious than ordinary extraction noise because it compromises provenance identity. It should be resolved before using document-level precision, exact provenance validity, or cross-document traversal as thesis claims. It does **not** require assuming that extraction itself failed.

## 7. Literal objects and community-graph coverage

Semantic object types are:

- URI objects: **4,690,458 (87.27%)**
- Literal objects: **684,273 (12.73%)**

The community constructor intentionally only adds triples whose subject and object are both URIs. Consequently, the Boolean proposition pattern—along with the smaller population of other literals—is absent from community construction.

The community graph has **3,842,904 unique URI-to-URI edges**, compared with 4,690,458 URI-object triple occurrences in chunk graphs. At least **847,554 occurrences (18.07%)** were consolidated because the same `(subject, predicate, object)` appeared across chunks. Such repetition is not inherently bad; it can represent repeated provisions, amendments, or parallel instruments. However, it means community topology discards occurrence-level provenance and should not be interpreted as evidence frequency without a separate count.

## 8. Community graph assessment

The base community level contains **317,270 communities** for 2,461,266 entities:

| Level-0 size | Communities |
|---|---:|
| 1 member | 549 |
| 2–5 members | 311,395 |
| 6–20 members | 5,065 |
| 21–100 members | 164 |
| 101–1,000 members | 12 |
| Over 1,000 members | 85 |

This is highly polarized: **98.15%** of level-0 communities contain two to five members, while 85 communities are larger than 1,000. The ten largest level-0 communities contain **943,130 entities, or 38.32% of all entity records**. Their six stored anchor labels are dominated by dashes, numerical fragments, percentages, table cells, and long list fragments rather than coherent legal subjects.

The higher hierarchy barely consolidates this forest:

- Level 1: **315,536 communities**, of which 315,532 are single-child
- Level 2: **315,533 communities**, of which 315,532 are single-child
- Level 3: **315,533 communities**, all single-child/root records

The hierarchy is structurally valid as a forest, but globally it supplies little compression. Four levels mostly encode one-child chains over approximately 315,000 disconnected components.

Practical conclusion: the Lazy Community Summarizer may still help for a well-targeted local community, but it cannot repair weak community boundaries. The present global community hierarchy should be used as an auxiliary orientation/diversity signal, not as a trusted topical map or mandatory route to evidence.

## 9. Corpus and modality coverage

Chunking itself is comparatively healthy:

- **251,532 chunks**
- Mean length: **3,282.64 characters**
- Maximum length: **6,501 characters**
- Empty chunks: **0**
- Chunks over 10,000 characters: **0**

All 437 batches have both RDF graph output and chunk indices. Modality coverage is partial by source availability:

- Table indices: **370/437 batches (84.67%)**
- Image indices: **225/437 batches (51.49%)**

Document-ID families suggest a heterogeneous corpus:

- OJ-L-like IDs: **27,885 documents (63.82%)**
- numeric CELEX-like IDs: **12,826 (29.35%)**
- OJ-C-like IDs: **1,919 (4.39%)**
- merger-case-like IDs: **592 (1.35%)**
- other/JOL-like IDs: **472**

These are identifier heuristics, not authoritative legal-document classifications. They nevertheless show that the corpus mixes legislation with decisions, notices, merger material, classifications, and highly tabular instruments. A single undifferentiated candidate pool will naturally retrieve semantically similar but legally inapplicable material unless instrument, date, and document-type constraints are preserved.

## 10. Implications for observed retrieval behavior

The audit supplies plausible upstream explanations for several failures already observed in global smokes:

1. **Wrong but semantically similar instruments:** heterogeneous document types and weak instrument/date scoping allow equivalent wording from another regime to rank highly.
2. **Wrong country or actor dominates:** high-degree shared predicates/objects and global actor/discourse hubs can overwhelm the requested subject.
3. **Multi-hop drift:** generic nodes such as `it`, `this regulation`, `commission`, and numerical fragments create cheap but legally incoherent paths.
4. **Communities do not rescue retrieval:** many communities are either tiny fragments or giant noisy aggregates; higher levels add little compression.
5. **Relevant proposition missing from community search:** Boolean-object assertions are not present in the URI-only community graph.
6. **Provenance ambiguity:** identifier collisions can make distinct source pages/documents appear to share an RDF document or chunk resource.

These findings do not prove that every retrieval failure originates in the KG. Candidate generation, scoring, query interpretation, and top-k policy remain independent failure points. They show that calibrating retrieval alone cannot fully compensate for global hub and identity problems.

## 11. Strengths worth preserving

- The source chunks are bounded, non-empty, and available for every batch.
- Named chunk graphs retain evidence locality better than a flat triple store would.
- The original legal wording is often preserved instead of normalized into unsupported abstractions.
- The graph retains modifiers rather than silently dropping them.
- CDM relations coexist with open-vocabulary relations, supporting both known-schema and long-tail facts.
- Repeated rules across instruments can be surfaced even when a designated gold source is not retrieved.
- The Oxigraph representation makes a 27-million-quad audit feasible without loading the whole RDF graph into Python objects.

## 12. Recommended priority order

These are recommendations only; this audit did not implement them.

### Priority 0 — measurement integrity

1. Correct or version the document/chunk/assertion URI construction so periods inside source IDs are not treated as file extensions.
2. Rebuild the affected RDF/provenance and derived community artifacts from retained pipeline outputs, if possible without new LLM extraction.
3. Add invariants: one source document ID per document URI, one `(document ID, chunk ID)` per chunk URI, and one subject/predicate/object tuple per assertion resource.

### Priority 1 — protect retrieval from topology noise

4. Scope demonstratives and pronouns to their source document/chunk, or exclude/penalize them as traversal hubs.
5. Preserve exact source/instrument/date constraints through candidate generation and reranking.
6. Treat chunk evidence as authoritative and graph paths as supporting signals, especially for multi-hop answers.
7. Keep community evidence optional until community coherence is measured on a labelled sample.

### Priority 2 — improve semantic usability without discarding faithfulness

8. Retain full extracted wording, but add separate compact aliases or descriptors for retrieval; do not overwrite the faithful form.
9. Represent objectless propositions in a way that remains searchable by the community/relation path, or explicitly index them as proposition text.
10. Introduce document-aware aliasing for obvious variants while avoiding unsafe global coreference.
11. Parse modifiers into typed fields only where evaluation shows value; preserve the opaque original alongside them.

### Priority 3 — evaluate rather than assume

12. Stratify assertion evaluation by ordinary triple, Boolean proposition, table-derived assertion, CDM relation, long-label entity, and modifier-bearing assertion.
13. Evaluate retrieval separately on exact-source recall, alternate-answer-bearing recall, instrument/date coherence, provenance validity, and ranking.
14. Sample communities by size bucket; do not infer quality from the largest communities alone.

## 13. Overall conclusion

Jurisynth's global KG is **not a failed extraction artifact**. It contains millions of traceable, often useful legal propositions and a strong chunk evidence layer. The extraction's faithfulness bias explains some awkward triples, but not all observed problems.

The decisive distinction is:

- **faithful representation noise:** long clauses, Boolean propositions, open-vocabulary relations, and legal wording retained verbatim;
- **resolvable engineering defects:** identifier collisions and multi-valued nominal assertion resources;
- **semantic modelling limitations:** global discourse hubs, unresolved aliases, numeric/table fragments, and weak community compression.

That distinction is encouraging because it points to targeted repairs and safer retrieval policy rather than a wholesale re-extraction. Until those repairs are evaluated, the soundest operational framing is: **retrieve with the graph, verify with the chunk, cite the source, and express uncertainty when graph structure alone supplies the connection.**

## Reproducibility artifacts

The audit inputs, scripts, and raw results are stored beside this report:

- `structural_metrics.json` — whole-store structural counts and top resources
- `metadata_metrics_v2.json` — E–R, community, chunk, and modality statistics
- `identifier_collisions.json` — reproduced URI normalization collisions
- `document_identifier_sharing.json` — directly measured RDF document-URI sharing among stored labels
- `corpus_id_distribution.json` — identifier-family and apparent-year distributions
- `assertion_samples.json` — bounded assertion-and-chunk sample
- `run_structural_queries.py`, `run_metadata_audit.py`, `analyze_identifier_collisions.py`, `analyze_corpus_ids.py`, and `sample_assertions.py` — read-only audit scripts
- `measure_document_identifier_sharing.py` — read-only exact RDF document-URI sharing query
