# Jurisynth Legal-Text NLI Adjudication

> AI-assisted source-based adjudication of the 90 supplied synthetic pairs. This is a component diagnostic, not expert-certified legal ground truth and not a determination of real legal conflicts.

## Summary

- Pairs reviewed: **90**
- Premise supported by supplied source: **90/90**
- Entailment: **30**
- Contradiction: **30**
- Neutral: **30**
- Reject/uncertain: **0**

No model thresholds were tuned. Labels were assigned from the exact premise→hypothesis relation using only the supplied source context and stated scope. The 30/30/30 final distribution is an outcome of the adjudication, not a balancing constraint.

## legal_nli_001

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2015343EN.01000101 / chunk_129
- **Rationale:** The rule makes the finishing-country result conditional on every working edge/surface/part being configured, the imported blank being incapable of functioning, and the stated processing limit; otherwise the blank's origin controls. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** (a) The country of origin of a good or part produced from a blank which by application of the Harmonized System General Interpretative Rule 2(a) is classified in the same heading, subheading or subdivision as the complete or finished good or part, shall be the country in which every working edge, working surface and working part was configured to final shape and dimension, provided, in its imported condition, the blank from which it was produced: (i) was not capable of functioning, and (ii) was not advanced beyond the initial stamping process or any processing required to remove the material from the forging platter or casting mould; (b) If the criteria in paragraph (a) are not satisfied, the country of origin is the country of origin of the blank of this Chapter.
- **Scope correction:** None

## legal_nli_002

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.98
- **Source:** L_2008289EN.01000101 / chunk_48
- **Rationale:** The rule permits applicant-requested interlocutory injunctions for imminent infringement, provisional continuation restrictions/guarantees, and injunctions against qualifying intermediaries. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.
- **Exact supporting quote:** The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.
- **Scope correction:** Clarify that the guarantee language makes continuation of the alleged infringement subject to lodging guarantees intended to compensate the right holder if infringement is determined; the judicial authority 'may' issue the measure.

## legal_nli_003

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2007345EN.01000101 / chunk_39
- **Rationale:** The rule expressly permits random verification and verification triggered by reasonable doubts about authenticity, originating status, or other Protocol requirements. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** Subsequent verifications of proofs of origin shall be carried out at random or whenever the customs authorities of the importing country have reasonable doubts as to the authenticity of such documents, the originating status of the products concerned or the fulfilment of the other requirements of this Protocol.
- **Scope correction:** None

## legal_nli_004

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.98
- **Source:** L_2011127EN.01000101 / chunk_8
- **Rationale:** The Committee on Trade in Goods may be convened at the request of a Party or the Trade Committee and comprises representatives of the Parties. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.
- **Exact supporting quote:** The Committee on Trade in Goods established pursuant to Article 15.2.1 (Specialised Committees) shall meet on the request of a Party or of the Trade Committee to consider any matter arising under this Chapter and comprise representatives of the Parties.
- **Scope correction:** None

## legal_nli_005

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2016294EN.01000101 / chunk_164
- **Rationale:** The definition requires tobacco and glycerol; listed additives and fruit flavouring are optional, and tobacco-free water-pipe products are excluded. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** For the purposes of subheading 2403 11, the expression 'water-pipe tobacco' means tobacco intended for smoking in a water pipe and which consists of a mixture of tobacco and glycerol, whether or not containing aromatic oils and extracts, molasses or sugar, and whether or not flavoured with fruit. However, tobacco-free products intended for smoking in a water pipe are excluded from this subheading.
- **Scope correction:** None

## legal_nli_006

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2011282EN.01000101 / chunk_271
- **Rationale:** The wood-flour definition allows no more than 8% by weight retained on a 0.63 mm sieve. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** For the purposes of heading 4405 , 'wood flour' means wood powder of which not more than 8 % by weight is retained by a sieve with an aperture of 0,63 mm.
- **Scope correction:** None

## legal_nli_007

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.96
- **Source:** L_2009165EN.01000101 / chunk_10
- **Rationale:** The premise gives an entry-into-force rule but does not identify whether any particular named State has deposited an instrument; the historical event claim is neutral.
- **Exact supporting quote:** This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.
- **Scope correction:** For exact source scope, replace 'eligible States' with 'States referred to in Article 52, paragraph 1'.

## legal_nli_008

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.98
- **Source:** L_2011282EN.01000101 / chunk_271
- **Rationale:** The wood-flour definition allows no more than 8% by weight retained on a 0.63 mm sieve. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.
- **Exact supporting quote:** For the purposes of heading 4405 , 'wood flour' means wood powder of which not more than 8 % by weight is retained by a sieve with an aperture of 0,63 mm.
- **Scope correction:** None

## legal_nli_009

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.98
- **Source:** L_2016294EN.01000101 / chunk_164
- **Rationale:** The definition requires tobacco and glycerol; listed additives and fruit flavouring are optional, and tobacco-free water-pipe products are excluded. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.
- **Exact supporting quote:** For the purposes of subheading 2403 11, the expression 'water-pipe tobacco' means tobacco intended for smoking in a water pipe and which consists of a mixture of tobacco and glycerol, whether or not containing aromatic oils and extracts, molasses or sugar, and whether or not flavoured with fruit. However, tobacco-free products intended for smoking in a water pipe are excluded from this subheading.
- **Scope correction:** None

