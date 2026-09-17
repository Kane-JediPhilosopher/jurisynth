# AI-assisted legal-text NLI adjudication

Proposed labels and model scores are withheld from this review copy.
Label premise→hypothesis as entailment, contradiction or neutral, or reject/uncertain.
First verify the premise against its supplied source. Hypotheses are synthetic, not real legal rules.
Then label the exact premise→hypothesis text, not extra facts elsewhere in the source. If scope is missing, propose a correction instead of silently adding it.
Do not import unstated law; permission does not entail obligation, and missing information is not negation.
Return pair_id, premise_supported, label, confidence, rationale, exact supporting quote, and any scope correction.
Do not tune thresholds. AI adjudication is not expert-certified ground truth.

## legal_nli_061

Premise: For subheading 2403 11, water-pipe tobacco is tobacco intended for smoking in a water pipe and consisting of tobacco and glycerol, whether or not it contains aromatic oils and extracts, molasses or sugar, and whether or not it is fruit-flavoured. Tobacco-free products intended for water-pipe smoking are excluded.

Hypothesis: Every water-pipe tobacco product must contain at least 2% nicotine.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2016294EN.01000101 / chunk_164

## legal_nli_062

Premise: When requested assistance is withheld or denied, the decision and its reasons must be notified to the applicant authority without delay.

Hypothesis: When requested assistance is withheld or denied, the applicant authority must receive the reasons.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_1994001EN.01000101 / chunk_50

## legal_nli_063

Premise: For a good or part made from a blank covered by the stated same-heading rule, origin is the country where every working edge, working surface and working part was configured to final shape and dimension, provided that the imported blank was incapable of functioning and was not advanced beyond initial stamping or the specified material-removal processing. If those criteria are not satisfied, origin is the origin of the blank of this Chapter.

Hypothesis: The stated rule concerns final configuration of every working edge, surface and part.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2015343EN.01000101 / chunk_129

## legal_nli_064

Premise: For heading 2001, vegetables, fruit, nuts and other edible plant parts prepared or preserved by vinegar or acetic acid must contain at least 0.5% free volatile acid by weight, expressed as acetic acid.

Hypothesis: The stated acid-content rule sets a minimum of 0.05% by weight instead of 0.5%.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2008291EN.01000101 / chunk_112

## legal_nli_065

Premise: The Convention enters into force six months after five eligible States have signed without reservation of ratification, acceptance or approval, or deposited their specified instruments. After that threshold, it enters into force for further Contracting Parties six months after deposit of their instruments.

Hypothesis: The fifth eligible State completed the specified step on 1 May 2027.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2009165EN.01000101 / chunk_10

## legal_nli_066

Premise: For heading 4405, wood flour means wood powder of which not more than 8% by weight is retained by a sieve with an aperture of 0.63 mm.

Hypothesis: Passing the stated sieve condition exempts the importer from customs declarations.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2011282EN.01000101 / chunk_271

## legal_nli_067

Premise: During the stated road-load procedure, elapsed time, vehicle speed and relative air velocity, including wind speed and direction, shall be measured at 5 Hz. Ambient temperature shall be synchronised and sampled at a minimum of 1 Hz. Coastdown measurements require at least ten consecutive runs, five in each direction.

Hypothesis: The stated coastdown run count is at least ten, five in each direction.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2017175EN.01000101 / chunk_157

## legal_nli_068

Premise: The Committee on Trade in Goods shall meet at the request of a Party or the Trade Committee to consider any matter arising under the relevant Chapter and shall comprise representatives of the Parties.

Hypothesis: The Trade Committee is expressly prohibited from requesting such a meeting.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2011127EN.01000101 / chunk_8

## legal_nli_069

Premise: For a good or part made from a blank covered by the stated same-heading rule, origin is the country where every working edge, working surface and working part was configured to final shape and dimension, provided that the imported blank was incapable of functioning and was not advanced beyond initial stamping or the specified material-removal processing. If those criteria are not satisfied, origin is the origin of the blank of this Chapter.

Hypothesis: If the paragraph-a criteria fail, the stated fallback is the country of origin of the blank.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2015343EN.01000101 / chunk_129

## legal_nli_070

Premise: For heading 2001, vegetables, fruit, nuts and other edible plant parts prepared or preserved by vinegar or acetic acid must contain at least 0.5% free volatile acid by weight, expressed as acetic acid.

Hypothesis: A relevant product with 0.4% free volatile acid by weight satisfies the stated minimum acid-content requirement.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2008291EN.01000101 / chunk_112

## legal_nli_071

Premise: Subsequent verification of proofs of origin shall be carried out at random or whenever the importing country's customs authorities have reasonable doubts about document authenticity, product originating status or fulfilment of the other requirements of the Protocol.

Hypothesis: The stated rule excludes reasonable doubts about document authenticity as a verification trigger.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2007345EN.01000101 / chunk_39

## legal_nli_072

Premise: Subsequent verification of proofs of origin shall be carried out at random or whenever the importing country's customs authorities have reasonable doubts about document authenticity, product originating status or fulfilment of the other requirements of the Protocol.

Hypothesis: The rule excludes doubts about fulfilment of other Protocol requirements as a verification trigger.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2007345EN.01000101 / chunk_39

## legal_nli_073

Premise: The Committee on Trade in Goods shall meet at the request of a Party or the Trade Committee to consider any matter arising under the relevant Chapter and shall comprise representatives of the Parties.

Hypothesis: Every meeting must be held in Brussels.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2011127EN.01000101 / chunk_8

## legal_nli_074

