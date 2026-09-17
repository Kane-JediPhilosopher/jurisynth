# Jurisynth consolidated hand-off — v2, 2026-09-14

READ THIS FIRST. This supersedes the earlier overview while preserving its evidence in previous_handoff/. The owner requests a second opinion and a focused recovery plan, not implementation changes. No runtime prompts/configuration were modified during these reviews. Two local-only diagnostic cases were run; no new NIM calls or full global smokes were launched.

## Review request

Help identify the causes of latency and the smallest faithful integration corrections. Separate measured causes from hypotheses. The owner is severely burned out: provide one prioritized plan, with few necessary decisions, and do not recommend another long run that discards completed work. The goal is a defensible local/open-source thesis demonstration, not a production deployment or wholesale rewrite.

## 1. Global v10 runs: what actually completed

- Messy: six leaves, approximately 83 minutes, 11 recorded HTTP 503 retries.
- Organized: seven leaves, approximately 96 minutes, nine recorded HTTP 503 retries.
- Both generated ASTs, completed retrieval and all leaves, then failed final-report JSON parsing after hitting the old explicit 1400-token output cap.
- The owner requested removing outbound max_tokens/max_completion_tokens. The current shared Reasoner NIM wrapper and Image Expander omit these fields. Compatibility arguments/default fields still exist but the shared NIM wrapper ignores them. Provider-default output limits remain possible. Forty local tests passed; no live revalidation of this change yet.
- Per-request, overall query and process-watchdog deadlines were disabled for these v10 runs by owner request; retry behavior remained unbounded for configured transient failures. The five-minute bound used in the new standalone diagnostic did NOT reinstate production timeouts.
- Full leaf/final raw responses and complete bundles were not checkpointed on final synthesis failure. Existing retrieval logs have IDs, status and total duration, not individual search spans or community skip reasons. NIM request events lack leaf query IDs, so some concurrent-request attribution is ambiguous.

## 2. Table, image and contradiction coverage in those runs

Tables: all six messy and seven organized retrieval events contain five table IDs. This is 30 and 35 hits, not necessarily unique resources, answer-bearing relevance, or proof every row reached the answer prompt. Returned table evidence can be inspected in the retrieval implementation; there are no persisted complete failed-run bundles.

Images: the wrapper schedules an image-search operation, but _search_images returns immediately unless constraints.include_images is true or the query contains one of its exact visual-keyword tokens (image, figure, diagram, chart, map, photo, photograph, scan, logo, visual). None of the 13 preserved atomic leaf texts matched those tokens; recorded task constraints omit include_images. No dependency-query-materialization event is recorded in these logs. Under the recorded path, these were not actual image-FAISS/Expander coverage tests. Image expansion has separate prior live tests, but no fine-grained Omni events in these global logs. Do not count unrelated Image Processor smoke calls as retrieval expansion coverage.

Contradictions: detection completed and logged eight messy/six organized warning IDs. The run logs do not record the selected scorer or CrossEncoder inference. main.py defaults JURISYNTH_CONTRADICTION_SCORER to explicit and enables NLI only for mode nli. The runner does not explicitly set that variable; inherited historical environment is not checkpointed. Therefore NLI inference in these runs is NOT confirmed. Offline NLI tests and separate synthetic conflict-explanation live tests exist, but do not imply global CrossEncoder coverage.

## 3. Community summarizer: two separate integration gaps

1. Default CommunitySelector retains top_n=3 communities; expand_for_orientation adds at most one LCA. Retrieval's count trigger requires >=6 contributing communities. It cannot fire under that default selection. A separate average-tree-distance >=4.0 trigger can still fire. No schema-less NIM requests (the current summarizer's call signature) were recorded in either v10 log. Skip reason/distance metadata was not checkpointed, so the precise per-leaf cause is unresolved.
2. EvidenceGroundedLeafGenerator constructs its user payload from node.query, dependency_claims, retrieval_status, bounded evidence_items and auxiliary_images. It does NOT include evidence.community_summary or explicit contextual_facts/constraints. Searching the current Agentic Reasoner source finds no community_summary consumption. Final report synthesis receives original_query and leaf answers, not the community summary. Thus even a generated summary is not currently wired into the answering LLM through this generator. Facts/constraints may partially appear in leaf text; this is not equivalent to explicit preservation.

Current summary inputs are deterministic graph descriptors (IDs, levels, counts, anchor labels), not raw legal assertions/chunks/tables. Summary outputs are orientation only and must not become legal authority. Spec section 15's coverage-guided parent/child summarization is not equivalent to simply appending an LCA and merging supplied descriptors. Review this against the owner's later preference for deterministic descriptors and lazy hierarchy handling, without reinstating expensive precomputed LLM leaf summaries.