## legal_nli_010

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2011127EN.01000101 / chunk_8
- **Rationale:** The Committee on Trade in Goods may be convened at the request of a Party or the Trade Committee and comprises representatives of the Parties. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** The Committee on Trade in Goods established pursuant to Article 15.2.1 (Specialised Committees) shall meet on the request of a Party or of the Trade Committee to consider any matter arising under this Chapter and comprise representatives of the Parties.
- **Scope correction:** None

## legal_nli_011

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2016294EN.01000101 / chunk_164
- **Rationale:** The definition requires tobacco and glycerol; listed additives and fruit flavouring are optional, and tobacco-free water-pipe products are excluded. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** For the purposes of subheading 2403 11, the expression 'water-pipe tobacco' means tobacco intended for smoking in a water pipe and which consists of a mixture of tobacco and glycerol, whether or not containing aromatic oils and extracts, molasses or sugar, and whether or not flavoured with fruit. However, tobacco-free products intended for smoking in a water pipe are excluded from this subheading.
- **Scope correction:** None

## legal_nli_012

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2009165EN.01000101 / chunk_10
- **Rationale:** The initial threshold is five Article 52(1) States and the interval is six months; further Contracting Parties also face a six-month interval after deposit. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.
- **Scope correction:** For exact source scope, replace 'eligible States' with 'States referred to in Article 52, paragraph 1'.

## legal_nli_013

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.98
- **Source:** L_1994001EN.01000101 / chunk_50
- **Rationale:** A withholding or denial requires notification of both the decision and reasons to the applicant authority without delay. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.
- **Exact supporting quote:** If assistance is withheld or denied, the decision and the reasons therefor must be notified to the applicant authority without delay.
- **Scope correction:** None

## legal_nli_014

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2011282EN.01000101 / chunk_271
- **Rationale:** The wood-flour definition allows no more than 8% by weight retained on a 0.63 mm sieve. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** For the purposes of heading 4405 , 'wood flour' means wood powder of which not more than 8 % by weight is retained by a sieve with an aperture of 0,63 mm.
- **Scope correction:** None

## legal_nli_015

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_1994001EN.01000101 / chunk_50
- **Rationale:** A withholding or denial requires notification of both the decision and reasons to the applicant authority without delay. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** If assistance is withheld or denied, the decision and the reasons therefor must be notified to the applicant authority without delay.
- **Scope correction:** None

## legal_nli_016

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.98
- **Source:** L_2011282EN.01000101 / chunk_271
- **Rationale:** The wood-flour definition allows no more than 8% by weight retained on a 0.63 mm sieve. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.
- **Exact supporting quote:** For the purposes of heading 4405 , 'wood flour' means wood powder of which not more than 8 % by weight is retained by a sieve with an aperture of 0,63 mm.
- **Scope correction:** None

## legal_nli_017

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2008291EN.01000101 / chunk_112
- **Rationale:** The rule sets a minimum free volatile acid content of 0.5% by weight, expressed as acetic acid, for the described heading-2001 products. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid.
- **Scope correction:** None

## legal_nli_018

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.99
- **Source:** L_2008291EN.01000101 / chunk_112
- **Rationale:** The premise describes the historical/source rule but says nothing about whether it remained unchanged or legally applicable in September 2026; the current-applicability claim is neutral.
- **Exact supporting quote:** For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid.
- **Scope correction:** None

## legal_nli_019

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2009165EN.01000101 / chunk_10
- **Rationale:** The initial threshold is five Article 52(1) States and the interval is six months; further Contracting Parties also face a six-month interval after deposit. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.
- **Scope correction:** For exact source scope, replace 'eligible States' with 'States referred to in Article 52, paragraph 1'.

## legal_nli_020

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2007345EN.01000101 / chunk_39
- **Rationale:** The rule expressly permits random verification and verification triggered by reasonable doubts about authenticity, originating status, or other Protocol requirements. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** Subsequent verifications of proofs of origin shall be carried out at random or whenever the customs authorities of the importing country have reasonable doubts as to the authenticity of such documents, the originating status of the products concerned or the fulfilment of the other requirements of this Protocol.
- **Scope correction:** None

## legal_nli_021

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.98
- **Source:** L_2007345EN.01000101 / chunk_39
- **Rationale:** The rule expressly permits random verification and verification triggered by reasonable doubts about authenticity, originating status, or other Protocol requirements. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.
- **Exact supporting quote:** Subsequent verifications of proofs of origin shall be carried out at random or whenever the customs authorities of the importing country have reasonable doubts as to the authenticity of such documents, the originating status of the products concerned or the fulfilment of the other requirements of this Protocol.
- **Scope correction:** None

## legal_nli_022

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2011127EN.01000101 / chunk_8
- **Rationale:** The Committee on Trade in Goods may be convened at the request of a Party or the Trade Committee and comprises representatives of the Parties. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** The Committee on Trade in Goods established pursuant to Article 15.2.1 (Specialised Committees) shall meet on the request of a Party or of the Trade Committee to consider any matter arising under this Chapter and comprise representatives of the Parties.
- **Scope correction:** None

## legal_nli_023

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2009165EN.01000101 / chunk_10
- **Rationale:** The initial threshold is five Article 52(1) States and the interval is six months; further Contracting Parties also face a six-month interval after deposit. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.
- **Scope correction:** For exact source scope, replace 'eligible States' with 'States referred to in Article 52, paragraph 1'.

## legal_nli_024

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2008291EN.01000101 / chunk_112
- **Rationale:** The rule sets a minimum free volatile acid content of 0.5% by weight, expressed as acetic acid, for the described heading-2001 products. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid.
- **Scope correction:** None