Premise: At an applicant's request, judicial authorities may issue an interlocutory injunction to prevent an imminent intellectual-property infringement, provisionally forbid continuation, or require guarantees for compensation. An injunction may also be issued against an intermediary whose services are used by a third party to infringe an intellectual-property right.

Hypothesis: An intermediary whose services are used for infringement can be subject to an interlocutory injunction.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2008289EN.01000101 / chunk_48

## legal_nli_075

Premise: For a good or part made from a blank covered by the stated same-heading rule, origin is the country where every working edge, working surface and working part was configured to final shape and dimension, provided that the imported blank was incapable of functioning and was not advanced beyond initial stamping or the specified material-removal processing. If those criteria are not satisfied, origin is the origin of the blank of this Chapter.

Hypothesis: A fully functioning imported blank satisfies the specified incapability-of-functioning condition.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2015343EN.01000101 / chunk_129

## legal_nli_076

Premise: For a good or part made from a blank covered by the stated same-heading rule, origin is the country where every working edge, working surface and working part was configured to final shape and dimension, provided that the imported blank was incapable of functioning and was not advanced beyond initial stamping or the specified material-removal processing. If those criteria are not satisfied, origin is the origin of the blank of this Chapter.

Hypothesis: The rule specifies which customs office must receive the declaration.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2015343EN.01000101 / chunk_129

## legal_nli_077

Premise: For a good or part made from a blank covered by the stated same-heading rule, origin is the country where every working edge, working surface and working part was configured to final shape and dimension, provided that the imported blank was incapable of functioning and was not advanced beyond initial stamping or the specified material-removal processing. If those criteria are not satisfied, origin is the origin of the blank of this Chapter.

Hypothesis: Configuring only one working edge is sufficient even when other working edges, surfaces and parts remain unconfigured.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2015343EN.01000101 / chunk_129

## legal_nli_078

Premise: For heading 4405, wood flour means wood powder of which not more than 8% by weight is retained by a sieve with an aperture of 0.63 mm.

Hypothesis: Retaining exactly 8% by weight satisfies the stated maximum-retention condition.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2011282EN.01000101 / chunk_271

## legal_nli_079

Premise: The Convention enters into force six months after five eligible States have signed without reservation of ratification, acceptance or approval, or deposited their specified instruments. After that threshold, it enters into force for further Contracting Parties six months after deposit of their instruments.

Hypothesis: The stated initial threshold is five eligible States completing the specified steps.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2009165EN.01000101 / chunk_10

## legal_nli_080

Premise: During the stated road-load procedure, elapsed time, vehicle speed and relative air velocity, including wind speed and direction, shall be measured at 5 Hz. Ambient temperature shall be synchronised and sampled at a minimum of 1 Hz. Coastdown measurements require at least ten consecutive runs, five in each direction.

Hypothesis: One coastdown run alone meets the stated minimum run-count requirement.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2017175EN.01000101 / chunk_157

## legal_nli_081

Premise: When requested assistance is withheld or denied, the decision and its reasons must be notified to the applicant authority without delay.

Hypothesis: The reasons for denying assistance need not be communicated to the applicant authority.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_1994001EN.01000101 / chunk_50

## legal_nli_082

Premise: For heading 2001, vegetables, fruit, nuts and other edible plant parts prepared or preserved by vinegar or acetic acid must contain at least 0.5% free volatile acid by weight, expressed as acetic acid.

Hypothesis: The tariff duty for the described products is 10%.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2008291EN.01000101 / chunk_112

## legal_nli_083

Premise: The Committee on Trade in Goods shall meet at the request of a Party or the Trade Committee to consider any matter arising under the relevant Chapter and shall comprise representatives of the Parties.

Hypothesis: The Committee must comprise only representatives of third States, not representatives of the Parties.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2011127EN.01000101 / chunk_8

## legal_nli_084

Premise: For heading 4405, wood flour means wood powder of which not more than 8% by weight is retained by a sieve with an aperture of 0.63 mm.

Hypothesis: The stated sieve aperture is 0.75 mm, not 0.63 mm.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2011282EN.01000101 / chunk_271

## legal_nli_085

Premise: During the stated road-load procedure, elapsed time, vehicle speed and relative air velocity, including wind speed and direction, shall be measured at 5 Hz. Ambient temperature shall be synchronised and sampled at a minimum of 1 Hz. Coastdown measurements require at least ten consecutive runs, five in each direction.

Hypothesis: Only equipment manufactured in the EU may be used.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2017175EN.01000101 / chunk_157

## legal_nli_086

Premise: Subsequent verification of proofs of origin shall be carried out at random or whenever the importing country's customs authorities have reasonable doubts about document authenticity, product originating status or fulfilment of the other requirements of the Protocol.

Hypothesis: Reasonable doubts about product originating status are a stated trigger for subsequent verification.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2007345EN.01000101 / chunk_39

## legal_nli_087

Premise: For a good or part made from a blank covered by the stated same-heading rule, origin is the country where every working edge, working surface and working part was configured to final shape and dimension, provided that the imported blank was incapable of functioning and was not advanced beyond initial stamping or the specified material-removal processing. If those criteria are not satisfied, origin is the origin of the blank of this Chapter.

Hypothesis: The finished good may enter the EU without any safety assessment.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2015343EN.01000101 / chunk_129

## legal_nli_088

Premise: Subsequent verification of proofs of origin shall be carried out at random or whenever the importing country's customs authorities have reasonable doubts about document authenticity, product originating status or fulfilment of the other requirements of the Protocol.

Hypothesis: The importer must pay a fixed fee for random verification.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2007345EN.01000101 / chunk_39

## legal_nli_089

Premise: The Convention enters into force six months after five eligible States have signed without reservation of ratification, acceptance or approval, or deposited their specified instruments. After that threshold, it enters into force for further Contracting Parties six months after deposit of their instruments.

