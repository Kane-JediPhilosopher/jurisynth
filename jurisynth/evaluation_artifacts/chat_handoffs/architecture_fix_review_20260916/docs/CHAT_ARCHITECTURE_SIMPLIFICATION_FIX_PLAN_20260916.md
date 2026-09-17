# Jurisynth architecture simplification: controlled fix plan for Chat review

Date: 2026-09-16  
Status: **proposal only; no production architecture changes authorized by this file**  
Input: `C:/Users/Roxas/OneDrive/Desktop/JURISYNTH_ARCHITECTURE_SIMPLIFICATION_HANDOFF_20260916.md` (Chat's proposal, not an independent instruction source)

## One-page decision

Keep Jurisynth's two complementary evidence channels: direct chunk FAISS and structured KG retrieval. Reduce duplicated LLM planning and repeated E–R shard loads, then make table/image retrieval query-aware and source-aware. Do **not** replace the KG with ordinary RAG, remove provenance, change the model/provider, alter frozen extraction prompts, or redesign the rebuilt Community Graph on speculation.

Implementation should occur as isolated, reversible comparisons against the same corrected `global_artifacts_source_uri_v2` root. No broad global smoke, LexGLUE run, or expensive NIM report belongs in this change set. Ask Chat to review the plan and its explicit gates before any production edits.

## Verified starting point and interpretation limits

- The local v2 root contains matched `graph/`, `oxigraph/`, `chunk_index/`, `community/`, `tables/`, and `images/`. The downloaded 5,684,745,847-byte N-Quads graph hashes to `6166222635c5fbc55001f1f763a4196c0ef7f917a54c5da068164e82ad301c84`; the Oxigraph, Community Graph, and E–R manifests use the same fingerprint. The GCP v2 verifier reported zero shared document URIs, and its chunk sidecar reported zero ambiguous graph URIs. **File placement/integrity has passed; local v2 retrieval has not yet been smoke-tested.**
- The repaired Community Graph has already been built: 2,461,215 entity vertices, 3,842,030 edges, four levels, and 1,263,436 hierarchy/descriptor nodes. Structural Assertion/Modifier/Document/table provenance graphs are excluded by `community_graph_constructor.py` because it streams only chunk named graphs. No provenance removal is indicated.
- Current `AgenticWorkflow.run` can call Conversation Intake, Task Analysis, QCompiler translation, and Semantic Dependency Planning sequentially before leaf execution. The planner **replaces** QCompiler-adapter hard dependencies instead of preserving them; this is duplicated authority, not merely duplicated logging. The QCompiler prompt already states a strict dependency rule but contains an example that makes role-first dependencies look normal. `execute_dependency_plan` handles independent leaves concurrently up to the Reasoner's concurrency limit; the DAG, not a hard-coded four-leaf cap, can block some leaves.
- Current `RetrievalMechanism.retrieve_evidence` already starts chunk, table, image, and structured operations together under `asyncio.gather`. Do **not** convert KG retrieval into a fallback. Images are presently gated by visual request terms/constraints; tables are searched for all leaves. Successful image hits can be expanded before evidence merging. `_status_for` recognizes strong structured/table results but not strong standalone chunk excerpts as `success`, which can trigger structured escalation even when chunks are useful.
- Current table `search(..., document_ids=...)` does a full-global FAISS top-`ntotal` search before filtering document IDs; image search has no document filter. Thus a source-scoped second pass is not merely a second call to the existing API: its actual cost and filtering behavior must be measured and, if needed, adjusted without inventing a new persistent index prematurely.
- `LazyShardedFlatIndex.search` reloads each exact FAISS shard on every search. `ERMatcher._match` searches separately per concept. Exact-label matches already bypass vector search. A bounded batch of all unmatched concept vectors by index kind could reduce repeated shard deserialization while preserving exact-label priority and exact top-k semantics. **The local v2 E–R directory presently has monolithic entity/relation indices and no v2 shard directory.** The old v1 shards cannot be reused against new v2 IDs/metadata.
- The frozen **v1** q003 diagnostic is a measurement reference, **not** a v2 before-state or a legal-quality gold. It had 14 entity + 9 relation concepts; 40 shard loads for ten sharded searches; 77.77 s retrieval, including about 43.71 s E–R matching, 12.90 s community selection, and 16.96 s two-hop traversal. Eight direct chunks included seven AI Act excerpts; five fast table hits appeared irrelevant; structured results were noisy. It did not execute leaf answers, vision expansion, Lazy Community Summarizer, or NLI. Neither baseline nor the `no_three_hop` comparison actually entered three-hop traversal. The earlier capture also found that NIM calls/retries dominated pre-retrieval wall time; local changes will not prove provider latency is fixed.

## Comparison contract: what must be held fixed

1. Use one immutable, fingerprinted v2 artifact root for every local before/after replay. Preserve the old `global_artifacts` and the downloaded v2 root; new shards, if needed, belong under the v2 root and must not overwrite monolithic indices.
2. Record query text, exact captured concepts, artifact fingerprint, index mode/shard count, retrieval settings, machine available RAM, process RSS, cold/warm state, and whether NIM was called. Use the q003 capture with **empty dependency claims** only as a retrieval-only probe; do not claim that it reproduces a fully materialized runtime leaf.
3. First run a read-only, zero-NIM global loader/retrieval smoke against v2. If OneDrive/RocksDB file access or adaptive E–R loading fails, stop architecture work and diagnose the environment. V2 sharding is a prerequisite **only if** the adaptive E–R loader cannot safely use the monolithic index on this laptop; produce exact shards on a host with adequate RAM/disk, then download them. Never force FAISS mmap on an IndexFlat layout as a false RAM fix.
4. For changes to prompts, retain the same model, structured-output schemas, retry policy, and input question. A single live NIM attempt can check format/concept scope, but provider latency is noisy; assess local retrieval costs with captured outputs and compare legal-source utility separately. Do not treat one provider timing as proof of speedup.
5. Each production diff gets focused tests, one controlled replay, a before/after event log, and a rollback point before the next diff. Fail closed on loss of answer-bearing source coverage, provenance, named-instrument grounding, or independent-leaf parallelism. Do not tune multiple unrelated thresholds to rescue a failed comparison.

## Phase 0 — v2 baseline and environment gate (no production change)

**Actions:** Verify the local Oxigraph store opens read-only and the v2 chunk/Community/E–R sidecars load. Check E–R RAM mode using the loader's normal adaptive policy; if low RAM blocks monolithic IndexFlat and no v2 shards exist, build/download one versioned exact shard configuration (four is the existing diagnostic reference, **not** an architectural cap). Run `benchmark_global_retrieval.py` for one simple source-grounded question and `diagnostics/latency_probe.py replay` on captured q003 with `--artifact-root jurisynth/global_artifacts_source_uri_v2` and `--community-dir jurisynth/global_artifacts_source_uri_v2/community`. Provider calls, image vision expansion, and LLM community merging must be absent. A frozen-concept replay needs no new Query Interpreter call.

**Record:** load time, first/warm retrieval time, RSS/peak, E–R search/load time and count, community selection time, one-/two-/three-hop counts/times, channel-level evidence counts, source documents, table/image hits, retrieval status, and warnings. Mark answer-bearing excerpts for a **small** sample; do not use unlabelled evidence quantity as legal precision. Store outputs in a new dated comparison directory, not in old q003 logs.

**Gate:** baseline must finish without a VM/NIM dependency and without a RAM safety override. If it does not, report that environmental blocker before changing prompts or routing.

## Phase 1 — remove duplicate dependency authority, then consider intake consolidation

### 1A. QCompiler dependency authority (smallest reversible diff)

**Candidate files:** `agentic_reasoner/workflow.py`, `agentic_reasoner/qcompiler_translator.py`, `agentic_reasoner/qcompiler_adapter.py` only if a contract issue appears; relevant tests in `agentic_reasoner/tests/test_qcompiler_translator.py`, `test_qcompiler_adapter.py`, `test_dependency_planner.py`, scheduler/workflow tests; wiring in `main.py`/global workflow entry point.

**Proposal:** Disable the separate Semantic Dependency Planner in the controlled variant **without deleting its module or interface**. Make parser-validated QCompiler hard edges authoritative. Change only the QCompiler example/instruction that biases `dependent` toward role-first issue spotting; keep JSON AST schema, parser validation, model, and retry behavior. A hard edge is legitimate only if target retrieval or a conditional answer cannot meaningfully start before the upstream result. Related legal issues remain parallel and can be reconciled during synthesis. Review the frozen organized/messy ASTs and the actual dependency-substitution behavior before finalizing examples; do not replace a hard edge with a broken placeholder.

**Comparison:** count logical NIM planning calls and physical retries; AST leaves, hard edges, runnable-at-start leaves, scheduler start/completion overlap, and whether the same legal questions survive. Test a genuine dependent fixture plus parallel issue-spotting fixtures. QCompiler JSON must still be schema-valid and parser-valid. If unsafe hard edges or missing necessary placeholders appear, restore planner wiring and review the edge policy rather than adding a third planner.

### 1B. Merge Intake + Task Analysis only if 1A works

**Candidate files:** `agentic_reasoner/intake.py`, `agentic_reasoner/workflow.py`, Task Analyzer implementation in `workflow.py`, structured-output schemas/tests, wiring in `main.py`.

**Proposal:** A single structured decision may return `proceed|clarify`, `direct|complex`, preserved contextual facts, constraints, and one necessary clarification. Keep the existing public `TaskAnalysis`/clarification/AST event contracts. Use one NIM call in the successful path; do not append a new verification call. If combined output increases invalid-response retries, loses conversational constraints, or misroutes complex queries, keep the separate calls. Consolidation is an optional measured subtraction, not a prerequisite for the retrieval work.

**Comparison:** direct and complex routes, history-dependent clarification, AST event timing, structured response validity, NIM call count, and preservation of stated facts. Do not claim reduction in end-to-end latency unless observed over a small repeated sample with provider-failure events reported separately.

## Phase 2 — leaf-scoped Query Interpreter (prompt/contract first, no arbitrary cap)

**Candidate files:** `retrieval_mech/query_interpreter.py`, `retrieval_mech/tests/test_query_interpreter.py`; inspect `retrieval_mech/rdf_retriever.py` and `contracts.py` but avoid rewiring them unless the prompt-only comparison fails.

**Proposal:** Interpret **this leaf** for minimal retrieval-specific entity/relation concepts. Contextual facts guide disambiguation, not global scenario issue spotting. Preserve named legal instruments, article identifiers, parties, places, and other genuinely relevant named entities verbatim. Keep the existing schema, variant limit, invalid-output retries, and E–R matcher contract; do not add a concept verifier or silently set a new concept-count ceiling.

**Comparison:** one controlled live interpretation for the frozen q003 request (existing capture had 14 entity + 9 relation concepts), plus a short/simple leaf and a named-instrument leaf. Track entity/relation concept counts, exact-name preservation, E–R seeds, shard searches/loads, retrieval time, ranked evidence, answer-bearing source coverage, and false-positive source spread. Existing frozen concepts remain the control for local code experiments; new interpreter outputs need their own checkpoint. If a shorter concept list loses necessary actors/instruments or source coverage, revise the *prompt*, not an arbitrary threshold.

## Phase 3 — E–R batching and measured structured expansion

**Candidate files:** `retrieval_mech/er_matcher.py`, `retrieval_mech/er_shards.py`, `retrieval_mech/rdf_retriever.py`, `retrieval_mech/mechanism.py`; E–R/structured retrieval tests; existing `diagnostics/tracing.py` for measurements.

**Proposal:** Preserve exact-label priority. Gather unmatched terms into one embedding/search batch for the entity index and one for the relation index rather than searching per concept. The sharded index already accepts multiple query vectors per `search`, so this can reduce repeated shard loads without keeping multi-GB shards resident across leaves. Preserve exact global IDs, score ordering/tie behavior, each concept's best-per-URI matches, and normalized vectors. Do not add a long-lived shard cache unless batching still leaves a demonstrated bottleneck **and** RAM headroom is measured.

**Comparison:** frozen q003 concept list before/after, identical E–R matches/seed IDs and ranked evidence, shard reads, shard-load seconds, E–R seconds, peak RSS, first/warm retrieval time, and concurrent-leaf memory. The v1 40-load result is a hypothesis source only; measure a v2 baseline before promising a particular improvement. Test multiple concepts/variants, exact-label bypass, tie ordering, sparse SQLite metadata, and two concurrent leaves.

**Structured expansion:** instrument one-hop direct quads, two-hop traversal, escalation, and (if triggered) three-hop separately. Do **not** restrict to one hop or disable two-hop by default because the prior `no_three_hop` experiment never invoked three-hop. Review `_status_for`: direct chunk excerpts can be answer-bearing yet are currently always weak alone. A chunk-driven sufficiency rule must require grounded, relevant, citable evidence and pass a small labelled case set; high cosine similarity by itself is insufficient. Keep structured and chunk search in tandem and allow evidence-status-driven escalation only after both initial results are merged. Avoid changing the E–R similarity threshold in the same diff.

## Phase 4 — two-pass table/image retrieval, staged by actual usefulness

**Candidate files:** `retrieval_mech/mechanism.py`, `retrieval_mech/artifacts.py`, `retrieval_mech/image_expander.py`, `contracts.py` only if origin metadata cannot fit existing evidence metadata; modality tests and `tests/test_mechanism.py`.

**Pass 1:** direct global FAISS search remains available without needing a KG source-document seed. Tables already do this; measure and gate inclusion so unrelated rows do not enter the Reasoner's final bundle merely because tables exist. Images currently search only on visual intent/constraint; preserve explicit-image recall. Enable ordinary-query automatic caption search only after demonstrating negligible measured cost and useful recall on a tiny labelled set. No vision API in Pass 1.

**Pass 2:** after initial chunk + structured evidence, collect document IDs from *strong/relevant* source chunks and assertions. Search table/image candidates scoped to those document IDs, score/gate them against the leaf, merge with Pass 1 by stable `(document_id, table_id, row_id)` or `(document_id, image_id)` identity, and checkpoint `direct` vs `source_scoped` origin. Source-scoped retrieval is additive, not a replacement for global recall. Keep table row provenance and image paths/captions. The existing table document filter performs global top-`ntotal` search; benchmark it before selecting a smaller in-memory scoped candidate implementation. Image search needs a document filter or equivalent scoped candidate procedure; avoid creating new persistent indices unless the measured corpus cost requires them.

**Vision expansion:** the current Mech can call `ImageExpander` for all initially returned hits. After deduplication/relevance gating, pass only a small high-relevance candidate set to expensive expansion; leave caption-only evidence on failure. Measure NIM image calls separately from FAISS caption search. Do not conflate the KG Image Processor (offline captions) with retrieval-time Image Expander (optional second vision pass).

**Comparison:** one table-primary, one image-primary, one non-modal legal question (including q003), plus a document-scoped fixture. Report Pass 1/Pass 2 items separately, unique relevant items, false positives, source coverage, provenance, FAISS latency, optional vision call count, and EvidenceBundle presentation. q003's prior five irrelevant table hits are a useful negative control; they are not a universal table threshold.

## Phase 5 — repaired Community Graph measurement, not redesign

**Candidate files:** existing community artifacts and read-only diagnostic scripts; `community_selector.py`, `community_hierarchy.py`, `community_summary.py`, and `mechanism.py` are **inspection targets only** initially.

**Actions:** on v2, measure leaf-community size distribution, largest hubs, hierarchy compression, descriptor/anchor coverage, selected communities/LCA/tree distance for a few representative leaves, orientation length, and whether Lazy Community Summarizer triggers. Distinguish selection/orientation from an actual LLM summary call. Compare against source-bearing retrieval and RAM/latency. Structural provenance should remain in the RDF graph but outside Leiden clustering. Do not tune Leiden, selector diversity, or summarizer thresholds before a specific measured failure and coverage review.

## Phase 6 — controlled acceptance and only then wider evaluation

Run focused unit/integration tests after each phase. For the final controlled comparison, use the same v2 root and a small case set containing: a simple source-grounded legal question, frozen q003, a genuinely dependent query, a parallel multi-issue query, a table-primary case, an image-primary case, and a negative/no-answer case. Keep the frozen KG extraction prompts and model fixed. Record NIM attempts, local timings, channel-level relevance/source coverage, result status, dependency overlap, modality origins, and report claims separately. A full agentic report smoke can be considered **after** local comparisons pass and provider conditions are acceptable; it is not required to judge local retrieval optimization.

Acceptance requires: no loss of necessary legal questions or provenance; parallel leaves actually start independently; matched v2 E–R and retrieval contracts pass; no new RAM crash; answer-bearing source coverage does not regress on reviewed cases; unrelated table/image noise falls rather than merely being hidden by top-k; and a measured local latency improvement without new expensive LLM calls. If a criterion fails, revert that isolated phase and report it. Do not rationalize a noisy success status as correct legal reasoning.

## Explicit non-goals and stop conditions

- No changes to frozen KG extraction prompts, graph serializer, source URI repair, or completed v2 global artifacts except versioned exact E–R shard files if needed for RAM feasibility.
- No server-first architecture, new LLM agent, second Query Interpreter verifier, provider/model switch, hidden max-token/retry policy change, or arbitrary concept/community/top-k limit.
- No chunks-first/KG-fallback redesign, no removal of RDF assertions/modifiers/document provenance, and no assumption that image expansion happens during offline caption retrieval.
- No broad LexGLUE/global quality run or hour-scale complex smoke as a test of a small local diff.
- Stop if the local v2 Oxigraph store cannot open safely on this OneDrive-backed Windows filesystem, if v2 E–R cannot load within memory headroom, or if a change loses answer-bearing source coverage. Diagnose that blocker rather than stacking workarounds.

## Review requested from Chat (please answer in the same order)

1. Is Phase 1A the narrowest defensible way to make QCompiler the single hard-dependency authority, given that the current planner replaces parser-derived edges? Are any captured organized/messy hard edges truly necessary for retrieval, rather than merely helpful for synthesis?
2. Is the Phase 0 comparison valid with the frozen q003 capture's empty dependency claims? If not, suggest one **short**, zero-NIM alternative without fabricating upstream legal answers.
3. Does batching unmatched E–R terms by index kind preserve exact-label priority, top-k semantics, and memory safety better than a cross-leaf shard cache? Identify any hidden correctness trap.
4. For Pass 2 modalities, is relevance-gated source-document expansion plus direct Pass 1 sufficient without a new persistent doc→vector sidecar? Flag any recall or cost failure, especially the table top-`ntotal` behavior and ImageIndex's absent document filter.
5. What is the smallest defensible chunk-aware retrieval-status rule that could avoid needless escalation **without** equating cosine similarity with answer support? If labels are required, specify the minimum review packet, not a broad eval program.

Please classify each recommendation as **keep**, **narrow/change**, or **defer**. Point out any step that adds an unearned LLM call, duplicates an existing mechanism, or confounds the before/after experiment. This is a plan review, not permission to implement or tune production code.

## Files to inspect (relative to `jurisynth/`)

Reasoner: `agentic_reasoner/workflow.py`, `intake.py`, `qcompiler_translator.py`, `qcompiler_adapter.py`, `dependency_planner.py`, `reasoner.py`, `scheduler.py`, `schemas.py`, `main.py`.

Retrieval: `retrieval_mech/mechanism.py`, `query_interpreter.py`, `rdf_retriever.py`, `er_matcher.py`, `er_shards.py`, `artifacts.py`, `image_expander.py`, `community_selector.py`, `community_hierarchy.py`, `community_summary.py`, `global_artifacts.py`, `contracts.py`.

Evidence/diagnostics: `evaluation_artifacts/chat_handoffs/latency_capture_20260915/HANDOFF.md` and its `capture/`, `baseline/`, `no_three_hop/` subdirectories; `diagnostics/latency_probe.py`, `diagnostics/tracing.py`, `benchmark_global_retrieval.py`, and the v2 build manifests (but **not** the multi-GB artifacts or credentials in a Chat hand-off). The v1 replay data must be labelled `v1` in any comparison.

## Deliverable format after implementation is separately approved

For each isolated diff: files changed, before/after config and artifact fingerprint, tests run, q003 and companion-case concept/seed counts, local latency/RSS, evidence/source summary, Pass 1/Pass 2 modality counts/origins where applicable, any provider attempt/error separately, and the rollback point. State plainly when a result is only a smoke test rather than a labelled evaluation.
