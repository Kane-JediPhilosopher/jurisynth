# Jurisynth: organized vs. messy AI-medical live-smoke hand-off

## Purpose and controls

This is a diagnostic comparison of two semantically equivalent, complex AI-medical legal questions run through the frozen production Jurisynth pipeline, using **NVIDIA NIM Nemotron Super** as a temporary compatibility model. It is not an accuracy benchmark for Nemotron Ultra.

Both runs used the repaired production-v2 artifacts and identical frozen retrieval, QCompiler, Query Interpreter, ranking, scheduling, community, modality, and retry settings. No system changes were made between them. The fresh 100-case held-out assertion test has **not** been sampled or inspected.

Artifacts:

- Organized run: `jurisynth/run_outputs/global_complex_ai_medical_organized_super_20260917.json`
- Organized reasoning log: `jurisynth/reasoning_logs/global_smoke_2223.jsonl`
- Messy run: `jurisynth/run_outputs/global_complex_ai_medical_messy_super_20260917.json`
- Production artifact root: `jurisynth/global_artifacts_source_uri_v2`

## Headline result

The organized run completed successfully, with seven leaves, no failed leaves, no retrieval exceptions, 37 generated claims, and a final report. It took **521.75 s** (8m 42s). The messy run completed in **281.5 s** (4m 42s), with four leaves and zero generated claims.

The organized wording materially improved decomposition and surfaced one substantive, grounded-looking AI Act obligations answer. It did **not** recover most of the other answer-bearing provisions needed for the full scenario. The final report appropriately retained uncertainty rather than silently filling those gaps.

Classification: **partial**.

## Decomposition and scheduling

### Organized query

QCompiler produced seven atomic leaves, one for each substantive issue:

1. economic-operator roles and multiple-role occupancy;
2. high-risk classification;
3. provider/importer/distributor/deployer obligations;
4. role change after modification, retraining, fine-tuning, intended-purpose change, or update;
5. AI Act-GDPR interaction;
6. tensions/overlap between AI Act and GDPR;
7. post-deployment false-negative incident responsibilities.

All dependency sets were empty. The deterministic scheduler began q001–q004 together, then admitted q005–q007 as execution slots freed. This is correct parallel execution for an AST with no declared dependencies; there was no artificial sequential dependency chain.

### Messy query

QCompiler condensed the scenario into four independent leaves:

1. operator/provider status and hospital modification;
2. high-risk classification;
3. AI Act-GDPR data-reuse interaction;
4. performance-degradation/incident responsibility.

All four were also independent.

### Comparison

The organized formulation preserved **seven explicit issue units** versus four in the messy version. It directly separated obligations, role-change, and cross-regime-tension questions that the messy version merged or omitted. This is a decomposition-fidelity improvement, not a retrieval-policy change.

## Organized per-leaf outcome

| Leaf | Retrieval status | Evidence items | Table candidates | Result |
|---|---:|---:|---:|---|
| q001 roles | weak | 8 | 5 | No role definitions/role-combination rule recovered; abstained. |
| q002 high-risk | weak | 10 | 5 | Some AI Act/high-risk material surfaced, but no scenario-applicable criterion; five claims were returned but the answer remained conditional/insufficient. |
| q003 operator obligations | weak | 17 | 5 | **Substantive result:** detailed provider/importer/distributor/deployer obligations, including cited AI Act articles. 32 claims generated. It is still conditional on high-risk/operator-role applicability. |
| q004 role change after modification | success | 21 | 5 | No answer-bearing rule for role change recovered; abstained. |
| q005 AI Act-GDPR interaction | success | 17 | 5 | No answer-bearing interaction/lawful-basis provisions recovered; abstained. |
| q006 regulatory tensions | weak | 24 | 5 | No answer-bearing AI Act/GDPR overlap provisions recovered; abstained. |
| q007 false-negative incident scenario | success | 23 | 5 | Importer/distributor risk-notification material surfaced, but not the full monitoring/corrective-action/serious-incident sequence; abstained. |