Hypothesis: A further Contracting Party is bound immediately on deposit, rather than after the stated six-month interval.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_2009165EN.01000101 / chunk_10

## legal_nli_090

Premise: When requested assistance is withheld or denied, the decision and its reasons must be notified to the applicant authority without delay.

Hypothesis: The prescribed notification must occur without delay.

Scope: Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.

Source context below: L_1994001EN.01000101 / chunk_50

# Source contexts (deduplicated)

## L_2016294EN.01000101 / chunk_164

```text
1. For the purposes of subheading 2403 11, the expression 'water-pipe tobacco' means tobacco intended for smoking in a water pipe and which consists of a mixture of tobacco and glycerol, whether or not containing aromatic oils and extracts, molasses or sugar, and whether or not flavoured with fruit. However, tobacco-free products intended for smoking in a water pipe are excluded from this subheading. CN code Description Conventional rate of duty (%) Supplementary unit (1) (2) (3) (4) 2401 Unmanufactured tobacco; tobacco refuse 2401 10 - Tobacco, not stemmed/stripped 2401 10 35 - - Light air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 148 - 2401 10 60 - - Sun-cured Oriental type tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 10 70 - - Dark air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 10 85 - - Flue-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 149 - 2401 10 95 - - Other 10 MIN 22 € MAX 56 €/100 kg/net ( 150 - 2401 20 - Tobacco, partly or wholly stemmed/stripped 2401 20 35 - - Light air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 148 - 2401 20 60 - - Sun-cured Oriental type tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 20 70 - - Dark air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 20 85 - - Flue-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 149 - 2401 20 95 - - Other 11,2 MIN 22 € MAX 56 €/100 kg/net ( 150 - 2401 30 00 - Tobacco refuse 11,2 MIN 22 € MAX 56 €/100 kg/net - 2402 Cigars, cheroots, cigarillos and cigarettes, of tobacco or of tobacco substitutes 2402 10 00 - Cigars, cheroots and cigarillos, containing tobacco 26 1 000 p/st 2402 20 - Cigarettes containing tobacco 2402 20 10 - - Containing cloves 10 1 000 p/st 2402 20 90 - - Other 57,6 1 000 p/st 2402 90 00 - Other 57,6 - 2403 Other manufactured tobacco and manufactured tobacco substitutes; 'homogenised' or 'reconstituted' tobacco; tobacco extracts and essences - Smoking tobacco, whether or not containing tobacco substitutes in any proportion 2403 11 00 - - Water-pipe tobacco specified in subheading note 1 to this chapter 74,9 - 2403 19 - - Other 2403 19 10 - - - In immediate packings of a net content not exceeding 500 g 74,9 - 2403 19 90 - - - Other 74,9 - - Other 2403 91 00 - - 'Homogenised' or 'reconstituted' tobacco 16,6 - 2403 99 - - Other 2403 99 10 - - - Chewing tobacco and snuff 41,6 - 2403 99 90 - - - Other 16,6 -
SECTION V
MINERAL PRODUCTS
CHAPTER 25
```

## L_1994001EN.01000101 / chunk_50

```text
1. Where the applicant authority asks for assistance which it would itself be unable to provide if so asked, it shall draw attention to that fact in its request. It shall then be left to the requested authority to decide how to respond to such a request.
2. If assistance is withheld or denied, the decision and the reasons therefor must be notified to the applicant authority without delay.
Article 10
Obligation to observe confidentiality
Any information communicated in whatever form pursuant to this Protocol shall be of a confidential nature. It shall be covered by the obligation of official secrecy and shall enjoy the protection extended to like information under the relevant laws applicable in the Contracting Party which received it and the corresponding provisions applying to the Community authorities.
Article 11
Use of information
1. Information obtained shall be used solely for the purposes of this Protocol and may be used within each Contracting Party for other purposes only with the prior written consent of the administrative authority which furnished the information and shall be subject to any restrictions laid down by that authority. These provisions are not applicable to information concerning offences relating to narcotic drugs and psychotropic substances. Such information may be communicated to other authorities directly involved in the combat of illicit drug traffic.
2. Paragraph 1 shall not impede the use of information in any judicial or administrative proceedings subsequently instituted for failure to comply with customs legislation.
3. The Contracting Parties may, in their records of evidence, reports and testimonies and in proceedings and charges brought before the courts, use as evidence information obtained and documents consulted in accordance with the provisions of this Protocol.
Article 12
Experts and witnesses
An official of a requested authority may be authorized to appear, within the limitations of the authorization granted, as expert or witness in judicial or administrative proceedings regarding the matters covered by this Protocol in the jurisdiction of another Contracting Party, and produce such objects, documents or authenticated copies thereof, as may be needed for the proceedings. The request for an appearance must indicate specifically on what matter and by virtue of what title or qualification the official will be questioned.
Article 13
Assistance expenses
The Contracting Parties shall waive all claims on each other for the reimbursement of expenses incurred pursuant to this Protocol, except, as appropriate, for expenses to experts and witnesses and to interpreters and translators who are not dependent upon public services.
Article 14
Implementation
1. The management of this Protocol shall be entrusted to the central customs authorities of the EFTA States, on the one hand, and the competent services of the EC Commission and, where appropriate, the customs authorities of the EC Member States, on the other. They shall decide on all practical measures and arrangements necessary for its application, taking into consideration rules in the field of data protection. They may recommend to the competent bodies amendments which they consider should be made to this Protocol.
2. The Contracting Parties shall transmit to each other lists of the competent authorities appointed to act as correspondents for the purpose of the operational implementation of this Protocol.
As regards cases covered by Community competence, due account shall be taken in this respect of specific situations which, because of the urgency or the fact that only two countries are involved in a request or communication, may require direct contacts between the competent services of the EFTA States and of the EC Member States for the handling of requests or exchange of information. This information shall be supplemented by lists, to be revised when necessary, of officials of those services responsible for preventing, investigating and combating contravention of customs legislation.
Moreover, in order to ensure the maximum efficiency of operation of this Protocol, the Contracting Parties shall take appropriate measures to ensure that the departments responsible for combating customs fraud establish direct personal contacts, including when applicable at the level of local customs authorities, in order to facilitate exchange of information and handling of requests.
1. The Contracting Parties shall consult each other and subsequently keep each other informed of the detailed rules of implementation which are adopted in accordance with the provisions of this Article.
Article 15
Complementarity
1. This Protocol shall complement and not impede application of any agreements on mutual assistance which have been concluded or may be concluded between EC Member States and EFTA States as well as between the EFTA States. Nor shall it preclude more extensive mutual assistance granted under such agreements.
2. Without prejudice to Article 11, these agreements do not prejudice Community provisions governing the communication between the competent services of the EC Commission and the customs authorities of the Member States of any information obtained in customs matters which could be of Community interest.
PROTOCOL 12
on conformity assessment agreements with third countries
```

