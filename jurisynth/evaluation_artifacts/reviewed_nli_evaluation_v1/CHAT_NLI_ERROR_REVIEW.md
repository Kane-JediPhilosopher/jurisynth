# AI-assisted NLI error review

This is synthetic AI-adjudicated data, not expert gold. Forward prediction errors below include source excerpts and scope notes. Assess whether the existing label remains justified; explicitly flag ambiguous negation/modality, actor, time or conditional scope. Do not tune thresholds or claim independent validation. Test results are now observed; any resulting dataset changes need a new version and must not be portrayed as untouched holdout validation. Reverse three-class outputs are diagnostic only.

## legal_nli_006

```json
{
  "pair_id": "legal_nli_006",
  "family_id": "wood_flour",
  "source_document_id": "L_2011282EN.01000101",
  "source_chunk_id": "chunk_271",
  "premise": "For heading 4405, wood flour means wood powder of which not more than 8% by weight is retained by a sieve with an aperture of 0.63 mm.",
  "hypothesis": "Wood powder with 9% by weight retained on the specified sieve does not meet this definition.",
  "premise_kind": "Codex paraphrase; source grounding requires review",
  "hypothesis_kind": "synthetic diagnostic proposition; not a claim of actual law",
  "scope_assumption": "Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.",
  "proposed_label": "entailment",
  "label_origin": "ChatGPT AI-assisted adjudication",
  "adjudicated_label": "entailment",
  "review_status": "AI_adjudicated",
  "split": "development",
  "source_excerpt": "1. For the purposes of heading 4405 , 'wood flour' means wood powder of which not more than 8 % by weight is retained by a sieve with an aperture of 0,63 mm. 2. For the purposes of subheadings 4414 00 10 , 4418 10 10 , 4418 20 10 , 4419 00 10 , 4420 10 11 and 4420 90 91 , 'tropical wood' means the following tropical woods: acajou d'Afrique, alan, azobé, balsa, dark red meranti, dibétou, ilomba, imbuia, iroko, jelutong, jongkong, kapur, kempas, keruing, light red meranti, limba, mahogany (Swietenia spp.), makoré, mansonia, meranti bakau, merbau, obeche, okoumé, palissandre de Para, palissandre de Rio, palissandre de Rose, ramin, sapelli, sipo, teak, tiama, virola, white lauan, white meranti, white seraya and yellow meranti. CN code Description Conventional rate of duty (%) Supplementary unit (1) (2) (3) (4) 4401 Fuel wood, in logs, in billets, in twigs, in faggots or in similar forms; wood in chips or particles; sawdust and wood waste and scrap, whether or not agglomerated in logs, briquettes, pellets or similar forms 4401 10 00 - Fuel wood, in logs, in billets, in twigs, in faggots or in similar forms Free - - Wood in chips or particles 4401 21 00 - - Coniferous Free - 4401 22 00 - - Non-coniferous Free - - Sawdust and wood waste and scrap, whether or not agglomerated in logs, briquettes, pellets or similar forms 4401 31 00 - - Wood pellets Free - 4401 39 - - Other 4401 39 10 - - - Sawdust Free - 4401 39 90 - - - Other Free - 4402 Wood charcoal (including shell or nut charcoal), whether or not agglomerated 4402 10 00 - Of bamboo Free - 4402 90 00 - Other Free - 4403 Wood in the rough, whether or not stripped of bark or sapwood, or roughly squared 4403 10 00 - Treated with paint, stains, creosote or other preservatives Free m 3 4403 20 - Other, coniferous - - Spruce of the species ' Picea abies Karst. Abies alba Mill. 4403 20 11 - - - Sawlogs Free m 3 4403 20 19 - - - Other Free m 3 - - Pine of the species ' Pinus sylvestris L.",
  "difficulty_tag": "modality_conditions_scope",
  "rationale": "Check against the entire premise and source, not lexical overlap.",
  "reviewer_notes": "",
  "review": {
    "pair_id": "legal_nli_006",
    "premise_supported": true,
    "label": "entailment",
    "confidence": 0.99,
    "rationale": "The wood-flour definition allows no more than 8% by weight retained on a 0.63 mm sieve. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.",
    "exact_supporting_quote": "For the purposes of heading 4405 , 'wood flour' means wood powder of which not more than 8 % by weight is retained by a sieve with an aperture of 0,63 mm.",
    "scope_correction": "",
    "source_key": "L_2011282EN.01000101 / chunk_271",
    "batch": "NLI_BATCH_1.md"
  },
  "quote_match": "contiguous_normalized",
  "scope_correction_pending": false,
  "expert_validated": false,
  "confidence_is_calibrated_probability": false,
  "prediction": "neutral",
  "reverse_prediction_diagnostic_only": "neutral",
  "forward_probabilities": {
    "contradiction": 0.0005558047560043633,
    "entailment": 0.010508210398256779,
    "neutral": 0.9889360070228577
  },
  "reverse_probabilities": {
    "contradiction": 0.0002679471508599818,
    "entailment": 0.00045256188604980707,
    "neutral": 0.9992795586585999
  },
  "symmetric_contradiction_score_diagnostic": 0.00041187595343217254,
  "input_tokens": 54
}
```

## legal_nli_011

```json
{
  "pair_id": "legal_nli_011",
  "family_id": "water_pipe",
  "source_document_id": "L_2016294EN.01000101",
  "source_chunk_id": "chunk_164",
  "premise": "For subheading 2403 11, water-pipe tobacco is tobacco intended for smoking in a water pipe and consisting of tobacco and glycerol, whether or not it contains aromatic oils and extracts, molasses or sugar, and whether or not it is fruit-flavoured. Tobacco-free products intended for water-pipe smoking are excluded.",
  "hypothesis": "Fruit flavouring is mandatory under the stated definition.",
  "premise_kind": "Codex paraphrase; source grounding requires review",
  "hypothesis_kind": "synthetic diagnostic proposition; not a claim of actual law",
  "scope_assumption": "Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.",
  "proposed_label": "contradiction",
  "label_origin": "ChatGPT AI-assisted adjudication",
  "adjudicated_label": "contradiction",
  "review_status": "AI_adjudicated",
  "split": "development",
  "source_excerpt": "1. For the purposes of subheading 2403 11, the expression 'water-pipe tobacco' means tobacco intended for smoking in a water pipe and which consists of a mixture of tobacco and glycerol, whether or not containing aromatic oils and extracts, molasses or sugar, and whether or not flavoured with fruit. However, tobacco-free products intended for smoking in a water pipe are excluded from this subheading. CN code Description Conventional rate of duty (%) Supplementary unit (1) (2) (3) (4) 2401 Unmanufactured tobacco; tobacco refuse 2401 10 - Tobacco, not stemmed/stripped 2401 10 35 - - Light air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 148 - 2401 10 60 - - Sun-cured Oriental type tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 10 70 - - Dark air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 10 85 - - Flue-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 149 - 2401 10 95 - - Other 10 MIN 22 € MAX 56 €/100 kg/net ( 150 - 2401 20 - Tobacco, partly or wholly stemmed/stripped 2401 20 35 - - Light air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 148 - 2401 20 60 - - Sun-cured Oriental type tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 20 70 - - Dark air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 20 85 - - Flue-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 149 - 2401 20 95 - - Other 11,2 MIN 22 € MAX 56 €/100 kg/net ( 150 - 2401 30 00 - Tobacco refuse 11,2 MIN 22 € MAX 56 €/100 kg/net - 2402 Cigars, cheroots, cigarillos and cigarettes, of tobacco or of tobacco substitutes 2402 10 00 - Cigars, cheroots and cigarillos, containing tobacco 26 1 000 p/st 2402 20 - Cigarettes containing tobacco 2402 20 10 - - Containing cloves 10 1 000 p/st 2402 20 90 - - Other 57,6 1 000 p/st 2402 90 00 - Other 57,6 - 2403 Other manufactured tobacco and manufactured tobacco substitutes; 'homogenised' or 'reconstituted' tobacco; tobacco extracts and essences - Smoking tobacco, whether or not containing tobacco substitutes in any proportion 2403 11 00 - - Water-pipe tobacco specified in subheading note 1 to this chapter 74,9 - 2403 19 - - Other 2403 19 10 - - - In immediate packings of a net content not exceeding 500 g 74,9 - 2403 19 90 - - - Other 74,9 - - Other 2403 91 00 - - 'Homogenised' or 'reconstituted' tobacco 16,6 - 2403 99 - - Other 2403 99 10 - - - Chewing tobacco and snuff 41,6 - 2403 99 90 - - - Other 16,6 -\nSECTION V\nMINERAL PRODUCTS\nCHAPTER 25",
  "difficulty_tag": "modality_conditions_scope",
  "rationale": "Check against the entire premise and source, not lexical overlap.",
  "reviewer_notes": "",
  "review": {
    "pair_id": "legal_nli_011",
    "premise_supported": true,
    "label": "contradiction",
    "confidence": 0.99,
    "rationale": "The definition requires tobacco and glycerol; listed additives and fruit flavouring are optional, and tobacco-free water-pipe products are excluded. The hypothesis reverses, excludes, or violates an express condition of the premise.",
    "exact_supporting_quote": "For the purposes of subheading 2403 11, the expression 'water-pipe tobacco' means tobacco intended for smoking in a water pipe and which consists of a mixture of tobacco and glycerol, whether or not containing aromatic oils and extracts, molasses or sugar, and whether or not flavoured with fruit. However, tobacco-free products intended for smoking in a water pipe are excluded from this subheading.",
    "scope_correction": "",
    "source_key": "L_2016294EN.01000101 / chunk_164",
    "batch": "NLI_BATCH_1.md"
  },
  "quote_match": "contiguous_normalized",
  "scope_correction_pending": false,
  "expert_validated": false,
  "confidence_is_calibrated_probability": false,
  "prediction": "neutral",
  "reverse_prediction_diagnostic_only": "neutral",
  "forward_probabilities": {
    "contradiction": 0.15899421274662018,
    "entailment": 0.0007576829520985484,
    "neutral": 0.8402481079101562
  },
  "reverse_probabilities": {
    "contradiction": 0.0032394814770668745,
    "entailment": 0.00205255881883204,
    "neutral": 0.9947079420089722
  },
  "symmetric_contradiction_score_diagnostic": 0.08111684769392014,
  "input_tokens": 76
}
```