The `success` labels in q004/q005/q007 are retrieval-contract statuses, not proof that the evidence was answer-bearing for the whole legal question. This run shows why evidence-level review remains necessary.

No image-primary evidence was reported. Table candidates were returned by every leaf, but none was central to the final legal conclusions.

## Answer coverage and provenance

### What improved over the messy run

- The messy run generated no claims and abstained on all four broad leaves.
- The organized q003 leaf retrieved enough material for a specific obligations answer, covering quality management, documentation/logging, conformity assessment, declaration/CE marking/registration, importer checks/document retention, distributor checks, and deployer impact-assessment duties.
- q007 retrieved a narrower but relevant subset about importer/distributor risk notification.
- The final synthesis preserved the important limitation: q003 obligations cannot be applied conclusively without evidence that the system is high-risk and that the actors fit the statutory roles.

### What remained missing in both forms

- statutory role definitions and multi-role rule;
- high-risk criterion tying medical-device status, intended purpose, and conformity assessment together;
- the provider-role change rule for substantial modification/retraining/fine-tuning;
- GDPR Articles 6/9, purpose-limitation/further-processing, and automated-decision-making rules in the requested interaction;
- a legally grounded AI Act/GDPR overlap analysis;
- full post-market monitoring, corrective-action, recall/withdrawal, and serious-incident sequence.

Thus the organized version obtained better **coverage of one core issue**, not a complete answer to the six/seven substantive issues.

## Latency and provider behavior

Organized scheduler retrieval durations (wall-clock per leaf, overlapping where parallel):

- q003: 166.2 s
- q004: 176.3 s
- q002: 182.0 s
- q007: 27.9 s
- q005: 45.3 s
- q001: 460.5 s
- q006: 270.2 s

The run made 22 completed NIM calls and scheduled 12 retries. One Query Interpreter `retrieval_concepts` request suffered a provider-side 504 after about 302 s, then succeeded on retry in about 1.25 s. No leaf failed and no terminal provider failure occurred.

Latency therefore reflects both long local/global retrieval work for high-coverage leaves and materially unstable provider time for interpretation/generation. The trace does not support attributing the total 8m42s solely to either the provider or retrieval layer.

## Community and contradiction observations

The compact run artifact does not preserve a per-leaf community-selection trace or raw Query Interpreter concepts; the reasoning log preserves lifecycle events and evidence IDs, but not those inner payloads. Therefore, do not infer that community selection was absent from this run merely because the compact artifact does not expose it.

Contradiction detection emitted a very large set of identifiers after the seven leaves completed. The compact artifact does not provide a claim-by-claim adjudication linking each identifier to a final conclusion. It should be treated as an operational trace, not evidence that 199 genuine legal contradictions were found.

## Failure localization

No decomposition, schema, scheduler, or terminal provider defect occurred.

The dominant correctness limitation is **answer-bearing source coverage/grounding for the complex AI Act–GDPR–medical-device scenario**. It appears upstream of final synthesis for the unresolved issues: the system generally abstained when those materials were absent. q003 demonstrates that when relevant provisions do reach the EvidenceBundle, the leaf generator can produce a detailed answer with claims.

The comparison does not isolate a systematic defect in the frozen Retrieval Mech itself, because it has not established whether the missing provisions are represented and reachable under the intended document metadata/instrument scope. It also does not justify changing the frozen architecture from one difficult scenario.

## Recommendation

**A — do not reopen a subsystem from this comparison. Keep the system frozen and proceed to the pre-authorized held-out 100-case component retrieval test**, using the confirmed production-v2 artifact fingerprint. Treat this live run as a useful end-to-end grounded-abstention/coverage diagnostic, not as a formal legal-QA score.

## Questions for Chat review

1. Does the organized-vs-messy comparison support treating q003 as a decomposition/coverage win, while preserving a `partial` overall classification?
2. Does the distinction between retrieval-contract `success` and answer-bearing coverage need to be made more explicit in the thesis evaluation protocol?
3. Is any *single* demonstrated defect strong enough to reopen one frozen subsystem before the held-out component test? The current evidence says no.
