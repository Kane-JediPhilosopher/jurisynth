# Jurisynth — Agentic Reasoner Specification v2

## 1. Purpose

The Agentic Reasoner orchestrates:

- conversational clarification;
- task/query understanding;
- semantic routing;
- complex-query decomposition;
- dependency planning;
- dependency-aware execution;
- evidence-grounded answer generation;
- Claim generation and provenance;
- contradiction detection;
- hierarchical report synthesis.

The system should prioritize:

1. Grounded legal answers.
2. Explicit provenance.
3. High recall.
4. Clear handling of contradictory information.
5. Deterministic orchestration where practical.
6. Parallel execution where dependencies permit.
7. Minimal unnecessary LLM calls.

User-facing transparency should follow:

```text
Report
  → Section
    → Claim
      → Evidence
        → Source
```

Internal reasoning/tool execution should not normally be exposed to the user.

---

# 2. High-Level Pipeline

```text
User Conversation
       │
       ▼
Conversation Intake / Clarification
       │
       ▼
Query + Context Analysis
       │
       ▼
Semantic Router
   ┌───┴────┐
DIRECT    COMPLEX
   │          │
   ▼          ▼
Answer     QCompiler
Generation     │
               ▼
        AST Dependency Planner
               │
               ▼
        Dependency Scheduler
               │
               ▼
        Retrieval Mech Tool
               │
               ▼
          EvidenceBundle
               │
               ▼
        Leaf Answer Generation
               │
               ▼
          Compiled Claims
               │
               ▼
      Contradiction Detection
               │
               ▼
      Hierarchical Synthesis
               │
               ▼
          Final Report
```

A separate **Reasoning Log** records observability and evaluation information.

---

# 3. Conversation Intake / Clarification

## Responsibility

Determine whether ambiguities in the current conversational task could materially affect:

- query understanding;
- retrieval;
- reasoning;
- legal interpretation.

Ask clarification only when necessary.

## Requirements

- Preserve relevant conversational context.
- Do not unnecessarily interrogate the user.
- Preserve factual/contextual information supplied by the user.
- Do not automatically interpret every factual statement as a retrieval query.
- Proceed once the information need is sufficiently clear.

---

# 4. Query + Context Analysis

## Responsibility

Use an LLM to compile the relevant conversation into a structured task representation.

Separate:

- questions / information needs;
- contextual facts;
- explicit constraints;
- other information relevant to the task.

Example:

```text
User:
"John was eating spaghetti at 11am at the cafe when the
accident occurred. Was the cafe operator liable?"

Questions:
- Was the cafe operator liable?

Context:
- John was present.
- An accident occurred at the cafe.
- Time: approximately 11am.
- John was eating spaghetti.

Constraints:
- None explicitly supplied.
```

Contextual facts should remain available for downstream reasoning without automatically becoming separate queries.

Relevant context should later be attached to appropriate AST leaves.

---

# 5. Semantic Router

## Responsibility

Classify the structured task as:

```text
DIRECT
```

or:

```text
COMPLEX
```

`DIRECT` tasks bypass QCompiler and complex scheduling.

`COMPLEX` tasks enter the decomposition/retrieval pipeline.

The Router must not itself generate the substantive answer.

---

# 6. QCompiler Query Decomposition

## Responsibility

Use Poisson Lab's QCompiler to transform complex information needs into a query AST.

QCompiler is responsible for decomposition only.

Jurisynth remains responsible for:

- dependency analysis;
- execution;
- retrieval;
- answering;
- contradiction analysis;
- synthesis.

Preserve AST structure and intermediate query text/value wherever available.

## TBD

Confirm the exact Python representation and API of the selected QCompiler version during implementation.

---

# 7. AST Dependency Planner

## Responsibility

After QCompiler produces the complete AST, perform **one LLM call over the AST** to identify semantic execution dependencies.

The planner should determine:

- which nodes depend on which other nodes;
- which nodes may run independently;
- what upstream information must be passed into dependent nodes.

## Important distinction

AST parent/child relationships represent **logical decomposition**.

Dependencies represent **information flow**.

Do not assume they are identical.

---

# 8. Community Handling

Community-related retrieval behavior belongs entirely to the **Retrieval Mech**.

The Agentic Reasoner does not:

- identify communities;
- rank communities;
- expand communities;
- generate community summaries.

Communities are used by Retrieval Mech as high-recall retrieval guidance rather than strict hard filters.

The Reasoner may receive one `community_summary` inside the resulting `EvidenceBundle`.

That summary is:

- orientation/context;
- not authoritative legal evidence;
- not independently citable unless grounded through underlying evidence.

---

# 9. Dependency Scheduler

## Responsibility

Execute the AST according to the dependency plan.

Conceptual node states:

```text
WAITING
READY
RUNNING
COMPLETE
FAILED
BLOCKED
```

## Policy

1. Nodes whose required dependencies are satisfied become `READY`.
2. Independent ready nodes may execute concurrently.
3. Dependent nodes wait for required upstream Claims/results.
4. Completion unlocks newly eligible nodes.
5. Failed required dependencies may cause downstream nodes to become `BLOCKED`.
6. Unrelated branches continue executing.

No speculative dependency execution is required for V1.

---

# 10. Retrieval Mech Interface

The Retrieval Mech is exposed as one opaque tool/function:

```python
retrieve_evidence(
    request: RetrievalRequest
) -> EvidenceBundle
```

Normally, **one AST leaf performs one logical retrieval call**.

The Agentic Reasoner owns:

- deciding when a leaf is eligible;
- constructing the `RetrievalRequest`;
- cross-leaf concurrency.

The Retrieval Mech owns:

- semantic retrieval interpretation;
- keyword/concept extraction;
- entity/relation variant generation;
- FAISS matching;
- community selection;
- SPARQL strategy;
- chunk/table retrieval;
- internal escalation;
- retries/fallbacks;
- evidence normalization;
- community summarization.

The Agentic Reasoner must not depend on the Retrieval Mech's internal search strategy.

---

# 11. RetrievalRequest

Conceptual structure:

```text
RetrievalRequest
├── query_id
├── leaf_query
├── contextual_facts
├── constraints              [optional]
├── dependency_claims        [optional]
└── retrieval_config         [optional]
```

## `query_id`

Stable AST/query-node identifier.

Used to map asynchronously completed retrieval results back to the correct node.

## `leaf_query`

The specific information need produced by decomposition.

Do not pass the entire original conversation.

## `contextual_facts`

Relevant facts from the current user task that may help retrieval.

These are context, not necessarily retrieval keywords.

## `constraints`

Optional explicit restrictions such as:

- jurisdiction;
- temporal scope;
- document scope;
- relevant entity constraints.

## `dependency_claims`

For dependent leaves, include only the **relevant upstream Claims/results required by the leaf**.

Do not automatically include:

- complete upstream answers;
- complete upstream EvidenceBundles;
- unrelated Claims.

## `retrieval_config`

Optional retrieval-level configuration.

Exact schema is configurable and may include evaluation-driven parameters.

---

# 12. Retrieval Mech Internal Boundary

The Reasoner should conceptually see only:

```text
RetrievalRequest
        ↓
retrieve_evidence(...)
        ↓
EvidenceBundle
```

Internally, the Retrieval Mech currently follows:

```text
RetrievalRequest
→ Query Interpreter LLM
→ entity/relation concepts + controlled variants
→ E-R FAISS Matcher
→ Community Selector
→ bounded community-aware expansion
→ deterministic SPARQL
→ assertion + provenance retrieval
→ direct Chunk FAISS + table retrieval
→ evidence normalization / quality scoring
→ Lazy Community Summarizer
→ EvidenceBundle
```

This internal pipeline should remain opaque to the Reasoner.