## legal_nli_025

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2008289EN.01000101 / chunk_48
- **Rationale:** The rule permits applicant-requested interlocutory injunctions for imminent infringement, provisional continuation restrictions/guarantees, and injunctions against qualifying intermediaries. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.
- **Scope correction:** Clarify that the guarantee language makes continuation of the alleged infringement subject to lodging guarantees intended to compensate the right holder if infringement is determined; the judicial authority 'may' issue the measure.

## legal_nli_026

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2008289EN.01000101 / chunk_48
- **Rationale:** The rule permits applicant-requested interlocutory injunctions for imminent infringement, provisional continuation restrictions/guarantees, and injunctions against qualifying intermediaries. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.
- **Scope correction:** Clarify that the guarantee language makes continuation of the alleged infringement subject to lodging guarantees intended to compensate the right holder if infringement is determined; the judicial authority 'may' issue the measure.

## legal_nli_027

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2017175EN.01000101 / chunk_157
- **Rationale:** The procedure requires time, speed and relative air velocity at 5 Hz, ambient temperature at at least 1 Hz, and at least ten coastdown runs, five each direction. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** During the procedure, elapsed time, vehicle speed, and air velocity (wind speed, direction) relative to the vehicle, shall be measured at a frequency of 5 Hz. Ambient temperature shall be synchronised and sampled at a minimum frequency of 1 Hz. The measurements shall be carried out in opposite directions until a minimum of ten consecutive runs (five in each direction) have been obtained.
- **Scope correction:** None

## legal_nli_028

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2008289EN.01000101 / chunk_48
- **Rationale:** The rule permits applicant-requested interlocutory injunctions for imminent infringement, provisional continuation restrictions/guarantees, and injunctions against qualifying intermediaries. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.
- **Scope correction:** Clarify that the guarantee language makes continuation of the alleged infringement subject to lodging guarantees intended to compensate the right holder if infringement is determined; the judicial authority 'may' issue the measure.

## legal_nli_029

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.94
- **Source:** L_2008291EN.01000101 / chunk_112
- **Rationale:** The premise states a necessary acid-content condition, but it does not say that satisfying that condition alone satisfies every other classification condition. The sufficiency claim is therefore neutral.
- **Exact supporting quote:** For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid.
- **Scope correction:** None

## legal_nli_030

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2017175EN.01000101 / chunk_157
- **Rationale:** The procedure requires time, speed and relative air velocity at 5 Hz, ambient temperature at at least 1 Hz, and at least ten coastdown runs, five each direction. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** During the procedure, elapsed time, vehicle speed, and air velocity (wind speed, direction) relative to the vehicle, shall be measured at a frequency of 5 Hz. Ambient temperature shall be synchronised and sampled at a minimum frequency of 1 Hz. The measurements shall be carried out in opposite directions until a minimum of ten consecutive runs (five in each direction) have been obtained.
- **Scope correction:** None

## legal_nli_031

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.98
- **Source:** L_1994001EN.01000101 / chunk_50
- **Rationale:** A withholding or denial requires notification of both the decision and reasons to the applicant authority without delay. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.
- **Exact supporting quote:** If assistance is withheld or denied, the decision and the reasons therefor must be notified to the applicant authority without delay.
- **Scope correction:** None

## legal_nli_032

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2011282EN.01000101 / chunk_271
- **Rationale:** The wood-flour definition allows no more than 8% by weight retained on a 0.63 mm sieve. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** For the purposes of heading 4405 , 'wood flour' means wood powder of which not more than 8 % by weight is retained by a sieve with an aperture of 0,63 mm.
- **Scope correction:** None

## legal_nli_033

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2016294EN.01000101 / chunk_164
- **Rationale:** The definition requires tobacco and glycerol; listed additives and fruit flavouring are optional, and tobacco-free water-pipe products are excluded. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** For the purposes of subheading 2403 11, the expression 'water-pipe tobacco' means tobacco intended for smoking in a water pipe and which consists of a mixture of tobacco and glycerol, whether or not containing aromatic oils and extracts, molasses or sugar, and whether or not flavoured with fruit. However, tobacco-free products intended for smoking in a water pipe are excluded from this subheading.
- **Scope correction:** None

## legal_nli_034

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.98
- **Source:** L_2011127EN.01000101 / chunk_8
- **Rationale:** The Committee on Trade in Goods may be convened at the request of a Party or the Trade Committee and comprises representatives of the Parties. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.
- **Exact supporting quote:** The Committee on Trade in Goods established pursuant to Article 15.2.1 (Specialised Committees) shall meet on the request of a Party or of the Trade Committee to consider any matter arising under this Chapter and comprise representatives of the Parties.
- **Scope correction:** None

## legal_nli_035

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.98
- **Source:** L_2017175EN.01000101 / chunk_157
- **Rationale:** The procedure requires time, speed and relative air velocity at 5 Hz, ambient temperature at at least 1 Hz, and at least ten coastdown runs, five each direction. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.
- **Exact supporting quote:** During the procedure, elapsed time, vehicle speed, and air velocity (wind speed, direction) relative to the vehicle, shall be measured at a frequency of 5 Hz. Ambient temperature shall be synchronised and sampled at a minimum frequency of 1 Hz. The measurements shall be carried out in opposite directions until a minimum of ten consecutive runs (five in each direction) have been obtained.
- **Scope correction:** None

## legal_nli_036

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2008289EN.01000101 / chunk_48
- **Rationale:** The rule permits applicant-requested interlocutory injunctions for imminent infringement, provisional continuation restrictions/guarantees, and injunctions against qualifying intermediaries. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.
- **Scope correction:** Clarify that the guarantee language makes continuation of the alleged infringement subject to lodging guarantees intended to compensate the right holder if infringement is determined; the judicial authority 'may' issue the measure.

