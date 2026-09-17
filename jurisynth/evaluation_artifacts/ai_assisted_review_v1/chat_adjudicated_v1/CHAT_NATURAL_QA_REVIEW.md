# Jurisynth Natural-QA Reference and Retrieval Review

> AI-assisted review of the supplied Codex packets. This is not expert legal review.

Important: these packets contain no system answers, so this file does **not** assign system PASS/PARTIAL/FAIL or legal-QA accuracy. It validates the proposed reference/question and reviews whether stored retrieval is answer-bearing.

## Summary

- Cases reviewed: **14**
- Reference/question decisions: **valid: 8**, **revise: 6**
- Retrieval labels: **partial: 5**, **insufficient: 5**, **sufficient: 3**, **irrelevant: 1**

## global_natural_001

**Decision:** valid

**Final question:** What must an authority tell the applicant authority when it refuses or withholds requested assistance?

**Verified reference answer:** It must notify the applicant authority of the decision to withhold/deny assistance and the reasons for that decision, without delay. The source does not supply a fixed numeric deadline or an appeal right.

**Supporting source excerpt/row:** If assistance is withheld or denied, the decision and the reasons therefor must be notified to the applicant authority without delay.

**Expected source keys:** L_1994001EN.01000101 / chunk_50

**Retrieval review:** partial

**Helpful retrieved source keys:** L_2010084EN.01000101 / chunk_7, L_2009284EN.01000101 / chunk_29, L_2010268EN.01000101 / chunk_13, L_2012121EN.01000101 / chunk_10

**Scope/date/version caveats:** The retrieved passages support communicating grounds for refusal, but they are from other instruments/versions and do not establish the expected source's full 'decision + reasons + without delay' formulation. Do not infer source equivalence.

**Confidence:** high

**Review notes:** Reference is sound. Retrieval is useful but incomplete for the intended rule.

## global_natural_002

**Decision:** valid

**Final question:** What interim protection may a judicial authority provide to prevent an imminent intellectual-property infringement?

**Verified reference answer:** At the applicant's request, the judicial authority may issue an interlocutory injunction to prevent imminent infringement, provisionally forbid continuation of the alleged infringement, or make continuation subject to guarantees intended to compensate the right holder if infringement is determined. Under the same conditions, an injunction may also issue against an intermediary whose services are used by a third party to infringe an intellectual-property right.

**Supporting source excerpt/row:** The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.

**Expected source keys:** L_2008289EN.01000101 / chunk_48

**Retrieval review:** partial

**Helpful retrieved source keys:** L_2004157EN.01004501 / chunk_7

**Scope/date/version caveats:** The helpful retrieved passage is substantively close but is not the expected source. Preserve the applicant-request condition and national-law qualification; do not assume alternate-instrument equivalence or current applicability.

**Confidence:** high

**Review notes:** Draft reference is substantively correct. The alternate retrieved provision is answer-bearing textually but not enough to establish the intended authority.

## global_natural_003

**Decision:** revise

**Final question:** Under the aquatic-toxicity testing procedure described in the source, what information must the test report contain?

**Verified reference answer:** The report must cover four groups: (1) the test substance—physical nature/relevant physicochemical properties plus chemical identification, purity and, where appropriate, the analytical quantification method; (2) the test species—scientific name and, where relevant, strain, size, supplier and pretreatment; (3) test conditions—procedure, design, stock-solution preparation/renewal, any solubilising agent, nominal and measured concentrations and variability, dilution-water characteristics, within-vessel water quality, and feeding details; and (4) results—control validity/mortality, statistical methods and treatment, fish weights and growth rates, statistical results including LOEC/NOEC or ECx where possible, and unusual reactions/visible effects.

**Supporting source excerpt/row:** The test report must include the following information: 2.3.1. Test substance: ... 2.3.2. Test species: ... 2.3.3. Test conditions: ... 2.3.4. Results:

**Expected source keys:** L_2008142EN.01000101 / chunk_319

**Retrieval review:** insufficient

**Helpful retrieved source keys:** None

**Scope/date/version caveats:** Retrieved material concerns other aquatic/ecotoxicity procedures and does not supply this source's report checklist. Do not substitute related test methods.

