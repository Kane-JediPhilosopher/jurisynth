# Jurisynth mixed-evidence selection fix

## Root cause

`RetrievalMechanism` already returned stable, provenance-bearing assertion and chunk `EvidenceItem` records. The downstream `EvidenceGroundedLeafGenerator._bounded_evidence()` treated their relevance values as one common scale, globally sorted them by relevance, structural score, and evidence ID, then retained twelve.

Assertion relevance is derived from E-R match similarity and structural retrieval. Chunk relevance is dense cosine similarity. They are useful within their channels but are not calibrated cross-channel. In the pre-fix `global_natural_010` hybrid bundle, 24 score-1.0 assertions outranked all eight chunks. The twelve-item leaf prompt consequently contained no chunks even though retrieval had found the frozen gold chunk.

Evidence order never determines claim identity. Claims cite stable evidence IDs, and each selected record retains its original source document, chunk, and text.

## Minimal fix

The total item budget remains twelve. Evidence retains the legacy within-representation rank key.

When assertions and chunks both exist:

1. Reserve one third of the item budget for the strongest assertions.
2. Reserve one third for the strongest chunks.
3. Interleave reserved items deterministically so the character budget cannot put one entire representation last.
4. Fill remaining slots from the strongest unselected evidence regardless of representation.
5. Recycle any unused reservation.

With the default budget this means four reserved assertion slots, four reserved chunk slots, and four open slots. This follows from two active textual representations and the existing twelve-item budget; no quota sweep or case optimization was performed. Single-modality bundles retain the original top-twelve behavior.

## Tests

- Focused leaf-generator suite: 23 passed.
- Adjacent workflow, reporting, mechanism, and result-contract suite: 41 passed.
- Total: 64 passed, 0 failed.

Coverage includes assertion-heavy hybrid input, chunk-heavy hybrid input, single-modality parity, unused-capacity recycling, deterministic order, provenance preservation, and prompt-limit enforcement.

## Retrieval integrity

All twelve case-arm reruns returned exactly the same retrieval evidence IDs as the preserved pre-fix run. No retrieval file, score, threshold, index, top-k, community behavior, prompt, or gold annotation changed.

## Before and after

### `global_natural_002`

- Before hybrid prompt: 4 assertions and 8 chunks; frozen gold present.
- After: 4 assertions and 8 chunks; frozen gold present.
- Before/after leaf status: supported / supported.
- Claims: 2 / 4; every post-fix claim cited chunks only.
- Interpretation: no starvation existed. Differences in claim detail cannot be separated from live-model variability.

### `global_natural_010`

- Retrieval before and after: unchanged 24 assertions and 8 chunks, including the frozen gold chunk.
- Before hybrid prompt: 12 assertions, 0 chunks.
- After hybrid prompt: 8 assertions, 4 chunks.
- The designated frozen chunk was rank seven within the chunk channel and did not enter the four reserved slots. Four higher-ranked equivalent chunks did enter.
- Before: insufficient evidence, zero claims, abstention.
- After: supported answer, four supported claims, no abstention.
- All four claims cited chunk evidence. Assertions were not used as corroborating claim support.
- Result: the complete modality-starvation defect is fixed. No further quota tuning was performed to force the designated gold into the prompt.

### `global_natural_011`

- Before and after hybrid prompt: 2 assertions and 8 chunks.
- Frozen gold chunk absent from retrieval and therefore absent from the prompt.
- Before/after leaf behavior: insufficient evidence / insufficient evidence.
- The post-fix output contained one explicit insufficient-evidence statement with no substantive evidence claim.
- Result: this case is distinct from starvation. Available assertions were non-answer-bearing, while the answer-bearing chunk was never retrieved.

### `global_natural_005`

- Before and after hybrid prompt: 0 assertions and 8 chunks.
- Before/after: supported, one chunk-cited claim, no abstention.
- Single-modality behavior remained effectively unchanged.
- The designated source remained absent; alternate-edition chunks supplied the rule and were not post-hoc added to gold.

## Cross-representation result

No post-fix claim cited both assertions and chunks. The fix allowed chunk evidence to reach the model in the formerly starved case, but did not establish claim-level structured corroboration. Assertions remained unused in `global_natural_002` and `global_natural_010`, and remained non-answer-bearing noise in `global_natural_011`.

## Interpretation boundary

The result establishes that deterministic representation-aware selection prevents one retrieved text representation from being completely excluded by incomparable channel scores. It does not establish hybrid superiority, legal correctness, calibrated cross-modal scores, or statistically significant answer improvement.

No further architecture change is justified from this four-case rerun. The separate `global_natural_011` relevance/noise limitation should be documented and evaluated independently rather than addressed by changing this quota.
