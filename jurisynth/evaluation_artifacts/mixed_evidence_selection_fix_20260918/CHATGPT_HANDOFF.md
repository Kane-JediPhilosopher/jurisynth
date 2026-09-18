### Jurisynth Mixed-Evidence Selection Fix — Handoff

**Root cause confirmed**

- Old selection algorithm: globally sort all assertion and chunk `EvidenceItem` records by descending relevance, descending structural score, then evidence ID; keep the first 12; apply the character budget in that order.
- Assertion scores come from E-R match/structured retrieval, while chunk scores are dense cosine similarities. They are not calibrated as one common cross-representation scale.
- In `global_natural_010`, 24 score-1.0 assertions outranked all eight chunks. The hybrid EvidenceBundle contained the gold chunk, but the leaf prompt contained 12 assertions and zero chunks.
- Affected interface: `EvidenceBundle.evidence_items` → `EvidenceGroundedLeafGenerator._bounded_evidence()` → leaf-answer model prompt.
- Provenance and claim linking use stable evidence IDs, not list positions.

**Fix implemented**

- New deterministic rule: rank assertions and chunks independently using the existing ranking key.
- Prompt budget remains 12 evidence items.
- When both representations exist, reserve one third of capacity for assertions and one third for chunks: four slots each with the default budget.
- Interleave reserved items deterministically, then fill the remaining four slots using the strongest unselected evidence regardless of representation.
- If one modality has fewer than four items, unused capacity is recycled by the other.
- Single-modality bundles retain the original global top-12 behavior.
- The one-third reservation was derived from two active textual representations plus an open competitive third. No quota sweep or optimization against the four validation cases occurred.

**Scope**

- Production files changed:
  - `jurisynth/agentic_reasoner/llm.py`
  - `jurisynth/agentic_reasoner/tests/test_llm.py`
- Evaluation harness updated for prompt-selection observability:
  - `jurisynth/run_reasoner_ablation_live_validation.py`
- Retrieval files changed: no.
- Prompts changed: no.
- Retrieval scores or thresholds changed: no.

**Tests**

- Added focused coverage for:
  - assertion-heavy hybrid bundles;
  - chunk-heavy hybrid bundles;
  - assertion-only and chunk-only parity;
  - unused-capacity recycling;
  - deterministic order;
  - evidence-ID and source provenance preservation;
  - unchanged prompt limit.
- Focused leaf-generator suite: 23 passed, 0 failed.
- Adjacent workflow/reporting/retrieval-contract suite: 41 passed, 0 failed.
- Total: 64 passed, 0 failed.
- Determinism: passed.
- Provenance preservation: passed.

**Before/after live validation**

- All 12 post-fix case-arm runs completed.
- Every case-arm returned the exact same retrieval evidence IDs before and after, confirming that retrieval semantics were unchanged.
- Provider instability was higher post-fix: 17 transient retries, all recovered; zero terminal failures. Wall-time changes therefore are not treated as evidence of selector performance.
- Mechanically unsupported substantive claims: zero. The only no-reference post-fix claim was explicitly labelled `insufficient_evidence`, not presented as a supported proposition.

- `global_natural_002`:
  - Pre-fix hybrid: 4 assertions and 8 chunks reached the prompt; gold retained; supported answer; 2 claims; no abstention.
  - Post-fix hybrid: 4 assertions and 8 chunks; gold retained; supported answer; 4 supported claims; no abstention.
  - Every post-fix claim cited chunks only. Assertions did not corroborate the claims.
  - Wall time: 11.453s before, 23.479s after, with two post-fix provider retries.

- `global_natural_010`:
  - Retrieval in both runs: 24 assertions plus 8 chunks, including the frozen gold chunk.
  - Pre-fix hybrid prompt: 12 assertions, 0 chunks; gold absent; insufficient evidence; zero claims; abstention.
  - Post-fix hybrid prompt: 8 assertions, 4 chunks; designated gold still absent because it ranked seventh among chunks; supported answer; 4 supported claims; no abstention.
  - The claims cited four higher-ranked chunk records carrying the same verification rule: `C_85bd49292d3dff02`, `C_85b753f5a06c58aa`, `C_dcfca3694386094b`, and `C_e86f11166c4f7dda`.
  - No claim cited an assertion.
  - Wall time: 8.980s before, 15.440s after, with two post-fix provider retries.