## legal_nli_012

```json
{
  "pair_id": "legal_nli_012",
  "family_id": "tir_entry",
  "source_document_id": "L_2009165EN.01000101",
  "source_chunk_id": "chunk_10",
  "premise": "Under Article 53(1)–(2), this Convention shall enter into force six months after the date on which five States referred to in Article 52(1) have either signed it without reservation of ratification, acceptance or approval, or deposited their instruments of ratification, acceptance, approval or accession. After that threshold has been met, the Convention shall enter into force for a further Contracting Party six months after the date on which that party deposits its instrument of ratification, acceptance, approval or accession.",
  "hypothesis": "The initial rule requires only four eligible States, rather than five.",
  "premise_kind": "Codex paraphrase; source grounding requires review",
  "hypothesis_kind": "synthetic diagnostic proposition; not a claim of actual law",
  "scope_assumption": "Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.",
  "proposed_label": "contradiction",
  "label_origin": "ChatGPT AI-assisted adjudication",
  "adjudicated_label": "contradiction",
  "review_status": "AI_adjudicated",
  "split": "locked_test",
  "source_excerpt": "Article 53\nEntry into force\n1. This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession.\n2. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.\n3. Any instrument of ratification, acceptance, approval or accession deposited after the entry into force of an amendment to this Convention shall be deemed to apply to this Convention as amended.\n4. Any such instrument deposited after an amendment has been accepted but before it has entered into force shall be deemed to apply to this Convention as amended on the date when the amendment enters into force.\nArticle 54\nDenunciation\n1. Any Contracting Party may denounce this Convention by so notifying the Secretary-General of the United Nations.\n2. Denunciation shall take effect fifteen months after the date of receipt by the Secretary-General of the notification of denunciation.\n3. The validity of TIR Carnets accepted by the Customs office of departure before the date when the denunciation takes effect shall not be affected thereby and the guarantee of the guaranteeing association shall hold good in accordance with the provisions of this Convention.\nArticle 55\nTermination\nIf, after the entry into force of this Convention, the number of States which are Contracting Parties is for any period of twelve consecutive months reduced to less than five, the Convention shall cease to have effect from the end of the twelve-month period.\nArticle 56\nTermination of the operation of the TIR Convention, 1959\n1. Upon its entry into force, this Convention shall terminate and replace, in relations between the Contracting Parties to this Convention, the TIR Convention, 1959.\n2. Certificates of approval issued in respect of road vehicles and containers under the conditions of the TIR Convention, 1959, shall be accepted during the period of their validity or any extension thereof for the transport of goods under Customs seal by Contracting Parties to this Convention, provided that such vehicles and containers continue to fulfil the conditions under which they were originally approved.\nArticle 57\nSettlement of disputes\n1. Any dispute between two or more Contracting Parties concerning the interpretation or application of this Convention shall, so far as possible be settled by negotiation between them or other means of settlement.\n2. Any dispute between two or more Contracting Parties concerning the interpretation or application of this Convention which cannot be settled by the means indicated in paragraph 1 of this Article shall, at the request of one of them, be referred to an arbitration tribunal composed as follows: each Party to the dispute shall appoint an arbitrator and these arbitrators shall appoint another arbitrator, who shall be chairman. If, three months after receipt of a request, one of the Parties has failed to appoint an arbitrator or if the arbitrators have failed to elect the chairman, any of the Parties may request the Secretary-General of the United Nations to appoint an arbitrator or the chairman of the arbitration tribunal.\n3. The decision of the arbitration tribunal established under the provisions of paragraph 2 shall be binding on the Parties to the dispute.\n4. The arbitration tribunal shall determine its own rules of procedure.\n5. Decisions of the arbitration tribunal shall be taken by majority vote.\n6. Any controversy which may arise between the Parties to the dispute as regards the interpretation and execution of the award may be submitted by any of the Parties for judgment to the arbitration tribunal which made the award.\nArticle 58\nReservations\n1. Any State may, at the time of signing, ratifying or acceding to this Convention, declare that it does not consider itself bound by Article 57, paragraphs 2 to 6, of this Convention. Other Contracting Parties shall not be bound by these paragraphs in respect of any Contracting Party which has entered such a reservation.\n2. Any Contracting Party having entered a reservation as provided for in paragraph 1 of this Article may at any time withdraw such reservation by notifying the Secretary-General of the United Nations.\n3. Apart from the reservations provided for in paragraph 1 of this Article, no reservation to this Convention shall be permitted.\nArticle 58 bis\nAdministrative Committee\nAn Administrative Committee composed of all the Contracting Parties shall be established. Its composition, functions and rules of procedure are set out in Annex 8.\nArticle 58 ter\nTIR Executive Board",
  "difficulty_tag": "modality_conditions_scope",
  "rationale": "Check against the entire premise and source, not lexical overlap.",
  "reviewer_notes": "",
  "review": {
    "pair_id": "legal_nli_012",
    "premise_supported": true,
    "label": "contradiction",
    "confidence": 0.99,
    "rationale": "The initial threshold is five Article 52(1) States and the interval is six months; further Contracting Parties also face a six-month interval after deposit. The hypothesis reverses, excludes, or violates an express condition of the premise.",
    "exact_supporting_quote": "This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.",
    "scope_correction": "For exact source scope, replace 'eligible States' with 'States referred to in Article 52, paragraph 1'.",
    "source_key": "L_2009165EN.01000101 / chunk_10",
    "batch": "NLI_BATCH_1.md"
  },
  "quote_match": "ordered_source_fragments",
  "scope_correction_pending": false,
  "expert_validated": false,
  "confidence_is_calibrated_probability": false,
  "original_premise": "The Convention enters into force six months after five eligible States have signed without reservation of ratification, acceptance or approval, or deposited their specified instruments. After that threshold, it enters into force for further Contracting Parties six months after deposit of their instruments.",
  "followup_status": "confirmed",
  "family_scope_note": "All nine prior labels are retained. The premise is corrected from the broader phrase 'eligible States' to the source's exact scope: 'States referred to in Article 52(1)'. For hypotheses 012, 065 and 079, 'eligible States' is interpreted under the existing family scope assumption as referring to that Article 52(1) group. If strict source wording is required in the hypotheses themselves, rewrite that phrase rather than changing the semantic labels.",
  "followup_quote_match": "ordered_source_fragments",
  "prediction": "neutral",
  "reverse_prediction_diagnostic_only": "neutral",
  "forward_probabilities": {
    "contradiction": 0.0004763304314110428,
    "entailment": 0.0005106423050165176,
    "neutral": 0.9990129470825195
  },
  "reverse_probabilities": {
    "contradiction": 0.00035042280796915293,
    "entailment": 0.0009989202953875065,
    "neutral": 0.9986507296562195
  },
  "symmetric_contradiction_score_diagnostic": 0.00041337660513818264,
  "input_tokens": 115
}
```

## legal_nli_019