## legal_nli_037

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.98
- **Source:** L_2015343EN.01000101 / chunk_129
- **Rationale:** The rule makes the finishing-country result conditional on every working edge/surface/part being configured, the imported blank being incapable of functioning, and the stated processing limit; otherwise the blank's origin controls. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.
- **Exact supporting quote:** (a) The country of origin of a good or part produced from a blank which by application of the Harmonized System General Interpretative Rule 2(a) is classified in the same heading, subheading or subdivision as the complete or finished good or part, shall be the country in which every working edge, working surface and working part was configured to final shape and dimension, provided, in its imported condition, the blank from which it was produced: (i) was not capable of functioning, and (ii) was not advanced beyond the initial stamping process or any processing required to remove the material from the forging platter or casting mould; (b) If the criteria in paragraph (a) are not satisfied, the country of origin is the country of origin of the blank of this Chapter.
- **Scope correction:** None

## legal_nli_038

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.96
- **Source:** L_2009165EN.01000101 / chunk_10
- **Rationale:** The premise describes Convention entry into force, not the effective date of every later amendment. The amendment-timing claim is not established and is neutral.
- **Exact supporting quote:** This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.
- **Scope correction:** For exact source scope, replace 'eligible States' with 'States referred to in Article 52, paragraph 1'.

## legal_nli_039

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.98
- **Source:** L_2007345EN.01000101 / chunk_39
- **Rationale:** The rule expressly permits random verification and verification triggered by reasonable doubts about authenticity, originating status, or other Protocol requirements. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.
- **Exact supporting quote:** Subsequent verifications of proofs of origin shall be carried out at random or whenever the customs authorities of the importing country have reasonable doubts as to the authenticity of such documents, the originating status of the products concerned or the fulfilment of the other requirements of this Protocol.
- **Scope correction:** None

## legal_nli_040

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_1994001EN.01000101 / chunk_50
- **Rationale:** A withholding or denial requires notification of both the decision and reasons to the applicant authority without delay. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** If assistance is withheld or denied, the decision and the reasons therefor must be notified to the applicant authority without delay.
- **Scope correction:** None

## legal_nli_041

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2011127EN.01000101 / chunk_8
- **Rationale:** The Committee on Trade in Goods may be convened at the request of a Party or the Trade Committee and comprises representatives of the Parties. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** The Committee on Trade in Goods established pursuant to Article 15.2.1 (Specialised Committees) shall meet on the request of a Party or of the Trade Committee to consider any matter arising under this Chapter and comprise representatives of the Parties.
- **Scope correction:** None

## legal_nli_042

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2011282EN.01000101 / chunk_271
- **Rationale:** The wood-flour definition allows no more than 8% by weight retained on a 0.63 mm sieve. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** For the purposes of heading 4405 , 'wood flour' means wood powder of which not more than 8 % by weight is retained by a sieve with an aperture of 0,63 mm.
- **Scope correction:** None

## legal_nli_043

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2008291EN.01000101 / chunk_112
- **Rationale:** The rule sets a minimum free volatile acid content of 0.5% by weight, expressed as acetic acid, for the described heading-2001 products. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid.
- **Scope correction:** None

## legal_nli_044

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.99
- **Source:** L_2017175EN.01000101 / chunk_157
- **Rationale:** The premise describes the historical/source rule but says nothing about whether it remained unchanged or legally applicable in September 2026; the current-applicability claim is neutral.
- **Exact supporting quote:** During the procedure, elapsed time, vehicle speed, and air velocity (wind speed, direction) relative to the vehicle, shall be measured at a frequency of 5 Hz. Ambient temperature shall be synchronised and sampled at a minimum frequency of 1 Hz. The measurements shall be carried out in opposite directions until a minimum of ten consecutive runs (five in each direction) have been obtained.
- **Scope correction:** None

## legal_nli_045

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2007345EN.01000101 / chunk_39
- **Rationale:** The rule expressly permits random verification and verification triggered by reasonable doubts about authenticity, originating status, or other Protocol requirements. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** Subsequent verifications of proofs of origin shall be carried out at random or whenever the customs authorities of the importing country have reasonable doubts as to the authenticity of such documents, the originating status of the products concerned or the fulfilment of the other requirements of this Protocol.
- **Scope correction:** None

## legal_nli_046

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2008291EN.01000101 / chunk_112
- **Rationale:** The rule sets a minimum free volatile acid content of 0.5% by weight, expressed as acetic acid, for the described heading-2001 products. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid.
- **Scope correction:** None

## legal_nli_047

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2017175EN.01000101 / chunk_157
- **Rationale:** The procedure requires time, speed and relative air velocity at 5 Hz, ambient temperature at at least 1 Hz, and at least ten coastdown runs, five each direction. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** During the procedure, elapsed time, vehicle speed, and air velocity (wind speed, direction) relative to the vehicle, shall be measured at a frequency of 5 Hz. Ambient temperature shall be synchronised and sampled at a minimum frequency of 1 Hz. The measurements shall be carried out in opposite directions until a minimum of ten consecutive runs (five in each direction) have been obtained.
- **Scope correction:** None

## legal_nli_048

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.98
- **Source:** L_2008289EN.01000101 / chunk_48
- **Rationale:** The rule permits applicant-requested interlocutory injunctions for imminent infringement, provisional continuation restrictions/guarantees, and injunctions against qualifying intermediaries. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.
- **Exact supporting quote:** The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.
- **Scope correction:** Clarify that the guarantee language makes continuation of the alleged infringement subject to lodging guarantees intended to compensate the right holder if infringement is determined; the judicial authority 'may' issue the measure.

