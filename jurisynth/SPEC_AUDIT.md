# Full-spec reconciliation audit

**Audit basis:** `agentic_reasoner_spec_v2.md`, `retrieval_mech_spec.md`, and
`CHECKLIST.md`, reviewed 2026-09-04.  This is a fidelity audit, not a claim
that pilot behaviour is fully calibrated.

## Verdict

The checklist is materially faithful to both original specifications.  It does
not conceal the major incomplete commitments: global KG/community artifacts,
community expansion and LLM summary synthesis, calibrated retrieval and
contradiction scoring, labelled legal-QA evaluation, and GUI integration.

There are three points that need precise wording in the thesis and checklist.

1. **Community selector is partial, not complete.** It implements semantic
   relevance, concept coverage, a relevance gate, and bounded tree-distance
   novelty.  It does not yet implement the specification's graph-edge/predicate
   structural-support signal or community-aware candidate expansion.  The
   checklist leaves expansion open, which is correct; do not describe the
   current score as the full specification formula.
2. **The current community summary is deterministic orientation, not the
   optional LLM Lazy Summarizer.** It returns one graph-only payload with LCA
   and dispersion metadata.  It is non-authoritative and does not include raw
   chunks.  The specification's batched summary-of-summaries path and live-NIM
   validation remain open.
3. **The GUI is now started, so its checklist item must move from `defer` to
   active once the server-side workflow runner and real report-card rendering
   are complete.** The exported Stitch UI must not be represented as a completed
   Jurisynth interface while Delaware mock components remain.

## Agentic Reasoner

- **Faithful:** conversation intake; semantic routing; QCompiler translation;
  semantic dependency planning; dependency-aware scheduling; opaque retrieval
  boundary; Claim/evidence ID validation; weak/empty handling; contradiction
  candidate detection; hierarchical report; progressive disclosure; streaming;
  reasoning log.
- **Still deliberately incomplete:** calibrated CrossEncoder/NLI contradiction
  scoring and LLM explanations.  Both depend on labelled examples, exactly as
  the specification says.
- **No material boundary deviation found:** the Reasoner does not create SPARQL,
  URI candidates, community IDs, or internal retrieval strategies.

## Retrieval Mechanism

- **Faithful:** one request per leaf; query interpreter boundary; direct chunk
  retrieval; E-R matching; deterministic SPARQL templates; direct/path/
  conjunctive escalation; provenance-normalised EvidenceItems; table evidence;
  separate relevance/structural/coherence fields; status taxonomy; bounded
  concurrency; community IDs as soft guidance rather than hard filtering.
- **Partial by design:** community structural support, hierarchy/LCA candidate
  expansion, production Lazy Summarizer, table reranker selection, and all
  tuned thresholds.
- **Important wording correction:** `structural_score` on an evidence item is
  currently traversal-origin support, not the complete community structural
  support described in section 9 of the Retrieval specification.

## Evaluation and reporting

- **Faithful:** the checklist separates synthetic retrieval-integrity probes,
  table diagnostics, and reviewed natural seeds.  It does not call them a
  benchmark or a legal-correctness result.
- **Open:** held-out source-checked legal QA, answer-faithfulness labels,
  contradiction labels, and calibrated acceptance thresholds.

## Thesis-safe claim

> Jurisynth implements and evaluates an auditable pilot architecture for
> evidence-linked retrieval and agentic legal-research synthesis over Batch
> 0009.  It does not claim full-corpus coverage, calibrated ranking, legal
> correctness, or benchmark-level generalisation.