```json
{
  "pair_id": "legal_nli_019",
  "family_id": "tir_entry",
  "source_document_id": "L_2009165EN.01000101",
  "source_chunk_id": "chunk_10",
  "premise": "Under Article 53(1)–(2), this Convention shall enter into force six months after the date on which five States referred to in Article 52(1) have either signed it without reservation of ratification, acceptance or approval, or deposited their instruments of ratification, acceptance, approval or accession. After that threshold has been met, the Convention shall enter into force for a further Contracting Party six months after the date on which that party deposits its instrument of ratification, acceptance, approval or accession.",
  "hypothesis": "The initial interval is three months rather than six months after the threshold date.",
  "premise_kind": "Codex paraphrase; source grounding requires review",
  "hypothesis_kind": "synthetic diagnostic proposition; not a claim of actual law",
  "scope_assumption": "Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.",
  "proposed_label": "contradiction",
  "label_origin": "ChatGPT AI-assisted adjudication",
  "adjudicated_label": "contradiction",
  "review_status": "AI_adjudicated",
  "split": "locked_test",
  "source_excerpt": "Article 53\nEntry into force\n1. This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession.\n2. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.\n3. Any instrument of ratification, acceptance, approval or accession deposited after the entry into force of an amendment to this Convention shall be deemed to apply to this Convention as amended.\n4. Any such instrument deposited after an amendment has been accepted but before it has entered into force shall be deemed to apply to this Convention as amended on the date when the amendment enters into force.\nArticle 54\nDenunciation\n1. Any Contracting Party may denounce this Convention by so notifying the Secretary-General of the United Nations.\n2. Denunciation shall take effect fifteen months after the date of receipt by the Secretary-General of the notification of denunciation.\n3. The validity of TIR Carnets accepted by the Customs office of departure before the date when the denunciation takes effect shall not be affected thereby and the guarantee of the guaranteeing association shall hold good in accordance with the provisions of this Convention.\nArticle 55\nTermination\nIf, after the entry into force of this Convention, the number of States which are Contracting Parties is for any period of twelve consecutive months reduced to less than five, the Convention shall cease to have effect from the end of the twelve-month period.\nArticle 56\nTermination of the operation of the TIR Convention, 1959\n1. Upon its entry into force, this Convention shall terminate and replace, in relations between the Contracting Parties to this Convention, the TIR Convention, 1959.\n2. Certificates of approval issued in respect of road vehicles and containers under the conditions of the TIR Convention, 1959, shall be accepted during the period of their validity or any extension thereof for the transport of goods under Customs seal by Contracting Parties to this Convention, provided that such vehicles and containers continue to fulfil the conditions under which they were originally approved.\nArticle 57\nSettlement of disputes\n1. Any dispute between two or more Contracting Parties concerning the interpretation or application of this Convention shall, so far as possible be settled by negotiation between them or other means of settlement.\n2. Any dispute between two or more Contracting Parties concerning the interpretation or application of this Convention which cannot be settled by the means indicated in paragraph 1 of this Article shall, at the request of one of them, be referred to an arbitration tribunal composed as follows: each Party to the dispute shall appoint an arbitrator and these arbitrators shall appoint another arbitrator, who shall be chairman. If, three months after receipt of a request, one of the Parties has failed to appoint an arbitrator or if the arbitrators have failed to elect the chairman, any of the Parties may request the Secretary-General of the United Nations to appoint an arbitrator or the chairman of the arbitration tribunal.\n3. The decision of the arbitration tribunal established under the provisions of paragraph 2 shall be binding on the Parties to the dispute.\n4. The arbitration tribunal shall determine its own rules of procedure.\n5. Decisions of the arbitration tribunal shall be taken by majority vote.\n6. Any controversy which may arise between the Parties to the dispute as regards the interpretation and execution of the award may be submitted by any of the Parties for judgment to the arbitration tribunal which made the award.\nArticle 58\nReservations\n1. Any State may, at the time of signing, ratifying or acceding to this Convention, declare that it does not consider itself bound by Article 57, paragraphs 2 to 6, of this Convention. Other Contracting Parties shall not be bound by these paragraphs in respect of any Contracting Party which has entered such a reservation.\n2. Any Contracting Party having entered a reservation as provided for in paragraph 1 of this Article may at any time withdraw such reservation by notifying the Secretary-General of the United Nations.\n3. Apart from the reservations provided for in paragraph 1 of this Article, no reservation to this Convention shall be permitted.\nArticle 58 bis\nAdministrative Committee\nAn Administrative Committee composed of all the Contracting Parties shall be established. Its composition, functions and rules of procedure are set out in Annex 8.\nArticle 58 ter\nTIR Executive Board",
  "difficulty_tag": "modality_conditions_scope",
  "rationale": "Check against the entire premise and source, not lexical overlap.",
  "reviewer_notes": "",
  "review": {
    "pair_id": "legal_nli_019",
    "premise_supported": true,
    "label": "contradiction",
    "confidence": 0.99,
    "rationale": "The initial threshold is five Article 52(1) States and the interval is six months; further Contracting Parties also face a six-month interval after deposit. The hypothesis reverses, excludes, or violates an express condition of the premise.",
    "exact_supporting_quote": "This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.",
    "scope_correction": "For exact source scope, replace 'eligible States' with 'States referred to in Article 52, paragraph 1'.",
    "source_key": "L_2009165EN.01000101 / chunk_10",
    "batch": "NLI_BATCH_1.md"
  },
  "quote_match": "ordered_source_fragments",
  "scope_correction_pending": false,
  "expert_validated": false,
  "confidence_is_calibrated_probability": false,
  "original_premise": "The Convention enters into force six months after five eligible States have signed without reservation of ratification, acceptance or approval, or deposited their specified instruments. After that threshold, it enters into force for further Contracting Parties six months after deposit of their instruments.",
  "followup_status": "confirmed",
  "family_scope_note": "All nine prior labels are retained. The premise is corrected from the broader phrase 'eligible States' to the source's exact scope: 'States referred to in Article 52(1)'. For hypotheses 012, 065 and 079, 'eligible States' is interpreted under the existing family scope assumption as referring to that Article 52(1) group. If strict source wording is required in the hypotheses themselves, rewrite that phrase rather than changing the semantic labels.",
  "followup_quote_match": "ordered_source_fragments",
  "prediction": "neutral",
  "reverse_prediction_diagnostic_only": "neutral",
  "forward_probabilities": {
    "contradiction": 0.001913533196784556,
    "entailment": 0.0010670906631276011,
    "neutral": 0.997019350528717
  },
  "reverse_probabilities": {
    "contradiction": 0.0009904542239382863,
    "entailment": 0.002039980376139283,
    "neutral": 0.9969696402549744
  },
  "symmetric_contradiction_score_diagnostic": 0.001451993710361421,
  "input_tokens": 117
}
```

## legal_nli_024

```json
{
  "pair_id": "legal_nli_024",
  "family_id": "vinegar",
  "source_document_id": "L_2008291EN.01000101",
  "source_chunk_id": "chunk_112",
  "premise": "For heading 2001, vegetables, fruit, nuts and other edible plant parts prepared or preserved by vinegar or acetic acid must contain at least 0.5% free volatile acid by weight, expressed as acetic acid.",
  "hypothesis": "A relevant product containing only 0.4% free volatile acid by weight fails the stated acid-content requirement.",
  "premise_kind": "Codex paraphrase; source grounding requires review",
  "hypothesis_kind": "synthetic diagnostic proposition; not a claim of actual law",
  "scope_assumption": "Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.",
  "proposed_label": "entailment",
  "label_origin": "ChatGPT AI-assisted adjudication",
  "adjudicated_label": "entailment",
  "review_status": "AI_adjudicated",
  "split": "development",
  "source_excerpt": "1. For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid. In addition, mushrooms of subheading 2001 90 50 should not have a salt content exceeding 2,5 % by weight. 2. 3. The products of subheadings 2008 20 to 2008 80 , 2008 92 and 2008 99 shall be considered as containing added sugar when the 'sugar content' thereof exceeds by weight the percentages given hereunder, according to the kind of fruit or edible part of plant concerned: - pineapples and grapes: 13 %, - other fruits, including mixtures of fruit, and other edible parts of plants: 9 %. 4. For the purposes of subheadings 2008 30 11 to 2008 30 39 , 2008 40 11 to 2008 40 39 , 2008 50 11 to 2008 50 59 , 2008 60 11 to 2008 60 39 , 2008 70 11 to 2008 70 59 , 2008 80 11 to 2008 80 39 , 2008 92 12 to 2008 92 38 and 2008 99 11 to 2008 99 40 , the following expressions shall have the meanings hereby assigned to them: - 'actual alcoholic strength by mass': the number of kilograms of pure alcohol contained in 100 kg of the product, - '% mas': the symbol for alcoholic strength by mass. 5. The following shall be applied to the products as they are presented: (a) the added sugar content of products of heading 2009 corresponds to the 'sugar content' less the figures given hereunder, according to the kind of juice concerned: - lemon or tomato juice: 3, - grape juice: 15, - other fruit or vegetable juices, including mixtures of juices: 13. (b) the fruit juices with added sugar, of a Brix value not exceeding 67 and containing less than 50 % by weight of fruit juice lose their original character of fruit juices of heading 2009 . Item (b) shall not apply to concentrated natural fruit juices. Consequently, concentrated natural fruit juices are not excluded from heading 2009 . 6. For the purposes of subheadings 2009 69 51 and 2009 69 71 , 'concentrated grape juice (including grape must)' means grape juice (including grape must) for which the figure indicated by a refractometer (used in accordance with the method prescribed in the Annex to Regulation (EEC) No 558/93) at a temperature of 20 °C is not less than 50,9 %. 7.",
  "difficulty_tag": "modality_conditions_scope",
  "rationale": "Check against the entire premise and source, not lexical overlap.",
  "reviewer_notes": "",
  "review": {
    "pair_id": "legal_nli_024",
    "premise_supported": true,
    "label": "entailment",
    "confidence": 0.99,
    "rationale": "The rule sets a minimum free volatile acid content of 0.5% by weight, expressed as acetic acid, for the described heading-2001 products. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.",
    "exact_supporting_quote": "For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid.",
    "scope_correction": "",
    "source_key": "L_2008291EN.01000101 / chunk_112",
    "batch": "NLI_BATCH_1.md"
  },
  "quote_match": "contiguous_normalized",
  "scope_correction_pending": false,
  "expert_validated": false,
  "confidence_is_calibrated_probability": false,
  "prediction": "neutral",
  "reverse_prediction_diagnostic_only": "neutral",
  "forward_probabilities": {
    "contradiction": 0.00041529705049470067,
    "entailment": 0.0010002050548791885,
    "neutral": 0.998584508895874
  },
  "reverse_probabilities": {
    "contradiction": 0.00030222133500501513,
    "entailment": 0.0006461434531956911,
    "neutral": 0.9990516304969788
  },
  "symmetric_contradiction_score_diagnostic": 0.0003587591927498579,
  "input_tokens": 66
}
```

## legal_nli_030

