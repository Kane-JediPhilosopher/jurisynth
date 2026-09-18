# Held-out 100 Assertion Retrieval Evaluation: Production-v2 Artifact Identity

Status: verified before sampling; no held-out cases have been generated.

## Resolved production artifact root

`jurisynth/global_artifacts_source_uri_v2`

This is the root named by the frozen production stabilization artifact:
`run_outputs/retrieval_stabilization_validation_production_conjunctive.json`.
The production 200-case conjunction report also explicitly states that it used
the repaired v2 artifacts.

## Authoritative existing build metadata

- Oxigraph: `global_artifacts_source_uri_v2/oxigraph/jurisynth_oxigraph_manifest.json`
- Community graph: `global_artifacts_source_uri_v2/community/build_metadata.json`
- E-R index: `global_artifacts_source_uri_v2/community/er_index/manifest.json`

All three identify the source graph as
`global_artifacts_source_uri_v2/graph/jurisynth_graph.nq` and agree on this
SHA-256 graph fingerprint:

`6166222635c5fbc55001f1f763a4196c0ef7f917a54c5da068164e82ad301c84`

## Verified production components

- Oxigraph RocksDB store: source bytes `5,684,745,847`; store bytes
  `9,624,781,603`; read-only query contract enabled.
- E-R index: 2,461,215 entity records; 358,398 relation records; MiniLM
  embedding dimension 384; normalized vectors.
- Community artifacts: 2,461,215 vertices; 3,842,030 edges; four levels;
  same graph fingerprint.
- Sidecars present: `chunk_index/chunk_metadata.sqlite`,
  `document_metadata.sqlite`, `community/community_metadata.sqlite`, and
  `community/er_index/er_metadata.sqlite`.

## Benchmark identity evidence

The frozen production benchmark summary reports the direct indexed conjunction
production path and v2 artifacts, with 0.670 exact assertion recall and no
case-level regression. The corresponding production retrieval stabilization
run uses this exact v2 root. Therefore this is the authoritative root for the
new held-out evaluation.

No new manifest was synthesized. The top-level v2 directory lacks a manifest,
but the existing build metadata above provides the authoritative identity.