## legal_nli_049

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2008289EN.01000101 / chunk_48
- **Rationale:** The rule permits applicant-requested interlocutory injunctions for imminent infringement, provisional continuation restrictions/guarantees, and injunctions against qualifying intermediaries. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.
- **Scope correction:** Clarify that the guarantee language makes continuation of the alleged infringement subject to lodging guarantees intended to compensate the right holder if infringement is determined; the judicial authority 'may' issue the measure.

## legal_nli_050

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2009165EN.01000101 / chunk_10
- **Rationale:** The initial threshold is five Article 52(1) States and the interval is six months; further Contracting Parties also face a six-month interval after deposit. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.
- **Scope correction:** For exact source scope, replace 'eligible States' with 'States referred to in Article 52, paragraph 1'.

## legal_nli_051

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2015343EN.01000101 / chunk_129
- **Rationale:** The rule makes the finishing-country result conditional on every working edge/surface/part being configured, the imported blank being incapable of functioning, and the stated processing limit; otherwise the blank's origin controls. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** (a) The country of origin of a good or part produced from a blank which by application of the Harmonized System General Interpretative Rule 2(a) is classified in the same heading, subheading or subdivision as the complete or finished good or part, shall be the country in which every working edge, working surface and working part was configured to final shape and dimension, provided, in its imported condition, the blank from which it was produced: (i) was not capable of functioning, and (ii) was not advanced beyond the initial stamping process or any processing required to remove the material from the forging platter or casting mould; (b) If the criteria in paragraph (a) are not satisfied, the country of origin is the country of origin of the blank of this Chapter.
- **Scope correction:** None

## legal_nli_052

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2016294EN.01000101 / chunk_164
- **Rationale:** The definition requires tobacco and glycerol; listed additives and fruit flavouring are optional, and tobacco-free water-pipe products are excluded. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** For the purposes of subheading 2403 11, the expression 'water-pipe tobacco' means tobacco intended for smoking in a water pipe and which consists of a mixture of tobacco and glycerol, whether or not containing aromatic oils and extracts, molasses or sugar, and whether or not flavoured with fruit. However, tobacco-free products intended for smoking in a water pipe are excluded from this subheading.
- **Scope correction:** None

## legal_nli_053

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2017175EN.01000101 / chunk_157
- **Rationale:** The procedure requires time, speed and relative air velocity at 5 Hz, ambient temperature at at least 1 Hz, and at least ten coastdown runs, five each direction. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** During the procedure, elapsed time, vehicle speed, and air velocity (wind speed, direction) relative to the vehicle, shall be measured at a frequency of 5 Hz. Ambient temperature shall be synchronised and sampled at a minimum frequency of 1 Hz. The measurements shall be carried out in opposite directions until a minimum of ten consecutive runs (five in each direction) have been obtained.
- **Scope correction:** None

## legal_nli_054

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.98
- **Source:** L_1994001EN.01000101 / chunk_50
- **Rationale:** A withholding or denial requires notification of both the decision and reasons to the applicant authority without delay. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.
- **Exact supporting quote:** If assistance is withheld or denied, the decision and the reasons therefor must be notified to the applicant authority without delay.
- **Scope correction:** None

## legal_nli_055

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2011127EN.01000101 / chunk_8
- **Rationale:** The Committee on Trade in Goods may be convened at the request of a Party or the Trade Committee and comprises representatives of the Parties. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** The Committee on Trade in Goods established pursuant to Article 15.2.1 (Specialised Committees) shall meet on the request of a Party or of the Trade Committee to consider any matter arising under this Chapter and comprise representatives of the Parties.
- **Scope correction:** None

## legal_nli_056

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2016294EN.01000101 / chunk_164
- **Rationale:** The definition requires tobacco and glycerol; listed additives and fruit flavouring are optional, and tobacco-free water-pipe products are excluded. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** For the purposes of subheading 2403 11, the expression 'water-pipe tobacco' means tobacco intended for smoking in a water pipe and which consists of a mixture of tobacco and glycerol, whether or not containing aromatic oils and extracts, molasses or sugar, and whether or not flavoured with fruit. However, tobacco-free products intended for smoking in a water pipe are excluded from this subheading.
- **Scope correction:** None

## legal_nli_057

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2016294EN.01000101 / chunk_164
- **Rationale:** The definition requires tobacco and glycerol; listed additives and fruit flavouring are optional, and tobacco-free water-pipe products are excluded. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** For the purposes of subheading 2403 11, the expression 'water-pipe tobacco' means tobacco intended for smoking in a water pipe and which consists of a mixture of tobacco and glycerol, whether or not containing aromatic oils and extracts, molasses or sugar, and whether or not flavoured with fruit. However, tobacco-free products intended for smoking in a water pipe are excluded from this subheading.
- **Scope correction:** None

## legal_nli_058

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.98
- **Source:** L_2016294EN.01000101 / chunk_164
- **Rationale:** The definition requires tobacco and glycerol; listed additives and fruit flavouring are optional, and tobacco-free water-pipe products are excluded. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.
- **Exact supporting quote:** For the purposes of subheading 2403 11, the expression 'water-pipe tobacco' means tobacco intended for smoking in a water pipe and which consists of a mixture of tobacco and glycerol, whether or not containing aromatic oils and extracts, molasses or sugar, and whether or not flavoured with fruit. However, tobacco-free products intended for smoking in a water pipe are excluded from this subheading.
- **Scope correction:** None

