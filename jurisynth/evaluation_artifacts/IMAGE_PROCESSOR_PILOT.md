# Image Processor pilot — Batch 0009

## Scope

On 2026-09-04, the opt-in Image Processor was run on Batch 0009 using the
configured Nemotron 3 Nano Omni vision endpoint. The batch contained three
eligible JPEG artefacts, all from `L_2001222EN.01005301`.

## Outcome

- 3 of 3 image descriptions completed successfully.
- 3 of 3 descriptions were embedded with `all-MiniLM-L6-v2` (384 dimensions)
  and persisted in `eu_legislation/batch_0009/image_index/`.
- No 429 response or per-image API error was observed.
- Captions correctly identified the images as fishing-technique tables/scans.

## Interpretation

This validates configuration, image-payload handling, provenance records, and
per-batch FAISS persistence. It does **not** establish that NVIDIA rate limits
are independent across models: the pilot was sequential and did not overlap
with a Nemotron Ultra workload. It also does not establish corpus-wide caption
quality, latency, or cost.

## Guardrails adopted after inspection

The first output was accurate but sometimes overly transcription-heavy. The
processor now deterministically bounds model text before indexing: description
at 110 words and visible text at 80 words. These limits prevent visual OCR
from dominating auxiliary evidence retrieval; they are not a legal-content
summary.
