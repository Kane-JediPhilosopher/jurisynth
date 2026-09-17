# Jurisynth Thesis Delivery Checklist

## Full-spec progress

**167 / 175 checklist items complete (95.4%).** Refresh this counter with:
`python -m jurisynth.checklist_progress`.

Latest live validation: Ultra conflict explanations passed on two synthetic
pairs. Organized v5 completed orchestration but all eight retrievals failed
on invalid Query Interpreter JSON; messy v5 failed AST dependency validation.
The 200-case assertion probe completed with 77 exact hits (38.5%), 17 direct
chunk hits (8.5%), and no execution errors; its KG gold remains unvalidated.
The adopted calibration protocol closes planning items only. JSON-AST compiler
and Query Interpreter repair changes are under live component validation;
A/B/C development ablations are complete; C improved exact recall from 35% to
40% on 40 controlled cases, without changing defaults. Provenance
scoring uses document + chunk identity, not legacy chunk-only matching.
Messy global v6 was later found abandoned with stale `running` status and no
live process; it is now `interrupted`, not a three-hour confirmed API call.
Bounded v7 retries add query deadlines/process watchdogs and explicit RAM gates;
see `run_outputs/GLOBAL_SMOKE_V6_INCIDENT.md`. Empirical validation remains open.
Bounded v8 generated an AST successfully (172.905 seconds), then timed out
during NIM query interpretation at the 900-second overall deadline; cancellation
was logged and global runs stayed gated. Chat's follow-up is imported into a
separate frozen dataset: 90 synthetic AI-adjudicated NLI pairs (18 corrected
premises), plus 14 contextual QA cases (six question revisions). These are not
expert-validated labels or completed system-QA evaluations.
Offline NLI evaluation is complete on the frozen 54-development/36-test split:
test macro-F1 0.891 and contradiction precision 0.909. Aggregate gates pass;
qualitative scope/error review and calibrated production settings remain open.
No threshold tuning or production-default changes were made. A Chat hand-off
contains 14 NLI disagreements and six selected development retrieval cases:
`evaluation_artifacts/CHAT_CALIBRATION_ERROR_REVIEW_v1.zip`.
V9's messy component passed AST/first-leaf interpretation (588.504 seconds,
two HTTP 503 retries). Global messy then exhausted its 900-second deadline
after a 504 intake retry and analysis; AST was cancelled, not rejected by the
parser. Organized remained RAM-gated. V10 is the owner-authorized serial
global retry with HTTP/query/watchdog deadlines disabled and RAM checks kept.
The preserved four-leaf component AST also needs intent-coverage review:
`evaluation_artifacts/CHAT_AST_FIDELITY_REVIEW_v1.md`; no planner changes made.
Both global v10 runs completed ASTs, retrieval and leaves, then failed final
report JSON parsing after hitting the 1400-token output cap. Messy had 11
logged 503 retries (eight leaf-answer); organized had nine (three leaf-answer).
At owner request, the Reasoner NIM wrapper and retrieval ImageExpander now
omit explicit output-token parameters; provider defaults still apply. Forty
local tests passed; no live revalidation yet. Detailed raw logs, retry-stage
locations, compiled AST versus semantic DAG and sparse retrieval events are in
`evaluation_artifacts/leaf_execution_handoff_v3/CHAT_LEAF_EXECUTION_FOLLOWUP.zip`.
The controlled 2026-09-16 simplification now removes the separate Semantic
Dependency Planner from the production path, consolidates intake/task analysis,
uses an event-driven QCompiler DAG scheduler, batches E-R searches, and adds
source-scoped second-pass modalities. The repaired-v2 frozen q003 replay fell
from 53.36 s to 33.05 s with identical frozen evidence/source identities; the
final 12-concept interpretation ran locally in 22.79 s with 14 AI Act-supported
items. The bounded acceptance suite passed 152 tests (six optional skips).

Use this in order. Five of the remaining ten days are reserved for the
literature review and other thesis writing. Items marked **MVP** are the
five-day engineering scope; items marked **defer** should not delay a tested
retrieval/reasoning demonstration.