```json
{
  "pair_id": "legal_nli_030",
  "family_id": "road_load",
  "source_document_id": "L_2017175EN.01000101",
  "source_chunk_id": "chunk_157",
  "premise": "During the stated road-load procedure, elapsed time, vehicle speed and relative air velocity, including wind speed and direction, shall be measured at 5 Hz. Ambient temperature shall be synchronised and sampled at a minimum of 1 Hz. Coastdown measurements require at least ten consecutive runs, five in each direction.",
  "hypothesis": "Ambient temperature sampled at 0.5 Hz fails the stated minimum sampling-frequency condition.",
  "premise_kind": "Codex paraphrase; source grounding requires review",
  "hypothesis_kind": "synthetic diagnostic proposition; not a claim of actual law",
  "scope_assumption": "Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.",
  "proposed_label": "entailment",
  "label_origin": "ChatGPT AI-assisted adjudication",
  "adjudicated_label": "entailment",
  "review_status": "AI_adjudicated",
  "split": "development",
  "source_excerpt": "4.3.2.2. Selection of vehicle speed range for road load curve determination\nThe test vehicle speed range shall be selected according to paragraph 2.2. of this Sub-Annex.\n4.3.2.3. Data collection\nDuring the procedure, elapsed time, vehicle speed, and air velocity (wind speed, direction) relative to the vehicle, shall be measured at a frequency of 5 Hz. Ambient temperature shall be synchronised and sampled at a minimum frequency of 1 Hz.\n4.3.2.4. Vehicle coastdown procedure\nThe measurements shall be carried out in opposite directions until a minimum of ten consecutive runs (five in each direction) have been obtained. Should an individual run fail to satisfy the required on-board anemometry test conditions, that run and the corresponding run in the opposite direction shall be rejected. All valid pairs shall be included in the final analysis with a minimum of 5 pairs of coastdown runs. See paragraph 4.3.2.6.10. of this Sub-Annex for statistical validation criteria.\nThe anemometer shall be installed in a position such that the effect on the operating characteristics of the vehicle is minimised.\nThe anemometer shall be installed according to one of the options below:\n(a) Using a boom approximately 2 metres in front of the vehicle's forward aerodynamic stagnation point; (b) On the roof of the vehicle at its centreline. If possible, the anemometer shall be mounted within 30 cm from the top of the windshield. (c) On the engine compartment cover of the vehicle at its centreline, mounted at the midpoint position between the vehicle front and the base of the windshield.\nIn all cases, the anemometer shall be mounted parallel to the road surface. In the event that positions (b) or (c) are used, the coastdown results shall be analytically adjusted for the additional aerodynamic drag induced by the anemometer. The adjustment shall be made by testing the coastdown vehicle in a wind tunnel both with and without the anemometer installed in the same position as used on the track., The calculated difference shall be the incremental aerodynamic drag coefficient C D combined with the frontal area, which shall be used to correct the coastdown results.\n4.3.2.4.1. Following the vehicle warm-up procedure described in paragraph 4.2.4. of this Sub-Annex and immediately prior to each test measurement, the vehicle shall be accelerated to 10 to 15 km/h above the highest reference speed and shall be driven at that speed for a maximum of 1 minute. After that, the coastdown shall be started immediately. 4.3.2.4.2. During a coastdown, the transmission shall be in neutral. Any steering wheel movement shall be avoided as much as possible, and the vehicle's brakes shall not be operated. 4.3.2.4.3. It is recommended that each coastdown run be performed without interruption. Split runs may however be performed if data cannot be collected in a single run for all the reference speed points. For split runs, care shall be taken so that vehicle conditions remain as stable as possible at each split point.\n4.3.2.5. Determination of the equation of motion\nSymbols used in the on-board anemometer equations of motion are listed in Table A4/4.\nTable A4/4\nSymbols used in the on-board anemometer equations of motion\n4.3.2.5.1. General form\nThe general form of the equation of motion is as follows:\nwhere:\nD mech = D tyre f r D aero = D grav =\nIn the case that the slope of the test track is equal to or less than 0.1 per cent over its length, D grav may be set to zero.\n4.3.2.5.2. Mechanical drag modelling\nMechanical drag consisting of separate components representing tyre D tyre and front and rear axle frictional losses, D f and D r , including transmission losses) shall be modelled as a three-term polynomial as a function of vehicle speed v as in the equation below:\nwhere:\nA m , B m , and C m are determined in the data analysis using the least squares method. These constants reflect the combined driveline and tyre drag.\nIn the case that the tested vehicle is the representative vehicle of a road load matrix family, the coefficient B m shall be set to zero and the coefficients A m and C m shall be recalculated with a least squares regression analysis.\n4.3.2.5.3. Aerodynamic drag modelling\nThe aerodynamic drag coefficient C D (Y) shall be modelled as a four-term polynomial as a function of yaw angle Y as in the equation below:\na 0 to a 4 are constant coefficients whose values are determined in the data analysis.",
  "difficulty_tag": "modality_conditions_scope",
  "rationale": "Check against the entire premise and source, not lexical overlap.",
  "reviewer_notes": "",
  "review": {
    "pair_id": "legal_nli_030",
    "premise_supported": true,
    "label": "entailment",
    "confidence": 0.99,
    "rationale": "The procedure requires time, speed and relative air velocity at 5 Hz, ambient temperature at at least 1 Hz, and at least ten coastdown runs, five each direction. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.",
    "exact_supporting_quote": "During the procedure, elapsed time, vehicle speed, and air velocity (wind speed, direction) relative to the vehicle, shall be measured at a frequency of 5 Hz. Ambient temperature shall be synchronised and sampled at a minimum frequency of 1 Hz. The measurements shall be carried out in opposite directions until a minimum of ten consecutive runs (five in each direction) have been obtained.",
    "scope_correction": "",
    "source_key": "L_2017175EN.01000101 / chunk_157",
    "batch": "NLI_BATCH_1.md"
  },
  "quote_match": "ordered_source_fragments",
  "scope_correction_pending": false,
  "expert_validated": false,
  "confidence_is_calibrated_probability": false,
  "prediction": "neutral",
  "reverse_prediction_diagnostic_only": "neutral",
  "forward_probabilities": {
    "contradiction": 0.0018475271062925458,
    "entailment": 0.00011460731911938637,
    "neutral": 0.9980378746986389
  },
  "reverse_probabilities": {
    "contradiction": 0.07053783535957336,
    "entailment": 6.721213139826432e-05,
    "neutral": 0.9293949007987976
  },
  "symmetric_contradiction_score_diagnostic": 0.03619268164038658,
  "input_tokens": 80
}
```

## legal_nli_032

```json
{
  "pair_id": "legal_nli_032",
  "family_id": "wood_flour",
  "source_document_id": "L_2011282EN.01000101",
  "source_chunk_id": "chunk_271",
  "premise": "For heading 4405, wood flour means wood powder of which not more than 8% by weight is retained by a sieve with an aperture of 0.63 mm.",
  "hypothesis": "Wood powder with 9% retained on the specified sieve meets this definition.",
  "premise_kind": "Codex paraphrase; source grounding requires review",
  "hypothesis_kind": "synthetic diagnostic proposition; not a claim of actual law",
  "scope_assumption": "Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.",
  "proposed_label": "contradiction",
  "label_origin": "ChatGPT AI-assisted adjudication",
  "adjudicated_label": "contradiction",
  "review_status": "AI_adjudicated",
  "split": "development",
  "source_excerpt": "1. For the purposes of heading 4405 , 'wood flour' means wood powder of which not more than 8 % by weight is retained by a sieve with an aperture of 0,63 mm. 2. For the purposes of subheadings 4414 00 10 , 4418 10 10 , 4418 20 10 , 4419 00 10 , 4420 10 11 and 4420 90 91 , 'tropical wood' means the following tropical woods: acajou d'Afrique, alan, azobé, balsa, dark red meranti, dibétou, ilomba, imbuia, iroko, jelutong, jongkong, kapur, kempas, keruing, light red meranti, limba, mahogany (Swietenia spp.), makoré, mansonia, meranti bakau, merbau, obeche, okoumé, palissandre de Para, palissandre de Rio, palissandre de Rose, ramin, sapelli, sipo, teak, tiama, virola, white lauan, white meranti, white seraya and yellow meranti. CN code Description Conventional rate of duty (%) Supplementary unit (1) (2) (3) (4) 4401 Fuel wood, in logs, in billets, in twigs, in faggots or in similar forms; wood in chips or particles; sawdust and wood waste and scrap, whether or not agglomerated in logs, briquettes, pellets or similar forms 4401 10 00 - Fuel wood, in logs, in billets, in twigs, in faggots or in similar forms Free - - Wood in chips or particles 4401 21 00 - - Coniferous Free - 4401 22 00 - - Non-coniferous Free - - Sawdust and wood waste and scrap, whether or not agglomerated in logs, briquettes, pellets or similar forms 4401 31 00 - - Wood pellets Free - 4401 39 - - Other 4401 39 10 - - - Sawdust Free - 4401 39 90 - - - Other Free - 4402 Wood charcoal (including shell or nut charcoal), whether or not agglomerated 4402 10 00 - Of bamboo Free - 4402 90 00 - Other Free - 4403 Wood in the rough, whether or not stripped of bark or sapwood, or roughly squared 4403 10 00 - Treated with paint, stains, creosote or other preservatives Free m 3 4403 20 - Other, coniferous - - Spruce of the species ' Picea abies Karst. Abies alba Mill. 4403 20 11 - - - Sawlogs Free m 3 4403 20 19 - - - Other Free m 3 - - Pine of the species ' Pinus sylvestris L.",
  "difficulty_tag": "modality_conditions_scope",
  "rationale": "Check against the entire premise and source, not lexical overlap.",
  "reviewer_notes": "",
  "review": {
    "pair_id": "legal_nli_032",
    "premise_supported": true,
    "label": "contradiction",
    "confidence": 0.99,
    "rationale": "The wood-flour definition allows no more than 8% by weight retained on a 0.63 mm sieve. The hypothesis reverses, excludes, or violates an express condition of the premise.",
    "exact_supporting_quote": "For the purposes of heading 4405 , 'wood flour' means wood powder of which not more than 8 % by weight is retained by a sieve with an aperture of 0,63 mm.",
    "scope_correction": "",
    "source_key": "L_2011282EN.01000101 / chunk_271",
    "batch": "NLI_BATCH_2.md"
  },
  "quote_match": "contiguous_normalized",
  "scope_correction_pending": false,
  "expert_validated": false,
  "confidence_is_calibrated_probability": false,
  "prediction": "neutral",
  "reverse_prediction_diagnostic_only": "neutral",
  "forward_probabilities": {
    "contradiction": 0.012732645496726036,
    "entailment": 0.000296257232548669,
    "neutral": 0.9869711399078369
  },
  "reverse_probabilities": {
    "contradiction": 0.004223422147333622,
    "entailment": 0.0004654651856981218,
    "neutral": 0.9953110814094543
  },
  "symmetric_contradiction_score_diagnostic": 0.008478034287691116,
  "input_tokens": 50
}
```

## legal_nli_033