The Reasoner does not need visibility into or control over generated search terms during normal execution.

Search terms may optionally be recorded in the Reasoning Log for debugging/evaluation.

---

# 13. EvidenceBundle

Finalized conceptual output:

```text
EvidenceBundle
├── query_id
├── status
├── evidence_items[]
├── table_evidence[]
├── community_summary
└── retrieval_metadata
```

Possible status values:

```text
success
weak
empty
error
```

---

# 14. EvidenceItem

Assertions and their supporting provenance chunks are returned together as one evidence unit.

Conceptually:

```text
EvidenceItem
├── evidence_id
├── assertion
├── source_chunks[]
├── modifiers[]
├── retrieval_origins[]
├── community_ids[]
├── relevance_score
├── structural_score
└── coherence_score
```

## `assertion`

The canonical structured assertion/triple:

```text
(subject, predicate, object)
```

## `source_chunks`

One or more provenance chunks supporting the assertion.

These supply linguistic/legal context that may not survive assertion extraction.

## `modifiers`

Assertion-level modifiers where available.

## `retrieval_origins`

Indicate how the evidence was found, e.g.:

```text
direct
path
conjunctive
chunk_faiss
...
```

## `community_ids`

Communities contributing to retrieval of the evidence.

## Retrieval scores

Keep the following conceptually distinct:

- `relevance_score`
- `structural_score`
- `coherence_score`

The Agentic Reasoner should not collapse these into a single score unless an explicitly designed downstream policy requires it.

---

# 15. Table Evidence

Tables/rows are returned separately as auxiliary evidence:

```text
table_evidence[]
```

Exact table/row evidence schema remains dependent on completion of table integration.

## TBD

Finalize table evidence representation after the KG/table pipeline is stable.

---

# 16. Community Summary

Each retrieval operation may return exactly one relevant community summary.

Role:

> Provide semantic orientation for the Leaf Answer Generator.

It should help the model understand the broader graph region represented by the retrieved evidence.

It must not be treated as authoritative evidence by itself.

No Claim should cite the community summary as its sole legal support.

---

# 17. Leaf Answer Generation

## Input

The Leaf Answer Generator receives:

```text
Leaf query
+ relevant contextual facts
+ relevant dependency Claims
+ EvidenceBundle
```

## Information roles

### EvidenceItems

Primary evidence units.

Their assertions provide granular structured propositions.

Their source chunks provide provenance and contextual nuance.

### Table evidence

Auxiliary evidence where relevant.

### Community summary

Guiding/orientational context only.

### Dependency Claims

Previously established information required by the current query.

---

# 18. LeafAnswer

The answer-generation LLM should produce structured output directly.

Conceptual structure:

```text
LeafAnswer
├── query_id
├── status
├── answer_text
└── claims[]
```

Example:

```json
{
  "query_id": "Q3",
  "status": "supported",
  "answer_text": "The operator appears to owe...",
  "claims": [
    {
      "text": "The operator owes a duty...",
      "evidence_refs": ["E4", "E7"]
    }
  ]
}
```

The prose answer and structured Claims are both generated in the same LLM call.

Do not generate prose and then attempt deterministic semantic Claim extraction afterward.

---

# 19. Claims

A `Claim` represents a substantive factual/legal proposition produced by Jurisynth.

Not every sentence in `answer_text` must become a Claim.

Conceptually:

```text
Claim
├── claim_id
├── text
├── evidence_refs[]
└── status
```

Each Claim should explicitly reference the EvidenceItems or table evidence that support it.

Claims are used for:

- provenance;
- contradiction detection;
- dependency propagation;
- hierarchical synthesis;
- user-facing transparency.

## TBD

Finalize Claim status taxonomy.

Possible concepts include:

```text
supported
partially_supported
insufficient_evidence
```

Do not hard-code these until finalized.

---

# 20. Deterministic Claim Validation

