# Focused AI-assisted review follow-up

No expert validation is claimed. Do not score system QA accuracy: system answers have not been generated.

For each of the six pending questions below, return a natural user-facing question, readable instrument/title and date or allocation period, revised reference answer, and exact supporting chunks/table rows. Keep machine IDs in metadata, not question text. Avoid implying simultaneous legal applicability across unrelated instruments. If supplied context cannot establish the title or period, mark unresolved rather than inventing it.

For the two NLI families, supply a corrected source-faithful premise preserving modal verbs and scope, then confirm or revise the labels for all nine hypotheses against that exact new premise. These are synthetic, AI-adjudicated labels, not independent expert gold.

## QA global_natural_003

```json
{
  "case_id": "global_natural_003",
  "category": "obligation_prohibition",
  "question": "Under the aquatic-toxicity testing procedure described in the source, what information must the test report contain?",
  "proposed_reference_answer": "The report checklist covers test substance, test species and test conditions. Complete the draft against the full supplied checklist; do not invent missing endpoint/report requirements.",
  "reference_status": "AI_adjudicated",
  "system_answer": null,
  "score_eligible": false,
  "expected_chunks": [
    {
      "document_id": "L_2008142EN.01000101",
      "chunk_id": "chunk_319",
      "excerpt": "The results should be interpreted with caution where measured toxicant concentrations in test solutions occur at levels near the detection limit of the analytical method or, in semi static tests, when the concentration of the test substance decreases between freshly prepared solution and before renewal. 2.3. TEST REPORT The test report must include the following information: 2.3.1. Test substance: - physical nature and relevant physical-chemical properties; - chemical identification data including purity and analytical method for quantification of the test substance where appropriate. 2.3.2. Test species: - scientific name, possibly - strain, size, supplier, any pre-treatment, etc. 2.3.3. Test conditions: - test procedure used (e.g. semi-static/renewal, flow-through, loading, stocking density, etc.), - test design (e.g. number of test vessels, test concentrations and replicates, number of fish per vessel), - method of preparation of stock solutions and frequency of renewal (the solubilising agent and its concentration must be given, when used), - the nominal test concentrations, the ",
      "full_text": "The results should be interpreted with caution where measured toxicant concentrations in test solutions occur at levels near the detection limit of the analytical method or, in semi static tests, when the concentration of the test substance decreases between freshly prepared solution and before renewal.\n2.3. TEST REPORT\nThe test report must include the following information:\n2.3.1. Test substance:\n- physical nature and relevant physical-chemical properties; - chemical identification data including purity and analytical method for quantification of the test substance where appropriate.\n2.3.2. Test species:\n- scientific name, possibly - strain, size, supplier, any pre-treatment, etc.\n2.3.3. Test conditions:\n- test procedure used (e.g. semi-static/renewal, flow-through, loading, stocking density, etc.), - test design (e.g. number of test vessels, test concentrations and replicates, number of fish per vessel), - method of preparation of stock solutions and frequency of renewal (the solubilising agent and its concentration must be given, when used), - the nominal test concentrations, the means of the measured values and their standard deviations in the test vessels and the method by which these were attained and evidence that the measurements refer to the concentrations of the test substance in true solution, - dilution water characteristics: pH, hardness, alkalinity, temperature, dissolved oxygen concentration, residual chlorine levels (if measured), total organic carbon, suspended solids, salinity of the test medium (if measured) and any other measurements made, - water quality within test vessels: pH, hardness, temperature and dissolved oxygen concentration, - detailed information on feeding, (e.g. type of food(s), source, amount given and frequency).\n2.3.4. Results:\n- evidence that controls met the validity criterion for survival, and data on mortalities occurring in any of the test concentrations, - statistical analytical techniques used, statistics based on replicates or fish, treatment of data and justification of techniques used, - tabulated data on individual and mean fish weights on days 0, 14 (if measured) and 28 values of tank-average or pseudo specific growth rates (as appropriate) for the periods 0-28 days or possibly 0-14 and 14-28, - results of the statistical analysis (i.e. regression analysis or ANOVA) preferably in tabular and graphical form and the LOEC (p = 0,05) and the NOEC or ECx with, when possible, standard errors, as appropriate, - incidence of any unusual reactions by the fish and any visible effects produced by the test substance.\n1. REFERENCES",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    }
  ],
  "expected_tables": [],
  "retrieved_chunks": [
    {
      "document_id": "L_2013093EN.01008501",
      "chunk_id": "chunk_26",
      "excerpt": "1. Testing of the plant protection product shall be necessary where its toxicity cannot be predicted on the basis of data on the active substance. Where testing is necessary, the aim shall be to demonstrate whether the plant protection product, taking account of content of active substance, is more toxic than the active substance. Thus bridging studies or a limit test may be sufficient. However, where a plant protection product is more toxic than the active substance (expressed in comparable units), definitive testing shall be required. Possible effects on organisms/ecosystems shall be investigated, unless the applicant shows that exposure of the organisms or ecosystems does not occur. Tests and studies conducted using the plant protection product as test material necessary to assess the toxicity of the active substance shall be reported in the context of the relevant data requirement co",
      "origin": [
        "direct"
      ],
      "full_text": "1. Testing of the plant protection product shall be necessary where its toxicity cannot be predicted on the basis of data on the active substance. Where testing is necessary, the aim shall be to demonstrate whether the plant protection product, taking account of content of active substance, is more toxic than the active substance. Thus bridging studies or a limit test may be sufficient. However, where a plant protection product is more toxic than the active substance (expressed in comparable units), definitive testing shall be required. Possible effects on organisms/ecosystems shall be investigated, unless the applicant shows that exposure of the organisms or ecosystems does not occur. Tests and studies conducted using the plant protection product as test material necessary to assess the toxicity of the active substance shall be reported in the context of the relevant data requirement concerning the active substance. 2. All potentially adverse effects found during routine ecotoxicological investigations shall be reported and such additional studies, which may be necessary to investigate the mechanisms involved and assess the significance of these effects, shall be undertaken and reported. 3. Whenever a study implies the use of different doses, the relationship between dose and adverse effect shall be reported. 4. Where exposure data are necessary to decide whether a study has to be performed, the data obtained in accordance with Section 9 shall be used. For the estimation of exposure of organisms, all information on the plant protection product and on the active substance shall be taken into account. A tiered approach shall start with default worst-case parameters for exposure and be followed by a parameter refinement based on the identification of representative organisms. Where relevant, the parameters set out in this Section shall be used. Where it appears from available data that the plant protection product is more toxic than the active substance, the toxicity data for the plant protection product shall be used for the calculation of appropriate risk quotients (see point 8 of this introduction). 5. The requirements laid down in this Section shall include certain study types that are set out in Section 8 of Part A of the Annex to Regulation (EU) No 283/2013 (such as standard laboratory tests with birds, aquatic organisms, bees, arthropods, earthworms, soil micro-organisms, soil meso-fauna and non-target plants). While each point shall be addressed, experimental data with a plant protection product shall be generated only if its toxicity cannot be predicted on the basis of data on the active substance. It may be sufficient to test the plant protection product with that species of a group that was most sensitive with the active substance. 6. A detailed description (specification) of the material used as provided for in accordance with point 1.4 shall be provided. 7. In order to facilitate the assessment of the significance of test results obtained, the same strain of each species shall, where possible, be used in the various toxicity tests specified. 8. The ecotoxicological assessment shall be based on the risk that the proposed plant protection product poses to non-target organisms. In carrying out a risk assessment, toxicity shall be compared with exposure. The general term for the output from such a comparison is 'risk quotient' (RQ). RQ may be expressed in several ways, for example, toxicity:exposure ratio (TER) and as a hazard quotient (HQ). 9. For those guidelines which allow for study to be designed to determine an effective concentration (EC x 10 20 x Existing acceptable studies that have been designed to generate a NOEC shall not be repeated. An assessment of the statistical power of the NOEC derived from those studies shall be carried out. 10. For solid formulations an assessment of the risk from dust drift on to non-target arthropods and plants shall be required. Details on the likely exposure levels shall be presented in accordance with Section 9 of this Annex. For aquatic life, the risk of movement of the whole particle as well as dust particles shall be considered. Until agreed dust dissipation rate assessments are available likely exposure levels shall be used in the risk assessment. 11. Higher tier studies using a plant protection product shall be designed and data analysed using suitable statistical methods. Full details of the statistical methods shall be reported. Where appropriate, higher tier studies shall be supported by chemical analysis to verify exposure has occurred at an appropriate level. 12. Pending the validation and adoption of new studies and of a new risk assessment scheme, existing protocols shall be used to address the acute and chronic risk to bees, including those on colony survival and development, and the identification and measurement of sub-lethal effects in the risk assessment.\n10.1. Effects on birds and other terrestrial vertebrates\n10.1.1. Effects on birds\nPossible risks to birds shall be investigated if the toxicity of the plant protection product cannot be predicted on the basis of the data for the active substance, except, for example, where the plant protection product is used in enclosed spaces or for wound-healing treatments where birds will experience neither direct nor secondary exposure.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2013093EN.01008501",
      "chunk_id": "chunk_39",
      "excerpt": "For each method of application and each use, the rate of application per unit (ha, m 2 , m 3 ) treated, in terms of g or kg or l for the preparation and in terms of appropriate units for the micro-organism, must be provided. Application rates shall normally be expressed in g or kg/ha or in kg/m 3 and where appropriate in g or kg/tonne; for protected crops and home gardening use rates shall be expressed in g or kg/100 m 2 or g or kg/m 3 . 3.5. Content of micro-organism in material used (e.g. in the diluted spray, baits or treated seed) The content of micro-organism shall be reported, as appropriate, in number of active unit/ml or g or any other relevant unit. 3.6. Method of application The method of application proposed must be described fully, indicating the type of equipment to be used, if any, as well as the type and volume of diluent to be used per unit of area or volume. 3.7. Number ",
      "origin": [
        "direct"
      ],
      "full_text": "For each method of application and each use, the rate of application per unit (ha, m 2 , m 3 ) treated, in terms of g or kg or l for the preparation and in terms of appropriate units for the micro-organism, must be provided.\nApplication rates shall normally be expressed in g or kg/ha or in kg/m 3 and where appropriate in g or kg/tonne; for protected crops and home gardening use rates shall be expressed in g or kg/100 m 2 or g or kg/m 3 .\n3.5. Content of micro-organism in material used (e.g. in the diluted spray, baits or treated seed)\nThe content of micro-organism shall be reported, as appropriate, in number of active unit/ml or g or any other relevant unit.\n3.6. Method of application\nThe method of application proposed must be described fully, indicating the type of equipment to be used, if any, as well as the type and volume of diluent to be used per unit of area or volume.\n3.7. Number and timing of applications and duration of protection\nThe maximum number of applications to be used and their timing, must be reported. Where relevant the growth stages of the crop or plants to be protected and the development stages of the harmful organisms, must be indicated. Where possible and necessary the interval between applications, in days, must be stated.\nThe duration of protection afforded both by each application and by the maximum number of applications to be used, must be indicated.\n3.8. Necessary waiting periods or other precautions to avoid phytopathogenic effects on succeeding crops\nWhere relevant, minimum waiting periods between last application and sowing or planting of succeeding crops, which are necessary to avoid phytopathogenic effects on succeeding crops, must be stated, and follow from the data provided under Section 6, point 6.6.\nLimitations on choice of succeeding crops, if any, must be stated.\n3.9. Proposed instructions for use\nThe proposed instructions for use of the preparation, to be printed on labels and leaflets, must be provided.\n1. FURTHER INFORMATION ON THE PLANT PROTECTION PRODUCT\n4.1. Packaging and compatibility of the preparation with proposed packaging materials\n(i) Packaging to be used must be fully described and specified in terms of the materials used, manner of construction (e.g. extruded, welded, etc.), size and capacity, size of opening, type of closure and seals. It must be designed in accordance with the criteria and guidelines specified in the FAO 'Guidelines for the Packaging of Pesticides'. (ii) The suitability of the packaging, including closures, in terms of its strength, leakproofness and resistance to normal transport and handling, must be determined and reported in accordance with ADR methods 3552, 3553, 3560, 3554, 3555, 3556, 3558, or appropriate ADR Methods for intermediate bulk containers, and, where for the preparation child-resistant closures are required, in accordance with ISO standard 8317. (iii) The resistance of the packaging material to its contents must be reported in accordance with GIFAP Monograph No 17.\n4.2. Procedures for cleaning application equipment\nCleaning procedures for both application equipment and protective clothing must be described in detail. The effectiveness of the cleaning procedure must be determined, using e.g. biotests, and reported.\n4.3. Re-entry periods, necessary waiting periods or other precautions to protect man, livestock and the environment\nThe information provided must follow from and be supported by the data provided for the micro-organism(s) and that provided under Sections 7 and 8.\n(i) Where relevant pre-harvest intervals, re-entry periods or withholding periods necessary to minimise the presence of residues in or on crops, plants and plant products, or in treated areas or spaces, with a view to protecting man or livestock, must be specified e.g.: - pre-harvest interval (in days) for each relevant crop, - re-entry period (in days) for livestock, to areas to be grazed, - re-entry period (in hours or days) for man to crops, buildings or spaces treated, - withholding period (in days) for animal feedingstuffs, - waiting period (in days), between application and handling treated products. (ii) Where necessary, in the light of the test results, information on any specific agricultural, plant health or environmental conditions under which the preparation may or may not be used must be provided.\n4.4. Recommended methods and precautions concerning: handling, storage, transport or fire",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2018285EN.01009701",
      "chunk_id": "chunk_7",
      "excerpt": "[( 9 )](#ntc9-L_2018285EN.01009701-E0009) Commission Decision 2012/629/EU of 10 October 2012 amending Decision 2008/577/EC accepting the undertakings offered in connection with the anti-dumping proceeding concerning imports of ammonium nitrate originating in Russia ( [OJ L 277, 11.10.2012, p. 8](http://publications.europa.eu/resource/oj/JOL_2012_277_R_TOC) ). [( 10 )](#ntc10-L_2018285EN.01009701-E0010) Case T-348/05. [( 11 )](#ntc11-L_2018285EN.01009701-E0011) Case T-348/05 INTP. [( 12 )](#ntc12-L_2018285EN.01009701-E0012) Council Regulation (EC) No 989/2009 of 19 October 2009 amending Regulation (EC) No 661/2008, imposing a definitive anti-dumping duty on imports of ammonium nitrate originating in Russia ( [OJ L 278, 23.10.2009, p. 1](http://publications.europa.eu/resource/oj/JOL_2009_278_R_TOC) ). [( 13 )](#ntc13-L_2018285EN.01009701-E0013) Council Regulation (EC) No 1225/2009 of 30 No",
      "origin": [
        "direct"
      ],
      "full_text": "[( 9 )](#ntc9-L_2018285EN.01009701-E0009)\nCommission Decision 2012/629/EU of 10 October 2012 amending Decision 2008/577/EC accepting the undertakings offered in connection with the anti-dumping proceeding concerning imports of ammonium nitrate originating in Russia (\n[OJ L 277, 11.10.2012, p. 8](http://publications.europa.eu/resource/oj/JOL_2012_277_R_TOC)\n).\n[( 10 )](#ntc10-L_2018285EN.01009701-E0010)\nCase T-348/05.\n[( 11 )](#ntc11-L_2018285EN.01009701-E0011)\nCase T-348/05 INTP.\n[( 12 )](#ntc12-L_2018285EN.01009701-E0012)\nCouncil Regulation (EC) No 989/2009 of 19 October 2009 amending Regulation (EC) No 661/2008, imposing a definitive anti-dumping duty on imports of ammonium nitrate originating in Russia (\n[OJ L 278, 23.10.2009, p. 1](http://publications.europa.eu/resource/oj/JOL_2009_278_R_TOC)\n).\n[( 13 )](#ntc13-L_2018285EN.01009701-E0013)\nCouncil Regulation (EC) No 1225/2009 of 30 November 2009 on protection against dumped imports from countries not members of the European Community (\n[OJ L 343, 22.12.2009, p. 51](http://publications.europa.eu/resource/oj/JOL_2009_343_R_TOC)\n).\n[( 14 )](#ntc14-L_2018285EN.01009701-E0014)\nCommission Implementing Regulation (EU) No 999/2014 of 23 September 2014 imposing a definitive anti-dumping duty on imports of ammonium nitrate originating in Russia (\n[OJ L 280, 24.9.2014, p. 19](http://publications.europa.eu/resource/oj/JOL_2014_280_R_TOC)\n).\n[( 15 )](#ntc15-L_2018285EN.01009701-E0015)\nCommission Implementing Regulation (EU) 2016/415 of 21 March 2016 withdrawing the acceptance of the undertaking for two exporting producers and repealing Decision 2008/577/EC accepting an undertaking offered in connection with the anti-dumping proceeding concerning imports of ammonium nitrate originating in Russia (\n[OJ L 75, 22.3.2016, p. 10](http://publications.europa.eu/resource/oj/JOL_2016_075_R_TOC)\n).\n[( 16 )](#ntc16-L_2018285EN.01009701-E0016)\nNotice of initiation of a partial interim review of the anti-dumping measures applicable to imports of ammonium nitrate originating in Russia (\n[OJ C 271, 17.8.2017, p. 9](http://publications.europa.eu/resource/oj/JOC_2017_271_R_TOC)\n).",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2019247EN.01000101",
      "chunk_id": "chunk_182",
      "excerpt": "In order for the thyroid gland to synthesise thyroid hormones to support normal metamorphosis, sufficient iodide should to be available to the larvae through a combination of aqueous and dietary sources. Currently, there are no empirically derived guidelines for minimum iodide concentrations in either food or water to ensure proper development. However, iodide availability may affect the responsiveness of the thyroid system to thyroid active agents and is known to modulate the basal activity of the thyroid gland which deserves attention when interpreting the results from thyroid histopathology. Based on previous work, successful performance of the assay has been demonstrated when dilution water iodide (I - Exposure system 18. The test was developed using a flow-through diluter system. The system components should have water-contact components of glass, stainless steel, and/or other chemi",
      "origin": [
        "direct"
      ],
      "full_text": "In order for the thyroid gland to synthesise thyroid hormones to support normal metamorphosis, sufficient iodide should to be available to the larvae through a combination of aqueous and dietary sources. Currently, there are no empirically derived guidelines for minimum iodide concentrations in either food or water to ensure proper development. However, iodide availability may affect the responsiveness of the thyroid system to thyroid active agents and is known to modulate the basal activity of the thyroid gland which deserves attention when interpreting the results from thyroid histopathology. Based on previous work, successful performance of the assay has been demonstrated when dilution water iodide (I - Exposure system 18. The test was developed using a flow-through diluter system. The system components should have water-contact components of glass, stainless steel, and/or other chemically inert materials. Exposure tanks should be glass or stainless steel aquaria and tank usable volume should be between 4,0 and 10,0 l (minimum water depth of 10 to 15 cm). The system should be capable of supporting all exposure concentrations, a control, and a solvent control, if necessary, with four replicates per treatment and eight in the controls. The flow rate to each tank should be constant in consideration of both the maintenance of biological conditions and chemical exposure. It is recommended that flow rates should be appropriate ( e.g etc Chemical delivery: preparation of test solutions 19. To make test solutions in the exposure system, stock solution of the test chemical should be dosed into the exposure system by an appropriate pump or other apparatus. The flow rate of the stock solution should be calibrated in accordance with analytical confirmation of the test solutions before the initiation of exposure, and checked volumetrically periodically during the test. The test solution in each chamber should be renewed at a minimum of 5 volume renewals/day. 20. The method used to introduce the test chemical to the system can vary depending on its physicochemical properties. Therefore, prior to the test, baseline information about the chemical that is relevant to determining its testability should be obtained. Useful information about test chemical-specific properties include the structural formula, molecular weight, purity, stability in water and light, pK a ow e.g 21. Test solutions of the chosen concentrations are prepared by dilution of a stock solution. The stock solution should preferably be prepared by simply mixing or agitating the test chemical in dilution water by mechanical means (e.g. stirring and/or ultrasonication). Saturation columns/systems or passive dosing methods (20) can be used for achieving a suitably concentrated stock solution. The preference is to use a co-solvent-free test system; however, different test chemicals will possess varied physicochemical properties that will likely require different approaches for preparation of chemical exposure water. All efforts should be made to avoid solvents or carriers because: (1) certain solvents themselves may result in toxicity and/or undesirable or unexpected responses, (2) testing chemicals above their water solubility (as can frequently occur through the use of solvents) can result in inaccurate determinations of effective concentrations, (3) the use of solvents in longer-term tests can result in a significant degree of \"biofilming\" associated with microbial activity which may impact environmental conditions as well as the ability to maintain exposure concentrations and (4) the absence of historical data that demonstrate that the solvent does not influence the outcome of the study, use of solvents requires a solvent control treatment which has significant animal welfare implications as additional animals are required to conduct the test. For difficult to test chemicals, a solvent may be employed as a last resort, and the OECD Guidance Document on Aquatic Toxicity Testing of Difficult Substances and Mixtures should be consulted (21) to determine the best method. The choice of solvent will be determined by the chemical properties of the test chemical and the availability of historical control data on the solvent. In the absence of historical data, the suitability of a solvent should be determined prior to conducting the definitive study. In the event that use of a solvent is unavoidable, and microbial activity (biofilming) occurs, recommend recording/reporting of the biofilming per tank (at least weekly) throughout the test. Ideally, the solvent concentration should be kept constant in the solvent control and all test treatments. If the concentration of solvent is not kept constant, the highest concentration of solvent in the test treatment should be used in the solvent control. In cases where a solvent carrier is used, maximum solvent concentrations should not exceed 100 μl/l or 100 mg/l (21), and it is recommended to keep solvent concentration as low as possible ( e.g Test animals Test species 22. The test species is X. laevis Adult care and breeding 23. Appropriate care and breeding of X. laevis X. laevis TEST DESIGN Test concentrations 24. It is recommended to use a minimum of four chemical concentrations and appropriate controls (including solvent controls, if necessary). Generally, a concentration separation (spacing factor) not exceeding 3.2 is recommended. 25.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2019247EN.01000101",
      "chunk_id": "chunk_166",
      "excerpt": "All efforts should be made to avoid solvents or carriers because: (1) certain solvents themselves may result in toxicity and/or undesirable or unexpected responses, (2) testing chemicals above their water solubility (as can frequently occur through the use of solvents) can result in inaccurate determinations of effective concentrations, (3) the use of solvents in longer-term tests can result in a significant degree of \"bio-filming\" associated with microbial activity which may impact environmental conditions as well as the ability to maintain exposure concentrations and (4) in the absence of historical data that demonstrates that the solvent does not influence the outcome of the study, use of solvents requires a solvent control treatment which has animal welfare implications as additional animals are required to conduct the test. For difficult to test chemicals, a solvent may be employed ",
      "origin": [
        "direct"
      ],
      "full_text": "All efforts should be made to avoid solvents or carriers because: (1) certain solvents themselves may result in toxicity and/or undesirable or unexpected responses, (2) testing chemicals above their water solubility (as can frequently occur through the use of solvents) can result in inaccurate determinations of effective concentrations, (3) the use of solvents in longer-term tests can result in a significant degree of \"bio-filming\" associated with microbial activity which may impact environmental conditions as well as the ability to maintain exposure concentrations and (4) in the absence of historical data that demonstrates that the solvent does not influence the outcome of the study, use of solvents requires a solvent control treatment which has animal welfare implications as additional animals are required to conduct the test. For difficult to test chemicals, a solvent may be employed as a last resort, and the OECD Guidance Document 23 on Aquatic Toxicity Testing of Difficult Substances and Mixtures (15) should be consulted to determine the best method. The choice of solvent will be determined by the chemical properties of the test chemical and the availability of historical data on use of the solvent. If solvent carriers are used, appropriate solvent controls should be evaluated in addition to non-solvent (negative) controls (dilution water only). In the event that use of a solvent is unavoidable, and microbial activity (bio-filming) occurs, recommend recording/reporting of the bio-filming per tank (at least weekly) throughout the test. Ideally, the solvent concentration should be kept constant in the solvent control and all test treatments. If the concentration of solvent is not kept constant, the highest concentration of solvent in the test treatment should be used in the solvent control. In cases where solvent carrier is used, maximum solvent concentrations should not exceed 100 μl/l or 100 mg/l (15), and it is recommended to keep solvent concentration as low as possible ( e.g Test animals Selection and holding of fish 16. The test species is Japanese medaka Oryzias latipes Artemia 17. As long as appropriate husbandry practices are followed, no specific culturing protocol is required. For example, medaka can be reared in 2 l tanks with 240 larval fish per tank until 4 wpf, then they can be reared in 2 l tanks with 10 fish per tank until 8 wpf, at which time, they transition to breeding pairs in 2 l tanks. Acclimation and selection of fish 18. Test fish should be selected from a single laboratory stock which has been acclimated for at least two weeks prior to the test under conditions of water quality and illumination similar to those used in the test (Note: This acclimation period is not an in situ 19. During the acclimation phase, mortalities in the culture fish should be recorded and the following criteria applied following a 48 h settling-down period: - Mortalities of greater than 10 % of the culture population in seven days preceding transfer to the test system: reject the entire batch; - Mortalities of between 5 % and 10 % of the population in the seven days preceding transfer to the test system: acclimation for seven additional days to the 2-week acclimation period; if more than 5 % mortality during the second seven days, reject the entire batch; - Mortalities of less than 5 % of the population in the seven days preceding transfer to the test system: accept the batch. 20. Fish should not receive treatment for disease in the two-week acclimation period preceding the test and during the exposure period, and disease treatment should be completely avoided if possible. Fish with clinical signs of disease should not be used in the study. A record of observations and any prophylactic and therapeutic disease treatments during the culture period preceding the test should be maintained. 21. The exposure phase should be started with sexually dimorphic, genetically sexed adult fish from a laboratory supply of reproductively mature animals cultured at 25 ± 2 °C. The fish should be identified as proven breeders (i.e. having produced viable offspring) during the week preceding exposure. For the whole group of fish used in the test, the range in individual weights by sex at the start of the test should be kept within ± 20 % of the arithmetic mean weight of the same sex. A subsample of fish should be weighed before the test to estimate the mean weight. The fish selected should be at least 12 wpf, being a weight ≥ 300 mg for females and ≥ 250 mg for males. TEST DESIGN Test concentrations 22. It is recommended to use five chemical concentrations plus control(s).",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2016054EN.01000101",
      "chunk_id": "chunk_107",
      "excerpt": "The following equipment and supplies are needed for the conduct of this assay: (a) Exposure system (see description below); (b) Glass or stainless steel aquaria (see description below); (c) Breeding tanks; (d) Temperature controlling apparatus (e.g., heaters or coolers (adjustable to 22° ± 1 °C)); (e) Thermometer; (f) Binocular dissection microscope; (g) Digital camera with at least 4 megapixel resolution and micro function; (h) Image digitising software; (i) Petri dish (e.g. 100 × 15 mm) or transparent plastic chamber of comparable size; (j) Analytical balance capable of measuring to 3 decimal places (mg); (k) Dissolved oxygen meter; (l) pH meter; (m) Light intensity meter capable of measuring in lux units; (n) Miscellaneous laboratory glassware and tools; (o) Adjustable pipettes (10 to 5 000 μl) or assorted pipettes of equivalent sizes; (p) Test chemical in sufficient quantities to con",
      "origin": [
        "direct"
      ],
      "full_text": "The following equipment and supplies are needed for the conduct of this assay: (a) Exposure system (see description below); (b) Glass or stainless steel aquaria (see description below); (c) Breeding tanks; (d) Temperature controlling apparatus (e.g., heaters or coolers (adjustable to 22° ± 1 °C)); (e) Thermometer; (f) Binocular dissection microscope; (g) Digital camera with at least 4 megapixel resolution and micro function; (h) Image digitising software; (i) Petri dish (e.g. 100 × 15 mm) or transparent plastic chamber of comparable size; (j) Analytical balance capable of measuring to 3 decimal places (mg); (k) Dissolved oxygen meter; (l) pH meter; (m) Light intensity meter capable of measuring in lux units; (n) Miscellaneous laboratory glassware and tools; (o) Adjustable pipettes (10 to 5 000 μl) or assorted pipettes of equivalent sizes; (p) Test chemical in sufficient quantities to conduct the study, preferably of one lot; (q) Analytical instrumentation appropriate for the chemical on test or contracted analytical services. Chemical Testability 6. The AMA is based upon an aqueous exposure protocol whereby test chemical is introduced into the test chambers via a flow-through system. Flow-through methods however, introduce constraints on the types of chemicals that can be tested, as determined by the physicochemical properties of the chemical. Therefore, prior to using this protocol, baseline information about the chemical should be obtained that is relevant to determining the testability, and the OECD Guidance Document on Aquatic Toxicity Testing of Difficult Substances and Mixtures (4) should be consulted. Characteristics which indicate that the chemical may be difficult to test in aquatic systems include: high octanol water partitioning coefficients (log K ow Exposure System 7. A flow-through diluter system is preferred, when possible, over a static renewal system. If physical and/or chemical properties of any of the test chemicals are not amenable to a flow-through diluter system, then an alternative exposure system (e.g., static-renewal) can be employed. The system components should have water-contact components of glass, stainless steel, and/or Polytetrafluoroethylene. However, suitable plastics can be utilised if they do not compromise the study. Exposure tanks should be glass or stainless steel aquaria, equipped with standpipes that result in an approximate tank volume between 4,0 and 10,0 l and minimum water depth of 10 to 15 cm. The system should be capable of supporting all exposure concentrations and a control, with four replicates per treatment. The flow rate to each tank should be constant in consideration of both the maintenance of biological conditions and chemical exposure (e.g. 25 ml/min). The treatment tanks should be randomly assigned to a position in the exposure system in order to reduce potential positional effects, including slight variations in temperature, light intensity, etc. Fluorescent lighting should be used to provide a photoperiod of 12 hr light: 12 hr dark at an intensity that ranges from 600 to 2 000 lux (lumen/m 2 Water quality 8. Any water that is locally available (e.g. springwater or charcoal-filtered tap water) and permits normal growth and development of X. laevis Xenopus Iodide Concentration in Test Water 9. In order for the thyroid gland to synthesise TH, sufficient iodide needs to be available to the larvae through a combination of aqueous and dietary sources. Currently, there are no empirically derived guidelines for minimal iodide concentrations. However, iodide availability may affect the responsiveness of the thyroid system to thyroid active agents and is known to modulate the basal activity of the thyroid gland, an aspect that deserves attention when interpreting the results from thyroid histopathology. Therefore, measured aqueous iodide concentrations from the test water should be reported. Based on the available data from the validation studies, the protocol has been demonstrated to work well when test water iodide (I - Holding of animals Adult Care and Breeding 10. Adult care and breeding is conducted in accordance with standard guidelines and the reader is directed to the standard guide for performing the Frog Embryo Teratogenesis Assay (FETAX) (6) for more detailed information. Such standard guidelines provide an example of appropriate care and breeding methods, but strict adherence is not required. To induce breeding, pairs (3-5) of adult females and males are injected with human chorionic gonadotropin (hCG). Female and male specimens are injected with approximately 800 IU-1 000 IU and 600 IU-800 IU, respectively, of hCG dissolved in 0,6-0,9 % saline solution.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2016054EN.01000101",
      "chunk_id": "chunk_92",
      "excerpt": "Saturation columns (solubility columns) can be used for achieving a suitable concentrated stock solution. The use of a solvent carrier is not recommended. However, in case a solvent is necessary, a solvent control should be run in parallel, at the same solvent concentration as the chemical treatments. For difficult test chemicals, a solvent may be technically the best solution; the OECD Guidance Document on aquatic toxicity testing of difficult substances and mixtures should be consulted (22). The choice of solvent will be determined by the chemical properties of the chemical. The OECD Guidance Document recommends a maximum of 100 μl/l, which should be observed. However a recent review (23) highlighted additional concerns when using solvents for endocrine activity testing. Therefore it is recommended that the solvent concentration, if necessary, is minimised wherever technically feasible",
      "origin": [
        "direct"
      ],
      "full_text": "Saturation columns (solubility columns) can be used for achieving a suitable concentrated stock solution. The use of a solvent carrier is not recommended. However, in case a solvent is necessary, a solvent control should be run in parallel, at the same solvent concentration as the chemical treatments. For difficult test chemicals, a solvent may be technically the best solution; the OECD Guidance Document on aquatic toxicity testing of difficult substances and mixtures should be consulted (22). The choice of solvent will be determined by the chemical properties of the chemical. The OECD Guidance Document recommends a maximum of 100 μl/l, which should be observed. However a recent review (23) highlighted additional concerns when using solvents for endocrine activity testing. Therefore it is recommended that the solvent concentration, if necessary, is minimised wherever technically feasible (dependent on the physical-chemical properties of the test chemical). 16. A flow-through test system will be used. Such a system continually dispenses and dilutes a stock solution of the test chemical (e.g. metering pump, proportional diluter, saturator system) in order to deliver a series of concentrations to the test chambers. The flow rates of stock solutions and dilution water should be checked at intervals, preferably daily, during the test and should not vary by more than 10 % throughout the test. Care should be taken to avoid the use of low-grade plastic tubing or other materials that may contain biologically active chemicals. When selecting the material for the flow-through system, possible adsorption of the test chemical to this material should be considered. Holding of fish 17. Test fish should be selected from a laboratory population, preferably from a single stock, which has been acclimated for at least two weeks prior to the test under conditions of water quality and illumination similar to those used in the test. It is important that the loading rate and stocking density (for definitions, see Appendix 1) be appropriate for the test species used (see Appendix 2). 18. Following a 48-hour settling-in period, mortalities are recorded and the following criteria applied: - mortalities of greater than 10 % of population in seven days: reject the entire batch; - mortalities of between 5 % and 10 % of population: acclimation for seven additional days; if more than 5 % mortality during second seven days, reject the entire batch; - mortalities of less than 5 % of population in seven days: accept the batch 19. Fish should not receive treatment for disease during the acclimation period, in the pre-exposure period, or during the exposure period. Pre-exposure and selection of fish 20. A one-week pre-exposure period is recommended, with animals placed in vessels similar to the actual test. Fish should be fed ad libitum TEST DESIGN 21. Three concentrations of the test chemical, one control (water) and, if needed, one solvent control are used. The data may be analysed in order to determine statistically significant differences between treatment and control responses. These analyses will inform whether further longer term testing for adverse effects (namely, survival, development, growth and reproduction) is required for the chemical, rather than for use in risk assessment (24). 22. For zebrafish and medaka, on day 21 of the experiment, males and females from each treatment level (5 males and 5 females in each of the two replicates) and from the control(s) are sampled for the measurement of vitellogenin and secondary sex characteristics, where applicable. For fathead minnow, on day 21 of exposure, males and females (2 males and 4 females in each of the four replicates) and from the control(s) are sampled for the measurement of vitellogenin and secondary sex characteristics. Selection of test concentrations 23. For the purposes of this test, the highest test concentration should be set by the maximum tolerated concentration (MTC) determined from a range finder or from other toxicity data, or 10 mg/l, or the maximum solubility in water, whichever is lowest. The MTC is defined as the highest test concentration of the chemical which results in less than 10 % mortality. Using this approach assumes that there are existing empirical acute toxicity data or other toxicity data from which the MTC can be estimated. Estimating the MTC can be inexact and typically requires some professional judgment. 24. Three test concentrations, spaced by a constant factor not exceeding 10, and a dilution-water control (and solvent control if necessary) are required. A range of spacing factors between 3,2 and 10 is recommended. PROCEDURE Selection and weighing of test fish 25. It is important to minimise variation in weight of the fish at the beginning of the assay. Suitable size ranges for the different species recommended for use in this test are given in Appendix 2.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2016054EN.01000101",
      "chunk_id": "chunk_138",
      "excerpt": "Non-turbulent flow through these small chambers may be induced by suspending them from an arm arranged to move the chamber up and down but always keeping the organisms submerged. 21. Where egg containers, grids or meshes have been used to hold eggs within the main test chamber, these restraints should be removed after the larvae hatch, except that meshes should be retained to prevent the escape of the fish. If there is a need to transfer the larvae, they should not be exposed to the air and nets should not be used to release fish from egg containers. The timing of this transfer varies with the species and transfer may not always be necessary. Water 22. Any water in which the test species shows control survival at least as good as in water described in Appendix 3 is suitable as test water. It should be of constant quality during the period of the test. In order to ensure that the dilution",
      "origin": [
        "direct"
      ],
      "full_text": "Non-turbulent flow through these small chambers may be induced by suspending them from an arm arranged to move the chamber up and down but always keeping the organisms submerged. 21. Where egg containers, grids or meshes have been used to hold eggs within the main test chamber, these restraints should be removed after the larvae hatch, except that meshes should be retained to prevent the escape of the fish. If there is a need to transfer the larvae, they should not be exposed to the air and nets should not be used to release fish from egg containers. The timing of this transfer varies with the species and transfer may not always be necessary. Water 22. Any water in which the test species shows control survival at least as good as in water described in Appendix 3 is suitable as test water. It should be of constant quality during the period of the test. In order to ensure that the dilution water will not unduly influence the test result (for example by reacting with the test chemical) or adversely affect the performance of the brood stock, samples should be taken at intervals for analysis. Total organic carbon, conductivity, pH and suspended solids should be measured, for example every three months where dilution water is known to be relatively constant in quality. Measurements of heavy metals (e.g. Cu, Pb, Zn, Hg, Cd, Ni), major anions and cations (e.g. Ca 2+ 2+ + + - 4 2- Test solutions 23. Flow-through system should be used if practically possible. For flow-through tests, a system that continually dispenses and dilutes a stock solution of the test chemical (e.g. metering pump, proportional diluter, and saturator system) is necessary to deliver a series of concentrations to the test chambers. The flow rates of stock solutions and dilution water should be checked at intervals during the test and should not vary by more than 10 % throughout the test. A flow rate equivalent to at least five test chamber volumes per 24 hours has been found suitable (1). Care should be taken to avoid the use of plastic tubing or other materials, some of which may contain biologically active chemicals or may adsorb the test chemical. 24. The stock solution should preferably be prepared without the use of solvents by simply mixing or agitating the test chemical in the dilution water by using mechanical means (e.g. stirring or ultrasonication). If the test chemical is difficult to dissolve in water, procedures described in the OECD Guidance Document on aquatic toxicity testing of difficult substances and mixtures should be followed (36). The use of solvents should be avoided but may be necessary in some cases in order to produce a suitably concentrated stock solution. Examples of suitable solvents are given in (36). 25. Semi-static test conditions should be avoided unless justification is provided on compelling reasons associated with the test chemical (e.g. stability, limited availability, high cost or hazard). For the semi-static technique, two different renewal procedures may be followed. Either new test solutions are prepared in clean chambers and surviving eggs and larvae gently transferred into the new chambers, or the test organisms are retained in the test chambers whilst a proportion (at least two thirds) of the test water is changed daily. PROCEDURE Conditions of Exposure Collection of eggs and duration 26. To avoid genetic bias, eggs are collected from a minimum of three breeding pairs or groups, mixed and randomly selected to initiate the test. For the three-spined stickleback, see the description of artificial fertilisation in Appendix 11. The test should start as soon as possible after the eggs have been fertilised, the embryos preferably being immersed in the test solutions before cleavage of the blastodisc commences, or as close as possible after this stage and no later than 12 h post fertilisation. The test should continue until sexual differentiation in the control group is completed (60 dph for Japanese medaka, the three-spined stickleback and zebrafish). Loading 27. The number of fertilised eggs at the start of the test should be at least 120 per concentration divided between a minimum of 4 replicates (square root allocation to control is accepted). The eggs should be randomly distributed (by using statistical tables for randomisation) among treatments. The loading rate (for definition, see Appendix 1) should be low enough in order that a dissolved oxygen concentration of at least 60 % of the ASV can be maintained without direct aeration of the chambers. For flow-through tests, a loading rate not exceeding 0,5 g/l per 24 hours, and not exceeding 5 g/l of solution at any time is recommended. No later than 28 days post fertilisation the number of fish per replicate should be redistributed, so that each replicate contains as equal a number of fish as possible. If exposure related mortality occurs, the number of replicates should be reduced appropriately so that fish density between treatment levels is kept as equal as possible.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    }
  ],
  "retrieved_tables": [
    {
      "document_id": "L_2021106EN.01000301",
      "table_id": "table_17",
      "row_ids": [
        0
      ],
      "headers": null,
      "rows": [
        [
          "‘9.1.1",
          "Short-term toxicity testing on fish When short-term fish toxicity data is required, the threshold approach (tiered strategy) should be applied. A long-term toxicity testing on fish in accordance with point 9.1.6.1 shall be considered if the substance is poorly water soluble, i.e. below 1 mg/L",
          "",
          "The study does not need to be conducted if:"
        ]
      ]
    },
    {
      "document_id": "L_2008139EN.01001001",
      "table_id": "table_1",
      "row_ids": [
        0
      ],
      "headers": [
        "No",
        "Einecs No",
        "CAS No",
        "Substance name",
        "Rapporteur",
        "Testing/information requirements",
        "Time limit from the date of entry into force of this Regulation"
      ],
      "rows": [
        [
          "1",
          "247-759-6",
          "26523-78-4",
          "Tris (nonylphenyl) phosphite",
          "FR",
          "Acute toxicity test with Daphnia magna Information on structure of TNPP Information on water solubility Log K ow Hydrolysis test Sediment test with Lumbriculus variegatus Monitoring data for sites with PEC/PNEC > 1 Long-term Daphnia test depending on outcome of acute Daphnia test",
          "4 months"
        ]
      ]
    },
    {
      "document_id": "L_2021106EN.01000301",
      "table_id": "table_18",
      "row_ids": [
        0
      ],
      "headers": null,
      "rows": [
        [
          "‘9.1.6.1",
          "Long term toxicity testing on fish The information shall be provided from long-term toxicity testing on fish in which early life-stages (eggs, larvae or juveniles) are exposed",
          "ADS’",
          ""
        ]
      ]
    },
    {
      "document_id": "L_2008139EN.01001001",
      "table_id": "table_1",
      "row_ids": [
        11
      ],
      "headers": [
        "No",
        "Einecs No",
        "CAS No",
        "Substance name",
        "Rapporteur",
        "Testing/information requirements",
        "Time limit from the date of entry into force of this Regulation"
      ],
      "rows": [
        [
          "8",
          "202-679-0",
          "98-54-4",
          "4-Tert-butylphenol",
          "NO",
          "Local exposure information on the releases from two processing sites (5 and 6) into wastewater treatment plants and aquatic compartment (freshwater and marine)",
          "4 months"
        ]
      ]
    },
    {
      "document_id": "L_202400365EN",
      "table_id": "table_7",
      "row_ids": [
        2
      ],
      "headers": [
        "",
        "Column 1 Standard information and testing",
        "Column 2 Specific rules for adaptation of the standard information and testing"
      ],
      "rows": [
        [
          "7.2.",
          "Repeated dose toxicity:",
          ""
        ]
      ]
    }
  ],
  "retrieval_call_status": "success",
  "review": {
    "case_id": "global_natural_003",
    "decision": "revise",
    "final_question": "Under the aquatic-toxicity testing procedure described in the source, what information must the test report contain?",
    "verified_reference_answer": "The report must cover four groups: (1) the test substance—physical nature/relevant physicochemical properties plus chemical identification, purity and, where appropriate, the analytical quantification method; (2) the test species—scientific name and, where relevant, strain, size, supplier and pretreatment; (3) test conditions—procedure, design, stock-solution preparation/renewal, any solubilising agent, nominal and measured concentrations and variability, dilution-water characteristics, within-vessel water quality, and feeding details; and (4) results—control validity/mortality, statistical methods and treatment, fish weights and growth rates, statistical results including LOEC/NOEC or ECx where possible, and unusual reactions/visible effects.",
    "supporting_quote": "The test report must include the following information: 2.3.1. Test substance: ... 2.3.2. Test species: ... 2.3.3. Test conditions: ... 2.3.4. Results:",
    "expected_source_keys": [
      "L_2008142EN.01000101 / chunk_319"
    ],
    "retrieval_label": "insufficient",
    "helpful_retrieved_source_keys": [],
    "scope_date_version_caveats": "Retrieved material concerns other aquatic/ecotoxicity procedures and does not supply this source's report checklist. Do not substitute related test methods.",
    "confidence": "high",
    "review_notes": "The draft reference was too skeletal because it omitted the Results category and most required checklist content. Revised reference supplied."
  },
  "reference_answer": "The report must cover four groups: (1) the test substance—physical nature/relevant physicochemical properties plus chemical identification, purity and, where appropriate, the analytical quantification method; (2) the test species—scientific name and, where relevant, strain, size, supplier and pretreatment; (3) test conditions—procedure, design, stock-solution preparation/renewal, any solubilising agent, nominal and measured concentrations and variability, dilution-water characteristics, within-vessel water quality, and feeding details; and (4) results—control validity/mortality, statistical methods and treatment, fish weights and growth rates, statistical results including LOEC/NOEC or ECx where possible, and unusual reactions/visible effects.",
  "label_origin": "ChatGPT AI-assisted adjudication",
  "quote_matches": [
    "ordered_source_fragments"
  ],
  "question_revision_pending": true,
  "expert_validated": false,
  "system_QA_outcome": null
}
```