## L_2015343EN.01000101 / chunk_129

```text
(a) The country of origin of a good or part produced from a blank which by application of the Harmonized System General Interpretative Rule 2(a) is classified in the same heading, subheading or subdivision as the complete or finished good or part, shall be the country in which every working edge, working surface and working part was configured to final shape and dimension, provided, in its imported condition, the blank from which it was produced: (i) was not capable of functioning, and (ii) was not advanced beyond the initial stamping process or any processing required to remove the material from the forging platter or casting mould; (b) If the criteria in paragraph (a) are not satisfied, the country of origin is the country of origin of the blank of this Chapter.
Chapter residual rule:
Where the country of origin cannot be determined by application of the primary rules, the country of origin of the goods shall be the country in which the major portion of the materials originated, as determined on the basis of the value of the materials.
SECTION XVI
MACHINERY AND MECHANICAL APPLIANCES; ELECTRICAL EQUIPMENT; PARTS THEREOF; SOUND RECORDERS AND REPRODUCERS, TELEVISION IMAGE AND SOUND RECORDERS AND REPRODUCERS, AND PARTS AND ACCESSORIES OF SUCH ARTICLES
CHAPTER 84
Nuclear reactors, boilers, machinery and mechanical appliances; parts thereof
Primary Rule: Parts and accessories produced from blanks:
1. The country of origin of goods that are produced from blanks which by application of the HS General Interpretative Rule 2(a), are classified in the same heading, subheading or subdivision as the complete or finished goods, shall be the country in which the blank was finished provided finishing included configuring to final shape by the removal of material (other than merely by honing or polishing or both), or by forming processes such as bending, hammering, pressing or stamping. 2. Paragraph 1 above applies to goods classifiable in provisions for parts or parts and accessories, including goods specifically named under such provisions.
Definition of 'Assembly of semi-conductor products' for the purpose of heading 8473
'Assembly of semi-conductor products' means a change from chips, dice or other semi-conductor products to chips, dice or other semi-conductor products that are packaged or mounted onto a common medium for connection or connected and then mounted. The assembly of semi-conductor products shall not be considered as a minimal operation.
Chapter Notes
Note 1: Collection of parts:
Where a change in classification results from the application of HS General Interpretative Rule 2(a) with respect to collections of parts that are presented as unassembled articles of another heading or subheading the individual parts shall retain their origin prior to such collection
Note 2: Assembly of the collection of parts:
Goods assembled from a collection of parts classified as the assembled good by application of General Interpretative Rule 2 shall have origin in the country of assembly, provided the assembly would have satisfied the primary rule for the good had each of the parts been presented separately and not as a collection
Note 3: Disassembly of goods:
A change of classification which results from the disassembly of goods shall not be considered as the change required by the rule set forth in the table of 'list rules'. The country of origin of the parts recovered from the goods shall be the country where the parts are recovered, unless the importer, exporter or any person with a justifiable cause to determine the origin of parts demonstrates another country of origin on the basis of verifiable evidence.
Chapter residual rule:
Where the country of origin cannot be determined by application of the primary rules, the country of origin of the goods shall be the country in which the major portion of the materials originated, as determined on the basis of the value of the materials.
CHAPTER 85
Electrical machinery and equipment and parts thereof; sound recorders and reproducers, television image and sound recorders and reproducers, and parts and accessories of such articles
Primary Rule: Parts and accessories produced from blanks:
(1) The country of origin of goods that are produced from blanks which by application of the HS General Interpretative Rule 2(a) are classified in the same heading, subheading or subdivision as the complete or finished goods, shall be the country in which the blank was finished provided finishing included configuring to final shape by the removal of material (other than merely by honing or polishing or both), or by forming processes such as bending, hammering, pressing or stamping. (2) Paragraph 1 above applies to goods classifiable in provisions for parts or parts and accessories, including goods specifically named under such provisions.
```

## L_2008291EN.01000101 / chunk_112

