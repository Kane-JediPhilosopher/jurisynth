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
(one request attempt per call, so a rate-limit result returns promptly), use
the local `.env` file and run:

```powershell
$env:JURISYNTH_RUN_LIVE_NIM = '1'
& $JurisynthPython -m pytest jurisynth\agentic_reasoner\tests\test_live_nim.py -q -s
```

Do not put keys in commands, source files, logs, or version control. An NVIDIA
service overload is expected to produce an xfail in that smoke suite; it is not
evidence of a model or parsing defect.

For an auditable single smoke result that survives a noisy terminal session:

```powershell
& $JurisynthPython -m jurisynth.run_live_nim_smoke `
  --output jurisynth\run_outputs\nim_live_smoke.json
```

The JSON records the configured model, success fields, or a sanitised service
status. It never records a key.

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

## Global corpus build (GCP/high-memory machine)

All 437 completed batch graphs are now recorded in
`jurisynth/global_artifacts/manifest.json`; the global N-Quads file is at
`jurisynth/global_artifacts/graph/jurisynth_graph.nq`. The latter was built by
streaming, not by loading all RDF into RAM.

The current Community Graph implementation uses RDFLib and igraph and does
materialise the completed graph. Do **not** run it on this 16-GB laptop merely
because disk space is available. On a GCP machine with at least 48 GB available
RAM and enough additional disk for indexes, run:

```powershell
& $JurisynthPython -m jurisynth.build_global_community `
  --graph jurisynth\global_artifacts\graph\jurisynth_graph.nq `
  --destination jurisynth\global_artifacts\community `
  --minimum-available-gb 48
```

It produces the Community Graph, hierarchy, deterministic non-authoritative
orientation descriptors, batched E-R FAISS indexes, and build metadata. The
command refuses to begin if the available memory check fails.

The Community Graph build above remains a high-memory GCP task.  In contrast,
global *retrieval* can run locally after a one-time, disk-backed preparation;
no network service is needed.  Run these commands once on the device that will
query the corpus (they refuse to overwrite an existing store):

```bash
python -m jurisynth.build_global_chunk_metadata
python -m jurisynth.build_global_oxigraph
```

The second command streams the N-Quads source into a local RocksDB-backed
Oxigraph store.  Thereafter, execute an end-to-end global query directly:

```bash
python -m jurisynth.run_global_smoke "What obligations apply to a data controller?"
```

Global E-R loading defaults to `JURISYNTH_ER_INDEX_MODE=auto`: it chooses a
normal RAM load only when free memory exceeds the E-R file size plus a 2 GB
reserve (`JURISYNTH_ER_INDEX_RESERVE_GB`). The present corpus uses FAISS
`IndexFlatIP`; mmap does **not** reduce its resident memory. Exact 2-, 3-, and
4-way disk-backed shard artifacts are available under
`community/er_index/shards/`. When the monolithic index is not affordable,
auto mode selects the smallest complete shard set that fits the reserve; this
is currently 2 shards. Searches remain exact but load one shard at a time, so
they are slower and deliberately serialized to keep concurrent leaves within
the memory budget. Set `JURISYNTH_ER_INDEX_MODE=sharded` and optionally
`JURISYNTH_ER_SHARD_COUNT=3` (or `4`) to force a specific configuration.
Use `JURISYNTH_ER_INDEX_MODE=memory` only when enough RAM is available.

To reproduce the shard artifacts and local agreement measurements:

```powershell
& $JurisynthPython -m jurisynth.build_er_shards --shards 2 3 4
& $JurisynthPython -m jurisynth.benchmark_er_shards baseline `
  --output jurisynth\run_outputs\er_shard_baseline.json
& $JurisynthPython -m jurisynth.benchmark_er_shards sharded --shard-count 2 `
  --output jurisynth\run_outputs\er_shard_benchmark_2.json
```

The FastAPI interface remains an optional *localhost* UI adapter. It is not a
hosted deployment requirement.

## Thesis-safe limitations

- The batch-0009 pilot and global corpus checks are separate empirical scopes;
  report each run's actual scope and denominator, not an assumed global result.
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
- Global Community Graph, E-R, table and image artifacts are available. Live
  complex-query validation and labelled quality calibration remain separate work.
- Jurisynth provides evidence-grounded information support, not legal advice or
  a guarantee of legal correctness.

## Optional contradiction scoring and explanations

The deterministic detector remains the default. Set
`JURISYNTH_CONTRADICTION_SCORER=nli` to use the CPU NLI CrossEncoder and
`JURISYNTH_NLI_THRESHOLD=0.95` for the provisional synthetic threshold.
The separate 20-pair synthetic holdout returned precision 0.714, recall 1.0,
and F1 0.833: four non-conflicts were falsely flagged. This is not legal-domain
validation and is not a reason to enable it by default.

