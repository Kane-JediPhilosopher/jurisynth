# GCP runbook: rebuild RDF with lossless source document IDs

This fixes the Graph Serializer's document/chunk/Assertion/Modifier URI collisions **without LLM calls or re-extraction**. Existing chunk/table/image embeddings are reused; the Community/E–R rebuild later recomputes entity/relation embeddings using the local model. It writes a **new versioned artifact root** and does not overwrite `jurisynth/global_artifacts` or existing per-batch graphs.

## Files to synchronize from the laptop

Put these at the same relative paths under `~/project_space` on the VM:

1. `jurisynth/kg_construction_pipeline/src/source_uri.py` **(new)**
2. `jurisynth/kg_construction_pipeline/src/graph_serializer.py` **(replace VM copy)**
3. `jurisynth/table_rdf_enricher.py` **(replace VM copy; also used by global chunk metadata)**
4. `jurisynth/rebuild_source_id_graphs.py` **(new)**
5. `jurisynth/build_global_oxigraph.py` **(copy to VM; required by Stage 2)**
6. `jurisynth/retrieval_mech/pilot_artifacts.py` **(replace VM copy; preserves read-only lookup of the still-active v1 pilot graph)**
7. `jurisynth/kg_construction_pipeline/tests/test_graph_serializer.py`, `jurisynth/tests/test_table_rdf_enricher.py`, and `jurisynth/tests/test_rebuild_source_id_graphs.py` **(new/updated tests used by the preflight command)**.
8. The **newly reprocessed** `resolved_assertions.pkl` checkpoints for `batch_0009` and `batch_0437`, their `diagnostics/validation_stats.json` files, and their `chunk_index/chunk_index.faiss` and `chunk_index/chunk_metadata.pkl` files. Synchronize these even if older files with the same names already exist on the VM; compare SHA-256 hashes if uncertain.

Keep the old files/artifacts elsewhere or use your normal version-control/snapshot workflow before replacement. Do **not** upload `.env` or use a NIM API key for this rebuild. All other 435 resolved checkpoints and batch chunk metadata must already exist on the VM; the first check below verifies this. Stage 3 also assumes the VM has the current `jurisynth/build_global_artifacts.py`, `jurisynth/resource_aggregator.py`, `jurisynth/build_global_chunk_metadata.py`, and `jurisynth/retrieval_mech/lazy_chunk_metadata.py`; synchronize those if they differ from the laptop.

For Stage 3, also synchronize the three sidecar entry points `jurisynth/build_global_chunk_metadata.py`, `jurisynth/build_global_er_metadata.py`, and `jurisynth/build_global_community_metadata.py` and their implementations `jurisynth/retrieval_mech/lazy_chunk_metadata.py`, `jurisynth/retrieval_mech/lazy_er_metadata.py`, and `jurisynth/retrieval_mech/lazy_community_metadata.py`. The E–R sidecar additionally imports `jurisynth/retrieval_mech/resource_records.py`; the community sidecar imports `jurisynth/retrieval_mech/community_summary.py`. Synchronize both. Confirm that `jurisynth/build_global_community.py` and its retrieval-mechanism imports are present on the VM before starting the long community build. Before running the two final sidecars, check `python -c "import jurisynth.build_global_er_metadata, jurisynth.build_global_community_metadata; print('imports OK')"`.

If you run global assertion evaluations or AI-review packet generation on the VM *before activation*, also synchronize `jurisynth/run_global_assertion_evaluation.py` and `jurisynth/build_ai_review_packets.py`, which now check both v1 and v2 chunk URI candidates.

Local SHA-256 fingerprints for the reprocessed resolved checkpoints: `batch_0009` = `a73cb4e0077cd9f3082f73b08e3dbca482b7e0903511cebfd74423f5886bb0d9`; `batch_0437` = `a9ff2c793a684a00586e35a50443b552394dbb8b77ed7ccfb97850840964719e`. Use `sha256sum` on the VM to verify the uploaded copies.

## Preconditions

Run from the project root, with your existing Python 3.12 virtual environment active:

```bash
cd ~/project_space
source .venv/bin/activate
df -h .
python -c 'import pyoxigraph; print("pyoxigraph available")'
PYTHONPATH="$PWD/jurisynth/kg_construction_pipeline/src:$PWD" python -m pytest jurisynth/kg_construction_pipeline/tests/test_graph_serializer.py jurisynth/tests/test_table_rdf_enricher.py jurisynth/tests/test_rebuild_source_id_graphs.py -q
python -m jurisynth.rebuild_source_id_graphs check
```

Proceed only if `check` reports **437 batches, 43,694 source document IDs, 251,532 source chunk pairs, and zero new URI collisions**. The previous global graph/store/community occupy about **5.5 + 9.5 + 21.1 GiB**, respectively. A versioned rebuild also temporarily retains roughly another 5.5 GiB of per-batch graphs, with possible extra temporary space during RocksDB optimization. Require **at least 60 GiB free disk** before starting; if less, stop and reassess rather than deleting old artifacts.

## Stage 1 — deterministic batch RDF rebuild

Use `tmux` for the long stage. The `--resume` flag verifies hashes before skipping completed batches. The output root below is new; leave the original output tree intact.

```bash
tmux new -s source-uri-v2
cd ~/project_space
source .venv/bin/activate
set -o pipefail
python -m jurisynth.rebuild_source_id_graphs build \
  --destination jurisynth/global_artifacts_source_uri_v2 \
  --resume 2>&1 | tee jurisynth/source_uri_v2_batch_build.log
```

