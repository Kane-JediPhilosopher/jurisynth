# Jurisynth live-NIM end-to-end retrieval-ablation follow-up

## Boundaries

- Qualitative follow-up only; the formal zero-NIM eight-case ablation was not rerun.
- Frozen direct-route analysis and Query Interpreter concepts were replayed identically across arms.
- Live NIM was used only for leaf-answer generation and final synthesis.
- Tables, images, lazy community summarization, and contradiction detection were disabled identically.
- Provider model: `nvidia/nemotron-3-super-120b-a12b`; temperature 0; top-p 0.000001; reasoning effort `none`.

## Aggregate

| Arm | Completed | Final answers | Abstentions | Mean claims | Mean unsupported | Provenance complete | Median wall (s) | Retries/failures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| kg_only | 4/4 | 4 | 4 | 0.25 | 0 | 4 | 9.332 | 0/0 |
| chunk_only | 4/4 | 4 | 0 | 2.5 | 0 | 4 | 13.943 | 2/0 |
| hybrid | 4/4 | 4 | 2 | 0.75 | 0 | 4 | 10.69 | 1/0 |

## Case comparison

### `global_natural_002`

Chunk-only recovered the strict gold; hybrid added assertions and changed retrieval status from weak to success.

- **kg_only:** retrieval `success`; source/gold False/False; 4 assertions + 0 chunks; leaf `insufficient_evidence` with 0 claims (0 mechanically unsupported); final=True; both-representations=False; wall=13.087s.
- **chunk_only:** retrieval `weak`; source/gold True/True; 0 assertions + 8 chunks; leaf `supported` with 3 claims (0 mechanically unsupported); final=True; both-representations=False; wall=11.463s.
- **hybrid:** retrieval `success`; source/gold True/True; 4 assertions + 8 chunks; leaf `supported` with 2 claims (0 mechanically unsupported); final=True; both-representations=False; wall=11.453s.

### `global_natural_010`

Strong corroboration stress case: strict chunk recovery plus 24 structured assertions and a weak-to-success status change.

- **kg_only:** retrieval `success`; source/gold False/False; 24 assertions + 0 chunks; leaf `insufficient_evidence` with 0 claims (0 mechanically unsupported); final=True; both-representations=False; wall=5.578s.
- **chunk_only:** retrieval `weak`; source/gold True/True; 0 assertions + 8 chunks; leaf `supported` with 1 claims (0 mechanically unsupported); final=True; both-representations=False; wall=21.33s.
- **hybrid:** retrieval `success`; source/gold True/True; 24 assertions + 8 chunks; leaf `insufficient_evidence` with 0 claims (0 mechanically unsupported); final=True; both-representations=False; wall=8.98s.

### `global_natural_011`

Both channels recovered the correct document and the KG supplied a road-load assertion although no arm recovered the exact gold chunk.

- **kg_only:** retrieval `success`; source/gold True/False; 2 assertions + 0 chunks; leaf `insufficient_evidence` with 1 claims (0 mechanically unsupported); final=True; both-representations=False; wall=15.27s.
- **chunk_only:** retrieval `weak`; source/gold True/False; 0 assertions + 8 chunks; leaf `partially_supported` with 5 claims (0 mechanically unsupported); final=True; both-representations=False; wall=16.423s.
- **hybrid:** retrieval `success`; source/gold True/False; 2 assertions + 8 chunks; leaf `insufficient_evidence` with 0 claims (0 mechanically unsupported); final=True; both-representations=False; wall=14.487s.

### `global_natural_005`

Difficult all-arm strict miss used to test abstention and fabrication.

- **kg_only:** retrieval `empty`; source/gold False/False; 0 assertions + 0 chunks; leaf `insufficient_evidence` with 0 claims (0 mechanically unsupported); final=True; both-representations=False; wall=3.278s.
- **chunk_only:** retrieval `weak`; source/gold False/False; 0 assertions + 8 chunks; leaf `supported` with 1 claims (0 mechanically unsupported); final=True; both-representations=False; wall=5.076s.
- **hybrid:** retrieval `weak`; source/gold False/False; 0 assertions + 8 chunks; leaf `supported` with 1 claims (0 mechanically unsupported); final=True; both-representations=False; wall=9.927s.

## Integrity

- Production code changed: no.
- Prompts, gold, thresholds, ranking, scoping, communities, and retrieval semantics changed: no.
- Prior formal ablation rerun: no.

## Comparative findings

- Chunk-only produced a substantive supported or partially supported leaf answer in all 4 cases. KG-only abstained in all 4. Hybrid answered 2 and abstained in 2.
- No hybrid claim cited both structured and chunk evidence. Cross-representation retrieval therefore did not become cross-representation claim support in this fixture.
- `global_natural_002`: chunk-only and hybrid both answered from chunks. The four structured assertions were unrelated and were not cited. Hybrid's internal `success` status produced no clear downstream benefit.
- `global_natural_010`: chunk-only answered correctly from the frozen gold chunk. Hybrid retrieved that same chunk, but 24 score-1.0 structured assertions occupied the leaf generator's 12-item evidence budget; no chunk reached the leaf prompt, and hybrid abstained.
- `global_natural_011`: chunk-only produced a partially supported response from retrieved road-load chunks. Hybrid saw the same eight chunks plus two structured assertions but abstained. The structured assertions did not supply the requested measurements and appear to have added noise.
- `global_natural_005`: KG-only correctly abstained. Chunk-only and hybrid both answered from alternate-edition chunks containing the 8% / 0.63 mm rule. The frozen designated source remained absent, so this is not reclassified as a strict-gold hit.
- Mechanically unsupported claims: zero in every arm. This validates evidence-reference integrity, not legal correctness.

## Deterministic defect — documented, not fixed

`EvidenceGroundedLeafGenerator._bounded_evidence` in `jurisynth/agentic_reasoner/llm.py` globally sorts mixed assertion and chunk evidence and retains only 12 items. In `global_natural_010`, the hybrid EvidenceBundle contained 24 structured assertions and 8 chunks, including the frozen gold chunk. The 12-item prompt view contained 12 structured assertions and 0 chunks. The failure occurred after retrieval, during evidence-to-prompt selection.

No code was changed because this evaluation prohibited tuning or fixes during the run.

## Interpretation

This four-case qualitative validation does not support the hypothesis that the current hybrid `weak → success` status change produces stronger downstream claims. It shows no claim-level cross-representation corroboration and two cases where adding structured evidence changed a non-abstaining chunk-only result into an abstention. One of those regressions has a deterministic prompt-budget cause; the other is consistent with irrelevant structured evidence making the model more cautious.

These findings do not prove chunk-only superiority or legal-answer correctness. They identify a downstream evidence-presentation bottleneck that prevents the current hybrid retriever's output from being tested fairly by the Reasoner.