## QA global_natural_004

```json
{
  "case_id": "global_natural_004",
  "category": "definition_scope",
  "question": "What level of free volatile acid is required for food preserved in vinegar or acetic acid to fall under heading 2001?",
  "proposed_reference_answer": "At least 0.5% free volatile acid by weight, expressed as acetic acid, is the stated requirement for the described heading-2001 products. This threshold alone does not prove every classification condition.",
  "reference_status": "AI_adjudicated",
  "system_answer": null,
  "score_eligible": false,
  "expected_chunks": [
    {
      "document_id": "L_2008291EN.01000101",
      "chunk_id": "chunk_112",
      "excerpt": "1. For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid. In addition, mushrooms of subheading 2001 90 50 should not have a salt content exceeding 2,5 % by weight. 2. 3. The products of subheadings 2008 20 to 2008 80 , 2008 92 and 2008 99 shall be considered as containing added sugar when the 'sugar content' thereof exceeds by weight the percentages given hereunder, according to the kind of fruit or edible part of plant concerned: - pineapples and grapes: 13 %, - other fruits, including mixtures of fruit, and other edible parts of plants: 9 %. 4. For the purposes of subheadings 2008 30 11 to 2008 30 39 , 2008 40 11 to 2008 40 39 , 2008 50 11 to 2008 50 59 , 2008 60 11 to 2008 60 39 , 2008 70 11 to 2008 70 59 , 2008 80 11 to 2008 80 39 , 2008 92 12 to 2008 92 38 and 2008 99 11 to 2008 99 40 , the following expressions shall have the meanings hereby assigned to them: - 'actual alcoholic strength by mass': t",
      "full_text": "1. For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid. In addition, mushrooms of subheading 2001 90 50 should not have a salt content exceeding 2,5 % by weight. 2. 3. The products of subheadings 2008 20 to 2008 80 , 2008 92 and 2008 99 shall be considered as containing added sugar when the 'sugar content' thereof exceeds by weight the percentages given hereunder, according to the kind of fruit or edible part of plant concerned: - pineapples and grapes: 13 %, - other fruits, including mixtures of fruit, and other edible parts of plants: 9 %. 4. For the purposes of subheadings 2008 30 11 to 2008 30 39 , 2008 40 11 to 2008 40 39 , 2008 50 11 to 2008 50 59 , 2008 60 11 to 2008 60 39 , 2008 70 11 to 2008 70 59 , 2008 80 11 to 2008 80 39 , 2008 92 12 to 2008 92 38 and 2008 99 11 to 2008 99 40 , the following expressions shall have the meanings hereby assigned to them: - 'actual alcoholic strength by mass': the number of kilograms of pure alcohol contained in 100 kg of the product, - '% mas': the symbol for alcoholic strength by mass. 5. The following shall be applied to the products as they are presented: (a) the added sugar content of products of heading 2009 corresponds to the 'sugar content' less the figures given hereunder, according to the kind of juice concerned: - lemon or tomato juice: 3, - grape juice: 15, - other fruit or vegetable juices, including mixtures of juices: 13. (b) the fruit juices with added sugar, of a Brix value not exceeding 67 and containing less than 50 % by weight of fruit juice lose their original character of fruit juices of heading 2009 . Item (b) shall not apply to concentrated natural fruit juices. Consequently, concentrated natural fruit juices are not excluded from heading 2009 . 6. For the purposes of subheadings 2009 69 51 and 2009 69 71 , 'concentrated grape juice (including grape must)' means grape juice (including grape must) for which the figure indicated by a refractometer (used in accordance with the method prescribed in the Annex to Regulation (EEC) No 558/93) at a temperature of 20 °C is not less than 50,9 %. 7.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    }
  ],
  "expected_tables": [],
  "retrieved_chunks": [
    {
      "document_id": "L_2019149EN.01000101",
      "chunk_id": "chunk_16",
      "excerpt": "- wines from Slovenia entitled to a protected designation of origin and described by the terms 'vrhunsko vino ZGP - jagodni izbor', 'vrhunsko vino ZGP - ledeno vino' or 'vrhunsko vino ZGP - suhi jagodni izbor', - wines originating in Canada entitled to the description 'Icewine', - wines from Croatia entitled to a protected designation of origin and described by the term 'vrhunsko vino KZP - izborna berba bobica', 'vrhunsko vino KZP - izborna berba prosušenih bobica' or 'vrhunsko vino KZP - ledeno vino'. 3. The lists of wines bearing a protected designation of origin or a protected geographical indication set out in points 2(c), (d) and (e) may be amended to include new wines or where the production conditions of the wines are amended or the designation of origin or geographical indication is changed. Member States shall send a request for derogation to the Commission in accordance with C",
      "origin": [
        "direct"
      ],
      "full_text": "- wines from Slovenia entitled to a protected designation of origin and described by the terms 'vrhunsko vino ZGP - jagodni izbor', 'vrhunsko vino ZGP - ledeno vino' or 'vrhunsko vino ZGP - suhi jagodni izbor', - wines originating in Canada entitled to the description 'Icewine', - wines from Croatia entitled to a protected designation of origin and described by the term 'vrhunsko vino KZP - izborna berba bobica', 'vrhunsko vino KZP - izborna berba prosušenih bobica' or 'vrhunsko vino KZP - ledeno vino'.\n3. The lists of wines bearing a protected designation of origin or a protected geographical indication set out in points 2(c), (d) and (e) may be amended to include new wines or where the production conditions of the wines are amended or the designation of origin or geographical indication is changed. Member States shall send a request for derogation to the Commission in accordance with Commission Delegated Regulation (EU) 2017/1183 and provide all the necessary technical information for the wines concerned, including their product specifications and the annual quantities produced. 4. In years when climatic conditions make this exceptionally necessary, Member States may authorise an increase of a maximum of 50 milligrams per litre in the maximum total sulphur dioxide levels of less than 300 milligrams per litre for wines produced in certain wine-growing areas within their territory. Member States shall notify those derogations within one month following the granting of the derogation to the Commission in accordance with Delegated Regulation (EU) 2017/1183 by specifying the year, the wine growing areas and the wines concerned and providing evidence indicating that the climatic conditions make the increase necessary. The Commission shall then publish the derogation on its website. 5. Member States may apply more restrictive provisions to wines produced within their territory.\nB. THE SULPHUR DIOXIDE CONTENT OF LIQUEUR WINES\nThe total sulphur dioxide content of liqueur wines, on their release to the market for direct human consumption, may not exceed:\n(a) 150 mg/l where the sugar content is less than 5 g/l; (b) 200 mg/l where the sugar content is not less than 5 g/l.\nC. THE SULPHUR DIOXIDE CONTENT OF SPARKLING WINES\n1. The total sulphur dioxide content of sparkling wines, on their release to the market for direct human consumption, may not exceed: (a) 185 mg/l for all categories of quality sparkling wine; and (b) 235 mg/l for other sparkling wines. 2. Where climate conditions make this necessary in certain wine-growing areas of the Union, the Member States concerned may authorise an increase of up to 40 mg/l in the maximum total sulphur dioxide content for the sparkling wines referred to in point 1(a) and (b) produced in their territory, provided that the wines covered by this authorisation are not sent outside the Member State in question.\nPART C\nTHE MAXIMUM VOLATILE ACID CONTENT OF WINES\n1. The volatile acid content may not exceed: (a) 18 milliequivalents per litre for partially fermented grape must; (b) 18 milliequivalents per litre for white and rosé wines; or (c) 20 milliequivalents per litre for red wines. 2. The levels referred to in point 1 shall apply: (a) to products from grapes harvested within the Union, at the production stage and at all stages of marketing; (b) to partially fermented grape must and wines originating in third countries, at all stages following their entry into the geographical territory of the Union. 3. Member States may grant derogations from the limits set out in point 1: Member States shall notify those derogations to the Commission in accordance with Delegated Regulation (EU) 2017/1183 and within one month following the date of granting the derogation. The Commission shall then make public the derogation on its website. (a) for certain wines bearing a protected designation of origin or a protected geographical indication: - where they have been aged for a period of at least two years, or - where they have been produced according to particular methods; (b) for wines with a total alcoholic strength by volume of at least 13 % vol.\nPART D\nLIMITS AND CONDITIONS FOR THE SWEETENING OF WINES",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2022282EN.01000101",
      "chunk_id": "chunk_34",
      "excerpt": "1. For the purposes of heading 2001, vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid. In addition, mushrooms of subheading 2001 90 50 should not have a salt content exceeding 2,5 % by weight. 2. 3. The products of subheadings 2008 20 to 2008 80, 2008 93, 2008 97 and 2008 99 are to be considered as containing added sugar when the 'sugar content' thereof exceeds by weight the percentages given hereunder, according to the kind of fruit or edible part of plant concerned: - pineapples and grapes: 13 %, - other fruits, including mixtures of fruit, and other edible parts of plants: 9 %. 4. For the purposes of subheadings 2008 30 11 to 2008 30 39, 2008 40 11 to 2008 40 39, 2008 50 11 to 2008 50 59, 2008 60 11 to 2008 60 39, 2008 70 11 to 2008 70",
      "origin": [
        "direct"
      ],
      "full_text": "1. For the purposes of heading 2001, vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid. In addition, mushrooms of subheading 2001 90 50 should not have a salt content exceeding 2,5 % by weight. 2. 3. The products of subheadings 2008 20 to 2008 80, 2008 93, 2008 97 and 2008 99 are to be considered as containing added sugar when the 'sugar content' thereof exceeds by weight the percentages given hereunder, according to the kind of fruit or edible part of plant concerned: - pineapples and grapes: 13 %, - other fruits, including mixtures of fruit, and other edible parts of plants: 9 %. 4. For the purposes of subheadings 2008 30 11 to 2008 30 39, 2008 40 11 to 2008 40 39, 2008 50 11 to 2008 50 59, 2008 60 11 to 2008 60 39, 2008 70 11 to 2008 70 59, 2008 80 11 to 2008 80 39, 2008 93 11 to 2008 93 29, 2008 97 12 to 2008 97 38 and 2008 99 11 to 2008 99 40, the following expressions have the meanings hereby assigned to them: - 'actual alcoholic strength by mass': the number of kilograms of pure alcohol contained in 100 kg of the product, - '% mas': the symbol for alcoholic strength by mass. 5. The following is to be applied to the products as they are presented: Item (b) does not apply to concentrated natural fruit juices. Consequently, concentrated natural fruit juices are not excluded from heading 2009. (a) the added sugar content of products of heading 2009 corresponds to the 'sugar content' less the figures given hereunder, according to the kind of juice concerned: - lemon or tomato juice: 3, - grape juice: 15, - other fruit or vegetable juices, including mixtures of juices: 13. (b) the fruit juices with added sugar, of a Brix value not exceeding 67 and containing less than 50 % by weight of fruit juice lose their original character of fruit juices of heading 2009. 6. For the purposes of subheadings 2009 69 51 and 2009 69 71, 'concentrated grape juice (including grape must)' means grape juice (including grape must) for which the figure indicated by a refractometer (used in accordance with the method prescribed in the Annex to Commission Implementing Regulation (EU) No 974/2014 ( 89 7.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_202402522EN",
      "chunk_id": "chunk_34",
      "excerpt": "1. For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid. In addition, mushrooms of subheading 2001 90 50 should not have a salt content exceeding 2,5 % by weight. 2. 3. The products of subheadings 2008 20 to 2008 80 , 2008 93 , 2008 97 and 2008 99 are to be considered as containing added sugar when the 'sugar content' thereof exceeds by weight the percentages given hereunder, according to the kind of fruit or edible part of plant concerned: - pineapples and grapes: 13 %, - other fruits, including mixtures of fruit, and other edible parts of plants: 9 %. 4. For the purposes of subheadings 2008 30 11 to 2008 30 39 , 2008 40 11 to 2008 40 39 , 2008 50 11 to 2008 50 59 , 2008 60 11 to 2008 60 39 , 2008 70 11 to ",
      "origin": [
        "direct"
      ],
      "full_text": "1. For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid. In addition, mushrooms of subheading 2001 90 50 should not have a salt content exceeding 2,5 % by weight. 2. 3. The products of subheadings 2008 20 to 2008 80 , 2008 93 , 2008 97 and 2008 99 are to be considered as containing added sugar when the 'sugar content' thereof exceeds by weight the percentages given hereunder, according to the kind of fruit or edible part of plant concerned: - pineapples and grapes: 13 %, - other fruits, including mixtures of fruit, and other edible parts of plants: 9 %. 4. For the purposes of subheadings 2008 30 11 to 2008 30 39 , 2008 40 11 to 2008 40 39 , 2008 50 11 to 2008 50 59 , 2008 60 11 to 2008 60 39 , 2008 70 11 to 2008 70 59 , 2008 80 11 to 2008 80 39 , 2008 93 11 to 2008 93 29 , 2008 97 12 to 2008 97 38 and 2008 99 11 to 2008 99 40 , the following expressions have the meanings hereby assigned to them: - 'actual alcoholic strength by mass': the number of kilograms of pure alcohol contained in 100 kg of the product, - '% mas': the symbol for alcoholic strength by mass. 5. The following is to be applied to the products as they are presented: Item (b) does not apply to concentrated natural fruit juices. Consequently, concentrated natural fruit juices are not excluded from heading 2009 . (a) the added sugar content of products of heading 2009 corresponds to the 'sugar content' less the figures given hereunder, according to the kind of juice concerned: - lemon or tomato juice: 3, - grape juice: 15, - other fruit or vegetable juices, including mixtures of juices: 13. (b) the fruit juices with added sugar, of a Brix value not exceeding 67 and containing less than 50 % by weight of fruit juice lose their original character of fruit juices of heading 2009 . 6. For the purposes of subheadings 2009 69 51 and 2009 69 71 , 'concentrated grape juice (including grape must)' means grape juice (including grape must) for which the figure indicated by a refractometer (used in accordance with the method prescribed in the Annex to Implementing Regulation (EU) No 974/2014 ( 89 7.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2018273EN.01000101",
      "chunk_id": "chunk_121",
      "excerpt": "1. For the purposes of heading 2001, vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid. In addition, mushrooms of subheading 2001 90 50 should not have a salt content exceeding 2,5 % by weight. 2. 3. The products of subheadings 2008 20 to 2008 80, 2008 93, 2008 97 and 2008 99 are to be considered as containing added sugar when the 'sugar content' thereof exceeds by weight the percentages given hereunder, according to the kind of fruit or edible part of plant concerned: - pineapples and grapes: 13 %, - other fruits, including mixtures of fruit, and other edible parts of plants: 9 %. 4. For the purposes of subheadings 2008 30 11 to 2008 30 39, 2008 40 11 to 2008 40 39, 2008 50 11 to 2008 50 59, 2008 60 11 to 2008 60 39, 2008 70 11 to 2008 70",
      "origin": [
        "direct"
      ],
      "full_text": "1. For the purposes of heading 2001, vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid. In addition, mushrooms of subheading 2001 90 50 should not have a salt content exceeding 2,5 % by weight. 2. 3. The products of subheadings 2008 20 to 2008 80, 2008 93, 2008 97 and 2008 99 are to be considered as containing added sugar when the 'sugar content' thereof exceeds by weight the percentages given hereunder, according to the kind of fruit or edible part of plant concerned: - pineapples and grapes: 13 %, - other fruits, including mixtures of fruit, and other edible parts of plants: 9 %. 4. For the purposes of subheadings 2008 30 11 to 2008 30 39, 2008 40 11 to 2008 40 39, 2008 50 11 to 2008 50 59, 2008 60 11 to 2008 60 39, 2008 70 11 to 2008 70 59, 2008 80 11 to 2008 80 39, 2008 93 11 to 2008 93 29, 2008 97 12 to 2008 97 38 and 2008 99 11 to 2008 99 40, the following expressions have the meanings hereby assigned to them: - 'actual alcoholic strength by mass': the number of kilograms of pure alcohol contained in 100 kg of the product, - '% mas': the symbol for alcoholic strength by mass. 5. The following is to be applied to the products as they are presented: Item (b) does not apply to concentrated natural fruit juices. Consequently, concentrated natural fruit juices are not excluded from heading 2009. (a) the added sugar content of products of heading 2009 corresponds to the 'sugar content' less the figures given hereunder, according to the kind of juice concerned: - lemon or tomato juice: 3, - grape juice: 15, - other fruit or vegetable juices, including mixtures of juices: 13. (b) the fruit juices with added sugar, of a Brix value not exceeding 67 and containing less than 50 % by weight of fruit juice lose their original character of fruit juices of heading 2009. 6. For the purposes of subheadings 2009 69 51 and 2009 69 71, 'concentrated grape juice (including grape must)' means grape juice (including grape must) for which the figure indicated by a refractometer (used in accordance with the method prescribed in the Annex to Commission Implementing Regulation (EU) No 974/2014 ( 51 7.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_202501926EN",
      "chunk_id": "chunk_34",
      "excerpt": "1. For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid. In addition, mushrooms of subheading 2001 90 50 should not have a salt content exceeding 2,5 % by weight. 2. 3. The products of subheadings 2008 20 to 2008 80 , 2008 93 , 2008 97 and 2008 99 are to be considered as containing added sugar when the 'sugar content' thereof exceeds by weight the percentages given hereunder, according to the kind of fruit or edible part of plant concerned: - pineapples and grapes: 13 %, - other fruits, including mixtures of fruit, and other edible parts of plants: 9 %. 4. For the purposes of subheadings 2008 30 11 to 2008 30 39 , 2008 40 11 to 2008 40 39 , 2008 50 11 to 2008 50 59 , 2008 60 11 to 2008 60 39 , 2008 70 11 to ",
      "origin": [
        "direct"
      ],
      "full_text": "1. For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid. In addition, mushrooms of subheading 2001 90 50 should not have a salt content exceeding 2,5 % by weight. 2. 3. The products of subheadings 2008 20 to 2008 80 , 2008 93 , 2008 97 and 2008 99 are to be considered as containing added sugar when the 'sugar content' thereof exceeds by weight the percentages given hereunder, according to the kind of fruit or edible part of plant concerned: - pineapples and grapes: 13 %, - other fruits, including mixtures of fruit, and other edible parts of plants: 9 %. 4. For the purposes of subheadings 2008 30 11 to 2008 30 39 , 2008 40 11 to 2008 40 39 , 2008 50 11 to 2008 50 59 , 2008 60 11 to 2008 60 39 , 2008 70 11 to 2008 70 59 , 2008 80 11 to 2008 80 39 , 2008 93 11 to 2008 93 29 , 2008 97 12 to 2008 97 38 and 2008 99 11 to 2008 99 40 , the following expressions have the meanings hereby assigned to them: - 'actual alcoholic strength by mass': the number of kilograms of pure alcohol contained in 100 kg of the product, - '% mas': the symbol for alcoholic strength by mass. 5. The following is to be applied to the products as they are presented: Item (b) does not apply to concentrated natural fruit juices. Consequently, concentrated natural fruit juices are not excluded from heading 2009 . (a) the added sugar content of products of heading 2009 corresponds to the 'sugar content' less the figures given hereunder, according to the kind of juice concerned: - lemon or tomato juice: 3, - grape juice: 15, - other fruit or vegetable juices, including mixtures of juices: 13. (b) the fruit juices with added sugar, of a Brix value not exceeding 67 and containing less than 50 % by weight of fruit juice lose their original character of fruit juices of heading 2009 . 6. For the purposes of subheadings 2009 69 51 and 2009 69 71 , 'concentrated grape juice (including grape must)' means grape juice (including grape must) for which the figure indicated by a refractometer (used in accordance with the method prescribed in the Annex to Implementing Regulation (EU) No 974/2014 ( 89 7.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2008291EN.01000101",
      "chunk_id": "chunk_112",
      "excerpt": "1. For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid. In addition, mushrooms of subheading 2001 90 50 should not have a salt content exceeding 2,5 % by weight. 2. 3. The products of subheadings 2008 20 to 2008 80 , 2008 92 and 2008 99 shall be considered as containing added sugar when the 'sugar content' thereof exceeds by weight the percentages given hereunder, according to the kind of fruit or edible part of plant concerned: - pineapples and grapes: 13 %, - other fruits, including mixtures of fruit, and other edible parts of plants: 9 %. 4. For the purposes of subheadings 2008 30 11 to 2008 30 39 , 2008 40 11 to 2008 40 39 , 2008 50 11 to 2008 50 59 , 2008 60 11 to 2008 60 39 , 2008 70 11 to 2008 70 59 ",
      "origin": [
        "direct"
      ],
      "full_text": "1. For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid. In addition, mushrooms of subheading 2001 90 50 should not have a salt content exceeding 2,5 % by weight. 2. 3. The products of subheadings 2008 20 to 2008 80 , 2008 92 and 2008 99 shall be considered as containing added sugar when the 'sugar content' thereof exceeds by weight the percentages given hereunder, according to the kind of fruit or edible part of plant concerned: - pineapples and grapes: 13 %, - other fruits, including mixtures of fruit, and other edible parts of plants: 9 %. 4. For the purposes of subheadings 2008 30 11 to 2008 30 39 , 2008 40 11 to 2008 40 39 , 2008 50 11 to 2008 50 59 , 2008 60 11 to 2008 60 39 , 2008 70 11 to 2008 70 59 , 2008 80 11 to 2008 80 39 , 2008 92 12 to 2008 92 38 and 2008 99 11 to 2008 99 40 , the following expressions shall have the meanings hereby assigned to them: - 'actual alcoholic strength by mass': the number of kilograms of pure alcohol contained in 100 kg of the product, - '% mas': the symbol for alcoholic strength by mass. 5. The following shall be applied to the products as they are presented: (a) the added sugar content of products of heading 2009 corresponds to the 'sugar content' less the figures given hereunder, according to the kind of juice concerned: - lemon or tomato juice: 3, - grape juice: 15, - other fruit or vegetable juices, including mixtures of juices: 13. (b) the fruit juices with added sugar, of a Brix value not exceeding 67 and containing less than 50 % by weight of fruit juice lose their original character of fruit juices of heading 2009 . Item (b) shall not apply to concentrated natural fruit juices. Consequently, concentrated natural fruit juices are not excluded from heading 2009 . 6. For the purposes of subheadings 2009 69 51 and 2009 69 71 , 'concentrated grape juice (including grape must)' means grape juice (including grape must) for which the figure indicated by a refractometer (used in accordance with the method prescribed in the Annex to Regulation (EEC) No 558/93) at a temperature of 20 °C is not less than 50,9 %. 7.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2019280EN.01000101",
      "chunk_id": "chunk_122",
      "excerpt": "1. For the purposes of heading 2001, vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid. In addition, mushrooms of subheading 2001 90 50 should not have a salt content exceeding 2,5 % by weight. 2. 3. The products of subheadings 2008 20 to 2008 80, 2008 93, 2008 97 and 2008 99 are to be considered as containing added sugar when the 'sugar content'thereof exceeds by weight the percentages given hereunder, according to the kind of fruit or edible part of plant concerned: - pineapples and grapes: 13 %, - other fruits, including mixtures of fruit, and other edible parts of plants: 9 %. 4. For the purposes of subheadings 2008 30 11 to 2008 30 39, 2008 40 11 to 2008 40 39, 2008 50 11 to 2008 50 59, 2008 60 11 to 2008 60 39, 2008 70 11 to 2008 70 ",
      "origin": [
        "direct"
      ],
      "full_text": "1. For the purposes of heading 2001, vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid. In addition, mushrooms of subheading 2001 90 50 should not have a salt content exceeding 2,5 % by weight. 2. 3. The products of subheadings 2008 20 to 2008 80, 2008 93, 2008 97 and 2008 99 are to be considered as containing added sugar when the 'sugar content'thereof exceeds by weight the percentages given hereunder, according to the kind of fruit or edible part of plant concerned: - pineapples and grapes: 13 %, - other fruits, including mixtures of fruit, and other edible parts of plants: 9 %. 4. For the purposes of subheadings 2008 30 11 to 2008 30 39, 2008 40 11 to 2008 40 39, 2008 50 11 to 2008 50 59, 2008 60 11 to 2008 60 39, 2008 70 11 to 2008 70 59, 2008 80 11 to 2008 80 39, 2008 93 11 to 2008 93 29, 2008 97 12 to 2008 97 38 and 2008 99 11 to 2008 99 40, the following expressions have the meanings hereby assigned to them: - 'actual alcoholic strength by mass': the number of kilograms of pure alcohol contained in 100 kg of the product, - '% mas': the symbol for alcoholic strength by mass. 5. The following is to be applied to the products as they are presented: Item (b) does not apply to concentrated natural fruit juices. Consequently, concentrated natural fruit juices are not excluded from heading 2009. (a) the added sugar content of products of heading 2009 corresponds to the 'sugar content'less the figures given hereunder, according to the kind of juice concerned: - lemon or tomato juice: 3, - grape juice: 15, - other fruit or vegetable juices, including mixtures of juices: 13. (b) the fruit juices with added sugar, of a Brix value not exceeding 67 and containing less than 50 % by weight of fruit juice lose their original character of fruit juices of heading 2009. 6. For the purposes of subheadings 2009 69 51 and 2009 69 71, 'concentrated grape juice (including grape must)'means grape juice (including grape must) for which the figure indicated by a refractometer (used in accordance with the method prescribed in the Annex to Commission Implementing Regulation (EU) No 974/2014 ( 51 7.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2012304EN.01000101",
      "chunk_id": "chunk_120",
      "excerpt": "1. For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid. In addition, mushrooms of subheading 2001 90 50 should not have a salt content exceeding 2,5 % by weight. 2. 3. The products of subheadings 2008 20 to 2008 80 , 2008 93 , 2008 97 and 2008 99 are to be considered as containing added sugar when the 'sugar content' thereof exceeds by weight the percentages given hereunder, according to the kind of fruit or edible part of plant concerned: - pineapples and grapes: 13 %, - other fruits, including mixtures of fruit, and other edible parts of plants: 9 %. 4. For the purposes of subheadings 2008 30 11 to 2008 30 39 , 2008 40 11 to 2008 40 39 , 2008 50 11 to 2008 50 59 , 2008 60 11 to 2008 60 39 , 2008 70 11 to ",
      "origin": [
        "direct"
      ],
      "full_text": "1. For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid. In addition, mushrooms of subheading 2001 90 50 should not have a salt content exceeding 2,5 % by weight. 2. 3. The products of subheadings 2008 20 to 2008 80 , 2008 93 , 2008 97 and 2008 99 are to be considered as containing added sugar when the 'sugar content' thereof exceeds by weight the percentages given hereunder, according to the kind of fruit or edible part of plant concerned: - pineapples and grapes: 13 %, - other fruits, including mixtures of fruit, and other edible parts of plants: 9 %. 4. For the purposes of subheadings 2008 30 11 to 2008 30 39 , 2008 40 11 to 2008 40 39 , 2008 50 11 to 2008 50 59 , 2008 60 11 to 2008 60 39 , 2008 70 11 to 2008 70 59 , 2008 80 11 to 2008 80 39 , 2008 93 11 to 2008 93 29 , 2008 97 12 to 2008 97 38 and 2008 99 11 to 2008 99 40 , the following expressions have the meanings hereby assigned to them: - 'actual alcoholic strength by mass': the number of kilograms of pure alcohol contained in 100 kg of the product, - '% mas': the symbol for alcoholic strength by mass. 5. The following is to be applied to the products as they are presented: Item (b) does not apply to concentrated natural fruit juices. Consequently, concentrated natural fruit juices are not excluded from heading 2009 . (a) the added sugar content of products of heading 2009 corresponds to the 'sugar content' less the figures given hereunder, according to the kind of juice concerned: - lemon or tomato juice: 3, - grape juice: 15, - other fruit or vegetable juices, including mixtures of juices: 13. (b) the fruit juices with added sugar, of a Brix value not exceeding 67 and containing less than 50 % by weight of fruit juice lose their original character of fruit juices of heading 2009 . 6. For the purposes of subheadings 2009 69 51 and 2009 69 71 , 'concentrated grape juice (including grape must)' means grape juice (including grape must) for which the figure indicated by a refractometer at a temperature of 20 °C is not less than 50,9 %. 7.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    }
  ],
  "retrieved_tables": [
    {
      "document_id": "L_2023241EN.01007301",
      "table_id": "table_1",
      "row_ids": [
        0
      ],
      "headers": null,
      "rows": [
        [
          "‘E 267",
          "Buffered vinegar’"
        ]
      ]
    },
    {
      "document_id": "L_2016050EN.01002501",
      "table_id": "table_1",
      "row_ids": [
        0
      ],
      "headers": null,
      "rows": [
        [
          "‘12.3",
          "Vinegars and diluted acetic acid (diluted with water to 4-30 % by volume)’"
        ]
      ]
    },
    {
      "document_id": "L_2023241EN.01007301",
      "table_id": "table_11",
      "row_ids": [
        0
      ],
      "headers": null,
      "rows": [
        [
          "",
          "‘E 267",
          "Buffered vinegar",
          "quantum satis",
          "",
          "only prepacked preparations of fresh minced meat and meat preparations to which other ingredients than additives or salt have been added’"
        ]
      ]
    },
    {
      "document_id": "L_2021132EN.01002401",
      "table_id": "table_13",
      "row_ids": [
        1
      ],
      "headers": [
        "CN code | (1)",
        "Description | (2)",
        "Qualification and explanation | (3)"
      ],
      "rows": [
        [
          "Ex20 04",
          "Other vegetables prepared or preserved otherwise than by vinegar or acetic acid, frozen, other than products of heading 2006",
          "Only if containing products of animal origin."
        ]
      ]
    },
    {
      "document_id": "L_2022200EN.01002501",
      "table_id": "table_14",
      "row_ids": [
        2
      ],
      "headers": [
        "CN code | (1)",
        "Description | (2)",
        "Qualification and explanation | (3)"
      ],
      "rows": [
        [
          "ex 2005",
          "Other vegetables prepared or preserved otherwise than by vinegar or acetic acid, not frozen, other than products of heading 2006",
          "Only if containing products of animal origin."
        ]
      ]
    }
  ],
  "retrieval_call_status": "success",
  "review": {
    "case_id": "global_natural_004",
    "decision": "revise",
    "final_question": "What minimum free volatile acid content does the source require for the described heading-2001 products preserved by vinegar or acetic acid?",
    "verified_reference_answer": "At least 0.5% by weight, expressed as acetic acid. This is a stated requirement, not proof that every other classification condition is satisfied; the source also gives an additional salt-content condition for mushrooms of subheading 2001 90 50.",
    "supporting_quote": "For the purposes of heading 2001 , vegetables, fruit, nuts and other edible parts of plants prepared or preserved by vinegar or acetic acid must have a content of free, volatile acid of 0,5 % by weight or more, expressed as acetic acid.",
    "expected_source_keys": [
      "L_2008291EN.01000101 / chunk_112"
    ],
    "retrieval_label": "sufficient",
    "helpful_retrieved_source_keys": [
      "L_2008291EN.01000101 / chunk_112",
      "L_2022282EN.01000101 / chunk_34",
      "L_202402522EN / chunk_34",
      "L_202501926EN / chunk_34"
    ],
    "scope_date_version_caveats": "The original wording 'to fall under heading 2001' could imply the acid threshold is sufficient by itself. The revised question asks only for the stated minimum. Later tariff versions repeat the rule but current applicability is not adjudicated here.",
    "confidence": "high",
    "review_notes": "Exact expected chunk was retrieved; answer-bearing retrieval is sufficient."
  },
  "reference_answer": "At least 0.5% by weight, expressed as acetic acid. This is a stated requirement, not proof that every other classification condition is satisfied; the source also gives an additional salt-content condition for mushrooms of subheading 2001 90 50.",
  "label_origin": "ChatGPT AI-assisted adjudication",
  "quote_matches": [
    "contiguous_normalized"
  ],
  "question_revision_pending": true,
  "expert_validated": false,
  "system_QA_outcome": null
}
```

