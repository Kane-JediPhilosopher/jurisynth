# Jurisynth Pilot Review Guide

Review 20 records from `retrieval_budget_revised/batch_0009_fallback_50_review_set.jsonl`.
These are **retrieval/provenance checks**, not legal-advice assessments. You do
not need to decide whether the underlying law is correct.

For each record, inspect the `case.expected_assertion`, the retrieved evidence
excerpts in `result.retrieved_evidence`, and fill the three fields under
`human_review`:

1. `evidence_relevant`
   - `yes`: an excerpt addresses the expected relationship.
   - `partly`: same topic but it does not establish the requested relationship.
   - `no`: unrelated topic, party, or legal issue.

2. `source_supports_assertion`
   - `yes`: the cited excerpt supports the expected subject–predicate–object.
   - `no`: it does not, or no relevant cited excerpt is present.

3. `status_appropriate`
   - `yes`: `success` accompanies relevant support, or `weak`/`empty` correctly
     signals insufficient support.
   - `no`: for example, the system reports `success` while returning unrelated
     evidence.

Leave a short `notes` value only for clear patterns, such as “same country but
wrong regulation” or “subject matches; predicate does not.”

The first record is intentionally a miss. It should be labelled `no`, `no`,
`no`: its retrieved Belgian-government evidence is unrelated to the expected
central-administrator assertion, yet its status is `success`.
