# Retrieval Mech temporary architecture freeze

Effective: 2026-09-17

The five retrieval-stabilization gates passed after the bounded,
leaf-explicit multi-instrument source recovery fix. The Retrieval Mech is now
under a temporary architecture freeze.

During this freeze, do not change thresholds, community logic, Query
Interpreter policy, E-R logic, table/image retrieval, ranking, top-p/adaptive
truncation, or provider/NIM configuration as part of retrieval work.

The 200-case controlled assertion benchmark identified one possible systematic
reopening condition: 92 of 123 exact-assertion misses recovered none of the
expected subject, predicate, or object. This indicates candidate-generation or
E-R seed recall rather than provenance corruption. No retuning has been made.
The freeze remains temporary pending an owner decision on that isolated issue.

Diagnostic exception: the candidate-generation/E-R path was reopened for
read-only tracing on 2026-09-17. All 92 complete misses localized to E-R
grounding under the benchmark's raw-leaf fallback interpreter. No production
retrieval policy was changed; all other freeze boundaries remain active.
