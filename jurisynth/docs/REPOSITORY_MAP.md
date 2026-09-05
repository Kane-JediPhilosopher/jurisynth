# Jurisynth repository map

This map is a navigation aid. It intentionally does **not** move operational
modules during the pilot, because `python -m jurisynth.<module>` paths are
already documented in the runbook and test scripts.

## Package root (`jurisynth/`)

- `main.py` — command-line pilot workflow entry point.
- `api.py` — FastAPI boundary (developer preview).
- `contracts.py` — shared result/data contracts.
- `build_pilot_er_index.py`, `resource_aggregator.py` — artifact builders.
- `run_*evaluation.py`, `retrieval_evaluation.py` — evaluation runners.
- `render_pilot_output.py`, `inspect_pilot_coverage.py` — inspection tools.
- `CHECKLIST.md`, `RUNBOOK.md`, `ROADMAP.md`, `SPEC_AUDIT.md` — active
  project-control documents; this `docs/` folder holds longer reference
  material.

## Main subsystems

- `agentic_reasoner/` — intake, QCompiler integration, workflow and reporting.
- `retrieval_mech/` — RDF/E-R/table retrieval and community artefacts.
- `kg_construction_pipeline/` — corpus-to-KG pipeline and component tests.
- `frontend/` — imported Stitch front-end plus integration notes.
- `evaluation_artifacts/` — human-review packets and pilot outcomes.

## Safe housekeeping policy

Keep package-root compatibility entry points until after the thesis pilot. New
documentation belongs in `docs/`; generated output belongs in `run_outputs/`,
`pilot_artifacts/`, or per-batch corpus directories. Do not delete any source
or generated data solely because it looks old without checking whether it is
referenced by a runbook, test, or thesis result.
