# Jurisynth retrieval ablation

## Design

- Cases: 8 frozen, AI-adjudicated valid natural text questions.
- Upstream state: previously captured Super Query Interpreter outputs replayed identically; zero NIM calls.
- KG-only: structured Oxigraph assertions + E-R/community guidance; no chunks/tables/images.
- Chunk-only: direct chunk FAISS only; no structured KG/tables/images.
- Hybrid: structured assertions + direct chunks; no tables/images.
- Contradiction detection, leaf answer generation, and final synthesis were not invoked.
- Strict answer-bearing success requires the frozen expected chunk. Expected-source coverage requires any evidence from the frozen expected document.
- Frozen manifest SHA-256: `a428d7b74fecc5dbf60238d7e033917cede15d1768c488eb33fc8aa2bbfb1c6a`.

## Aggregate results

| Metric | KG-only | Chunk-only | Hybrid |
| --- | ---: | ---: | ---: |
| Expected-source coverage | 12.5% | 75.0% | 75.0% |
| Strict answer-bearing coverage | 0.0% | 62.5% | 62.5% |
| Provenance-complete cases | 100.0% | 100.0% | 100.0% |
| Weak/empty/error rate | 37.5% | 100.0% | 37.5% |
| Mean retrieval latency (s) | 19.621 | 0.287 | 20.749 |
| Median retrieval latency (s) | 13.757 | 0.287 | 9.442 |
| P95 retrieval latency (s) | 53.373 | 0.323 | 65.741 |

## Case-level comparison

| Case | KG-only source / gold / evidence / status / s | Chunk-only source / gold / evidence / status / s | Hybrid source / gold / evidence / status / s |
| --- | --- | --- | --- |
| `global_natural_001` | 0 / 0 / 4 / success / 10.135 | 0 / 0 / 8 / weak / 0.286 | 0 / 0 / 12 / success / 4.172 |
| `global_natural_002` | 0 / 0 / 4 / success / 5.165 | 1 / 1 / 8 / weak / 0.310 | 1 / 1 / 12 / success / 9.120 |
| `global_natural_005` | 0 / 0 / 0 / empty / 1.347 | 0 / 0 / 8 / weak / 0.271 | 0 / 0 / 8 / weak / 3.402 |
| `global_natural_006` | 0 / 0 / 2 / success / 18.195 | 1 / 1 / 8 / weak / 0.254 | 1 / 1 / 10 / success / 9.764 |
| `global_natural_007` | 0 / 0 / 0 / empty / 40.298 | 1 / 1 / 8 / weak / 0.297 | 1 / 1 / 8 / weak / 79.772 |
| `global_natural_009` | 0 / 0 / 0 / empty / 60.413 | 1 / 1 / 8 / weak / 0.262 | 1 / 1 / 8 / weak / 39.684 |
| `global_natural_010` | 0 / 0 / 24 / success / 4.032 | 1 / 1 / 8 / weak / 0.288 | 1 / 1 / 32 / success / 1.656 |
| `global_natural_011` | 1 / 0 / 2 / success / 17.380 | 1 / 0 / 8 / weak / 0.330 | 1 / 0 / 10 / success / 18.425 |

## Complementarity

- KG-only strict wins over chunk-only: none.
- Chunk-only strict wins over KG-only: ['global_natural_002', 'global_natural_006', 'global_natural_007', 'global_natural_009', 'global_natural_010'].
- Strict hybrid-only wins: none.
- Hybrid regressions: none.
- Hybrid had both evidence channels populated: ['global_natural_002', 'global_natural_006', 'global_natural_010', 'global_natural_011'].

## Statistical caution

- KG-only expected-source Wilson 95% CI: [0.0224, 0.4709].
- Chunk-only expected-source Wilson 95% CI: [0.4093, 0.9285].
- Hybrid expected-source Wilson 95% CI: [0.4093, 0.9285].
- Total measured retrieval wall time: 325.264 seconds; provider attempts and retries: 0.

## Interpretation boundaries

This is a controlled retrieval ablation on a small, curated set. It measures source and strict frozen-chunk recovery, not legal-answer accuracy. Claims and final answers were deliberately not generated because doing so would require stochastic provider calls or an unfrozen judge, confounding the retrieval-only independent variable. Chunk-only weak statuses reflect the current production status contract, which requires structured/table strength or structured corroboration for `success`; this ablation did not change that behavior.