- `global_natural_011`:
  - Pre-fix hybrid prompt: 2 assertions and 8 chunks; gold absent; insufficient evidence; zero claims; abstention.
  - Post-fix: the same 2 assertions and 8 chunks; gold absent; insufficient evidence; one explicit insufficient-evidence statement; abstention unchanged.
  - No supported claim was produced.
  - This case did not suffer modality starvation. Its failure remains a distinct retrieval relevance/noise issue.
  - Wall time: 14.487s before, 30.935s after, with three post-fix provider retries.

- `global_natural_005`:
  - Pre-fix and post-fix hybrid prompt: 0 assertions and 8 chunks; designated gold absent.
  - Both runs produced one supported chunk-cited claim and did not abstain.
  - Alternate-edition chunks supplied the 8% / 0.63 mm rule; gold was not changed post hoc.
  - Wall time: 9.927s before, 15.577s after, with no post-fix retries.

**global_natural_010**

- The original complete chunk-starvation defect is fixed: prompt composition changed from 12 assertions / 0 chunks to 8 assertions / 4 chunks, and the leaf changed from abstention to a four-claim supported answer.
- The designated gold chunk itself did not survive because it ranked seventh within the chunk channel. Equivalent higher-ranked chunks supported the answer.
- The quota was not retuned to force this particular gold into the prompt.

**global_natural_011**

- Behavior did not materially change.
- The prompt already contained all 2 assertions and 8 chunks before the fix, so starvation was never its cause.
- Its remaining failure appears distinct: the frozen answer-bearing chunk was not retrieved, and the structured assertions were not answer-bearing.

**Cross-representation result**

- Claims citing both modalities after the fix: 0.
- Cases where assertions actually corroborated chunks at claim level: 0.
- Assertions remained unused in `global_natural_002` and `global_natural_010`.
- Assertions remained primarily noise/non-answer-bearing context in `global_natural_011`.
- What changed downstream: formerly starved chunk evidence reached the `global_natural_010` leaf model, which changed from abstention to a supported answer.

**Integrity**

- Formal eight-case ablation rerun: no.
- Gold changed: no.
- Retrieval semantics changed: no.
- Quota tuned against evaluation cases: no.

**Interpretation**

- The fix supports the narrow claim that representation-aware prompt selection prevents deterministic exclusion of an entire retrieved textual representation.
- It does not establish general hybrid superiority, improved legal correctness, calibrated cross-representation scores, or statistically significant answer improvement.
- Claim-level assertion-plus-chunk corroboration remains unobserved.
- `global_natural_011` remains unresolved but reflects a different limitation, not a reason to retune the selection quota.
- No further architecture change is justified from this four-case rerun alone.

**Files produced**

- `jurisynth/agentic_reasoner/llm.py`
- `jurisynth/agentic_reasoner/tests/test_llm.py`
- `jurisynth/run_reasoner_ablation_live_validation.py`
- `jurisynth/evaluation_artifacts/reasoner_ablation_live_nim_20260918/`
- `jurisynth/evaluation_artifacts/reasoner_ablation_live_nim_20260918_postfix/`
- `jurisynth/evaluation_artifacts/mixed_evidence_selection_fix_20260918/before_after_comparison.json`
- `jurisynth/evaluation_artifacts/mixed_evidence_selection_fix_20260918/JURISYNTH_MIXED_EVIDENCE_SELECTION_FIX_20260918.md`
- `jurisynth/evaluation_artifacts/mixed_evidence_selection_fix_20260918/CHATGPT_HANDOFF.md`

**Recommended next step**

- Freeze this selector and assess it in grounded-QA evaluation; document `global_natural_011` separately rather than changing the allocation again.