## legal_nli_059

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_1994001EN.01000101 / chunk_50
- **Rationale:** A withholding or denial requires notification of both the decision and reasons to the applicant authority without delay. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** If assistance is withheld or denied, the decision and the reasons therefor must be notified to the applicant authority without delay.
- **Scope correction:** None

## legal_nli_060

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.95
- **Source:** L_2008289EN.01000101 / chunk_48
- **Rationale:** The premise says judicial authorities may issue the interlocutory injunction. Permission does not entail a duty to grant every application, but the premise alone also does not expressly negate every possible mandatory rule. The stronger 'must grant every application' claim is therefore neutral.
- **Exact supporting quote:** The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.
- **Scope correction:** Clarify that the guarantee language makes continuation of the alleged infringement subject to lodging guarantees intended to compensate the right holder if infringement is determined; the judicial authority 'may' issue the measure.

## legal_nli_061

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.98
- **Source:** L_2016294EN.01000101 / chunk_164
- **Rationale:** The definition requires tobacco and glycerol; listed additives and fruit flavouring are optional, and tobacco-free water-pipe products are excluded. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.
- **Exact supporting quote:** For the purposes of subheading 2403 11, the expression 'water-pipe tobacco' means tobacco intended for smoking in a water pipe and which consists of a mixture of tobacco and glycerol, whether or not containing aromatic oils and extracts, molasses or sugar, and whether or not flavoured with fruit. However, tobacco-free products intended for smoking in a water pipe are excluded from this subheading.
- **Scope correction:** None

## legal_nli_062

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_1994001EN.01000101 / chunk_50
- **Rationale:** A withholding or denial requires notification of both the decision and reasons to the applicant authority without delay. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** If assistance is withheld or denied, the decision and the reasons therefor must be notified to the applicant authority without delay.
- **Scope correction:** None

## legal_nli_063

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2015343EN.01000101 / chunk_129
- **Rationale:** The rule makes the finishing-country result conditional on every working edge/surface/part being configured, the imported blank being incapable of functioning, and the stated processing limit; otherwise the blank's origin controls. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** (a) The country of origin of a good or part produced from a blank which by application of the Harmonized System General Interpretative Rule 2(a) is classified in the same heading, subheading or subdivision as the complete or finished good or part, shall be the country in which every working edge, working surface and working part was configured to final shape and dimension, provided, in its imported condition, the blank from which it was produced: (i) was not capable of functioning, and (ii) was not advanced beyond the initial stamping process or any processing required to remove the material from the forging platter or casting mould; (b) If the criteria in paragraph (a) are not satisfied, the country of origin is the country of origin of the blank of this Chapter.
- **Scope correction:** None

## legal_nli_064

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2008291EN.01000101 / chunk_112
- **Rationale:** The rule sets a minimum free volatile acid content of 0.5% by weight, expressed as acetic acid, for the described heading-2001 products. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid.
- **Scope correction:** None

## legal_nli_065

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.96
- **Source:** L_2009165EN.01000101 / chunk_10
- **Rationale:** The premise gives the five-State threshold and timing rule but does not state that the fifth State completed the step on 1 May 2027; that date claim is neutral.
- **Exact supporting quote:** This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.
- **Scope correction:** For exact source scope, replace 'eligible States' with 'States referred to in Article 52, paragraph 1'.

## legal_nli_066

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.98
- **Source:** L_2011282EN.01000101 / chunk_271
- **Rationale:** The wood-flour definition allows no more than 8% by weight retained on a 0.63 mm sieve. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.
- **Exact supporting quote:** For the purposes of heading 4405 , 'wood flour' means wood powder of which not more than 8 % by weight is retained by a sieve with an aperture of 0,63 mm.
- **Scope correction:** None

## legal_nli_067

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2017175EN.01000101 / chunk_157
- **Rationale:** The procedure requires time, speed and relative air velocity at 5 Hz, ambient temperature at at least 1 Hz, and at least ten coastdown runs, five each direction. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** During the procedure, elapsed time, vehicle speed, and air velocity (wind speed, direction) relative to the vehicle, shall be measured at a frequency of 5 Hz. Ambient temperature shall be synchronised and sampled at a minimum frequency of 1 Hz. The measurements shall be carried out in opposite directions until a minimum of ten consecutive runs (five in each direction) have been obtained.
- **Scope correction:** None

## legal_nli_068

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2011127EN.01000101 / chunk_8
- **Rationale:** The Committee on Trade in Goods may be convened at the request of a Party or the Trade Committee and comprises representatives of the Parties. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** The Committee on Trade in Goods established pursuant to Article 15.2.1 (Specialised Committees) shall meet on the request of a Party or of the Trade Committee to consider any matter arising under this Chapter and comprise representatives of the Parties.
- **Scope correction:** None

## legal_nli_069

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2015343EN.01000101 / chunk_129
- **Rationale:** The rule makes the finishing-country result conditional on every working edge/surface/part being configured, the imported blank being incapable of functioning, and the stated processing limit; otherwise the blank's origin controls. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** (a) The country of origin of a good or part produced from a blank which by application of the Harmonized System General Interpretative Rule 2(a) is classified in the same heading, subheading or subdivision as the complete or finished good or part, shall be the country in which every working edge, working surface and working part was configured to final shape and dimension, provided, in its imported condition, the blank from which it was produced: (i) was not capable of functioning, and (ii) was not advanced beyond the initial stamping process or any processing required to remove the material from the forging platter or casting mould; (b) If the criteria in paragraph (a) are not satisfied, the country of origin is the country of origin of the blank of this Chapter.
- **Scope correction:** None

