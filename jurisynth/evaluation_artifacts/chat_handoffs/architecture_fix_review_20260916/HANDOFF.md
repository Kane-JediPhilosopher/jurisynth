# Jurisynth controlled architecture-fix review hand-off

Date: 2026-09-16  
Prepared for: ChatGPT second-opinion review  
Status: implemented controlled comparison; **not** a broad legal-quality evaluation

## What changed

The project owner approved a staged simplification plan with reversible changes:

1. Verify the repaired `global_artifacts_source_uri_v2` corpus locally.
2. Remove the Semantic Dependency Planner LLM from production execution.
   QCompiler is now the only LLM authority for genuine hard dependencies.
3. Replace wave-barrier scheduling with deterministic event-driven DAG execution.
4. Consolidate Conversation Intake + Task Analysis into one structured call while
   preserving public workflow events/contracts.
5. Tighten the Query Interpreter to the current leaf and prevent it from inventing
   likely answer content as retrieval concepts.
6. Batch all unmatched entity terms into one E-R vector search and all unmatched
   relation terms into one vector search, preserving exact-label priority.
7. Instrument structured-retrieval stage costs and add a conservative
   chunk/structured corroboration status signal.
8. Add two-pass table/image retrieval: global FAISS first, then a direct-chunk
   source-document scope; deduplicate by stable resource identity and record each
   pass origin. Vision expansion is limited to two candidates that clear the
   existing relevance threshold.
9. Inspect—but do not redesign—the repaired v2 Community Graph.

The KG extraction prompts, serialized global KG, model/provider, retry policy,
output-token policy, and provenance structures were not changed.

## Results to verify

Artifact fingerprint:
`6166222635c5fbc55001f1f763a4196c0ef7f917a54c5da068164e82ad301c84`

### Logical LLM calls

Complex planning before leaf execution changed from four logical calls to two:

- before: Conversation Intake → Task Analysis → QCompiler → Semantic Dependency Planner;
- after: combined Intake/Analysis → QCompiler.

Transport retries remain independently logged. This is a code-path count, not a
claim that provider latency has been eliminated.

### Local retrieval

- Repaired-v2 frozen-concept q003 baseline: 53.360 s.
- After E-R batching: 36.656 s.
- After final two-pass modality integration: 33.046 s.
- The code-only comparison retained the same 67 evidence IDs and 69 source-chunk
  identities.
- Final q003 interpretation reduced 14 entity + 9 relation concepts to 8 entity
  + 4 relation concepts.
- E-R matches fell from 185 to 101; pre-filter evidence from 1,595 to 860;
  selected structured evidence from 60 to 26.
- Final q003 local replay: 22.790 s, 33 evidence items, 32 unique source chunks.
- All eight direct chunk hits remained; seven are AI Act excerpts.
- Items supported by the AI Act document increased from 7 to 14.

The final q003 live interpretation used one provider request, no retry, and took
34.085 s. Companion checks also completed in one request each:

- simple importer leaf: 5 concepts, 11.019 s;
- named Article 25 leaf: 9 concepts, 32.687 s.

These timings are single smoke measurements and are not provider benchmarks.

### Modalities

For q003, the source-scoped second pass used only the two documents independently
surfaced by strong direct chunks and cost about 116 ms. It found no source-local
table/image items. Five low-scoring global table candidates remained. They appear
irrelevant, but were not filtered because a reviewed correct Lakeland Dairies
table row scored only 0.376 while the q003 rows scored 0.26–0.33. Applying the
shared 0.55 threshold would remove valid table evidence as well as noise.

### Communities

- 1,263,436 hierarchy/descriptor records, four levels, zero missing parents.
- Level counts: 316,635 / 315,603 / 315,599 / 315,599.
- There are 315,599 roots, so hierarchy compression is weak.
- q003 selected three leaf communities plus one LCA; all resolve in v2.
- q003 average tree distance = 3.0; maximum = 4.
- Lazy summarisation did not trigger.
- With selector `top_n=3`, orientation contains at most three seeds + one LCA,
  making the six-community trigger unreachable. The separate average-distance
  trigger remains reachable but q003 stayed below its 4.0 threshold.

No Leiden or summariser threshold was changed.

### Tests

Final bounded suite: **152 passed, 6 optional skips, 0 failures**.

The suite covers combined intake/analysis, QCompiler translation and dependency
contracts, event-driven scheduling, genuine dependencies, independent leaves,
E-R batching, RDF retrieval, escalation/status logic, modality origins and
deduplication, image expansion gating, community orientation, and diagnostic
replay contracts.

## Requested review

Please review the supplied current source and evidence, then answer in this order:

1. **Dependency authority:** Is removing the Semantic Dependency Planner from the
   production path correct, or does any current QCompiler adapter behavior still
   require a second semantic planner? Identify a concrete failing AST if so.
2. **Scheduler:** Does the event-driven DAG scheduler preserve required failure,
   cycle, and substitution semantics while allowing dependants to begin as soon
   as their own prerequisites finish?
3. **Combined intake:** Is the one-call `request_analysis` schema sufficiently
   strict without losing necessary clarification/context? Flag contract regressions.
4. **Interpreter:** Is the final prompt defensibly leaf-scoped, or does it now risk
   losing an essential retrieval anchor? Assess the three captured outputs rather
   than concept count alone.
5. **E-R batching:** Does batching preserve per-concept top-k, best-per-URI,
   exact-label bypass, ordering, and sharded memory behavior?
6. **Status logic:** Is direct-chunk/structured-source corroboration a defensible
   success signal, or can it suppress necessary escalation in a concrete case?
7. **Two-pass modalities:** Is chunk-anchored document scoping acceptable? Recommend
   the smallest defensible table gating/reranking experiment without inventing a
   universal cutoff from one positive and one negative example.
8. **Community diagnostics:** Does the topology indicate a likely hierarchy-build
   problem, merely low graph compressibility, or insufficient evidence? Should the
   unreachable count trigger be removed, lowered, or left deferred pending cases?
9. **Evidence claims:** Check whether the reported before/after comparisons are
   genuinely like-for-like and whether the answer-bearing/provenance non-regression
   claim is supported by the included outputs.
10. Return each finding as **approve**, **revise**, **revert**, or **defer**. Propose
    only small, isolated next steps. Do not recommend a new agent, verifier LLM,
    server-first design, broad LexGLUE run, extraction-prompt change, or community
    redesign without concrete evidence from this package.

## Package map

- `docs/`: approved controlled plan, implementation report, and current checklist.
- `current/reasoner/`: current production reasoner files and focused tests.
- `current/retrieval/`: current production retrieval files and focused tests.
- `current/shared/`: public contracts and production workflow wiring.
- `diagnostics/`: current diagnostic code.
- `results/`: compact q003 before/intermediate/after results, community diagnostic,
  accepted live concept captures, and simple/named-instrument captures.
- `fixtures/`: the two companion RetrievalRequest inputs.

No API keys, `.env` files, virtual environments, full corpus, graph store,
multi-gigabyte FAISS index, image binaries, or provider credentials are included.
The package is for code/evidence review, not for executing the global corpus.
