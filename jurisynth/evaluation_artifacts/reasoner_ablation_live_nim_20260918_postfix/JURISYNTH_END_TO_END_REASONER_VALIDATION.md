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
| kg_only | 4/4 | 4 | 4 | 0.5 | 0 | 4 | 13.614 | 5/0 |
| chunk_only | 4/4 | 4 | 0 | 3.25 | 0 | 4 | 16.236 | 5/0 |
| hybrid | 4/4 | 4 | 1 | 2.5 | 0.25 | 4 | 19.528 | 7/0 |

## Case comparison

### `global_natural_002`

Chunk-only recovered the strict gold; hybrid added assertions and changed retrieval status from weak to success.

- **kg_only:** retrieval `success`; source/gold False/False; 4 assertions + 0 chunks; leaf `insufficient_evidence` with 1 claims (0 mechanically unsupported); final=True; both-representations=False; wall=26.635s.
- **chunk_only:** retrieval `weak`; source/gold True/True; 0 assertions + 8 chunks; leaf `supported` with 4 claims (0 mechanically unsupported); final=True; both-representations=False; wall=21.678s.
- **hybrid:** retrieval `success`; source/gold True/True; 4 assertions + 8 chunks; leaf `supported` with 4 claims (0 mechanically unsupported); final=True; both-representations=False; wall=23.479s.

### `global_natural_010`

Strong corroboration stress case: strict chunk recovery plus 24 structured assertions and a weak-to-success status change.

- **kg_only:** retrieval `success`; source/gold False/False; 24 assertions + 0 chunks; leaf `insufficient_evidence` with 0 claims (0 mechanically unsupported); final=True; both-representations=False; wall=5.891s.
- **chunk_only:** retrieval `weak`; source/gold True/True; 0 assertions + 8 chunks; leaf `supported` with 4 claims (0 mechanically unsupported); final=True; both-representations=False; wall=10.795s.
- **hybrid:** retrieval `success`; source/gold True/True; 24 assertions + 8 chunks; leaf `supported` with 4 claims (0 mechanically unsupported); final=True; both-representations=False; wall=15.44s.

### `global_natural_011`

Both channels recovered the correct document and the KG supplied a road-load assertion although no arm recovered the exact gold chunk.

- **kg_only:** retrieval `success`; source/gold True/False; 2 assertions + 0 chunks; leaf `insufficient_evidence` with 1 claims (0 mechanically unsupported); final=True; both-representations=False; wall=21.338s.
- **chunk_only:** retrieval `weak`; source/gold True/False; 0 assertions + 8 chunks; leaf `partially_supported` with 4 claims (0 mechanically unsupported); final=True; both-representations=False; wall=8.559s.
- **hybrid:** retrieval `success`; source/gold True/False; 2 assertions + 8 chunks; leaf `insufficient_evidence` with 1 claims (1 mechanically unsupported); final=True; both-representations=False; wall=30.935s.

### `global_natural_005`

Difficult all-arm strict miss used to test abstention and fabrication.

- **kg_only:** retrieval `empty`; source/gold False/False; 0 assertions + 0 chunks; leaf `insufficient_evidence` with 0 claims (0 mechanically unsupported); final=True; both-representations=False; wall=3.785s.
- **chunk_only:** retrieval `weak`; source/gold False/False; 0 assertions + 8 chunks; leaf `supported` with 1 claims (0 mechanically unsupported); final=True; both-representations=False; wall=22.76s.
- **hybrid:** retrieval `weak`; source/gold False/False; 0 assertions + 8 chunks; leaf `supported` with 1 claims (0 mechanically unsupported); final=True; both-representations=False; wall=15.577s.

## Integrity

- Production code changed: no.
- Prompts, gold, thresholds, ranking, scoping, communities, and retrieval semantics changed: no.
- Prior formal ablation rerun: no.
