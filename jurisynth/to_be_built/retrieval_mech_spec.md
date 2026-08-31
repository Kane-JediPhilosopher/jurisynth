# Jurisynth Retrieval Mechanism — V1 Specification

## 1. Purpose

Implement the Retrieval Mechanism as a single callable tool:

```python
retrieve_evidence(request: RetrievalRequest) -> EvidenceBundle
```

Each call handles exactly one AST leaf query from the Agentic Reasoner.

The Retrieval Mech owns all retrieval-specific logic internally. The Agentic Reasoner should not generate keywords, synonyms, RDF URIs, SPARQL, community IDs, retries, or fallback strategies.

---

# 2. Architectural boundaries — LOCKED

The Agentic Reasoner:

- decides when a leaf is dependency-ready;
- passes one `RetrievalRequest`;
- owns cross-leaf scheduling/concurrency;
- receives one `EvidenceBundle`;
- maps the result back through `query_id`.

The Retrieval Mech:

- interprets the retrieval request;
- performs controlled semantic expansion;
- performs FAISS retrieval;
- identifies/prioritizes communities;
- builds deterministic SPARQL;
- retrieves chunks/tables;
- performs internal fallback/escalation;
- generates one community summary;
- normalizes/ranks evidence;
- returns the final bundle.

Do **not** expose retrieval internals to the Reasoner during normal execution.

---

# 3. Input contract — LOCKED

```text
RetrievalRequest
├── query_id
├── leaf_query
├── contextual_facts
├── constraints?
├── dependency_claims?
└── retrieval_config?
```

### Fields

`query_id`
- Stable AST/node identifier.

`leaf_query`
- Main information need.
- Also used directly for chunk FAISS retrieval.

`contextual_facts`
- Relevant facts from the user/query that guide retrieval.

`constraints`
- Optional jurisdictional, temporal, document, scope, etc. restrictions.

`dependency_claims`
- Relevant prerequisite Claims only.
- Do not pass entire upstream evidence bundles.

`retrieval_config`
- Optional overrides.
- Defaults should normally be system-owned.

---

# 4. High-level pipeline — LOCKED

```text
RetrievalRequest
        │
        ├──────────────→ Chunk FAISS Matcher
        │
        ▼
Query Interpreter LLM
        │
        ▼
entity/relation concepts + controlled variants
        │
        ▼
E-R Matcher / FAISS
        │
        ▼
Community Selector
        │
        ▼
bounded community-aware candidate expansion
        │
        ▼
SPARQL retrieval
   ├── direct/neighborhood
   └── bounded path
        │
        ▼
merge + normalize evidence
        │
        ├──────────────→ Table retrieval
        │
        ▼
quality evaluation
        │
        ├── if insufficient → internal escalation
        │
        ▼
Lazy Community Summarizer
        │
        ▼
EvidenceBundle
```

Direct/neighborhood and bounded-path SPARQL retrieval may run concurrently.

Conjunctive retrieval is fallback-only.

---

# 5. Query Interpreter — LOCKED

This is an internal LLM step.

Its purpose is query interpretation / controlled semantic expansion, not general reasoning.

Suggested output:

```text
QueryInterpretation
├── entity_concepts[]
├── relation_concepts[]
└── constraints[]
```

Preserve concept grouping.

Example:

```json
{
  "entity_concepts": [
    {
      "concept": "data controller",
      "variants": ["controller"]
    }
  ],
  "relation_concepts": [
    {
      "concept": "required to provide",
      "variants": ["must provide", "obliged to provide"]
    }
  ]
}
```

Rules:

- generate only a small number of useful variants;
- target approximately 1–3 alternatives per concept;
- relation concepts may be empty;
- do not generate chunk-search terms;
- do not generate RDF URIs;
- do not generate SPARQL;
- do not generate community IDs or query templates.

The raw `leaf_query` is used directly for chunk retrieval.

---

# 6. Chunk Matcher — LOCKED

Embed/search the complete `leaf_query` directly against the chunk FAISS index.

Do not rely on LLM-generated text keywords for this path.

Return:

```text
ChunkMatch
├── chunk_id
├── document_id
├── similarity
└── text / retrievable text reference
```

Chunk similarity is an auxiliary relevance signal.

Because chunks may be up to approximately 1024 tokens, low/moderate query-to-chunk similarity must not automatically invalidate otherwise strong evidence.