```json
{
  "pair_id": "legal_nli_033",
  "family_id": "water_pipe",
  "source_document_id": "L_2016294EN.01000101",
  "source_chunk_id": "chunk_164",
  "premise": "For subheading 2403 11, water-pipe tobacco is tobacco intended for smoking in a water pipe and consisting of tobacco and glycerol, whether or not it contains aromatic oils and extracts, molasses or sugar, and whether or not it is fruit-flavoured. Tobacco-free products intended for water-pipe smoking are excluded.",
  "hypothesis": "The stated definition prohibits any product containing molasses or sugar.",
  "premise_kind": "Codex paraphrase; source grounding requires review",
  "hypothesis_kind": "synthetic diagnostic proposition; not a claim of actual law",
  "scope_assumption": "Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.",
  "proposed_label": "contradiction",
  "label_origin": "ChatGPT AI-assisted adjudication",
  "adjudicated_label": "contradiction",
  "review_status": "AI_adjudicated",
  "split": "development",
  "source_excerpt": "1. For the purposes of subheading 2403 11, the expression 'water-pipe tobacco' means tobacco intended for smoking in a water pipe and which consists of a mixture of tobacco and glycerol, whether or not containing aromatic oils and extracts, molasses or sugar, and whether or not flavoured with fruit. However, tobacco-free products intended for smoking in a water pipe are excluded from this subheading. CN code Description Conventional rate of duty (%) Supplementary unit (1) (2) (3) (4) 2401 Unmanufactured tobacco; tobacco refuse 2401 10 - Tobacco, not stemmed/stripped 2401 10 35 - - Light air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 148 - 2401 10 60 - - Sun-cured Oriental type tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 10 70 - - Dark air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 10 85 - - Flue-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 149 - 2401 10 95 - - Other 10 MIN 22 € MAX 56 €/100 kg/net ( 150 - 2401 20 - Tobacco, partly or wholly stemmed/stripped 2401 20 35 - - Light air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 148 - 2401 20 60 - - Sun-cured Oriental type tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 20 70 - - Dark air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 20 85 - - Flue-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 149 - 2401 20 95 - - Other 11,2 MIN 22 € MAX 56 €/100 kg/net ( 150 - 2401 30 00 - Tobacco refuse 11,2 MIN 22 € MAX 56 €/100 kg/net - 2402 Cigars, cheroots, cigarillos and cigarettes, of tobacco or of tobacco substitutes 2402 10 00 - Cigars, cheroots and cigarillos, containing tobacco 26 1 000 p/st 2402 20 - Cigarettes containing tobacco 2402 20 10 - - Containing cloves 10 1 000 p/st 2402 20 90 - - Other 57,6 1 000 p/st 2402 90 00 - Other 57,6 - 2403 Other manufactured tobacco and manufactured tobacco substitutes; 'homogenised' or 'reconstituted' tobacco; tobacco extracts and essences - Smoking tobacco, whether or not containing tobacco substitutes in any proportion 2403 11 00 - - Water-pipe tobacco specified in subheading note 1 to this chapter 74,9 - 2403 19 - - Other 2403 19 10 - - - In immediate packings of a net content not exceeding 500 g 74,9 - 2403 19 90 - - - Other 74,9 - - Other 2403 91 00 - - 'Homogenised' or 'reconstituted' tobacco 16,6 - 2403 99 - - Other 2403 99 10 - - - Chewing tobacco and snuff 41,6 - 2403 99 90 - - - Other 16,6 -\nSECTION V\nMINERAL PRODUCTS\nCHAPTER 25",
  "difficulty_tag": "modality_conditions_scope",
  "rationale": "Check against the entire premise and source, not lexical overlap.",
  "reviewer_notes": "",
  "review": {
    "pair_id": "legal_nli_033",
    "premise_supported": true,
    "label": "contradiction",
    "confidence": 0.99,
    "rationale": "The definition requires tobacco and glycerol; listed additives and fruit flavouring are optional, and tobacco-free water-pipe products are excluded. The hypothesis reverses, excludes, or violates an express condition of the premise.",
    "exact_supporting_quote": "For the purposes of subheading 2403 11, the expression 'water-pipe tobacco' means tobacco intended for smoking in a water pipe and which consists of a mixture of tobacco and glycerol, whether or not containing aromatic oils and extracts, molasses or sugar, and whether or not flavoured with fruit. However, tobacco-free products intended for smoking in a water pipe are excluded from this subheading.",
    "scope_correction": "",
    "source_key": "L_2016294EN.01000101 / chunk_164",
    "batch": "NLI_BATCH_2.md"
  },
  "quote_match": "contiguous_normalized",
  "scope_correction_pending": false,
  "expert_validated": false,
  "confidence_is_calibrated_probability": false,
  "prediction": "entailment",
  "reverse_prediction_diagnostic_only": "neutral",
  "forward_probabilities": {
    "contradiction": 0.021290641278028488,
    "entailment": 0.9514225721359253,
    "neutral": 0.027286801487207413
  },
  "reverse_probabilities": {
    "contradiction": 0.05536828562617302,
    "entailment": 0.07888788729906082,
    "neutral": 0.8657438158988953
  },
  "symmetric_contradiction_score_diagnostic": 0.038329463452100754,
  "input_tokens": 78
}
```

## legal_nli_038

```json
{
  "pair_id": "legal_nli_038",
  "family_id": "tir_entry",
  "source_document_id": "L_2009165EN.01000101",
  "source_chunk_id": "chunk_10",
  "premise": "Under Article 53(1)–(2), this Convention shall enter into force six months after the date on which five States referred to in Article 52(1) have either signed it without reservation of ratification, acceptance or approval, or deposited their instruments of ratification, acceptance, approval or accession. After that threshold has been met, the Convention shall enter into force for a further Contracting Party six months after the date on which that party deposits its instrument of ratification, acceptance, approval or accession.",
  "hypothesis": "Every later amendment takes effect on the same date as the original Convention.",
  "premise_kind": "Codex paraphrase; source grounding requires review",
  "hypothesis_kind": "synthetic diagnostic proposition; not a claim of actual law",
  "scope_assumption": "Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.",
  "proposed_label": "neutral",
  "label_origin": "ChatGPT AI-assisted adjudication",
  "adjudicated_label": "neutral",
  "review_status": "AI_adjudicated",
  "split": "locked_test",
  "source_excerpt": "Article 53\nEntry into force\n1. This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession.\n2. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.\n3. Any instrument of ratification, acceptance, approval or accession deposited after the entry into force of an amendment to this Convention shall be deemed to apply to this Convention as amended.\n4. Any such instrument deposited after an amendment has been accepted but before it has entered into force shall be deemed to apply to this Convention as amended on the date when the amendment enters into force.\nArticle 54\nDenunciation\n1. Any Contracting Party may denounce this Convention by so notifying the Secretary-General of the United Nations.\n2. Denunciation shall take effect fifteen months after the date of receipt by the Secretary-General of the notification of denunciation.\n3. The validity of TIR Carnets accepted by the Customs office of departure before the date when the denunciation takes effect shall not be affected thereby and the guarantee of the guaranteeing association shall hold good in accordance with the provisions of this Convention.\nArticle 55\nTermination\nIf, after the entry into force of this Convention, the number of States which are Contracting Parties is for any period of twelve consecutive months reduced to less than five, the Convention shall cease to have effect from the end of the twelve-month period.\nArticle 56\nTermination of the operation of the TIR Convention, 1959\n1. Upon its entry into force, this Convention shall terminate and replace, in relations between the Contracting Parties to this Convention, the TIR Convention, 1959.\n2. Certificates of approval issued in respect of road vehicles and containers under the conditions of the TIR Convention, 1959, shall be accepted during the period of their validity or any extension thereof for the transport of goods under Customs seal by Contracting Parties to this Convention, provided that such vehicles and containers continue to fulfil the conditions under which they were originally approved.\nArticle 57\nSettlement of disputes\n1. Any dispute between two or more Contracting Parties concerning the interpretation or application of this Convention shall, so far as possible be settled by negotiation between them or other means of settlement.\n2. Any dispute between two or more Contracting Parties concerning the interpretation or application of this Convention which cannot be settled by the means indicated in paragraph 1 of this Article shall, at the request of one of them, be referred to an arbitration tribunal composed as follows: each Party to the dispute shall appoint an arbitrator and these arbitrators shall appoint another arbitrator, who shall be chairman. If, three months after receipt of a request, one of the Parties has failed to appoint an arbitrator or if the arbitrators have failed to elect the chairman, any of the Parties may request the Secretary-General of the United Nations to appoint an arbitrator or the chairman of the arbitration tribunal.\n3. The decision of the arbitration tribunal established under the provisions of paragraph 2 shall be binding on the Parties to the dispute.\n4. The arbitration tribunal shall determine its own rules of procedure.\n5. Decisions of the arbitration tribunal shall be taken by majority vote.\n6. Any controversy which may arise between the Parties to the dispute as regards the interpretation and execution of the award may be submitted by any of the Parties for judgment to the arbitration tribunal which made the award.\nArticle 58\nReservations\n1. Any State may, at the time of signing, ratifying or acceding to this Convention, declare that it does not consider itself bound by Article 57, paragraphs 2 to 6, of this Convention. Other Contracting Parties shall not be bound by these paragraphs in respect of any Contracting Party which has entered such a reservation.\n2. Any Contracting Party having entered a reservation as provided for in paragraph 1 of this Article may at any time withdraw such reservation by notifying the Secretary-General of the United Nations.\n3. Apart from the reservations provided for in paragraph 1 of this Article, no reservation to this Convention shall be permitted.\nArticle 58 bis\nAdministrative Committee\nAn Administrative Committee composed of all the Contracting Parties shall be established. Its composition, functions and rules of procedure are set out in Annex 8.\nArticle 58 ter\nTIR Executive Board",
  "difficulty_tag": "unstated_actor_time_or_extra_duty",
  "rationale": "Check against the entire premise and source, not lexical overlap.",
  "reviewer_notes": "",
  "review": {
    "pair_id": "legal_nli_038",
    "premise_supported": true,
    "label": "neutral",
    "confidence": 0.96,
    "rationale": "The premise describes Convention entry into force, not the effective date of every later amendment. The amendment-timing claim is not established and is neutral.",
    "exact_supporting_quote": "This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.",
    "scope_correction": "For exact source scope, replace 'eligible States' with 'States referred to in Article 52, paragraph 1'.",
    "source_key": "L_2009165EN.01000101 / chunk_10",
    "batch": "NLI_BATCH_2.md"
  },
  "quote_match": "ordered_source_fragments",
  "scope_correction_pending": false,
  "expert_validated": false,
  "confidence_is_calibrated_probability": false,
  "original_premise": "The Convention enters into force six months after five eligible States have signed without reservation of ratification, acceptance or approval, or deposited their specified instruments. After that threshold, it enters into force for further Contracting Parties six months after deposit of their instruments.",
  "followup_status": "confirmed",
  "family_scope_note": "All nine prior labels are retained. The premise is corrected from the broader phrase 'eligible States' to the source's exact scope: 'States referred to in Article 52(1)'. For hypotheses 012, 065 and 079, 'eligible States' is interpreted under the existing family scope assumption as referring to that Article 52(1) group. If strict source wording is required in the hypotheses themselves, rewrite that phrase rather than changing the semantic labels.",
  "followup_quote_match": "ordered_source_fragments",
  "prediction": "contradiction",
  "reverse_prediction_diagnostic_only": "neutral",
  "forward_probabilities": {
    "contradiction": 0.9996762275695801,
    "entailment": 2.0627750927815214e-05,
    "neutral": 0.00030321365920826793
  },
  "reverse_probabilities": {
    "contradiction": 0.00048733409494161606,
    "entailment": 0.001212932402268052,
    "neutral": 0.998299777507782
  },
  "symmetric_contradiction_score_diagnostic": 0.5000817775726318,
  "input_tokens": 116
}
```