```text
1. For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid. In addition, mushrooms of subheading 2001 90 50 should not have a salt content exceeding 2,5 % by weight. 2. 3. The products of subheadings 2008 20 to 2008 80 , 2008 92 and 2008 99 shall be considered as containing added sugar when the 'sugar content' thereof exceeds by weight the percentages given hereunder, according to the kind of fruit or edible part of plant concerned: - pineapples and grapes: 13 %, - other fruits, including mixtures of fruit, and other edible parts of plants: 9 %. 4. For the purposes of subheadings 2008 30 11 to 2008 30 39 , 2008 40 11 to 2008 40 39 , 2008 50 11 to 2008 50 59 , 2008 60 11 to 2008 60 39 , 2008 70 11 to 2008 70 59 , 2008 80 11 to 2008 80 39 , 2008 92 12 to 2008 92 38 and 2008 99 11 to 2008 99 40 , the following expressions shall have the meanings hereby assigned to them: - 'actual alcoholic strength by mass': the number of kilograms of pure alcohol contained in 100 kg of the product, - '% mas': the symbol for alcoholic strength by mass. 5. The following shall be applied to the products as they are presented: (a) the added sugar content of products of heading 2009 corresponds to the 'sugar content' less the figures given hereunder, according to the kind of juice concerned: - lemon or tomato juice: 3, - grape juice: 15, - other fruit or vegetable juices, including mixtures of juices: 13. (b) the fruit juices with added sugar, of a Brix value not exceeding 67 and containing less than 50 % by weight of fruit juice lose their original character of fruit juices of heading 2009 . Item (b) shall not apply to concentrated natural fruit juices. Consequently, concentrated natural fruit juices are not excluded from heading 2009 . 6. For the purposes of subheadings 2009 69 51 and 2009 69 71 , 'concentrated grape juice (including grape must)' means grape juice (including grape must) for which the figure indicated by a refractometer (used in accordance with the method prescribed in the Annex to Regulation (EEC) No 558/93) at a temperature of 20 °C is not less than 50,9 %. 7.
```

## L_2009165EN.01000101 / chunk_10

```text
Article 53
Entry into force
1. This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession.
2. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.
3. Any instrument of ratification, acceptance, approval or accession deposited after the entry into force of an amendment to this Convention shall be deemed to apply to this Convention as amended.
4. Any such instrument deposited after an amendment has been accepted but before it has entered into force shall be deemed to apply to this Convention as amended on the date when the amendment enters into force.
Article 54
Denunciation
1. Any Contracting Party may denounce this Convention by so notifying the Secretary-General of the United Nations.
2. Denunciation shall take effect fifteen months after the date of receipt by the Secretary-General of the notification of denunciation.
3. The validity of TIR Carnets accepted by the Customs office of departure before the date when the denunciation takes effect shall not be affected thereby and the guarantee of the guaranteeing association shall hold good in accordance with the provisions of this Convention.
Article 55
Termination
If, after the entry into force of this Convention, the number of States which are Contracting Parties is for any period of twelve consecutive months reduced to less than five, the Convention shall cease to have effect from the end of the twelve-month period.
Article 56
Termination of the operation of the TIR Convention, 1959
1. Upon its entry into force, this Convention shall terminate and replace, in relations between the Contracting Parties to this Convention, the TIR Convention, 1959.
2. Certificates of approval issued in respect of road vehicles and containers under the conditions of the TIR Convention, 1959, shall be accepted during the period of their validity or any extension thereof for the transport of goods under Customs seal by Contracting Parties to this Convention, provided that such vehicles and containers continue to fulfil the conditions under which they were originally approved.
Article 57
Settlement of disputes
1. Any dispute between two or more Contracting Parties concerning the interpretation or application of this Convention shall, so far as possible be settled by negotiation between them or other means of settlement.
2. Any dispute between two or more Contracting Parties concerning the interpretation or application of this Convention which cannot be settled by the means indicated in paragraph 1 of this Article shall, at the request of one of them, be referred to an arbitration tribunal composed as follows: each Party to the dispute shall appoint an arbitrator and these arbitrators shall appoint another arbitrator, who shall be chairman. If, three months after receipt of a request, one of the Parties has failed to appoint an arbitrator or if the arbitrators have failed to elect the chairman, any of the Parties may request the Secretary-General of the United Nations to appoint an arbitrator or the chairman of the arbitration tribunal.
3. The decision of the arbitration tribunal established under the provisions of paragraph 2 shall be binding on the Parties to the dispute.
4. The arbitration tribunal shall determine its own rules of procedure.
5. Decisions of the arbitration tribunal shall be taken by majority vote.
6. Any controversy which may arise between the Parties to the dispute as regards the interpretation and execution of the award may be submitted by any of the Parties for judgment to the arbitration tribunal which made the award.
Article 58
Reservations
1. Any State may, at the time of signing, ratifying or acceding to this Convention, declare that it does not consider itself bound by Article 57, paragraphs 2 to 6, of this Convention. Other Contracting Parties shall not be bound by these paragraphs in respect of any Contracting Party which has entered such a reservation.
2. Any Contracting Party having entered a reservation as provided for in paragraph 1 of this Article may at any time withdraw such reservation by notifying the Secretary-General of the United Nations.
3. Apart from the reservations provided for in paragraph 1 of this Article, no reservation to this Convention shall be permitted.
Article 58 bis
Administrative Committee
An Administrative Committee composed of all the Contracting Parties shall be established. Its composition, functions and rules of procedure are set out in Annex 8.
Article 58 ter
TIR Executive Board
```

## L_2011282EN.01000101 / chunk_271

