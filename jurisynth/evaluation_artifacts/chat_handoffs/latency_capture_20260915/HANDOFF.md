# Jurisynth latency capture and replay hand-off

Date analysed: 15 September 2026  
Run model: `nvidia/nemotron-3-ultra-550b-a55b`  
Purpose: isolate live planning/interpretation latency from local global-KG retrieval latency without changing production prompts, request timeouts, output limits, or retry behavior.

## Executive answer: were leaf queries executed?

There are three different operations that must not be conflated:

1. **Leaf planning:** yes. The current workflow produced seven leaves (`q001`–`q007`) and dependency edges.
2. **Agentic leaf execution:** no. The diagnostic deliberately stopped the normal workflow at `execute_leaves`. It did not retrieve or generate answers for the seven-node plan, did not run the scheduler, and did not synthesize a report.
3. **Standalone retrieval of one selected leaf:** yes. The fully materialized text of `q003` was interpreted once by NIM, then replayed through the global Retrieval Mechanism twice: baseline and `no_three_hop`. These were retrieval-only runs. No leaf-answer LLM was called.

The selected `q003` ordinarily depends on `q001` and `q002`. Those dependency leaves were not executed, so the replay request has empty `dependency_claims` and `dependency_substitutions`. This makes the replay valid for measuring retrieval on the explicit `q003` wording, but **not** a complete reproduction of runtime `q003` after upstream answers.

## Experiment boundaries

- Live capture ran normal Conversation Intake, Task Analysis, QCompiler translation, Semantic Dependency Planning, and one Query Interpretation.
- It did not load the KG and did not answer any leaf.
- Replays reused the exact captured 14 entity concepts and 9 relation concepts. They made zero NIM calls.
- Both replays used four E-R shards and ran in separate processes. Each was process-cold; OS cache state was not controlled.
- LLM community merging and vision expansion were suppressed by the diagnostic replay. Caption search retained the production opt-in gate.
- Timings are instrumented and nested. Nested stages overlap and must not be summed as independent totals.
- Evidence quality below is a preliminary inspection, not legal-expert adjudication.

## Live capture timeline

Total wall time: **1,887.50 s (31.46 min)**.

| Stage | Wall time | API outcome |
|---|---:|---|
| Conversation Intake | 167.13 s | success, attempt 1 |
| Task Analysis | 453.51 s | 503 after 165.95 s; retry succeeded in 286.45 s |
| QCompiler AST | 203.52 s | success, attempt 1 |
| Semantic Dependency Planning | 456.26 s | 503 after 208.56 s; retry succeeded in 245.77 s |
| `q003` Query Interpretation | 605.61 s | 504 after 302.18 s; retry succeeded in 301.89 s |

This was five logical NIM operations and eight physical HTTP attempts. Three physical attempts ended in HTTP failures: two 503s and one 504. Approximately 1,881.3 seconds were spent inside API attempts; retry backoffs totalled only about 4.6 seconds. Local orchestration overhead during capture was therefore negligible. The capture establishes that **live NIM calls and their failed attempts dominated this run's pre-retrieval latency**. It does not distinguish provider queueing/generation from network read latency because the 503/504 exception chains contain no lower-level transport subtype.

The request used provider-default output length and no per-request timeout. Successful usage:

- Intake: 700 prompt / 219 completion tokens.
- Task analysis: 651 / 203.
- QCompiler: 827 / 536.
- Dependency planner: 652 / 92.
- Query interpreter: 555 / 860.

The long waits are not explained by unusually large prompt token counts alone.

## Planned AST / dependency graph

```text
q001 ─┬─> q003 ─────> q007
      ├─> q004         ▲
      └───────────────>│
q002 ─┬─> q003 ───────>│
      └─> q005 ─> q006
```

Exact dependencies:

- `q001`: none
- `q002`: none
- `q003`: `q001`, `q002`
- `q004`: `q001`
- `q005`: `q002`
- `q006`: `q005`
- `q007`: `q001`, `q002`, `q003`

This hand-off does not re-adjudicate whether those semantic dependencies are justified. The raw seven leaf texts and constraints are in `capture/planned_leaves.json`.

## Local retrieval replay

| Measurement | Baseline | `no_three_hop` |
|---|---:|---:|
| Retrieval iteration | 77.77 s | 70.77 s |
| Whole process through completed replay | 109.99 s | 99.64 s |
| E-R matcher | 43.71 s | 43.15 s |
| Four-shard index work, inclusive | 43.05 s | 42.53 s |
| Shard loads (40 loads) | 21.33 s | 21.02 s |
| FAISS shard searches (40 searches) | 8.17 s | 8.04 s |
| Community selection | 12.90 s | 11.50 s |
| Two-hop traversal | 16.96 s | 13.28 s |
| Chunk search | 0.26 s | 0.25 s |
| Table search | 0.18 s | 0.17 s |