## legal_nli_057

```json
{
  "pair_id": "legal_nli_057",
  "family_id": "water_pipe",
  "source_document_id": "L_2016294EN.01000101",
  "source_chunk_id": "chunk_164",
  "premise": "For subheading 2403 11, water-pipe tobacco is tobacco intended for smoking in a water pipe and consisting of tobacco and glycerol, whether or not it contains aromatic oils and extracts, molasses or sugar, and whether or not it is fruit-flavoured. Tobacco-free products intended for water-pipe smoking are excluded.",
  "hypothesis": "The definition requires tobacco and glycerol.",
  "premise_kind": "Codex paraphrase; source grounding requires review",
  "hypothesis_kind": "synthetic diagnostic proposition; not a claim of actual law",
  "scope_assumption": "Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.",
  "proposed_label": "entailment",
  "label_origin": "ChatGPT AI-assisted adjudication",
  "adjudicated_label": "entailment",
  "review_status": "AI_adjudicated",
  "split": "development",
  "source_excerpt": "1. For the purposes of subheading 2403 11, the expression 'water-pipe tobacco' means tobacco intended for smoking in a water pipe and which consists of a mixture of tobacco and glycerol, whether or not containing aromatic oils and extracts, molasses or sugar, and whether or not flavoured with fruit. However, tobacco-free products intended for smoking in a water pipe are excluded from this subheading. CN code Description Conventional rate of duty (%) Supplementary unit (1) (2) (3) (4) 2401 Unmanufactured tobacco; tobacco refuse 2401 10 - Tobacco, not stemmed/stripped 2401 10 35 - - Light air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 148 - 2401 10 60 - - Sun-cured Oriental type tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 10 70 - - Dark air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 10 85 - - Flue-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 149 - 2401 10 95 - - Other 10 MIN 22 € MAX 56 €/100 kg/net ( 150 - 2401 20 - Tobacco, partly or wholly stemmed/stripped 2401 20 35 - - Light air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 148 - 2401 20 60 - - Sun-cured Oriental type tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 20 70 - - Dark air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 20 85 - - Flue-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 149 - 2401 20 95 - - Other 11,2 MIN 22 € MAX 56 €/100 kg/net ( 150 - 2401 30 00 - Tobacco refuse 11,2 MIN 22 € MAX 56 €/100 kg/net - 2402 Cigars, cheroots, cigarillos and cigarettes, of tobacco or of tobacco substitutes 2402 10 00 - Cigars, cheroots and cigarillos, containing tobacco 26 1 000 p/st 2402 20 - Cigarettes containing tobacco 2402 20 10 - - Containing cloves 10 1 000 p/st 2402 20 90 - - Other 57,6 1 000 p/st 2402 90 00 - Other 57,6 - 2403 Other manufactured tobacco and manufactured tobacco substitutes; 'homogenised' or 'reconstituted' tobacco; tobacco extracts and essences - Smoking tobacco, whether or not containing tobacco substitutes in any proportion 2403 11 00 - - Water-pipe tobacco specified in subheading note 1 to this chapter 74,9 - 2403 19 - - Other 2403 19 10 - - - In immediate packings of a net content not exceeding 500 g 74,9 - 2403 19 90 - - - Other 74,9 - - Other 2403 91 00 - - 'Homogenised' or 'reconstituted' tobacco 16,6 - 2403 99 - - Other 2403 99 10 - - - Chewing tobacco and snuff 41,6 - 2403 99 90 - - - Other 16,6 -\nSECTION V\nMINERAL PRODUCTS\nCHAPTER 25",
  "difficulty_tag": "modality_conditions_scope",
  "rationale": "Check against the entire premise and source, not lexical overlap.",
  "reviewer_notes": "",
  "review": {
    "pair_id": "legal_nli_057",
    "premise_supported": true,
    "label": "entailment",
    "confidence": 0.99,
    "rationale": "The definition requires tobacco and glycerol; listed additives and fruit flavouring are optional, and tobacco-free water-pipe products are excluded. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.",
    "exact_supporting_quote": "For the purposes of subheading 2403 11, the expression 'water-pipe tobacco' means tobacco intended for smoking in a water pipe and which consists of a mixture of tobacco and glycerol, whether or not containing aromatic oils and extracts, molasses or sugar, and whether or not flavoured with fruit. However, tobacco-free products intended for smoking in a water pipe are excluded from this subheading.",
    "scope_correction": "",
    "source_key": "L_2016294EN.01000101 / chunk_164",
    "batch": "NLI_BATCH_2.md"
  },
  "quote_match": "contiguous_normalized",
  "scope_correction_pending": false,
  "expert_validated": false,
  "confidence_is_calibrated_probability": false,
  "prediction": "neutral",
  "reverse_prediction_diagnostic_only": "neutral",
  "forward_probabilities": {
    "contradiction": 0.00017177870904561132,
    "entailment": 0.024065213277935982,
    "neutral": 0.9757629632949829
  },
  "reverse_probabilities": {
    "contradiction": 0.000494117324706167,
    "entailment": 0.0015532121760770679,
    "neutral": 0.9979526996612549
  },
  "symmetric_contradiction_score_diagnostic": 0.00033294802415184677,
  "input_tokens": 74
}
```

## legal_nli_070

```json
{
  "pair_id": "legal_nli_070",
  "family_id": "vinegar",
  "source_document_id": "L_2008291EN.01000101",
  "source_chunk_id": "chunk_112",
  "premise": "For heading 2001, vegetables, fruit, nuts and other edible plant parts prepared or preserved by vinegar or acetic acid must contain at least 0.5% free volatile acid by weight, expressed as acetic acid.",
  "hypothesis": "A relevant product with 0.4% free volatile acid by weight satisfies the stated minimum acid-content requirement.",
  "premise_kind": "Codex paraphrase; source grounding requires review",
  "hypothesis_kind": "synthetic diagnostic proposition; not a claim of actual law",
  "scope_assumption": "Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.",
  "proposed_label": "contradiction",
  "label_origin": "ChatGPT AI-assisted adjudication",
  "adjudicated_label": "contradiction",
  "review_status": "AI_adjudicated",
  "split": "development",
  "source_excerpt": "1. For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid. In addition, mushrooms of subheading 2001 90 50 should not have a salt content exceeding 2,5 % by weight. 2. 3. The products of subheadings 2008 20 to 2008 80 , 2008 92 and 2008 99 shall be considered as containing added sugar when the 'sugar content' thereof exceeds by weight the percentages given hereunder, according to the kind of fruit or edible part of plant concerned: - pineapples and grapes: 13 %, - other fruits, including mixtures of fruit, and other edible parts of plants: 9 %. 4. For the purposes of subheadings 2008 30 11 to 2008 30 39 , 2008 40 11 to 2008 40 39 , 2008 50 11 to 2008 50 59 , 2008 60 11 to 2008 60 39 , 2008 70 11 to 2008 70 59 , 2008 80 11 to 2008 80 39 , 2008 92 12 to 2008 92 38 and 2008 99 11 to 2008 99 40 , the following expressions shall have the meanings hereby assigned to them: - 'actual alcoholic strength by mass': the number of kilograms of pure alcohol contained in 100 kg of the product, - '% mas': the symbol for alcoholic strength by mass. 5. The following shall be applied to the products as they are presented: (a) the added sugar content of products of heading 2009 corresponds to the 'sugar content' less the figures given hereunder, according to the kind of juice concerned: - lemon or tomato juice: 3, - grape juice: 15, - other fruit or vegetable juices, including mixtures of juices: 13. (b) the fruit juices with added sugar, of a Brix value not exceeding 67 and containing less than 50 % by weight of fruit juice lose their original character of fruit juices of heading 2009 . Item (b) shall not apply to concentrated natural fruit juices. Consequently, concentrated natural fruit juices are not excluded from heading 2009 . 6. For the purposes of subheadings 2009 69 51 and 2009 69 71 , 'concentrated grape juice (including grape must)' means grape juice (including grape must) for which the figure indicated by a refractometer (used in accordance with the method prescribed in the Annex to Regulation (EEC) No 558/93) at a temperature of 20 °C is not less than 50,9 %. 7.",
  "difficulty_tag": "modality_conditions_scope",
  "rationale": "Check against the entire premise and source, not lexical overlap.",
  "reviewer_notes": "",
  "review": {
    "pair_id": "legal_nli_070",
    "premise_supported": true,
    "label": "contradiction",
    "confidence": 0.99,
    "rationale": "The rule sets a minimum free volatile acid content of 0.5% by weight, expressed as acetic acid, for the described heading-2001 products. The hypothesis reverses, excludes, or violates an express condition of the premise.",
    "exact_supporting_quote": "For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid.",
    "scope_correction": "",
    "source_key": "L_2008291EN.01000101 / chunk_112",
    "batch": "NLI_BATCH_3.md"
  },
  "quote_match": "contiguous_normalized",
  "scope_correction_pending": false,
  "expert_validated": false,
  "confidence_is_calibrated_probability": false,
  "prediction": "neutral",
  "reverse_prediction_diagnostic_only": "neutral",
  "forward_probabilities": {
    "contradiction": 0.05991131812334061,
    "entailment": 0.006181447766721249,
    "neutral": 0.9339072704315186
  },
  "reverse_probabilities": {
    "contradiction": 0.1356465071439743,
    "entailment": 0.0012363563291728497,
    "neutral": 0.8631171584129333
  },
  "symmetric_contradiction_score_diagnostic": 0.09777891635894775,
  "input_tokens": 66
}
```