---

# 7. E-R Matcher — LOCKED

Deterministic FAISS matcher over separately persisted:

- entity index;
- relation/property index.

Input:

```text
ERMatchRequest
├── entity_concepts[]
├── relation_concepts[]
└── config
```

Output:

```text
ERMatchResult
├── entity_matches[]
│   ├── concept_id
│   ├── input_term
│   ├── uri
│   ├── label?
│   └── similarity
└── relation_matches[]
    ├── concept_id
    ├── input_term
    ├── uri
    ├── label?
    └── similarity
```

Rules:

- preserve concept grouping;
- keep similarity scores;
- map FAISS IDs back to RDF resources;
- never enumerate a full Cartesian product of top-k matches;
- top-k candidates are candidate sets.

---

# 8. Community Graph assumptions — LOCKED

Current Community Graph Constructor produces a hierarchy:

```text
Entity
  → memberOf → Level-0 Community
  → memberOf → Level-1 Community
  → ...
```

Level-0 communities contain entities.

Higher communities contain lower-level communities.

The original entity graph preserves semantic edges and their RDF predicates.

The community graph is currently undirected and unweighted for Leiden detection.

Communities are primarily a retrieval-guidance mechanism, not authoritative evidence.

---

# 9. Community Selector — LOCKED CONCEPT, CONFIGURABLE FORMULA

Community selection happens after E-R matching.

FAISS matches act as seeds.

Community ranking must introduce graph-structural information and must not simply duplicate FAISS ranking.

Conceptual score:

```text
community_score =
    semantic_relevance
  + λ1 * concept_coverage
  + λ2 * structural_support
  + λ3 * dispersion_bonus
```

Components:

### Semantic relevance
Derived from entity/relation FAISS evidence associated with the community.

### Concept coverage
Rewards communities representing several distinct query concepts instead of only one strong match.

### Structural support
Use graph connectivity between matched concepts.

Candidate signals include:

- whether matched concepts are connected;
- shortest-path distance;
- whether paths use matched predicates.

A simple distance component may resemble:

```text
support ∝ 1 / (1 + hops)
```

Do not let hop distance dominate the score.

### Dispersion / novelty bonus
MMR-inspired.

A highly relevant but distant community may contribute complementary information.

Important:

- distance alone is never relevance;
- first gate on adequate relevance;
- only then grant a bounded dispersion/novelty bonus.

This avoids promoting distant noise.

Do not call this formal information-theoretic entropy unless an actual entropy measure is later defined.

---

# 10. Community influence — LOCKED

For V1, communities are a **soft constraint / prioritization mechanism**, not a hard filter.

Selected communities may:

- boost candidates;
- prioritize graph regions;
- introduce additional structurally relevant candidates.

They must not automatically eliminate resources outside selected communities.

Community-aware expansion must be bounded.

Do not include every member of a selected community.

Expansion candidates may be ranked using:

- graph proximity to direct E-R matches;
- matched-relation connectivity;
- community score;
- weak tie-breakers such as local degree if useful.

Direct FAISS matches retain priority over community-expanded candidates.

---

# 11. SPARQL Builder — LOCKED

The LLM must never generate arbitrary SPARQL.

SPARQL is produced deterministically by code/templates.

Candidate sets should normally be supplied through `VALUES` / equivalent mechanisms rather than enumerating candidate combinations.

Supported V1 patterns:

### A. Direct / neighborhood lookup
Retrieve assertions involving matched entities and/or relations.

Must support:

- both graph directions where appropriate;
- URI objects;
- literal-valued objects.

### B. Bounded path lookup
Retrieve indirect relationships.

- normal max depth: 2 hops;
- escalation may allow 3 hops.

### C. Conjunctive graph-pattern lookup
Fallback-only.

- heavily constrained;
- deterministic construction;
- approximately max 3 clauses;
- no uncontrolled Cartesian enumeration.

### D. Provenance lookup
Map retrieved semantic assertions to their originating source chunks.

Direct and bounded-path retrieval should normally run concurrently.

---

# 12. Internal escalation — LOCKED

One logical retrieval call per AST leaf.

The Retrieval Mech owns retries/fallbacks.

Suggested sequence:

```text
NORMAL
  ↓ insufficient
BROADEN_CANDIDATES
  ↓ insufficient
PATH_EXPANSION / deeper bounded search
  ↓ insufficient
CONJUNCTIVE_FALLBACK
  ↓
return weak / empty
```