## QA global_natural_008

```json
{
  "case_id": "global_natural_008",
  "category": "procedure_deadline",
  "question": "When does the TIR Convention enter into force after the required States have completed the specified signature or ratification steps?",
  "proposed_reference_answer": "Six months after five eligible States complete the specified steps; further Contracting Parties are covered six months after their deposit. Do not infer actual deposit dates.",
  "reference_status": "AI_adjudicated",
  "system_answer": null,
  "score_eligible": false,
  "expected_chunks": [
    {
      "document_id": "L_2009165EN.01000101",
      "chunk_id": "chunk_10",
      "excerpt": "Article 53 Entry into force 1. This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession. 2. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession. 3. Any instrument of ratification, acceptance, approval or accession deposited after the entry into force of an amendment to this Convention shall be deemed to apply to this Convention as amended. 4. Any such instrument deposited after an amendment has been accepted but before it has entered into force shall be deemed to apply to this Convention as amended on the date",
      "full_text": "Article 53\nEntry into force\n1. This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession.\n2. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.\n3. Any instrument of ratification, acceptance, approval or accession deposited after the entry into force of an amendment to this Convention shall be deemed to apply to this Convention as amended.\n4. Any such instrument deposited after an amendment has been accepted but before it has entered into force shall be deemed to apply to this Convention as amended on the date when the amendment enters into force.\nArticle 54\nDenunciation\n1. Any Contracting Party may denounce this Convention by so notifying the Secretary-General of the United Nations.\n2. Denunciation shall take effect fifteen months after the date of receipt by the Secretary-General of the notification of denunciation.\n3. The validity of TIR Carnets accepted by the Customs office of departure before the date when the denunciation takes effect shall not be affected thereby and the guarantee of the guaranteeing association shall hold good in accordance with the provisions of this Convention.\nArticle 55\nTermination\nIf, after the entry into force of this Convention, the number of States which are Contracting Parties is for any period of twelve consecutive months reduced to less than five, the Convention shall cease to have effect from the end of the twelve-month period.\nArticle 56\nTermination of the operation of the TIR Convention, 1959\n1. Upon its entry into force, this Convention shall terminate and replace, in relations between the Contracting Parties to this Convention, the TIR Convention, 1959.\n2. Certificates of approval issued in respect of road vehicles and containers under the conditions of the TIR Convention, 1959, shall be accepted during the period of their validity or any extension thereof for the transport of goods under Customs seal by Contracting Parties to this Convention, provided that such vehicles and containers continue to fulfil the conditions under which they were originally approved.\nArticle 57\nSettlement of disputes\n1. Any dispute between two or more Contracting Parties concerning the interpretation or application of this Convention shall, so far as possible be settled by negotiation between them or other means of settlement.\n2. Any dispute between two or more Contracting Parties concerning the interpretation or application of this Convention which cannot be settled by the means indicated in paragraph 1 of this Article shall, at the request of one of them, be referred to an arbitration tribunal composed as follows: each Party to the dispute shall appoint an arbitrator and these arbitrators shall appoint another arbitrator, who shall be chairman. If, three months after receipt of a request, one of the Parties has failed to appoint an arbitrator or if the arbitrators have failed to elect the chairman, any of the Parties may request the Secretary-General of the United Nations to appoint an arbitrator or the chairman of the arbitration tribunal.\n3. The decision of the arbitration tribunal established under the provisions of paragraph 2 shall be binding on the Parties to the dispute.\n4. The arbitration tribunal shall determine its own rules of procedure.\n5. Decisions of the arbitration tribunal shall be taken by majority vote.\n6. Any controversy which may arise between the Parties to the dispute as regards the interpretation and execution of the award may be submitted by any of the Parties for judgment to the arbitration tribunal which made the award.\nArticle 58\nReservations\n1. Any State may, at the time of signing, ratifying or acceding to this Convention, declare that it does not consider itself bound by Article 57, paragraphs 2 to 6, of this Convention. Other Contracting Parties shall not be bound by these paragraphs in respect of any Contracting Party which has entered such a reservation.\n2. Any Contracting Party having entered a reservation as provided for in paragraph 1 of this Article may at any time withdraw such reservation by notifying the Secretary-General of the United Nations.\n3. Apart from the reservations provided for in paragraph 1 of this Article, no reservation to this Convention shall be permitted.\nArticle 58 bis\nAdministrative Committee\nAn Administrative Committee composed of all the Contracting Parties shall be established. Its composition, functions and rules of procedure are set out in Annex 8.\nArticle 58 ter\nTIR Executive Board",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    }
  ],
  "expected_tables": [],
  "retrieved_chunks": [
    {
      "document_id": "L_2013207EN.01000101",
      "chunk_id": "chunk_37",
      "excerpt": "1. The name and full address of the law firm completing the questionnaire. 2. The law firm's relevant experience, which could include experience in legislative and constitutional processes as they relate to the implementation of international treaties in the State, and specific experience in CTC related issues including any experience in advising either a government on implementation and enforcement of the Cape Town Convention or the private sector, or enforcement of creditor's rights in the State which is proposed to be added to the Cape Town List; 3. Whether the law firm is involved or intends to be involved in any transactions that may benefit from a reduction of minimum premium rates if the proposed State is added to the CTC list; ( 21 4. The date on which this questionnaire was completed. II. QUESTIONS 1. Qualifying declarations 1.1 Has the State ( 22 1.2 Please describe the way in ",
      "origin": [
        "direct"
      ],
      "full_text": "1. The name and full address of the law firm completing the questionnaire. 2. The law firm's relevant experience, which could include experience in legislative and constitutional processes as they relate to the implementation of international treaties in the State, and specific experience in CTC related issues including any experience in advising either a government on implementation and enforcement of the Cape Town Convention or the private sector, or enforcement of creditor's rights in the State which is proposed to be added to the Cape Town List; 3. Whether the law firm is involved or intends to be involved in any transactions that may benefit from a reduction of minimum premium rates if the proposed State is added to the CTC list; ( 21 4. The date on which this questionnaire was completed.\nII. QUESTIONS\n1. Qualifying declarations\n1.1 Has the State ( 22 1.2 Please describe the way in which the declarations made differ, if at all, from the requirements referred to in Question 1.1. 1.3 Please confirm that the State has not made any of the declarations listed in Article 3 of Annex 1 to Appendix II of the ASU.\n1. Ratification\n1.1 Has the State ratified, accepted, approved or acceded to the Cape Town Convention and Aircraft Protocol (\"Convention\")? Please could you state the date of ratification/accession and briefly describe the State's process of accession to or ratification of the Convention? 1.2 Do the Convention and Qualifying Declarations (\"QD\") made have the force of law in the whole territory of the State without any further act, implementing legislation or the passing of any further law or regulation? 1.3 If so, please briefly explain the process that gives the Convention and QDs the force of law.\n1. Effect of national and local law\n1.1 Describe and list, if applicable, the implementing legislation and regulation(s) with respect to the Convention and each QD made by the State. 1.2 Would the Convention and QDs made, as translated into national law ( 23 ( 24 1.3 Are there any existing gaps in the implementation of the Convention and QDs? If so, please describe. ( 25\n1. Court and administrative decisions\n1.1. Please describe any matters, including judicial, regulatory, or administrative practice which could be expected to result in the courts, authorities or administrative bodies failing to give full force and effect to the Convention and QDs. ( 26 ( 27 1.2. To your knowledge, has there been any judicial or administrative enforcement action taken by a creditor under the Convention? If so, please describe the action and indicate whether it was successful. 1.3. To your knowledge, since ratification/implementation, have the courts in that State refused in any instance to enforce loan obligations of a debtor or guarantor in the State contrary to the Convention and QDs? 1.4. To your knowledge, are there any other matters that may impact whether courts and administrative bodies should be expected to act in a manner consistent with the Convention and QDs? If so, please specify.\nAppendix III\nMinimum interest rates\nThe provision of official financing support shall not offset or compensate, in part or in full, for the appropriate premium rate to be charged for the risk of non-repayment pursuant to the provisions of Appendix II.\n1. MINIMUM FLOATING INTEREST RATE",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2013218EN.01000801",
      "chunk_id": "chunk_2",
      "excerpt": "(7) Common definitions in this area are important in order to ensure a consistent approach in the Member States to the application of this Directive. (8) There is a need to achieve a common approach to the constituent elements of criminal offences by introducing common offences of illegal access to an information system, illegal system interference, illegal data interference, and illegal interception. (9) Interception includes, but is not necessarily limited to, the listening to, monitoring or surveillance of the content of communications and the procuring of the content of data either directly, through access and use of the information systems, or indirectly through the use of electronic eavesdropping or tapping devices by technical means. (10) Member States should provide for penalties in respect of attacks against information systems. Those penalties should be effective, proportionate",
      "origin": [
        "direct"
      ],
      "full_text": "(7) Common definitions in this area are important in order to ensure a consistent approach in the Member States to the application of this Directive.\n(8) There is a need to achieve a common approach to the constituent elements of criminal offences by introducing common offences of illegal access to an information system, illegal system interference, illegal data interference, and illegal interception.\n(9) Interception includes, but is not necessarily limited to, the listening to, monitoring or surveillance of the content of communications and the procuring of the content of data either directly, through access and use of the information systems, or indirectly through the use of electronic eavesdropping or tapping devices by technical means.\n(10) Member States should provide for penalties in respect of attacks against information systems. Those penalties should be effective, proportionate and dissuasive and should include imprisonment and/or fines.\n(11) This Directive provides for criminal penalties at least for cases which are not minor. Member States may determine what constitutes a minor case according to their national law and practice. A case may be considered minor, for example, where the damage caused by the offence and/or the risk to public or private interests, such as to the integrity of a computer system or to computer data, or to the integrity, rights or other interests of a person, is insignificant or is of such a nature that the imposition of a criminal penalty within the legal threshold or the imposition of criminal liability is not necessary.\n(12) The identification and reporting of threats and risks posed by cyber attacks and the related vulnerability of information systems is a pertinent element of effective prevention of, and response to, cyber attacks and to improving the security of information systems. Providing incentives to report security gaps could add to that effect. Member States should endeavour to provide possibilities for the legal detection and reporting of security gaps.\n(13) It is appropriate to provide for more severe penalties where an attack against an information system is committed by a criminal organisation, as defined in Council Framework Decision 2008/841/JHA of 24 October 2008 on the fight against organised crime ( 3\n(14) Setting up effective measures against identity theft and other identity-related offences constitutes another important element of an integrated approach against cybercrime. Any need for Union action against this type of criminal behaviour could also be considered in the context of evaluating the need for a comprehensive horizontal Union instrument.\n(15) The Council Conclusions of 27 to 28 November 2008 indicated that a new strategy should be developed with the Member States and the Commission, taking into account the content of the 2001 Council of Europe Convention on Cybercrime. That Convention is the legal framework of reference for combating cybercrime, including attacks against information systems. This Directive builds on that Convention. Completing the process of ratification of that Convention by all Member States as soon as possible should be considered to be a priority.\n(16) Given the different ways in which attacks can be conducted, and given the rapid developments in hardware and software, this Directive refers to tools that can be used in order to commit the offences laid down in this Directive. Such tools could include malicious software, including those able to create botnets, used to commit cyber attacks. Even where such a tool is suitable or particularly suitable for carrying out one of the offences laid down in this Directive, it is possible that it was produced for a legitimate purpose Motivated by the need to avoid criminalisation where such tools are produced and put on the market for legitimate purposes, such as to test the reliability of information technology products or the security of information systems, apart from the general intent requirement, a direct intent requirement that those tools be used to commit one or more of the offences laid down in this Directive must be also fulfilled.\n(17) This Directive does not impose criminal liability where the objective criteria of the offences laid down in this Directive are met but the acts are committed without criminal intent, for instance where a person does not know that access was unauthorised or in the case of mandated testing or protection of information systems, such as where a person is assigned by a company or vendor to test the strength of its security system. In the context of this Directive, contractual obligations or agreements to restrict access to information systems by way of a user policy or terms of service, as well as labour disputes as regards the access to and use of information systems of an employer for private purposes, should not incur criminal liability where the access under such circumstances would be deemed unauthorised and thus would constitute the sole basis for criminal proceedings. This Directive is without prejudice to the right of access to information as laid down in national and Union law, while at the same time it may not serve as a justification for unlawful or arbitrary access to information.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2004241EN.01002101",
      "chunk_id": "chunk_9",
      "excerpt": "1. The arbitration tribunal shall lay down its own procedure. Its decisions shall be taken by majority vote. Its award, which shall be based on this Convention, shall be final. 2. The procedure for the settlement of disputes shall not apply to disputes relating to questions within the competence of the European Community or to the definition of the scope of that competence between Parties which are members of the European Community or between such members and the Community. FINAL CLAUSES Article 37 Signature, ratification, acceptance, approval 1. This Convention shall be open for signature by the Member States of the Council of Europe and the European Community. It is subject to ratification, acceptance or approval. Instruments of ratification, acceptance or approval shall be deposited with the Secretary-General of the Council of Europe. 2. No State party to the European Convention on th",
      "origin": [
        "direct"
      ],
      "full_text": "1. The arbitration tribunal shall lay down its own procedure. Its decisions shall be taken by majority vote. Its award, which shall be based on this Convention, shall be final.\n2. The procedure for the settlement of disputes shall not apply to disputes relating to questions within the competence of the European Community or to the definition of the scope of that competence between Parties which are members of the European Community or between such members and the Community.\nFINAL CLAUSES\nArticle 37\nSignature, ratification, acceptance, approval\n1. This Convention shall be open for signature by the Member States of the Council of Europe and the European Community. It is subject to ratification, acceptance or approval. Instruments of ratification, acceptance or approval shall be deposited with the Secretary-General of the Council of Europe.\n2. No State party to the European Convention on the Protection of Animals during International Transport, opened for signature in Paris on 13 December 1968, may deposit its instrument of ratification, acceptance or approval unless it has already denounced the said Convention or denounces it simultaneously.\n3. This Convention shall enter into force six months after the date on which four States have expressed their consent to be bound by this Convention in accordance with the provisions of the preceding paragraphs.\n4. Whenever, in application of the preceding two paragraphs, the denunciation of the Convention of 13 December 1968 would not become effective simultaneously with the entry into force of this Convention, a Contracting State or the European Community may, when depositing its instrument of ratification, acceptance or approval, declare that it will continue to apply the Convention of 13 December 1968 until the entry into force of this Convention.\n5. In respect of any signatory State or the European Community which subsequently expresses its consent to be bound by it, this Convention shall enter into force six months after the date of the deposit of the instrument of ratification, acceptance or approval.\nArticle 38\nAccession of non-Member States\n1. After the entry into force of this Convention, the Committee of Ministers of the Council of Europe may invite any other non-Member State of the Council to accede to this Convention by a decision taken by the majority provided for in Article 20.d of the Statute of the Council of Europe and by the unanimous vote of the representatives of the Contracting States entitled to sit on the Committee.\n2. In respect of any acceding State, this Convention shall enter into force six months after the date of deposit of the instrument of accession with the Secretary-General of the Council of Europe.\nArticle 39\nTerritorial clause\n1. Any State or the European Community may, at the time of signature or when depositing its instrument of ratification, acceptance, approval or accession, specify the territory or territories to which this Convention shall apply.\n2. Any State or the European Community may at any later date, by a declaration addressed to the Secretary-General of the Council of Europe, extend the application of this Convention to any other territory specified in the declaration. In respect of such territory this Convention shall enter into force six months after the date of receipt of such declaration by the Secretary-General.\n3. Any declaration made under the two preceding paragraphs may, in respect of any territory specified in such declaration, be withdrawn by a notification addressed to the Secretary-General. The withdrawal shall become effective six months after the date of receipt of such notification by the Secretary-General.\nArticle 40\nDenunciation\n1. Any Party may at any time denounce this Convention by means of a notification addressed to the Secretary-General of the Council of Europe.\n2. Such denunciation shall become effective six months following the date of receipt of such notification by the Secretary-General.\nArticle 41\nNotifications\nThe Secretary-General of the Council of Europe shall notify the Member States of the Council of Europe, the European Community and any State which has acceded or has been invited to accede to this Convention of:\n(a) any signature; (b) the deposit of any instrument of ratification, acceptance, approval or accession; (c) any date of entry into force of this Convention in accordance with Articles 37 and 38; (d) any other act, notification or communication relating to this Convention.\nIn witness whereof the undersigned, being duly authorised thereto, have signed this Convention.\nDone at ..., this ... day of ..., in English and French, both texts being equally authentic, in a single copy which shall be deposited in the archives of the Council of Europe. The Secretary-General of the Council of Europe shall transmit certified copies to each Member State of the Council of Europe, to the European Community and to any State invited to accede to this Convention.\nEXPLANATORY REPORT\n(as adopted by the Committee of Ministers on 11 June 2003)",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2009121EN.01000301",
      "chunk_id": "chunk_19",
      "excerpt": "(a) inform all Contracting States of: (i) each new signature or deposit of an instrument of ratification, acceptance, approval or accession, together with the date thereof; (ii) the date of entry into force of this Convention; (iii) each declaration made in accordance with this Convention, together with the date thereof; (iv) the withdrawal or amendment of any declaration, together with the date thereof; and (v) the notification of any denunciation of this Convention together with the date thereof and the date on which it takes effect; (b) transmit certified true copies of this Convention to all Contracting States; (c) provide the Supervisory Authority and the Registrar with a copy of each instrument of ratification, acceptance, approval or accession, together with the date of deposit thereof, of each declaration or withdrawal or amendment of a declaration and of each notification of den",
      "origin": [
        "direct",
        "path"
      ],
      "full_text": "(a) inform all Contracting States of: (i) each new signature or deposit of an instrument of ratification, acceptance, approval or accession, together with the date thereof; (ii) the date of entry into force of this Convention; (iii) each declaration made in accordance with this Convention, together with the date thereof; (iv) the withdrawal or amendment of any declaration, together with the date thereof; and (v) the notification of any denunciation of this Convention together with the date thereof and the date on which it takes effect; (b) transmit certified true copies of this Convention to all Contracting States; (c) provide the Supervisory Authority and the Registrar with a copy of each instrument of ratification, acceptance, approval or accession, together with the date of deposit thereof, of each declaration or withdrawal or amendment of a declaration and of each notification of denunciation, together with the date of notification thereof, so that the information contained therein is easily and fully available; and (d) perform such other functions customary for depositaries.\nIN WITNESS WHEREOF the undersigned Plenipotentiaries, having been duly authorised, have signed this Convention.\nDONE at Cape Town, this sixteenth day of November, two thousand and one, in a single original in the English, Arabic, Chinese, French, Russian and Spanish languages, all texts being equally authentic, such authenticity to take effect upon verification by the Joint Secretariat of the Conference under the authority of the President of the Conference within ninety days hereof as to the conformity of the texts with one another.\nPROTOCOL\nto the Convention on international interests in mobile equipment on matters specific to aircraft equipment\nTHE STATES PARTIES TO THIS PROTOCOL,\nCONSIDERING it necessary to implement the Convention on international interests in mobile equipment (hereinafter referred to as 'the Convention') as it relates to aircraft equipment, in the light of the purposes set out in the preamble to the Convention,\nMINDFUL of the need to adapt the Convention to meet the particular requirements of aircraft finance and to extend the sphere of application of the Convention to include contracts of sale of aircraft equipment,\nMINDFUL of the principles and objectives of the Convention on International Civil Aviation, signed at Chicago on 7 December 1944,\nHAVE AGREED upon the following provisions relating to aircraft equipment:\nCHAPTER I\nSPHERE OF APPLICATION AND GENERAL PROVISIONS\nArticle I\nDefined terms\n1. In this Protocol, except where the context otherwise requires, terms used in it have the meanings set out in the Convention.\n2. In this Protocol the following terms are employed with the meanings set out below:",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "31981D0691en",
      "chunk_id": "chunk_8",
      "excerpt": "This Convention shall enter into force on the 30th day following the date of deposit of the eighth instrument of ratification, acceptance or approval by States referred to in paragraph 1 of Article XXVI of this Convention. 2. With respect to each State or regional economic integration organization which subsequent to the date of entry into force of this Convention deposits an instrument of ratification, acceptance, approval or accession, the Convention shall enter into force on the 30th day following such deposit. Article XXIX 1. This Convention shall be open for accession by any State interested in research or harvesting activities in relation to the marine living resources to which this Convention applies. 2. This Convention shall be open for accession by regional economic integration organizations constituted by sovereign States which include among their members one or more States mem",
      "origin": [
        "direct",
        "path"
      ],
      "full_text": "This Convention shall enter into force on the 30th day following the date of deposit of the eighth instrument of ratification, acceptance or approval by States referred to in paragraph 1 of Article XXVI of this Convention. 2. With respect to each State or regional economic integration organization which subsequent to the date of entry into force of this Convention deposits an instrument of ratification, acceptance, approval or accession, the Convention shall enter into force on the 30th day following such deposit. Article XXIX 1. This Convention shall be open for accession by any State interested in research or harvesting activities in relation to the marine living resources to which this Convention applies. 2. This Convention shall be open for accession by regional economic integration organizations constituted by sovereign States which include among their members one or more States members of the Commission and to which the States members of the organization have transferred in whole or in part, competences with regard to the matters covered by this Convention. The accession of such regional economic integration organizations shall be the subject of consultations among members of the Commission. Article XXX 1. This Convention may be amended at any time. 2. If one-third of the members of the Commission request a meeting to discuss a proposed amendement, the Depositary shall call such a meeting. 3. An amendment shall enter into force when the Depositary has received instruments of ratification, acceptance or approval thereof from all the members of the Commission. 4. Such amendment shall thereafter enter into force as to any other Contracting Party when notice of ratification, acceptance or approval by it has been received by the Depositary. Any such Contracting Party from which no such notice has been received within a period of one year from the date of entry into force of the amendment in accordance with paragraph 3 above shall be deemed to have withdrawn from this Convention. Article XXXI 1. Any Contracting Party may withdraw from this Convention on 30 June of any year, by giving written notice not later than 1 January of the same year to the Depositary, which, upon receipt of such a notice, shall communicate it forthwith to the other Contracting Parties. 2. Any other Contracting Party may, within 60 days of the receipt of a copy of such a notice from the Depositary, give written notice of withdrawal to the Depositary in which case the Convention shall cease to be in force on 30 June of the same year with respect to the Contracting Party giving such notice. 3. Withdrawal from this Convention by any Member of the Commission shall not affect its financial obligations under this Convention. Article XXXII The Depositary shall notify all Contracting Parties of the following: (a) signatures of this Convention and the deposit of instruments of ratification, acceptance, approval or accession; (b) the date of entry into force of this Convention and of any amendment thereto. Article XXXIII 1. This Convention, of which the English, French, Russian and Spanish texts are equally authentic, shall be deposited with the Government of Australia which shall transmit duly certified copies thereof to all signatory and acceding Parties. 2. This Convention shall be registered by the Depositary pursuant to Article 102 of the Charter of the United Nations. In witness whereof the undersigned, being duly authorized, have signed this Convention. Drawn up at Canberra this 20th day of May 1980. ANNEX ARBITRAL TRIBUNAL The arbitral tribunal referred to in paragraph 3 of Article XXV shall be composed of three arbitrators who shall be appointed as follows: The Party commencing proceedings shall communicate the name of an arbitrator to the other Party which, in turn, within a period of 40 days following such notification, shall communicate the name of the second arbitrator. The Parties shall, within a period of 60 days following the appointment of the second arbitrator, appoint the third arbitrator, who shall not be a national of either Party and shall not be of the same nationality as either of the first two arbitrators. The third arbitrator shall preside over the tribunal. If the second arbitrator has not been appointed within the prescribed period, or if the Parties have not reached agreement within the prescribed period on the appointment of the third arbitrator, that arbitrator shall be appointed, at the request of either Party, by the Secretary-General of the Permanent Court of Arbitration, from among persons of international standing not having the nationality of a State which is a Party to this Convention. The arbitral tribunal shall decide where its headquarters will be located and shall adopt its own rules of procedure. The award of the arbitral tribunal shall be made by a majority of its members, who may not abstain from voting. Any Contracting Party which is not a Party to the dispute may intervene in the proceedings with the consent of the arbitral tribunal.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2005032EN.01000101",
      "chunk_id": "chunk_18",
      "excerpt": "1.55.1. Entry into force 1. This Convention shall enter into force 30 days after the deposit of instruments of ratification, acceptance, approval or accession by: (a) three States situated north of the 20 o (b) seven States situated south of the 20 o 2. If, within three years of its adoption, this Convention has not been ratified by three of the States referred to in paragraph 1(a), this Convention shall enter into force six months after the deposit of the thirteenth instrument of ratification, acceptance, approval or accession or in accordance with paragraph 1, whichever is the earlier. 3. For each State, entity referred to in Article 305(1)(c), (d) and (e) of the 1982 Convention which is situated in the Convention Area, or regional economic integration organisation which ratifies, formally confirms, accepts or approves the Convention or accedes thereto after the entry into force of thi",
      "origin": [
        "chunk"
      ],
      "full_text": "1.55.1. Entry into force 1. This Convention shall enter into force 30 days after the deposit of instruments of ratification, acceptance, approval or accession by: (a) three States situated north of the 20 o (b) seven States situated south of the 20 o 2. If, within three years of its adoption, this Convention has not been ratified by three of the States referred to in paragraph 1(a), this Convention shall enter into force six months after the deposit of the thirteenth instrument of ratification, acceptance, approval or accession or in accordance with paragraph 1, whichever is the earlier. 3. For each State, entity referred to in Article 305(1)(c), (d) and (e) of the 1982 Convention which is situated in the Convention Area, or regional economic integration organisation which ratifies, formally confirms, accepts or approves the Convention or accedes thereto after the entry into force of this Convention, this Convention shall enter into force on the thirtieth day following the deposit of its instrument of ratification, formal confirmation, acceptance, approval or accession.\n1.56. Article 37\n1.56.1. Reservations and exceptions\nNo reservations or exceptions may be made to this Convention.\n1.57. Article 38\n1.57.1. Declarations and statements\nArticle 37 does not preclude a State, entity referred to in Article 305(1)(c), (d) and (e) of the 1982 Convention which is situated in the Convention Area, or regional economic integration organisation, when signing, ratifying or acceding to this Convention, from making declarations or statements, however phrased or named, with a view, inter alia, to the harmonisation of its laws and regulations with the provisions of this Convention, provided that such declarations or statements do not purport to exclude or to modify the legal effect of the provisions of this Convention in their application to that State, entity or regional economic integration organisation.\n1.58. Article 39\n1.58.1. Relation to other agreements\nThis Convention shall not alter the rights and obligations of Contracting Parties, and fishing entities referred to in Article 9(2), which arise from other agreements compatible with this Convention and which do not affect the enjoyment by other Contracting Parties of their rights or the performance of their obligations under this Convention.\n1.59. Article 40\n1.59.1. Amendment 1. Any member of the Commission may propose amendments to this Convention to be considered by the Commission. Any such proposal shall be made by written communication addressed to the Executive Director at least 60 days before the meeting of the Commission at which it is to be considered. The Executive Director shall promptly circulate such communication to all members of the Commission. 2. Amendments to this Convention shall be considered at the annual meeting of the Commission unless a majority of the members request a special meeting to consider the proposed amendment. A special meeting may be convened on not less than 60 days notice. Amendments to this Convention shall be adopted by consensus. The text of any amendment adopted by the Commission shall be transmitted promptly by the Executive Director to all members of the Commission. 3. Amendments to this Convention shall enter into force for the Contracting Parties ratifying or acceding to them on the 30th day following the deposit of instruments of ratification or accession by a majority of Contracting Parties. Thereafter, for each Contracting Party ratifying or acceding to an amendment after the deposit of the required number of such instruments, the amendment shall enter into force on the thirtieth day following the deposit of its instrument of ratification or accession.\n1.60. Article 41\n1.60.1. Annexes 1. The Annexes form an integral part of this Convention and, unless expressly provided otherwise, a reference to this Convention or to one of its Parts includes a reference to the Annexes relating thereto. 2. The Annexes to this Convention may be revised from time to time and any member of the Commission may propose revisions to an Annex. Notwithstanding the provisions of Article 40, if a revision to an Annex is adopted by consensus at a meeting of the Commission, it shall be incorporated in this Convention and shall take effect from the date of its adoption or from such other date as may be specified in the revision.\n1.61. Article 42",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2009133EN.01000101",
      "chunk_id": "chunk_7",
      "excerpt": "1. At the time of signature, acceptance, approval or accession, a Regional Economic Integration Organisation may declare that it exercises competence over all the matters governed by this Convention and that its Member States will not be Parties to this Convention but shall be bound by virtue of the signature, acceptance, approval or accession of the Organisation. 2. In the event that a declaration is made by a Regional Economic Integration Organisation in accordance with paragraph 1, any reference to a 'Contracting State' or 'State' in this Convention shall apply equally, where appropriate, to the Member States of the Organisation. Article 31 Entry into force 1. This Convention shall enter into force on the first day of the month following the expiration of three months after the deposit of the second instrument of ratification, acceptance, approval or accession referred to in Article 2",
      "origin": [
        "chunk"
      ],
      "full_text": "1. At the time of signature, acceptance, approval or accession, a Regional Economic Integration Organisation may declare that it exercises competence over all the matters governed by this Convention and that its Member States will not be Parties to this Convention but shall be bound by virtue of the signature, acceptance, approval or accession of the Organisation.\n2. In the event that a declaration is made by a Regional Economic Integration Organisation in accordance with paragraph 1, any reference to a 'Contracting State' or 'State' in this Convention shall apply equally, where appropriate, to the Member States of the Organisation.\nArticle 31\nEntry into force\n1. This Convention shall enter into force on the first day of the month following the expiration of three months after the deposit of the second instrument of ratification, acceptance, approval or accession referred to in Article 27.\n2. Thereafter this Convention shall enter into force:\n(a) for each State or Regional Economic Integration Organisation subsequently ratifying, accepting, approving or acceding to it, on the first day of the month following the expiration of three months after the deposit of its instrument of ratification, acceptance, approval or accession; (b) for a territorial unit to which this Convention has been extended in accordance with Article 28(1), on the first day of the month following the expiration of three months after the notification of the declaration referred to in that Article.\nArticle 32\nDeclarations\n1. Declarations referred to in Articles 19, 20, 21, 22 and 26 may be made upon signature, ratification, acceptance, approval or accession or at any time thereafter, and may be modified or withdrawn at any time.\n2. Declarations, modifications and withdrawals shall be notified to the depositary.\n3. A declaration made at the time of signature, ratification, acceptance, approval or accession shall take effect simultaneously with the entry into force of this Convention for the State concerned.\n4. A declaration made at a subsequent time, and any modification or withdrawal of a declaration, shall take effect on the first day of the month following the expiration of three months after the date on which the notification is received by the depositary.\n5. A declaration under Articles 19, 20, 21 and 26 shall not apply to exclusive choice of court agreements concluded before it takes effect.\nArticle 33\nDenunciation\n1. This Convention may be denounced by notification in writing to the depositary. The denunciation may be limited to certain territorial units of a non-unified legal system to which this Convention applies.\n2. The denunciation shall take effect on the first day of the month following the expiration of 12 months after the date on which the notification is received by the depositary. Where a longer period for the denunciation to take effect is specified in the notification, the denunciation shall take effect upon the expiration of such longer period after the date on which the notification is received by the depositary.\nArticle 34\nNotifications by the depositary\nThe depositary shall notify the Members of the Hague Conference on Private International Law, and other States and Regional Economic Integration Organisations which have signed, ratified, accepted, approved or acceded in accordance with Articles 27, 29 and 30 of the following:\n(a) the signatures, ratifications, acceptances, approvals and accessions referred to in Articles 27, 29 and 30; (b) the date on which this Convention enters into force in accordance with Article 31; (c) the notifications, declarations, modifications and withdrawals of declarations referred to in Articles 19, 20, 21, 22, 26, 28, 29 and 30; (d) the denunciations referred to in Article 33.\nIn witness whereof the undersigned, being duly authorised thereto, have signed this Convention.\nDone at The Hague, on 30 June 2005, in the English and French languages, both texts being equally authentic, in a single copy which shall be deposited in the archives of the Government of the Kingdom of the Netherlands, and of which a certified copy shall be sent, through diplomatic channels, to each of the Member States of the Hague Conference on Private International Law as of the date of its Twentieth Session and to each State which participated in that Session.\nANNEX II\nDeclaration by the European Community in accordance with Article 30 of the Convention on Choice of Court Agreements\nThe European Community declares, in accordance with Article 30 of the Convention on Choice of Court Agreements, that it exercises competence over all the matters governed by this Convention. Its Member States will not sign, ratify, accept or approve the Convention, but shall be bound by the Convention by virtue of its conclusion by the European Community.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2005015EN.01000901",
      "chunk_id": "chunk_13",
      "excerpt": "1. This Convention shall enter into force fifteen (15) months after the deposit with the Depositary of the seventh instrument of ratification, acceptance, approval, or accession of the Parties to the 1949 Convention that were Parties to that Convention on the date this Convention was opened for signature. 2. After the date of entry into force of this Convention, with respect to each State or regional economic integration organization that meets the requirements of Article XXVII or Article XXX, this Convention shall enter into force for said State or regional economic integration organization on the thirtieth (30th) day following the deposit of its instrument of ratification, acceptance, approval, or accession. 3. Upon entry into force of this Convention, this Convention shall prevail, as between Parties to this Convention and the 1949 Convention, over the 1949 Convention. 4. Upon the ent",
      "origin": [
        "chunk"
      ],
      "full_text": "1. This Convention shall enter into force fifteen (15) months after the deposit with the Depositary of the seventh instrument of ratification, acceptance, approval, or accession of the Parties to the 1949 Convention that were Parties to that Convention on the date this Convention was opened for signature.\n2. After the date of entry into force of this Convention, with respect to each State or regional economic integration organization that meets the requirements of Article XXVII or Article XXX, this Convention shall enter into force for said State or regional economic integration organization on the thirtieth (30th) day following the deposit of its instrument of ratification, acceptance, approval, or accession.\n3. Upon entry into force of this Convention, this Convention shall prevail, as between Parties to this Convention and the 1949 Convention, over the 1949 Convention.\n4. Upon the entry into force of this Convention, conservation and management measures and other arrangements adopted by the Commission under the 1949 Convention shall remain in force until such time as they expire, are terminated by a decision of the Commission, or are replaced by other measures or arrangements adopted pursuant to this Convention.\n5. Upon entry into force of this Convention, a Party to the 1949 Convention that has not yet consented to be bound by this Convention shall be deemed to remain a member of the Commission unless such Party elects not to remain a member of the Commission by so notifying the Depositary in writing prior to the entry into force of this Convention.\n6. Upon entry into force of this Convention for all Parties to the 1949 Convention, the 1949 Convention shall be considered as terminated in accordance with the relevant rules of international law as reflected in Article 59 of the Vienna Convention on the Law of Treaties.\nArticle XXXII\nProvisional application\n1. In accordance with its laws and regulations, a State or regional economic integration organization that meets the requirements of Article XXVII or Article XXX of this Convention may apply this Convention provisionally by so notifying the Depositary in writing. Such provisional application shall commence on the later of the date of entry into force of this Convention and the date of receipt of such notification by the Depositary.\n2. Provisional application of this Convention by a State or regional economic integration organization referred to in paragraph 1 of this Article shall terminate upon entry into force of this Convention for that State or regional economic integration organization, or upon notification to the Depositary by that State or regional economic integration organization of its intention to terminate its provisional application of this Convention.\nArticle XXXIII\nReservations\nNo reservations may be made to this Convention.\nArticle XXXIV\nAmendments\n1. Any member of the Commission may propose an amendment to the Convention by providing to the Director the text of a proposed amendment at least sixty (60) days in advance of a meeting of the Commission. The Director shall provide a copy of this text to all other members promptly.\n2. Amendments to the Convention shall be adopted in accordance with Article IX, paragraph 2, of this Convention.\n3. Amendments to this Convention shall enter into force ninety (90) days after all Parties to the Convention at the time the amendments were approved have deposited their instruments of ratification, acceptance, or approval of such amendments with the Depositary.\n4. States or regional economic integration organizations that become Parties to this Convention after the entry into force of amendments to the Convention or its annexes shall be considered to be Party to the Convention as amended.\nArticle XXXV\nAnnexes\n1. The Annexes to this Convention form an integral part thereof and, unless expressly provided otherwise, a reference to this Convention includes a reference to the Annexes thereto.\n2. Any member of the Commission may propose an amendment to an Annex to the Convention by providing to the Director the text of a proposed amendment at least sixty (60) days in advance of a meeting of the Commission. The Director shall provide a copy of this text to all other members promptly.\n3. Amendments to the Annexes shall be adopted in accordance with Article IX, paragraph 2, of this Convention.\n4. Unless otherwise agreed, amendments to an Annex shall enter into force for all members of the Commission ninety (90) days after their adoption pursuant to paragraph 3 of this Article.\nArticle XXXVI\nWithdrawal",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    }
  ],
  "retrieved_tables": [
    {
      "document_id": "L_2015250EN.01003801",
      "table_id": "table_7",
      "row_ids": [
        3
      ],
      "headers": [
        "Agreement (date of signature)",
        "Period during which the agreement was set to apply"
      ],
      "rows": [
        [
          "2006 ASA (3 April 2006)",
          "1 January 2006-31 December 2010"
        ]
      ]
    },
    {
      "document_id": "L_2020163EN.01000101",
      "table_id": "table_34",
      "row_ids": [
        0
      ],
      "headers": null,
      "rows": [
        [
          "(Place) (Date)",
          "(Signature ( 107",
          "(Stamp of the approval authority)"
        ]
      ]
    },
    {
      "document_id": "L_2015250EN.01003801",
      "table_id": "table_7",
      "row_ids": [
        4
      ],
      "headers": [
        "Agreement (date of signature)",
        "Period during which the agreement was set to apply"
      ],
      "rows": [
        [
          "2010 ASA (20 October 2010)",
          "1 January 2010-31 December 2013"
        ]
      ]
    },
    {
      "document_id": "L_2015250EN.01003801",
      "table_id": "table_7",
      "row_ids": [
        0
      ],
      "headers": [
        "Agreement (date of signature)",
        "Period during which the agreement was set to apply"
      ],
      "rows": [
        [
          "2000 ASA (22 June 2000)",
          "22 June 2000-21 June 2010"
        ]
      ]
    },
    {
      "document_id": "L_2015250EN.01003801",
      "table_id": "table_7",
      "row_ids": [
        2
      ],
      "headers": [
        "Agreement (date of signature)",
        "Period during which the agreement was set to apply"
      ],
      "rows": [
        [
          "2003 ASA (1 September 2003)",
          "1 September 2003-1 September 2014"
        ]
      ]
    }
  ],
  "retrieval_call_status": "success",
  "review": {
    "case_id": "global_natural_008",
    "decision": "revise",
    "final_question": "Under the supplied TIR Convention provision, when does the Convention enter into force after the required Article 52(1) States complete the specified signature or instrument steps?",
    "verified_reference_answer": "It enters into force six months after five States referred to in Article 52(1) have signed without reservation of ratification, acceptance or approval, or deposited the specified instruments. For a further Contracting Party, it enters into force six months after that party deposits its instrument.",
    "supporting_quote": "This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.",
    "expected_source_keys": [
      "L_2009165EN.01000101 / chunk_10"
    ],
    "retrieval_label": "insufficient",
    "helpful_retrieved_source_keys": [],
    "scope_date_version_caveats": "Retrieved passages concern other conventions with different thresholds and entry-into-force rules (e.g. four States or other deposit counts). They are not substitutes and could actively mislead. 'Eligible States' was tightened to 'States referred to in Article 52(1)'.",
    "confidence": "high",
    "review_notes": "Reference corrected for exact source scope; retrieval does not support the TIR rule."
  },
  "reference_answer": "It enters into force six months after five States referred to in Article 52(1) have signed without reservation of ratification, acceptance or approval, or deposited the specified instruments. For a further Contracting Party, it enters into force six months after that party deposits its instrument.",
  "label_origin": "ChatGPT AI-assisted adjudication",
  "quote_matches": [
    "ordered_source_fragments"
  ],
  "question_revision_pending": true,
  "expert_validated": false,
  "system_QA_outcome": null
}
```