After the answer LLM produces structured output, deterministic code should:

- validate the JSON/schema;
- ensure referenced `evidence_id`s exist;
- assign stable `claim_id`s;
- detect dangling evidence references;
- normalize output;
- preserve the raw LLM output for diagnostics.

The deterministic layer should not perform semantic Claim extraction from prose.

---

# 21. Provenance

The authoritative provenance chain is:

```text
Claim
  ↓
EvidenceItem
  ↓
Assertion + Source Chunks
  ↓
Document / Source
```

For table-based Claims:

```text
Claim
  ↓
Table Evidence
  ↓
Table / Row
  ↓
Source Document
```

The LLM selects evidence references.

Deterministic code validates those references and resolves them to source information.

The LLM must not invent citation identifiers.

---

# 22. Retrieval Quality Handling

The Reasoner reacts to the final retrieval status returned by the Retrieval Mech.

The Reasoner does **not** manage normal retrieval escalation.

The Retrieval Mech internally owns:

```text
normal
→ broaden candidates
→ deeper bounded path search
→ conjunctive fallback
→ weak / empty
```

## `success`

Proceed normally.

## `weak`

Proceed cautiously.

The Leaf Answer Generator should be informed that retrieved support is weak and should avoid overstating conclusions.

It may produce:

```text
status: insufficient_evidence
```

if support remains inadequate.

## `empty`

Do not force an answer.

Return an insufficient-evidence result unless the leaf can legitimately be answered solely from valid dependency Claims/context.

## `error`

Treat as a retrieval failure.

Dependent behavior follows the scheduler's failure policy.

---

# 23. LLM Output Failure

Malformed structured LLM output should be handled through deterministic validation.

If invalid:

1. retain the validation error;
2. retry the generation with the validation error supplied;
3. do not silently accept malformed output.

Exact retry count should remain configurable.

---

# 24. Dependency Failure

If a required dependency fails:

```text
Q1 FAILED
   ↓
Q2 BLOCKED
```

Unrelated branches continue.

If a dependency completes with insufficient evidence, do not pretend its conclusion was established.

Dependent leaves should receive the dependency's explicit status.

## Possible future extension

Required vs. optional dependencies may be encoded by the Dependency Planner if evaluation demonstrates a need.

Not required for initial implementation unless straightforward.

---

# 25. Contradiction Detection

Contradiction detection occurs after relevant leaf answers and Claims have been compiled.

It does not block answer generation.

Pipeline:

```text
Compiled Claims
      ↓
E-R Matcher
      ↓
High-recall candidate pairs
      ↓
CrossEncoder
      ↓
Contradiction scores
      ↓
Flagged conflicts
      ↓
Batched LLM explanation
```

## E-R Matcher

Use entity/relation similarity to cheaply constrain the potentially quadratic Claim comparison space.

The matcher is a high-recall candidate generator.

It is not the contradiction classifier.

Quadratic vector similarity over resources in the current reasoning task is acceptable where efficiently vectorized/batched.

Do not perform unnecessary whole-KG pairwise comparison.

## CrossEncoder

Evaluates candidate Claim pairs for contradiction.

The CrossEncoder:

- returns contradiction scores;
- flags potential conflicts;
- does not decide which legal proposition is correct;
- does not block downstream synthesis.

Exact model and thresholds remain evaluation-driven.

## LLM contradiction explanation

Flagged conflicts may be batched, e.g. approximately 10 per call.

Batch size should remain configurable.

Each input conflict should include:

- Claim A;
- Claim A evidence;
- Claim B;
- Claim B evidence.

The LLM should characterize/explain the conflict rather than adjudicating a legally correct winner.

---

# 26. Contradiction Failure Handling

Contradiction analysis is an auxiliary epistemic-warning layer.

If:

- E-R matching;
- CrossEncoder inference;
- or contradiction explanation

fails, final report generation should continue.

Record the failure in the Reasoning Log.

---