**Confidence:** high

**Review notes:** The draft reference was too skeletal because it omitted the Results category and most required checklist content. Revised reference supplied.

## global_natural_004

**Decision:** revise

**Final question:** What minimum free volatile acid content does the source require for the described heading-2001 products preserved by vinegar or acetic acid?

**Verified reference answer:** At least 0.5% by weight, expressed as acetic acid. This is a stated requirement, not proof that every other classification condition is satisfied; the source also gives an additional salt-content condition for mushrooms of subheading 2001 90 50.

**Supporting source excerpt/row:** For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid.

**Expected source keys:** L_2008291EN.01000101 / chunk_112

**Retrieval review:** sufficient

**Helpful retrieved source keys:** L_2008291EN.01000101 / chunk_112, L_2022282EN.01000101 / chunk_34, L_202402522EN / chunk_34, L_202501926EN / chunk_34

**Scope/date/version caveats:** The original wording 'to fall under heading 2001' could imply the acid threshold is sufficient by itself. The revised question asks only for the stated minimum. Later tariff versions repeat the rule but current applicability is not adjudicated here.

**Confidence:** high

**Review notes:** Exact expected chunk was retrieved; answer-bearing retrieval is sufficient.

## global_natural_005

**Decision:** valid

**Final question:** When does wood powder qualify as wood flour for tariff-heading purposes?

**Verified reference answer:** For heading 4405, wood flour is wood powder of which not more than 8% by weight is retained by a sieve with an aperture of 0.63 mm.

**Supporting source excerpt/row:** For the purposes of heading 4405 , 'wood flour' means wood powder of which not more than 8 % by weight is retained by a sieve with an aperture of 0,63 mm.

**Expected source keys:** L_2011282EN.01000101 / chunk_271

**Retrieval review:** partial

**Helpful retrieved source keys:** L_1994345EN.01000101 / chunk_280

**Scope/date/version caveats:** The retrieved 1994 tariff text states the same definition, but it is not the expected 2011 source. Temporal/version equivalence must not be assumed solely from matching wording.

**Confidence:** high

**Review notes:** Reference is valid; retrieval is textually answer-bearing but source-version mismatch keeps it partial.

## global_natural_006

**Decision:** valid

**Final question:** What is treated as water-pipe tobacco for the relevant tariff subheading?

**Verified reference answer:** For subheading 2403 11, water-pipe tobacco is tobacco intended for smoking in a water pipe and consisting of tobacco and glycerol. Aromatic oils/extracts, molasses or sugar, and fruit flavouring are optional; tobacco-free products intended for water-pipe smoking are excluded.

**Supporting source excerpt/row:** For the purposes of subheading 2403 11, the expression 'water-pipe tobacco' means tobacco intended for smoking in a water pipe and which consists of a mixture of tobacco and glycerol, whether or not containing aromatic oils and extracts, molasses or sugar, and whether or not flavoured with fruit. However, tobacco-free products intended for smoking in a water pipe are excluded from this subheading.

**Expected source keys:** L_2016294EN.01000101 / chunk_164

**Retrieval review:** partial

**Helpful retrieved source keys:** L_2021385EN.01000101 / chunk_166, L_2021414EN.01000101 / chunk_167, L_2020361EN.01000101 / chunk_166

**Scope/date/version caveats:** Several retrieved tariff versions repeat the definition, but the expected 2016 source was not recovered. Do not silently equate tariff versions or infer current applicability.

**Confidence:** high

**Review notes:** Reference is valid; alternate-version retrieval is strong textually but remains partial for source-specific evaluation.

## global_natural_007

**Decision:** valid

**Final question:** How is the country of origin determined for a good or part produced from a blank under the stated same-heading rule?

**Verified reference answer:** If the good/part and blank satisfy the stated HS GRI 2(a) same-heading/subheading/subdivision condition, origin is the country where every working edge, working surface and working part was configured to final shape and dimension, provided the imported blank was incapable of functioning and was not advanced beyond the stated initial-stamping/material-removal stage. If those paragraph-(a) criteria are not met, origin is the origin of the blank.