Both runs returned:

- status `success`;
- 67 evidence items, 66 distinct source chunk pairs, and 5 table evidence rows;
- 18 bounded paths, no conjunctive matches, and no escalation beyond `normal`;
- identical evidence bundles, including identical retrieval metadata;
- approximately 2.35 GiB process RSS at completion.

### Important three-hop result

**Neither run invoked three-hop traversal.** Baseline reported `three_hop_path_count: 0` and has no `three_hop` timing span. Consequently, the seven-second difference cannot be attributed to disabling three-hop; it is ordinary run/cache/system variation between two process-cold executions. This pair is not evidence that the `no_three_hop` policy is faster for this request.

### Main local latency findings

The local bottleneck is not chunk/table similarity search. E-R matching consumed about 43 seconds, with ten sharded searches causing all four shards to be loaded each time (40 loads). Shard loading alone took about 21 seconds. Community selection took another 11–13 seconds, and two-hop traversal took 13–17 seconds. These are concrete optimization candidates, but this one capture does not authorize a production change.

## Modality and community behavior

- **Tables:** table retrieval ran and returned five rows in roughly 0.18 seconds. Inspection indicates all five are irrelevant to the legal question (rail TSI placement procedure, medicinal-product variation, and AIF marketing material). This channel added noise, not useful support, for `q003`.
- **Images:** the image operation was scheduled, but the actual image search returned immediately with zero hits because the request did not satisfy the image opt-in/visual-keyword gate. Image expansion did not run.
- **Communities:** community selection ran and returned three leaf communities plus their LCA/orientation region. Average tree distance was 3.0. The deterministic orientation artifact was produced and marked non-authoritative.
- **Lazy Community Summarizer:** did not trigger. The recorded decision was `threshold_not_met` with four input communities and average distance 3.0. No community-summary NIM call occurred.
- **Contradiction/NLI:** did not run. Contradiction detection belongs to downstream reasoning/report work, which this retrieval-only diagnostic intentionally omitted.

## Preliminary evidence-quality inspection

The direct chunk channel performed encouragingly for the selected leaf:

- Seven of eight direct chunk matches came from the AI Act document `L_202401689EN`.
- They include answer-bearing text from Articles 16–17 and 22–26: provider, authorised representative, importer, distributor, value-chain/provider-role, and deployer obligations, as well as post-market/conformity material.
- One of eight direct matches was an irrelevant finance-law passage about AIF “pre-marketing,” showing lexical confusion around “pre-market.”

The structured assertion channel appears much weaker:

- It selected 60 items after reducing 1,584 pre-filter candidates to 213 coverage-filtered candidates.
- Source-document counts are dominated by unrelated merger/case identifiers and other instruments; the AI Act appears primarily through the direct chunk results.
- The successful status reflects evidence quantity/coverage rules, not demonstrated legal precision.

Thus the correct preliminary conclusion is: **direct chunk retrieval found highly useful AI Act evidence, while structured and table retrieval introduced substantial noise.** A legal answer was not generated, and the 67-item bundle has not been fully relevance-labelled.

## Questions for Chat's second opinion

1. Does the capture support removing or consolidating one of the duplicate planning authorities (QCompiler dependencies versus Semantic Dependency Planner), given that API stages dominate wall time? Treat this as a proposed controlled comparison, not permission to edit production behavior.
2. For local retrieval, should the next isolated experiment target repeated shard deserialization/batching before changing traversal depth?
3. What is the most defensible way to score the mixed bundle: channel-level precision/recall, answer-bearing source recall, and ranked utility separately?
4. Should table retrieval be made more strongly conditional for non-tabular legal questions, given five fast but irrelevant hits here?
5. How should `q003` be replayed later with authentic `q001`/`q002` dependency claims without rerunning a full hour-scale report?

## Included files

- `capture/`: complete live capture checkpoints, raw interpretation output, events, exact request, and planned leaves.
- `baseline/`: complete zero-API baseline events, configuration, result, and evidence bundle.
- `no_three_hop/`: corresponding comparison files.
- `tooling/`: diagnostic source and usage documentation needed to interpret experimental boundaries.

No `.env`, API key, credential, model cache, or global KG artifact is included.