# 27. Hierarchical Report Synthesis

Do not perform an LLM synthesis at every AST level.

Instead, perform one hierarchical synthesis operation using:

- AST structure;
- intermediate-node query text;
- completed leaf answers;
- Claims;
- contradiction information.

The AST should act as **structural guidance**, not a mandatory presentation hierarchy.

The synthesis model may:

- merge sparse branches;
- organize noisy branches;
- preserve meaningful distinctions;
- create user-friendly nested sections.

AST depth should not directly determine report depth.

The root does not require a separate answer-generation call.

The original task/conversational framing supplies the overall context.

---

# 28. FinalReport

Conceptual structure:

```text
FinalReport
├── overview
├── sections[]
│   ├── section_id
│   ├── title
│   ├── answer_text
│   ├── claim_refs[]
│   └── child_sections[]
└── contradiction_refs[]
```

The report should reference existing Claim objects rather than duplicate Claim/evidence data.

---

# 29. User-facing Transparency

UI transparency should expose:

```text
Section
  → Claim
    → EvidenceItem
      → Assertion
      → Source Chunk(s)
      → Source Document
```

Claims may be represented as clickable/hoverable UI elements.

The UI may expose:

- Claim text;
- evidence;
- source chunks;
- RDF assertion;
- table rows;
- contradiction warnings;
- document/source identity.

Do not normally expose:

- retrieval keywords;
- scheduler state;
- internal LLM calls;
- SPARQL execution details;
- community ranking internals.

---

# 30. Streaming Policy

Leaf answers remain internal.

Users see synthesized report sections.

Independent execution may finish out of order, but stable `query_id`s map outputs back into the AST.

The scheduler may emit events such as:

```text
NODE_STARTED
NODE_COMPLETED
RETRIEVAL_COMPLETED
CONTRADICTION_ANALYSIS_READY
SYNTHESIS_READY
```

The UI/presentation layer—not the scheduler—owns how those events become streamed presentation.

Final sections should appear in deterministic report order.

---

# 31. Reasoning Log

The Reasoning Log is a separate observability component.

Potential information includes:

- structured user task;
- AST;
- dependency plan;
- node states;
- query IDs;
- retrieval statuses;
- retrieval latency;
- optional internal retrieval diagnostics/search terms;
- LLM latency;
- retries;
- failures;
- Claim/evidence mappings;
- contradiction scores;
- synthesis stages.

Exact schema remains **TBD**.

---

# 32. Explicit Non-Goals

The initial implementation should NOT:

- expose Retrieval Mech internals to the Reasoner unnecessarily;
- let the Reasoner generate or modify retrieval keywords;
- let the Reasoner generate SPARQL;
- make repeated Reasoner-level retrieval calls for ordinary retrieval fallback;
- build a general autonomous recovery agent;
- synthesize prose at every AST level;
- treat community summaries as authoritative evidence;
- automatically resolve legal contradictions;
- expose internal execution traces as normal user-facing transparency;
- perform unnecessary global KG-wide contradiction comparison.

---

# 33. Remaining TBD Items

The following remain intentionally open:

1. Exact `Claim` schema/status taxonomy.
2. Exact `FinalReport` schema.
3. QCompiler Python API/object mapping.
4. CrossEncoder model and thresholds.
5. Contradiction E-R similarity thresholds.
6. Concrete Python scheduler/concurrency implementation.
7. Exact LLM retry configuration.
8. Table/row evidence schema.
9. Reasoning Log schema.
10. Exact prompts for:
   - Query + Context Analysis;
   - Dependency Planning;
   - Leaf Answer Generation;
   - Contradiction Explanation;
   - Hierarchical Synthesis.

Retrieval-specific thresholds, scoring weights, community heuristics, SPARQL behavior, and retrieval escalation policy belong to the Retrieval Mech specification rather than this document.

TBD items should not be interpreted as permission to introduce additional architectural components without explicit design justification.