Detach with `Ctrl-B`, then `D`. To inspect progress: `tmux attach -t source-uri-v2` or `tail -n 30 jurisynth/source_uri_v2_batch_build.log`. Do not run a second build in the same destination concurrently. A successful finish reports **437 selected**; every batch line is either `built` or `verified_and_skipped`.

The script revalidates each saved `resolved_assertions.pkl`, requires validation statistics to match the existing diagnostic file, and serializes into `jurisynth/global_artifacts_source_uri_v2/batches/<batch>/graph/`. It makes no model/API request. If validation statistics drift, it stops instead of silently creating a different KG.

## Stage 2 — versioned global graph, Oxigraph, identity check

Run these only after Stage 1 succeeds:

```bash
python -m jurisynth.rebuild_source_id_graphs merge \
  --destination jurisynth/global_artifacts_source_uri_v2

python -m jurisynth.build_global_oxigraph \
  --graph jurisynth/global_artifacts_source_uri_v2/graph/jurisynth_graph.nq \
  --destination jurisynth/global_artifacts_source_uri_v2/oxigraph

python -m jurisynth.rebuild_source_id_graphs verify \
  --destination jurisynth/global_artifacts_source_uri_v2
```

The verifier must report **`shared_document_uris: 0`** and must not raise a multi-valued Assertion-component or Modifier-value error. It does not assume that the total source-label count remains identical after your reprocessing of batches 0009 and 0437. Keep the old global graph/store until this passes.

## Stage 3 — rebuilt chunk provenance and community/E–R artifacts

The per-batch FAISS vectors already exist; **do not recompute embeddings**. Because batches 0009 and 0437 were reprocessed, first re-aggregate their current per-batch vectors/metadata into the versioned root rather than assuming the old global aggregate pickle is still synchronized. The existing 437-batch manifest can be used for this explicit chunk-only merge:

```bash
python -m jurisynth.build_global_artifacts chunks \
  --manifest jurisynth/global_artifacts/manifest.json \
  --destination jurisynth/global_artifacts_source_uri_v2
```

This reconstructs FAISS vectors from saved per-batch indices and does not call an embedding model. Then build the fresh graph-URI SQLite sidecar from the **new** aggregate metadata:

```bash
python -m jurisynth.build_global_chunk_metadata \
  --source jurisynth/global_artifacts_source_uri_v2/chunk_index/chunk_metadata.pkl \
  --destination jurisynth/global_artifacts_source_uri_v2/chunk_index/chunk_metadata.sqlite
```

Require **`ambiguous_graph_uri_count: 0`**. If it is nonzero, stop before the expensive community rebuild.

With at least 48 GiB *available RAM* and sufficient disk, rebuild community and E–R artifacts against the corrected global graph:

```bash
python -m jurisynth.build_global_community \
  --graph jurisynth/global_artifacts_source_uri_v2/graph/jurisynth_graph.nq \
  --destination jurisynth/global_artifacts_source_uri_v2/community \
  --minimum-available-gb 48

python -m jurisynth.build_global_er_metadata \
  --source jurisynth/global_artifacts_source_uri_v2/community/er_index/metadata.json \
  --destination jurisynth/global_artifacts_source_uri_v2/community/er_index/er_metadata.sqlite

python -m jurisynth.build_global_community_metadata \
  --hierarchy jurisynth/global_artifacts_source_uri_v2/community/community_hierarchy.json \
  --descriptors jurisynth/global_artifacts_source_uri_v2/community/community_descriptors.json \
  --destination jurisynth/global_artifacts_source_uri_v2/community/community_metadata.sqlite
```

If `build_global_community` fails, preserve the logs and stop; its destination builder refuses to overwrite a partially created directory. Do not erase or replace the original community artifacts to retry.

## What can be reused, and what still needs integration

- Rebuild: batch RDF, global N-Quads, Oxigraph, graph-URI chunk sidecar, Community Graph and E–R indices/sidecars.
- Reuse without new embeddings: saved **per-batch** chunk FAISS vectors (re-aggregated for synchronization), table and image indices/stores.
- The new artifacts remain under `jurisynth/global_artifacts_source_uri_v2/` on GCP. **Do not swap this with the existing local `global_artifacts` yet.** After all checks pass, download the corrected graph/store/community/sidecars and pair them with the unchanged FAISS/table/image artifacts under a complete versioned local root; then run an offline retrieval smoke before activation.

## Local verification already performed

- All **437/437** local completed batches now have extracted, normalized, scored, and resolved checkpoints.
- Lossless URI check: **43,694 unique source documents; 251,532 unique source chunk pairs; zero URI collisions**.
- Deterministic pilot reserialization of **batch_0009** and **batch_0437** succeeded, with existing validation statistics unchanged.
- An in-memory Oxigraph load of the **actual rebuilt batch_0009 graph** found **100 source document labels on 100 Document URIs**, zero shared IDs, and one-valued Assertion/Modifier components.
- Focused offline tests: **38 passed, 1 skipped** across serializer/table/chunk-metadata/pilot/Oxigraph/rebuild integration; the existing batch-0009 pilot-loader integration test also **passed live against the original graph**.
- A persistent Oxigraph *pilot* on this OneDrive-backed Windows workspace failed with a RocksDB file-access error; the verifier itself passed against an in-memory Oxigraph test store. The GCP Linux persistent-store step has **not** yet been executed and must be checked in Stage 2.