## Scope guardrails

- [x] Freeze the thesis MVP corpus to `batch_0009` plus only any additional batches
  needed for a small, explicit demonstration.
- [x] Complete all 437 KG-construction batches; keep the global build separate from
  the already demonstrated batch-0009 MVP.
- [x] Run the project only in the documented Python 3.12 environment.
- [x] Pin all new dependencies and exclude virtual environments, caches, keys, and
  generated large artifacts from version control.

## Local-first global RDF retrieval (Oxigraph migration)

- [x] Preserve RDFLib for construction and pilot fixtures; introduce a bounded
  RDF-store boundary only for corpus-wide retrieval.
- [x] Pin `pyoxigraph` and add a read-only RocksDB-backed Oxigraph adapter for
  direct RDF matching and deterministic SPARQL diagnostics.
- [x] Add an overwrite-safe, streaming global N-Quads → Oxigraph build command
  with a reproducibility manifest, source hash, output size, and elapsed time.
- [x] Replace global RDFLib `Dataset.parse()` loading with the local read-only
  Oxigraph store; no HTTP server or remote deployment is required.
- [x] Add a SQLite chunk-metadata sidecar so FAISS result records and graph
  provenance are resolved on demand rather than materialising the aggregate
  metadata dictionary on the Python heap.
- [x] Verify Oxigraph direct retrieval, SPARQL-compatible bounded patterns,
  provenance resolution, and global-loader integration on persisted fixtures.
- [x] Build the complete local Oxigraph store and SQLite chunk sidecar from the
  437-batch aggregate; record actual disk size, build time, and any failures.
- [x] Build a SQLite E-R metadata sidecar and use it for global FAISS candidate
  labels, exact-label matches, and community memberships on demand.
- [x] Build a slim SQLite Community Graph guidance sidecar so hierarchy and
  deterministic descriptors do not require eager JSON materialisation.
- [ ] Re-run the global loader and complex-query smoke tests after all lazy
  sidecars are present; record peak RSS and cold/warm timings.
- [x] Benchmark global cold-start RAM, first-query latency, and warm-query
  latency on the consumer laptop. With four shards, the recorded run took
  20.86 s to load, 6.50 s for first retrieval, and 5.70 s warm at 2.26 GB
  post-query RSS (3.16 GB process peak). A two-shard comparison reached a
  4.06 GB peak, confirming that the adaptive four-shard route is safer under
  tight headroom. An RDFLib global comparison remains intentionally omitted
  because it cannot run safely here.

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
- [x] Run all remaining KG batches without making their completion a condition for
  the already tested pilot MVP.

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
- [x] Run the full aggregation now that all target KG batches have completed.
  - [x] Materialize and byte-verify the streamed 437-batch global RDF N-Quads file.
  - [x] Merge compatible chunk FAISS indexes and metadata.
  - [x] Merge compatible table and row indexes plus table JSON artifacts: 84,298
    accepted tables; 2,004 tables without source row metadata excluded and recorded
    in `global_artifacts/tables/validation_report.json`.
  - [x] Merge 27,647 image caption vectors and namespaced image artifacts.

## Community graph and global E-R indexes

- [x] Run the Community Graph Constructor over the merged semantic KG.
  - [x] Persist the completed global graph: 2,461,266 entity records,
    358,503 relation records, four community levels, and a source fingerprint.