**Supporting source excerpt/row:** (a) The country of origin of a good or part produced from a blank which by application of the Harmonized System General Interpretative Rule 2(a) is classified in the same heading, subheading or subdivision as the complete or finished good or part, shall be the country in which every working edge, working surface and working part was configured to final shape and dimension, provided, in its imported condition, the blank from which it was produced: (i) was not capable of functioning, and (ii) was not advanced beyond the initial stamping process or any processing required to remove the material from the forging platter or casting mould; (b) If the criteria in paragraph (a) are not satisfied, the country of origin is the country of origin of the blank of this Chapter.

**Expected source keys:** L_2015343EN.01000101 / chunk_129

**Retrieval review:** irrelevant

**Helpful retrieved source keys:** None

**Scope/date/version caveats:** Retrieved country-of-origin material concerns unrelated produce/labelling/origin contexts, not this blank-finishing rule.

**Confidence:** high

**Review notes:** Clear controlled miss: retrieval does not bear the answer despite some lexical country-of-origin overlap.

## global_natural_008

**Decision:** revise

**Final question:** Under the supplied TIR Convention provision, when does the Convention enter into force after the required Article 52(1) States complete the specified signature or instrument steps?

**Verified reference answer:** It enters into force six months after five States referred to in Article 52(1) have signed without reservation of ratification, acceptance or approval, or deposited the specified instruments. For a further Contracting Party, it enters into force six months after that party deposits its instrument.

**Supporting source excerpt/row:** This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.

**Expected source keys:** L_2009165EN.01000101 / chunk_10

**Retrieval review:** insufficient

**Helpful retrieved source keys:** None

**Scope/date/version caveats:** Retrieved passages concern other conventions with different thresholds and entry-into-force rules (e.g. four States or other deposit counts). They are not substitutes and could actively mislead. 'Eligible States' was tightened to 'States referred to in Article 52(1)'.

**Confidence:** high

**Review notes:** Reference corrected for exact source scope; retrieval does not support the TIR rule.

## global_natural_009

**Decision:** valid

**Final question:** Who may request a meeting of the Committee on Trade in Goods, and what is it meant to consider?

**Verified reference answer:** A Party or the Trade Committee may request the meeting. The Committee on Trade in Goods is to consider any matter arising under the relevant Chapter and comprises representatives of the Parties.

**Supporting source excerpt/row:** The Committee on Trade in Goods established pursuant to Article 15.2.1 (Specialised Committees) shall meet on the request of a Party or of the Trade Committee to consider any matter arising under this Chapter and comprise representatives of the Parties.

**Expected source keys:** L_2011127EN.01000101 / chunk_8

**Retrieval review:** insufficient

**Helpful retrieved source keys:** None

**Scope/date/version caveats:** Retrieved passages discuss the Customs Committee, Trade Committee, or other committees. These are not interchangeable with the Committee on Trade in Goods.

**Confidence:** high

**Review notes:** Same-document retrieval does not itself make the evidence answer-bearing when it concerns a different committee.

## global_natural_010

**Decision:** valid

**Final question:** When may customs authorities carry out a subsequent verification of a proof of origin under the stated Protocol?

**Verified reference answer:** Subsequent verification is provided for at random or when the importing country's customs authorities have reasonable doubts about document authenticity, the products' originating status, or fulfilment of other requirements of the Protocol.

**Supporting source excerpt/row:** Subsequent verifications of proofs of origin shall be carried out at random or whenever the customs authorities of the importing country have reasonable doubts as to the authenticity of such documents, the originating status of the products concerned or the fulfilment of the other requirements of this Protocol.

**Expected source keys:** L_2007345EN.01000101 / chunk_39

**Retrieval review:** partial

**Helpful retrieved source keys:** L_2011127EN.01000101 / chunk_138, L_2019222EN.01000101 / chunk_17, L_2012111EN.01000101 / chunk_36, L_202402144EN / chunk_15

**Scope/date/version caveats:** Several retrieved Protocols contain substantially similar verification rules, but the expected Protocol was not retrieved. Agreement-specific scope and wording must not be silently treated as equivalent.

**Confidence:** high

**Review notes:** Strong semantic retrieval, but alternate-instrument provenance prevents a 'sufficient' source-specific label.

