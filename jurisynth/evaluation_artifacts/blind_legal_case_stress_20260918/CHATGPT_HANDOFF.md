### Jurisynth Blind Legal Case Stress Test — Handoff

**Design**

- Cases: 1.
- Selected case: *Bundesverband der Verbraucherzentralen und Verbraucherverbande v Planet49 GmbH*, C-673/17, ECLI:EU:C:2019:801.
- Selection rationale: compact factual dispute; central issues concern EU legislation present or referenced in Jurisynth (ePrivacy Directive, Directive 95/46 and GDPR); authoritative full judgment available; outcome could be withheld cleanly; no repository evidence that Jurisynth had previously been tuned against this case.
- Status: qualitative case study, not a statistical benchmark or court-prediction test.

**Sanitization**

- Retained: neutralized facts about a 2013 promotional registration, preselected analytics checkbox, opt-out mechanism, cookie identifier linked to registration data, advertising uses, missing duration/third-party details, forward-looking injunction and the four legal questions.
- Withheld: case name/number, operative order, who prevailed, the court's conclusions, holding-revealing paragraphs and editorial summaries.
- Leakage check: the packet did not quote the judgment or identify Planet49; it stated facts/issues without outcome language. Only `blind_case_packet.json` was read by the runner.
- Rubric frozen before inference: yes. SHA-256: `cf06298180db4bdfec4f8c5c8b7b8452edf0385af68e2d2d86519e97854b7e6f`.

**Execution**

- Provider/model: NVIDIA NIM, `nvidia/nemotron-3-super-120b-a12b`.
- Decoding: temperature 0; top-p 0.000001; reasoning effort none; provider-default output limit.
- Current post-fix mixed-evidence selector used: yes.
- Contradiction detector: disabled only for the official run after a faithful attempt generated 6,441 CPU-NLI pairs from 114 evidence items and remained in that local stage for over 30 minutes. The aborted trace was preserved; no detector code changed.
- Provider events: 16 attempts, 15 completed calls, one retried HTTP 503, zero terminal failures.
- Total wall time: 1,212.911 s (20.2 min). Completed NIM time: 60.303 s. Peak RSS: 2.54 GiB.

**Case 1**

- Case: Planet49, C-673/17.
- Legal issue: validity of preselected cookie consent; whether the ePrivacy rule depends on personal data; whether information must cover cookie duration and third-party access; temporal interaction of Directive 95/46, GDPR and ePrivacy.
- Held-out actual disposition: the Court held that a pre-ticked checkbox is not valid consent; Article 5(3) applies regardless of whether the stored/accessed information is personal data; and clear/comprehensive information includes cookie duration and whether third parties may access cookies. It also addressed the transition from Directive 95/46 to GDPR for the forward-looking action.
- Expected key rules: ePrivacy Articles 2(f) and 5(3), read with Directive 95/46/GDPR consent rules; GDPR information provisions relevant to duration/recipients; the 25 May 2018 repeal/replacement transition.
- Provisions/rules recovered: active affirmative consent and invalidity of pre-ticked boxes; repeal/replacement of Directive 95/46 by GDPR from 25 May 2018; identity of Directive 2002/58. The direct amended ePrivacy Article 5(3) provision, duration duty and third-party-access duty were not recovered.
- Key retrieved evidence: a structured assertion that pre-ticked boxes should not constitute consent; structured assertions about GDPR replacing Directive 95/46; original ePrivacy chunks, but not the answer-bearing 2009 amendment chunk.
- Representations contributing: assertions supplied the useful consent and repeal propositions; chunks contributed instrument text/title and one mixed-modality claim. Tables/images did not help.
- Claims: 4 total; 3 with explicit evidence; 1 without evidence; 2 assertion-only; 0 chunk-only; 1 assertion+chunk; all cited IDs resolved.
- Unsupported claims: the final overview asserted that the ePrivacy rule is independent of personal-data status even though q002 abstained and provided no supporting claim/evidence. The overview also overstated the temporal coexistence/application point beyond the retrieved support.
- Major omissions: direct amended Article 5(3) chain, cookie duration, third-party access and precise temporal/national-court qualification.
- Reasoning alignment: partial. Consent reasoning aligned; duration/third-party holdings were missed; one correct point was unsupported; temporal reasoning was overgeneralized.
- Outcome alignment: partial. The central preselected-checkbox direction matched; the personal-data holding appeared only as an unsupported synthesis assertion; two operative information holdings were absent.
- Provenance quality: strong for the three cited claims—all references resolved—but incomplete at the final-report level because one substantive overview proposition lacked claim/evidence support.
- Important failure stages: retrieval failure for the amended ePrivacy chunk; corpus/metadata and scope-parsing limitation for Directive 95/46; downstream synthesis inconsistency for q002; no evidence-selection starvation.

