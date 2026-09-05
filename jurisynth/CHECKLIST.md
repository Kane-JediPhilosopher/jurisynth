# Jurisynth Thesis Delivery Checklist

## Full-spec progress

**117 / 141 checklist items complete (83.0%).** Refresh this counter with:
`python -m jurisynth.checklist_progress`.

Use this in order. Five of the remaining ten days are reserved for the
literature review and other thesis writing. Items marked **MVP** are the
five-day engineering scope; items marked **defer** should not delay a tested
retrieval/reasoning demonstration.

## Scope guardrails

- [x] Freeze the thesis MVP corpus to `batch_0009` plus only any additional batches
  needed for a small, explicit demonstration.
- [ ] Keep the full 437-batch global build as a follow-on run, not an MVP dependency.
- [x] Run the project only in the documented Python 3.12 environment.
- [x] Pin all new dependencies and exclude virtual environments, caches, keys, and
  generated large artifacts from version control.

## Timebox: five engineering days maximum

- [x] **Day 1:** Community Graph Constructor tests and pilot run on `batch_0009`.
- [x] **Day 1–2:** E-R Index Builder implementation, persistence, and tests on that
  pilot graph.
- [x] **Day 2:** Minimal Table RDF Enricher and provenance tests.
- [x] **Day 3:** Retrieval MVP: direct E-R matching plus RDF/assertion/chunk provenance.
- [x] **Day 4:** QCompiler adapter, NIM/Nemotron AST validation, and Reasoner leaf flow.
  - [x] Verify one live NIM translation and evidence-grounded leaf smoke test using
    the configured `nvidia/nemotron-3-ultra-550b-a55b` model.
  - [x] Complete the three-prompt translator validation set: all three prompts
    produced valid plans under the configured NVIDIA NIM model.
- [x] **Day 5:** Retrieval-first evaluation, 20-item review, reproducibility notes, and
  thesis-ready limitations.
- [ ] Run remaining KG batches in the background when compute is available, but do not
  make their completion a condition for the pilot MVP.

## Immediate: establish confidence in existing graph outputs

- [x] **MVP** Write Community Graph Constructor tests using completed `batch_0009`.
  - [x] RDF N-Quads parses successfully.
  - [x] Semantic triples are extracted while provenance graphs are excluded from the
    entity graph.
  - [x] Community membership is deterministic with a fixed seed/configuration.
  - [x] Serialized membership links round-trip through RDF.
- [x] **MVP** Write E-R Index Builder tests before implementation.
  - [x] Entity and relation index entries map back to stable RDF URIs and labels.
  - [x] Index/metadata cardinalities agree.
  - [x] Empty graphs and literals are handled safely.
  - [x] Query top-k results preserve similarity score and concept grouping.
- [x] Implement the E-R Index Builder against the `batch_0009` pilot graph.
- [x] Persist pilot artifacts with a manifest containing source graph, embedding model,
  dimensions, index paths, and build version.

## Table RDF Enricher

- [x] Finalize the input contract: persisted table JSON plus optional source chunk ID.
- [x] **MVP** Add a minimal source/provenance representation without ontology expansion:
  - [x] `table rdf:type js_source:Table`.
  - [x] `document js_source:has_table table`.
  - [x] `table js_source:source_document document`.
  - [x] Add `table js_source:source_chunk chunk` only when a reliable anchor exists.
  - [x] Keep headers, cells, and full rows in persisted table JSON; do not create RDF
    cell/row resources in V1.
- [x] Keep Table resources out of Community Graph semantic-edge construction by default.
- [x] Add round-trip/provenance tests against a small table fixture.

## Resource Aggregator / Collector

- [x] Define a versioned global manifest before writing merge code.
- [x] Merge RDF N-Quads into one parseable Dataset while retaining named graph IDs.
- [x] Merge chunk indexes and metadata with collision checks and deterministic IDs.
- [x] Register table batch indexes/metadata under a global table manifest; do not rebuild
  embeddings unnecessarily.
  - [x] Provide a safe materialized merge path for compatible table/row FAISS indexes,
    table JSON, and row metadata; defer its full-corpus execution.
- [x] Register image metadata paths; images are not retrieval evidence in V1.
  - [x] Provide a batch-namespaced physical image-store merge path; defer its
    full-corpus execution.