```text
1. For the purposes of heading 4405 , 'wood flour' means wood powder of which not more than 8 % by weight is retained by a sieve with an aperture of 0,63 mm. 2. For the purposes of subheadings 4414 00 10 , 4418 10 10 , 4418 20 10 , 4419 00 10 , 4420 10 11 and 4420 90 91 , 'tropical wood' means the following tropical woods: acajou d'Afrique, alan, azobé, balsa, dark red meranti, dibétou, ilomba, imbuia, iroko, jelutong, jongkong, kapur, kempas, keruing, light red meranti, limba, mahogany (Swietenia spp.), makoré, mansonia, meranti bakau, merbau, obeche, okoumé, palissandre de Para, palissandre de Rio, palissandre de Rose, ramin, sapelli, sipo, teak, tiama, virola, white lauan, white meranti, white seraya and yellow meranti. CN code Description Conventional rate of duty (%) Supplementary unit (1) (2) (3) (4) 4401 Fuel wood, in logs, in billets, in twigs, in faggots or in similar forms; wood in chips or particles; sawdust and wood waste and scrap, whether or not agglomerated in logs, briquettes, pellets or similar forms 4401 10 00 - Fuel wood, in logs, in billets, in twigs, in faggots or in similar forms Free - - Wood in chips or particles 4401 21 00 - - Coniferous Free - 4401 22 00 - - Non-coniferous Free - - Sawdust and wood waste and scrap, whether or not agglomerated in logs, briquettes, pellets or similar forms 4401 31 00 - - Wood pellets Free - 4401 39 - - Other 4401 39 10 - - - Sawdust Free - 4401 39 90 - - - Other Free - 4402 Wood charcoal (including shell or nut charcoal), whether or not agglomerated 4402 10 00 - Of bamboo Free - 4402 90 00 - Other Free - 4403 Wood in the rough, whether or not stripped of bark or sapwood, or roughly squared 4403 10 00 - Treated with paint, stains, creosote or other preservatives Free m 3 4403 20 - Other, coniferous - - Spruce of the species ' Picea abies Karst. Abies alba Mill. 4403 20 11 - - - Sawlogs Free m 3 4403 20 19 - - - Other Free m 3 - - Pine of the species ' Pinus sylvestris L.
```

## L_2017175EN.01000101 / chunk_157

```text
4.3.2.2. Selection of vehicle speed range for road load curve determination
The test vehicle speed range shall be selected according to paragraph 2.2. of this Sub-Annex.
4.3.2.3. Data collection
During the procedure, elapsed time, vehicle speed, and air velocity (wind speed, direction) relative to the vehicle, shall be measured at a frequency of 5 Hz. Ambient temperature shall be synchronised and sampled at a minimum frequency of 1 Hz.
4.3.2.4. Vehicle coastdown procedure
The measurements shall be carried out in opposite directions until a minimum of ten consecutive runs (five in each direction) have been obtained. Should an individual run fail to satisfy the required on-board anemometry test conditions, that run and the corresponding run in the opposite direction shall be rejected. All valid pairs shall be included in the final analysis with a minimum of 5 pairs of coastdown runs. See paragraph 4.3.2.6.10. of this Sub-Annex for statistical validation criteria.
The anemometer shall be installed in a position such that the effect on the operating characteristics of the vehicle is minimised.
The anemometer shall be installed according to one of the options below:
(a) Using a boom approximately 2 metres in front of the vehicle's forward aerodynamic stagnation point; (b) On the roof of the vehicle at its centreline. If possible, the anemometer shall be mounted within 30 cm from the top of the windshield. (c) On the engine compartment cover of the vehicle at its centreline, mounted at the midpoint position between the vehicle front and the base of the windshield.
In all cases, the anemometer shall be mounted parallel to the road surface. In the event that positions (b) or (c) are used, the coastdown results shall be analytically adjusted for the additional aerodynamic drag induced by the anemometer. The adjustment shall be made by testing the coastdown vehicle in a wind tunnel both with and without the anemometer installed in the same position as used on the track., The calculated difference shall be the incremental aerodynamic drag coefficient C D combined with the frontal area, which shall be used to correct the coastdown results.
4.3.2.4.1. Following the vehicle warm-up procedure described in paragraph 4.2.4. of this Sub-Annex and immediately prior to each test measurement, the vehicle shall be accelerated to 10 to 15 km/h above the highest reference speed and shall be driven at that speed for a maximum of 1 minute. After that, the coastdown shall be started immediately. 4.3.2.4.2. During a coastdown, the transmission shall be in neutral. Any steering wheel movement shall be avoided as much as possible, and the vehicle's brakes shall not be operated. 4.3.2.4.3. It is recommended that each coastdown run be performed without interruption. Split runs may however be performed if data cannot be collected in a single run for all the reference speed points. For split runs, care shall be taken so that vehicle conditions remain as stable as possible at each split point.
4.3.2.5. Determination of the equation of motion
Symbols used in the on-board anemometer equations of motion are listed in Table A4/4.
Table A4/4
Symbols used in the on-board anemometer equations of motion
4.3.2.5.1. General form
The general form of the equation of motion is as follows:
where:
D mech = D tyre f r D aero = D grav =
In the case that the slope of the test track is equal to or less than 0.1 per cent over its length, D grav may be set to zero.
4.3.2.5.2. Mechanical drag modelling
Mechanical drag consisting of separate components representing tyre D tyre and front and rear axle frictional losses, D f and D r , including transmission losses) shall be modelled as a three-term polynomial as a function of vehicle speed v as in the equation below:
where:
A m , B m , and C m are determined in the data analysis using the least squares method. These constants reflect the combined driveline and tyre drag.
In the case that the tested vehicle is the representative vehicle of a road load matrix family, the coefficient B m shall be set to zero and the coefficients A m and C m shall be recalculated with a least squares regression analysis.
4.3.2.5.3. Aerodynamic drag modelling
The aerodynamic drag coefficient C D (Y) shall be modelled as a four-term polynomial as a function of yaw angle Y as in the equation below:
a 0 to a 4 are constant coefficients whose values are determined in the data analysis.
```

## L_2011127EN.01000101 / chunk_8

