# Jurisynth ablation expansion feasibility audit

This was a read-only audit. No retrieval was run, no LLM was called, and no production or gold artifact was changed.

## 1. Current ablation

The current set contains eight natural-semantic questions and no structured or mixed cases:

- `global_natural_001`
- `global_natural_002`
- `global_natural_005`
- `global_natural_006`
- `global_natural_007`
- `global_natural_009`
- `global_natural_010`
- `global_natural_011`

All eight have exact expected document/chunk gold and captured Super Query Interpreter outputs. Their eight gold document/chunk targets are unique. None overlaps the assertion-200, assertion held-out-100, direct-chunk-40, or batch-0009 pilot targets.

## 2. Reusable asset inventory

| Source | Total | Eligible | Main exclusion or caveat |
| --- | ---: | ---: | --- |
| Global natural packet | 20 | 8, all already current | 3 need revisions without matching interpreter captures; 6 rejected joins; 3 table-primary |
| Batch-0009 natural pilot | 3 | 3 cases / 2 unique targets | `natural_001` and `natural_002` share one chunk; frozen interpreter behavior must be deterministically reconstructed |
| Assertion development benchmark | 200 | 0 | Every query is an artificial quoted subject-predicate probe |
| Assertion held-out benchmark | 100 | 0 | Same artificial template; held-out result must remain untouched |
| Controlled chunk benchmark | 40 | 0 | Same artificial subject-predicate template |
| Natural chunk corroboration | 14 | 8, all already current | Remaining 3 text cases require revision; 3 have table gold |
| Temporary-Super acceptance suite | 8 | 5 | Dependent case leaks prior hybrid upstream answer; table/image cases are modality-primary |
| Stabilization gates | 5 | 0 net-new | Text cases duplicate acceptance/Q003 targets; one table-primary case |
| Organized/messy complex smokes | 2 | 0 | No frozen provision/chunk gold; both are paraphrases of one scenario |
| Formal table benchmark | 20 | 0 | Table-primary |
| Image benchmark | 1 | 0 | Image-primary |

## 3. Expansion candidates

| Case | Source | Regime | Gold | Expected source | Replayability | Overlap/caveat |
| --- | --- | --- | --- | --- | --- | --- |
| `global_natural_001` | Current ablation | Natural | Exact chunk | `L_1994001EN.01000101/chunk_50` | Ready zero-NIM | Previously used in global and chunk runs |
| `global_natural_002` | Current ablation | Natural | Exact chunk | `L_2008289EN.01000101/chunk_48` | Ready zero-NIM | Previously used in global and chunk runs |
| `global_natural_005` | Current ablation | Natural | Exact chunk | `L_2011282EN.01000101/chunk_271` | Ready zero-NIM | Previously used in global and chunk runs |
| `global_natural_006` | Current ablation | Natural | Exact chunk | `L_2016294EN.01000101/chunk_164` | Ready zero-NIM | Previously used in global and chunk runs |
| `global_natural_007` | Current ablation | Natural | Exact chunk | `L_2015343EN.01000101/chunk_129` | Ready zero-NIM | Previously used in global and chunk runs |
| `global_natural_009` | Current ablation | Natural | Exact chunk | `L_2011127EN.01000101/chunk_8` | Ready zero-NIM | Previously used in global and chunk runs |
| `global_natural_010` | Current ablation | Natural | Exact chunk | `L_2007345EN.01000101/chunk_39` | Ready zero-NIM | Previously used in global and chunk runs |
| `global_natural_011` | Current ablation | Natural | Exact chunk | `L_2017175EN.01000101/chunk_157` | Ready zero-NIM | Previously used in global and chunk runs |
| `natural_001` | Batch-0009 pilot | Natural | Exact chunk | `L_2011065EN.01000101/chunk_6` | Deterministic reconstruction | Same target as `natural_002` |
| `natural_002` | Batch-0009 pilot | Natural | Exact chunk | `L_2011065EN.01000101/chunk_6` | Deterministic reconstruction | Same target as `natural_001` |
| `natural_003` | Batch-0009 pilot | Natural | Exact chunk | `L_2018268EN.01005301/chunk_3` | Deterministic reconstruction | Revised and frozen before its recorded retrieval run |
| `simple_ai_act` | Acceptance suite | Natural | Document only | `L_202401689EN` | Ready zero-NIM | AI Act target repeats in three other smoke cases |
| `frozen_q003` | Acceptance suite | Mixed | Document only | `L_202401689EN` | Ready zero-NIM | Eight leaves share broad document-level gold |
| `parallel_ai_act_gdpr` | Acceptance suite | Mixed | Two documents | AI Act + GDPR | Ready zero-NIM | AI Act leaf overlaps `simple_ai_act` |
| `cross_ai_act_ivdr` | Acceptance suite | Mixed | Two documents | AI Act + IVDR | Ready zero-NIM | AI Act document repeats |
| `negative_nonexistent_instrument` | Acceptance suite | Mixed/control | Absence | No positive source | Ready zero-NIM | Cannot enter positive source-coverage denominator |