- [x] Serialize the community hierarchy and retain the entity graph build metadata.
- [x] Build and persist global entity and relation/property indexes.
- [x] Validate URI/label/community mappings and index cardinalities.
- [x] Generate and persist versioned orientation summaries for hierarchy nodes during the global Community Graph build; summaries exclude raw chunk text and remain non-authoritative.

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
- [x] Complete bounded community expansion, greedy Lazy Community Summarizer activation, and community-level escalation.
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
- [x] **MVP** Consolidate necessary clarification, task analysis, and routing into
  one structured call; use QCompiler as the only LLM authority for hard AST
  dependencies and schedule its validated DAG deterministically.
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
  - [x] Run a disclosed synthetic 24-pair NLI component calibration:
    `cross-encoder/nli-deberta-v3-base` achieved provisional precision 0.82,
    recall 0.90, and F1 0.86 at threshold 0.95. This is not legal-domain
    validation and does not enable NLI as the default detector.
  - [x] Request strict JSON-schema output for every structured Agentic Reasoner
    model turn (combined intake/task analysis, QCompiler translation,
    leaf answers, and report synthesis).
  - [x] Add optional bounded, evidence-linked batched conflict explanations with
    strict schemas, finite invalid-output retries and isolated failure logging;
    live-test on default Nemotron Ultra (99.316 seconds for two synthetic pairs).
  - [x] Evaluate a separate 20-pair synthetic NLI holdout at the fixed 0.95
    threshold: precision 0.714, recall 1.0, F1 0.833; four false positives.
    Retain the deterministic default pending real legal-domain validation.
  - [x] Fix incomplete complex QCompiler output handling: increase expression
    budget to 2048 tokens and retry invalid ASTs twice with parser feedback;
    regression tests pass. Global live rerun remains pending above.

## Full-spec reconciliation (post-MVP commitments)

This section records the remaining commitments from the original component specifications that are not already tracked above. It is deliberately broader than the MVP: completing it makes the implementation faithful to the intended architecture, not merely demo-ready.

### Retrieval Mechanism

- [x] Add a deterministic, bounded SPARQL-query-builder path alongside the current RDFLib graph-pattern retrieval, then compare their outputs on the pilot graph.
  - [x] Add deterministic direct and two/three-hop SPARQL templates that accept only matcher-produced URI candidates.
  - [x] Add diagnostic direct-SPARQL versus indexed-RDFLib agreement measurement with a deterministic fixture.
- [x] Complete controlled three-hop and conjunctive graph traversal, with explicit hop, branching, and evidence-budget limits.
  - [x] Add escalation-only three-hop traversal with per-seed limits and reverse-path deduplication.
- [x] Add bounded community expansion using hierarchy/LCA proximity, dispersion, novelty, and a relevance threshold; do not assume a global community hierarchy is valid until the full graph is built.
  - [x] Implement a versioned hierarchy artifact, relevance-gated bounded MMR-style novelty bonus, and deterministic graph-only orientation context; selected communities guide ranking and never hard-filter direct candidates.
  - [x] Add one shared-LCA context node for orientation only; it never affects candidate matching, graph traversal, or legal-evidence selection.
- [x] Implement lazy community summarisation for large or dispersed result sets, including batched input bounds and summary provenance.
  - [x] Define the greedy hierarchy contract: summarize persisted child/LCA community descriptions, never raw leaf evidence.
  - [x] Add versioned persisted community-summary artifacts (ID, summary, level, distance, provenance) without raw chunks.
  - [x] Wire optional persisted hierarchy loading and exactly one deterministic, non-authoritative orientation payload into the Retrieval Mech; it includes LCA, branch count, and tree-distance metadata without raw chunks.
  - [x] Add hierarchy/LCA-guided community expansion and optional batched LLM summary-of-summaries using persisted deterministic descriptors. Provisional count/dispersion triggers remain subject to labelled calibration.
- [ ] Calibrate retrieval configuration jointly: entity/relation top-*k*, exact-label priority, reranker weight, candidate limits, escalation triggers, and table-vs-text allocation.
- [x] Formalise retrieval concurrency and timeout limits for embedding, graph, table, and optional reranking calls.
- [x] Define and test the retrieval-result contract for direct, graph, table, escalation, weak/empty, and error branches; community summaries remain pending their global hierarchy.

### Agentic Reasoner

- [x] Add conversation intake/state and a clarification policy for underspecified, ambiguous, or out-of-scope questions.
  - [x] Define and test the model-backed conversation-state and necessary-only clarification contract.
