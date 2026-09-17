# Jurisynth user manual — draft

> Status: developer documentation. The tested interactive demonstration uses
> Batch-0009; the completed 437-batch RDF aggregation requires a separate
> high-memory Community Graph/E-R indexing run, followed by a one-time local
> Oxigraph store build before global querying. Jurisynth
> is a research aid, not legal advice or a production legal-information service.

## 1. What Jurisynth does

Jurisynth combines a provenance-preserving RDF knowledge graph, chunk/table
retrieval, and an agentic reasoning workflow. A question is decomposed when
necessary, evidence is retrieved from the corpus, and the reasoner produces a
report whose claims point back to evidence identifiers and source chunks.

## 2. Before you start

- Use Python 3.12 and install the project requirements.
- Build a pilot E-R index after graph construction:

  ```powershell
  & $JurisynthPython -m jurisynth.build_pilot_er_index `
    jurisynth\kg_construction_pipeline\output\batch_0009 `
    jurisynth\pilot_artifacts\batch_0009\er_index
  ```

- Keep NVIDIA API keys in a local `.env` file. Never commit or paste keys into
  notebooks, logs, issue trackers, or this manual.

## 3. Ask a research question

Run a pilot query and save the compact result:

```powershell
& $JurisynthPython -m jurisynth.main "What obligations apply to a data controller?" `
  --output "jurisynth\run_outputs\question.json"
```

Open the JSON in an editor or render it into readable text:

```powershell
& $JurisynthPython -m jurisynth.render_pilot_output `
  jurisynth\run_outputs\question.json `
  jurisynth\run_outputs\question.txt
```

Read the answer as a research lead. Check the report's evidence references,
source chunks, and limitations before relying on it. An
`insufficient_evidence` result is an appropriate outcome when the pilot corpus
does not support the question.

## 4. Run the developer-preview web interface

Start the API in one terminal:

```powershell
& $JurisynthPython -m uvicorn jurisynth.server:app --reload --port 8000
```

Start the extracted Stitch/Vite front end in another terminal:

```powershell
Set-Location jurisynth\frontend\stitch_research_dossier
npm install
npm run dev
```

Open the Vite address printed by the second command (normally
`http://localhost:3000`). The UI is a developer preview and invokes a
server-side workflow runner; it must never expose an API key in browser code.
The AST is available after QCompiler completes. Retrieved evidence is still the
authoritative review surface; the UI does not turn a model answer into legal
advice.

For the Batch-0009 developer preview, the API serves an image only at
`/api/v1/images/{image_id}` when that exact ID is present in the batch's
`image_index/metadata.json`. It resolves the manifest path inside the approved
batch root and rejects arbitrary paths. The image modal labels all visual
material as auxiliary context, never as independent legal evidence.

The web interface is optional and runs only on `localhost`. The core pipeline
and global embedded RDF store can be queried directly from Python; neither
requires a hosted server.

## 5. Prepare and query the complete corpus locally

After copying the aggregated global artifacts to a device, prepare the
disk-backed store once. This trades disk space and build time for a much lower
query-time RAM footprint than loading N-Quads into RDFLib:

```powershell
& $JurisynthPython -m jurisynth.build_global_chunk_metadata
& $JurisynthPython -m jurisynth.build_global_oxigraph
& $JurisynthPython -m jurisynth.run_global_smoke "What obligations apply to a data controller?"
```

The first command builds a lazy SQLite provenance sidecar. The second streams
the N-Quads file into an embedded read-only Oxigraph/RocksDB store; it does not
start an HTTP service. The third writes an auditable timed output under
`jurisynth/run_outputs/`.

## 6. Build visual-description artefacts (optional)

The document preprocessor saves source images in each batch's `image_store`.
The optional image processor uses Nemotron 3 Nano Omni to make concise visual
descriptions and builds `image_index` in the same batch. Set a dedicated
`NEMOTRON_NANO_OMNI_API_KEY` (or use the existing provider-level
`JURISYNTH_NIM_API_KEY`), then run:

```powershell
& $JurisynthPython jurisynth\kg_construction_pipeline\src\image_processor.py `
  eu_legislation\batch_0009
```

This is deliberately separate from ordinary KG construction because it makes
vision-model calls. The output is auxiliary visual evidence, not a legal
assertion source.

Run one bounded provider smoke check (one caption plus one lazy expansion) and
save a secret-free JSON log:

```powershell
& $JurisynthPython -m jurisynth.run_image_nim_smoke `
  --batch eu_legislation\batch_0009 `
  --output jurisynth\run_outputs\image_nim_smoke.json
```

If captioning is temporarily rate-limited, test only the Expander's API path:

```powershell
& $JurisynthPython -m jurisynth.run_image_nim_smoke `
  --batch eu_legislation\batch_0009 --skip-caption `
  --output jurisynth\run_outputs\image_expander_nim_smoke.json
```

For a small provider-concurrency probe over two distinct images, add
`--parallel 2`. This is a diagnostic only; normal corpus captioning remains
serial and rate-limited so it does not amplify transient NIM capacity errors.

## 6. Validate a change

Run the targeted unit tests before a commit:

```powershell
& $JurisynthPython -m pytest `
  jurisynth\kg_construction_pipeline\tests\test_image_processor.py `
  jurisynth\retrieval_mech\tests\test_image_expander.py `
  jurisynth\tests\test_api.py -q
```

For retrieval evaluation, use the reviewed source-first queue and preserve
both expected and retrieved source chunks. Batch-0009 results are pilot
diagnostics, not a claim of corpus-wide legal-answering performance.

## 7. Troubleshooting

- **Missing model/key error:** set the relevant environment variable in your
  local `.env`; verify its name rather than printing its value.
- **Slow or rate-limited NIM request:** wait for the built-in backoff; do not
  add a second account just to bypass service limits.
- **No image index:** verify `image_store/*.json` lists successful JPEG, PNG,
  or WebP files. Unsupported or missing files are skipped safely.
- **Too much output:** use `--output` and inspect the saved JSON/text file
  instead of terminal scrollback.