```text
1. The Committee on Trade in Goods established pursuant to Article 15.2.1 (Specialised Committees) shall meet on the request of a Party or of the Trade Committee to consider any matter arising under this Chapter and comprise representatives of the Parties.
2. The Committee's functions shall include:
(a) promoting trade in goods between the Parties, including through consultations on accelerating and broadening the scope of tariff elimination and broadening of the scope of commitments on non-tariff measures under this Agreement and other issues as appropriate; and (b) addressing tariff and non-tariff measures to trade in goods between the Parties and, if appropriate, referring such matters to the Trade Committee for its consideration, in so far as these tasks have not been entrusted to the relevant Working Groups established pursuant to Article 15.3.1 (Working Groups).
Article 2.17
Special provisions on administrative cooperation
1. The Parties agree that administrative cooperation is essential for the implementation and the control of preferential tariff treatment granted under this Chapter and underline their commitments to combat irregularities and fraud in customs and related matters.
2. Where a Party has made a finding, on the basis of objective information, of a failure to provide administrative cooperation and/or irregularities or fraud, on the request of that Party, the Customs Committee shall meet within 20 days of such request to seek, as a matter of urgency, to resolve the situation. The consultations held within the framework of the Customs Committee will be considered as fulfilling the same function as consultation under Article 14.3 (Consultations).
CHAPTER THREE
TRADE REMEDIES
SECTION A
Bilateral safeguard measures
Article 3.1
Application of a bilateral safeguard measure
1. If, as a result of the reduction or elimination of a customs duty under this Agreement, originating goods of a Party are being imported into the territory of the other Party in such increased quantities, in absolute terms or relative to domestic production, and under such conditions as to cause or threaten to cause serious injury to a domestic industry producing like or directly competitive goods, the importing Party may adopt measures provided for in paragraph 2 in accordance with the conditions and procedures laid down in this Section.
2. The importing Party may take a bilateral safeguard measure which:
(a) suspends further reduction of the rate of customs duty on the good concerned provided for under this Agreement; or (b) increases the rate of customs duty on the good to a level which does not exceed the lesser of: (i) the MFN applied rate of customs duty on the good in effect at the time the measure is taken; or (ii) the base rate of customs duty specified in the Schedules included in Annex 2-A (Elimination of Customs Duties) pursuant to Article 2.5.2 (Elimination of Customs Duties).
Article 3.2
Conditions and limitations
1. A Party shall notify the other Party in writing of the initiation of an investigation described in paragraph 2 and consult with the other Party as far in advance of applying a bilateral safeguard measure as practicable, with a view to reviewing the information arising from the investigation and exchanging views on the measure.
2. A Party shall apply a bilateral safeguard measure only following an investigation by its competent authorities in accordance with Articles 3 and 4.2(c) of the Agreement on Safeguards contained in Annex 1A to the WTO Agreement (hereinafter referred to as the 'Agreement on Safeguards') and to this end, Articles 3 and 4.2(c) of the Agreement on Safeguards are incorporated into and made part of this Agreement, mutatis mutandis .
3. In the investigation described in paragraph 2, the Party shall comply with the requirements of Article 4.2(a) of the Agreement on Safeguards and to this end, Article 4.2(a) of the Agreement on Safeguards is incorporated into and made part of this Agreement, mutatis mutandis .
4. Each Party shall ensure that its competent authorities complete any such investigation within one year of its date of initiation.
5. Neither Party may apply a bilateral safeguard measure:
(a) except to the extent, and for such time, as may be necessary to prevent or remedy serious injury and to facilitate adjustment; (b) for a period exceeding two years, except that the period may be extended by up to two years if the competent authorities of the importing Party determine, in conformity with the procedures specified in this Article, that the measure continues to be necessary to prevent or remedy serious injury and to facilitate adjustment and that there is evidence that the industry is adjusting, provided that the total period of application of a safeguard measure, including the period of initial application and any extension thereof, shall not exceed four years; or (c) beyond the expiration of the transition period, except with the consent of the other Party.
```

## L_2007345EN.01000101 / chunk_39