- [x] Preserve the Semantic Dependency Planner module as a tested rollback path,
  but remove it from production execution so it cannot replace QCompiler-derived
  dependencies. QCompiler is the sole LLM dependency authority.
  - [x] Preserve intermediate QCompiler node text/structure in synthesis guidance
    alongside normalized leaves and parser-validated dependency edges.
- [x] Materialise dependency outputs into dependent leaf-query placeholders before retrieval, with an auditable substitution record.
- [x] Complete AST-guided hierarchical synthesis, with nested user-facing sections rather than a flat leaf-answer report.
- [x] Produce a UI-ready progressive-disclosure payload: report section → claim → evidence item → source excerpt/provenance.
- [x] Add opt-in streaming events for planning, retrieval, synthesis, and completion without changing the synchronous API contract.
- [ ] Calibrate the optional NLI contradiction scorer and add an LLM explanation layer only after a labelled contradiction set exists; retain the current deterministic pilot detector as the safe fallback.
  - [x] Add a disclosed synthetic calibration set and retain its result as a
    non-deployment, component-level measurement only.

### Evaluation and operational readiness

- [x] Create a normalised copy of the manually annotated evidence queue (one currently malformed JSONL row), preserving the original annotation file unchanged.
- [x] Run and record the source-aligned natural-query seed set. The current
  three-case Batch-0009 set achieved expected chunk/document recall of 1.0;
  it remains a retrieval smoke rather than a legal-QA benchmark.
- [ ] Expand the source-aligned seeds into a labelled legal-QA evaluation set only
  after corpus coverage and the proposed labels have been reviewed.
  AI-assisted review packets now exist under `evaluation_artifacts/ai_assisted_review_v1`:
  14 source-first natural candidates, six excluded joins, and 90 proposed
  source-grounded three-class NLI pairs. References and labels remain pending
  Chat adjudication; no expert review or representative benchmark is claimed.
  Chat's returned 14 QA reviews and 90 NLI labels have now been imported to
  `ai_assisted_review_v1/chat_adjudicated_v1`, with complete ID/source checks.
  Follow-up revisions are now frozen separately: six contextual questions
  revised and 18 NLI premises corrected with labels confirmed. Offline NLI
  testing is complete; qualitative error review, standalone QA source/version
  resolution and downstream system-answer scoring remain pending.
- [x] Adopt metric semantics, legal-QA rubric and provisional engineering
  acceptance criteria in `evaluation_artifacts/CALIBRATION_PROTOCOL.md`;
  report reviewed denominators and remaining empirical validation separately.
- [x] Add regression fixtures for discovered retrieval/reasoning failures, including context-budget overflow and irrelevant semantic matches.
- [x] Produce a versioned pilot evaluation report and reproducibility manifest (corpus/artifact versions, model versions, configuration, commands, and seeds).
  - [x] Add a hash-backed, secret-free manifest writer for pilot artifacts, commands, model identifiers, and configuration.

### Full-spec traceability and unresolved decisions

- [x] Reconcile every numbered section of `agentic_reasoner_spec_v2.md` and `retrieval_mech_spec.md` to either an implemented component, a pending item above, or an explicitly deferred corpus/evaluation dependency.
- [x] Preserve the locked architectural boundaries: the Reasoner never generates SPARQL or retrieval terms; retrieval keeps its internal strategy opaque; community summaries are contextual rather than standalone legal authority; dependency scheduling stays in the Reasoner.
- [x] Define and document the conversation-state input/output schema and the user-visible clarification response shape.
- [x] Support explicit optional dependency semantics while retaining QCompiler's
  required edges as the execution default; deterministic scheduling never invents
  or reorganizes semantic dependencies.
- [ ] Decide the retrieval table-reranking algorithm and the community-summary trigger/LCA heuristic after pilot measurements.
- [ ] Decide calibrated defaults for all specification-marked configurable values (including summary token budget, reranker choice, quality thresholds, and escalation-stop rules) from labelled evaluation data.

## Parallel components and evaluation