The three revised global-natural questions (`003`, `004`, `008`) are not ready: their exact revised wording has no matching frozen Query Interpreter output and would require a new LLM call. The dependent acceptance case is not fair to replay because its second-leaf interpretation includes the historical hybrid answer from the first leaf.

## 4. Expansion options

### Uniform exact-gold ceiling

Ten cases are available with comparable exact document/chunk gold:

`global_natural_001`, `global_natural_002`, `global_natural_005`, `global_natural_006`, `global_natural_007`, `global_natural_009`, `global_natural_010`, `global_natural_011`, `natural_001`, `natural_003`.

This is methodologically clean, but it remains 10/10 natural-semantic and therefore does not solve the channel-balance concern.

### Option A — strongest practical expansion

Fifteen cases:

`global_natural_001`, `global_natural_002`, `global_natural_005`, `global_natural_006`, `global_natural_007`, `global_natural_009`, `global_natural_010`, `global_natural_011`, `natural_001`, `natural_003`, `simple_ai_act`, `frozen_q003`, `parallel_ai_act_gdpr`, `cross_ai_act_ivdr`, `negative_nonexistent_instrument`.

- Regimes: 11 natural, 0 structured, 4 mixed.
- Gold: 10 exact chunks, 4 document-only, 1 absence control.
- Zero-NIM replay: 100%.
- Exact captured interpreter output: 13/15 (86.7%).
- Deterministic reconstruction: 2/15 (13.3%).

This set must be reported in separate gold strata. A pooled answer-bearing coverage percentage would be invalid.

### Option B — most balanced existing set

Ten cases:

`global_natural_002`, `global_natural_005`, `global_natural_009`, `global_natural_011`, `natural_001`, `natural_003`, `frozen_q003`, `parallel_ai_act_gdpr`, `cross_ai_act_ivdr`, `negative_nonexistent_instrument`.

- Regimes: 6 natural, 0 structured, 4 mixed.
- Gold: 6 exact chunks, 3 document-only, 1 absence control.
- Zero-NIM replay: 100%.
- Exact captured interpreter output: 8/10 (80%).
- Deterministic reconstruction: 2/10 (20%).

This is more balanced in wording, but it is not an expansion of all eight current cases and it confounds query regime with gold granularity.

## 5. S/P probe verdict

The assertion-200, assertion held-out-100, controlled chunk-40, and earlier assertion-ablation-40 datasets are not defensible additions. Every inspected query uses the same form:

> According to the source, what is stated about '[gold subject]' in relation to '[gold predicate]'?

That wording directly exposes the gold E-R anchors. Feeding its deterministic subject and predicate concepts to structured retrieval intentionally activates exact E-R/conjunctive lookup, while chunk retrieval receives an unnatural query. It would create an artificial KG advantage—the opposite bias—not balance the natural set. Because the template is uniform, there is no representation-neutral subset to salvage without rewriting questions, which this audit forbids.

Natural questions with evidence represented in the KG do exist in the batch-0009 pilot and acceptance suite, but their reusable gold is either exact chunk-only or document-only; no existing balanced pool has both natural wording and frozen assertion-plus-chunk answer-bearing gold.

## Recommendation

**Keep the current 8-case ablation.**

The existing assets can technically produce 15 cases, but only by mixing incompatible gold granularities while remaining strongly natural-heavy. The uniformly scored ceiling is 10 and remains entirely natural. The only large structured pools are artificial S/P probes that would bias the KG arm. Expanding now would increase `n` without answering the methodological concern that motivated the audit.
