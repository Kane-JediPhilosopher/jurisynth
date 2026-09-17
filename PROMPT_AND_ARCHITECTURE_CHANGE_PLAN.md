# Jurisynth proposed changes — not applied

Approved implementation scope: standalone diagnostic tooling and launcher for the existing UI. Production prompts, schemas, architecture, retrieval policy and retries remain unchanged. Live NIM capture still needs separate approval.

## First: use evidence, not another broad rewrite

Capture one real request/interpretation; replay baseline versus a single path/escalation change. Use saved bundles and stage events to identify the expensive operation. The provided hand-authored fixture is only a tooling test. Do not run another long global smoke or large calibration grid yet.

## Proposed production diffs requiring approval

1. **Leaf input wiring** (`agentic_reasoner/llm.py`, plus tests): add `contextual_facts`, `constraints`, and a clearly labelled `community_orientation` input derived from bundle.community_summary. Preserve current evidence/citation validation; orientation and user facts cannot count as legal evidence. Add bounds/explicit truncation metadata for context without reinstating output-token parameters. Inspect upstream claim-reference requirements before changing downstream provenance contracts or copying bundles.

2. **Single dependency authority** (`main.py`, compiler/planner tests): controlled comparison with the semantic planner disabled and existing compiler edges retained. This is NOT a decision to make every leaf parallel. Alternatively retain semantic planning as sole authority with full context and clearer hard-versus-optional semantics, but do not implement both alternatives. Preserve original questions/uncertainties, no presupposed classifications.

3. **Scheduler readiness** (`agentic_reasoner/scheduler.py`, tests): event-driven admission of newly ready nodes instead of waiting for entire ready waves; retain a configurable concurrency/RAM policy, cycle detection and failure isolation. First decide dependency semantics; raising concurrency alone does not remove gates.

4. **Community interpretation** (`community_selector.py`, `community_hierarchy.py`, `mechanism.py`, `community_summary.py`): owner must approve deterministic orientation with optional LLM descriptor merging versus stronger generated-summary claims. Reconcile unreachable >=6 count trigger with top_n=3 plus one LCA, implement coverage-guided region choice, preserve dispersion/provenance and non-authoritative status. Wire consumption before claiming usefulness. Do not reinstate precomputed LLM leaf summaries automatically or force one provider call for every retrieval.

5. **Compiler/report wording** (translator/reporting): mostly parallel compilation example, explicit coverage/no invented issues/no unresolved presuppositions, and report preservation of temporal/applicability caveats, supported rules/inferences/gaps and unresolved tensions. Current prompts already contain several safeguards; edits need a controlled fidelity check, not blanket shortening.

6. **Interpreter budgets** (query_interpreter.py/schemas.py): only after captured workload and evidence-loss measurements, consider leaf-specific concept instructions and explicit count limits. Do not cap concepts/alter named entities on diagnostic baseline or tune on held-out test data.

7. **Production observability/checkpoints** (reasoner/workflow/llm): port proven diagnostic spans/query IDs and checkpoint bundles/leaf outputs before synthesis; retain HTTP cause/context types without logging credentials or raw transport repr blindly. Keep request deadlines/output caps disabled as requested. Standalone diagnostic tracing is currently process-local, not production logging.

## Deferred evaluation decisions

Do not silently narrow the owner's prior request for EU-related LexGLUE tasks/model comparisons. Chat's EUR-LEX-first screening and runtime estimation are recommendations awaiting a scope decision. Maintain distinction between zero-shot generative evaluation, fine-tuned leaderboard results, ECtHR case-law generalization and actual EU-legislation retrieval quality. Do not run a full model/task grid yet.

The checklist's 167/175 figure is unchanged and not a demo-readiness claim. Diagnostic implementation does not close the global live validation, calibration or legal gold-quality gates.