- [x] Build and benchmark exact 2-, 3-, and 4-way disk-backed global E-R index
  shards: all configurations reproduced the monolithic top-10 exactly. Isolated
  peak entity-index RSS was 1.85 GB / 1.25 GB / 0.95 GB, respectively, versus
  4.18 GB monolithic. The first 8-query search took 5.67 s / 5.92 s / 4.86 s;
  these are cache-sensitive local measurements, not portable cold-start claims.
  Keep 2 shards as the adaptive default because it is the least fragmented safe
  option; select 3 or 4 explicitly when system headroom is tighter.
- [x] Preserve adaptive E-R loading: use the monolithic index when affordable;
  otherwise select the smallest safe complete exact shard configuration and
  serialize shard searches to honor the memory budget.

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
  - [x] Record an initial global source-sampled controlled assertion probe
    (10 cases, Oxigraph/FAISS, no NIM): assertion recall/provenance validity
    0.40, assertion MRR 0.105, direct-chunk recall 0.00. This is a diagnostic
    integrity probe—not natural legal-QA or a corpus-wide performance claim—
    and its weak direct-chunk coverage is retained as a retrieval limitation.
  - [x] Preserve table retrieval diagnostics: 0.15 sequential row-echo, 0.55
    stratified row-echo, and 0.35 natural-question table/row recall.
  - [x] Define evidence-coverage denominators and an owner-approved provisional quality target before
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
- [x] Build the initial GUI after the report → Claim → evidence payload is stable.
  - [x] Add an opt-in server-side Batch-0009 runner and display the completed
    QCompiler AST in the frontend; browser code never receives NIM credentials.
  - [x] Replace the imported template's fictitious legal content with live report
    sections, expandable evidence excerpts, and a clear unavailable-state.

## Auxiliary visual evidence (post-pilot extension)

- [x] Define an opt-in visual-description stage so ordinary KG construction never
  silently incurs vision-model calls.
- [x] Build per-batch `image_index` artifacts: provenance-preserving JSONL
  descriptions, normalized FAISS vectors, and embedding metadata.
- [x] Add offline unit tests for image-manifest loading, caption-record provenance,
  and FAISS persistence; no test calls an external vision model.
- [x] Run a small Batch-0009 live-NIM caption pilot: all three eligible images
  produced indexed descriptions with no observed 429 or per-image error.
- [x] Record corpus-scale caption failures and latency from the downloaded
  processing log: 27,829 eligible images, 27,771 indexed, 58 recorded errors,
  185.5 cumulative logged minutes, and approximately 2.50 images/s.
- [x] Record corpus-scale image completion/reliability under the zero-provider-
  budget configuration rather than provider billing: 27,771/27,829 images
  indexed (99.79%), 58 recorded errors, 185.5 cumulative logged minutes, and
  approximately 2.50 images/s. External GPU-rental cost is intentionally out
  of scope for this metric.
- [x] Integrate image candidates as separately labelled auxiliary evidence in the
  Retrieval Mech, Agentic Reasoner disclosure payload, and frontend evidence drawer.
  - [x] Add per-batch image-index loading, visual-intent-only FAISS retrieval, and
    `ImageEvidence` contract records; images do not change legal-evidence status.
  - [x] Add lazy query-aware Image Expander output (expanded description,
    findings, and separate visual relevance) without replacing canonical caption
    vectors or making images legal authority.
  - [x] Return safe auxiliary image metadata in the API and display it in a
    labelled frontend modal; internal filesystem paths are never exposed.
  - [x] Serve allowlisted local image bytes for the laptop-demo deployment boundary.
    - [x] Implement the laptop-demo route: manifest-indexed image IDs only,
      approved batch-root containment, and no local path disclosure.
    - [x] Add bounded, secret-free Nano Omni smoke logging for caption and
      Expander API paths; preserve provider failures as measurements.

## Thesis-ready evidence

- [x] Capture reproducible commands, configurations, artifact versions, and corpus scope.
- [x] Preserve failed/weak cases alongside successful demonstrations.
- [x] Write limitations plainly: pilot corpus scope, no legal correctness guarantee,
  QCompiler/Nemotron adaptation, and deferred features.
