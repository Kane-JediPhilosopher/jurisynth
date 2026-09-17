# Abandoned messy global smoke v6

The prior `running` JSON was stale. On inspection no matching global smoke or
calibration queue process remained. The output is now `interrupted`; elapsed
runtime cannot be recovered. Artifact age must not be reported as live runtime.

The log records intake completing in 268.787 seconds, task analysis completing
in 77.069 seconds, then a QCompiler AST request starting at 10:27:12 UTC without
a completion, cancellation or failure event. There are no logged transient
429/503 retries in this run. Standard error contains only embedding load output.
The checked Windows resource-exhaustion/Python-crash events supplied no matching
evidence. This does not establish why the process exited, a provider-side hang,
a memory crash, corpus absence, or legal reasoning failure.

Previously both the HTTP timeout and query runtime were unbounded. The v7 smoke
uses 180-second HTTP timeout, 900-second async query timeout and an independent
930-second process-tree watchdog. Transient retries continue within the query
deadline. These are smoke-only overrides; existing API defaults and extraction
prompts are unchanged. Timeout failures measure operational latency and cannot
be interpreted as legal-quality failures. The old intake latency exceeds this
new request budget, so slow but valid replies may be cut off intentionally.

Seventeen cancellation, watchdog and existing client regression checks passed.
The retry first isolates the last compiler/concept stage without global indices.
Global messy/organized retries are gated on format success and at least 5.5 GB
free memory. Only 4.64 GB was available at launch, so global loading is deferred
unless headroom improves after the component retry. No user applications are
closed automatically and no unrelated processes are terminated.
