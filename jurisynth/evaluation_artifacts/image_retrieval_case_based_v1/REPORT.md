# Jurisynth image retrieval and expansion component evaluation

This is a case-based, reused-frozen, zero-NIM evaluation. Caption retrieval, path resolution, local expansion-contract invocation, live provider inference, and semantic usefulness are reported separately.

## Corpus and existing-gold inventory

- Indexed images: **27647**.
- Distinct source documents: **2876**.
- Defensible image-primary cases: **1**.
- **complex smokes:** Images were auxiliary/incidental rather than clean image-primary gold; not scored.
- **fixtures:** Validate local contracts only; not used as benchmark cases.
- **global acceptance image primary:** One legitimate frozen query with exact document and image ID gold; used.
- **global natural candidate packet:** No defensible image-primary gold cases.
- **image sidecars:** 27,647 captioned images with production FAISS vectors and path/provenance metadata.
- **prior live image smokes:** Two successful Nano Omni expansion diagnostics exist, but their generic prompts do not define unique global-retrieval gold; not scored.

## Gold and query policy

- The sole case is the unchanged global acceptance `image_primary` query with exact document and image-ID gold.
- No new query, paraphrase, weak caption-derived case, or post-retrieval alternate was created.
- This result is descriptive evidence about one legitimate case, not a corpus-level accuracy estimate.

## Stage A — caption/index retrieval

| Metric | Result |
|---|---:|
| Recall@1 | 0.000 |
| Recall@3 | 0.000 |
| Recall@5 | 0.000 |
| Recall@10 | 0.000 |
| MRR | 0.0000 |
| Correct-document Recall@10 | 0.000 |
| Alternate-valid recoveries | 0 |
| Mean / median latency | 0.0281 / 0.0281 s |
| P95 / worst latency | 0.0281 / 0.0281 s |
| Peak RSS | 629.6 MB |

## Stage B — vision expansion

- Images eligible after production-cutoff retrieval: **0**.
- Gold paths resolved locally: **1**; failures: **0**.
- Local recording-client attempts: **0**; contract successes: **0**.
- Image-byte deliveries to recording client: **0**.
- Returned expansions attached: **0**.
- Live provider attempts/successes: **0 / 0**.
- Semantic usefulness was not assessed because no live vision description was generated.

## Failure audit

- `expected_image_below_top_100`: 1
- `expected_file_absent_from_disk`: 0
- `path_resolution_failure`: 0

## Interpretation

The evaluation can establish whether the one frozen image-primary target is caption-retrievable and whether its corrected aggregate path resolves. It cannot establish corpus-wide image recall or vision-description quality. No deterministic path/index-presence defect is inferred unless the corresponding counts are non-zero.

The frozen query addresses an image by document ID and image number, while the dense index represents its visual caption. Its miss therefore suggests an identifier-to-caption retrieval mismatch for this case, not index corruption. Once a candidate is supplied, the corrected path contract is operational; prior live smoke captures suggest expansion can be useful, but they are not part of this evaluation's scored evidence.

Production code, image captions, FAISS artifacts, embeddings, thresholds, ranking, scoping, and prior evaluations were not modified.
