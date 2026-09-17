# Jurisynth completion, community integration and dependency review hand-off

## Request to Chat

Give a second opinion on the attached code and recorded evidence. Distinguish confirmed defects, design mismatches, hypotheses, and missing validation. Provide a short prioritized recovery plan for a local thesis demonstration, not a production rebuild. The owner is severely burned out: minimize decisions, do not request wholesale new annotations, and do not disguise validation gaps with a high checklist percentage. Document recommendations first; this hand-off does not authorize implementation changes.

## Current picture

- The repository checklist states 167/175 (95.4%), with eight unchecked entries. That measures recorded implementation items, not end-to-end readiness, legal correctness, or eight independent remaining changes. Several entries overlap or contain partly implemented deferred features.
- Corpus processing, aggregation, global Community Graph, disk-backed RDF/Oxigraph and adaptive/sharded index work exist. This is not a project with no working components. Do not infer all global artifacts are missing from an unsuccessful answer.
- The two global v10 complex runs generated ASTs, retrieved evidence and completed all 6/7 leaves, then failed final-report JSON parsing. They took approximately 83/96 minutes. Their final outputs hit the old explicit 1400-token cap. Removal of outbound max_tokens/max_completion_tokens is implemented and locally tested but not live revalidated. Provider-default limits remain unknown; omission is not unlimited output.
- Ultra v10 logs record 11 messy and 9 organized HTTP 503 retries. Provider latency is an important contributor, but it does not explain all uninstrumented retrieval intervals. Do not declare every delay NVIDIA's fault.
- Full leaf responses, final raw responses and complete evidence bundles were not checkpointed on synthesis failure. Retrieval timing events have IDs and total durations but lack fine-grained spans and community skip metadata. Some per-leaf API correlations are ambiguous because request logs lack query IDs.
- Named-instrument retrieval quality was previously identified as a problem. The owner explicitly rejected/reverted a named-instrument retrieval implementation change. Do not reintroduce it or claim absent coverage without inspecting corpus evidence.

## Confirmed current integration concerns

1. Default community selection retains top_n=3 plus at most one ancestor; Lazy Summarizer count trigger requires six. That count trigger is unreachable on this default path. A separate average-tree-distance >=4.0 trigger remains possible. No summarizer NIM call is recorded in either v10 run; exact skip reason was not logged.
2. The current summarizer merges deterministic IDs/shape/anchor-label descriptors, not legal assertions or raw source chunks. Its purpose is orientation. Original retrieval spec section 15 describes parent/child coverage behavior that is not equivalent to merely adding an LCA and merging selected descriptors. Review fidelity without changing the owner's prohibition against precomputing LLM leaf summaries.
3. A prior small live community fixture DID succeed. Its distance threshold was overridden to 1.0 and observed average distance was 1.3333. This demonstrates an operational component, not calibrated default global integration.
4. AgenticReasoner defaults to four concurrent leaves. Retrieval separately limits shared internal operations to four. Neither is empirically demonstrated optimal. The spec's provisional 3–4 value refers to internal retrieval operations, not necessarily Reasoner leaves.
5. Organized raw QCompiler AST had seven parallel queries. The semantic dependency planner then overwrote required dependencies, producing ready waves 2/3/2. Four was not the binding limit. Its prompt forbids dependencies based only on related topics; validation checks identifiers/shape, not semantic necessity.
6. In particular, blocking the GDPR leaf on AI high-risk classification is unjustified as a blanket execution prerequisite. Roles, obligations, modification and incident findings often help final application/synthesis without being prerequisites for initiating their independent retrieval. See the accompanying edge-by-edge review for both runs.
7. Scheduler asyncio.gather waits for entire ready waves, so dependents cannot launch as soon as their own prerequisites finish. Raising the concurrency cap alone would not resolve this.

## Questions to answer