Possible broadening:

- lower FAISS threshold slightly;
- increase top-k modestly;
- widen bounded community expansion.

Do not repeatedly ask the LLM to reinterpret the query.

Do not recurse indefinitely.

Stop escalation immediately once evidence quality becomes satisfactory.

---

# 13. Quality signals — LOCKED CATEGORIES

Keep these conceptually separate.

### Relevance

Possible signals:

- entity/relation similarity;
- concept coverage;
- community relevance;
- presence of usable SPARQL results.

### Structural support

Possible signals:

- connectivity;
- path length;
- matched-predicate path support.

### Coherence

Compare:

1. chunks reached through quad/assertion provenance;
2. chunks independently retrieved through direct chunk FAISS.

High overlap means structured and textual retrieval independently converge on the same source region.

Track directional overlap because the sets may differ greatly in size:

```text
quad_support_coverage =
    |quad_chunks ∩ faiss_chunks| / |quad_chunks|

faiss_agreement =
    |quad_chunks ∩ faiss_chunks| / |faiss_chunks|
```

Do not rely solely on Jaccard similarity.

High coherence is strong positive evidence.

Low coherence is only weak negative evidence.

---

# 14. Retrieval status — LOCKED

Deterministic statuses:

```text
success
weak
empty
error
```

`success`
- usable evidence exists;
- at least one strong relevance signal exists.

`weak`
- usable evidence exists but relevance/structural signals remain marginal or conflicting.

`empty`
- retrieval completed successfully but produced no usable evidence.

`error`
- execution failure such as loading, SPARQL, serialization, timeout, malformed input, etc.

Exact numeric thresholds remain configurable/evaluation-driven.

---

# 15. Lazy Community Summarizer — LOCKED CONCEPT

Return exactly **one community summary per RetrievalRequest**.

The summary is orientation/context, not authoritative evidence.

Relevant communities may be:

- nearby;
- distributed across multiple branches;
- distant.

Do not assume distant communities are irrelevant.

### LCA coverage heuristic

For relevant child communities under an ancestor/LCA:

```text
coverage =
    relevant_children / total_children
```

If coverage exceeds a configurable threshold, e.g. approximately `0.8`:

- summarize the parent/LCA region directly.

If only a minority of children are relevant:

- summarize only the relevant child regions rather than unnecessarily including the whole ancestor.

Exact threshold is provisional/configurable.

### Large summary inputs

If inputs exceed the LLM context/token budget:

1. batch child/community summaries;
2. summarize each batch;
3. synthesize batch summaries;
4. return one final community summary.

Prefer summary-of-summaries over truncating raw evidence.

### Dispersion-aware summarization

Track metadata such as:

- contributing communities;
- LCAs;
- branch count;
- average/max tree distance or similar dispersion measure.

When dispersion is high, instruct the summarizer to preserve:

- differences between regions;
- relationships between regions;
- why multiple distinct regions are relevant.

Do not collapse highly dispersed evidence into a generic ancestor-level description.

---

# 16. Tables — LOCKED OUTPUT ROLE, RETRIEVAL ALGORITHM PROVISIONAL

Tables are auxiliary structured evidence.

Do not return entire tables by default.

Return only matched rows/cells plus enough context:

```text
TableEvidence
├── table_id
├── headers
├── matched_rows / matched_cells
├── source_document
├── source_chunk?
└── retrieval_score?
```

Exact table matching strategy may remain modular/provisional.

---

# 17. Result normalization — LOCKED

After SPARQL retrieval:

### Canonicalize
Treat identical:

```text
(subject, predicate, object)
```

as the same semantic assertion.

### Merge provenance
Collect all unique source chunks supporting the canonical assertion.

### Preserve retrieval origin
Examples:

```text
direct
path
conjunctive
```

One assertion may have multiple origins.

### Attach signals

Keep separate:

- relevance score;
- structural score;
- coherence score;
- community IDs/contribution.

Do not prematurely collapse everything into one opaque score.

A final ranking score may be computed separately.

---

# 18. EvidenceBundle — LOCKED

Core evidence units must remain paired with their sources.

