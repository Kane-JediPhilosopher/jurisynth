# Jurisynth global KG audit — hand-off to Chat

**Date:** 15 September 2026  
**Purpose:** Independent review of the global KG's structural and semantic quality, particularly the difference between faithful extraction noise and true engineering defects.  
**Current work boundary:** This is a read-only audit. Do not infer authorization to change production code, the frozen extraction prompt, retrieval policy, or the Agentic Reasoner architecture from this hand-off.

## The answer in one paragraph

Jurisynth's global KG is a substantial, provenance-aware evidence store rather than a clean, globally resolved legal ontology. It contains many useful, faithful legal assertions. Its **semantic core consists of ordinary triples plus n-ary Assertion resources**: 5,374,731 chunk-scoped triples and 2,210,380 modifier-bearing Assertion resources. These are partly two representations of the *same* legal statements, so their counts must not be added as independent facts. Measure the modifier layer only after that: 2,645,088 Modifier resources/links and 2,646,145 modifier-value quads. The highest-confidence defect is source identifier normalization: **22,154 source documents actually represented in RDF share an RDF document identifier with at least one other source document**, across **4,917 shared document URIs**.

## Semantic core, then modifiers

### 1. Ordinary semantic triples

- **5,374,731** triples in **180,427** non-empty chunk named graphs.
- **951,515** distinct subjects, **565,123** distinct predicates, and **1,840,792** distinct objects.
- **4,690,458** URI objects (87.27%) and **684,273** literal objects (12.73%).
- Generated Jurisynth predicates occur in **4,775,994** triples (88.86%) and span **564,704** distinct predicates; CDM ontology predicates occur in **598,737** triples (11.14%) and span **419** predicates.

### 2. N-ary semantic Assertion resources

- **2,210,380** Assertion resources encode the subject, predicate, object, source chunk, and modifier links of modifier-bearing statements.
- This is **41.13%** relative to the ordinary-triple count, but **not** a clean fraction of *unique legal propositions*: RDF triples may deduplicate repeated extraction occurrences, while assertions are an overlapping second representation.
- Statements without modifiers remain ordinary triples with provenance through their chunk graph and have no separate Assertion resource.
- Assertion component values slightly exceed resource counts: subject **2,211,389**, predicate **2,211,377**, object **2,211,436**, versus **2,210,380** resources. Source-chunk values are exactly **2,210,380**. Some nominal Assertion resources are therefore multi-valued; identifier collisions are plausible but not yet proven to be the cause.

### 3. Modifier layer, measured separately

- **2,645,088** Modifier resources and **2,645,088** Assertion→Modifier links.
- **2,646,145** `source:value` quads, **1,057** more than Modifier-resource count.
- Average **1.197 modifiers per modifier-bearing Assertion**.
- Modifiers preserve extracted wording as opaque literals rather than typed legal conditions. This is loss-averse but limits structured modifier filtering. Do not count Modifier-resource quads as independent legal propositions.

### Physical storage, not semantic-fact count

The Oxigraph store has **27,007,011 quads**. It physically partitions into **5,374,731 chunk-graph quads**, **18,991,283 assertion-graph quads**, and **2,640,997 document-graph quads**. The assertion graph contains *both* n-ary semantic assertions and modifier/provenance encoding. It is incorrect to call the 19.90% chunk-graph share the complete semantic core, or the remaining 80.10% merely non-semantic metadata. It is also incorrect to call 27 million quads 27 million independent legal facts.

## Exact answer: how many documents share RDF identifiers?

The **directly observed RDF answer is 22,154 source documents**. A read-only query grouped stored `rdfs:label` values by RDF Document URI and found:

- **43,500** labelled source documents in the RDF graph;
- **26,263** RDF document URIs;
- **4,917** URIs with more than one distinct source-document label;
- **22,154** source-document labels attached to those shared URIs (**50.93%** of labelled source documents);
- largest sharing group: **28** source IDs.

The earlier sidecar-wide normalization audit produced a different, broader count: **22,281 of 43,694 indexed source document IDs (50.99%)** participate in collision groups, spread over **4,934** normalized keys. The sidecar includes source IDs that have no graph-bearing RDF document label, so **22,281 should not be used as the exact count of documents currently sharing identifiers in the stored RDF graph**.

The serializer normalizer removes the final dotted segment as if it were a file extension. Thus distinct source IDs such as `C_2012219EN.01000101` and `C_2012219EN.01000501` both become `c_2012219en`. It also affects chunk URIs: **78,243 of 251,532 source `(document, chunk)` pairs** occur in groups sharing a normalized graph URI (**31.11%**). This merges distinct source identities at the RDF resource level; it does *not* establish that their legal text is identical.

## Faithfulness versus noise

