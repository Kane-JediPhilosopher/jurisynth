# Jurisynth user manual — draft

> Status: developer/pilot documentation. Jurisynth currently operates on the
> Batch-0009 pilot and is a research aid, not legal advice or a production
> legal-information service.

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
& $JurisynthPython -m uvicorn jurisynth.api:app --reload --port 8000
```

Start the extracted Stitch/Vite front end in another terminal:

```powershell
Set-Location jurisynth\frontend\stitch_research_dossier
npm install
npm run dev
```

The UI is currently a developer preview. Its live-query endpoint is deliberately
disabled until a server-side workflow runner is configured; it must not expose
an API key in browser code.

## 5. Build visual-description artefacts (optional)

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

## 6. Validate a change

Run the targeted unit tests before a commit:

```powershell
& $JurisynthPython -m pytest `
  jurisynth\kg_construction_pipeline\tests\test_image_processor.py `
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
