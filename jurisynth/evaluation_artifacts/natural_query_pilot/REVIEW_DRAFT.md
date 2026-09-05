# Batch 0009 natural-query review draft

## What you need to do

This is a **small source-validation exercise**, not a review of the entire retrieval output. For each case, decide whether the question and its proposed source really match. You do not need to judge every retrieved evidence item or the retrieval score.

Use one of these decisions:

- **KEEP** — the question is natural and the proposed source genuinely answers it.
- **REWRITE** — the underlying topic is useful, but the question or its expected source needs changing.
- **DROP** — we cannot currently verify a good source-backed version; exclude it from the pilot set for now.

The current pilot result is **not a model-accuracy claim**. It only tells us whether a known target document/chunk appeared among retrieved results. A case is only appropriate for later evaluation once its wording and source are defensible.

## Quick decisions
```text
1: keep
2: keep
3: approve rewrite
4: drop
```

`verify` means you would like to inspect the cited source before deciding. I will make the corresponding dataset edits once you choose.

---

## Case natural_001 — citizens' initiative organisers

**Question**

> What must organisers do with personal data collected for a citizens' initiative?

**Current expected source**

- Document: `L_2011065EN.01000101`
- Chunk: `chunk_6`

**Expected chunk — relevant provisions**

> Article 12, *Protection of personal data*: “In processing personal data pursuant to this Regulation, the organisers of a citizens' initiative ... shall comply with Directive 95/46/EC and the national provisions adopted pursuant thereto.” The same chunk later says organisers must ensure that personal data collected for an initiative “are not used for any purpose other than their indicated support for that initiative” and must destroy the statements of support within the stated deadline.

**Retrieved chunk**

- `L_2011065EN.01000101`, `chunk_6` — **same as expected**.
- The retrieved evidence was attached to an Article 10 assertion about the Commission receiving organisers, but its source chunk also contains Article 12 above. This is a useful distinction: the right source chunk was found, while the top RDF assertion was not the most directly phrased one.

**What the retrieval run established**

- The expected document was retrieved.
- The expected chunk was retrieved.
- The top evidence was mostly about organisers' procedural responsibilities, liability, and the Commission's handling of an initiative.

**My recommendation: KEEP.**

The expected chunk expressly supports the question. The case is valid, although the later answer-generation evaluation should check whether the selected evidence item actually surfaces the Article 12 rule rather than only Article 10 procedure.

Reply: `1: KEEP`.

---

## Case natural_002 — use of support data

**Question**

> Can organisers use citizens' initiative support data for purposes unrelated to the initiative?

**Current expected source**

- Document: `L_2011065EN.01000101`
- Chunk: `chunk_6`

**Expected chunk — exact answer**

> Article 12(3): “The organisers shall ensure that personal data collected for a given citizen's initiative are not used for any purpose other than their indicated support for that initiative ...”

**Retrieved chunk**

- `L_2011065EN.01000101`, `chunk_6` — **same as expected**.
- As with case 1, the retrieved source chunk is correct, though the highest displayed RDF assertion concerns initiative procedure rather than this paragraph's prohibition.

**What the retrieval run established**

- The expected document and chunk were both retrieved.
- The returned evidence again centred on initiative procedure and organisers' roles.

**My recommendation: KEEP.**

This is a strong source-backed natural question. The expected chunk gives a direct negative answer: organisers may not use the data for unrelated purposes.

Reply: `2: KEEP`.

---

## Case natural_003 — European Vehicle Register

**Original question**

> How should data in the European Vehicle Register be managed under data-protection rules?

**Current expected source**

- Document: `L_2018268EN.01005301`
- Chunk: `chunk_10`

**Expected chunk — content to compare**

> `chunk_10` says EVR data must be retained for 10 years after a vehicle registration is withdrawn, with at least the first three years available online; later data may be archived. It also says changes must be recorded, describes user-access requests and access rights, and begins a security section.

**Retrieved chunk — the chunk the mechanism selected instead**

> `L_2018268EN.01005301`, `chunk_3`: “The Agency shall set up and maintain the European Vehicle Register ... [It] shall be a centralised register and provide a harmonised interface ... for the consultation, registration of vehicle and data management.” It also covers decentralised registration functions and transfer of vehicle data from national registers.

**What actually happened**

- The expected document was retrieved.
- The expected `chunk_10` was not retrieved.
- A different chunk from the same document, `chunk_3`, was retrieved and appears to discuss the European Vehicle Register as a centralised register, including consultation, registration, and data management.

**Why the current wording is risky**

The question adds a data-protection framing that the retrieved material may not support. It would be misleading to score a system down for failing to find a privacy rule when the source is actually about registry administration.

**My recommendation: REWRITE this into a clean, source-backed retrieval case.**

Proposed replacement:

> What data-management functions does the European Vehicle Register provide?

Proposed expected source:

- Document: `L_2018268EN.01005301`
- Chunk: `chunk_3`

Reply: `3: REWRITE`

---

## Case natural_004 — Serbia agreement

**Question**

> When may personal data be communicated under the Serbia agreement?

**Current expected source**

- Document: `L_2007334EN.01004501`
- Chunk: `chunk_7`

**Expected chunk — what it actually contains**

> `L_2007334EN.01004501`, `chunk_7` concerns transit/readmission operations: transit applications, admission responses, airport transit visas, assistance in transit operations, and costs. It does **not** contain a personal-data communication rule.

**Retrieved chunks — why they looked relevant**

> `L_2007334EN.01014801`, `chunk_7` (Moldova, not Serbia): “The communication of personal data shall only take place if such communication is necessary for the implementation of this Agreement ...” It then states purpose-limitation, proportionality, accuracy, retention, and related safeguards.

> `L_2011052EN.01004501`, `chunk_8`: contains the same kind of data-protection safeguards, including that data must be collected for the agreement's explicit legitimate purpose and not further processed incompatibly.

**What actually happened**

- Neither the expected document nor chunk was retrieved.
- The strongest similar-looking result referred to a **Moldova** agreement, not Serbia.

**Why this should not remain in the evaluation set**

This looks like a target-source mismatch, not a fair retrieval failure. It may have arisen from a similar agreement title, a copied identifier, or an incorrect source assumption. We should not include it in measured results until its source is verified.

**My recommendation: DROP for this pilot.**

Later, if you find a verified Serbia-agreement provision, we can restore it as a new case with its exact document/chunk.

Reply: `4: DROP`

---

## Recommendation before expansion — plain-language version

You do **not** need to approve every case before we add more data. The safe next move is:

1. Keep only cases whose answer is visibly supported by their designated source.
2. Rewrite cases where the source is good but the question overstates what it says.
3. Remove cases with a document/country/topic mismatch.
4. Expand from a reviewed seed set, not from automatically generated targets alone.

For this first set, my suggested disposition is:

- `natural_001`: **keep** — Article 12 in the expected chunk directly supports it.
- `natural_002`: **keep** — Article 12(3) in the expected chunk directly supports it.
- `natural_003`: **rewrite** using the proposed Vehicle Register question and `chunk_3`.
- `natural_004`: **drop** until a Serbia-specific source is verified.

After these four decisions, I can prepare the next review batch in the same format: natural language, one clearly identified source, and a short explanation of why the source answers the question. That gives you a credible evaluation set without asking you to audit the entire knowledge graph.