## legal_nli_070

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2008291EN.01000101 / chunk_112
- **Rationale:** The rule sets a minimum free volatile acid content of 0.5% by weight, expressed as acetic acid, for the described heading-2001 products. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid.
- **Scope correction:** None

## legal_nli_071

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2007345EN.01000101 / chunk_39
- **Rationale:** The rule expressly permits random verification and verification triggered by reasonable doubts about authenticity, originating status, or other Protocol requirements. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** Subsequent verifications of proofs of origin shall be carried out at random or whenever the customs authorities of the importing country have reasonable doubts as to the authenticity of such documents, the originating status of the products concerned or the fulfilment of the other requirements of this Protocol.
- **Scope correction:** None

## legal_nli_072

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2007345EN.01000101 / chunk_39
- **Rationale:** The rule expressly permits random verification and verification triggered by reasonable doubts about authenticity, originating status, or other Protocol requirements. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** Subsequent verifications of proofs of origin shall be carried out at random or whenever the customs authorities of the importing country have reasonable doubts as to the authenticity of such documents, the originating status of the products concerned or the fulfilment of the other requirements of this Protocol.
- **Scope correction:** None

## legal_nli_073

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.98
- **Source:** L_2011127EN.01000101 / chunk_8
- **Rationale:** The Committee on Trade in Goods may be convened at the request of a Party or the Trade Committee and comprises representatives of the Parties. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.
- **Exact supporting quote:** The Committee on Trade in Goods established pursuant to Article 15.2.1 (Specialised Committees) shall meet on the request of a Party or of the Trade Committee to consider any matter arising under this Chapter and comprise representatives of the Parties.
- **Scope correction:** None

## legal_nli_074

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2008289EN.01000101 / chunk_48
- **Rationale:** The rule permits applicant-requested interlocutory injunctions for imminent infringement, provisional continuation restrictions/guarantees, and injunctions against qualifying intermediaries. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.
- **Scope correction:** Clarify that the guarantee language makes continuation of the alleged infringement subject to lodging guarantees intended to compensate the right holder if infringement is determined; the judicial authority 'may' issue the measure.

## legal_nli_075

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2015343EN.01000101 / chunk_129
- **Rationale:** The rule makes the finishing-country result conditional on every working edge/surface/part being configured, the imported blank being incapable of functioning, and the stated processing limit; otherwise the blank's origin controls. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** (a) The country of origin of a good or part produced from a blank which by application of the Harmonized System General Interpretative Rule 2(a) is classified in the same heading, subheading or subdivision as the complete or finished good or part, shall be the country in which every working edge, working surface and working part was configured to final shape and dimension, provided, in its imported condition, the blank from which it was produced: (i) was not capable of functioning, and (ii) was not advanced beyond the initial stamping process or any processing required to remove the material from the forging platter or casting mould; (b) If the criteria in paragraph (a) are not satisfied, the country of origin is the country of origin of the blank of this Chapter.
- **Scope correction:** None

## legal_nli_076

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.98
- **Source:** L_2015343EN.01000101 / chunk_129
- **Rationale:** The rule makes the finishing-country result conditional on every working edge/surface/part being configured, the imported blank being incapable of functioning, and the stated processing limit; otherwise the blank's origin controls. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.
- **Exact supporting quote:** (a) The country of origin of a good or part produced from a blank which by application of the Harmonized System General Interpretative Rule 2(a) is classified in the same heading, subheading or subdivision as the complete or finished good or part, shall be the country in which every working edge, working surface and working part was configured to final shape and dimension, provided, in its imported condition, the blank from which it was produced: (i) was not capable of functioning, and (ii) was not advanced beyond the initial stamping process or any processing required to remove the material from the forging platter or casting mould; (b) If the criteria in paragraph (a) are not satisfied, the country of origin is the country of origin of the blank of this Chapter.
- **Scope correction:** None

## legal_nli_077

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2015343EN.01000101 / chunk_129
- **Rationale:** The rule makes the finishing-country result conditional on every working edge/surface/part being configured, the imported blank being incapable of functioning, and the stated processing limit; otherwise the blank's origin controls. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** (a) The country of origin of a good or part produced from a blank which by application of the Harmonized System General Interpretative Rule 2(a) is classified in the same heading, subheading or subdivision as the complete or finished good or part, shall be the country in which every working edge, working surface and working part was configured to final shape and dimension, provided, in its imported condition, the blank from which it was produced: (i) was not capable of functioning, and (ii) was not advanced beyond the initial stamping process or any processing required to remove the material from the forging platter or casting mould; (b) If the criteria in paragraph (a) are not satisfied, the country of origin is the country of origin of the blank of this Chapter.
- **Scope correction:** None

## legal_nli_078

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2011282EN.01000101 / chunk_271
- **Rationale:** The wood-flour definition allows no more than 8% by weight retained on a 0.63 mm sieve. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** For the purposes of heading 4405 , 'wood flour' means wood powder of which not more than 8 % by weight is retained by a sieve with an aperture of 0,63 mm.
- **Scope correction:** None

## legal_nli_079

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2009165EN.01000101 / chunk_10
- **Rationale:** The initial threshold is five Article 52(1) States and the interval is six months; further Contracting Parties also face a six-month interval after deposit. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.
- **Scope correction:** For exact source scope, replace 'eligible States' with 'States referred to in Article 52, paragraph 1'.