## legal_nli_078

```json
{
  "pair_id": "legal_nli_078",
  "family_id": "wood_flour",
  "source_document_id": "L_2011282EN.01000101",
  "source_chunk_id": "chunk_271",
  "premise": "For heading 4405, wood flour means wood powder of which not more than 8% by weight is retained by a sieve with an aperture of 0.63 mm.",
  "hypothesis": "Retaining exactly 8% by weight satisfies the stated maximum-retention condition.",
  "premise_kind": "Codex paraphrase; source grounding requires review",
  "hypothesis_kind": "synthetic diagnostic proposition; not a claim of actual law",
  "scope_assumption": "Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.",
  "proposed_label": "entailment",
  "label_origin": "ChatGPT AI-assisted adjudication",
  "adjudicated_label": "entailment",
  "review_status": "AI_adjudicated",
  "split": "development",
  "source_excerpt": "1. For the purposes of heading 4405 , 'wood flour' means wood powder of which not more than 8 % by weight is retained by a sieve with an aperture of 0,63 mm. 2. For the purposes of subheadings 4414 00 10 , 4418 10 10 , 4418 20 10 , 4419 00 10 , 4420 10 11 and 4420 90 91 , 'tropical wood' means the following tropical woods: acajou d'Afrique, alan, azobé, balsa, dark red meranti, dibétou, ilomba, imbuia, iroko, jelutong, jongkong, kapur, kempas, keruing, light red meranti, limba, mahogany (Swietenia spp.), makoré, mansonia, meranti bakau, merbau, obeche, okoumé, palissandre de Para, palissandre de Rio, palissandre de Rose, ramin, sapelli, sipo, teak, tiama, virola, white lauan, white meranti, white seraya and yellow meranti. CN code Description Conventional rate of duty (%) Supplementary unit (1) (2) (3) (4) 4401 Fuel wood, in logs, in billets, in twigs, in faggots or in similar forms; wood in chips or particles; sawdust and wood waste and scrap, whether or not agglomerated in logs, briquettes, pellets or similar forms 4401 10 00 - Fuel wood, in logs, in billets, in twigs, in faggots or in similar forms Free - - Wood in chips or particles 4401 21 00 - - Coniferous Free - 4401 22 00 - - Non-coniferous Free - - Sawdust and wood waste and scrap, whether or not agglomerated in logs, briquettes, pellets or similar forms 4401 31 00 - - Wood pellets Free - 4401 39 - - Other 4401 39 10 - - - Sawdust Free - 4401 39 90 - - - Other Free - 4402 Wood charcoal (including shell or nut charcoal), whether or not agglomerated 4402 10 00 - Of bamboo Free - 4402 90 00 - Other Free - 4403 Wood in the rough, whether or not stripped of bark or sapwood, or roughly squared 4403 10 00 - Treated with paint, stains, creosote or other preservatives Free m 3 4403 20 - Other, coniferous - - Spruce of the species ' Picea abies Karst. Abies alba Mill. 4403 20 11 - - - Sawlogs Free m 3 4403 20 19 - - - Other Free m 3 - - Pine of the species ' Pinus sylvestris L.",
  "difficulty_tag": "modality_conditions_scope",
  "rationale": "Check against the entire premise and source, not lexical overlap.",
  "reviewer_notes": "",
  "review": {
    "pair_id": "legal_nli_078",
    "premise_supported": true,
    "label": "entailment",
    "confidence": 0.99,
    "rationale": "The wood-flour definition allows no more than 8% by weight retained on a 0.63 mm sieve. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.",
    "exact_supporting_quote": "For the purposes of heading 4405 , 'wood flour' means wood powder of which not more than 8 % by weight is retained by a sieve with an aperture of 0,63 mm.",
    "scope_correction": "",
    "source_key": "L_2011282EN.01000101 / chunk_271",
    "batch": "NLI_BATCH_3.md"
  },
  "quote_match": "contiguous_normalized",
  "scope_correction_pending": false,
  "expert_validated": false,
  "confidence_is_calibrated_probability": false,
  "prediction": "neutral",
  "reverse_prediction_diagnostic_only": "neutral",
  "forward_probabilities": {
    "contradiction": 7.743020250927657e-05,
    "entailment": 0.008174365386366844,
    "neutral": 0.9917482137680054
  },
  "reverse_probabilities": {
    "contradiction": 9.232443699147552e-05,
    "entailment": 0.0008185590850189328,
    "neutral": 0.9990891218185425
  },
  "symmetric_contradiction_score_diagnostic": 8.487731975037605e-05,
  "input_tokens": 51
}
```

## legal_nli_079

```json
{
  "pair_id": "legal_nli_079",
  "family_id": "tir_entry",
  "source_document_id": "L_2009165EN.01000101",
  "source_chunk_id": "chunk_10",
  "premise": "Under Article 53(1)–(2), this Convention shall enter into force six months after the date on which five States referred to in Article 52(1) have either signed it without reservation of ratification, acceptance or approval, or deposited their instruments of ratification, acceptance, approval or accession. After that threshold has been met, the Convention shall enter into force for a further Contracting Party six months after the date on which that party deposits its instrument of ratification, acceptance, approval or accession.",
  "hypothesis": "The stated initial threshold is five eligible States completing the specified steps.",
  "premise_kind": "Codex paraphrase; source grounding requires review",
  "hypothesis_kind": "synthetic diagnostic proposition; not a claim of actual law",
  "scope_assumption": "Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.",
  "proposed_label": "entailment",
  "label_origin": "ChatGPT AI-assisted adjudication",
  "adjudicated_label": "entailment",
  "review_status": "AI_adjudicated",
  "split": "locked_test",
  "source_excerpt": "Article 53\nEntry into force\n1. This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession.\n2. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.\n3. Any instrument of ratification, acceptance, approval or accession deposited after the entry into force of an amendment to this Convention shall be deemed to apply to this Convention as amended.\n4. Any such instrument deposited after an amendment has been accepted but before it has entered into force shall be deemed to apply to this Convention as amended on the date when the amendment enters into force.\nArticle 54\nDenunciation\n1. Any Contracting Party may denounce this Convention by so notifying the Secretary-General of the United Nations.\n2. Denunciation shall take effect fifteen months after the date of receipt by the Secretary-General of the notification of denunciation.\n3. The validity of TIR Carnets accepted by the Customs office of departure before the date when the denunciation takes effect shall not be affected thereby and the guarantee of the guaranteeing association shall hold good in accordance with the provisions of this Convention.\nArticle 55\nTermination\nIf, after the entry into force of this Convention, the number of States which are Contracting Parties is for any period of twelve consecutive months reduced to less than five, the Convention shall cease to have effect from the end of the twelve-month period.\nArticle 56\nTermination of the operation of the TIR Convention, 1959\n1. Upon its entry into force, this Convention shall terminate and replace, in relations between the Contracting Parties to this Convention, the TIR Convention, 1959.\n2. Certificates of approval issued in respect of road vehicles and containers under the conditions of the TIR Convention, 1959, shall be accepted during the period of their validity or any extension thereof for the transport of goods under Customs seal by Contracting Parties to this Convention, provided that such vehicles and containers continue to fulfil the conditions under which they were originally approved.\nArticle 57\nSettlement of disputes\n1. Any dispute between two or more Contracting Parties concerning the interpretation or application of this Convention shall, so far as possible be settled by negotiation between them or other means of settlement.\n2. Any dispute between two or more Contracting Parties concerning the interpretation or application of this Convention which cannot be settled by the means indicated in paragraph 1 of this Article shall, at the request of one of them, be referred to an arbitration tribunal composed as follows: each Party to the dispute shall appoint an arbitrator and these arbitrators shall appoint another arbitrator, who shall be chairman. If, three months after receipt of a request, one of the Parties has failed to appoint an arbitrator or if the arbitrators have failed to elect the chairman, any of the Parties may request the Secretary-General of the United Nations to appoint an arbitrator or the chairman of the arbitration tribunal.\n3. The decision of the arbitration tribunal established under the provisions of paragraph 2 shall be binding on the Parties to the dispute.\n4. The arbitration tribunal shall determine its own rules of procedure.\n5. Decisions of the arbitration tribunal shall be taken by majority vote.\n6. Any controversy which may arise between the Parties to the dispute as regards the interpretation and execution of the award may be submitted by any of the Parties for judgment to the arbitration tribunal which made the award.\nArticle 58\nReservations\n1. Any State may, at the time of signing, ratifying or acceding to this Convention, declare that it does not consider itself bound by Article 57, paragraphs 2 to 6, of this Convention. Other Contracting Parties shall not be bound by these paragraphs in respect of any Contracting Party which has entered such a reservation.\n2. Any Contracting Party having entered a reservation as provided for in paragraph 1 of this Article may at any time withdraw such reservation by notifying the Secretary-General of the United Nations.\n3. Apart from the reservations provided for in paragraph 1 of this Article, no reservation to this Convention shall be permitted.\nArticle 58 bis\nAdministrative Committee\nAn Administrative Committee composed of all the Contracting Parties shall be established. Its composition, functions and rules of procedure are set out in Annex 8.\nArticle 58 ter\nTIR Executive Board",
  "difficulty_tag": "modality_conditions_scope",
  "rationale": "Check against the entire premise and source, not lexical overlap.",
  "reviewer_notes": "",
  "review": {
    "pair_id": "legal_nli_079",
    "premise_supported": true,
    "label": "entailment",
    "confidence": 0.99,
    "rationale": "The initial threshold is five Article 52(1) States and the interval is six months; further Contracting Parties also face a six-month interval after deposit. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.",
    "exact_supporting_quote": "This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.",
    "scope_correction": "For exact source scope, replace 'eligible States' with 'States referred to in Article 52, paragraph 1'.",
    "source_key": "L_2009165EN.01000101 / chunk_10",
    "batch": "NLI_BATCH_3.md"
  },
  "quote_match": "ordered_source_fragments",
  "scope_correction_pending": false,
  "expert_validated": false,
  "confidence_is_calibrated_probability": false,
  "original_premise": "The Convention enters into force six months after five eligible States have signed without reservation of ratification, acceptance or approval, or deposited their specified instruments. After that threshold, it enters into force for further Contracting Parties six months after deposit of their instruments.",
  "followup_status": "confirmed_with_terminology_note",
  "family_scope_note": "All nine prior labels are retained. The premise is corrected from the broader phrase 'eligible States' to the source's exact scope: 'States referred to in Article 52(1)'. For hypotheses 012, 065 and 079, 'eligible States' is interpreted under the existing family scope assumption as referring to that Article 52(1) group. If strict source wording is required in the hypotheses themselves, rewrite that phrase rather than changing the semantic labels.",
  "followup_quote_match": "ordered_source_fragments",
  "prediction": "neutral",
  "reverse_prediction_diagnostic_only": "neutral",
  "forward_probabilities": {
    "contradiction": 0.00014261354226619005,
    "entailment": 0.11327657848596573,
    "neutral": 0.8865808248519897
  },
  "reverse_probabilities": {
    "contradiction": 0.0003994566504843533,
    "entailment": 0.0010135213378816843,
    "neutral": 0.9985870122909546
  },
  "symmetric_contradiction_score_diagnostic": 0.0002710350963752717,
  "input_tokens": 115
}
```