Separate live fixture DID pass: run_outputs/live_community_smoke.json used a small artificial hierarchy and community_summary_min_average_distance=1.0; observed average distance=1.3333. This demonstrates live component operation under that fixture, not default global activation or answer usefulness.

No changes were made to these triggers or answer-input wiring. A rerun alone cannot be promised to invoke or consume the summarizer.

## 4. Concurrency and required dependencies

The Reasoner defaults to four concurrent leaves. Retrieval separately has four shared internal-operation slots. The retrieval specification's provisional 3–4 internal-operation limit is not calibration of Reasoner leaf concurrency.

Organized QCompiler-compatible AST had seven parallel leaves. A separate NIM semantic planner replaced every required-dependency list, resulting in q001/q002 -> q003/q004/q005 -> q006/q007. Four was not the binding limit; raising it alone would not change these waves. asyncio.gather also waits for the entire ready group before discovering new ready dependents.

Semantic validation checks output shape and IDs, not necessity. Prompt says only add an upstream answer when required to execute target, but the returned map conflates useful legal cross-references and conditional answer application with mandatory whole-leaf prerequisites. Blocking the GDPR leaf on high-risk AI classification is especially unjustified. Actor obligations, provider-change conditions and incident rules can largely begin retrieving named conditional rules independently; later scenario-specific synthesis can combine roles/classification.

See COMMUNITY_AND_DEPENDENCY_REVIEW_20260914.md for all eight organized and six messy added dependency edges. Distinguish raw AST from final semantic execution DAG; do not treat a placeholder inherited from a questionable dependent wrapper as proof of necessity. Do not change all dependencies to parallel indiscriminately.

## 5. Latency: measured global gaps versus the new local diagnostic

Confirmed global contributors: slow NIM attempts, 503 retries, additional logical validation calls after truncated outputs, mandatory dependency waves, shared operation slots. Their times overlap, so summing attempts is not wall-clock attribution.

Organized q003 retrieval took 1896.718 seconds (31.612 minutes). The conservative possible logged-interpreter-interval upper bound was 156.328 seconds; the remainder lower bound is 1740.390 seconds (~29 minutes). This shows the interval is not explained by its possible logged Query Interpreter call alone. It does not prove local CPU work: queue/lock wait, page faults, graph/index operations and other uninstrumented stages can contribute. Full per-stage and per-query request correlation is missing.

New diagnostic, no API calls, two sequential hand-authored interpretations against global artifacts:

- Startup: module imports reached artifact loading at 90.979 seconds. Global artifact loading took 6.360 seconds; setup reached first case at 104.079 seconds. Distinguish startup from mid-query latency.
- Small interpretation (2 entity concepts, 1 relation): 31.829 seconds, weak retrieval. Initial structured pass 3.193 seconds; escalated structured pass 28.616 seconds, including three-hop expansion 16.811 seconds. Chunk .188 seconds; table .179 seconds. Five table hits; eight evidence items.
- Broader interpretation (5 entities, 4 relations, 17 terms including variants): 5.318 seconds, success status. Structured pass 5.303 seconds, including relation matching 3.549 seconds and bounded two-hop paths 1.330 seconds. No weak-evidence escalation. Chunk .074 seconds; table .065 seconds. Five table hits; 22 evidence items.
- End-of-case RSS 2.388/2.400 GiB, not peak RSS. Adaptive auto mode selected two E-R shards with 4.236 GiB available at load. Production adaptive policy was unchanged.
- Three-hop traversal is a demonstrated local contributor in this diagnostic, not a demonstrated complete explanation of the old 14–32 minute retrieval intervals. Those large delays were not reproduced. Hand-authored terms often hit exact-label lookup, so this is not a replay of actual NIM-generated concept/variant workload. Sequential case/cache differences and inclusive overlapping spans prevent strong comparisons.

Read diagnostic/results.json, events.jsonl and INTERPRETATION.md, plus the exact diagnostic script. The watchdog did not fire; process finished normally. No quality gate was closed.

## 6. Proposed next experiment — NOT RUN OR IMPLEMENTED

Owner suggested a 1-hop-only comparison. Capture one real NIM interpretation including concepts and variants, then replay identical local inputs with default 2/3-hop expansion versus a diagnostic-only 1-hop path. Keep seeds, top-k, exact-label policy, evidence budgets and query wording fixed. Measure latency AND answer-bearing evidence recall/source coverage. No additional prompt changes or provider substitutions in that comparison. Repeated/counterbalanced runs can help distinguish caches.

Add spans for operation-queue wait, shard-lock wait, shard load/search, embedding, graph enumeration, chunk resolution, 2/3-hop expansion and escalation. Record query/call IDs and checkpoint bundles/leaf outputs before final synthesis. Start sequential; add limited concurrency only after checking memory. Do not remove shard locks simply to speed up searches: they protect peak RAM.