Bounded assertion-and-chunk inspection found strong, answer-bearing examples: definitions of collecting societies and financial market infrastructure, duties of a head of mission, and CN-code duty rates. These often preserve the legal clause better than a compact ontology relation would.

But the faithful form is structurally awkward:

- The validator deliberately turns complete objectless assertions into `(subject, full proposition as predicate, xsd:boolean true)`. **659,528** semantic triples have Boolean-true objects (**12.27%** of all ordinary triples; **96.38%** of literal-object triples). This avoids inventing objects but fragments the relation vocabulary.
- The community constructor only uses URI subjects and URI objects, so these Boolean propositions are excluded from current community topology.
- Of **2,461,266** entity labels, **846,942 (34.41%)** exceed 80 characters and **374,126 (15.20%)** exceed 150. Many retain legally relevant conditions but behave like clauses rather than reusable entities.
- Generated predicate vocabulary ranges from generic `is`/`are` (**188,672** triple occurrences combined) to entire clause-length predicates. This produces both coarse and over-specific matching problems.
- Actual sample noise includes fragmentary assertions and month names such as `May` parsed as objects. This does not justify judging every long triple as wrong.

## Topology and community findings

- Global discourse references are major hubs: `it` has **59,031** subject triples, `this regulation` **46,338**, `this decision` **33,416**, `there` **21,462**, and `this` **18,951**. Since those resources are not document-scoped, they can bridge unrelated instruments.
- Aliases remain split: `the commission` has **178,055** subject triples versus `commission` **151,189**; `member states` has **84,168** versus `the member states` **16,953**. The graph simultaneously over-merges document-relative references and under-merges common actors.
- The community entity graph has **2,461,266 vertices** and **3,842,904 distinct URI-to-URI edges**. Compared with 4,690,458 URI-object triple occurrences, at least **847,554 occurrences (18.07%)** are consolidated as repeated `(subject, predicate, object)` edges across chunks. Repetition can be legitimate; dedup loses occurrence frequency for topology.
- Level 0 has **317,270 communities**: **311,395** contain 2–5 members, but **85** exceed 1,000 members. The ten largest hold **943,130 entities (38.32%)**. Their stored anchors are dominated by numeric/punctuation/table fragments, not clearly coherent legal themes.
- Higher hierarchy levels barely compress the forest: **315,532 of 315,536** level-1 communities are single-child, and levels 2–3 are similarly almost all single-child. A Lazy Summarizer cannot make incoherent boundaries coherent by summarizing them.

## Corpus and evidence strengths

- **437/437** batches have RDF graphs and chunk indices; **370/437** have table indices and **225/437** have image indices.
- Chunk sidecar has **251,532 non-empty chunks**, mean **3,282.64** characters, maximum **6,501**. This bounded chunk layer is comparatively healthy.
- The corpus mixes OJ-L-like, numeric CELEX-like, OJ-C-like, merger-like, and other source IDs. Those are identifier heuristics, not authoritative document classifications. The mix raises instrument/date-coherence risk for a global retriever.
- Chunk graphs retain evidence locality and modifiers preserve extracted conditions. The correct operational stance is: **use triples/indices to find evidence, verify against the source chunk, cite the instrument, and mark cross-provision inferences explicitly**.

## Requested second opinion from Chat

Please review, **without prescribing production edits as already approved**:

1. Whether the two-part semantic-core framing and non-additivity of ordinary triples/Assertion resources are accurate.
2. Whether the directly stored RDF collision count (22,154) versus sidecar-wide count (22,281) is explained and denominated correctly.
3. Which observations are verified structural defects versus plausible retrieval impacts that still need labelled evaluation.
4. Whether the remediation priority should be: provenance identity first, discourse-hub control/instrument scoping second, then vocabulary/community improvements—while preserving faithful source wording.
5. What minimal assertion-quality strata would fairly test faithful-but-awkward propositions, modifier-bearing assertions, ordinary URI-to-URI triples, and table-derived fragments.

## Source artifacts

All files are local to `C:\Users\Roxas\OneDrive\Desktop\Project_Space\jurisynth\evaluation_artifacts\kg_audit_20260915`:

- `KG_EXPLORATION_REPORT.md` — full interpretation and recommendations.
- `structural_metrics.json` — exact store partitions, predicate/entity counts, Assertion components, Modifier links.
- `metadata_metrics_v2.json` — E–R, community, chunk, and modality statistics.
- `identifier_collisions.json` — sidecar-wide document/chunk URI-normalization collisions.
- `document_identifier_sharing.json` — **direct RDF count** of source documents sharing Document URIs.
- `assertion_samples.json` — bounded ordinary-triple/source-chunk qualitative sample.
- `corpus_id_distribution.json` — identifier-family and apparent-year distributions.
- `measure_document_identifier_sharing.py` and other adjacent scripts — read-only reproducibility code.

