# Jurisynth AI Review Packet — Chat Review Summary

## Scope

Reviewed all material in `AI_REVIEW_PACKETS.zip`:

- 14 natural-QA reference/retrieval candidates
- 90 legal-text NLI pairs
- 3 natural-QA batches
- 3 NLI batches

All judgments are **AI-assisted review**, not expert legal validation.

## Natural-QA

Reference/question decisions:

- valid: 8
- revise: 6

Retrieval labels:

- partial: 5
- insufficient: 5
- sufficient: 3
- irrelevant: 1

Main finding: retrieval misses are heterogeneous. Some cases retrieved substantively similar provisions from another instrument/version and are therefore marked **partial**, not fully sufficient; others retrieved only topic-adjacent or unrelated material and are marked **insufficient/irrelevant**. Exact expected-source/table recovery supports **sufficient** where appropriate.

No system-answer PASS/PARTIAL/FAIL was assigned because these packets contain no system answers.

## NLI

- Premises supported by supplied source: 90/90
- Entailment: 30
- Contradiction: 30
- Neutral: 30
- Reject/uncertain: 0

The final 30/30/30 label distribution was **not forced**; it resulted from source-based adjudication.

Two recurring scope corrections are recorded:

1. The injunction premise should preserve that the guarantees condition applies to continuation of the alleged infringement and that the judicial authority **may** issue the measure.
2. The TIR premise should use the source-exact scope “States referred to in Article 52, paragraph 1” rather than the looser shorthand “eligible States”.

## Files

- `CHAT_NATURAL_QA_REVIEW.md` — human-readable natural-QA review
- `CHAT_NATURAL_QA_REVIEW.jsonl` — machine-readable natural-QA review
- `CHAT_NLI_ADJUDICATION.md` — human-readable NLI adjudication
- `CHAT_NLI_ADJUDICATION.csv` — tabular NLI adjudication
- `CHAT_NLI_ADJUDICATION.jsonl` — machine-readable NLI adjudication

## Guardrails retained

- Do not equate execution success with relevance.
- Do not treat alternate-source wording as proof of source equivalence or current applicability.
- Do not assign legal-QA accuracy from these packets because no system answers are present.
- Do not treat AI-agreement as independent expert validation.
- Do not tune thresholds from these adjudications.