## global_natural_011

**Decision:** valid

**Final question:** Which measurements must be collected during the stated road-load curve determination procedure?

**Verified reference answer:** Elapsed time, vehicle speed, and air velocity relative to the vehicle (wind speed and direction) must be measured at 5 Hz. Ambient temperature must be synchronised and sampled at a minimum frequency of 1 Hz.

**Supporting source excerpt/row:** During the procedure, elapsed time, vehicle speed, and air velocity (wind speed, direction) relative to the vehicle, shall be measured at a frequency of 5 Hz. Ambient temperature shall be synchronised and sampled at a minimum frequency of 1 Hz.

**Expected source keys:** L_2017175EN.01000101 / chunk_157

**Retrieval review:** insufficient

**Helpful retrieved source keys:** None

**Scope/date/version caveats:** Retrieved chunks are from nearby road-load sections and related procedures but do not supply the required data-collection frequencies in the expected clause.

**Confidence:** high

**Review notes:** Domain/topic proximity is not enough; the actual requested measurements were not recovered.

## global_natural_018

**Decision:** revise

**Final question:** In C_2022160EN.01002701 table_1, what annual and total allocation quantities are recorded for Audi Brussels for 2021–2025?

**Verified reference answer:** The row for Audi Brussels records 3,076 for each of 2021, 2022, 2023, 2024 and 2025, for a total allocation of 15,380.

**Supporting source excerpt/row:** Audi Brussels NV | Audi Brussels | 3 076 | 3 076 | 3 076 | 3 076 | 3 076 | 15 380

**Expected source keys:** C_2022160EN.01002701 / table_1

**Retrieval review:** insufficient

**Helpful retrieved source keys:** None

**Scope/date/version caveats:** Allocation tables can be revised for the same years. The question is made document/table-specific so a later revision is not silently substituted. Retrieved material contains allocation context but not the Audi row/quantities.

**Confidence:** high

**Review notes:** Reference table is internally clear; retrieval does not recover the answer-bearing row.

## global_natural_019

**Decision:** revise

**Final question:** In C_2022236EN.01000501 table_11, what annual and total allocation quantities are recorded for the Lakeland Dairies Killeshandra Site for 2021–2025?

**Verified reference answer:** The row records 4,334 for each of 2021, 2022, 2023, 2024 and 2025, for a total allocation of 21,670.

**Supporting source excerpt/row:** Lakeland Dairies Killeshandra Site | Lakeland Dairies Co-operative Society Ltd. | 4 334 | 4 334 | 4 334 | 4 334 | 4 334 | 21 670

**Expected source keys:** C_2022236EN.01000501 / table_11

**Retrieval review:** sufficient

**Helpful retrieved source keys:** C_2022236EN.01000501 / table_11

**Scope/date/version caveats:** The question is made document/table-specific because later revisions for the same period may differ.

**Confidence:** high

**Review notes:** Exact expected table row was retrieved.

## global_natural_020

**Decision:** revise

**Final question:** In L_2010041EN.01000801 table_10, how does the table distinguish Metier*Fleet segment (Cell), Metier, and Fleet segment across the displayed geographic aggregation levels?

**Verified reference answer:** The table maps Metier*Fleet segment (Cell) to A / A1 / A2 / A3; Metier to B / B1 / B2 / B3; and Fleet segment to C / C1 / C2 / C3 across the displayed base, sub-region-or-fishing-ground, region and supra-region columns. The table itself does not provide a substantive interpretation of what the letter symbols mean beyond these mappings.

**Supporting source excerpt/row:** Metier*Fleet segment (Cell) | A | A1 | A2 | A3; Metier | B | B1 | B2 | B3; Fleet segment | C | C1 | C2 | C3

**Expected source keys:** L_2010041EN.01000801 / table_10

**Retrieval review:** sufficient

**Helpful retrieved source keys:** L_2010041EN.01000801 / table_10

**Scope/date/version caveats:** Do not infer substantive meaning for A/B/C or numbered variants beyond the table's displayed mappings. Question is made table-specific for reproducibility.

**Confidence:** high

**Review notes:** The three expected rows were recovered as table evidence; sufficient.