**Cross-representation findings**

- Claims supported by chunks only: 0.
- Claims supported by assertions only: 2.
- Claims supported by both: 1, but mainly for instrument identity/title rather than substantive corroboration.
- Useful table/image evidence: none; no successful image expansion was relevant.
- Modality interference: assertions added substantial irrelevant material, but the selector preserved chunks in every mixed bundle.
- Selector behavior: sensible. q001 selected 8 assertions/4 chunks; q002 4/8; q003 0/8; q004 3/9. The recent starvation defect did not recur.

**Overall interpretation**

- Demonstrated: valid blind/outcome-held-out execution; coherent four-leaf decomposition; traceable retrieval; grounded central consent claim; appropriate abstention on two unsupported issues; preserved provenance; deterministic mixed-modality representation.
- Failed: retrieval of the direct amended ePrivacy rule and two information duties; final synthesis consistency; efficient local execution (retrieval dominated the 20-minute run).
- Main origins: retrieval/source coverage plus downstream synthesis, not prompt-budget modality starvation and not provider instability.
- Does not establish: general legal accuracy, statistical reliability, hybrid superiority, outcome prediction, or that correct propositions without evidence count as grounded reasoning.

**Integrity**

- Production code changed: no.
- Prompts changed: no.
- Retrieval thresholds changed: no.
- Rubric changed after inference: no.
- Outcome visible during inference: no.

**Files produced**

- `jurisynth/evaluation_artifacts/blind_legal_case_stress_20260918/authoritative_sources.json`
- `jurisynth/evaluation_artifacts/blind_legal_case_stress_20260918/blind_case_packet.json`
- `jurisynth/evaluation_artifacts/blind_legal_case_stress_20260918/sealed_held_out_reference.json`
- `jurisynth/evaluation_artifacts/blind_legal_case_stress_20260918/frozen_rubric.json`
- `jurisynth/evaluation_artifacts/blind_legal_case_stress_20260918/evaluation_freeze_manifest.json`
- `jurisynth/evaluation_artifacts/blind_legal_case_stress_20260918/live_run/complete_run.json`
- `jurisynth/evaluation_artifacts/blind_legal_case_stress_20260918/live_run/reasoning.jsonl`
- `jurisynth/evaluation_artifacts/blind_legal_case_stress_20260918/live_run/system_trace.jsonl`
- `jurisynth/evaluation_artifacts/blind_legal_case_stress_20260918/live_run_aborted_cpu_nli/`
- `jurisynth/evaluation_artifacts/blind_legal_case_stress_20260918/structural_analysis.json`
- `jurisynth/evaluation_artifacts/blind_legal_case_stress_20260918/rubric_evaluation.json`
- `jurisynth/evaluation_artifacts/blind_legal_case_stress_20260918/case_comparison_report.md`

**Recommended next step**

- Trace, read-only, why the known amended ePrivacy Article 5(3) chunk never entered q001/q003 and why final synthesis promoted q002's abstained proposition; do not tune until those two failure paths are localized.
