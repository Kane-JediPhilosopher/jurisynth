# Jurisynth Pilot Runbook

This runbook is for the `batch_0009` thesis pilot. It is intentionally not a
claim that the complete 437-batch corpus has been aggregated or evaluated.

## Runtime

Use the confirmed Python 3.12 interpreter. The workspace virtual environment
is optional; do not rely on it unless it has been recreated against this
interpreter.

```powershell
$JurisynthPython = 'C:\Users\Roxas\AppData\Local\Programs\Python\Python312\python.exe'
& $JurisynthPython --version
```

The active pilot uses the locally cached `all-MiniLM-L6-v2` embedding model
(384 dimensions, normalized vectors), the persisted `batch_0009` N-Quads,
chunk FAISS index, raw table index, and the generated E-R indexes.

## Verify the non-live implementation

```powershell
& $JurisynthPython -m pytest jurisynth\agentic_reasoner\tests jurisynth\retrieval_mech\tests jurisynth\tests -q
```

Live NVIDIA calls are skipped by default. To opt into the bounded smoke suite
(maximum two attempts per call), use the local `.env` file and run:

```powershell
$env:JURISYNTH_RUN_LIVE_NIM = '1'
& $JurisynthPython -m pytest jurisynth\agentic_reasoner\tests\test_live_nim.py -q -s
```

Do not put keys in commands, source files, logs, or version control. An NVIDIA
service overload is expected to produce an xfail in that smoke suite; it is not
evidence of a model or parsing defect.

## Rebuild pilot E-R indexes

```powershell
& $JurisynthPython -m jurisynth.build_pilot_er_index `
  jurisynth\kg_construction_pipeline\output\batch_0009 `
  jurisynth\pilot_artifacts\batch_0009\er_index
```

The destination contains separate entity and relation FAISS indexes,
URI/label/community metadata, and a reproducibility manifest.

## Run the end-to-end pilot

```powershell
$JurisynthStamp = Get-Date -Format 'yyyyMMdd_HHmmss'
& $JurisynthPython -m jurisynth.main "What obligations apply to a data controller?" `
  --output "jurisynth\run_outputs\main_$JurisynthStamp.json"
```

This command uses the NVIDIA NIM values in
`jurisynth/agentic_reasoner/.env`, writes a JSONL reasoning log under
`jurisynth/reasoning_logs/`, and may wait through the production NIM retry and
backoff policy during a transient service error. Before the NIM call, Jurisynth
deterministically limits the prompt to 12 ranked evidence items, one source
excerpt per item, and a 50,000-character evidence payload. The complete
retrieval bundle remains available in the reasoning log; only the model-facing
view is bounded. The default CLI output is a compact summary, avoiding a giant
terminal dump. Add `--full-output` only together with `--output` when a
complete UTF-8 JSON export is truly needed.

## Run the local retrieval smoke evaluation

```powershell
& $JurisynthPython -m jurisynth.run_pilot_evaluation --limit 50
```

This writes URI-free generated cases, per-case outcomes, and aggregate
assertion-recall, entity/predicate recall, expected-assertion rank, and
provenance-validity metrics under
`jurisynth/evaluation_artifacts/`, plus a 20-item review queue that puts
misses/weak results first. It is a controlled retrieval smoke test, not a
held-out legal QA benchmark.

The default `subject-predicate` probe includes both the target subject and
predicate. To reproduce the old subject/object-only probe artifacts, pass:

```powershell
& $JurisynthPython -m jurisynth.run_pilot_evaluation --limit 50 --query-style legacy-subject-object
```

## Run the table-row retrieval smoke evaluation

```powershell
& $JurisynthPython -m jurisynth.run_table_evaluation --limit 20
```

This writes table/row recall separately from RDF assertion metrics. By default,
it uses short identifier/context questions derived from known rows. Use
`--query-style integrity` only for the older full-row echo probes. Neither mode
is a held-out legal-QA benchmark.

## Aggregate only completed batches

The aggregation functions are deliberately explicit and refuse to overwrite
existing outputs. Use them only after every selected batch has completed KG
construction and its embedding specifications are known to match.

```python
from pathlib import Path
from jurisynth.resource_aggregator import (
    EmbeddingSpec, discover_batch, build_manifest, write_manifest,
    merge_nquads, merge_chunk_indices,
    merge_table_artifacts, merge_image_stores,
)

spec = EmbeddingSpec("all-MiniLM-L6-v2", 384, normalized=True)
batches = [
    discover_batch(
        "batch_0009",
        processed_batch_dir="jurisynth/kg_construction_pipeline/output/batch_0009",
        source_batch_dir="eu_legislation/batch_0009",
        chunk_embedding=spec,
        table_embedding=spec,
    )
]
output = Path("jurisynth/aggregates/pilot")
output.mkdir(parents=True, exist_ok=True)
write_manifest(build_manifest(batches, workspace_root="."), output / "manifest.json")
merge_nquads(batches, output / "jurisynth_graph.nq")
merge_chunk_indices(
    batches,
    destination_index=output / "chunk_index.faiss",
    destination_metadata=output / "chunk_metadata.pkl",
)
merge_table_artifacts(batches, output / "tables")
merge_image_stores(batches, output / "images")
```

## Thesis-safe limitations

- The current empirical scope is `batch_0009`, not the complete corpus.
- Retrieval smoke cases are generated from known KG assertions; they validate
provenance and plumbing but are not a held-out legal QA benchmark.

## Inspect corpus coverage before a natural-language demonstration

Before interpreting a natural-language miss, check whether its defining terms
are represented in the pilot chunks or KG labels:

```powershell
& $JurisynthPython -m jurisynth.inspect_pilot_coverage `
  "data controller" GDPR "personal data" `
  --output jurisynth\evaluation_artifacts\coverage_data_controller.json
```

No lexical hit means the `batch_0009` pilot cannot establish coverage for that
term. It is not evidence that the complete corpus lacks the concept.
- The Community Graph and E-R indexes are pilot artifacts; global indexes need
  the merged complete KG.
- Jurisynth provides evidence-grounded information support, not legal advice or
  a guarantee of legal correctness.