```text
1. Subsequent verifications of proofs of origin shall be carried out at random or whenever the customs authorities of the importing country have reasonable doubts as to the authenticity of such documents, the originating status of the products concerned or the fulfilment of the other requirements of this Protocol.
2. For the purposes of implementing the provisions of paragraph 1, the customs authorities of the importing country shall return the movement certificate EUR.1 and the invoice, if it has been submitted, the invoice declaration, or a copy of these documents, to the customs authorities of the exporting country giving, where appropriate, the reasons for the enquiry. Any documents and information obtained suggesting that the information given on the proof of origin is incorrect shall be forwarded in support of the request for verification.
3. The verification shall be carried out by the customs authorities of the exporting country. For this purpose, they shall have the right to call for any evidence and to carry out any inspection of the exporter's accounts or any other check considered appropriate.
4. If the customs authorities of the importing country decide to suspend the granting of preferential treatment to the products concerned while awaiting the results of the verification, release of the products shall be offered to the importer subject to any precautionary measures judged necessary.
5. The customs authorities requesting the verification shall be informed of the results of this verification as soon as possible. These results must indicate clearly whether the documents are authentic and whether the products concerned can be considered as products originating in the Community, in Montenegro or in one of the other countries or territories referred to in Articles 3 and 4 and fulfil the other requirements of this Protocol.
6. If in cases of reasonable doubt there is no reply within ten months of the date of the verification request or if the reply does not contain sufficient information to determine the authenticity of the document in question or the real origin of the products, the requesting customs authorities shall, except in exceptional circumstances, refuse entitlement to the preferences.
Article 34
Dispute settlement
Where disputes arise in relation to the verification procedures of Article 33 which cannot be settled between the customs authorities requesting a verification and the customs authorities responsible for carrying out this verification or where they raise a question as to the interpretation of this Protocol, they shall be submitted to the Interim Committee.
In all cases the settlement of disputes between the importer and the customs authorities of the importing country shall be under the legislation of the said country.
Article 35
Penalties
Penalties shall be imposed on any person who draws up, or causes to be drawn up, a document which contains incorrect information for the purpose of obtaining a preferential treatment for products.
Article 36
Free zones
1. The Community and Montenegro shall take all necessary steps to ensure that products traded under cover of a proof of origin which in the course of transport use a free zone situated in their territory, are not substituted by other goods and do not undergo handling other than normal operations designed to prevent their deterioration.
2. By means of an exemption to the provisions contained in paragraph 1, when products originating in the Community or in Montenegro are imported into a free zone under cover of a proof of origin and undergo treatment or processing, the authorities concerned shall issue a new movement certificate EUR.1 at the exporter's request, if the treatment or processing undergone is in conformity with the provisions of this Protocol.
TITLE VII
CEUTA AND MELILLA
Article 37
Application of this Protocol
1. The term 'Community' used in Article 2 does not cover Ceuta or Melilla.
2. Products originating in Montenegro, when imported into Ceuta and Melilla, shall enjoy in all respects the same customs regime as that which is applied to products originating in the customs territory of the Community under Protocol 2 of the Act of Accession of the Kingdom of Spain and the Portuguese Republic to the European Communities. Montenegro shall grant to imports of products covered by this Agreement and originating in Ceuta and Melilla the same customs regime as that which is granted to products imported from and originating in the Community.
3. For the purpose of the application of paragraph 2 concerning products originating in Ceuta and Melilla, this Protocol shall apply mutatis mutandis subject to the special conditions set out in Article 38.
Article 38
Special conditions
1. Providing they have been transported directly in accordance with the provisions of Article 13, the following shall be considered as:
2. products originating in Ceuta and Melilla:
(a) products wholly obtained in Ceuta and Melilla; (b) products obtained in Ceuta and Melilla in the manufacture of which products other than those referred to in (a) are used, provided that: (i) the said products have undergone sufficient working or processing within the meaning of Article 6; or that (ii) those products are originating in Montenegro or in the Community, provided that they have been submitted to working or processing which goes beyond the operations referred to in Article 7
```

## L_2008289EN.01000101 / chunk_48

```text
1. The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.
2. An interlocutory injunction may also be issued to order the seizure or delivery up of the goods suspected of infringing an intellectual property right so as to prevent their entry into or movement within channels of commerce.
3. In the case of an infringement committed on a commercial scale, the EC Party and the Signatory CARIFORUM States shall ensure that, if the applicant demonstrates circumstances likely to endanger the recovery of damages, the judicial authorities may order the precautionary seizure of the movable and immovable property of the alleged infringer, including the blocking of his/her bank accounts and other assets. To that end, the competent authorities may order the communication of bank, financial or commercial documents, or appropriate access to the relevant information.
Article 157
Corrective measures
1. The EC Party and the Signatory CARIFORUM States shall ensure that the competent judicial authorities may order, at the request of the applicant and without prejudice to any damages due to the right holder by reason of the infringement, and without compensation of any sort, the recall, definitive removal from channels of commerce or destruction of goods that they have found to be infringing an intellectual property right.
2. The EC Party and the Signatory CARIFORUM States shall ensure that those measures are carried out at the expense of the infringer, unless particular reasons are invoked for not doing so.
Article 158
Injunctions
The EC Party and the Signatory CARIFORUM States shall ensure that, where a judicial decision is taken finding an infringement of an intellectual property right, the judicial authorities may issue against the infringer an injunction aimed at prohibiting the continuation of the infringement. Where provided for by national law, non-compliance with an injunction shall, where appropriate, be subject to a recurring penalty payment, with a view to ensuring compliance. The EC Party and the Signatory CARIFORUM States shall also ensure that right holders are in a position to apply for an injunction against intermediaries whose services are used by a third party to infringe an intellectual property right.
Article 159
Alternative measures
The EC Party and the Signatory CARIFORUM States may provide that, in appropriate cases and at the request of the person liable to be subject to the measures provided for in Part III of the TRIPS Agreement and in this Chapter, the competent judicial authorities may order pecuniary compensation to be paid to the injured party instead of applying the measures provided for in Part III of the TRIPS Agreement or in this Chapter if that person acted unintentionally and without negligence, if execution of the measures in question would cause him disproportionate harm and if pecuniary compensation to the injured party appears reasonably satisfactory.
Article 160
Damages
1. The EC Party and the Signatory CARIFORUM States shall ensure that when the judicial authorities set the damages:
(a) they shall take into account all appropriate aspects, such as the negative economic consequences, including lost profits, which the injured party has suffered, any unfair profits made by the infringer and, in appropriate cases, elements other than economic factors; or (b) as an alternative to (a), they may, in appropriate cases, set the damages as a lump sum on the basis of elements such as at least the amount of royalties or fees which would have been due if the infringer had requested authorisation to use the intellectual property right in question.
1. Where the infringer did not know, or did not have reasonable grounds to know, that he, she or it was engaging in infringing activity, the EC Party and the Signatory CARIFORUM States may provide that the judicial authorities may order the recovery of profits or the payment of damages which may be pre-established.
Article 161
Legal costs
The EC Party and the Signatory CARIFORUM States shall ensure that their domestic law contains measures for the allocation of costs which generally require that the unsuccessful party will bear the costs, unless equity requires that costs be allocated otherwise.
Article 162
Publication of judicial decisions
```