Set `JURISYNTH_CONFLICT_EXPLANATIONS=1` to request evidence-linked, strict-schema
explanations from the configured reasoning model. Optional
`JURISYNTH_CONFLICT_BATCH_SIZE` defaults to 10. Explanation failure preserves
the original warnings and allows report synthesis to continue. The explanation
does not override the NLI score or adjudicate legal correctness.

Reproduce the synthetic explanation component smoke on default Nemotron Ultra:

```powershell
& $JurisynthPython -m jurisynth.run_conflict_explanation_smoke
```

The successful pilot took 31.790 seconds for NLI and 99.316 seconds for Ultra.
It identified a direct contradiction and explained why a temporal NLI false
positive was compatible. These are synthetic component checks, not legal QA.

## Bounded unattended smoke retries

Versions 7–10 already have preserved outputs and must not be overwritten.
V10 was explicitly authorized with no smoke deadlines:
`python -m jurisynth.run_bounded_global_smokes --version 10 --query-timeout-seconds 0 --passed-format-output jurisynth/run_outputs/structured_output_smoke_v4.json`.
Use a new version number for subsequent authorized runs.
It first retests messy-query compilation/concept interpretation without global
indices, then runs messy and organized global smokes serially if format and RAM
guards pass, unless a successful component result is explicitly reused. V9 disabled the HTTP timeout (CLI
`--request-timeout-seconds 0` maps to SDK `timeout=None`), while retaining a
900-second async query deadline and an independent 930-second process watchdog.
Transient errors remain retried within an enabled query deadline. At the owner's
request, V10 disables both the overall query deadline and the process watchdog;
the RAM guard and owned-process cleanup on runner interruption remain enabled.
Runs can therefore persist indefinitely until completed or explicitly stopped.
The default Agentic Reasoner/API configuration is unchanged.

Inspect `run_outputs/bounded_global_smokes_v8.json` and the per-run JSON/logs.
V8 stopped at the format gate: AST generation succeeded, but concept
interpretation timed out and the overall 900-second deadline cancelled it.
No global smoke was started by that run.
V9 keeps prompts, schemas, token limits, context and retry behavior unchanged.
V9's component passed in 588.504 seconds after two HTTP 503s. The following
global messy run consumed most of its deadline on intake (including HTTP 504)
and analysis, then cancelled AST generation before a response arrived. Organized
was paused for RAM. V10 reuses the passed component gate and restarts the two
global cases serially without changing production prompts or retry settings.
Retry/failure logs now include elapsed attempt time and nested exception class
names, without exception messages or request secrets. An underlying ReadTimeout
still cannot by itself distinguish provider generation delay from network delay.
A stale `running` output without a matching process is an interrupted run,
not evidence of continuous execution or a provider error. Do not infer API
429s, corpus absence or legal-answer failure without relevant logged evidence.

## Offline reviewed NLI evaluation

Owner-requested output-budget change: the Reasoner shared NIM client and
retrieval ImageExpander now omit outbound `max_tokens`/`max_completion_tokens`.
Legacy internal adapter arguments are accepted but not transmitted or enforced
by the shared NIM client. Omission uses provider defaults, not unlimited output;
provider-default truncation remains possible and has not yet been live-tested.
KG construction's separate completion utilities are unchanged. Forty local
client/report/interpreter/compiler/image tests passed after this patch.
The v10 retry/AST/retrieval follow-up is packaged under
`evaluation_artifacts/leaf_execution_handoff_v3/CHAT_LEAF_EXECUTION_FOLLOWUP.zip`.

Run `python -m jurisynth.run_reviewed_nli_evaluation` once for the frozen
90-pair corrected AI-adjudicated dataset. It uses cached CPU weights only,
two threads and batches of four, and refuses to overwrite an existing output
directory. Reports are under `evaluation_artifacts/reviewed_nli_evaluation_v1`.
Forward three-class scores use the existing development/locked-test split;
reverse scores are diagnostic only. No thresholds or production defaults are
changed. Send `CHAT_NLI_ERROR_REVIEW.md` to Chat for qualitative error review.
Do not describe synthetic AI adjudication as expert gold or a subsequently
revised observed test set as an untouched holdout.

The completed v1 evaluation had no input truncation (maximum 151 of 512 tokens).
Test macro-F1 was 0.891, with contradiction precision 0.909 and recall 0.833.
The fixed symmetric 0.95 diagnostic had precision 1.0 but recall 0.5 on test;
this is not an adopted default. Aggregate gates do not replace qualitative
scope review. The combined importer/compiler/client/evaluation regression
suite passed 33 tests after this run. Send
`evaluation_artifacts/CHAT_CALIBRATION_ERROR_REVIEW_v1.zip` to Chat for the
14 NLI disagreements and six selected development-only retrieval diagnostics.