## legal_nli_080

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2017175EN.01000101 / chunk_157
- **Rationale:** The procedure requires time, speed and relative air velocity at 5 Hz, ambient temperature at at least 1 Hz, and at least ten coastdown runs, five each direction. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** During the procedure, elapsed time, vehicle speed, and air velocity (wind speed, direction) relative to the vehicle, shall be measured at a frequency of 5 Hz. Ambient temperature shall be synchronised and sampled at a minimum frequency of 1 Hz. The measurements shall be carried out in opposite directions until a minimum of ten consecutive runs (five in each direction) have been obtained.
- **Scope correction:** None

## legal_nli_081

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_1994001EN.01000101 / chunk_50
- **Rationale:** A withholding or denial requires notification of both the decision and reasons to the applicant authority without delay. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** If assistance is withheld or denied, the decision and the reasons therefor must be notified to the applicant authority without delay.
- **Scope correction:** None

## legal_nli_082

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.98
- **Source:** L_2008291EN.01000101 / chunk_112
- **Rationale:** The rule sets a minimum free volatile acid content of 0.5% by weight, expressed as acetic acid, for the described heading-2001 products. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.
- **Exact supporting quote:** For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid.
- **Scope correction:** None

## legal_nli_083

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2011127EN.01000101 / chunk_8
- **Rationale:** The Committee on Trade in Goods may be convened at the request of a Party or the Trade Committee and comprises representatives of the Parties. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** The Committee on Trade in Goods established pursuant to Article 15.2.1 (Specialised Committees) shall meet on the request of a Party or of the Trade Committee to consider any matter arising under this Chapter and comprise representatives of the Parties.
- **Scope correction:** None

## legal_nli_084

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2011282EN.01000101 / chunk_271
- **Rationale:** The wood-flour definition allows no more than 8% by weight retained on a 0.63 mm sieve. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** For the purposes of heading 4405 , 'wood flour' means wood powder of which not more than 8 % by weight is retained by a sieve with an aperture of 0,63 mm.
- **Scope correction:** None

## legal_nli_085

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.98
- **Source:** L_2017175EN.01000101 / chunk_157
- **Rationale:** The procedure requires time, speed and relative air velocity at 5 Hz, ambient temperature at at least 1 Hz, and at least ten coastdown runs, five each direction. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.
- **Exact supporting quote:** During the procedure, elapsed time, vehicle speed, and air velocity (wind speed, direction) relative to the vehicle, shall be measured at a frequency of 5 Hz. Ambient temperature shall be synchronised and sampled at a minimum frequency of 1 Hz. The measurements shall be carried out in opposite directions until a minimum of ten consecutive runs (five in each direction) have been obtained.
- **Scope correction:** None

## legal_nli_086

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_2007345EN.01000101 / chunk_39
- **Rationale:** The rule expressly permits random verification and verification triggered by reasonable doubts about authenticity, originating status, or other Protocol requirements. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** Subsequent verifications of proofs of origin shall be carried out at random or whenever the customs authorities of the importing country have reasonable doubts as to the authenticity of such documents, the originating status of the products concerned or the fulfilment of the other requirements of this Protocol.
- **Scope correction:** None

## legal_nli_087

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.98
- **Source:** L_2015343EN.01000101 / chunk_129
- **Rationale:** The rule makes the finishing-country result conditional on every working edge/surface/part being configured, the imported blank being incapable of functioning, and the stated processing limit; otherwise the blank's origin controls. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.
- **Exact supporting quote:** (a) The country of origin of a good or part produced from a blank which by application of the Harmonized System General Interpretative Rule 2(a) is classified in the same heading, subheading or subdivision as the complete or finished good or part, shall be the country in which every working edge, working surface and working part was configured to final shape and dimension, provided, in its imported condition, the blank from which it was produced: (i) was not capable of functioning, and (ii) was not advanced beyond the initial stamping process or any processing required to remove the material from the forging platter or casting mould; (b) If the criteria in paragraph (a) are not satisfied, the country of origin is the country of origin of the blank of this Chapter.
- **Scope correction:** None

## legal_nli_088

- **Premise supported:** true
- **Label:** neutral
- **Confidence:** 0.98
- **Source:** L_2007345EN.01000101 / chunk_39
- **Rationale:** The rule expressly permits random verification and verification triggered by reasonable doubts about authenticity, originating status, or other Protocol requirements. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.
- **Exact supporting quote:** Subsequent verifications of proofs of origin shall be carried out at random or whenever the customs authorities of the importing country have reasonable doubts as to the authenticity of such documents, the originating status of the products concerned or the fulfilment of the other requirements of this Protocol.
- **Scope correction:** None

## legal_nli_089

- **Premise supported:** true
- **Label:** contradiction
- **Confidence:** 0.99
- **Source:** L_2009165EN.01000101 / chunk_10
- **Rationale:** The initial threshold is five Article 52(1) States and the interval is six months; further Contracting Parties also face a six-month interval after deposit. The hypothesis reverses, excludes, or violates an express condition of the premise.
- **Exact supporting quote:** This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.
- **Scope correction:** For exact source scope, replace 'eligible States' with 'States referred to in Article 52, paragraph 1'.

## legal_nli_090

- **Premise supported:** true
- **Label:** entailment
- **Confidence:** 0.99
- **Source:** L_1994001EN.01000101 / chunk_50
- **Rationale:** A withholding or denial requires notification of both the decision and reasons to the applicant authority without delay. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.
- **Exact supporting quote:** If assistance is withheld or denied, the decision and the reasons therefor must be notified to the applicant authority without delay.
- **Scope correction:** None
