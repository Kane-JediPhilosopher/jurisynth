# Local retrieval latency diagnostic

2026-09-14. Two sequential cases against the global Oxigraph/SQLite/modal artifacts. No NIM requests. A five-minute watchdog existed only in the diagnostic process; it did not fire. Production prompts, retry policies, timeouts and adaptive index policy were unchanged. Auto-loading selected two E-R shards at the measured available memory.

## Findings

- Heavy module imports reached artifact loading at 90.98 seconds. Global artifact loading itself took 6.36 seconds; E-R loading and embedding/hierarchy setup finished at approximately 104.08 seconds. Startup must not be confused with mid-query retrieval latency.
- The small hand-authored interpretation (2 entities, 1 relation) took 31.829 seconds and returned weak evidence. Initial structured retrieval took 3.193 seconds. Its escalated structured pass took 28.616 seconds, including 16.811 seconds in three-hop path expansion. Chunk search took .188 seconds; table search .179 seconds.
- The broader hand-authored interpretation (5 entities, 4 relations, 17 total terms including variants) took 5.318 seconds and returned success status. It did not enter the weak-evidence escalation path. Structured retrieval took 5.303 seconds, including 3.549 seconds for relation matching and 1.330 seconds for bounded two-hop paths. Chunk search took .074 seconds; table search .065 seconds.
- End-of-case RSS was approximately 2.39/2.40 GiB. This is not peak RSS and is not proof of safety under concurrent leaves.

## What this establishes

Local escalation can materially increase latency even with fewer concepts. Raw concept count alone is not a sufficient predictor. The ordinary searches were fast in these cases. A diagnostic 'success' status establishes execution, not legal relevance or correctness.

## What it does not establish

These are hand-authored interpretations, not captured v10 NIM concept outputs. Entity terms often hit exact-label lookup and therefore do not stress full vector matching like some generated variants might. Cases were sequential and cache-sensitive. No vision, NLI or LLM summary calls were exercised. The prior global 14–32 minute retrieval intervals were not reproduced, so their full cause remains unresolved; it cannot honestly be labelled entirely provider latency or entirely local computation.

Next discriminating experiment: capture one actual interpretation, including concept counts/variants, and replay its local work with spans for shard lock wait/load/search, graph enumeration/path expansion, chunk resolution, escalation and operation-queue wait. Run sequential first, then limited concurrency only if memory permits. This is a proposed next experiment, not a completed run or an authorization to change production retrieval policy.

See results.json for inclusive nested timings (do not sum overlapping spans), and events.jsonl for checkpoints. No checklist validation gates were closed by this diagnostic.