## legal_nli_087

```json
{
  "pair_id": "legal_nli_087",
  "family_id": "blank_origin",
  "source_document_id": "L_2015343EN.01000101",
  "source_chunk_id": "chunk_129",
  "premise": "For a good or part made from a blank covered by the stated same-heading rule, origin is the country where every working edge, working surface and working part was configured to final shape and dimension, provided that the imported blank was incapable of functioning and was not advanced beyond initial stamping or the specified material-removal processing. If those criteria are not satisfied, origin is the origin of the blank of this Chapter.",
  "hypothesis": "The finished good may enter the EU without any safety assessment.",
  "premise_kind": "Codex paraphrase; source grounding requires review",
  "hypothesis_kind": "synthetic diagnostic proposition; not a claim of actual law",
  "scope_assumption": "Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.",
  "proposed_label": "neutral",
  "label_origin": "ChatGPT AI-assisted adjudication",
  "adjudicated_label": "neutral",
  "review_status": "AI_adjudicated",
  "split": "development",
  "source_excerpt": "(a) The country of origin of a good or part produced from a blank which by application of the Harmonized System General Interpretative Rule 2(a) is classified in the same heading, subheading or subdivision as the complete or finished good or part, shall be the country in which every working edge, working surface and working part was configured to final shape and dimension, provided, in its imported condition, the blank from which it was produced: (i) was not capable of functioning, and (ii) was not advanced beyond the initial stamping process or any processing required to remove the material from the forging platter or casting mould; (b) If the criteria in paragraph (a) are not satisfied, the country of origin is the country of origin of the blank of this Chapter.\nChapter residual rule:\nWhere the country of origin cannot be determined by application of the primary rules, the country of origin of the goods shall be the country in which the major portion of the materials originated, as determined on the basis of the value of the materials.\nSECTION XVI\nMACHINERY AND MECHANICAL APPLIANCES; ELECTRICAL EQUIPMENT; PARTS THEREOF; SOUND RECORDERS AND REPRODUCERS, TELEVISION IMAGE AND SOUND RECORDERS AND REPRODUCERS, AND PARTS AND ACCESSORIES OF SUCH ARTICLES\nCHAPTER 84\nNuclear reactors, boilers, machinery and mechanical appliances; parts thereof\nPrimary Rule: Parts and accessories produced from blanks:\n1. The country of origin of goods that are produced from blanks which by application of the HS General Interpretative Rule 2(a), are classified in the same heading, subheading or subdivision as the complete or finished goods, shall be the country in which the blank was finished provided finishing included configuring to final shape by the removal of material (other than merely by honing or polishing or both), or by forming processes such as bending, hammering, pressing or stamping. 2. Paragraph 1 above applies to goods classifiable in provisions for parts or parts and accessories, including goods specifically named under such provisions.\nDefinition of 'Assembly of semi-conductor products' for the purpose of heading 8473\n'Assembly of semi-conductor products' means a change from chips, dice or other semi-conductor products to chips, dice or other semi-conductor products that are packaged or mounted onto a common medium for connection or connected and then mounted. The assembly of semi-conductor products shall not be considered as a minimal operation.\nChapter Notes\nNote 1: Collection of parts:\nWhere a change in classification results from the application of HS General Interpretative Rule 2(a) with respect to collections of parts that are presented as unassembled articles of another heading or subheading the individual parts shall retain their origin prior to such collection\nNote 2: Assembly of the collection of parts:\nGoods assembled from a collection of parts classified as the assembled good by application of General Interpretative Rule 2 shall have origin in the country of assembly, provided the assembly would have satisfied the primary rule for the good had each of the parts been presented separately and not as a collection\nNote 3: Disassembly of goods:\nA change of classification which results from the disassembly of goods shall not be considered as the change required by the rule set forth in the table of 'list rules'. The country of origin of the parts recovered from the goods shall be the country where the parts are recovered, unless the importer, exporter or any person with a justifiable cause to determine the origin of parts demonstrates another country of origin on the basis of verifiable evidence.\nChapter residual rule:\nWhere the country of origin cannot be determined by application of the primary rules, the country of origin of the goods shall be the country in which the major portion of the materials originated, as determined on the basis of the value of the materials.\nCHAPTER 85\nElectrical machinery and equipment and parts thereof; sound recorders and reproducers, television image and sound recorders and reproducers, and parts and accessories of such articles\nPrimary Rule: Parts and accessories produced from blanks:\n(1) The country of origin of goods that are produced from blanks which by application of the HS General Interpretative Rule 2(a) are classified in the same heading, subheading or subdivision as the complete or finished goods, shall be the country in which the blank was finished provided finishing included configuring to final shape by the removal of material (other than merely by honing or polishing or both), or by forming processes such as bending, hammering, pressing or stamping. (2) Paragraph 1 above applies to goods classifiable in provisions for parts or parts and accessories, including goods specifically named under such provisions.",
  "difficulty_tag": "unstated_actor_time_or_extra_duty",
  "rationale": "Check against the entire premise and source, not lexical overlap.",
  "reviewer_notes": "",
  "review": {
    "pair_id": "legal_nli_087",
    "premise_supported": true,
    "label": "neutral",
    "confidence": 0.98,
    "rationale": "The rule makes the finishing-country result conditional on every working edge/surface/part being configured, the imported blank being incapable of functioning, and the stated processing limit; otherwise the blank's origin controls. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.",
    "exact_supporting_quote": "(a) The country of origin of a good or part produced from a blank which by application of the Harmonized System General Interpretative Rule 2(a) is classified in the same heading, subheading or subdivision as the complete or finished good or part, shall be the country in which every working edge, working surface and working part was configured to final shape and dimension, provided, in its imported condition, the blank from which it was produced: (i) was not capable of functioning, and (ii) was not advanced beyond the initial stamping process or any processing required to remove the material from the forging platter or casting mould; (b) If the criteria in paragraph (a) are not satisfied, the country of origin is the country of origin of the blank of this Chapter.",
    "scope_correction": "",
    "source_key": "L_2015343EN.01000101 / chunk_129",
    "batch": "NLI_BATCH_3.md"
  },
  "quote_match": "contiguous_normalized",
  "scope_correction_pending": false,
  "expert_validated": false,
  "confidence_is_calibrated_probability": false,
  "prediction": "contradiction",
  "reverse_prediction_diagnostic_only": "neutral",
  "forward_probabilities": {
    "contradiction": 0.9993813037872314,
    "entailment": 1.196047287521651e-05,
    "neutral": 0.0006067493231967092
  },
  "reverse_probabilities": {
    "contradiction": 0.004361129365861416,
    "entailment": 0.0004870076954830438,
    "neutral": 0.9951518774032593
  },
  "symmetric_contradiction_score_diagnostic": 0.5018712282180786,
  "input_tokens": 97
}
```