- Confirm or challenge every dependency assessment using actual leaf wording and the original scenario. Distinguish hard information-flow requirements from optional answer reuse and final synthesis dependencies. What is the smallest faithful correction?
- Is default community summarization behavior consistent with the original spec and subsequently agreed descriptor/lazy approach? Identify conflicts explicitly. Do not simply force a summary call on every retrieval or remove bounds without assessing context, latency and usefulness.
- Which telemetry/checkpoints would make one controlled rerun conclusive about triggers, stage latency, truncation and semantic evidence quality? Avoid another hour-long run that loses all answers on final failure.
- Which changes are necessary for a defensible demonstration, which improve quality, and which can be transparently deferred? Separate prompt changes, scheduler changes, calibration, and provider behavior.
- Review all ten exact system prompts and their schemas. Recommend scoped improvements only; the KG extraction prompt remains frozen.
- Explain what the current NLI and retrieval evaluation results support and do not support. AI-adjudicated synthetic labels are not expert-validated legal gold.

## Remaining eight unchecked checklist entries (verbatim scope)

1. Re-run the global loader and complex-query smoke tests after all lazy sidecars are present; record peak RSS and cold/warm timings.
2. Deferred calibrated CrossEncoder scoring/thresholds and batched LLM conflict explanations; also streaming, elaborate clarification policy, and multi-level report presentation. This is a legacy bundled entry: some associated features already exist; do not treat the entire bundle as unbuilt.
3. Joint retrieval calibration: entity/relation top-k, exact-label priority, reranker weight, candidate limits, escalation triggers, table-versus-text allocation.
4. Optional NLI scorer calibration/explanation integration, retaining deterministic fallback. The LLM explanation layer has separate live synthetic test evidence; calibrated production adoption is still pending.
5. Source-aligned labelled legal-QA evaluation: standalone instrument/version resolution and downstream system-answer scoring. AI-assisted revisions are frozen separately; they are not yet a representative scored benchmark.
6. Decide table reranking and community trigger/LCA heuristic after pilot measurements.
7. Decide specification-marked configurable defaults from labelled evidence, including reranking, quality and stopping rules. This overlaps entry 3 and does not mean every default must undergo exhaustive tuning before a demo.
8. Record chunk/table recall@k, provenance validity, evidence coverage, weak/empty behavior on the chosen valid evaluation set.

Newly identified hard-dependency/trigger/checkpoint issues are not additional counted checkboxes yet. The existing 95.4% headline should not obscure them. The owner requested this hand-off, not a runtime implementation or checklist rewrite.

## Evaluation context

- Global 200-case controlled assertion probe: 77 exact hits (38.5%), 17 direct source-chunk hits (8.5%), no execution errors. These are retrieval diagnostics against unvalidated KG-derived gold, not assertion extraction accuracy or legal answer accuracy.
- Development retrieval ablation A/B/C used 40 controlled cases: A .35, B .35, C .40 exact recall; no production defaults changed. Improvement is preliminary, not proof of a globally fixed retriever.
- Frozen AI-adjudicated synthetic NLI set: 54 development / 36 test. Test macro-F1 .891; contradiction precision .909. Qualitative errors, legal-domain representativeness and production threshold adoption remain open.
- Natural legal QA review exists with alternate-source successes, genuine failures, rejected incoherent joins, and temporal/source revisions. Do not invent scoring-ready gold where source applicability is unresolved.

## Package map

- THIS_HANDOFF.md: this overview and review request.
- COMMUNITY_AND_DEPENDENCY_REVIEW_20260914.md: detailed current-code findings, including every dependency edge and separate live fixture evidence.
- SYSTEM_PROMPTS_20260914.md: exact ten current system prompts, with source paths/line numbers.
- prior_leaf_execution/: previous expanded hand-off archive contents, including 36 source/evidence files, raw logs, retries, sparse retrieval events, parsed ASTs and execution diagrams.
- current/: additional current wiring/config/community sources, fixture script/output, checklist and both original specifications. These are a source snapshot for review, not new smoke results.

No .env, credentials, full corpus, index binaries or huge global graphs are included. The source files can contain environment-variable names, not supplied key values. No API tests were launched for this package.