```text
EvidenceBundle
├── query_id
│
├── evidence_items[]
│   └── EvidenceItem
│       ├── assertion
│       │   ├── subject
│       │   ├── predicate
│       │   └── object
│       ├── modifiers[]
│       ├── source_chunks[]
│       │   ├── chunk_id
│       │   ├── document_id
│       │   └── text
│       ├── retrieval_origins[]
│       ├── community_ids[]
│       ├── relevance_score
│       ├── structural_score
│       └── coherence_score
│
├── table_evidence[]
│
├── community_summary
│
└── retrieval_metadata
    ├── matched_entities[]
    ├── matched_relations[]
    ├── relevant_communities[]
    ├── retrieval_status
    └── warnings[]
```

Key principle:

> Assertions and supporting source chunks form one evidence unit.

Do not return unrelated flat `assertions[]` and `chunks[]` and force the Reasoner to reconstruct provenance.

One semantic assertion may legitimately have multiple source chunks.

---

# 19. Concurrency — LOCKED

The Agentic Reasoner scheduler owns cross-leaf concurrency.

The Retrieval Mech processes one independent request:

```text
RetrievalRequest → EvidenceBundle
```

It does not know about sibling AST leaves.

Different leaf requests may finish out of order.

`query_id` restores deterministic structural mapping.

Internal concurrency is allowed where operations are independent.

Examples:

- chunk FAISS retrieval;
- table retrieval;
- portions of structured retrieval;
- direct and bounded-path SPARQL retrieval.

Dependent stages must remain ordered.

Community summarization occurs only after relevant communities are established.

---

# 20. Suggested default configuration — CONFIGURABLE

Initial defaults:

```text
entity_top_k = 5
relation_top_k = 5
chunk_top_k = 8

similarity_threshold ≈ 0.55

community_top_n = 3
community_expansion_limit = 5
community_coverage_threshold = 0.8

max_path_depth = 2
escalated_max_path_depth = 3

max_conjunctive_clauses = 3

summary_token_budget = model-dependent

internal_concurrency_limit = 3–4
```

These are starting values only.

They must be configurable and should later be tuned through evaluation.

---

# 21. Provisional / unresolved heuristics

Codex may implement conservative defaults behind isolated helper functions/configuration, but must not treat these choices as final architecture:

- exact community-score weights;
- exact evidence-ranking formula;
- exact similarity thresholds;
- exact `success` / `weak` thresholds;
- exact community-expansion ranking formula;
- exact relation → community endpoint weighting;
- exact dispersion metric;
- exact Lazy Summarizer batching/token policy;
- exact number of provenance chunks retained per assertion;
- exact table-matching algorithm;
- exact escalation thresholds.

These should be easy to replace after evaluation.

---

# 22. Explicit non-goals / DO NOT redesign

Do not:

- move keyword/synonym generation into the Agentic Reasoner;
- make the Reasoner generate SPARQL;
- expose generated retrieval terms to Reasoner control flow;
- allow arbitrary LLM-generated SPARQL;
- hard-filter the entire KG by community in V1;
- enumerate Cartesian products of FAISS candidates;
- return assertions without their provenance/source context;
- make community summaries authoritative evidence;
- require more than one logical retrieval call per leaf;
- put dependency scheduling inside Retrieval Mech;
- introduce speculative cross-leaf retrieval;
- recursively reformulate indefinitely;
- collapse all quality signals into one uninterpretable score;
- redesign existing Community Graph semantics without explicit approval.

---

# 23. Existing modules/artifacts to integrate

Codex should reuse rather than reimplement where possible:

- RDF Dataset / Graph Serializer;
- Community Graph Constructor;
- persisted entity FAISS index;
- persisted relation/property FAISS index;
- chunk FAISS index;
- entity/relation FAISS-ID mappings;
- JSON table outputs from Table Processor;
- existing LLM batching/utilities;
- existing chunk/document identifiers and provenance conventions.

If entity/relation FAISS persistence is not yet implemented, add persistence/loading cleanly without altering the semantic matching behavior unnecessarily.

---

# 24. Implementation philosophy

Prefer:

- deterministic logic after LLM query interpretation;
- small composable helpers;
- explicit typed/internal contracts;
- configurable thresholds;
- logging useful for tests/evals;
- graceful weak/empty results;
- high recall before aggressive pruning.

The Retrieval Mech should be independently testable without running the full Agentic Reasoner.

Do not optimize or add architectural complexity unless required by these specifications or existing module interfaces.