- [x] Add tests for duplicate IDs, incompatible embedding dimensions/models, missing
  files, and deterministic manifest output.
- [ ] Run the full aggregation only after the target KG batches have completed.

## Community graph and global E-R indexes

- [ ] Run the Community Graph Constructor over the merged semantic KG.
- [ ] Serialize the community hierarchy and retain the entity graph build metadata.
- [ ] Build and persist global entity and relation/property indexes.
- [ ] Validate URI/label/community mappings and index cardinalities.
- [ ] Generate and persist versioned orientation summaries for hierarchy nodes during the global Community Graph build; summaries must exclude raw chunk text and remain non-authoritative.

## Retrieval Mechanism

- [x] Shared `RetrievalRequest`, `EvidenceBundle`, EvidenceItem, SourceChunk, and
  TableEvidence contracts.
- [x] Chunk/table persisted-artifact adapters and opaque Reasoner boundary.
- [x] **MVP** Load one pilot chunk index, table index, RDF dataset, and E-R indexes.
- [x] **MVP** Implement deterministic E-R FAISS matching with grouped candidate sets.
- [x] **MVP** Implement direct/neighborhood RDF retrieval plus assertion/chunk provenance.
- [x] Bound broad RDF candidate expansion with a 60-item retained-evidence budget and
  multi-concept corroboration, while preserving the 50-case assertion baseline
  (0.98 recall / 0.98 provenance validity).
- [x] **MVP** Normalize assertions with their supporting source chunks into EvidenceItems.
- [x] Surface direct chunk-FAISS hits as citable, explicitly weak EvidenceItems so a
  relevant source chunk is not discarded when E-R/RDF matching is ambiguous.
- [x] **MVP** Implement deterministic `success` / `weak` / `empty` / `error` statuses.
- [x] Add bounded path retrieval (depth 2) after direct retrieval tests pass.
- [x] Add table retrieval normalization and source-document constraints.
- [x] Select relevant communities deterministically as soft retrieval metadata; do not
  hard-filter direct evidence.
- [ ] defer: bounded community expansion, greedy Lazy Community Summarizer activation, and community-level escalation.
  - [x] Add the first bounded escalation stage: one broadened E-R candidate attempt
    after a weak/empty normal result, with stage metadata and no repeated LLM call.
  - [x] Add controlled 3-hop and conjunctive fallback stages with their
    deterministic fixtures and quality-stop rules are tested.
- [x] Add retrieval tests from known assertions/table rows and measure recall@k.

## Agentic Reasoner

- [x] Dependency-aware concurrent leaf scheduler and deterministic Claim/evidence
  reference validation.
- [x] Install or vendor QCompiler's parser/AST utilities after pinning its commit.
- [x] **MVP** Write a QCompiler adapter that converts `AtomicQuery`, `DependentQuery`,
  and `ListQuery` into Jurisynth nodes without using QCompiler's executor.
- [x] **MVP** Configure the Translator against NVIDIA NIM with Nemotron-3-Ultra, then
  test AST validity on a small prompt set.
  - [x] Live translation plus evidence-grounded leaf smoke test passed with the
    configured model.
  - [x] Three-prompt AST validation passed (four live-NIM tests passed in total).
- [x] **MVP** Add structured task analysis, routing, and one dependency-planning call.
- [x] **MVP** Add leaf-answer generation with Claim/evidence IDs and cautious handling
  of `weak`/`empty` retrieval results.
- [x] Apply a deterministic model-facing evidence budget and compact UTF-8-safe CLI
  output so broad E-R matches cannot exceed NIM context limits or flood the console.
- [x] Retry malformed structured leaf output once with its validation error; retain the
  final validation failure rather than accepting invalid Claim references.
- [x] **MVP** Add a minimal final report synthesizer over completed leaf answers.
- [x] **Pilot** Contradiction Detector — evidence-linked local E-R candidate pairing,
  explicit-negation conflict warnings, conflict IDs, report references, and isolated
  failure logging. It never adjudicates legal correctness or blocks synthesis.
- [ ] defer: calibrated CrossEncoder scoring/thresholds and batched LLM conflict
  explanations; also streaming, elaborate clarification policy, and multi-level report
  presentation.

## Full-spec reconciliation (post-MVP commitments)

This section records the remaining commitments from the original component specifications that are not already tracked above. It is deliberately broader than the MVP: completing it makes the implementation faithful to the intended architecture, not merely demo-ready.