Relevance-guided best-first/beam search is an alternative for later discussion, not a drop-in A*/Dijkstra optimum guarantee. It can prune useful intermediate nodes or paths. NetworkX describes highest-value-neighbor beam traversal here: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.traversal.beamsearch.bfs_beam_edges.html . No such traversal replacement was made.

## 7. Prompt review and actual QCompiler integration

All ten current system prompts are exported verbatim with source locations in SYSTEM_PROMPTS_20260914.md. Schemas are separate in agentic_reasoner/schemas.py and ImageExpander's expansion schema.

Highest-priority prompt/input concerns: distinguish retrieval prerequisites from synthesis reuse in semantic planning; review dependency-heavy compiler example as a possible bias (not proven cause); restore intended explicit facts/constraints/orientation hand-off to answering; preserve temporal applicability, conditionality, direct rules versus inferences versus gaps. The other prompts are concise and scoped but not empirically demonstrated optimal. Merely shortening prompts is not a measured cure for multi-minute latency. No prompts were edited.

Important naming clarification: jurisynth/vendor/qcompiler_parser.py explicitly identifies itself as a minimal custom implementation of QCompiler's grammar, excluding upstream translator and recursive executor. Jurisynth's custom QCompilerTranslator performs NIM JSON-AST prompting, converts to a compatible expression and uses that parser. It is NOT currently the upstream QCompiler Translator or pretrained compiler model.

Upstream components.py Translator.__init__ accepts client/model_name; translate accepts query, max_tries and generation kwargs but constructs its own messages using fixed BNF_PROMPT. There is no dedicated custom system-prompt argument in that reviewed source. Custom prompting is possible by adapting the translator; our current wrapper already defines its own prompt. Official source: https://github.com/YuyaoZhangQAQ/QCompiler/blob/main/src/components.py . Review whether this integration matches the original intended QCompiler dependency; do not automatically replace it without owner approval.

## 8. Remaining work and guardrails

The checklist still reports 167/175, with eight overlapping unchecked entries: global loader/complex smoke validation; bundled deferred scoring/presentation features; joint retrieval calibration; NLI adoption calibration; source/version-resolved legal QA and answer scoring; table/community heuristic decisions; configurable-default decisions; final retrieval/provenance/coverage metrics. That percentage measures recorded implementation work, NOT dependable demo readiness. Newly discovered integration/observability concerns are not yet separate counted boxes.

Current priority clusters: reliable execution/dependency scheduling, community/input wiring, complete checkpointed report delivery, retrieval quality diagnosis/calibration, defensible evaluation. Several modules exist and have separate tests; do not conclude the whole project is absent or every feature remains unbuilt.

Global controlled assertion probe: .385 exact recall, .085 direct source-chunk recall on 200 cases, no execution errors; unvalidated KG-derived gold, not legal accuracy. Dev A/B/C: .35/.35/.40 on 40 controlled cases, production unchanged. AI-adjudicated synthetic NLI: test macro-F1 .891, contradiction precision .909 on 36 test pairs; not expert legal gold, qualitative scope/error review remains pending. Natural QA includes alternate-source successes and real misses, but source/version applicability and final scoring are unfinished.

Preserve frozen KG extraction prompts. Do not reinstate the owner-reverted named-instrument retrieval fix. Do not change models to Super except an explicitly approved comparison. Do not reinstate production timeouts or max-token parameters. Do not treat this hand-off as authorization to change runtime code, label synthetic data expert gold, or tune on held-out evaluation cases.

## 9. What Chat should return

1. Challenge/confirm the findings using attached code; explain uncertainty in scorer/modality coverage and latency attribution.
2. Rank the smallest necessary fixes separately from quality improvements and deferrable features.
3. Recommend one checkpointed, single-variable diagnostic plan and criteria for deciding whether 1-hop restriction sacrifices too much evidence.
4. Review hard versus optional dependencies, parent/child summary fidelity, summary consumption and facts/constraints propagation.
5. Give a short readable owner-facing summary, without false reassurance, a large new annotation burden or another readiness percentage.

## Package map

- THIS_HANDOFF.md: this consolidated overview; read first.
- SYSTEM_PROMPTS_20260914.md and COMMUNITY_AND_DEPENDENCY_REVIEW_20260914.md: exact prompts and detailed edge review.
- diagnostic/: exact profiling script, timing results, checkpoints and interpretation.
- current/: relevant source snapshots/specs/checklist; includes latest leaf generator, workflow, RDF retriever, shard implementation and scorer selection.
- previous_handoff/: complete v1 hand-off, with raw v10 logs/results, all AST/execution graphs, retry evidence, source files and earlier review context.

No credentials, .env, full corpus, large graphs or index binaries are included. The archive is a review package, not a runnable global-artifact distribution.