## QA global_natural_018

```json
{
  "case_id": "global_natural_018",
  "category": "table",
  "question": "For the 2021–2025 allocation table, what annual and total allocation quantities are recorded for Audi Brussels?",
  "proposed_reference_answer": "The supplied Audi Brussels row records 3,076 for each year 2021–2025, totalling 15,380. A later revision for the same period may differ: identify document/version, not just years.",
  "reference_status": "AI_adjudicated",
  "system_answer": null,
  "score_eligible": false,
  "expected_chunks": [],
  "expected_tables": [
    {
      "document_id": "C_2022160EN.01002701",
      "table_id": "table_1",
      "row_ids": [
        0
      ],
      "headers": [
        "Installation ID",
        "Installation ID (Union registry)",
        "Installation name",
        "Operator name",
        "Quantity to be allocated | 2021",
        "Quantity to be allocated | 2022",
        "Quantity to be allocated | 2023",
        "Quantity to be allocated | 2024",
        "Quantity to be allocated | 2025",
        "Quantity to be allocated by installation"
      ],
      "rows": [
        [
          "BE000000000000158",
          "158",
          "Audi Brussels NV",
          "Audi Brussels",
          "3 076",
          "3 076",
          "3 076",
          "3 076",
          "3 076",
          "15 380"
        ]
      ]
    }
  ],
  "retrieved_chunks": [
    {
      "document_id": "L_2021231EN.01000101",
      "chunk_id": "chunk_9",
      "excerpt": "Where the update of an integrated national energy and climate plan pursuant to Article 14 of Regulation (EU) 2018/1999 necessitates a revision of a territorial just transition plan, that revision shall be carried out as part of the mid-term review in accordance with Article 18 of Regulation (EU) 2021/1060. 1. Where Member States intend to make use of the possibility to receive support under the other pillars of the Just Transition Mechanism, their territorial just transition plans shall set out the sectors and thematic areas envisaged to be supported under those pillars. Article 12 Indicators 1. Common output and result indicators, as set out in Annex III and, where duly justified in the territorial just transition plan, programme-specific output and result indicators shall be used in accordance with point (a) of the second subparagraph of Article 16(1), point (d)(ii) of Article 22(3) an",
      "origin": [
        "direct"
      ],
      "full_text": "Where the update of an integrated national energy and climate plan pursuant to Article 14 of Regulation (EU) 2018/1999 necessitates a revision of a territorial just transition plan, that revision shall be carried out as part of the mid-term review in accordance with Article 18 of Regulation (EU) 2021/1060.\n1. Where Member States intend to make use of the possibility to receive support under the other pillars of the Just Transition Mechanism, their territorial just transition plans shall set out the sectors and thematic areas envisaged to be supported under those pillars.\nArticle 12\nIndicators\n1. Common output and result indicators, as set out in Annex III and, where duly justified in the territorial just transition plan, programme-specific output and result indicators shall be used in accordance with point (a) of the second subparagraph of Article 16(1), point (d)(ii) of Article 22(3) and point (b) of Article 42(2) of Regulation (EU) 2021/1060.\n2. For output indicators, baselines shall be set at zero. The milestones set for 2024 and targets set for 2029 shall be cumulative. Targets shall not be revised after the request for programme amendment, submitted pursuant to Article 18(3) of Regulation (EU) 2021/1060, has been approved by the Commission.\n3. Where a JTF priority supports the activities referred to in points (k), (l) or (m) of Article 8(2), data on the indicators for participants shall only be transmitted where all the data relating to that participant, required in accordance with Annex III, are available.\nArticle 13\nFinancial corrections\nBased on the examination of the final performance report of the programme, the Commission may make financial corrections in accordance with Article 104 of Regulation (EU) 2021/1060 where less than 65 % of the target set out for one or more output indicators is achieved.\nFinancial corrections shall be in proportion to the achievements and shall not be applied where the failure to achieve targets is due to the impact of socio-economic or environmental factors, significant changes in the economic or environmental conditions in the Member State concerned or because of reasons of force majeure seriously affecting implementation of the priorities concerned.\nArticle 14\nReview\nBy 30 June 2025, the Commission shall review the implementation of the JTF with regard to the specific objective set out in Article 2, taking into account possible changes in Regulation (EU) 2020/852 and the Union's climate objectives set out in a Regulation of the European Parliament and of the Council establishing the framework for achieving climate neutrality and amending Regulations (EC) No 401/2009 and (EU) 2018/1999 ('European Climate Law'), and the evolution in the implementation of the Sustainable Europe Investment Plan. On that basis, the Commission shall submit a report to the European Parliament and to the Council, which may be accompanied by legislative proposals.\nArticle 15\nEntry into force\nThis Regulation shall enter into force on the day following that of its publication in the Official Journal of the European Union .\nThis Regulation shall be binding in its entirety and directly applicable in all Member States.\nDone at Brussels, 24 June 2021.\nFor the European Parliament\nThe President\nD. M. SASSOLI\nFor the Council\nThe President\nA. P. ZACARIAS\n[( 1 )](#ntc1-L_2021231EN.01000101-E0001)\n[OJ C 290, 1.9.2020, p. 1](http://publications.europa.eu/resource/oj/JOC_2020_290_R_TOC)\n.\n[( 2 )](#ntc2-L_2021231EN.01000101-E0002)\n[OJ C 311, 18.9.2020, p. 55](http://publications.europa.eu/resource/oj/JOC_2020_311_R_TOC)\nand\n[OJ C 429, 11.12.2020, p. 240](http://publications.europa.eu/resource/oj/JOC_2020_429_R_TOC)\n.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "LI2020433EN.01002301",
      "chunk_id": "chunk_4",
      "excerpt": "1. For the purpose of Article 21(5) of the Financial Regulation, EUR 384 400 million in 2018 prices, of the amount referred to in Article 2(1) of this Regulation, shall constitute external assigned revenue to the Union programmes referred to in point (a) of Article 2(2) of this Regulation and EUR 5 600 million in 2018 prices of that amount shall constitute external assigned revenue to the Union programmes referred to in point (c) of Article 2(2) of this Regulation. 2. EUR 360 000 million in 2018 prices, of the amount referred to in Article 2(1), shall be used for loans to Member States under the Union programmes referred to in point (b) of Article 2(2). 3. Commitment appropriations covering support to the Union programmes referred to in points (a) and (c) of Article 2(2) shall be made available automatically up to the respective amounts referred to in those points as of the date of entry",
      "origin": [
        "direct"
      ],
      "full_text": "1. For the purpose of Article 21(5) of the Financial Regulation, EUR 384 400 million in 2018 prices, of the amount referred to in Article 2(1) of this Regulation, shall constitute external assigned revenue to the Union programmes referred to in point (a) of Article 2(2) of this Regulation and EUR 5 600 million in 2018 prices of that amount shall constitute external assigned revenue to the Union programmes referred to in point (c) of Article 2(2) of this Regulation.\n2. EUR 360 000 million in 2018 prices, of the amount referred to in Article 2(1), shall be used for loans to Member States under the Union programmes referred to in point (b) of Article 2(2).\n3. Commitment appropriations covering support to the Union programmes referred to in points (a) and (c) of Article 2(2) shall be made available automatically up to the respective amounts referred to in those points as of the date of entry into force of the Own Resources Decision which provides for the empowerment referred to in Article 2(1) of this Regulation.\n4. Legal commitments giving rise to expenditure for support as referred to in point (a) of Article 2(2), and, where appropriate, in point (c) of Article 2(2), shall be entered into by the Commission or by its executive agencies by 31 December 2023. Legal commitments of at least 60 % of the amount referred to in point (a) of Article 2(2) shall be entered into by 31 December 2022.\n5. Decisions on the granting of the loans referred to in point (b) of Article 2(2) shall be adopted by 31 December 2023.\n6. The Union's budgetary guarantees up to an amount which, in accordance with the relevant provisioning rate set out in the respective basic acts, corresponds to the provisioning for budgetary guarantees referred to in point (c) of Article 2(2), depending on the risk profiles of the supported financing and investment operations, shall be granted only for supporting operations which have been approved by the counterparts by 31 December 2023. The respective budgetary guarantee agreements shall contain provisions requiring that financial operations corresponding to at least 60 % of the amount of those budgetary guarantees are approved by the counterparts by 31 December 2022. Where provisioning for budgetary guarantees is used for non-repayable support related to the financing and investment operations referred to in point (c) of Article 2(2), the related legal commitments shall be entered into by the Commission by 31 December 2023.\n7. Paragraphs 4 to 6 of this Article shall not apply to technical and administrative assistance referred to in Article 1(3).\n8. Costs from technical and administrative assistance for the implementation of the Instrument, such as preparatory, monitoring, control, audit and evaluation activities including corporate information technology systems for the purposes of this Regulation, shall be financed from the Union budget.\n9. Payments related to the legal commitments entered into, decisions adopted and the provisions regarding financial operations approved in accordance with paragraphs 4 to 6 of this Article shall be made by 31 December 2026, with the exception of technical and administrative assistance referred to in Article 1(3) and of cases where, exceptionally, although the legal commitment has been entered into, the decision has been adopted or the operation has been approved, on terms compliant with the deadline applicable under this paragraph, payments after 2026 are necessary for the Union to be able to honour its obligations towards third parties, including as a result of a definitive judgment against the Union.\nArticle 4\nReporting\nBy 31 October 2022, the Commission shall submit to the Council a report on the progress achieved in the implementation of the Instrument and the use of the funds allocated in accordance with Article 2(2).\nArticle 5\nApplicability\n1. This Regulation shall not be applicable to or in the United Kingdom.\n2. References to 'Member States' in this Regulation shall not be understood to include the United Kingdom.\nArticle 6\nEntry into force\nThis Regulation shall enter into force on the day following that of its publication in the Official Journal of the European Union .\nThis Regulation shall be binding in its entirety and directly applicable in all Member States.\nDone at Brussels, 14 December 2020.\nFor the Council\nThe President\nM. ROTH",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "31990Y1231_02_en",
      "chunk_id": "chunk_8",
      "excerpt": "The situation is still more striking as regards payment appropriations: between 1984 and 1989 annual payments made amounted on average to 5 % of the total allocation each year while in the first half of 1990 alone 15 % of the total payment appropriations were used. Programme (b) is a special case: in view of the difficulties experienced in implementing the psychiatric reform (see 5.15 5.19 below), the Commission stopped approving new projects in 1989 so the new commitment appropriations available were not used. Considerable delays were also detected in a number of projects approved by the Commission between 1984 and 1988. Those projects, on which work had still not begun by 1 December 1990, were cancelled and the corresponding commitment appropriations will be released. III. The programmes 3.1. The programmes have been improved considerably thanks to technical assistance from the Commiss",
      "origin": [
        "direct"
      ],
      "full_text": "The situation is still more striking as regards payment appropriations: between 1984 and 1989 annual payments made amounted on average to 5 % of the total allocation each year while in the first half of 1990 alone 15 % of the total payment appropriations were used. Programme (b) is a special case: in view of the difficulties experienced in implementing the psychiatric reform (see 5.15 5.19 below), the Commission stopped approving new projects in 1989 so the new commitment appropriations available were not used. Considerable delays were also detected in a number of projects approved by the Commission between 1984 and 1988. Those projects, on which work had still not begun by 1 December 1990, were cancelled and the corresponding commitment appropriations will be released. III. The programmes 3.1. The programmes have been improved considerably thanks to technical assistance from the Commission. The report of 29 March 1984 on 'Psychiatric reform in Greece\n```",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "C_202406955EN",
      "chunk_id": "chunk_4",
      "excerpt": "[( 3 )](#ntc3-C_202406955EN.000101-E0003) Commission Implementing Regulation (EU) 2019/1842 of 31 October 2019 laying down rules for the application of Directive 2003/87/EC of the European Parliament and of the Council as regards further arrangements for the adjustments to free allocation of emission allowances due to activity level changes ( [OJ L 282, 4.11.2019, p. 20](http://publications.europa.eu/resource/oj/JOL_2019_282_R_TOC) , ELI: [http://data.europa.eu/eli/reg](http://data.europa.eu/eli/reg_impl/2019/1842/oj) [_](http://data.europa.eu/eli/reg_impl/2019/1842/oj) [impl/2019/1842/oj](http://data.europa.eu/eli/reg_impl/2019/1842/oj) ). [( 4 )](#ntc4-C_202406955EN.000101-E0004) Commission Decision of 29 June 2021 instructing the Central Administrator of the European Union Transaction Log to enter the national allocation tables of Belgium, Bulgaria, Czechia, Denmark, Germany, Estonia,",
      "origin": [
        "direct"
      ],
      "full_text": "[( 3 )](#ntc3-C_202406955EN.000101-E0003)\nCommission Implementing Regulation (EU) 2019/1842 of 31 October 2019 laying down rules for the application of Directive 2003/87/EC of the European Parliament and of the Council as regards further arrangements for the adjustments to free allocation of emission allowances due to activity level changes (\n[OJ L 282, 4.11.2019, p. 20](http://publications.europa.eu/resource/oj/JOL_2019_282_R_TOC)\n, ELI:\n[http://data.europa.eu/eli/reg](http://data.europa.eu/eli/reg_impl/2019/1842/oj)\n[_](http://data.europa.eu/eli/reg_impl/2019/1842/oj)\n[impl/2019/1842/oj](http://data.europa.eu/eli/reg_impl/2019/1842/oj)\n).\n[( 4 )](#ntc4-C_202406955EN.000101-E0004)\nCommission Decision of 29 June 2021 instructing the Central Administrator of the European Union Transaction Log to enter the national allocation tables of Belgium, Bulgaria, Czechia, Denmark, Germany, Estonia, Ireland, Greece, Spain, France, Croatia, Italy, Cyprus, Latvia, Lithuania, Luxembourg, Hungary, Netherlands, Austria, Poland, Portugal, Romania, Slovenia, Slovakia, Finland and Sweden into the European Union Transaction Log (\n[OJ C 302, 28.7.2021, p. 1](http://publications.europa.eu/resource/oj/JOC_2021_302_R_TOC)\n).\nANNEX I\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Belgium\nANNEX II\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Czechia\nANNEX III\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Denmark\nANNEX IV\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Germany\nANNEX V\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Estonia\nANNEX VI\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Ireland\nANNEX VII\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Greece\nANNEX VIII\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Spain\nANNEX IX\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: France\nANNEX X\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Croatia\nANNEX XI\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Cyprus\nANNEX XII\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Latvia\nANNEX XIII",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "C_202505531EN",
      "chunk_id": "chunk_4",
      "excerpt": "[( 3 )](#ntc3-C_202505531EN.000101-E0003) Commission Implementing Regulation (EU) 2019/1842 of 31 October 2019 laying down rules for the application of Directive 2003/87/EC of the European Parliament and of the Council as regards further arrangements for the adjustments to free allocation of emission allowances due to activity level changes ( [OJ L 282, 4.11.2019, p. 20](http://publications.europa.eu/resource/oj/JOL_2019_282_R_TOC) , ELI: [http://data.europa.eu/eli/reg](http://data.europa.eu/eli/reg_impl/2019/1842/oj) [_](http://data.europa.eu/eli/reg_impl/2019/1842/oj) [impl/2019/1842/oj](http://data.europa.eu/eli/reg_impl/2019/1842/oj) ). [( 4 )](#ntc4-C_202505531EN.000101-E0004) Commission Decision 2021/C 302/01 of 29 June 2021 instructing the Central Administrator of the European Union Transaction Log to enter the national allocation tables of Belgium, Bulgaria, Czechia, Denmark, Ger",
      "origin": [
        "direct"
      ],
      "full_text": "[( 3 )](#ntc3-C_202505531EN.000101-E0003)\nCommission Implementing Regulation (EU) 2019/1842 of 31 October 2019 laying down rules for the application of Directive 2003/87/EC of the European Parliament and of the Council as regards further arrangements for the adjustments to free allocation of emission allowances due to activity level changes (\n[OJ L 282, 4.11.2019, p. 20](http://publications.europa.eu/resource/oj/JOL_2019_282_R_TOC)\n, ELI:\n[http://data.europa.eu/eli/reg](http://data.europa.eu/eli/reg_impl/2019/1842/oj)\n[_](http://data.europa.eu/eli/reg_impl/2019/1842/oj)\n[impl/2019/1842/oj](http://data.europa.eu/eli/reg_impl/2019/1842/oj)\n).\n[( 4 )](#ntc4-C_202505531EN.000101-E0004)\nCommission Decision 2021/C 302/01 of 29 June 2021 instructing the Central Administrator of the European Union Transaction Log to enter the national allocation tables of Belgium, Bulgaria, Czechia, Denmark, Germany, Estonia, Ireland, Greece, Spain, France, Croatia, Italy, Cyprus, Latvia, Lithuania, Luxembourg, Hungary, Netherlands, Austria, Poland, Portugal, Romania, Slovenia, Slovakia, Finland and Sweden into the European Union Transaction Log (\n[OJ C 302, 28.7.2021, p. 1](http://publications.europa.eu/resource/oj/JOC_2021_302_R_TOC)\n).\nANNEX I\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Belgium\nANNEX II\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Bulgaria\nANNEX III\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Czechia\nANNEX IV\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Denmark\nANNEX V\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Germany\nANNEX VI\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Estonia\nANNEX VII\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Spain\nANNEX VIII\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: France\nANNEX IX\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Croatia\nANNEX X\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Italy\nANNEX XI\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Lithuania\nANNEX XII\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Luxembourg\nANNEX XIII",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "C_2023340EN.01000701",
      "chunk_id": "chunk_3",
      "excerpt": "[( 3 )](#ntc3-C_2023340EN.01000701-E0003) Commission Decision (EU) 2021/355 of 25 February 2021 concerning national implementation measures for the transitional free allocation of greenhouse gas emission allowances in accordance with Article 11(3) of Directive 2003/87/EC of the European Parliament and of the Council ( [OJ L 68, 26.2.2021, p. 221](http://publications.europa.eu/resource/oj/JOL_2021_068_R_TOC) ). [( 4 )](#ntc4-C_2023340EN.01000701-E0004) Commission Implementing Regulation (EU) 2021/447 of 12 March 2021 determining revised benchmark values for free allocation of emission allowances for the period from 2021 to 2025 pursuant to Article 10a(2) of Directive 2003/87/EC of the European Parliament and of the Council ( [OJ L 87, 15.3.2021, p. 29](http://publications.europa.eu/resource/oj/JOL_2021_087_R_TOC) ). [( 5 )](#ntc5-C_2023340EN.01000701-E0005) Commission Delegated Regulation",
      "origin": [
        "direct"
      ],
      "full_text": "[( 3 )](#ntc3-C_2023340EN.01000701-E0003)\nCommission Decision (EU) 2021/355 of 25 February 2021 concerning national implementation measures for the transitional free allocation of greenhouse gas emission allowances in accordance with Article 11(3) of Directive 2003/87/EC of the European Parliament and of the Council (\n[OJ L 68, 26.2.2021, p. 221](http://publications.europa.eu/resource/oj/JOL_2021_068_R_TOC)\n).\n[( 4 )](#ntc4-C_2023340EN.01000701-E0004)\nCommission Implementing Regulation (EU) 2021/447 of 12 March 2021 determining revised benchmark values for free allocation of emission allowances for the period from 2021 to 2025 pursuant to Article 10a(2) of Directive 2003/87/EC of the European Parliament and of the Council (\n[OJ L 87, 15.3.2021, p. 29](http://publications.europa.eu/resource/oj/JOL_2021_087_R_TOC)\n).\n[( 5 )](#ntc5-C_2023340EN.01000701-E0005)\nCommission Delegated Regulation (EU) 2019/331 of 19 December 2018 determining transitional Union-wide rules for harmonised free allocation of emission allowances pursuant to Article 10a of Directive 2003/87/EC of the European Parliament and of the Council (\n[OJ L 59, 27.2.2019, p. 8](http://publications.europa.eu/resource/oj/JOL_2019_059_R_TOC)\n).\n[( 6 )](#ntc6-C_2023340EN.01000701-E0006)\nCommission Implementing Decision (EU) 2021/927 of 31 May 2021 determining the uniform cross-sectoral correction factor for the adjustment of free allocations of emission allowances for the period 2021 to 2025 (\n[OJ L 203, 9.6.2021, p. 14](http://publications.europa.eu/resource/oj/JOL_2021_203_R_TOC)\n).\nANNEX I\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Belgium\nANNEX II\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Czechia\nANNEX III\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Denmark\nANNEX IV\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Germany\nANNEX V\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Spain\nANNEX VI\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: France\nANNEX VII\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Croatia\nANNEX VIII\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Italy\nANNEX IX",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "C_202506247EN",
      "chunk_id": "chunk_4",
      "excerpt": "[( 3 )](#ntc3-C_202506247EN.000101-E0003) Commission Implementing Regulation (EU) 2019/1842 of 31 October 2019 laying down rules for the application of Directive 2003/87/EC of the European Parliament and of the Council as regards further arrangements for the adjustments to free allocation of emission allowances due to activity level changes ( [OJ L 282, 4.11.2019, p. 20](http://publications.europa.eu/resource/oj/JOL_2019_282_R_TOC) , ELI: [http://data.europa.eu/eli/reg](http://data.europa.eu/eli/reg_impl/2019/1842/oj) [_](http://data.europa.eu/eli/reg_impl/2019/1842/oj) [impl/2019/1842/oj](http://data.europa.eu/eli/reg_impl/2019/1842/oj) ). [( 4 )](#ntc4-C_202506247EN.000101-E0004) Commission Decision 2021/C 302/01 of 29 June 2021 instructing the Central Administrator of the European Union Transaction Log to enter the national allocation tables of Belgium, Bulgaria, Czechia, Denmark, Ger",
      "origin": [
        "direct"
      ],
      "full_text": "[( 3 )](#ntc3-C_202506247EN.000101-E0003)\nCommission Implementing Regulation (EU) 2019/1842 of 31 October 2019 laying down rules for the application of Directive 2003/87/EC of the European Parliament and of the Council as regards further arrangements for the adjustments to free allocation of emission allowances due to activity level changes (\n[OJ L 282, 4.11.2019, p. 20](http://publications.europa.eu/resource/oj/JOL_2019_282_R_TOC)\n, ELI:\n[http://data.europa.eu/eli/reg](http://data.europa.eu/eli/reg_impl/2019/1842/oj)\n[_](http://data.europa.eu/eli/reg_impl/2019/1842/oj)\n[impl/2019/1842/oj](http://data.europa.eu/eli/reg_impl/2019/1842/oj)\n).\n[( 4 )](#ntc4-C_202506247EN.000101-E0004)\nCommission Decision 2021/C 302/01 of 29 June 2021 instructing the Central Administrator of the European Union Transaction Log to enter the national allocation tables of Belgium, Bulgaria, Czechia, Denmark, Germany, Estonia, Ireland, Greece, Spain, France, Croatia, Italy, Cyprus, Latvia, Lithuania, Luxembourg, Hungary, Netherlands, Austria, Poland, Portugal, Romania, Slovenia, Slovakia, Finland and Sweden into the European Union Transaction Log (\n[OJ C 302, 28.7.2021, p. 1](http://publications.europa.eu/resource/oj/JOC_2021_302_R_TOC)\n).\nANNEX I\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Belgium\nANNEX II\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Bulgaria\nANNEX III\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Czechia\nANNEX IV\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Denmark\nANNEX V\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Germany\nANNEX VI\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Ireland\nANNEX VII\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Greece\nANNEX VIII\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Spain\nANNEX IX\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: France\nANNEX X\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Italy\nANNEX XI\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Latvia\nANNEX XII\nNational allocation table for the period 2021-2025 pursuant to Article 10a of Directive 2003/87/EC\nMember State: Hungary\nANNEX XIII",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2012112EN.01000601",
      "chunk_id": "chunk_74",
      "excerpt": "In the rural development legislative framework for the 2014-2020 programming period, as regards Croatia, special support to facilitate the setting up and administrative operation of producer groups shall be granted, pursuant to the principles laid down in Article 35 of Council Regulation (EC) No 1698/2005, to producer groups which are officially recognised by Croatia's competent authority by 31 December 2017, provided that no similar general measures and/or support is foreseen in the new rural development regulation for the 2014-2020 programming period. C. Leader In the rural development legislative framework for the 2014-2020 programming period, as regards Croatia, the minimum EAFRD contribution to the rural development programme for Leader shall be set on average at a level which is at least half of the percentage of the budget that shall be applicable to the other Member States, if su",
      "origin": [
        "direct"
      ],
      "full_text": "In the rural development legislative framework for the 2014-2020 programming period, as regards Croatia, special support to facilitate the setting up and administrative operation of producer groups shall be granted, pursuant to the principles laid down in Article 35 of Council Regulation (EC) No 1698/2005, to producer groups which are officially recognised by Croatia's competent authority by 31 December 2017, provided that no similar general measures and/or support is foreseen in the new rural development regulation for the 2014-2020 programming period.\nC. Leader\nIn the rural development legislative framework for the 2014-2020 programming period, as regards Croatia, the minimum EAFRD contribution to the rural development programme for Leader shall be set on average at a level which is at least half of the percentage of the budget that shall be applicable to the other Member States, if such a requirement is set.\nD. Complements to direct payments\n1. Support may be granted to farmers eligible for complementary national direct payments or aid under Article 132 of Council Regulation (EC) No 73/2009. 2. The support granted to a farmer in respect of the years 2014, 2015 and 2016 shall not exceed the difference between: (a) the level of direct payments applicable in Croatia for the year concerned in accordance with Article 121 of Council Regulation (EC) No 73/2009; and (b) 45 % of the level of direct payments applicable in the Union as constituted on 30 April 2004 in the relevant year. 3. The Union contribution to support granted under this subsection D in Croatia in respect of the years 2014, 2015 and 2016 shall not exceed 20 % of its respective total annual EAFRD allocation. 4. The Union contribution rate for the complements to direct payments shall not exceed 80 %.\nE. Instrument for pre-accession assistance - Rural development\n1. Croatia may continue to contract or enter into commitments under the IPARD programme under Commission Regulation (EC) No 718/2007 of 12 June 2007 implementing Council Regulation (EC) No 1085/2006 establishing an instrument for pre-accession assistance (IPA) ( 1 2. The Commission shall adopt the necessary measures to this end in accordance with the procedure referred to in Article 5 of European Parliament and Council Regulation (EU) No 182/2011. To that effect, the Commission shall be assisted by the IPA Committee referred to in Article 14(1) of Council Regulation (EC) No 1085/2006.\nF. IPARD ex post evaluation\nIn the rural development legislative framework for the 2014-2020 programming period, as regards the implementation of the IPARD programme for Croatia, expenditure relating to the ex post evaluation of the IPARD programme provided for in Article 191 of Commission Regulation (EC) No 718/2007 may be eligible under technical assistance.\nG. Modernisation of agricultural holdings\nIn the rural development legislative framework for the 2014-2020 programming period, as regards Croatia, the maximum intensity of an aid for the modernisation of agricultural holdings shall be 75 % of the amount of eligible investment for the implementation of Council Directive 91/676/EEC of 12 December 1991 concerning the protection of waters against pollution caused by nitrates from agricultural sources\n[( 2 )](#ntr2-L_2012112EN.01008701-E0002)\n, within a maximum period of four years from the date of accession pursuant to Articles 3(2) and 5(1) of that Directive.\nH. Respect of standards\nIn the rural development legislative framework for the 2014-2020 programming period, as regards Croatia, the statutory management requirements referred to in Annex II to Council Regulation (EC) No 73/2009 applicable in that programming period shall be respected in accordance with the following timetable: requirements referred to in Point A of Annex II shall apply from 1 January 2014; requirements referred to in Point B of Annex II shall apply from 1 January 2016; and requirements referred to in Point C of Annex II shall apply from 1 January 2018.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    }
  ],
  "retrieved_tables": [
    {
      "document_id": "L_2013259EN.01000101",
      "table_id": "table_1",
      "row_ids": [
        0
      ],
      "headers": [
        "",
        "2013",
        "2014",
        "2015",
        "2016",
        "2017",
        "2018"
      ],
      "rows": [
        [
          "Allocation coefficient per year:",
          "0,0000 %",
          "10,7875 %",
          "25,8831 %",
          "76,6830 %",
          "100,0000 %",
          "100,0000 %"
        ]
      ]
    },
    {
      "document_id": "L_2012232EN.01000301",
      "table_id": "table_1",
      "row_ids": [
        0
      ],
      "headers": [
        "",
        "2012",
        "2013",
        "2014",
        "2015",
        "2016",
        "2017"
      ],
      "rows": [
        [
          "Allocation coefficient per year:",
          "87,52 %",
          "45,01 %",
          "100 %",
          "100 %",
          "100 %",
          "100 %"
        ]
      ]
    },
    {
      "document_id": "L_2013259EN.01000101",
      "table_id": "table_1",
      "row_ids": [
        1
      ],
      "headers": [
        "",
        "2013",
        "2014",
        "2015",
        "2016",
        "2017",
        "2018"
      ],
      "rows": [
        [
          "Total amount allocated per Member State (in EUR):",
          "",
          "",
          "",
          "",
          "",
          ""
        ]
      ]
    },
    {
      "document_id": "L_2013280EN.01000301",
      "table_id": "table_1",
      "row_ids": [
        0
      ],
      "headers": [
        "",
        "2013",
        "2014",
        "2015",
        "2016",
        "2017",
        "From 2018"
      ],
      "rows": [
        [
          "Total units per year (global quota per year, caps per subheading)",
          "2 250 000",
          "10 157 500",
          "11 315 000",
          "12 472 500",
          "13 630 000",
          "14 787 500"
        ]
      ]
    },
    {
      "document_id": "L_2013259EN.01000101",
      "table_id": "table_1",
      "row_ids": [
        6
      ],
      "headers": [
        "",
        "2013",
        "2014",
        "2015",
        "2016",
        "2017",
        "2018"
      ],
      "rows": [
        [
          "Total amount allocated to the Member States referred to in points (a) to (d) (in EUR)",
          "0",
          "1 342 478",
          "3 858 439",
          "6 559 570",
          "8 359 247",
          "3 904 420"
        ]
      ]
    }
  ],
  "retrieval_call_status": "success",
  "review": {
    "case_id": "global_natural_018",
    "decision": "revise",
    "final_question": "In C_2022160EN.01002701 table_1, what annual and total allocation quantities are recorded for Audi Brussels for 2021–2025?",
    "verified_reference_answer": "The row for Audi Brussels records 3,076 for each of 2021, 2022, 2023, 2024 and 2025, for a total allocation of 15,380.",
    "supporting_quote": "Audi Brussels NV | Audi Brussels | 3 076 | 3 076 | 3 076 | 3 076 | 3 076 | 15 380",
    "expected_source_keys": [
      "C_2022160EN.01002701 / table_1"
    ],
    "retrieval_label": "insufficient",
    "helpful_retrieved_source_keys": [],
    "scope_date_version_caveats": "Allocation tables can be revised for the same years. The question is made document/table-specific so a later revision is not silently substituted. Retrieved material contains allocation context but not the Audi row/quantities.",
    "confidence": "high",
    "review_notes": "Reference table is internally clear; retrieval does not recover the answer-bearing row."
  },
  "reference_answer": "The row for Audi Brussels records 3,076 for each of 2021, 2022, 2023, 2024 and 2025, for a total allocation of 15,380.",
  "label_origin": "ChatGPT AI-assisted adjudication",
  "quote_matches": [
    "structured_table_requires_row_check"
  ],
  "question_revision_pending": true,
  "expert_validated": false,
  "system_QA_outcome": null
}
```

## QA global_natural_019

```json
{
  "case_id": "global_natural_019",
  "category": "table",
  "question": "For the 2021–2025 allocation table, what amounts are recorded for the Lakeland Dairies Killeshandra Site?",
  "proposed_reference_answer": "The supplied Lakeland Killeshandra row records 4,334 for each year 2021–2025, totalling 21,670. Confirm document/version and any later allocation revisions.",
  "reference_status": "AI_adjudicated",
  "system_answer": null,
  "score_eligible": false,
  "expected_chunks": [],
  "expected_tables": [
    {
      "document_id": "C_2022236EN.01000501",
      "table_id": "table_11",
      "row_ids": [
        1
      ],
      "headers": [
        "Installation ID",
        "Installation ID (Union registry)",
        "Installation name",
        "Operator name",
        "Quantity to be allocated | 2021",
        "Quantity to be allocated | 2022",
        "Quantity to be allocated | 2023",
        "Quantity to be allocated | 2024",
        "Quantity to be allocated | 2025",
        "Quantity to be allocated by installation"
      ],
      "rows": [
        [
          "IE000000000000027",
          "27",
          "Lakeland Dairies Killeshandra Site",
          "Lakeland Dairies Co-operative Society Ltd.",
          "4 334",
          "4 334",
          "4 334",
          "4 334",
          "4 334",
          "21 670"
        ]
      ]
    }
  ],
  "retrieved_chunks": [
    {
      "document_id": "LI2020433EN.01002301",
      "chunk_id": "chunk_4",
      "excerpt": "1. For the purpose of Article 21(5) of the Financial Regulation, EUR 384 400 million in 2018 prices, of the amount referred to in Article 2(1) of this Regulation, shall constitute external assigned revenue to the Union programmes referred to in point (a) of Article 2(2) of this Regulation and EUR 5 600 million in 2018 prices of that amount shall constitute external assigned revenue to the Union programmes referred to in point (c) of Article 2(2) of this Regulation. 2. EUR 360 000 million in 2018 prices, of the amount referred to in Article 2(1), shall be used for loans to Member States under the Union programmes referred to in point (b) of Article 2(2). 3. Commitment appropriations covering support to the Union programmes referred to in points (a) and (c) of Article 2(2) shall be made available automatically up to the respective amounts referred to in those points as of the date of entry",
      "origin": [
        "direct"
      ],
      "full_text": "1. For the purpose of Article 21(5) of the Financial Regulation, EUR 384 400 million in 2018 prices, of the amount referred to in Article 2(1) of this Regulation, shall constitute external assigned revenue to the Union programmes referred to in point (a) of Article 2(2) of this Regulation and EUR 5 600 million in 2018 prices of that amount shall constitute external assigned revenue to the Union programmes referred to in point (c) of Article 2(2) of this Regulation.\n2. EUR 360 000 million in 2018 prices, of the amount referred to in Article 2(1), shall be used for loans to Member States under the Union programmes referred to in point (b) of Article 2(2).\n3. Commitment appropriations covering support to the Union programmes referred to in points (a) and (c) of Article 2(2) shall be made available automatically up to the respective amounts referred to in those points as of the date of entry into force of the Own Resources Decision which provides for the empowerment referred to in Article 2(1) of this Regulation.\n4. Legal commitments giving rise to expenditure for support as referred to in point (a) of Article 2(2), and, where appropriate, in point (c) of Article 2(2), shall be entered into by the Commission or by its executive agencies by 31 December 2023. Legal commitments of at least 60 % of the amount referred to in point (a) of Article 2(2) shall be entered into by 31 December 2022.\n5. Decisions on the granting of the loans referred to in point (b) of Article 2(2) shall be adopted by 31 December 2023.\n6. The Union's budgetary guarantees up to an amount which, in accordance with the relevant provisioning rate set out in the respective basic acts, corresponds to the provisioning for budgetary guarantees referred to in point (c) of Article 2(2), depending on the risk profiles of the supported financing and investment operations, shall be granted only for supporting operations which have been approved by the counterparts by 31 December 2023. The respective budgetary guarantee agreements shall contain provisions requiring that financial operations corresponding to at least 60 % of the amount of those budgetary guarantees are approved by the counterparts by 31 December 2022. Where provisioning for budgetary guarantees is used for non-repayable support related to the financing and investment operations referred to in point (c) of Article 2(2), the related legal commitments shall be entered into by the Commission by 31 December 2023.\n7. Paragraphs 4 to 6 of this Article shall not apply to technical and administrative assistance referred to in Article 1(3).\n8. Costs from technical and administrative assistance for the implementation of the Instrument, such as preparatory, monitoring, control, audit and evaluation activities including corporate information technology systems for the purposes of this Regulation, shall be financed from the Union budget.\n9. Payments related to the legal commitments entered into, decisions adopted and the provisions regarding financial operations approved in accordance with paragraphs 4 to 6 of this Article shall be made by 31 December 2026, with the exception of technical and administrative assistance referred to in Article 1(3) and of cases where, exceptionally, although the legal commitment has been entered into, the decision has been adopted or the operation has been approved, on terms compliant with the deadline applicable under this paragraph, payments after 2026 are necessary for the Union to be able to honour its obligations towards third parties, including as a result of a definitive judgment against the Union.\nArticle 4\nReporting\nBy 31 October 2022, the Commission shall submit to the Council a report on the progress achieved in the implementation of the Instrument and the use of the funds allocated in accordance with Article 2(2).\nArticle 5\nApplicability\n1. This Regulation shall not be applicable to or in the United Kingdom.\n2. References to 'Member States' in this Regulation shall not be understood to include the United Kingdom.\nArticle 6\nEntry into force\nThis Regulation shall enter into force on the day following that of its publication in the Official Journal of the European Union .\nThis Regulation shall be binding in its entirety and directly applicable in all Member States.\nDone at Brussels, 14 December 2020.\nFor the Council\nThe President\nM. ROTH",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2021231EN.01000101",
      "chunk_id": "chunk_9",
      "excerpt": "Where the update of an integrated national energy and climate plan pursuant to Article 14 of Regulation (EU) 2018/1999 necessitates a revision of a territorial just transition plan, that revision shall be carried out as part of the mid-term review in accordance with Article 18 of Regulation (EU) 2021/1060. 1. Where Member States intend to make use of the possibility to receive support under the other pillars of the Just Transition Mechanism, their territorial just transition plans shall set out the sectors and thematic areas envisaged to be supported under those pillars. Article 12 Indicators 1. Common output and result indicators, as set out in Annex III and, where duly justified in the territorial just transition plan, programme-specific output and result indicators shall be used in accordance with point (a) of the second subparagraph of Article 16(1), point (d)(ii) of Article 22(3) an",
      "origin": [
        "direct"
      ],
      "full_text": "Where the update of an integrated national energy and climate plan pursuant to Article 14 of Regulation (EU) 2018/1999 necessitates a revision of a territorial just transition plan, that revision shall be carried out as part of the mid-term review in accordance with Article 18 of Regulation (EU) 2021/1060.\n1. Where Member States intend to make use of the possibility to receive support under the other pillars of the Just Transition Mechanism, their territorial just transition plans shall set out the sectors and thematic areas envisaged to be supported under those pillars.\nArticle 12\nIndicators\n1. Common output and result indicators, as set out in Annex III and, where duly justified in the territorial just transition plan, programme-specific output and result indicators shall be used in accordance with point (a) of the second subparagraph of Article 16(1), point (d)(ii) of Article 22(3) and point (b) of Article 42(2) of Regulation (EU) 2021/1060.\n2. For output indicators, baselines shall be set at zero. The milestones set for 2024 and targets set for 2029 shall be cumulative. Targets shall not be revised after the request for programme amendment, submitted pursuant to Article 18(3) of Regulation (EU) 2021/1060, has been approved by the Commission.\n3. Where a JTF priority supports the activities referred to in points (k), (l) or (m) of Article 8(2), data on the indicators for participants shall only be transmitted where all the data relating to that participant, required in accordance with Annex III, are available.\nArticle 13\nFinancial corrections\nBased on the examination of the final performance report of the programme, the Commission may make financial corrections in accordance with Article 104 of Regulation (EU) 2021/1060 where less than 65 % of the target set out for one or more output indicators is achieved.\nFinancial corrections shall be in proportion to the achievements and shall not be applied where the failure to achieve targets is due to the impact of socio-economic or environmental factors, significant changes in the economic or environmental conditions in the Member State concerned or because of reasons of force majeure seriously affecting implementation of the priorities concerned.\nArticle 14\nReview\nBy 30 June 2025, the Commission shall review the implementation of the JTF with regard to the specific objective set out in Article 2, taking into account possible changes in Regulation (EU) 2020/852 and the Union's climate objectives set out in a Regulation of the European Parliament and of the Council establishing the framework for achieving climate neutrality and amending Regulations (EC) No 401/2009 and (EU) 2018/1999 ('European Climate Law'), and the evolution in the implementation of the Sustainable Europe Investment Plan. On that basis, the Commission shall submit a report to the European Parliament and to the Council, which may be accompanied by legislative proposals.\nArticle 15\nEntry into force\nThis Regulation shall enter into force on the day following that of its publication in the Official Journal of the European Union .\nThis Regulation shall be binding in its entirety and directly applicable in all Member States.\nDone at Brussels, 24 June 2021.\nFor the European Parliament\nThe President\nD. M. SASSOLI\nFor the Council\nThe President\nA. P. ZACARIAS\n[( 1 )](#ntc1-L_2021231EN.01000101-E0001)\n[OJ C 290, 1.9.2020, p. 1](http://publications.europa.eu/resource/oj/JOC_2020_290_R_TOC)\n.\n[( 2 )](#ntc2-L_2021231EN.01000101-E0002)\n[OJ C 311, 18.9.2020, p. 55](http://publications.europa.eu/resource/oj/JOC_2020_311_R_TOC)\nand\n[OJ C 429, 11.12.2020, p. 240](http://publications.europa.eu/resource/oj/JOC_2020_429_R_TOC)\n.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "31999D0485en",
      "chunk_id": "chunk_12",
      "excerpt": "Table 6 takes as its basis the amount of capacity offered and the volume of cargo carried by the EATA parties eastbound and westbound in 1989. In order to make a comparison with subsequent years each base figure has been converted into 100. Table 6 Increase in capacity measured against increase in demand 1989 to 1992 >TABLE> (95) Table 6 demonstates that over the four years 1989 to 1992 taken as a whole capacity eastbound increased at the same rate as demand and that capacity westbound has also grown as a similar rate to the growth of demand. Accordingly it may be deduced from Table 6 that the argument of the EATA parties that eastbound capacity had grown in excess of eastbound demand is not substantiated. (96) The Commission understands that demand on the eastbound leg was well in advance of expectations for the fourth quarter of 1993 and that as a result the capacity non-utilisation pr",
      "origin": [
        "direct"
      ],
      "full_text": "Table 6 takes as its basis the amount of capacity offered and the volume of cargo carried by the EATA parties eastbound and westbound in 1989. In order to make a comparison with subsequent years each base figure has been converted into 100. Table 6 Increase in capacity measured against increase in demand 1989 to 1992 >TABLE> (95) Table 6 demonstates that over the four years 1989 to 1992 taken as a whole capacity eastbound increased at the same rate as demand and that capacity westbound has also grown as a similar rate to the growth of demand. Accordingly it may be deduced from Table 6 that the argument of the EATA parties that eastbound capacity had grown in excess of eastbound demand is not substantiated. (96) The Commission understands that demand on the eastbound leg was well in advance of expectations for the fourth quarter of 1993 and that as a result the capacity non-utilisation programme of the EATA was \"temporarily\" suspended (see recital 27), never to be reintroduced. The assertions of the EATA parties as to the structural nature of the alleged overcapacity on eastbound northern Europe to the Far East services (see recital 24) were accordingly unsubstantiated. In any event, the relevance of these assertions is considered further at recital 227. (97) Moreover, the assertion that the overcapacity at that time was structural in nature is contradicted by the arguments put forward by the parties in the application for individual exemption. To show that any such overcapacity is structural in nature, the parties would have to demonstrate that it could never in its lifetime be efficiently used. However, the EATA parties argued precisely the opposite: \"Even allowing for the present degree of overcapacity ... capacity will have to grow substantially over a 10-year period.\" \"Taking a 10 year view, the maritime transport industry will have to meet substantial demands for additional capacity, as well as a certain level of replacement, at high new-building prices(38).\" (98) In the light of these comments, which the Commission has no reason to doubt, it is considered that the parties assertions that there existed a structural problem of overcapacity on the northern Europe/Far East trades have not been demonstrated to be well-founded. (99) Finally, according to Drewry, the supply/demand balance on the north Europe/Far East trades looked as follows in the period 1992 to 1997. Table 7 North Europe/Far East supply/demand balance 1992 to 1995 >TABLE> (100) The figures given for demand in Table 7 exclude military traffic and relay/transshipment cargo moved via main trade ports as well as empty containers. They therefore underestimate actual vessel utilisation. The figures given for capacity are calculated after deduction of EATA cap in 1993 and 20 % slot reduction due to deadweight limitations. (101) Table 7 demonstrates not only continuous eastbound and westbound growth in demand but also demonstrates, as further illustrated in Table 8, that during the period in which the EATA was in operation, the increase in supply easily outstripped demand. Accordingly, in so far as there were any problems of overcapacity, it may be deduced that these would have been caused by the introduction of new capacity and not the existence of overcapacity at the time of implementation of the EATA. Table 8 North Europe/Far East supply/demand balance Eastbound 1992 to 1997 (million TEUs) >PIC FILE= \"L\n_",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2007095EN.01004101",
      "chunk_id": "chunk_5",
      "excerpt": "Records of bacteriology shall be kept on all samples processed in a format in accordance with or comparable to the example given in Table 3. All strains isolated shall be stored at the NRLs of the two Member States as long as it ensures integrity of the strains for a minimum of five years. All samples of meat juice for serology shall be stored frozen for two years. Table 3 Example of records to be taken on all processed samples 1. Reporting from Bulgaria and Romania The competent authority responsible for the preparation of the yearly national report on the monitoring of Salmonella in animals pursuant to Article 9 of Directive 2003/99/EC shall collect and evaluate the results and report to the Commission. Those reports shall include at least the following information: 6.1. Overall description on the implementation of the survey programme - description of the population under study strati",
      "origin": [
        "direct"
      ],
      "full_text": "Records of bacteriology shall be kept on all samples processed in a format in accordance with or comparable to the example given in Table 3.\nAll strains isolated shall be stored at the NRLs of the two Member States as long as it ensures integrity of the strains for a minimum of five years.\nAll samples of meat juice for serology shall be stored frozen for two years.\nTable 3\nExample of records to be taken on all processed samples\n1. Reporting from Bulgaria and Romania\nThe competent authority responsible for the preparation of the yearly national report on the monitoring of Salmonella in animals pursuant to Article 9 of Directive 2003/99/EC shall collect and evaluate the results and report to the Commission.\nThose reports shall include at least the following information:\n6.1. Overall description on the implementation of the survey programme\n- description of the population under study stratified according to slaughterhouses capacity, - description of randomization procedure, including notification system, - sample size calculated, - details of authorities and laboratories involved in sampling/testing/typing, - overall results of the study (samples analyzed by bacteriology, number of positive, serovar, phage type and antibiotic resistance testing).\n6.2. Complete data on each animal sampled and corresponding tests results\nThe Member States shall submit the results of the survey in the form of raw data using a data dictionary and data collection forms provided by the Commission.\nThat dictionary and forms shall be established by the Commission and include at least the following:\n- reference of the slaughterhouse, - capacity of the slaughterhouse, - date and time of sampling, - reference of the samples (the number), - type of samples taken: lymph nodes, - date of dispatch to the laboratory.\nThe following information shall be collected in the Member States for each sample sent to the laboratory:\n- ID of the laboratory (in case several laboratories are involved), - means of transport of samples, - date of reception by the laboratory, - when testing lymph nodes, weight of the specimen, - results for the individual samples tested: 'negative' or in case positive for Salmonella Salmonella - results for strains subject to antimicrobial susceptibility testing and/or phagetyping results.\n[( 1 )](#ntc1-L_2007095EN.01004401-E0001)\nThis number must represent at least 80 % of slaughtered fattening pigs in a Member State.\n[( 2 )](#ntc2-L_2007095EN.01004401-E0002)\nThe 5th carcass to be processed on the 19th day of that month should be sampled for the survey.\nANNEX II\nMaximum Community financial contribution to Bulgaria and Romania\nANNEX III\nCertified financial report on the implementation of a baseline survey on the prevalence of Salmonella spp. in herds of slaughter pigs\nReporting period: 1 April 2007 to 30 September 2007\nStatement on costs incurred on the survey and eligible for Community financial contribution\nReference number of Commission Decision providing Community financial contribution: ...\n...\nDeclaration by the beneficiary\nWe certify that\n- the costs set out in the statement on costs are genuine and have been incurred in carrying out the tasks laid down in Commission Decision 2007/219/EC and were essential for the proper performance of those tasks; - all supporting documents for those costs are available for audit purposes.\nDate: ...\nPerson financially responsible: ...\nSignature: ...",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2006015EN.01000101",
      "chunk_id": "chunk_6",
      "excerpt": "(54) In the absence of any new information or evidence submitted, the provisional findings concerning the imports into the Community from Norway (volume, market share and average prices) as set out in recitals 54 to 59 of the provisional Regulation are hereby confirmed. 4.7. Price undercutting (55) For the purposes of calculating the level of price undercutting during the IP, the methodology used at provisional stage was also used at definitive stage. The weighted average sales prices of the five companies selected in the sample of Community producers were compared to the weighted average export prices of the sampled exporting producers from Norway on a type-by-type basis. This comparison was made for comparable types of farmed salmon and at the same level of trade, namely for sales to the first independent customer. The comparison was made after deduction of rebates and discounts and th",
      "origin": [
        "direct"
      ],
      "full_text": "(54) In the absence of any new information or evidence submitted, the provisional findings concerning the imports into the Community from Norway (volume, market share and average prices) as set out in recitals 54 to 59 of the provisional Regulation are hereby confirmed.\n4.7. Price undercutting\n(55) For the purposes of calculating the level of price undercutting during the IP, the methodology used at provisional stage was also used at definitive stage. The weighted average sales prices of the five companies selected in the sample of Community producers were compared to the weighted average export prices of the sampled exporting producers from Norway on a type-by-type basis. This comparison was made for comparable types of farmed salmon and at the same level of trade, namely for sales to the first independent customer. The comparison was made after deduction of rebates and discounts and the prices of the imports were CIF Community frontier, adjusted for customs duties. (56) The prices of the sampled Community producers were taken at an ex-works level, i.e. excluding transport costs and at levels of trade comparable to those of the imports concerned. For those sampled Community producers which sold their fish at the farm gate with a deduction of a fee paid to a processing factory, an upward adjustment was made to reflect processing and packing costs in order to make their prices comparable to those of other producers in the sample and to the imports subject to investigation. This adjustment was made on the basis of the actual fee paid to the processing facility or on the basis of the costs incurred by other producers in the sample for these activities. (57) As a result, the price comparison exercise showed that prices of salmon originating in Norway were significantly undercutting the Community industry prices on the Community market during the IP. The average undercutting margin, when expressed as a percentage of the Community industry's prices, was established at around 12 %, i.e. there was, as at the provisional stage, substantial undercutting\n4.8. Situation of the Community industry\n(58) It is recalled that in recital 89 of the provisional Regulation, it was provisionally established that the Community industry had suffered material injury within the meaning of Article 3 of the basic Regulation. (59) Several interested parties questioned the interpretation of the figures relating to the situation of the Community industry as presented in recitals 63 to 89 of the provisional Regulation. They stated that the figures did not show any material injury because some injury indicators, such as production, production capacity, sales volume and stocks showed positive trends. At the same time, whilst they admitted that the business perspectives of the Community industry are not very positive, they considered that overall this should not lead to the conclusion that the Community industry has suffered material injury. (60) In view of these claims, the Commission continued its investigation of injury. It is recalled that as mentioned at recital 40 above, 15 complaining Community producers now constitute the Community industry and, as mentioned at recital 49, five complaining Community producers were selected for the sample. On this basis, the following findings are made.\n4.8.1. Production, production capacity and capacity utilisation\n(61) The production, the production capacity and the capacity utilisation of the Community industry as a whole developed as follows: Table 1 Production, production capacity and capacity utilisation (62) As shown in the table above, production of the Community industry overall increased by 5 % during the period considered. Production first increased by 8 % between 2001 and 2002 but it subsequently decreased by around 1 %, and further decreased again by 2 % in the IP, remaining below the level of 2002. The trends observed are in line with those found at the provisional stage. (63) During the period considered production capacity increased by 21 %. The main increase took place in 2002 (+ 14 %). It is recalled that farmed salmon production in the Community is effectively limited by government licences specifying the maximum amount of live fish, which may be held in the water at any place at any point in time. Thus, the above capacity figures reflect a theoretical capacity based on the total quantity licensed rather than the physical fish-holding capacity of the cages or other production material operated by the Community industry. It is therefore considered that these capacity figures are not decisive in the analysis, as the actual production capacity is lower. (64) Capacity utilisation first decreased by 5 % between 2001 and 2002 and further decreased in 2003 by around 7 % and during the IP by around 2 %.\n4.8.2. Sales volume, market shares, average unit prices in the EC and growth",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_202402746EN",
      "chunk_id": "chunk_25",
      "excerpt": "The quantities of quota (owned quota, rented-in quota and rented-out quota) are compulsory items. Only the quantity as of the end of the accounting year is recorded. The values concerning quotas which can be traded separately from associated land are recorded in this table. The quotas which cannot be traded separately from associated land are only recorded in Table D 'Assets'. The quotas originally acquired freely must be entered as well and valuated at current market values if they can be traded separately from land. Some data entries are simultaneously included, individually or as components of aggregates, at other groups or categories in Tables D 'Assets', H 'Inputs' and/or I 'Crops'. The following categories must be used: 50 Organic manure 60 Entitlements for payments under the basic payment scheme and entitlements for payments under basic income support for sustainability. The follo",
      "origin": [
        "chunk"
      ],
      "full_text": "The quantities of quota (owned quota, rented-in quota and rented-out quota) are compulsory items. Only the quantity as of the end of the accounting year is recorded.\nThe values concerning quotas which can be traded separately from associated land are recorded in this table. The quotas which cannot be traded separately from associated land are only recorded in Table D 'Assets'. The quotas originally acquired freely must be entered as well and valuated at current market values if they can be traded separately from land.\nSome data entries are simultaneously included, individually or as components of aggregates, at other groups or categories in Tables D 'Assets', H 'Inputs' and/or I 'Crops'.\nThe following categories must be used:\n50 Organic manure 60 Entitlements for payments under the basic payment scheme and entitlements for payments under basic income support for sustainability.\nThe following groups of information must be used:\nE.QQ. Quantity (to be recorded for columns N, I, O only)\nThe units to be used are:\n- Category 50 (organic manure): number of animals converted with standard conversion factors for manure excretion, * Category 60 (basic payment scheme and basic income support for sustainability): number of entitlements\nE.QP. Quota purchased (to be recorded for column N only)\nThe amount paid for purchase during the accounting year of quotas or other rights which can be traded separately from associated land should be recorded.\nE.QS. Quota sold (to be recorded for column N only)\nThe amount received for sale during the accounting year of quotas or other rights which can be traded separately from associated land should be recorded.\nE.OV. Opening valuation (to be recorded for column N only)\nThe value at opening valuation of the quantities at the holder's own disposal, whether originally acquired freely or purchased, should be recorded at current market values, if the quotas can be traded separately from associated land.\nE.CV. Closing valuation (to be recorded for column N only)\nThe value at closing valuation of the quantities at the holder's own disposal, whether originally acquired freely or purchased, should be recorded at current market values if the quotas can be traded separately from associated land.\nE.PQ. Payments for quota leased or rented in quota (to be recorded for column I only)\nAmount paid for leasing or renting of quotas or other rights. Also included in rent paid under category 5070 (Rent paid) in Table H 'Inputs'.\nE.RQ. Receipts from leasing or renting out quota (to be recorded for column O only)\nAmount received for renting or leasing of quotas or other rights. Also included under category 90900 ('Other') in Table I 'Crops'.\nE.TX. Taxes, additional levy (column T)\nAmount paid.\nCOLUMNS IN TABLE E\nColumn N refers to owned quota, column I to rented-in quota, column O to rented-out quota, and column T to taxes.\nTable F\nDebts and credits\nStructure of the table\nLiabilities of the holding: the amounts indicated shall relate only to amounts still outstanding, i.e., loans contracted minus the repayments already made.\nThe following categories are to be used:\n    1. Debt - commercial standard - refers to loans not supported by any public policy targeting loan-taking. - 1020. Debt - commercial special - refers to loans benefiting from a public policy support (interest subsidies, guarantees, etc.). - 1030. Debt - family/private loans - loans concluded with a physical person thanks to their family/private relationship with the debtor. - 2010. Payables - amounts owed to suppliers. - 3000. Other liabilities - liabilities other than loans or payables.\nTwo groups of information are to be registered: (OV) opening valuation and (CV) closing valuation.\nThere are two columns: (S) short-term liabilities and (L) long-term liabilities:\n- Short-term liabilities - debt and other liabilities in respect of the holding due in less than one year. - Long-term liabilities - debt and other liabilities in respect of the holding for duration of one year and over.\nTable G\nValue added tax (VAT)\nStructure of the table\nData in monetary terms in the farm return are expressed exclusive of VAT.\nThe following details on VAT should be provided as categories:\n1. Main VAT system in the farm\n2. Minority VAT system in the farm\nCodes as defined for the main VAT system.\nThere is only one group of information (VA) VAT system in the farm. There are three columns: (C) code of the VAT system, (NI) balance non-investments transactions and (I) balance investment transactions.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2010021EN.01000101",
      "chunk_id": "chunk_21",
      "excerpt": "[( 48 )](#ntc48-L_2010021EN.01001901-E0048) Provisional quota in accordance with Article 1(2). [( 49 )](#ntc49-L_2010021EN.01001901-E0049) The use of this quota is subject to the conditions set out in point 3 of the Appendix to this Annex. [( 50 )](#ntc50-L_2010021EN.01001901-E0050) By-catches of cod, haddock and saithe shall be counted against the quotas for these species. [( 51 )](#ntc51-L_2010021EN.01001901-E0051) Provisional quota in accordance with Article 1(2). [( 52 )](#ntc52-L_2010021EN.01001901-E0052) Within an overall TAC of 55 105 tonnes for the northern stock of hake. [( 53 )](#ntc53-L_2010021EN.01001901-E0053) Within an overall TAC of 55 105 tonnes for the northern stock of hake. [( 54 )](#ntc54-L_2010021EN.01001901-E0054) Transfers of this quota may be effected to EU waters of IIa and IV. However, such transfers must be notified in advance to the Commission. [( 55 )](#ntc55",
      "origin": [
        "chunk"
      ],
      "full_text": "[( 48 )](#ntc48-L_2010021EN.01001901-E0048)\nProvisional quota in accordance with Article 1(2).\n[( 49 )](#ntc49-L_2010021EN.01001901-E0049)\nThe use of this quota is subject to the conditions set out in point 3 of the Appendix to this Annex.\n[( 50 )](#ntc50-L_2010021EN.01001901-E0050)\nBy-catches of cod, haddock and saithe shall be counted against the quotas for these species.\n[( 51 )](#ntc51-L_2010021EN.01001901-E0051)\nProvisional quota in accordance with Article 1(2).\n[( 52 )](#ntc52-L_2010021EN.01001901-E0052)\nWithin an overall TAC of 55 105 tonnes for the northern stock of hake.\n[( 53 )](#ntc53-L_2010021EN.01001901-E0053)\nWithin an overall TAC of 55 105 tonnes for the northern stock of hake.\n[( 54 )](#ntc54-L_2010021EN.01001901-E0054)\nTransfers of this quota may be effected to EU waters of IIa and IV. However, such transfers must be notified in advance to the Commission.\n[( 55 )](#ntc55-L_2010021EN.01001901-E0055)\nWithin an overall TAC of 55 105 tonnes for the northern stock of hake.\n[( 56 )](#ntc56-L_2010021EN.01001901-E0056)\nTransfers of this quota may be effected to IV and EU waters of IIa. However, such transfers must be notified in advance to the Commission.\n[( 57 )](#ntc57-L_2010021EN.01001901-E0057)\nWithin an overall TAC of 55 105 tonnes for the northern stock of hake.\n[( 58 )](#ntc58-L_2010021EN.01001901-E0058)\nProvisional quota in accordance with Article 1(2).\n[( 59 )](#ntc59-L_2010021EN.01001901-E0059)\nOf which up to 68 % may be fished in Norwegian Exclusive Economic Zone or in the fishery zone around Jan Mayen (WHB/*NZJM1). This condition will only be applicable as from the date of conclusion of the bilateral fisheries arrangement with Norway for 2010.\n[( 60 )](#ntc60-L_2010021EN.01001901-E0060)\nOf which up to 27 % may be fished in Faroese waters (WHB/*05B-F). This condition will only be applicable as from the date of conclusion of the bilateral fisheries arrangement with the Faroe Islands for 2010.\n[( 61 )](#ntc61-L_2010021EN.01001901-E0061)\nProvisional quota in accordance with Article 1(2).\n[( 62 )](#ntc62-L_2010021EN.01001901-E0062)\nProvisional quota in accordance with Article 1(2).\n[( 63 )](#ntc63-L_2010021EN.01001901-E0063)\nOf which up to 68 % may be fished in Norwegian Exclusive Economic Zone or in the fishery zone around Jan Mayen (WHB/*NZJM2). This condition will only be applicable as from the date of conclusion of the bilateral fisheries arrangement with Norway for 2010.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "31988Y0204_02_en",
      "chunk_id": "chunk_7",
      "excerpt": "Table 3 - Expenditure on each type of measure - Flood II 30 November 1985 Measure Description Expenditure budgeted for 1978-85 Expenditure incurred as at 30 November 1985 Cr Rs % % of Cr Rs actual total measures scheduled 1 Transport and processing capacity ( *) 150 31 151 46 101 2 Technical inputs for milk production (* ) 109 22 39 12 36 3 Milk marketing ( *) 54 11 26 8 48 4 Support for village cooperatives 65 13 15 5 23 5 Planning, information, training and research (*",
      "origin": [
        "chunk"
      ],
      "full_text": "Table 3 - Expenditure on each type of measure - Flood II 30 November 1985 Measure Description Expenditure budgeted for 1978-85 Expenditure incurred as at 30 November 1985 Cr Rs % % of Cr Rs actual total measures scheduled 1 Transport and processing capacity (\n*) 150 31 151 46 101 2 Technical inputs for milk production (*\n) 109 22 39 12 36 3 Milk marketing (\n*) 54 11 26 8 48 4 Support for village cooperatives 65 13 15 5 23 5 Planning, information, training and research (*",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    }
  ],
  "retrieved_tables": [
    {
      "document_id": "C_2022236EN.01000501",
      "table_id": "table_11",
      "row_ids": [
        1
      ],
      "headers": [
        "Installation ID",
        "Installation ID (Union registry)",
        "Installation name",
        "Operator name",
        "Quantity to be allocated | 2021",
        "Quantity to be allocated | 2022",
        "Quantity to be allocated | 2023",
        "Quantity to be allocated | 2024",
        "Quantity to be allocated | 2025",
        "Quantity to be allocated by installation"
      ],
      "rows": [
        [
          "IE000000000000027",
          "27",
          "Lakeland Dairies Killeshandra Site",
          "Lakeland Dairies Co-operative Society Ltd.",
          "4 334",
          "4 334",
          "4 334",
          "4 334",
          "4 334",
          "21 670"
        ]
      ]
    },
    {
      "document_id": "L_202500325EN",
      "table_id": "table_5",
      "row_ids": [
        2
      ],
      "headers": [
        "",
        "2020",
        "2021",
        "2022",
        "RIP"
      ],
      "rows": [
        [
          "Production capacity (tonnes)",
          "480 578",
          "477 621",
          "477 379",
          "476 874"
        ]
      ]
    },
    {
      "document_id": "L_202402163EN",
      "table_id": "table_6",
      "row_ids": [
        2
      ],
      "headers": [
        "",
        "2020",
        "2021",
        "2022",
        "IP"
      ],
      "rows": [
        [
          "Production capacity (tonnes)",
          "21 360 776",
          "21 406 110",
          "21 686 443",
          "21 574 276"
        ]
      ]
    },
    {
      "document_id": "L_202500325EN",
      "table_id": "table_5",
      "row_ids": [
        4
      ],
      "headers": [
        "",
        "2020",
        "2021",
        "2022",
        "RIP"
      ],
      "rows": [
        [
          "Capacity utilisation (%)",
          "83,6",
          "83,0",
          "56,1",
          "36,9"
        ]
      ]
    },
    {
      "document_id": "L_202500325EN",
      "table_id": "table_5",
      "row_ids": [
        0
      ],
      "headers": [
        "",
        "2020",
        "2021",
        "2022",
        "RIP"
      ],
      "rows": [
        [
          "Production volume (tonnes)",
          "401 780",
          "396 575",
          "268 034",
          "175 786"
        ]
      ]
    }
  ],
  "retrieval_call_status": "success",
  "review": {
    "case_id": "global_natural_019",
    "decision": "revise",
    "final_question": "In C_2022236EN.01000501 table_11, what annual and total allocation quantities are recorded for the Lakeland Dairies Killeshandra Site for 2021–2025?",
    "verified_reference_answer": "The row records 4,334 for each of 2021, 2022, 2023, 2024 and 2025, for a total allocation of 21,670.",
    "supporting_quote": "Lakeland Dairies Killeshandra Site | Lakeland Dairies Co-operative Society Ltd. | 4 334 | 4 334 | 4 334 | 4 334 | 4 334 | 21 670",
    "expected_source_keys": [
      "C_2022236EN.01000501 / table_11"
    ],
    "retrieval_label": "sufficient",
    "helpful_retrieved_source_keys": [
      "C_2022236EN.01000501 / table_11"
    ],
    "scope_date_version_caveats": "The question is made document/table-specific because later revisions for the same period may differ.",
    "confidence": "high",
    "review_notes": "Exact expected table row was retrieved."
  },
  "reference_answer": "The row records 4,334 for each of 2021, 2022, 2023, 2024 and 2025, for a total allocation of 21,670.",
  "label_origin": "ChatGPT AI-assisted adjudication",
  "quote_matches": [
    "structured_table_requires_row_check"
  ],
  "question_revision_pending": true,
  "expert_validated": false,
  "system_QA_outcome": null
}
```

## QA global_natural_020

```json
{
  "case_id": "global_natural_020",
  "category": "table",
  "question": "How does the fisheries table distinguish a metier from a fleet segment across its listed geographic aggregation levels?",
  "proposed_reference_answer": "Rows 0–2 distinguish Metier*Fleet segment (Cell): A/A1/A2/A3; Metier: B/B1/B2/B3; Fleet segment: C/C1/C2/C3 across the displayed geographic levels. Do not invent the substantive meaning of the symbols.",
  "reference_status": "AI_adjudicated",
  "system_answer": null,
  "score_eligible": false,
  "expected_chunks": [],
  "expected_tables": [
    {
      "document_id": "L_2010041EN.01000801",
      "table_id": "table_10",
      "row_ids": [
        0,
        1,
        2
      ],
      "headers": [
        "",
        "",
        "Sub regions or fishing grounds | 1",
        "Regions | 2",
        "Supra regions | 3"
      ],
      "rows": [
        [
          "Metier*Fleet segment (Cell)",
          "A",
          "A1",
          "A2",
          "A3"
        ],
        [
          "Metier",
          "B",
          "B1",
          "B2",
          "B3"
        ],
        [
          "Fleet segment",
          "C",
          "C1",
          "C2",
          "C3"
        ]
      ]
    }
  ],
  "retrieved_chunks": [
    {
      "document_id": "L_2010041EN.01000801",
      "chunk_id": "chunk_8",
      "excerpt": "1. Variables 2. Variables to be collected are listed in Appendix VIII. Data shall be provided according to the periodicity stated in that Appendix. 2. Some delays may occur between information provided on the fleet segmentation and on the fishing effort. 3. Disaggregation level 4. The disaggregation level is given in Appendix VIII in accordance with the criteria defined in Appendix V. 2. The degree of aggregation shall correspond to the most disaggregated level required. A grouping of cells within this scheme may be made provided that an appropriate statistical analysis demonstrates its suitability. Such mergers must be approved by the relevant Regional Coordination Meeting. 5. Sampling strategy 6. Wherever possible, transversal data shall be collected in an exhaustive way. Where this is not possible, Member States shall specify the sampling procedures within their national programmes. 7",
      "origin": [
        "direct"
      ],
      "full_text": "1. Variables\n2. Variables to be collected are listed in Appendix VIII. Data shall be provided according to the periodicity stated in that Appendix. 2. Some delays may occur between information provided on the fleet segmentation and on the fishing effort.\n3. Disaggregation level\n4. The disaggregation level is given in Appendix VIII in accordance with the criteria defined in Appendix V. 2. The degree of aggregation shall correspond to the most disaggregated level required. A grouping of cells within this scheme may be made provided that an appropriate statistical analysis demonstrates its suitability. Such mergers must be approved by the relevant Regional Coordination Meeting.\n5. Sampling strategy\n6. Wherever possible, transversal data shall be collected in an exhaustive way. Where this is not possible, Member States shall specify the sampling procedures within their national programmes.\n7. Precision levels\n8. Member States shall include in their annual report information on the quality (accuracy and precision) of the data.\nD. RESEARCH SURVEYS AT SEA\n1. All surveys listed in Appendix IX shall be covered. 2. Member States shall guarantee within their national programmes, continuity with previous survey designs. 3. Notwithstanding points 1 and 2, Member States may propose a modification in the survey effort or sampling design, provided that this does not negatively affect the quality of the results. Acceptance by the Commission of any modification shall be conditional to STECF approval.\nCHAPTER IV\nModule of evaluation of the economic situation of the aquaculture and the processing industry sectors\nA. COLLECTION OF ECONOMIC DATA FOR THE AQUACULTURE SECTOR\n1. Variables\n2. All variables listed in Appendix X are to be collected on an annual basis per segment according to the segmentation set out in Appendix XI. 2. The statistical unit shall be the 'enterprise' defined as the lowest legal entity for accounting purposes. 3. The population shall refer to enterprises whose primary activity is defined according to the EUROSTAT definition under NACE Code 05.02: 'Fish Farming'. 4. National currencies shall be transformed into Euro using the average annual exchange rate available from the European Central Bank (ECB).\n3. Disaggregation level\n4. Data shall be segmented by species and technique for aquaculture, as mentioned in Appendix XI. Member States may further segment by size of enterprise or other relevant criteria, if necessary. 2. Collection of data for fresh water species is not mandatory. However, if this data is collected, Member States shall follow the segmentation set out in Appendix XI.\n5. Sampling strategy\n6. Member States shall describe their methodologies for estimating each economic variable, including quality aspects, in their national programmes. 2. Member States shall ensure consistency and comparability of all economic variables when derived from different sources (e.g. questionnaires, financial accounts).\n7. Precision levels\n8. Member States shall include in their annual report information on the quality (accuracy and precision) of estimates.\nB. COLLECTION OF ECONOMIC DATA CONCERNING THE PROCESSING INDUSTRY\n1. Variables\n2. All variables listed in Appendix XII are to be collected on an annual basis for the population. 2. The population shall refer to enterprises whose main activity is defined according to the EUROSTAT definition under NACE Code 15.20: 'Processing and preserving of fish and fish products'. 3. As a guideline, the national codes applied by Member States under Regulations (EC) No 852/2004 ( 4 ( 5 ( 6 4. National currencies shall be transformed into Euro using the average annual exchange rate available from the European Central Bank (ECB).\n3. Disaggregation level\n4. The statistical unit for collection of data shall be the 'enterprise' as defined as the lowest legal entity for accounting purposes. 2. For enterprises that carry out fish processing but not as a main activity, it is mandatory to collect the following data, in the first year of each programming period: (a) number of enterprises; (b) the turnover attributed to fish processing.\n5. Sampling strategy\n6. Member States shall describe their methodologies for estimating each economic variable, including quality aspects, in their national programmes. 2. Member States shall ensure consistency and comparability of all economic variables when derived from different sources (e.g. questionnaires, financial accounts).\n7. Precision levels\n8. Member States shall include in their annual report information on the quality (accuracy and precision) of estimates.\nCHAPTER V\nModule of evaluation of the effects of the fisheries sector on the marine ecosystem",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "31998D0414en",
      "chunk_id": "chunk_17",
      "excerpt": "In cases where an international organisation referred to in Annex IX, Article 1, of the Convention has competence over all the matters governed by this Agreement, the following provisions shall apply to participation by such international organisation in this Agreement: (a) at the time of signature or accession, such international organisation shall make a declaration stating: (i) that it has competence over all the matters governed by this Agreement; (ii) that, for this reason, its Member States shall not become States Parties, except in respect of their territories for which the international organisation has no responsibility; (iii) that it accepts the rights and obligations of States under this Agreement; (b) participation of such an international organisation shall in no case confer any rights under this Agreement on Member States of the international organisation; (c) in the event ",
      "origin": [
        "direct"
      ],
      "full_text": "In cases where an international organisation referred to in Annex IX, Article 1, of the Convention has competence over all the matters governed by this Agreement, the following provisions shall apply to participation by such international organisation in this Agreement: (a) at the time of signature or accession, such international organisation shall make a declaration stating: (i) that it has competence over all the matters governed by this Agreement; (ii) that, for this reason, its Member States shall not become States Parties, except in respect of their territories for which the international organisation has no responsibility; (iii) that it accepts the rights and obligations of States under this Agreement; (b) participation of such an international organisation shall in no case confer any rights under this Agreement on Member States of the international organisation; (c) in the event of a conflict between the obligations of an international organisation under this Agreement and its obligations under the agreement establishing the international organisation or any acts relating to it, the obligations under this Agreement shall prevail. Article 48 Annexes 1. The Annexes form an integral part of this Agreement and, unless expressly provided otherwise, a reference to this Agreement or to one of its Parts includes a reference to the Annexes relating thereto. 2. The Annexes may be revised from time to time by States Parties. Such revisions shall be based on scientific and technical considerations. Notwithstanding the provisions of Article 45, if a revision to an Annex is adopted by consensus at a meeting of States Parties, it shall be incorporated in this Agreement and shall take effect from the date of its adoption or from such other date as may be specified in the revision. If a revision to an Annex is not adopted by consensus at such a meeting, the amendment procedures set out in Article 45 shall apply. Article 49 Depositary The Secretary-General of the United Nations shall be the depositary of this Agreement and any amendments or revisions thereto. Article 50 Authentic texts The Arabic, Chinese, English, French, Russian and Spanish texts of this Agreement are equally authentic. In witness whereof, the undersigned Plenipotentiaries, being duly authorised thereto, have signed this Agreement. Opened for signature at New York, this fourth day of December, one thousand nine hundred and ninety-five, in a single original, in the Arabic, Chinese, English, French, Russian and Spanish languages. Annex I STANDARD REQUIREMENTS FOR THE COLLECTION AND SHARING OF DATA Article 1 General principles 1. The timely collection, compilation and analysis of data are fundamental to the effective conservation and management of straddling fish stocks and highly migratory fish stocks. To this end, data from fisheries for these stocks on the high seas and those in areas under national jurisdiction are required and should be collected and compiled in such a way as to enable statistically meaningful analysis for the purposes of fishery resource conservation and management. These data include catch and fishing effort statistics and other fishery-related information, such as vessel-related and other data for standardising fishing effort. Data collected should also include information on non-target and associated or dependent species. All data should be verified to ensure accuracy. Confidentiality of non-aggregated data shall be maintained. The dissemination of such data shall be subject to the terms on which they have been provided. 2. Assistance, including training as well as financial and technical assistance, shall be provided to developing States in order to build capacity in the field of conservation and management of living marine resources. Assistance should focus on enhancing capacity to implement data collection and verification, observer programmes, data analysis and research projects supporting stock assessments. The fullest possible involvement of developing State scientists and managers in conservation and management of straddling fish stocks and highly migratory fish stocks should be promoted. Article 2 Principles of data collection, compilation and exchange The following general principles should be considered in defining the parameters for collection, compilation and exchange of data from fishing operations for straddling fish stocks and highly migratory fish stocks: (a) States should ensure that data are collected from vessels flying their flag on fishing activities according to the operational characteristics of each fishing method (e.g., each individual tow for trawl, each set for long-line and purse-seine, each school fished for pole-and-line and each day fished for troll) and in sufficient detail to facilitate effective stock assessment; (b) States should ensure that fishery data are verified through an appropriate system; (c) States should compile fishery-related and other supporting scientific data and provide them in an agreed format and in a timely manner to the relevant subregional or regional fisheries management organisation or arrangement where one exists.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "31998D0414en",
      "chunk_id": "chunk_11",
      "excerpt": "Such procedures shall be consistent with this Article and the basic procedures set out in Article 22 and shall not discriminate against non-members of the organisation or non-participants in the arrangement. Boarding and inspection as well as any subsequent enforcement action shall be conducted in accordance with such procedures. States shall give due publicity to procedures established pursuant to this paragraph. 3. If, within two years of the adoption of this Agreement, any organisation or arrangement has not established such procedures, boarding and inspection pursuant to paragraph 1, as well as any subsequent enforcement action, shall, pending the establishment of such procedures, be conducted in accordance with this Article and the basic procedures set out in Article 22. 4. Prior to taking action under this Article, inspecting States shall, either directly or through the relevant su",
      "origin": [
        "direct"
      ],
      "full_text": "Such procedures shall be consistent with this Article and the basic procedures set out in Article 22 and shall not discriminate against non-members of the organisation or non-participants in the arrangement. Boarding and inspection as well as any subsequent enforcement action shall be conducted in accordance with such procedures. States shall give due publicity to procedures established pursuant to this paragraph. 3. If, within two years of the adoption of this Agreement, any organisation or arrangement has not established such procedures, boarding and inspection pursuant to paragraph 1, as well as any subsequent enforcement action, shall, pending the establishment of such procedures, be conducted in accordance with this Article and the basic procedures set out in Article 22. 4. Prior to taking action under this Article, inspecting States shall, either directly or through the relevant subregional or regional fisheries management organisation or arrangement, inform all States whose vessels fish on the high seas in the subregion or region of the form of identification issued to their duly authorised inspectors. The vessels used for boarding and inspection shall be clearly marked and identifiable as being on government service. At the time of becoming a Party to this Agreement, a State shall designate an appropriate authority to receive notifications pursuant to this Article and shall give due publicity of such designation through the relevant subregional or regional fisheries management organisation or arrangement. 5. Where, following a boarding and inspection, there are clear grounds for believing that a vessel has engaged in any activity contrary to the conservation and management measures referred to in paragraph 1, the inspecting State shall, where appropriate, secure evidence and shall promptly notify the flag State of the alleged violation. 6. The flag State shall respond to the notification referred to in paragraph 5 within three working days of its receipt, or such other period as may be prescribed in procedures established in accordance with paragraph 2, and shall either: (a) fulfil, without delay, its obligations under Article 19 to investigate and, if evidence so warrants, take enforcement action with respect to the vessel, in which case it shall promptly inform the inspecting State of the results of the investigation and of any enforcement action taken; or (b) authorise the inspecting State to investigate. 7. Where the flag State authorises the inspecting State to investigate an alleged violation, the inspecting State shall, without delay, communicate the results of that investigation to the flag State. The flag State shall, if evidence so warrants, fulfil its obligations to take enforcement action with respect to the vessel. Alternatively, the flag State may authorise the inspecting State to take such enforcement action as the flag State may specify with respect to the vessel, consistent with the rights and obligations of the flag State under this Agreement. 8. Where, following boarding and inspection, there are clear grounds for believing that a vessel has committed a serious violation, and the flag State has either failed to respond or failed to take action as required under paragraphs 6 or 7, the inspectors may remain on board and secure evidence and may require the master to assist in further investigation including, where appropriate, by bringing the vessel without delay to the nearest appropriate port, or to such other port as may be specified in procedures established in accordance with paragraph 2. The inspecting State shall immediately inform the flag State of the name of the port to which the vessel is to proceed. The inspecting State and the flag State and, as appropriate, the port State shall take all necessary steps to ensure the well-being of the crew regardless of their nationality. 9. The inspecting State shall inform the flag State and the relevant organisation or the participants in the relevant arrangement of the results of any further investigation. 10. The inspecting State shall require its inspectors to observe generally accepted international regulations, procedures and practices relating to the safety of the vessel and the crew, minimise interference with fishing operations and, to the extent practicable, avoid action which would adversely affect the quality of the catch on board. The inspecting State shall ensure that boarding and inspection is not conducted in a manner that would constitute harassment of any fishing vessel. 11.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "31993D0464en",
      "chunk_id": "chunk_6",
      "excerpt": "The framework already laid down for transport statistics will, of course, continue to be developed through the revision of directives on transport by road, rail and inland waterway and these will be extended to air and sea transport. The information system must be consolidated by a more intermodal approach which can link sectoral methodologies and simplify survey organization. 5. R & D statistics The competency for research and technological development vested in the Community by virtue of the Single Act, strenghtened by the Maastricht agreements and Community policy on promoting innovation, calls for up-to-date and precise statistics. Pursuant to the proposal for a Council Decision on R & D and innovation statistics, the aims of the 1993 to 1997 programme will be to consolidate the present situation and to extend data collection activities, i.e. new information on R & D workers, measuri",
      "origin": [
        "direct"
      ],
      "full_text": "The framework already laid down for transport statistics will, of course, continue to be developed through the revision of directives on transport by road, rail and inland waterway and these will be extended to air and sea transport. The information system must be consolidated by a more intermodal approach which can link sectoral methodologies and simplify survey organization. 5. R & D statistics The competency for research and technological development vested in the Community by virtue of the Single Act, strenghtened by the Maastricht agreements and Community policy on promoting innovation, calls for up-to-date and precise statistics. Pursuant to the proposal for a Council Decision on R & D and innovation statistics, the aims of the 1993 to 1997 programme will be to consolidate the present situation and to extend data collection activities, i.e. new information on R & D workers, measuring the technological potential of the regions and pilot surveys on innovation. Cooperation with the OECD should be stepped up so as to obtain information on R & D financing and expenditure within shorter deadlines. 6. Energy statistics The outlook for energy statistics depends on developments in the economic situation in general and the energy market in particular. Efforts will be directed at improving balance sheets, as regards both product breakdowns and aggregates. The price and consumption surveys will need to be expanded so as to provide better coverage. The activities envisaged will improve, and render more comparable, statistics on the transparency of energy prices and flows, security of supply with targeted measures regarding the extension of the geographical distribution of resourced, the substitution of energy products, the rational use of energy, the exploitation of renewable energy sources, the impact on the environment of emissions resulting from the transformation of energy products (CO2, SO2 etc.) and assessment of their economic significance and on regional energy investment. A strategy of careful use of non-energy raw materials is an important counterpart to these activities. When the networks are opened up, statistical monitoring of their use may be necessary. 7. Tourism statistics A system of tourism statistics will need to be set up in the context of the European Economic Area, based mainly on tourist supply and demand. B. The sectoral programmes for management of the common agricultural policy (CAP) and fisheries statistics Purpose To contribute to the statistical information necessary to manage and monitor the arrangements made under the CAP and as part of fisheries policy. Statistical objectives To propose to the Member States the Community surveys to be carried out, the comparable processing of national surveys, the application of harmonized standards and the introduction of common infrastructure statistics in the following fields: 1. Agricultural statistics Agricultural statistics will undergo a significant change in the coming years as a result of the reform of the CAP and the implementation of the results of a 'screening' operation carried out under the previous programme. It seems inevitable that changes to the instruments for collecting information on production and forecasting production, prices, revenues and agricultural structures will be necessary. The goal is to attain better utilization of the resources devoted to agricultural statistics while limiting as far as possible the growing administrative burden on farmers. (a) Agricultural production Crop production: the introduction of stabilizers in various sectors of crop production, as well as certain likely elements in CAP reform, have emphasized the need to improve the quality, comparability and provision times of these statistics. Reform of the CAP will reinforce the direct impact of statistics on market management. It is therefore necessary not only to create a binding legal framework for crop statistics, but also to continue to seek the most appropriate means of guaranteeing their reliability and objectivity whilst containing financial and manpower costs as far as possible. It is with this aim in mind that research on sampling and forecasting techniques and remote sensing for agricultural statistics will be continued and, if possible, intensified. Animal production: Community statistics and legislation will have to adapt to changes in the markets and market management; they will therefore need to be reviewed carefully at regular intervals in order to ensure that the objectives can be attained at the lowest cost, taking account in particular of the different levels of importance of production in the various countries. Special attention will have to be paid to improving the overall information on slaughterings. Supply balances: these balances provide a synthesis of the statistics on the supply and uses of the various crop and animal products, and their main function is to permit monitoring of the degree of self-sufficiency and of consumption. Adaptations may be required as a consequense of the new system of intra-Community trade after 1992. It is necessary to improve their quality and better define the essential information required, taking account of the fact that the figures constitute reference data for international agreements, in particular for GATT. Fodder supply balances: statistics have been compiled for the last 20 years on the supply of animal feedingstuffs. Studies have been undertaken to determine the nutritional needs of animals in order to assess the demand for feedingstuffs well before data on supply are known.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_202302842EN",
      "chunk_id": "chunk_41",
      "excerpt": "Member States shall set up an electronic database for the purpose of validation of data recorded in accordance with this Regulation. The validation of the data recorded shall include the cross-checking, analysis and verification of the data. 2. Member States shall ensure that all data recorded in accordance with this Regulation are accurate, complete and submitted by operators, masters or other persons authorised under this Regulation within deadlines laid down in the rules of the common fisheries policy.' (b) the following paragraph is inserted: '2a. For the purposes of paragraphs 1 and 2: (c) paragraph 5 is replaced by the following: '5. If an inconsistency in the data has been identified, the Member State concerned shall undertake and document the necessary investigations, analyses and cross-checks. The results of the investigations and corresponding documentation shall be transmitted",
      "origin": [
        "direct"
      ],
      "full_text": "Member States shall set up an electronic database for the purpose of validation of data recorded in accordance with this Regulation. The validation of the data recorded shall include the cross-checking, analysis and verification of the data. 2. Member States shall ensure that all data recorded in accordance with this Regulation are accurate, complete and submitted by operators, masters or other persons authorised under this Regulation within deadlines laid down in the rules of the common fisheries policy.' (b) the following paragraph is inserted: '2a. For the purposes of paragraphs 1 and 2: (c) paragraph 5 is replaced by the following: '5. If an inconsistency in the data has been identified, the Member State concerned shall undertake and document the necessary investigations, analyses and cross-checks. The results of the investigations and corresponding documentation shall be transmitted to the Commission on request. If there are reasons to suspect that an infringement has been committed, the Member State shall also carry out investigations and take the necessary immediate measures in accordance with Articles 85 and 91.' (d) paragraph 8 is replaced by the following: '8. Member States shall establish and keep up to date a national plan for the implementation of the validation system covering the data listed under paragraph 2a, points (a) and (b), and the follow-up of inconsistencies. The plan shall define the Member State priorities for the validation of data and subsequent follow-up on inconsistencies, following a risk-based approach. Member States shall submit that national plan to the Commission within two months from its adoption or update.' (86) Articles 110 and 111 are replaced by the following: 'Article 110 Access to, storage and processing of data 1. Member States shall ensure the remote access at all time and without prior notice, for the Commission or the body designated by it, of the following data in a non-aggregated form: 2. The Commission or the body designated by it may process the data referred to in paragraph 1, in order to fulfil their duties under the rules of the common fisheries policy, in particular for carrying out inspections, verifications, audits and enquiries, or under the rules of agreements with third countries or international organisations. In addition, the Commission may use data referred in paragraph 1 for the development, production and dissemination of European statistics, in particular by Eurostat in accordance with Regulation (EC) No 223/2009 of the European Parliament and of the Council ( *16 3. For the purpose of performing scientific research or provide scientific advice, data listed in paragraph 1, point (a)(i) to (iv), and data concerning catches, discards and landings listed in paragraph 1, point (b)(iii) and (v), may, where necessary, be provided to independent scientific bodies that are recognised at Union, national or international level. Before transferring such data, Member States shall consider whether the scientific research can be conducted on the basis of pseudonymised or anonymised data. In any advice or publication based on such data, those data shall be anonymised. 4. Member States shall establish, implement and host the relevant fisheries databases containing the data referred to in paragraph 1. 5. Member States shall upon a reasoned request by the Commission transmit data on infringements to the Commission or the body designated by it. The data shall include, in particular, the date of the infringement, the date of the definitive decision and the applied sanctions and measures, including assigned points. Article 111 Exchange of data 1. Each flag Member State shall ensure the direct electronic exchange of relevant information with other Member States concerned, in particular: 2. Each coastal Member State shall ensure the direct electronic exchange of relevant information with other Member States concerned and the Commission or the body designated by it, in particular by sending: 3. Each flag Member State shall ensure the direct electronic exchange of relevant information concerning vessels flying its flag to the Commission or the body designated by it, in particular: ( *16 OJ L 87, 31.3.2009, p. 164 (87) The following article is inserted: 'Article 111a Uniform conditions for the implementation of provisions on data For the purpose of implementing provisions of this Chapter, the Commission may, by means of implementing acts, lay down detailed rules on: Those implementing acts shall be adopted in accordance with the examination procedure referred to in Article 119(2).'. (88) Article 112 is replaced by the following: 'Article 112 Protection of personal data 1. Regulations (EU) 2016/679 ( *17 ( *18 ( *19 2. Personal data collected under this Regulation may only be processed for the following purposes, provided that those purposes cannot be fulfilled with data that do not permit identification of data subjects: 3.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2013354EN.01008601",
      "chunk_id": "chunk_3",
      "excerpt": "1. Until 31 December 2021, Article 5(3) and Articles 6, 8, 41, 56, 58 to 62, 66, 68 and 109 shall not apply to France in respect of fishing vessels which are less than 10 metres in overall length and which operate from Mayotte, an outermost region within the meaning of Article 349 of the Treaty on the Functioning of the European Union (hereinafter \"Mayotte\"), and the activities and catch of such fishing vessels. 2. By 30 September 2014, France shall establish a simplified and provisional scheme of control applicable to fishing vessels which are less than 10 metres in overall length and which operate from Mayotte. That scheme shall address the following issues: (a) knowledge of fishing capacity; (b) access to Mayotte waters; (c) implementation of declaration obligations; (d) designation of the authorities responsible for the control activities; (e) measures ensuring that any enforcement o",
      "origin": [
        "direct"
      ],
      "full_text": "1. Until 31 December 2021, Article 5(3) and Articles 6, 8, 41, 56, 58 to 62, 66, 68 and 109 shall not apply to France in respect of fishing vessels which are less than 10 metres in overall length and which operate from Mayotte, an outermost region within the meaning of Article 349 of the Treaty on the Functioning of the European Union (hereinafter \"Mayotte\"), and the activities and catch of such fishing vessels.\n2. By 30 September 2014, France shall establish a simplified and provisional scheme of control applicable to fishing vessels which are less than 10 metres in overall length and which operate from Mayotte. That scheme shall address the following issues:\n(a) knowledge of fishing capacity; (b) access to Mayotte waters; (c) implementation of declaration obligations; (d) designation of the authorities responsible for the control activities; (e) measures ensuring that any enforcement on vessels longer than 10 metres length is carried out on a non-discriminatory basis.\nBy 30 September 2020, France shall present to the Commission an action plan setting out the measures to be taken in order to ensure the full implementation of Regulation (EC) No 1224/2009 from 1 January 2022 concerning fishing vessels which are less than 10 metres in overall length and which operate from Mayotte. That action plan shall be the subject of a dialogue between France and the Commission. France shall take all necessary measures to implement that action plan.\"\nArticle 6\nEntry into force\nThis Regulation shall enter into force on 1 January 2014.\nThis Regulation shall be binding in its entirety and directly applicable in all Member States.\nDone at Brussels, 17 December 2013.\nFor the Council\nThe President\nL. LINKEVIČIUS\n[( 1 )](#ntc1-L_2013354EN.01008601-E0001)\nOpinion of 12 December 2013 (not yet published in the Official Journal).\n[( 2 )](#ntc2-L_2013354EN.01008601-E0002)\n[OJ C 341, 21.11.2013, p. 97](http://publications.europa.eu/resource/oj/JOC_2013_341_R_TOC)\n.\n[( 3 )](#ntc3-L_2013354EN.01008601-E0003)\nEuropean Council Decision 2012/419/EU of 11 July 2012 amending the status of Mayotte with regard to the European Union (\n[OL L 204, 31.7.2012, p. 131](http://publications.europa.eu/resource/oj/JOL_2012_204_R_TOC)\n).\n[( 4 )](#ntc4-L_2013354EN.01008601-E0004)\nCouncil Regulation (EC) No 850/98 of 30 March 1998 for the conservation of fishery resources through technical measures for the protection of juveniles of marine organism (\n[OJ L 125, 27.4.1998, p. 1](http://publications.europa.eu/resource/oj/JOL_1998_125_R_TOC)\n).\n[( 5 )](#ntc5-L_2013354EN.01008601-E0005)\nSee page 1 of this Official Journal.\n[( 6 )](#ntc6-L_2013354EN.01008601-E0006)\nSee page 22 of this Official Journal.",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2021253EN.01005101",
      "chunk_id": "chunk_5",
      "excerpt": "Table 4 (previously Table 3) Species for which data are to be collected for recreational fisheries Table 5 (previously Table 2) Fishing activity (metier) Table 6 (previously Table 4) Fishing activity variables Table 7 (previously Table 5A) Fleet economic variables Table 8 (previously Table 5B) Fleet segmentation Table 9 (previously Table 6) Social variables for the fishing and aquaculture sectors Table 10 (previously Table 7) Economic variables in the aquaculture sector Table 11 (previously Table 9) Segmentation to be applied for the collection of aquaculture data [( 65 )](#ntr65-L_2021253EN.01005301-E0065) [( 1 )](#ntc1-L_2021253EN.01005301-E0001) Regulation (EU) 2017/1004 of the European Parliament and of the Council of 17 May 2017 on the establishment of a Union framework for the collection, management and use of data in the fisheries sector and support for scientific advice regarding",
      "origin": [
        "chunk"
      ],
      "full_text": "Table 4 (previously Table 3)\nSpecies for which data are to be collected for recreational fisheries\nTable 5 (previously Table 2)\nFishing activity (metier)\nTable 6 (previously Table 4)\nFishing activity variables\nTable 7 (previously Table 5A)\nFleet economic variables\nTable 8 (previously Table 5B)\nFleet segmentation\nTable 9 (previously Table 6)\nSocial variables for the fishing and aquaculture sectors\nTable 10 (previously Table 7)\nEconomic variables in the aquaculture sector\nTable 11 (previously Table 9)\nSegmentation to be applied for the collection of aquaculture data\n[( 65 )](#ntr65-L_2021253EN.01005301-E0065)\n[( 1 )](#ntc1-L_2021253EN.01005301-E0001)\nRegulation (EU) 2017/1004 of the European Parliament and of the Council of 17 May 2017 on the establishment of a Union framework for the collection, management and use of data in the fisheries sector and support for scientific advice regarding the common fisheries policy and repealing Council Regulation (EC) No 199/2008 (\n[OJ L 157, 20.6.2017, p. 1](http://publications.europa.eu/resource/oj/JOL_2017_157_R_TOC)\n).\n[( 2 )](#ntc2-L_2021253EN.01005301-E0002)\nCouncil Regulation (EC) No 1224/2009 of 20 November 2009 establishing a Union control system for ensuring compliance with the rules of the common fisheries policy, amending Regulations (EC) No 847/96, (EC) No 2371/2002, (EC) No 811/2004, (EC) No 768/2005, (EC) No 2115/2005, (EC) No 2166/2005, (EC) No 388/2006, (EC) No 509/2007, (EC) No 676/2007, (EC) No 1098/2007, (EC) No 1300/2008, (EC) No 1342/2008 and repealing Regulations (EEC) No 2847/93, (EC) No 1627/94 and (EC) No 1966/2006 (\n[OJ L 343, 22.12.2009, p. 1](http://publications.europa.eu/resource/oj/JOL_2009_343_R_TOC)\n).\n[( 3 )](#ntc3-L_2021253EN.01005301-E0003)\nCommission Implementing Regulation (EU) No 404/2011 of 8 April 2011 laying down detailed rules for the implementation of Council Regulation (EC) No 1224/2009 establishing a Community control system for ensuring compliance with the rules of the Common Fisheries Policy (\n[OJ L 112, 30.4.2011, p. 1](http://publications.europa.eu/resource/oj/JOL_2011_112_R_TOC)\n).",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    },
    {
      "document_id": "L_2010041EN.01000801",
      "chunk_id": "chunk_4",
      "excerpt": "1. Variables 2. Sampling must be performed in order to evaluate the quarterly length distribution of species in the catches, and the quarterly volume of discards. Data shall be collected by metier referred to as level 6 of the matrix defined in Appendix IV (1 to 5) and for the stocks listed in Appendix VII. 2. Where relevant additional biological sampling programmes of the unsorted landings have to be carried out in order to estimate: (a) the share of the various stocks in these landings for Herring in the Skagerrak IIIA-N, Kattegat IIIa-S, and Eastern North Sea separately and salmon in the Baltic Sea; (b) the share of the various species for those groups of species that are internationally assessed, e.g. Megrims, Anglerfishes and elasmobranches. 3. Disaggregation level 4. In order to optimise the sampling programmes, the metiers defined in Appendix IV (1 to 5) may be merged. When metier",
      "origin": [
        "chunk"
      ],
      "full_text": "1. Variables\n2. Sampling must be performed in order to evaluate the quarterly length distribution of species in the catches, and the quarterly volume of discards. Data shall be collected by metier referred to as level 6 of the matrix defined in Appendix IV (1 to 5) and for the stocks listed in Appendix VII. 2. Where relevant additional biological sampling programmes of the unsorted landings have to be carried out in order to estimate: (a) the share of the various stocks in these landings for Herring in the Skagerrak IIIA-N, Kattegat IIIa-S, and Eastern North Sea separately and salmon in the Baltic Sea; (b) the share of the various species for those groups of species that are internationally assessed, e.g. Megrims, Anglerfishes and elasmobranches.\n3. Disaggregation level\n4. In order to optimise the sampling programmes, the metiers defined in Appendix IV (1 to 5) may be merged. When metiers are merged (vertical merging), statistical evidence shall be brought regarding the homogeneity of the combined metiers. Merging of neighbouring cells corresponding to fleet segments of the vessels (horizontal merging) shall be supported by statistical evidence. Such horizontal merging shall be done primarily by clustering neighbouring vessel LOA classes, independently of the dominant fishing techniques, when appropriate to distinguish different exploitation patterns. Regional agreement on mergers shall be sought at the relevant Regional Coordination Meeting and endorsed by STECF. 2. At national level, one metier defined at level 6 of the matrix in Appendix IV (1 to 5) may be further disaggregated into several more precise strata, i.e. distinguishing different target species. Such further stratification shall be done respecting the two following principles: (a) the strata defined at national level do not overlap the metiers defined in Appendix IV (1 to 5); (b) the strata defined at national level must, in their entirety comprise of all the fishing trips of the metier defined at level 6. 3. The spatial units for metier sampling are defined by level 3 of Appendix I for all the regions with the following exceptions: (a) the Baltic Sea (ICES areas III b-d), Mediterranean Sea and the Black Sea where the resolution shall be level 4; (b) Regional Fisheries Management Organisations units, providing they are metier-based (in the absence of such definitions, Regional Fisheries Management Organisations shall proceed to appropriate mergers). 4. For the purpose of collection and aggregation of data, spatial sampling units may be clustered by regions as referred to in Article 1 of Commission Regulation (EC) 665/2008 ( 2 5. For parameters referred to in Chapter III section B/B1 1. (2), data shall be provided quarterly and be consistent with the fleet fishing activity matrix described in Appendix IV (1 to 5).\n5. Sampling strategy",
      "source_resolution": "document_chunk_sqlite",
      "text_is_complete": true
    }
  ],
  "retrieved_tables": [
    {
      "document_id": "L_2022008EN.01014201",
      "table_id": "table_26",
      "row_ids": [
        0
      ],
      "headers": null,
      "rows": [
        [
          "General comment: This table is intended to indicate the size of fleet segments and clustering schemes. The population shall include all active and inactive vessels registered in the Union Fishing Fleet Register, as defined in Commission Regulation (EU) 2017/218 on 31 December of the reporting year, and vessels that do not appear on the Register at that date but have fished at least one day during the reporting year.",
          "General comment: This table is intended to indicate the size of fleet segments and clustering schemes. The population shall include all active and inactive vessels registered in the Union Fishing Fleet Register, as defined in Commission Regulation (EU) 2017/218 on 31 December of the reporting year, and vessels that do not appear on the Register at that date but have fished at least one day during the reporting year."
        ]
      ]
    },
    {
      "document_id": "L_2010041EN.01000801",
      "table_id": "table_10",
      "row_ids": [
        0
      ],
      "headers": [
        "",
        "",
        "Sub regions or fishing grounds | 1",
        "Regions | 2",
        "Supra regions | 3"
      ],
      "rows": [
        [
          "Metier*Fleet segment (Cell)",
          "A",
          "A1",
          "A2",
          "A3"
        ]
      ]
    },
    {
      "document_id": "L_2010041EN.01000801",
      "table_id": "table_10",
      "row_ids": [
        2
      ],
      "headers": [
        "",
        "",
        "Sub regions or fishing grounds | 1",
        "Regions | 2",
        "Supra regions | 3"
      ],
      "rows": [
        [
          "Fleet segment",
          "C",
          "C1",
          "C2",
          "C3"
        ]
      ]
    },
    {
      "document_id": "L_2022008EN.01014201",
      "table_id": "table_28",
      "row_ids": [
        1
      ],
      "headers": null,
      "rows": [
        [
          "1. Description of clustering In cases where a fleet segment has less than 10 vessels: Clustering should be described, and information should be given on the segments that are clustered. The Member State should distinguish between segments considered for clustering as follows: Importance of fleet segments should be assessed in terms of landings (value and volume) and/or effort. Similarity should be demonstrated using expert knowledge on fishing patterns or on available data on landings and/or effort. For each of the cases described, the Member State should apply the following approaches for clustering according to the different characteristics of fleet segments: 2. Description of activity indicator If the Member State is using an activity indicator to divide the fleet segment into different activity levels, use ‘L’ for the low activity vessels and ‘A’ for the normal economic activity vessels. Please provide a description of the activity methodology used. 3. Deviation from the RCG ECON (ex. PGECON) definitions Describe and justify any deviations from variable definitions as listed in the ‘EU MAP Guidance Document’ on the DCF website. In case the PIM is not used, explain and justify the application of alternative methods. (max. 900 words)"
        ]
      ]
    },
    {
      "document_id": "L_2010041EN.01000801",
      "table_id": "table_10",
      "row_ids": [
        1
      ],
      "headers": [
        "",
        "",
        "Sub regions or fishing grounds | 1",
        "Regions | 2",
        "Supra regions | 3"
      ],
      "rows": [
        [
          "Metier",
          "B",
          "B1",
          "B2",
          "B3"
        ]
      ]
    }
  ],
  "retrieval_call_status": "success",
  "review": {
    "case_id": "global_natural_020",
    "decision": "revise",
    "final_question": "In L_2010041EN.01000801 table_10, how does the table distinguish Metier*Fleet segment (Cell), Metier, and Fleet segment across the displayed geographic aggregation levels?",
    "verified_reference_answer": "The table maps Metier*Fleet segment (Cell) to A / A1 / A2 / A3; Metier to B / B1 / B2 / B3; and Fleet segment to C / C1 / C2 / C3 across the displayed base, sub-region-or-fishing-ground, region and supra-region columns. The table itself does not provide a substantive interpretation of what the letter symbols mean beyond these mappings.",
    "supporting_quote": "Metier*Fleet segment (Cell) | A | A1 | A2 | A3; Metier | B | B1 | B2 | B3; Fleet segment | C | C1 | C2 | C3",
    "expected_source_keys": [
      "L_2010041EN.01000801 / table_10"
    ],
    "retrieval_label": "sufficient",
    "helpful_retrieved_source_keys": [
      "L_2010041EN.01000801 / table_10"
    ],
    "scope_date_version_caveats": "Do not infer substantive meaning for A/B/C or numbered variants beyond the table's displayed mappings. Question is made table-specific for reproducibility.",
    "confidence": "high",
    "review_notes": "The three expected rows were recovered as table evidence; sufficient."
  },
  "reference_answer": "The table maps Metier*Fleet segment (Cell) to A / A1 / A2 / A3; Metier to B / B1 / B2 / B3; and Fleet segment to C / C1 / C2 / C3 across the displayed base, sub-region-or-fishing-ground, region and supra-region columns. The table itself does not provide a substantive interpretation of what the letter symbols mean beyond these mappings.",
  "label_origin": "ChatGPT AI-assisted adjudication",
  "quote_matches": [
    "structured_table_requires_row_check"
  ],
  "question_revision_pending": true,
  "expert_validated": false,
  "system_QA_outcome": null
}
```

## NLI family interim_ip

```json
[
  {
    "pair_id": "legal_nli_002",
    "family_id": "interim_ip",
    "source_document_id": "L_2008289EN.01000101",
    "source_chunk_id": "chunk_48",
    "premise": "At an applicant's request, judicial authorities may issue an interlocutory injunction to prevent an imminent intellectual-property infringement, provisionally forbid continuation, or require guarantees for compensation. An injunction may also be issued against an intermediary whose services are used by a third party to infringe an intellectual-property right.",
    "hypothesis": "Court fees for an injunction application are EUR 100.",
    "premise_kind": "Codex paraphrase; source grounding requires review",
    "hypothesis_kind": "synthetic diagnostic proposition; not a claim of actual law",
    "scope_assumption": "Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.",
    "proposed_label": "neutral",
    "label_origin": "ChatGPT AI-assisted adjudication",
    "adjudicated_label": "neutral",
    "review_status": "AI_adjudicated",
    "split": "locked_test",
    "source_excerpt": "1. The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.\n2. An interlocutory injunction may also be issued to order the seizure or delivery up of the goods suspected of infringing an intellectual property right so as to prevent their entry into or movement within channels of commerce.\n3. In the case of an infringement committed on a commercial scale, the EC Party and the Signatory CARIFORUM States shall ensure that, if the applicant demonstrates circumstances likely to endanger the recovery of damages, the judicial authorities may order the precautionary seizure of the movable and immovable property of the alleged infringer, including the blocking of his/her bank accounts and other assets. To that end, the competent authorities may order the communication of bank, financial or commercial documents, or appropriate access to the relevant information.\nArticle 157\nCorrective measures\n1. The EC Party and the Signatory CARIFORUM States shall ensure that the competent judicial authorities may order, at the request of the applicant and without prejudice to any damages due to the right holder by reason of the infringement, and without compensation of any sort, the recall, definitive removal from channels of commerce or destruction of goods that they have found to be infringing an intellectual property right.\n2. The EC Party and the Signatory CARIFORUM States shall ensure that those measures are carried out at the expense of the infringer, unless particular reasons are invoked for not doing so.\nArticle 158\nInjunctions\nThe EC Party and the Signatory CARIFORUM States shall ensure that, where a judicial decision is taken finding an infringement of an intellectual property right, the judicial authorities may issue against the infringer an injunction aimed at prohibiting the continuation of the infringement. Where provided for by national law, non-compliance with an injunction shall, where appropriate, be subject to a recurring penalty payment, with a view to ensuring compliance. The EC Party and the Signatory CARIFORUM States shall also ensure that right holders are in a position to apply for an injunction against intermediaries whose services are used by a third party to infringe an intellectual property right.\nArticle 159\nAlternative measures\nThe EC Party and the Signatory CARIFORUM States may provide that, in appropriate cases and at the request of the person liable to be subject to the measures provided for in Part III of the TRIPS Agreement and in this Chapter, the competent judicial authorities may order pecuniary compensation to be paid to the injured party instead of applying the measures provided for in Part III of the TRIPS Agreement or in this Chapter if that person acted unintentionally and without negligence, if execution of the measures in question would cause him disproportionate harm and if pecuniary compensation to the injured party appears reasonably satisfactory.\nArticle 160\nDamages\n1. The EC Party and the Signatory CARIFORUM States shall ensure that when the judicial authorities set the damages:\n(a) they shall take into account all appropriate aspects, such as the negative economic consequences, including lost profits, which the injured party has suffered, any unfair profits made by the infringer and, in appropriate cases, elements other than economic factors; or (b) as an alternative to (a), they may, in appropriate cases, set the damages as a lump sum on the basis of elements such as at least the amount of royalties or fees which would have been due if the infringer had requested authorisation to use the intellectual property right in question.\n1. Where the infringer did not know, or did not have reasonable grounds to know, that he, she or it was engaging in infringing activity, the EC Party and the Signatory CARIFORUM States may provide that the judicial authorities may order the recovery of profits or the payment of damages which may be pre-established.\nArticle 161\nLegal costs\nThe EC Party and the Signatory CARIFORUM States shall ensure that their domestic law contains measures for the allocation of costs which generally require that the unsuccessful party will bear the costs, unless equity requires that costs be allocated otherwise.\nArticle 162\nPublication of judicial decisions",
    "difficulty_tag": "unstated_actor_time_or_extra_duty",
    "rationale": "Check against the entire premise and source, not lexical overlap.",
    "reviewer_notes": "",
    "review": {
      "pair_id": "legal_nli_002",
      "premise_supported": true,
      "label": "neutral",
      "confidence": 0.98,
      "rationale": "The rule permits applicant-requested interlocutory injunctions for imminent infringement, provisional continuation restrictions/guarantees, and injunctions against qualifying intermediaries. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.",
      "exact_supporting_quote": "The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.",
      "scope_correction": "Clarify that the guarantee language makes continuation of the alleged infringement subject to lodging guarantees intended to compensate the right holder if infringement is determined; the judicial authority 'may' issue the measure.",
      "source_key": "L_2008289EN.01000101 / chunk_48",
      "batch": "NLI_BATCH_1.md"
    },
    "quote_match": "contiguous_normalized",
    "scope_correction_pending": true,
    "expert_validated": false,
    "confidence_is_calibrated_probability": false
  },
  {
    "pair_id": "legal_nli_025",
    "family_id": "interim_ip",
    "source_document_id": "L_2008289EN.01000101",
    "source_chunk_id": "chunk_48",
    "premise": "At an applicant's request, judicial authorities may issue an interlocutory injunction to prevent an imminent intellectual-property infringement, provisionally forbid continuation, or require guarantees for compensation. An injunction may also be issued against an intermediary whose services are used by a third party to infringe an intellectual-property right.",
    "hypothesis": "The described interim measures can make continuation subject to compensation guarantees.",
    "premise_kind": "Codex paraphrase; source grounding requires review",
    "hypothesis_kind": "synthetic diagnostic proposition; not a claim of actual law",
    "scope_assumption": "Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.",
    "proposed_label": "entailment",
    "label_origin": "ChatGPT AI-assisted adjudication",
    "adjudicated_label": "entailment",
    "review_status": "AI_adjudicated",
    "split": "locked_test",
    "source_excerpt": "1. The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.\n2. An interlocutory injunction may also be issued to order the seizure or delivery up of the goods suspected of infringing an intellectual property right so as to prevent their entry into or movement within channels of commerce.\n3. In the case of an infringement committed on a commercial scale, the EC Party and the Signatory CARIFORUM States shall ensure that, if the applicant demonstrates circumstances likely to endanger the recovery of damages, the judicial authorities may order the precautionary seizure of the movable and immovable property of the alleged infringer, including the blocking of his/her bank accounts and other assets. To that end, the competent authorities may order the communication of bank, financial or commercial documents, or appropriate access to the relevant information.\nArticle 157\nCorrective measures\n1. The EC Party and the Signatory CARIFORUM States shall ensure that the competent judicial authorities may order, at the request of the applicant and without prejudice to any damages due to the right holder by reason of the infringement, and without compensation of any sort, the recall, definitive removal from channels of commerce or destruction of goods that they have found to be infringing an intellectual property right.\n2. The EC Party and the Signatory CARIFORUM States shall ensure that those measures are carried out at the expense of the infringer, unless particular reasons are invoked for not doing so.\nArticle 158\nInjunctions\nThe EC Party and the Signatory CARIFORUM States shall ensure that, where a judicial decision is taken finding an infringement of an intellectual property right, the judicial authorities may issue against the infringer an injunction aimed at prohibiting the continuation of the infringement. Where provided for by national law, non-compliance with an injunction shall, where appropriate, be subject to a recurring penalty payment, with a view to ensuring compliance. The EC Party and the Signatory CARIFORUM States shall also ensure that right holders are in a position to apply for an injunction against intermediaries whose services are used by a third party to infringe an intellectual property right.\nArticle 159\nAlternative measures\nThe EC Party and the Signatory CARIFORUM States may provide that, in appropriate cases and at the request of the person liable to be subject to the measures provided for in Part III of the TRIPS Agreement and in this Chapter, the competent judicial authorities may order pecuniary compensation to be paid to the injured party instead of applying the measures provided for in Part III of the TRIPS Agreement or in this Chapter if that person acted unintentionally and without negligence, if execution of the measures in question would cause him disproportionate harm and if pecuniary compensation to the injured party appears reasonably satisfactory.\nArticle 160\nDamages\n1. The EC Party and the Signatory CARIFORUM States shall ensure that when the judicial authorities set the damages:\n(a) they shall take into account all appropriate aspects, such as the negative economic consequences, including lost profits, which the injured party has suffered, any unfair profits made by the infringer and, in appropriate cases, elements other than economic factors; or (b) as an alternative to (a), they may, in appropriate cases, set the damages as a lump sum on the basis of elements such as at least the amount of royalties or fees which would have been due if the infringer had requested authorisation to use the intellectual property right in question.\n1. Where the infringer did not know, or did not have reasonable grounds to know, that he, she or it was engaging in infringing activity, the EC Party and the Signatory CARIFORUM States may provide that the judicial authorities may order the recovery of profits or the payment of damages which may be pre-established.\nArticle 161\nLegal costs\nThe EC Party and the Signatory CARIFORUM States shall ensure that their domestic law contains measures for the allocation of costs which generally require that the unsuccessful party will bear the costs, unless equity requires that costs be allocated otherwise.\nArticle 162\nPublication of judicial decisions",
    "difficulty_tag": "modality_conditions_scope",
    "rationale": "Check against the entire premise and source, not lexical overlap.",
    "reviewer_notes": "",
    "review": {
      "pair_id": "legal_nli_025",
      "premise_supported": true,
      "label": "entailment",
      "confidence": 0.99,
      "rationale": "The rule permits applicant-requested interlocutory injunctions for imminent infringement, provisional continuation restrictions/guarantees, and injunctions against qualifying intermediaries. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.",
      "exact_supporting_quote": "The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.",
      "scope_correction": "Clarify that the guarantee language makes continuation of the alleged infringement subject to lodging guarantees intended to compensate the right holder if infringement is determined; the judicial authority 'may' issue the measure.",
      "source_key": "L_2008289EN.01000101 / chunk_48",
      "batch": "NLI_BATCH_1.md"
    },
    "quote_match": "contiguous_normalized",
    "scope_correction_pending": true,
    "expert_validated": false,
    "confidence_is_calibrated_probability": false
  },
  {
    "pair_id": "legal_nli_026",
    "family_id": "interim_ip",
    "source_document_id": "L_2008289EN.01000101",
    "source_chunk_id": "chunk_48",
    "premise": "At an applicant's request, judicial authorities may issue an interlocutory injunction to prevent an imminent intellectual-property infringement, provisionally forbid continuation, or require guarantees for compensation. An injunction may also be issued against an intermediary whose services are used by a third party to infringe an intellectual-property right.",
    "hypothesis": "Judicial authorities are prohibited from issuing an interlocutory injunction to prevent an imminent infringement.",
    "premise_kind": "Codex paraphrase; source grounding requires review",
    "hypothesis_kind": "synthetic diagnostic proposition; not a claim of actual law",
    "scope_assumption": "Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.",
    "proposed_label": "contradiction",
    "label_origin": "ChatGPT AI-assisted adjudication",
    "adjudicated_label": "contradiction",
    "review_status": "AI_adjudicated",
    "split": "locked_test",
    "source_excerpt": "1. The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.\n2. An interlocutory injunction may also be issued to order the seizure or delivery up of the goods suspected of infringing an intellectual property right so as to prevent their entry into or movement within channels of commerce.\n3. In the case of an infringement committed on a commercial scale, the EC Party and the Signatory CARIFORUM States shall ensure that, if the applicant demonstrates circumstances likely to endanger the recovery of damages, the judicial authorities may order the precautionary seizure of the movable and immovable property of the alleged infringer, including the blocking of his/her bank accounts and other assets. To that end, the competent authorities may order the communication of bank, financial or commercial documents, or appropriate access to the relevant information.\nArticle 157\nCorrective measures\n1. The EC Party and the Signatory CARIFORUM States shall ensure that the competent judicial authorities may order, at the request of the applicant and without prejudice to any damages due to the right holder by reason of the infringement, and without compensation of any sort, the recall, definitive removal from channels of commerce or destruction of goods that they have found to be infringing an intellectual property right.\n2. The EC Party and the Signatory CARIFORUM States shall ensure that those measures are carried out at the expense of the infringer, unless particular reasons are invoked for not doing so.\nArticle 158\nInjunctions\nThe EC Party and the Signatory CARIFORUM States shall ensure that, where a judicial decision is taken finding an infringement of an intellectual property right, the judicial authorities may issue against the infringer an injunction aimed at prohibiting the continuation of the infringement. Where provided for by national law, non-compliance with an injunction shall, where appropriate, be subject to a recurring penalty payment, with a view to ensuring compliance. The EC Party and the Signatory CARIFORUM States shall also ensure that right holders are in a position to apply for an injunction against intermediaries whose services are used by a third party to infringe an intellectual property right.\nArticle 159\nAlternative measures\nThe EC Party and the Signatory CARIFORUM States may provide that, in appropriate cases and at the request of the person liable to be subject to the measures provided for in Part III of the TRIPS Agreement and in this Chapter, the competent judicial authorities may order pecuniary compensation to be paid to the injured party instead of applying the measures provided for in Part III of the TRIPS Agreement or in this Chapter if that person acted unintentionally and without negligence, if execution of the measures in question would cause him disproportionate harm and if pecuniary compensation to the injured party appears reasonably satisfactory.\nArticle 160\nDamages\n1. The EC Party and the Signatory CARIFORUM States shall ensure that when the judicial authorities set the damages:\n(a) they shall take into account all appropriate aspects, such as the negative economic consequences, including lost profits, which the injured party has suffered, any unfair profits made by the infringer and, in appropriate cases, elements other than economic factors; or (b) as an alternative to (a), they may, in appropriate cases, set the damages as a lump sum on the basis of elements such as at least the amount of royalties or fees which would have been due if the infringer had requested authorisation to use the intellectual property right in question.\n1. Where the infringer did not know, or did not have reasonable grounds to know, that he, she or it was engaging in infringing activity, the EC Party and the Signatory CARIFORUM States may provide that the judicial authorities may order the recovery of profits or the payment of damages which may be pre-established.\nArticle 161\nLegal costs\nThe EC Party and the Signatory CARIFORUM States shall ensure that their domestic law contains measures for the allocation of costs which generally require that the unsuccessful party will bear the costs, unless equity requires that costs be allocated otherwise.\nArticle 162\nPublication of judicial decisions",
    "difficulty_tag": "modality_conditions_scope",
    "rationale": "Check against the entire premise and source, not lexical overlap.",
    "reviewer_notes": "",
    "review": {
      "pair_id": "legal_nli_026",
      "premise_supported": true,
      "label": "contradiction",
      "confidence": 0.99,
      "rationale": "The rule permits applicant-requested interlocutory injunctions for imminent infringement, provisional continuation restrictions/guarantees, and injunctions against qualifying intermediaries. The hypothesis reverses, excludes, or violates an express condition of the premise.",
      "exact_supporting_quote": "The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.",
      "scope_correction": "Clarify that the guarantee language makes continuation of the alleged infringement subject to lodging guarantees intended to compensate the right holder if infringement is determined; the judicial authority 'may' issue the measure.",
      "source_key": "L_2008289EN.01000101 / chunk_48",
      "batch": "NLI_BATCH_1.md"
    },
    "quote_match": "contiguous_normalized",
    "scope_correction_pending": true,
    "expert_validated": false,
    "confidence_is_calibrated_probability": false
  },
  {
    "pair_id": "legal_nli_028",
    "family_id": "interim_ip",
    "source_document_id": "L_2008289EN.01000101",
    "source_chunk_id": "chunk_48",
    "premise": "At an applicant's request, judicial authorities may issue an interlocutory injunction to prevent an imminent intellectual-property infringement, provisionally forbid continuation, or require guarantees for compensation. An injunction may also be issued against an intermediary whose services are used by a third party to infringe an intellectual-property right.",
    "hypothesis": "The stated measures exclude making continuation subject to compensation guarantees.",
    "premise_kind": "Codex paraphrase; source grounding requires review",
    "hypothesis_kind": "synthetic diagnostic proposition; not a claim of actual law",
    "scope_assumption": "Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.",
    "proposed_label": "contradiction",
    "label_origin": "ChatGPT AI-assisted adjudication",
    "adjudicated_label": "contradiction",
    "review_status": "AI_adjudicated",
    "split": "locked_test",
    "source_excerpt": "1. The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.\n2. An interlocutory injunction may also be issued to order the seizure or delivery up of the goods suspected of infringing an intellectual property right so as to prevent their entry into or movement within channels of commerce.\n3. In the case of an infringement committed on a commercial scale, the EC Party and the Signatory CARIFORUM States shall ensure that, if the applicant demonstrates circumstances likely to endanger the recovery of damages, the judicial authorities may order the precautionary seizure of the movable and immovable property of the alleged infringer, including the blocking of his/her bank accounts and other assets. To that end, the competent authorities may order the communication of bank, financial or commercial documents, or appropriate access to the relevant information.\nArticle 157\nCorrective measures\n1. The EC Party and the Signatory CARIFORUM States shall ensure that the competent judicial authorities may order, at the request of the applicant and without prejudice to any damages due to the right holder by reason of the infringement, and without compensation of any sort, the recall, definitive removal from channels of commerce or destruction of goods that they have found to be infringing an intellectual property right.\n2. The EC Party and the Signatory CARIFORUM States shall ensure that those measures are carried out at the expense of the infringer, unless particular reasons are invoked for not doing so.\nArticle 158\nInjunctions\nThe EC Party and the Signatory CARIFORUM States shall ensure that, where a judicial decision is taken finding an infringement of an intellectual property right, the judicial authorities may issue against the infringer an injunction aimed at prohibiting the continuation of the infringement. Where provided for by national law, non-compliance with an injunction shall, where appropriate, be subject to a recurring penalty payment, with a view to ensuring compliance. The EC Party and the Signatory CARIFORUM States shall also ensure that right holders are in a position to apply for an injunction against intermediaries whose services are used by a third party to infringe an intellectual property right.\nArticle 159\nAlternative measures\nThe EC Party and the Signatory CARIFORUM States may provide that, in appropriate cases and at the request of the person liable to be subject to the measures provided for in Part III of the TRIPS Agreement and in this Chapter, the competent judicial authorities may order pecuniary compensation to be paid to the injured party instead of applying the measures provided for in Part III of the TRIPS Agreement or in this Chapter if that person acted unintentionally and without negligence, if execution of the measures in question would cause him disproportionate harm and if pecuniary compensation to the injured party appears reasonably satisfactory.\nArticle 160\nDamages\n1. The EC Party and the Signatory CARIFORUM States shall ensure that when the judicial authorities set the damages:\n(a) they shall take into account all appropriate aspects, such as the negative economic consequences, including lost profits, which the injured party has suffered, any unfair profits made by the infringer and, in appropriate cases, elements other than economic factors; or (b) as an alternative to (a), they may, in appropriate cases, set the damages as a lump sum on the basis of elements such as at least the amount of royalties or fees which would have been due if the infringer had requested authorisation to use the intellectual property right in question.\n1. Where the infringer did not know, or did not have reasonable grounds to know, that he, she or it was engaging in infringing activity, the EC Party and the Signatory CARIFORUM States may provide that the judicial authorities may order the recovery of profits or the payment of damages which may be pre-established.\nArticle 161\nLegal costs\nThe EC Party and the Signatory CARIFORUM States shall ensure that their domestic law contains measures for the allocation of costs which generally require that the unsuccessful party will bear the costs, unless equity requires that costs be allocated otherwise.\nArticle 162\nPublication of judicial decisions",
    "difficulty_tag": "modality_conditions_scope",
    "rationale": "Check against the entire premise and source, not lexical overlap.",
    "reviewer_notes": "",
    "review": {
      "pair_id": "legal_nli_028",
      "premise_supported": true,
      "label": "contradiction",
      "confidence": 0.99,
      "rationale": "The rule permits applicant-requested interlocutory injunctions for imminent infringement, provisional continuation restrictions/guarantees, and injunctions against qualifying intermediaries. The hypothesis reverses, excludes, or violates an express condition of the premise.",
      "exact_supporting_quote": "The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.",
      "scope_correction": "Clarify that the guarantee language makes continuation of the alleged infringement subject to lodging guarantees intended to compensate the right holder if infringement is determined; the judicial authority 'may' issue the measure.",
      "source_key": "L_2008289EN.01000101 / chunk_48",
      "batch": "NLI_BATCH_1.md"
    },
    "quote_match": "contiguous_normalized",
    "scope_correction_pending": true,
    "expert_validated": false,
    "confidence_is_calibrated_probability": false
  },
  {
    "pair_id": "legal_nli_036",
    "family_id": "interim_ip",
    "source_document_id": "L_2008289EN.01000101",
    "source_chunk_id": "chunk_48",
    "premise": "At an applicant's request, judicial authorities may issue an interlocutory injunction to prevent an imminent intellectual-property infringement, provisionally forbid continuation, or require guarantees for compensation. An injunction may also be issued against an intermediary whose services are used by a third party to infringe an intellectual-property right.",
    "hypothesis": "An intermediary whose services are used for infringement can never be subject to the described injunction.",
    "premise_kind": "Codex paraphrase; source grounding requires review",
    "hypothesis_kind": "synthetic diagnostic proposition; not a claim of actual law",
    "scope_assumption": "Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.",
    "proposed_label": "contradiction",
    "label_origin": "ChatGPT AI-assisted adjudication",
    "adjudicated_label": "contradiction",
    "review_status": "AI_adjudicated",
    "split": "locked_test",
    "source_excerpt": "1. The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.\n2. An interlocutory injunction may also be issued to order the seizure or delivery up of the goods suspected of infringing an intellectual property right so as to prevent their entry into or movement within channels of commerce.\n3. In the case of an infringement committed on a commercial scale, the EC Party and the Signatory CARIFORUM States shall ensure that, if the applicant demonstrates circumstances likely to endanger the recovery of damages, the judicial authorities may order the precautionary seizure of the movable and immovable property of the alleged infringer, including the blocking of his/her bank accounts and other assets. To that end, the competent authorities may order the communication of bank, financial or commercial documents, or appropriate access to the relevant information.\nArticle 157\nCorrective measures\n1. The EC Party and the Signatory CARIFORUM States shall ensure that the competent judicial authorities may order, at the request of the applicant and without prejudice to any damages due to the right holder by reason of the infringement, and without compensation of any sort, the recall, definitive removal from channels of commerce or destruction of goods that they have found to be infringing an intellectual property right.\n2. The EC Party and the Signatory CARIFORUM States shall ensure that those measures are carried out at the expense of the infringer, unless particular reasons are invoked for not doing so.\nArticle 158\nInjunctions\nThe EC Party and the Signatory CARIFORUM States shall ensure that, where a judicial decision is taken finding an infringement of an intellectual property right, the judicial authorities may issue against the infringer an injunction aimed at prohibiting the continuation of the infringement. Where provided for by national law, non-compliance with an injunction shall, where appropriate, be subject to a recurring penalty payment, with a view to ensuring compliance. The EC Party and the Signatory CARIFORUM States shall also ensure that right holders are in a position to apply for an injunction against intermediaries whose services are used by a third party to infringe an intellectual property right.\nArticle 159\nAlternative measures\nThe EC Party and the Signatory CARIFORUM States may provide that, in appropriate cases and at the request of the person liable to be subject to the measures provided for in Part III of the TRIPS Agreement and in this Chapter, the competent judicial authorities may order pecuniary compensation to be paid to the injured party instead of applying the measures provided for in Part III of the TRIPS Agreement or in this Chapter if that person acted unintentionally and without negligence, if execution of the measures in question would cause him disproportionate harm and if pecuniary compensation to the injured party appears reasonably satisfactory.\nArticle 160\nDamages\n1. The EC Party and the Signatory CARIFORUM States shall ensure that when the judicial authorities set the damages:\n(a) they shall take into account all appropriate aspects, such as the negative economic consequences, including lost profits, which the injured party has suffered, any unfair profits made by the infringer and, in appropriate cases, elements other than economic factors; or (b) as an alternative to (a), they may, in appropriate cases, set the damages as a lump sum on the basis of elements such as at least the amount of royalties or fees which would have been due if the infringer had requested authorisation to use the intellectual property right in question.\n1. Where the infringer did not know, or did not have reasonable grounds to know, that he, she or it was engaging in infringing activity, the EC Party and the Signatory CARIFORUM States may provide that the judicial authorities may order the recovery of profits or the payment of damages which may be pre-established.\nArticle 161\nLegal costs\nThe EC Party and the Signatory CARIFORUM States shall ensure that their domestic law contains measures for the allocation of costs which generally require that the unsuccessful party will bear the costs, unless equity requires that costs be allocated otherwise.\nArticle 162\nPublication of judicial decisions",
    "difficulty_tag": "modality_conditions_scope",
    "rationale": "Check against the entire premise and source, not lexical overlap.",
    "reviewer_notes": "",
    "review": {
      "pair_id": "legal_nli_036",
      "premise_supported": true,
      "label": "contradiction",
      "confidence": 0.99,
      "rationale": "The rule permits applicant-requested interlocutory injunctions for imminent infringement, provisional continuation restrictions/guarantees, and injunctions against qualifying intermediaries. The hypothesis reverses, excludes, or violates an express condition of the premise.",
      "exact_supporting_quote": "The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.",
      "scope_correction": "Clarify that the guarantee language makes continuation of the alleged infringement subject to lodging guarantees intended to compensate the right holder if infringement is determined; the judicial authority 'may' issue the measure.",
      "source_key": "L_2008289EN.01000101 / chunk_48",
      "batch": "NLI_BATCH_2.md"
    },
    "quote_match": "contiguous_normalized",
    "scope_correction_pending": true,
    "expert_validated": false,
    "confidence_is_calibrated_probability": false
  },
  {
    "pair_id": "legal_nli_048",
    "family_id": "interim_ip",
    "source_document_id": "L_2008289EN.01000101",
    "source_chunk_id": "chunk_48",
    "premise": "At an applicant's request, judicial authorities may issue an interlocutory injunction to prevent an imminent intellectual-property infringement, provisionally forbid continuation, or require guarantees for compensation. An injunction may also be issued against an intermediary whose services are used by a third party to infringe an intellectual-property right.",
    "hypothesis": "An applicant automatically receives damages when requesting an injunction.",
    "premise_kind": "Codex paraphrase; source grounding requires review",
    "hypothesis_kind": "synthetic diagnostic proposition; not a claim of actual law",
    "scope_assumption": "Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.",
    "proposed_label": "neutral",
    "label_origin": "ChatGPT AI-assisted adjudication",
    "adjudicated_label": "neutral",
    "review_status": "AI_adjudicated",
    "split": "locked_test",
    "source_excerpt": "1. The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.\n2. An interlocutory injunction may also be issued to order the seizure or delivery up of the goods suspected of infringing an intellectual property right so as to prevent their entry into or movement within channels of commerce.\n3. In the case of an infringement committed on a commercial scale, the EC Party and the Signatory CARIFORUM States shall ensure that, if the applicant demonstrates circumstances likely to endanger the recovery of damages, the judicial authorities may order the precautionary seizure of the movable and immovable property of the alleged infringer, including the blocking of his/her bank accounts and other assets. To that end, the competent authorities may order the communication of bank, financial or commercial documents, or appropriate access to the relevant information.\nArticle 157\nCorrective measures\n1. The EC Party and the Signatory CARIFORUM States shall ensure that the competent judicial authorities may order, at the request of the applicant and without prejudice to any damages due to the right holder by reason of the infringement, and without compensation of any sort, the recall, definitive removal from channels of commerce or destruction of goods that they have found to be infringing an intellectual property right.\n2. The EC Party and the Signatory CARIFORUM States shall ensure that those measures are carried out at the expense of the infringer, unless particular reasons are invoked for not doing so.\nArticle 158\nInjunctions\nThe EC Party and the Signatory CARIFORUM States shall ensure that, where a judicial decision is taken finding an infringement of an intellectual property right, the judicial authorities may issue against the infringer an injunction aimed at prohibiting the continuation of the infringement. Where provided for by national law, non-compliance with an injunction shall, where appropriate, be subject to a recurring penalty payment, with a view to ensuring compliance. The EC Party and the Signatory CARIFORUM States shall also ensure that right holders are in a position to apply for an injunction against intermediaries whose services are used by a third party to infringe an intellectual property right.\nArticle 159\nAlternative measures\nThe EC Party and the Signatory CARIFORUM States may provide that, in appropriate cases and at the request of the person liable to be subject to the measures provided for in Part III of the TRIPS Agreement and in this Chapter, the competent judicial authorities may order pecuniary compensation to be paid to the injured party instead of applying the measures provided for in Part III of the TRIPS Agreement or in this Chapter if that person acted unintentionally and without negligence, if execution of the measures in question would cause him disproportionate harm and if pecuniary compensation to the injured party appears reasonably satisfactory.\nArticle 160\nDamages\n1. The EC Party and the Signatory CARIFORUM States shall ensure that when the judicial authorities set the damages:\n(a) they shall take into account all appropriate aspects, such as the negative economic consequences, including lost profits, which the injured party has suffered, any unfair profits made by the infringer and, in appropriate cases, elements other than economic factors; or (b) as an alternative to (a), they may, in appropriate cases, set the damages as a lump sum on the basis of elements such as at least the amount of royalties or fees which would have been due if the infringer had requested authorisation to use the intellectual property right in question.\n1. Where the infringer did not know, or did not have reasonable grounds to know, that he, she or it was engaging in infringing activity, the EC Party and the Signatory CARIFORUM States may provide that the judicial authorities may order the recovery of profits or the payment of damages which may be pre-established.\nArticle 161\nLegal costs\nThe EC Party and the Signatory CARIFORUM States shall ensure that their domestic law contains measures for the allocation of costs which generally require that the unsuccessful party will bear the costs, unless equity requires that costs be allocated otherwise.\nArticle 162\nPublication of judicial decisions",
    "difficulty_tag": "unstated_actor_time_or_extra_duty",
    "rationale": "Check against the entire premise and source, not lexical overlap.",
    "reviewer_notes": "",
    "review": {
      "pair_id": "legal_nli_048",
      "premise_supported": true,
      "label": "neutral",
      "confidence": 0.98,
      "rationale": "The rule permits applicant-requested interlocutory injunctions for imminent infringement, provisional continuation restrictions/guarantees, and injunctions against qualifying intermediaries. The hypothesis introduces an additional fee, duty, date, location, equipment/origin restriction, compensation/refund, licensing rule, appeal right, or other fact absent from the premise; it is neutral.",
      "exact_supporting_quote": "The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.",
      "scope_correction": "Clarify that the guarantee language makes continuation of the alleged infringement subject to lodging guarantees intended to compensate the right holder if infringement is determined; the judicial authority 'may' issue the measure.",
      "source_key": "L_2008289EN.01000101 / chunk_48",
      "batch": "NLI_BATCH_2.md"
    },
    "quote_match": "contiguous_normalized",
    "scope_correction_pending": true,
    "expert_validated": false,
    "confidence_is_calibrated_probability": false
  },
  {
    "pair_id": "legal_nli_049",
    "family_id": "interim_ip",
    "source_document_id": "L_2008289EN.01000101",
    "source_chunk_id": "chunk_48",
    "premise": "At an applicant's request, judicial authorities may issue an interlocutory injunction to prevent an imminent intellectual-property infringement, provisionally forbid continuation, or require guarantees for compensation. An injunction may also be issued against an intermediary whose services are used by a third party to infringe an intellectual-property right.",
    "hypothesis": "Preventing an imminent infringement is a permitted purpose of an interlocutory injunction.",
    "premise_kind": "Codex paraphrase; source grounding requires review",
    "hypothesis_kind": "synthetic diagnostic proposition; not a claim of actual law",
    "scope_assumption": "Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.",
    "proposed_label": "entailment",
    "label_origin": "ChatGPT AI-assisted adjudication",
    "adjudicated_label": "entailment",
    "review_status": "AI_adjudicated",
    "split": "locked_test",
    "source_excerpt": "1. The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.\n2. An interlocutory injunction may also be issued to order the seizure or delivery up of the goods suspected of infringing an intellectual property right so as to prevent their entry into or movement within channels of commerce.\n3. In the case of an infringement committed on a commercial scale, the EC Party and the Signatory CARIFORUM States shall ensure that, if the applicant demonstrates circumstances likely to endanger the recovery of damages, the judicial authorities may order the precautionary seizure of the movable and immovable property of the alleged infringer, including the blocking of his/her bank accounts and other assets. To that end, the competent authorities may order the communication of bank, financial or commercial documents, or appropriate access to the relevant information.\nArticle 157\nCorrective measures\n1. The EC Party and the Signatory CARIFORUM States shall ensure that the competent judicial authorities may order, at the request of the applicant and without prejudice to any damages due to the right holder by reason of the infringement, and without compensation of any sort, the recall, definitive removal from channels of commerce or destruction of goods that they have found to be infringing an intellectual property right.\n2. The EC Party and the Signatory CARIFORUM States shall ensure that those measures are carried out at the expense of the infringer, unless particular reasons are invoked for not doing so.\nArticle 158\nInjunctions\nThe EC Party and the Signatory CARIFORUM States shall ensure that, where a judicial decision is taken finding an infringement of an intellectual property right, the judicial authorities may issue against the infringer an injunction aimed at prohibiting the continuation of the infringement. Where provided for by national law, non-compliance with an injunction shall, where appropriate, be subject to a recurring penalty payment, with a view to ensuring compliance. The EC Party and the Signatory CARIFORUM States shall also ensure that right holders are in a position to apply for an injunction against intermediaries whose services are used by a third party to infringe an intellectual property right.\nArticle 159\nAlternative measures\nThe EC Party and the Signatory CARIFORUM States may provide that, in appropriate cases and at the request of the person liable to be subject to the measures provided for in Part III of the TRIPS Agreement and in this Chapter, the competent judicial authorities may order pecuniary compensation to be paid to the injured party instead of applying the measures provided for in Part III of the TRIPS Agreement or in this Chapter if that person acted unintentionally and without negligence, if execution of the measures in question would cause him disproportionate harm and if pecuniary compensation to the injured party appears reasonably satisfactory.\nArticle 160\nDamages\n1. The EC Party and the Signatory CARIFORUM States shall ensure that when the judicial authorities set the damages:\n(a) they shall take into account all appropriate aspects, such as the negative economic consequences, including lost profits, which the injured party has suffered, any unfair profits made by the infringer and, in appropriate cases, elements other than economic factors; or (b) as an alternative to (a), they may, in appropriate cases, set the damages as a lump sum on the basis of elements such as at least the amount of royalties or fees which would have been due if the infringer had requested authorisation to use the intellectual property right in question.\n1. Where the infringer did not know, or did not have reasonable grounds to know, that he, she or it was engaging in infringing activity, the EC Party and the Signatory CARIFORUM States may provide that the judicial authorities may order the recovery of profits or the payment of damages which may be pre-established.\nArticle 161\nLegal costs\nThe EC Party and the Signatory CARIFORUM States shall ensure that their domestic law contains measures for the allocation of costs which generally require that the unsuccessful party will bear the costs, unless equity requires that costs be allocated otherwise.\nArticle 162\nPublication of judicial decisions",
    "difficulty_tag": "modality_conditions_scope",
    "rationale": "Check against the entire premise and source, not lexical overlap.",
    "reviewer_notes": "",
    "review": {
      "pair_id": "legal_nli_049",
      "premise_supported": true,
      "label": "entailment",
      "confidence": 0.99,
      "rationale": "The rule permits applicant-requested interlocutory injunctions for imminent infringement, provisional continuation restrictions/guarantees, and injunctions against qualifying intermediaries. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.",
      "exact_supporting_quote": "The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.",
      "scope_correction": "Clarify that the guarantee language makes continuation of the alleged infringement subject to lodging guarantees intended to compensate the right holder if infringement is determined; the judicial authority 'may' issue the measure.",
      "source_key": "L_2008289EN.01000101 / chunk_48",
      "batch": "NLI_BATCH_2.md"
    },
    "quote_match": "contiguous_normalized",
    "scope_correction_pending": true,
    "expert_validated": false,
    "confidence_is_calibrated_probability": false
  },
  {
    "pair_id": "legal_nli_060",
    "family_id": "interim_ip",
    "source_document_id": "L_2008289EN.01000101",
    "source_chunk_id": "chunk_48",
    "premise": "At an applicant's request, judicial authorities may issue an interlocutory injunction to prevent an imminent intellectual-property infringement, provisionally forbid continuation, or require guarantees for compensation. An injunction may also be issued against an intermediary whose services are used by a third party to infringe an intellectual-property right.",
    "hypothesis": "Judicial authorities must grant every application for an interlocutory injunction.",
    "premise_kind": "Codex paraphrase; source grounding requires review",
    "hypothesis_kind": "synthetic diagnostic proposition; not a claim of actual law",
    "scope_assumption": "Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.",
    "proposed_label": "neutral",
    "label_origin": "ChatGPT AI-assisted adjudication",
    "adjudicated_label": "neutral",
    "review_status": "AI_adjudicated",
    "split": "locked_test",
    "source_excerpt": "1. The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.\n2. An interlocutory injunction may also be issued to order the seizure or delivery up of the goods suspected of infringing an intellectual property right so as to prevent their entry into or movement within channels of commerce.\n3. In the case of an infringement committed on a commercial scale, the EC Party and the Signatory CARIFORUM States shall ensure that, if the applicant demonstrates circumstances likely to endanger the recovery of damages, the judicial authorities may order the precautionary seizure of the movable and immovable property of the alleged infringer, including the blocking of his/her bank accounts and other assets. To that end, the competent authorities may order the communication of bank, financial or commercial documents, or appropriate access to the relevant information.\nArticle 157\nCorrective measures\n1. The EC Party and the Signatory CARIFORUM States shall ensure that the competent judicial authorities may order, at the request of the applicant and without prejudice to any damages due to the right holder by reason of the infringement, and without compensation of any sort, the recall, definitive removal from channels of commerce or destruction of goods that they have found to be infringing an intellectual property right.\n2. The EC Party and the Signatory CARIFORUM States shall ensure that those measures are carried out at the expense of the infringer, unless particular reasons are invoked for not doing so.\nArticle 158\nInjunctions\nThe EC Party and the Signatory CARIFORUM States shall ensure that, where a judicial decision is taken finding an infringement of an intellectual property right, the judicial authorities may issue against the infringer an injunction aimed at prohibiting the continuation of the infringement. Where provided for by national law, non-compliance with an injunction shall, where appropriate, be subject to a recurring penalty payment, with a view to ensuring compliance. The EC Party and the Signatory CARIFORUM States shall also ensure that right holders are in a position to apply for an injunction against intermediaries whose services are used by a third party to infringe an intellectual property right.\nArticle 159\nAlternative measures\nThe EC Party and the Signatory CARIFORUM States may provide that, in appropriate cases and at the request of the person liable to be subject to the measures provided for in Part III of the TRIPS Agreement and in this Chapter, the competent judicial authorities may order pecuniary compensation to be paid to the injured party instead of applying the measures provided for in Part III of the TRIPS Agreement or in this Chapter if that person acted unintentionally and without negligence, if execution of the measures in question would cause him disproportionate harm and if pecuniary compensation to the injured party appears reasonably satisfactory.\nArticle 160\nDamages\n1. The EC Party and the Signatory CARIFORUM States shall ensure that when the judicial authorities set the damages:\n(a) they shall take into account all appropriate aspects, such as the negative economic consequences, including lost profits, which the injured party has suffered, any unfair profits made by the infringer and, in appropriate cases, elements other than economic factors; or (b) as an alternative to (a), they may, in appropriate cases, set the damages as a lump sum on the basis of elements such as at least the amount of royalties or fees which would have been due if the infringer had requested authorisation to use the intellectual property right in question.\n1. Where the infringer did not know, or did not have reasonable grounds to know, that he, she or it was engaging in infringing activity, the EC Party and the Signatory CARIFORUM States may provide that the judicial authorities may order the recovery of profits or the payment of damages which may be pre-established.\nArticle 161\nLegal costs\nThe EC Party and the Signatory CARIFORUM States shall ensure that their domestic law contains measures for the allocation of costs which generally require that the unsuccessful party will bear the costs, unless equity requires that costs be allocated otherwise.\nArticle 162\nPublication of judicial decisions",
    "difficulty_tag": "unstated_actor_time_or_extra_duty",
    "rationale": "Check against the entire premise and source, not lexical overlap.",
    "reviewer_notes": "",
    "review": {
      "pair_id": "legal_nli_060",
      "premise_supported": true,
      "label": "neutral",
      "confidence": 0.95,
      "rationale": "The premise says judicial authorities may issue the interlocutory injunction. Permission does not entail a duty to grant every application, but the premise alone also does not expressly negate every possible mandatory rule. The stronger 'must grant every application' claim is therefore neutral.",
      "exact_supporting_quote": "The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.",
      "scope_correction": "Clarify that the guarantee language makes continuation of the alleged infringement subject to lodging guarantees intended to compensate the right holder if infringement is determined; the judicial authority 'may' issue the measure.",
      "source_key": "L_2008289EN.01000101 / chunk_48",
      "batch": "NLI_BATCH_2.md"
    },
    "quote_match": "contiguous_normalized",
    "scope_correction_pending": true,
    "expert_validated": false,
    "confidence_is_calibrated_probability": false
  },
  {
    "pair_id": "legal_nli_074",
    "family_id": "interim_ip",
    "source_document_id": "L_2008289EN.01000101",
    "source_chunk_id": "chunk_48",
    "premise": "At an applicant's request, judicial authorities may issue an interlocutory injunction to prevent an imminent intellectual-property infringement, provisionally forbid continuation, or require guarantees for compensation. An injunction may also be issued against an intermediary whose services are used by a third party to infringe an intellectual-property right.",
    "hypothesis": "An intermediary whose services are used for infringement can be subject to an interlocutory injunction.",
    "premise_kind": "Codex paraphrase; source grounding requires review",
    "hypothesis_kind": "synthetic diagnostic proposition; not a claim of actual law",
    "scope_assumption": "Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.",
    "proposed_label": "entailment",
    "label_origin": "ChatGPT AI-assisted adjudication",
    "adjudicated_label": "entailment",
    "review_status": "AI_adjudicated",
    "split": "locked_test",
    "source_excerpt": "1. The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.\n2. An interlocutory injunction may also be issued to order the seizure or delivery up of the goods suspected of infringing an intellectual property right so as to prevent their entry into or movement within channels of commerce.\n3. In the case of an infringement committed on a commercial scale, the EC Party and the Signatory CARIFORUM States shall ensure that, if the applicant demonstrates circumstances likely to endanger the recovery of damages, the judicial authorities may order the precautionary seizure of the movable and immovable property of the alleged infringer, including the blocking of his/her bank accounts and other assets. To that end, the competent authorities may order the communication of bank, financial or commercial documents, or appropriate access to the relevant information.\nArticle 157\nCorrective measures\n1. The EC Party and the Signatory CARIFORUM States shall ensure that the competent judicial authorities may order, at the request of the applicant and without prejudice to any damages due to the right holder by reason of the infringement, and without compensation of any sort, the recall, definitive removal from channels of commerce or destruction of goods that they have found to be infringing an intellectual property right.\n2. The EC Party and the Signatory CARIFORUM States shall ensure that those measures are carried out at the expense of the infringer, unless particular reasons are invoked for not doing so.\nArticle 158\nInjunctions\nThe EC Party and the Signatory CARIFORUM States shall ensure that, where a judicial decision is taken finding an infringement of an intellectual property right, the judicial authorities may issue against the infringer an injunction aimed at prohibiting the continuation of the infringement. Where provided for by national law, non-compliance with an injunction shall, where appropriate, be subject to a recurring penalty payment, with a view to ensuring compliance. The EC Party and the Signatory CARIFORUM States shall also ensure that right holders are in a position to apply for an injunction against intermediaries whose services are used by a third party to infringe an intellectual property right.\nArticle 159\nAlternative measures\nThe EC Party and the Signatory CARIFORUM States may provide that, in appropriate cases and at the request of the person liable to be subject to the measures provided for in Part III of the TRIPS Agreement and in this Chapter, the competent judicial authorities may order pecuniary compensation to be paid to the injured party instead of applying the measures provided for in Part III of the TRIPS Agreement or in this Chapter if that person acted unintentionally and without negligence, if execution of the measures in question would cause him disproportionate harm and if pecuniary compensation to the injured party appears reasonably satisfactory.\nArticle 160\nDamages\n1. The EC Party and the Signatory CARIFORUM States shall ensure that when the judicial authorities set the damages:\n(a) they shall take into account all appropriate aspects, such as the negative economic consequences, including lost profits, which the injured party has suffered, any unfair profits made by the infringer and, in appropriate cases, elements other than economic factors; or (b) as an alternative to (a), they may, in appropriate cases, set the damages as a lump sum on the basis of elements such as at least the amount of royalties or fees which would have been due if the infringer had requested authorisation to use the intellectual property right in question.\n1. Where the infringer did not know, or did not have reasonable grounds to know, that he, she or it was engaging in infringing activity, the EC Party and the Signatory CARIFORUM States may provide that the judicial authorities may order the recovery of profits or the payment of damages which may be pre-established.\nArticle 161\nLegal costs\nThe EC Party and the Signatory CARIFORUM States shall ensure that their domestic law contains measures for the allocation of costs which generally require that the unsuccessful party will bear the costs, unless equity requires that costs be allocated otherwise.\nArticle 162\nPublication of judicial decisions",
    "difficulty_tag": "modality_conditions_scope",
    "rationale": "Check against the entire premise and source, not lexical overlap.",
    "reviewer_notes": "",
    "review": {
      "pair_id": "legal_nli_074",
      "premise_supported": true,
      "label": "entailment",
      "confidence": 0.99,
      "rationale": "The rule permits applicant-requested interlocutory injunctions for imminent infringement, provisional continuation restrictions/guarantees, and injunctions against qualifying intermediaries. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.",
      "exact_supporting_quote": "The EC Party and the Signatory CARIFORUM States shall ensure that the judicial authorities may, at the request of the applicant issue an interlocutory injunction intended to prevent any imminent infringement of an intellectual property right, or to forbid, on a provisional basis and subject, where appropriate, to a recurring penalty payment where provided for by national law, the continuation of the alleged infringements of that right, or to make such continuation subject to the lodging of guarantees intended to ensure the compensation of the right holder where an infringement is determined. An interlocutory injunction may also be issued, under the same conditions, against an intermediary whose services are being used by a third party to infringe an intellectual property right.",
      "scope_correction": "Clarify that the guarantee language makes continuation of the alleged infringement subject to lodging guarantees intended to compensate the right holder if infringement is determined; the judicial authority 'may' issue the measure.",
      "source_key": "L_2008289EN.01000101 / chunk_48",
      "batch": "NLI_BATCH_3.md"
    },
    "quote_match": "contiguous_normalized",
    "scope_correction_pending": true,
    "expert_validated": false,
    "confidence_is_calibrated_probability": false
  }
]
```

## NLI family tir_entry

```json
[
  {
    "pair_id": "legal_nli_007",
    "family_id": "tir_entry",
    "source_document_id": "L_2009165EN.01000101",
    "source_chunk_id": "chunk_10",
    "premise": "The Convention enters into force six months after five eligible States have signed without reservation of ratification, acceptance or approval, or deposited their specified instruments. After that threshold, it enters into force for further Contracting Parties six months after deposit of their instruments.",
    "hypothesis": "A particular named State has already deposited its instrument.",
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
      "pair_id": "legal_nli_007",
      "premise_supported": true,
      "label": "neutral",
      "confidence": 0.96,
      "rationale": "The premise gives an entry-into-force rule but does not identify whether any particular named State has deposited an instrument; the historical event claim is neutral.",
      "exact_supporting_quote": "This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.",
      "scope_correction": "For exact source scope, replace 'eligible States' with 'States referred to in Article 52, paragraph 1'.",
      "source_key": "L_2009165EN.01000101 / chunk_10",
      "batch": "NLI_BATCH_1.md"
    },
    "quote_match": "ordered_source_fragments",
    "scope_correction_pending": true,
    "expert_validated": false,
    "confidence_is_calibrated_probability": false
  },
  {
    "pair_id": "legal_nli_012",
    "family_id": "tir_entry",
    "source_document_id": "L_2009165EN.01000101",
    "source_chunk_id": "chunk_10",
    "premise": "The Convention enters into force six months after five eligible States have signed without reservation of ratification, acceptance or approval, or deposited their specified instruments. After that threshold, it enters into force for further Contracting Parties six months after deposit of their instruments.",
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
    "scope_correction_pending": true,
    "expert_validated": false,
    "confidence_is_calibrated_probability": false
  },
  {
    "pair_id": "legal_nli_019",
    "family_id": "tir_entry",
    "source_document_id": "L_2009165EN.01000101",
    "source_chunk_id": "chunk_10",
    "premise": "The Convention enters into force six months after five eligible States have signed without reservation of ratification, acceptance or approval, or deposited their specified instruments. After that threshold, it enters into force for further Contracting Parties six months after deposit of their instruments.",
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
    "scope_correction_pending": true,
    "expert_validated": false,
    "confidence_is_calibrated_probability": false
  },
  {
    "pair_id": "legal_nli_023",
    "family_id": "tir_entry",
    "source_document_id": "L_2009165EN.01000101",
    "source_chunk_id": "chunk_10",
    "premise": "The Convention enters into force six months after five eligible States have signed without reservation of ratification, acceptance or approval, or deposited their specified instruments. After that threshold, it enters into force for further Contracting Parties six months after deposit of their instruments.",
    "hypothesis": "For further Contracting Parties, the stated interval is six months after their deposit.",
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
      "pair_id": "legal_nli_023",
      "premise_supported": true,
      "label": "entailment",
      "confidence": 0.99,
      "rationale": "The initial threshold is five Article 52(1) States and the interval is six months; further Contracting Parties also face a six-month interval after deposit. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.",
      "exact_supporting_quote": "This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.",
      "scope_correction": "For exact source scope, replace 'eligible States' with 'States referred to in Article 52, paragraph 1'.",
      "source_key": "L_2009165EN.01000101 / chunk_10",
      "batch": "NLI_BATCH_1.md"
    },
    "quote_match": "ordered_source_fragments",
    "scope_correction_pending": true,
    "expert_validated": false,
    "confidence_is_calibrated_probability": false
  },
  {
    "pair_id": "legal_nli_038",
    "family_id": "tir_entry",
    "source_document_id": "L_2009165EN.01000101",
    "source_chunk_id": "chunk_10",
    "premise": "The Convention enters into force six months after five eligible States have signed without reservation of ratification, acceptance or approval, or deposited their specified instruments. After that threshold, it enters into force for further Contracting Parties six months after deposit of their instruments.",
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
    "scope_correction_pending": true,
    "expert_validated": false,
    "confidence_is_calibrated_probability": false
  },
  {
    "pair_id": "legal_nli_050",
    "family_id": "tir_entry",
    "source_document_id": "L_2009165EN.01000101",
    "source_chunk_id": "chunk_10",
    "premise": "The Convention enters into force six months after five eligible States have signed without reservation of ratification, acceptance or approval, or deposited their specified instruments. After that threshold, it enters into force for further Contracting Parties six months after deposit of their instruments.",
    "hypothesis": "The initial entry-into-force interval is six months after the threshold date.",
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
      "pair_id": "legal_nli_050",
      "premise_supported": true,
      "label": "entailment",
      "confidence": 0.99,
      "rationale": "The initial threshold is five Article 52(1) States and the interval is six months; further Contracting Parties also face a six-month interval after deposit. The hypothesis restates an express element of that rule or follows directly from its stated numerical condition.",
      "exact_supporting_quote": "This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.",
      "scope_correction": "For exact source scope, replace 'eligible States' with 'States referred to in Article 52, paragraph 1'.",
      "source_key": "L_2009165EN.01000101 / chunk_10",
      "batch": "NLI_BATCH_2.md"
    },
    "quote_match": "ordered_source_fragments",
    "scope_correction_pending": true,
    "expert_validated": false,
    "confidence_is_calibrated_probability": false
  },
  {
    "pair_id": "legal_nli_065",
    "family_id": "tir_entry",
    "source_document_id": "L_2009165EN.01000101",
    "source_chunk_id": "chunk_10",
    "premise": "The Convention enters into force six months after five eligible States have signed without reservation of ratification, acceptance or approval, or deposited their specified instruments. After that threshold, it enters into force for further Contracting Parties six months after deposit of their instruments.",
    "hypothesis": "The fifth eligible State completed the specified step on 1 May 2027.",
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
      "pair_id": "legal_nli_065",
      "premise_supported": true,
      "label": "neutral",
      "confidence": 0.96,
      "rationale": "The premise gives the five-State threshold and timing rule but does not state that the fifth State completed the step on 1 May 2027; that date claim is neutral.",
      "exact_supporting_quote": "This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.",
      "scope_correction": "For exact source scope, replace 'eligible States' with 'States referred to in Article 52, paragraph 1'.",
      "source_key": "L_2009165EN.01000101 / chunk_10",
      "batch": "NLI_BATCH_3.md"
    },
    "quote_match": "ordered_source_fragments",
    "scope_correction_pending": true,
    "expert_validated": false,
    "confidence_is_calibrated_probability": false
  },
  {
    "pair_id": "legal_nli_079",
    "family_id": "tir_entry",
    "source_document_id": "L_2009165EN.01000101",
    "source_chunk_id": "chunk_10",
    "premise": "The Convention enters into force six months after five eligible States have signed without reservation of ratification, acceptance or approval, or deposited their specified instruments. After that threshold, it enters into force for further Contracting Parties six months after deposit of their instruments.",
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
    "scope_correction_pending": true,
    "expert_validated": false,
    "confidence_is_calibrated_probability": false
  },
  {
    "pair_id": "legal_nli_089",
    "family_id": "tir_entry",
    "source_document_id": "L_2009165EN.01000101",
    "source_chunk_id": "chunk_10",
    "premise": "The Convention enters into force six months after five eligible States have signed without reservation of ratification, acceptance or approval, or deposited their specified instruments. After that threshold, it enters into force for further Contracting Parties six months after deposit of their instruments.",
    "hypothesis": "A further Contracting Party is bound immediately on deposit, rather than after the stated six-month interval.",
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
      "pair_id": "legal_nli_089",
      "premise_supported": true,
      "label": "contradiction",
      "confidence": 0.99,
      "rationale": "The initial threshold is five Article 52(1) States and the interval is six months; further Contracting Parties also face a six-month interval after deposit. The hypothesis reverses, excludes, or violates an express condition of the premise.",
      "exact_supporting_quote": "This Convention shall enter into force six months after the date on which five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval or have deposited their instruments of ratification, acceptance, approval or accession. After five States referred to in Article 52, paragraph 1, have signed it without reservation of ratification, acceptance or approval, or have deposited their instruments of ratification, acceptance, approval or accession, this Convention shall enter into force for further Contracting Parties six months after the date of the deposit of their instruments of ratification, acceptance, approval or accession.",
      "scope_correction": "For exact source scope, replace 'eligible States' with 'States referred to in Article 52, paragraph 1'.",
      "source_key": "L_2009165EN.01000101 / chunk_10",
      "batch": "NLI_BATCH_3.md"
    },
    "quote_match": "ordered_source_fragments",
    "scope_correction_pending": true,
    "expert_validated": false,
    "confidence_is_calibrated_probability": false
  }
]
```