### Retrieval Mechanism

- [x] Add a deterministic, bounded SPARQL-query-builder path alongside the current RDFLib graph-pattern retrieval, then compare their outputs on the pilot graph.
  - [x] Add deterministic direct and two/three-hop SPARQL templates that accept only matcher-produced URI candidates.
  - [x] Add diagnostic direct-SPARQL versus indexed-RDFLib agreement measurement with a deterministic fixture.
- [x] Complete controlled three-hop and conjunctive graph traversal, with explicit hop, branching, and evidence-budget limits.
  - [x] Add escalation-only three-hop traversal with per-seed limits and reverse-path deduplication.
- [ ] Add bounded community expansion using hierarchy/LCA proximity, dispersion, novelty, and a relevance threshold; do not assume a global community hierarchy is valid until the full graph is built.
  - [x] Implement a versioned hierarchy artifact, relevance-gated bounded MMR-style novelty bonus, and deterministic graph-only orientation context; selected communities guide ranking and never hard-filter direct candidates.
- [ ] Implement lazy community summarisation for large or dispersed result sets, including batched input bounds and summary provenance.
  - [x] Define the greedy hierarchy contract: summarize persisted child/LCA community descriptions, never raw leaf evidence.
  - [x] Add versioned persisted community-summary artifacts (ID, summary, level, distance, provenance) without raw chunks.
  - [x] Wire optional persisted hierarchy loading and exactly one deterministic, non-authoritative orientation payload into the Retrieval Mech; it includes LCA, branch count, and tree-distance metadata without raw chunks.
  - [ ] Add hierarchy/LCA-guided community expansion and optional batched LLM summary-of-summaries once global artifacts and calibrated summary triggers exist.
- [ ] Calibrate retrieval configuration jointly: entity/relation top-*k*, exact-label priority, reranker weight, candidate limits, escalation triggers, and table-vs-text allocation.
- [x] Formalise retrieval concurrency and timeout limits for embedding, graph, table, and optional reranking calls.
- [x] Define and test the retrieval-result contract for direct, graph, table, escalation, weak/empty, and error branches; community summaries remain pending their global hierarchy.

### Agentic Reasoner

- [x] Add conversation intake/state and a clarification policy for underspecified, ambiguous, or out-of-scope questions.
  - [x] Define and test the model-backed conversation-state and necessary-only clarification contract.
- [x] Add a one-call semantic dependency planner over the QCompiler AST. It models actual data dependencies rather than assuming every AST parent/child relation is a dependency.
  - [x] Preserve intermediate QCompiler node text/structure in synthesis guidance alongside normalized leaves and semantic dependency edges.
- [x] Materialise dependency outputs into dependent leaf-query placeholders before retrieval, with an auditable substitution record.
- [x] Complete AST-guided hierarchical synthesis, with nested user-facing sections rather than a flat leaf-answer report.
- [x] Produce a UI-ready progressive-disclosure payload: report section → claim → evidence item → source excerpt/provenance.
- [x] Add opt-in streaming events for planning, retrieval, synthesis, and completion without changing the synchronous API contract.
- [ ] Calibrate the optional NLI contradiction scorer and add an LLM explanation layer only after a labelled contradiction set exists; retain the current deterministic pilot detector as the safe fallback.

### Evaluation and operational readiness

- [x] Create a normalised copy of the manually annotated evidence queue (one currently malformed JSONL row), preserving the original annotation file unchanged.
- [ ] Run and record the source-aligned natural-query seed set; expand it into a labelled legal-QA evaluation set only after corpus coverage is known.
  - [x] Run and record the initial four-case natural-query seed evaluation; document target-alignment review before expansion.
- [ ] Define denominators and acceptance thresholds for entity, relation, path, table, provenance, answer faithfulness, contradiction, latency, and cost metrics.
- [x] Add regression fixtures for discovered retrieval/reasoning failures, including context-budget overflow and irrelevant semantic matches.
- [x] Produce a versioned pilot evaluation report and reproducibility manifest (corpus/artifact versions, model versions, configuration, commands, and seeds).
  - [x] Add a hash-backed, secret-free manifest writer for pilot artifacts, commands, model identifiers, and configuration.

### Full-spec traceability and unresolved decisions

