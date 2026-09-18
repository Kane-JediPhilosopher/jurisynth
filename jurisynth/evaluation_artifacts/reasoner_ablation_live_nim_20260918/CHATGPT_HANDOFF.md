### Jurisynth End-to-End Reasoner Validation — Handoff

**Purpose**

- Case count: 4 selected from the existing frozen eight-case retrieval ablation.
- Selection was diagnostic rather than success-oriented: two strict chunk hits with hybrid `weak → success`, one correct-document/structured-support case without exact-gold recovery, and one strict all-arm miss.
- This is a qualitative live-NIM follow-up. The controlled zero-NIM eight-case retrieval ablation remains the primary experiment and was not rerun.

**Execution setup**

- Provider/model: NVIDIA NIM, `nvidia/nemotron-3-super-120b-a12b`.
- Decoding: temperature `0`, top-p `0.000001`, reasoning effort `none`; no request timeout; unchanged production retry policy.
- Live NIM was used for leaf-answer generation and final synthesis.
- Frozen direct-route analysis, leaf query, contextual facts, constraints, and captured Super Query Interpreter concepts were replayed identically across arms.
- QCompiler was not invoked because all four frozen cases are single-leaf direct routes.
- Contradiction detection was disabled identically across arms because exhaustive CPU NLI is unrelated to the retrieval-source independent variable.
- Deterministic community selection/orientation remained enabled in KG-containing arms; it was absent from chunk-only. Lazy NIM community summarization was disabled as in the formal ablation.

**Cases**

- `global_natural_002`: chunk-only recovered the strict gold; hybrid added four assertions and changed retrieval status from `weak` to `success`.
- `global_natural_010`: strong corroboration stress case; strict chunk recovery plus 24 structured assertions and the same `weak → success` change.
- `global_natural_011`: both channels recovered the correct document; KG supplied two road-load assertions although no arm recovered the exact gold chunk.
- `global_natural_005`: difficult strict all-arm miss, selected to inspect abstention and fabrication behavior.

**Per-arm aggregate summary**

- KG-only:
  - runs completed: 4/4;
  - final report objects produced: 4/4;
  - substantive leaf answers: 0/4;
  - abstention/insufficient-evidence: 4/4;
  - mean supported claims: 0.00;
  - mean mechanically unsupported claims: 0.00;
  - provenance-complete bundles: 4/4;
  - expected-source recovery: 1/4;
  - strict gold-chunk recovery: 0/4;
  - mean/median retrieval latency: 4.763s / 3.955s;
  - total/median wall time: 37.213s / 9.332s;
  - provider retries/failures: 0/0.
- Chunk-only:
  - runs completed: 4/4;
  - final report objects produced: 4/4;
  - substantive leaf answers: 4/4, including one partially supported answer;
  - abstention/insufficient-evidence: 0/4;
  - mean supported claims: 2.25;
  - mean mechanically unsupported claims: 0.00;
  - provenance-complete bundles: 4/4;
  - expected-source recovery: 3/4;
  - strict gold-chunk recovery: 2/4;
  - mean/median retrieval latency: 0.059s / 0.057s;
  - total/median wall time: 54.292s / 13.943s;
  - provider retries/failures: 2/0; both retries were HTTP 503s in `global_natural_010`.
- Hybrid:
  - runs completed: 4/4;
  - final report objects produced: 4/4;
  - substantive leaf answers: 2/4;
  - abstention/insufficient-evidence: 2/4;
  - mean supported claims: 0.75;
  - mean mechanically unsupported claims: 0.00;
  - provenance-complete bundles: 4/4;
  - expected-source recovery: 3/4;
  - strict gold-chunk recovery: 2/4;
  - mean/median retrieval latency: 4.136s / 2.713s;
  - total/median wall time: 44.847s / 10.690s;
  - provider retries/failures: 1/0; the retry was an HTTP 503 in `global_natural_005`.
- Total measured wall time across all 12 runs: 136.352s. There were 3 transient HTTP 503 retries and no terminal provider failure.

**Case-level findings**

- `global_natural_002`:
  - KG-only retrieved four unrelated Small Claims Procedure assertions and correctly abstained.
  - Chunk-only recovered the frozen answer-bearing chunk and produced three supported claims covering interlocutory injunctions, seizure/delivery up, and precautionary seizure.
  - Hybrid recovered the same chunk plus four unrelated assertions and produced two supported chunk-only claims.
  - Hybrid did not cite structured assertions and did not materially improve the answer. Its internal `success` label did not propagate into cross-representation support.
