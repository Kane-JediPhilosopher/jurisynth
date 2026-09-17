# Community and dependency review — v10 complex smokes

Read-only implementation review, 2026-09-14. Only this report and the accompanying prompt export were added. No runtime logic, prompts, thresholds or defaults were modified; no API calls were made.

## 1. What the community summarizer currently does

The current LazyCommunitySummarizer merges deterministic graph descriptors: community IDs, levels, member/child counts, and anchor labels. It does not summarize the community's assertions, chunks or tables. Its intended output is orientation and answer organization, not legal authority. Such orientation can be useful, but these runs do not establish that this particular LLM merge improves retrieval or answers.

The global builder wires it in when descriptors exist. Retrieval first constructs deterministic orientation, then optionally invokes the summarizer. Both v10 logs contain no schema-less NIM requests, which the current summarizer would emit. Thus no summarizer LLM call is recorded. These logs omit the returned community metadata and explicit skip reasons; the exact per-leaf reason cannot be recovered from them. Do not equate deterministic orientation with a tested LLM summarization path.

Separate prior evidence: run_outputs/live_community_smoke.json records a successful live NIM summarizer fixture. run_live_community_smoke.py uses a small artificial hierarchy and overrides community_summary_min_average_distance to 1.0; the observed average distance was 1.3333. This demonstrates a callable live summarizer path under that fixture, not that default global triggers work or that global legal answers improve. The component is not wholly untested; its default global integration remains unvalidated.

Concrete default mismatch:

- CommunitySelector.top_n = 3.
- expand_for_orientation adds at most one LCA, yielding at most 4 contributing communities.
- RetrievalMechanism.community_summary_min_communities = 6.
- Therefore the community-count trigger is unreachable in the default global path.
- A separate average-tree-distance >= 4.0 trigger remains possible. The absence of calls does not prove what distances the actual runs produced, nor whether all returned IDs had usable hierarchy/descriptor entries.

The original retrieval specification section 15 also describes relevant-child coverage and choosing a parent versus relevant child regions. The current summarizer itself does not implement that coverage decision: it batches supplied descriptors, with an optional merge. The selector adds an LCA as orientation, which is not equivalent to summarizing a parent region by the specified coverage heuristic. Integration fidelity and usefulness remain unresolved, not demonstrated complete by these smokes.

Sources: retrieval_mech/community_selector.py; retrieval_mech/mechanism.py; retrieval_mech/community_summary.py; retrieval_mech/community_hierarchy.py; main.py; to_be_built/retrieval_mech_spec.md, section 15.

## 2. Why four leaves, and why the second run formed waves

AgenticReasoner.max_concurrency and execute_dependency_plan default to 4. RetrievalSettings.internal_concurrency_limit separately defaults to 4 shared internal operations. These are different limits; one leaf can need several operations. The retrieval specification lists 3–4 internal operations as provisional starting values, not a proof that four Agentic Reasoner leaves is optimal. No measured leaf-concurrency calibration is established here.

The organized raw AST contains seven parallel queries. SemanticDependencyPlanner performs another LLM call and replaces every leaf's required dependency list with that model's returned map. Its prompt says to add only dependencies whose answers are required to execute the target. Validation checks IDs and shape; the scheduler catches cycles. Neither validates semantic necessity. The planner receives query text, not the original full scenario/constraints or an explicit explanation of each edge.

It changed the organized run to q001/q002 -> q003/q004/q005 -> q006/q007. The four-leaf cap was not binding in these waves. Raising it alone would not parallelize the run. asyncio.gather also creates a whole-wave barrier: a dependent cannot start immediately when its own prerequisites finish if another leaf in that ready wave is still running.

## 3. Organized run: every added edge

All seven leaves can start their own legal-rule retrieval from their question and scenario context. Some final scenario-specific conclusions benefit from other leaves' findings, but that is not automatically a prerequisite for initiating retrieval. Review below distinguishes useful answer integration from required execution dependency; it is not legal adjudication.