- [x] Reconcile every numbered section of `agentic_reasoner_spec_v2.md` and `retrieval_mech_spec.md` to either an implemented component, a pending item above, or an explicitly deferred corpus/evaluation dependency.
- [x] Preserve the locked architectural boundaries: the Reasoner never generates SPARQL or retrieval terms; retrieval keeps its internal strategy opaque; community summaries are contextual rather than standalone legal authority; dependency scheduling stays in the Reasoner.
- [x] Define and document the conversation-state input/output schema and the user-visible clarification response shape.
- [x] Support explicit optional dependency semantics while retaining required dependencies as the current planner default; future labelled evaluation may decide when the planner should emit optional edges.
- [ ] Decide the retrieval table-reranking algorithm and the community-summary trigger/LCA heuristic after pilot measurements.
- [ ] Decide calibrated defaults for all specification-marked configurable values (including summary token budget, reranker choice, quality thresholds, and escalation-stop rules) from labelled evaluation data.

## Parallel components and evaluation

- [x] Add a JSONL Reasoning Log with run ID, AST/query IDs, states, timings, statuses,
  failures, Claim IDs, and Evidence IDs.
- [x] Build a retrieval-first evaluation set automatically from pilot assertions and
  table rows with known provenance targets.
  - [x] Add a pilot-coverage inspector for chunk text and indexed KG labels before
    interpreting a natural-language miss as a retrieval failure.
  - [x] Separate row-echo retrieval-integrity probes from natural identifier/context
    table questions; do not treat either as held-out legal QA.
  - [x] Add a small source-aligned natural-query seed set with expected pilot chunks;
    keep it separate from synthetic assertion probes and do not report it as a
    benchmark until manually reviewed.
- [ ] Record chunk/table recall@k, provenance validity, evidence coverage, and
  weak/empty behavior.
  - [x] Record pilot assertion recall (0.98), provenance validity (0.98), and
    direct-chunk recall (0.66) on the deterministic 50-case assertion set.
  - [x] Preserve table retrieval diagnostics: 0.15 sequential row-echo, 0.55
    stratified row-echo, and 0.35 natural-question table/row recall.
  - [ ] Define evidence-coverage denominators and a reviewed quality target before
    reporting an evidence-coverage score.
  - [x] Record an initial 20-case table/row retrieval smoke baseline and preserve its
    weak-result distribution separately from assertion retrieval.
  - [x] Add a second stratified table-row diagnostic to expose sample sensitivity rather
    than reporting the sequential numeric-table sample alone.
- [x] Manually review 20 pilot answers/evidence bundles before writing quality claims.
  - [x] Generate a deterministic 20-item review queue that prioritizes misses and weak
    outcomes, with expected assertions and observed results side by side.
  - [x] Include bounded retrieved assertion/source excerpts and explicit review labels
    in newly generated review records.
  - [x] Preserve the completed annotated queue; normalize its one malformed JSONL line
    before computing aggregate human-label statistics.
- [x] Add the LexGLUE zero-shot response adapter now that the report schema is stable.
- [ ] defer: GUI until the report → Claim → evidence payload is stable.

## Auxiliary visual evidence (post-pilot extension)

- [x] Define an opt-in visual-description stage so ordinary KG construction never
  silently incurs vision-model calls.
- [x] Build per-batch `image_index` artifacts: provenance-preserving JSONL
  descriptions, normalized FAISS vectors, and embedding metadata.
- [x] Add offline unit tests for image-manifest loading, caption-record provenance,
  and FAISS persistence; no test calls an external vision model.
- [x] Run a small Batch-0009 live-NIM caption pilot: all three eligible images
  produced indexed descriptions with no observed 429 or per-image error.
- [ ] Record corpus-scale caption failures, latency, and per-image cost before
  processing every batch.
- [ ] Integrate image candidates as separately labelled auxiliary evidence in the
  Retrieval Mech, Agentic Reasoner disclosure payload, and frontend evidence drawer.
  - [x] Add per-batch image-index loading, visual-intent-only FAISS retrieval, and
    `ImageEvidence` contract records; images do not change legal-evidence status.

## Thesis-ready evidence

- [x] Capture reproducible commands, configurations, artifact versions, and corpus scope.
- [x] Preserve failed/weak cases alongside successful demonstrations.
- [x] Write limitations plainly: pilot corpus scope, no legal correctness guarantee,
  QCompiler/Nemotron adaptation, and deferred features.