- `global_natural_010`:
  - KG-only retrieved 24 unrelated customs assertions from other instruments and abstained.
  - Chunk-only recovered the frozen gold chunk and correctly stated that verification may occur at random, through risk analysis, or when reasonable doubts exist.
  - Hybrid recovered the same gold chunk and 24 assertions but abstained.
  - Deterministic root cause: the leaf generator globally sorted the 32 evidence items and retained 12; all 12 were score-1.0 structured assertions, so zero chunks reached the leaf-answer prompt. The loss occurred after retrieval, not in retrieval.
- `global_natural_011`:
  - KG-only recovered the correct document but only two assertions about transmission selection and road-load determination; it abstained.
  - Chunk-only retrieved eight road-load chunks and produced a partially supported five-claim answer about speed, torque, time, sampling frequency, and the torque-meter method. It did not recover the frozen chunk containing the requested elapsed-time, wind, and ambient-temperature measurements.
  - Hybrid received the same eight chunks plus the two structured assertions but abstained. All ten items fit the prompt budget, so this is not the same truncation defect as case 010; the added assertions appear non-answer-bearing and likely increased caution/noise.
- `global_natural_005`:
  - KG-only returned no evidence and abstained.
  - Chunk-only and hybrid both missed the frozen designated source but retrieved alternate-edition chunks containing the same 8% / 0.63 mm wood-flour rule. Both produced one supported claim citing those chunks.
  - Because alternates were not added to the frozen gold, this remains a strict miss and is not post-hoc rescored.

**Cross-representation corroboration**

- Hybrid bundles containing both chunks and assertions: 3/4 cases.
- Claims citing both representations: 0.
- Cases where assertions reinforced chunk evidence at claim level: 0.
- Cases where the added structured channel changed leaf behavior: 2, both negatively—from supported/partially supported chunk-only answers to hybrid abstentions.
- Cases where it changed final-answer behavior: 2, both negatively.
- Clearly harmful structured-noise cases: 2 (`global_natural_010`, `global_natural_011`).
- Cases where structured evidence was present but simply ignored: 1 (`global_natural_002`).
- Cases where chunk-only remained sufficient for a substantive response: 4/4, though only 2/4 recovered the frozen strict gold.

**Interpretation**

- Strongest evidence that hybrid corroboration matters: none at claim level in this fixture. No claim cited both representations.
- Strongest evidence against the current implementation: hybrid recovered the same strict gold as chunk-only in `global_natural_010`, but a modality-unaware 12-item leaf-prompt budget excluded every chunk and caused abstention. In `global_natural_011`, non-answer-bearing assertions also changed a partial answer into abstention.
- The earlier retrieval-level `weak → success` effect did not yield stronger claims or answers. It was neutral in one case and harmful in two.
- This does not prove chunk-only is universally superior, does not measure legal correctness, and does not justify changing retrieval thresholds. It reveals a downstream mixed-evidence selection bottleneck that prevents fair use of hybrid evidence.

**Integrity**

- Production code changed: no.
- Prompts changed: no.
- Gold changed: no.
- Retrieval thresholds changed: no.
- Prior formal ablation rerun: no.

**Files produced**

- `jurisynth/evaluation_artifacts/reasoner_ablation_live_nim_20260918/selected_cases_manifest.json`
- `jurisynth/evaluation_artifacts/reasoner_ablation_live_nim_20260918/structured_comparison.json`
- `jurisynth/evaluation_artifacts/reasoner_ablation_live_nim_20260918/JURISYNTH_END_TO_END_REASONER_VALIDATION.md`
- `jurisynth/evaluation_artifacts/reasoner_ablation_live_nim_20260918/CHATGPT_HANDOFF.md`
- `jurisynth/evaluation_artifacts/reasoner_ablation_live_nim_20260918/logs/`
- `jurisynth/evaluation_artifacts/reasoner_ablation_live_nim_20260918/runs/`

**Recommended next step**

- Review the deterministic mixed-evidence prompt-budget defect before any further end-to-end comparison; do not reopen frozen retrieval semantics.