- q001 roles: no dependencies. Appropriate independent starting point.
- q002 high-risk classification: no dependencies. Appropriate independent starting point.
- q003 obligations <- q001 roles: useful for applying actor-specific rules, but q003 explicitly names the actors. Their rules can be retrieved independently; not demonstrated necessary as a hard whole-leaf gate.
- q003 obligations <- q002 classification: useful/conditional for concluding which high-risk duties apply. Retrieve those conditional duties independently and combine classification later. Not demonstrated necessary before retrieval.
- q004 provider changes <- q001 roles: not required to retrieve modification/role-transfer conditions; q004 names those conditions and candidate actors. Useful cross-reference, over-strong execution gate.
- q005 GDPR interaction <- q002 classification: unjustified as a blanket prerequisite. Personal/special-category data, Articles 6/9, purpose limitation and automated-decision rules do not require first completing the AI Act classification question. Specific interaction conclusions can reference it later.
- q006 tensions <- q005 GDPR interaction: the strongest useful synthesis edge. The tensions question overlaps q005 and can use its results, but independently retrieving conflicting/overlapping provisions is still possible. Better justified for final synthesis than for blocking its entire retrieval pass; it also does not explicitly depend on the separately retrieved AI Act obligations.
- q007 incident sequence <- q001 roles: useful when assigning scenario duties, but all actors are named in q007. Not a demonstrated prerequisite for retrieving their incident/corrective-action rules.
- q007 incident sequence <- q002 classification: conditionally relevant to applicability of high-risk duties, but q007 can retrieve the conditional rules and medical-device vigilance rules independently.
- q007 incident sequence <- q003 obligations: useful synthesis/reuse, but q007 explicitly asks the specialized incident obligations itself. Not established as a necessary whole-leaf execution dependency. q001/q002 are additionally transitive prerequisites through q003 under this map.

Conclusion: the organized planner conflated legal relevance and answer-integration needs with mandatory information flow. It does not justify blocking q005 behind q002, and most other gates are stronger than required. A truly data-dependent leaf (e.g. 'apply the obligations to the actor identified by q001' without that actor otherwise known) would be different. These questions mostly name their targets already.

## 4. Messy run: required edges after semantic planning

- q003 duties <- q001 roles: useful actor-specific application, not required to retrieve rules for the explicitly named provider/importer/distributor/hospital.
- q003 duties <- q002 risk: conditional applicability, not required to retrieve conditional high-risk obligations.
- q004 GDPR reuse <- q002 risk: unjustified blanket prerequisite. GDPR reuse rules can be retrieved independently of AI Act high-risk classification.
- q005 regime interaction <- q003 duties: useful cross-regime synthesis, but not required to initiate its own retrieval.
- q005 regime interaction <- q004 GDPR reuse: useful to one portion of the interaction answer, but q005 concerns broader GDPR compliance than data reuse alone. Not a demonstrated blanket execution prerequisite.
- q006 incidents <- q003 duties: useful reuse of post-market findings, but incident/vigilance provisions can be retrieved from q006 independently.

The messy raw AST itself used a broad dependent wrapper over its two parallel groups. Its adapted downstream leaf texts contain 'Using {upstream_result}'. That wrapper is also too broad for the GDPR-reuse question. The semantic planner changed those original edges rather than simply preserving the compiled AST. A placeholder inherited from a questionable AST wrapper is not evidence that the underlying legal question genuinely requires earlier answers.

## 5. Evidence and prompt package

Raw logs: reasoning_logs/global_smoke_252757.jsonl (messy) and global_smoke_257808.jsonl (organized).

Parsed ASTs and execution graphs: evaluation_artifacts/leaf_execution_handoff_v3/messy_parsed_AST.json, organized_parsed_AST.json, messy_execution_DAG.mmd, organized_execution_DAG.mmd.

Exact current system prompts: evaluation_artifacts/SYSTEM_PROMPTS_20260914.md (10 prompts). Generative response schemas are separately defined in agentic_reasoner/schemas.py and retrieval_mech/image_expander.py. The NLI CrossEncoder and deterministic graph/index operations have no generative system prompts.

Recommended next changes require a separate implementation decision: reconcile summary triggers with selection policy; log summary skip reasons and metadata; distinguish retrieval-ready work from answer-synthesis dependencies; validate necessity of hard edges; remove the scheduler wave barrier; calibrate leaf and internal concurrency separately. Do not change provider, question wording, retry behavior, or frozen extraction prompts as part of this review.
