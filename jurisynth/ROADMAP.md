# Jurisynth Component Roadmap

This is the maintained component/dependency list. Status describes current
implementation maturity, not research validation.

## Critical path

```text
Batch KG/table artifacts
  → Resource Aggregator
  → global RDF dataset + merged retrieval artifacts
  → Table RDF Enricher + global Community Graph
  → E-R Index Builder
  → structured Retrieval Mechanism
  → QCompiler-enabled Agentic Reasoner
  → evaluation adapters and GUI
```

## Components

1. **KG Construction Pipeline** — in progress
   - Produces per-batch RDF N-Quads, chunk indexes, table artifacts, and diagnostics.

2. **Resource Aggregator** — pilot-ready
   - Registers batch-level table/image artifacts through a deterministic manifest.
   - Merges RDF N-Quads and compatible chunk/table indexes with overwrite and collision
     protection; preserves table JSON and per-table row indexes. Full-corpus execution
     remains pending.
   - Must produce deterministic global manifests and preserve original batch/source IDs.

3. **Table RDF Enricher** — pilot-ready
   - Proposed name for the table-to-RDF component.
   - Adds a minimal `Table` resource and source-document/source-chunk provenance links.
   - Table JSON remains source of truth for headers, rows, and cells; V1 does not add
     RDF row/cell resources or new table-specific ontology properties.
   - Table resources are excluded from Community Graph semantic-edge construction by
     default.

4. **Community Graph Constructor** — pilot-ready
   - Test first against completed `batch_0009`; run globally only after aggregation.

5. **E-R Index Builder** — pilot-ready
   - Builds persisted, query-time entity and relation/property FAISS indexes from the
     global graph and community graph.
   - Maps every FAISS ID back to stable RDF URI, label, and community membership.

6. **Retrieval Mechanism** — pilot-ready
   - Current: contracts, artifact adapters, E-R matching, direct/two-hop RDF retrieval,
     assertion/chunk provenance, table constraints, coherence signals, and soft
     community selection.
   - Pending: community expansion/summaries, conjunctive fallback, and global artifacts.

7. **Agentic Reasoner** — pilot-ready
   - Current: dependency-aware scheduler, QCompiler adapter, NIM task routing,
     evidence-grounded leaf answers, report synthesis, validation retry, and logging.
   - Pilot contradiction warnings now pair only evidence-linked claims and detect
     explicit opposing polarity. A calibrated CrossEncoder and batched LLM conflict
     explanations remain pending; warnings never adjudicate legal correctness.
   - Pending: richer intake and multi-level/streamed presentation.

8. **Reasoning Log** — pilot-ready, parallel component
   - Records task, AST, dependency plan, node transitions, retrieval/LLM latency,
     failures, Claims, evidence mappings, and evaluation diagnostics.

9. **LexGLUE Evaluation Adapter** — pending
   - Converts final Reasoner output into the selected zero-shot LexGLUE task format.
   - Needs a task-specific mapping and non-legal-answer baselines before score claims.

10. **GUI** — pending
    - Exposes the user-facing chain: report → section → Claim → evidence → source.
    - Must not expose internal retrieval/scheduler traces by default.

## Evaluation sequence

1. Artifact invariants: IDs, index/metadata alignment, RDF parseability, provenance links.
2. Retrieval-first weak supervision: derive natural-language test queries from assertions
   and table rows with known source chunks/rows.
3. Measure recall@k, provenance-link validity, and correct weak/empty handling.
4. Human review: sample a small set of retrieved evidence and later final reports.

## Explicitly deferred decisions

- Full-corpus aggregation execution and its storage location.
- QCompiler/NIM prompt-set acceptance threshold after the live validation run.
- Community-scoring weights and E-R thresholds.
- CrossEncoder model/thresholds for contradiction detection.
- Final Claim, report, table-evidence, and Reasoning Log schemas.
