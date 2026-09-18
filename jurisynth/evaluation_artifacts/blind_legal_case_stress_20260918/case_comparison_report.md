# Jurisynth blind legal case stress test

## Design and integrity

This was a qualitative, single-case, outcome-held-out stress test. The selected authority was the Court of Justice judgment in *Bundesverband der Verbraucherzentralen und Verbraucherverbande v Planet49 GmbH*, C-673/17, ECLI:EU:C:2019:801. The authoritative source was the official EUR-Lex judgment at <https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:62017CJ0673>.

The live runner was given only `blind_case_packet.json`. The case name, number, court outcome, principal findings and reference analysis remained in `sealed_held_out_reference.json`. The rubric was frozen before inference with SHA-256 `cf06298180db4bdfec4f8c5c8b7b8452edf0385af68e2d2d86519e97854b7e6f`. No rubric, gold, prompt, retrieval threshold or production behavior was changed after inference.

## Execution

- Provider/model: NVIDIA NIM, `nvidia/nemotron-3-super-120b-a12b`
- Decoding: temperature `0`, top-p `0.000001`, reasoning effort `none`, provider-default output limit
- QCompiler: four independent leaves; no dependency edges; all leaves became runnable in parallel
- Total wall time: 1,212.911 seconds (20.2 minutes)
- Completed NIM time: 60.303 seconds across 15 completed calls
- Provider behavior: 16 attempts, one retried HTTP 503, no terminal provider failure
- Peak process RSS: 2,722,435,072 bytes (2.54 GiB)
- Contradiction detection: disabled only for the official case-study run after a production-faithful attempt generated 6,441 CPU-NLI pairs from 114 evidence items and remained in that local stage for more than 30 minutes. The aborted trace is preserved. No detector code was changed.

Most elapsed time was local retrieval, not NIM generation. The four parallel leaf retrievals ranged from 516.281 to 1,190.000 seconds; leaf-generation calls ranged from 1.906 to 8.297 seconds.

## Retrieval and reasoning findings

### Preselected-checkbox consent

Jurisynth answered that a preselected checkbox is not valid consent and produced a supported claim. The cited structured assertion preserved source provenance and expressed that pre-ticked boxes should not constitute consent. This matched the judgment's direction.

The support was incomplete at the instrument-chain level. The corpus contains the amended ePrivacy Article 5(3) wording in document `L_2009337EN.01001101`, chunk 20, but that answer-bearing chunk never entered any EvidenceBundle. The system therefore connected the consent rule through GDPR-derived evidence rather than retrieving the direct amended ePrivacy rule.

### Whether cookie information must be personal data

The relevant leaf correctly abstained because its EvidenceBundle did not establish the answer. Its lone Claim object was marked insufficient and carried no evidence references. The final overview nevertheless asserted the correct held-out proposition—that the ePrivacy storage/access rule does not depend on the information being personal data—while the detailed report section said the matter could not be established. This is a downstream synthesis inconsistency, not a grounded success.

### Cookie duration and third-party access

The relevant leaf received eight chunks but no structured assertions and appropriately returned insufficient evidence. Neither the duration duty nor third-party-access duty was recovered. This was a retrieval/coverage miss rather than hallucination.

### Temporal relationship

The system recovered that Directive 95/46/EC was replaced by the GDPR from 25 May 2018 and identified Directive 2002/58/EC. It then overgeneralized that both regimes applied to cookie processing before/after the date without retrieving enough authority for the precise temporal qualification. The scope parser also represented `Directive 95/46/EC` as `citation:directive:2046:95`, and the primary Directive 95/46 document was not found in production document metadata.

## Cross-representation behavior

The representation-aware prompt selector behaved as intended and prevented modality starvation:

- q001 selected 8 assertions and 4 chunks;
- q002 selected 4 assertions and 8 chunks;
- q003 selected 8 chunks;
- q004 selected 3 assertions and 9 chunks.

Four substantive claims were generated: three carried evidence, two were assertion-only, none were chunk-only, and one cited both an assertion and a chunk. The mixed claim concerned instrument identity/title rather than a substantive corroboration of the disputed legal rule. Assertions helped with affirmative-consent and repeal propositions but also introduced unrelated material. Chunks did not recover the most important missing amended ePrivacy provision. Tables and images contributed no useful evidence; no image expansion succeeded or was needed.

Community selection ran for every leaf and produced community summaries, but the current leaf-answer payload did not include those summaries. They therefore did not influence this case's leaf answers.

## Frozen-rubric comparison

- Supported/matched: R2, R8
- Partially supported: R1, R3, R4, R7, R10
- Missed: R5, R6
- Contradicted: R9
- Not assessable: none

Overall classification: **partial**.

The case shows that Jurisynth can decompose a compact real dispute, retrieve traceable evidence, reach one central legal conclusion, preserve claim-level provenance and abstain on missing material. It also reveals material limitations: the direct answer-bearing ePrivacy amendment was not retrieved, two information-duty holdings were missed, and final synthesis promoted one correct-but-unsupported proposition despite the leaf's abstention.

This case does not establish legal accuracy, generalization, statistical reliability or court-outcome prediction. Outcome alignment is only partial, and a correct proposition reached without retrieved support is not counted as grounded reasoning.

## Recommended next step

Perform a read-only trace of why `L_2009337EN.01001101` chunk 20 did not enter the q001/q003 EvidenceBundles, and separately inspect the final-synthesis contract that allowed an abstained leaf to become an unsupported affirmative overview statement; do not tune the architecture until those two paths are localized.
