# Send these packets to Chat

Start with NATURAL_QA_BATCH_1.md, then batches 2 and 3. These 14 candidates
include expected AND retrieved complete chunk text and relevant table rows.
Six incoherent joins remain excluded; this set is formative, not representative.
Ask Chat to validate/correct the proposed references and review retrieval.
There are no system answers here yet: legal-QA outcome scoring is a later phase.

For NLI, send NLI_BATCH_1.md, then batches 2 and 3 (90 synthetic pairs, opaque
IDs, no proposed labels or predictions). Request the output fields at the top
of each packet. Do not send the PRIVATE proposal/manifest files during first
adjudication: they disclose proposed labels and splits. Allow uncertain/reject.
Do not force balanced final labels or tune on the locked test subset.

Save Chat's responses with the IDs and source-based rationales, and supply
them to Codex. Disagreement requires explicit adjudication/versioning; a vote
between AI models is not independent legal validation. All final labels must
be attributed to AI-assisted review, not expert review. No NIM calls or model
predictions were used to prepare these packets. No thresholds were changed.

The NLI corpus uses paraphrased source rules and synthetic hypotheses. It is
a legal-text component diagnostic, not a test that resolves real legal conflicts.
Full chunk text is supplied for scope checks; passage context may still depend
on another instrument or document version. Reject unsupported paraphrases.
