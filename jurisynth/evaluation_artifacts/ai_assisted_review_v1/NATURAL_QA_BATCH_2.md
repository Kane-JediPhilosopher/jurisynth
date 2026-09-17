# AI-assisted natural-QA reference and retrieval review

Phase A: validate questions, draft reference answers and answer-bearing retrieval.
No system answers exist for these stored retrieval cases. Do NOT assign system PASS/PARTIAL/FAIL or QA accuracy yet.
Do not accept source applicability, alternate-source equivalence or temporal coherence merely because wording matches.
Return case_id; valid/revise/reject/uncertain; final question; verified reference answer with source quotes;
expected source keys; sufficient/partial/insufficient/irrelevant retrieval; helpful retrieved source keys;
scope/date/version caveats; confidence; and review notes. Use uncertain when sources are inadequate.
Draft references are Codex proposals, not adjudicated gold. Review them independently.

## global_natural_006

What is treated as water-pipe tobacco for the relevant tariff subheading?

Draft reference: Tobacco intended for water-pipe smoking and consisting of tobacco and glycerol, with listed additives/flavouring optional; tobacco-free products are excluded from subheading 2403 11.

Retrieval execution status: success (NOT relevance)

### Expected: L_2016294EN.01000101 / chunk_164

Resolution: document_chunk_sqlite

```text
1. For the purposes of subheading 2403 11, the expression 'water-pipe tobacco' means tobacco intended for smoking in a water pipe and which consists of a mixture of tobacco and glycerol, whether or not containing aromatic oils and extracts, molasses or sugar, and whether or not flavoured with fruit. However, tobacco-free products intended for smoking in a water pipe are excluded from this subheading. CN code Description Conventional rate of duty (%) Supplementary unit (1) (2) (3) (4) 2401 Unmanufactured tobacco; tobacco refuse 2401 10 - Tobacco, not stemmed/stripped 2401 10 35 - - Light air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 148 - 2401 10 60 - - Sun-cured Oriental type tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 10 70 - - Dark air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 10 85 - - Flue-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 149 - 2401 10 95 - - Other 10 MIN 22 € MAX 56 €/100 kg/net ( 150 - 2401 20 - Tobacco, partly or wholly stemmed/stripped 2401 20 35 - - Light air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 148 - 2401 20 60 - - Sun-cured Oriental type tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 20 70 - - Dark air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 20 85 - - Flue-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 149 - 2401 20 95 - - Other 11,2 MIN 22 € MAX 56 €/100 kg/net ( 150 - 2401 30 00 - Tobacco refuse 11,2 MIN 22 € MAX 56 €/100 kg/net - 2402 Cigars, cheroots, cigarillos and cigarettes, of tobacco or of tobacco substitutes 2402 10 00 - Cigars, cheroots and cigarillos, containing tobacco 26 1 000 p/st 2402 20 - Cigarettes containing tobacco 2402 20 10 - - Containing cloves 10 1 000 p/st 2402 20 90 - - Other 57,6 1 000 p/st 2402 90 00 - Other 57,6 - 2403 Other manufactured tobacco and manufactured tobacco substitutes; 'homogenised' or 'reconstituted' tobacco; tobacco extracts and essences - Smoking tobacco, whether or not containing tobacco substitutes in any proportion 2403 11 00 - - Water-pipe tobacco specified in subheading note 1 to this chapter 74,9 - 2403 19 - - Other 2403 19 10 - - - In immediate packings of a net content not exceeding 500 g 74,9 - 2403 19 90 - - - Other 74,9 - - Other 2403 91 00 - - 'Homogenised' or 'reconstituted' tobacco 16,6 - 2403 99 - - Other 2403 99 10 - - - Chewing tobacco and snuff 41,6 - 2403 99 90 - - - Other 16,6 -
SECTION V
MINERAL PRODUCTS
CHAPTER 25
```

### Retrieved: L_2021414EN.01000101 / chunk_168

Resolution: document_chunk_sqlite

```text
CN code Description Conventional rate of duty (%) Supplementary unit (1) (2) (3) (4) 2401 Unmanufactured tobacco; tobacco refuse 2401 10 - Tobacco, not stemmed/stripped 2401 10 35 - - Light air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 180 - 2401 10 60 - - Sun-cured Oriental type tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 10 70 - - Dark air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 10 85 - - Flue-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 183 - 2401 10 95 - - Other 10 MIN 22 € MAX 56 €/100 kg/net ( 185 - 2401 20 - Tobacco, partly or wholly stemmed/stripped 2401 20 35 - - Light air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 180 - 2401 20 60 - - Sun-cured Oriental type tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 20 70 - - Dark air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 20 85 - - Flue-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 183 - 2401 20 95 - - Other 11,2 MIN 22 € MAX 56 €/100 kg/net ( 185 - 2401 30 00 - Tobacco refuse 11,2 MIN 22 € MAX 56 €/100 kg/net - 2402 Cigars, cheroots, cigarillos and cigarettes, of tobacco or of tobacco substitutes 2402 10 00 - Cigars, cheroots and cigarillos, containing tobacco 26 1 000 p/st 2402 20 - Cigarettes containing tobacco 2402 20 10 - - Containing cloves 10 1 000 p/st 2402 20 90 - - Other 57,6 1 000 p/st 2402 90 00 - Other 57,6 - 2403 Other manufactured tobacco and manufactured tobacco substitutes; 'homogenised' or 'reconstituted' tobacco; tobacco extracts and essences - Smoking tobacco, whether or not containing tobacco substitutes in any proportion 2403 11 00 - - Water-pipe tobacco specified in subheading note 1 to this chapter 74,9 - 2403 19 - - Other 2403 19 10 - - - In immediate packings of a net content not exceeding 500 g 74,9 - 2403 19 90 - - - Other 74,9 - - Other 2403 91 00 - - 'Homogenised' or 'reconstituted' tobacco 16,6 - 2403 99 - - Other 2403 99 10 - - - Chewing tobacco and snuff (nasal tobacco) 41,6 - 2403 99 90 - - - Other 16,6 - 2404 Products containing tobacco, reconstituted tobacco, nicotine, or tobacco or nicotine substitutes, intended for inhalation without combustion;
```

### Retrieved: L_2021385EN.01000101 / chunk_167

Resolution: document_chunk_sqlite

```text
CN code Description Conventional rate of duty (%) Supplementary unit (1) (2) (3) (4) 2401 Unmanufactured tobacco; tobacco refuse 2401 10 - Tobacco, not stemmed/stripped 2401 10 35 - - Light air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 24 - 2401 10 60 - - Sun-cured Oriental type tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 10 70 - - Dark air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 10 85 - - Flue-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 25 - 2401 10 95 - - Other 10 MIN 22 € MAX 56 €/100 kg/net ( 26 - 2401 20 - Tobacco, partly or wholly stemmed/stripped 2401 20 35 - - Light air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 24 - 2401 20 60 - - Sun-cured Oriental type tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 20 70 - - Dark air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 20 85 - - Flue-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 25 - 2401 20 95 - - Other 11,2 MIN 22 € MAX 56 €/100 kg/net ( 26 - 2401 30 00 - Tobacco refuse 11,2 MIN 22 € MAX 56 €/100 kg/net - 2402 Cigars, cheroots, cigarillos and cigarettes, of tobacco or of tobacco substitutes 2402 10 00 - Cigars, cheroots and cigarillos, containing tobacco 26 1 000 p/st 2402 20 - Cigarettes containing tobacco 2402 20 10 - - Containing cloves 10 1 000 p/st 2402 20 90 - - Other 57,6 1 000 p/st 2402 90 00 - Other 57,6 - 2403 Other manufactured tobacco and manufactured tobacco substitutes; 'homogenised' or 'reconstituted' tobacco; tobacco extracts and essences - Smoking tobacco, whether or not containing tobacco substitutes in any proportion 2403 11 00 - - Water-pipe tobacco specified in subheading note 1 to this chapter 74,9 - 2403 19 - - Other 2403 19 10 - - - In immediate packings of a net content not exceeding 500 g 74,9 - 2403 19 90 - - - Other 74,9 - - Other 2403 91 00 - - 'Homogenised' or 'reconstituted' tobacco 16,6 - 2403 99 - - Other 2403 99 10 - - - Chewing tobacco and snuff (nasal tobacco) 41,6 - 2403 99 90 - - - Other 16,6 - 2404 Products containing tobacco, reconstituted tobacco, nicotine, or tobacco or nicotine substitutes, intended for inhalation without combustion;
```

### Retrieved: L_2021385EN.01000101 / chunk_166

Resolution: document_chunk_sqlite

```text
maltodextrine or maltodextrin syrup - - - - - Containing no starch or containing 10 % or less by weight of starch 2309 90 31 - - - - - - Containing no milk products or containing less than 10 % by weight of such products 23 €/t ( 2 - 2309 90 33 - - - - - - Containing not less than 10 % but less than 50 % by weight of milk products 498 €/t - 2309 90 35 - - - - - - Containing not less than 50 % but less than 75 % by weight of milk products 730 €/t - 2309 90 39 - - - - - - Containing not less than 75 % by weight of milk products 948 €/t - - - - - - Containing more than 10 % but not more than 30 % by weight of starch 2309 90 41 - - - - - - Containing no milk products or containing less than 10 % by weight of such products 55 €/t ( 2 - 2309 90 43 - - - - - - Containing not less than 10 % but less than 50 % by weight of milk products 530 €/t - 2309 90 49 - - - - - - Containing not less than 50 % by weight of milk products 888 €/t - - - - - - Containing more than 30 % by weight of starch 2309 90 51 - - - - - - Containing no milk products or containing less than 10 % by weight of such products 102 €/t ( 2 - 2309 90 53 - - - - - - Containing not less than 10 % but less than 50 % by weight of milk products 577 €/t - 2309 90 59 - - - - - - Containing not less than 50 % by weight of milk products 730 €/t - 2309 90 70 - - - - Containing no starch, glucose, glucose syrup, maltodextrine or maltodextrine syrup but containing milk products 948 €/t - - - - Other 2309 90 91 - - - - Beet-pulp with added molasses 12 - 2309 90 96 - - - - Other 9,6 -
CHAPTER 24
TOBACCO AND MANUFACTURED TOBACCO SUBSTITUTES; PRODUCTS, WHETHER OR NOT CONTAINING NICOTINE, INTENDED FOR INHALATION WITHOUT COMBUSTION; OTHER NICOTINE CONTAINING PRODUCTS INTENDED FOR THE INTAKE OF NICOTINE INTO THE HUMAN BODY
Notes
1. This chapter does not cover medicinal cigarettes (Chapter 30). 2. Any products classifiable in heading 2404 and any other heading of the chapter are to be classified in heading 2404. 3. For the purposes of heading 2404, the expression 'inhalation without combustion' means inhalation through heated delivery or other means, without combustion.
Subheading note
1. For the purposes of subheading 2403 11, the expression 'water-pipe tobacco' means tobacco intended for smoking in a water pipe and which consists of a mixture of tobacco and glycerol, whether or not containing aromatic oils and extracts, molasses or sugar, and whether or not flavoured with fruit. However, tobacco-free products intended for smoking in a water pipe are excluded from this subheading.
```

### Retrieved: L_2021414EN.01000101 / chunk_167

Resolution: document_chunk_sqlite

```text
maltodextrine or maltodextrin syrup - - - - - Containing no starch or containing 10 % or less by weight of starch 2309 90 31 - - - - - - Containing no milk products or containing less than 10 % by weight of such products 23 €/t ( 26 - 2309 90 33 - - - - - - Containing not less than 10 % but less than 50 % by weight of milk products 498 €/t - 2309 90 35 - - - - - - Containing not less than 50 % but less than 75 % by weight of milk products 730 €/t - 2309 90 39 - - - - - - Containing not less than 75 % by weight of milk products 948 €/t - - - - - - Containing more than 10 % but not more than 30 % by weight of starch 2309 90 41 - - - - - - Containing no milk products or containing less than 10 % by weight of such products 55 €/t ( 26 - 2309 90 43 - - - - - - Containing not less than 10 % but less than 50 % by weight of milk products 530 €/t - 2309 90 49 - - - - - - Containing not less than 50 % by weight of milk products 888 €/t - - - - - - Containing more than 30 % by weight of starch 2309 90 51 - - - - - - Containing no milk products or containing less than 10 % by weight of such products 102 €/t ( 26 - 2309 90 53 - - - - - - Containing not less than 10 % but less than 50 % by weight of milk products 577 €/t - 2309 90 59 - - - - - - Containing not less than 50 % by weight of milk products 730 €/t - 2309 90 70 - - - - Containing no starch, glucose, glucose syrup, maltodextrine or maltodextrine syrup but containing milk products 948 €/t - - - - Other 2309 90 91 - - - - Beet-pulp with added molasses 12 - 2309 90 96 - - - - Other 9,6 -
CHAPTER 24
TOBACCO AND MANUFACTURED TOBACCO SUBSTITUTES; PRODUCTS, WHETHER OR NOT CONTAINING NICOTINE, INTENDED FOR INHALATION WITHOUT COMBUSTION; OTHER NICOTINE CONTAINING PRODUCTS INTENDED FOR THE INTAKE OF NICOTINE INTO THE HUMAN BODY
Notes
1. This chapter does not cover medicinal cigarettes (Chapter 30). 2. Any products classifiable in heading 2404 and any other heading of the chapter are to be classified in heading 2404. 3. For the purposes of heading 2404, the expression 'inhalation without combustion' means inhalation through heated delivery or other means, without combustion.
Subheading note
1. For the purposes of subheading 2403 11, the expression 'water-pipe tobacco' means tobacco intended for smoking in a water pipe and which consists of a mixture of tobacco and glycerol, whether or not containing aromatic oils and extracts, molasses or sugar, and whether or not flavoured with fruit. However, tobacco-free products intended for smoking in a water pipe are excluded from this subheading.
```

### Retrieved: L_2022282EN.01000101 / chunk_42

Resolution: document_chunk_sqlite

```text
Their starch content may not exceed 28 % by weight on the dry product in accordance with the method contained in Annex III, part L, to Commission Regulation (EC) No 152/2009, their fat content may not exceed 4,5 % by weight on the dry product determined in accordance with the method contained in Annex III, part H, to Commission Regulation (EC) No 152/2009, and their protein content may not exceed 40 % on the dry product determined in accordance with the method contained in Annex III, part C, to Commission Regulation (EC) No 152/2009. - screenings from maize used in the wet process in a proportion not exceeding 15 % by weight, and/or - residues of maize steep-water, from the wet process, including residues of steep-water used for the manufacture of alcohol or of other starch derived products.
CHAPTER 24
TOBACCO AND MANUFACTURED TOBACCO SUBSTITUTES; PRODUCTS, WHETHER OR NOT CONTAINING NICOTINE, INTENDED FOR INHALATION WITHOUT COMBUSTION; OTHER NICOTINE CONTAINING PRODUCTS INTENDED FOR THE INTAKE OF NICOTINE INTO THE HUMAN BODY
Notes
1. This chapter does not cover medicinal cigarettes (Chapter 30). 2. Any products classifiable in heading 2404 and any other heading of the chapter are to be classified in heading 2404. 3. For the purposes of heading 2404, the expression 'inhalation without combustion' means inhalation through heated delivery or other means, without combustion.
Subheading note
1. For the purposes of subheading 2403 11, the expression 'water-pipe tobacco' means tobacco intended for smoking in a water pipe and which consists of a mixture of tobacco and glycerol, whether or not containing aromatic oils and extracts, molasses or sugar, and whether or not flavoured with fruit. However, tobacco-free products intended for smoking in a water pipe are excluded from this subheading.
SECTION V
MINERAL PRODUCTS
CHAPTER 25
SALT; SULPHUR; EARTHS AND STONE; PLASTERING MATERIALS, LIME AND CEMENT
Notes
```

### Retrieved: L_2012304EN.01000101 / chunk_159

Resolution: document_chunk_sqlite

```text
1. For the purposes of subheading 2403 11 , the expression 'water-pipe tobacco' means tobacco intended for smoking in a water pipe and which consists of a mixture of tobacco and glycerol, whether or not containing aromatic oils and extracts, molasses or sugar, and whether or not flavoured with fruit. However, tobacco-free products intended for smoking in a water pipe are excluded from this subheading. CN code Description Conventional rate of duty (%) Supplementary unit (1) (2) (3) (4) 2401 Unmanufactured tobacco; tobacco refuse 2401 10 - Tobacco, not stemmed/stripped 2401 10 35 - - Light air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 139 - 2401 10 60 - - Sun-cured oriental type tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 10 70 - - Dark air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 10 85 - - Flue-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 140 - 2401 10 95 - - Other 10 MIN 22 € MAX 56 €/100 kg/net ( 141 - 2401 20 - Tobacco, partly or wholly stemmed/stripped 2401 20 35 - - Light air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 139 - 2401 20 60 - - Sun-cured oriental type tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 20 70 - - Dark air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 20 85 - - Flue-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 140 - 2401 20 95 - - Other 11,2 MIN 22 € MAX 56 €/100 kg/net ( 141 - 2401 30 00 - Tobacco refuse 11,2 MIN 22 € MAX 56 €/100 kg/net - 2402 Cigars, cheroots, cigarillos and cigarettes, of tobacco or of tobacco substitutes 2402 10 00 - Cigars, cheroots and cigarillos, containing tobacco 26 1 000 p/st 2402 20 - Cigarettes containing tobacco 2402 20 10 - - Containing cloves 10 1 000 p/st 2402 20 90 - - Other 57,6 1 000 p/st 2402 90 00 - Other 57,6 - 2403 Other manufactured tobacco and manufactured tobacco substitutes; 'homogenised' or 'reconstituted' tobacco; tobacco extracts and essences - Smoking tobacco, whether or not containing tobacco substitutes in any proportion 2403 11 00 - - Water-pipe tobacco specified in subheading note 1 to this chapter 74,9 - 2403 19 - - Other 2403 19 10 - - - In immediate packings of a net content not exceeding 500 g 74,9 - 2403 19 90 - - - Other 74,9 - - Other 2403 91 00 - - 'Homogenised' or 'reconstituted' tobacco 16,6 - 2403 99 - - Other 2403 99 10 - - - Chewing tobacco and snuff 41,6 - 2403 99 90 - - - Other 16,6 -
SECTION V
MINERAL PRODUCTS
CHAPTER 25
```

### Retrieved: L_202402522EN / chunk_42

Resolution: document_chunk_sqlite

```text
Their starch content shall not exceed 28 % by weight on the dry product in accordance with the method contained in Annex III, part K, to Regulation (EC) No 152/2009, their fat content shall not exceed 4,5 % by weight on the dry product determined in accordance with the method contained in Annex III, part G, to Regulation (EC) No 152/2009, and their protein content shall not exceed 40 % on the dry product determined in accordance with the method contained in Annex III, part C, to Regulation (EC) No 152/2009. - screenings from maize used in the wet process in a proportion not exceeding 15 % by weight, and/or - residues of maize steep-water, from the wet process, including residues of steep-water used for the manufacture of alcohol or of other starch derived products.
CHAPTER 24
TOBACCO AND MANUFACTURED TOBACCO SUBSTITUTES; PRODUCTS, WHETHER OR NOT CONTAINING NICOTINE, INTENDED FOR INHALATION WITHOUT COMBUSTION; OTHER NICOTINE CONTAINING PRODUCTS INTENDED FOR THE INTAKE OF NICOTINE INTO THE HUMAN BODY
Notes
1. This chapter does not cover medicinal cigarettes (Chapter 30). 2. Any products classifiable in heading 2404 and any other heading of the chapter are to be classified in heading 2404 . 3. For the purposes of heading 2404 , the expression 'inhalation without combustion' means inhalation through heated delivery or other means, without combustion.
Subheading note
1. For the purposes of subheading 2403 11 , the expression 'water-pipe tobacco' means tobacco intended for smoking in a water pipe and which consists of a mixture of tobacco and glycerol, whether or not containing aromatic oils and extracts, molasses or sugar, and whether or not flavoured with fruit. However, tobacco-free products intended for smoking in a water pipe are excluded from this subheading.
SECTION V
MINERAL PRODUCTS
CHAPTER 25
SALT; SULPHUR; EARTHS AND STONE; PLASTERING MATERIALS, LIME AND CEMENT
Notes
```

### Retrieved: L_2020361EN.01000101 / chunk_166

Resolution: document_chunk_sqlite

```text
1. For the purposes of subheading 2403 11, the expression 'water-pipe tobacco' means tobacco intended for smoking in a water pipe and which consists of a mixture of tobacco and glycerol, whether or not containing aromatic oils and extracts, molasses or sugar, and whether or not flavoured with fruit. However, tobacco-free products intended for smoking in a water pipe are excluded from this subheading. CN code Description Conventional rate of duty (%) Supplementary unit (1) (2) (3) (4) 2401 Unmanufactured tobacco; tobacco refuse 2401 10 - Tobacco, not stemmed/stripped 2401 10 35 - - Light air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 133 - 2401 10 60 - - Sun-cured Oriental type tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 10 70 - - Dark air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 10 85 - - Flue-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 134 - 2401 10 95 - - Other 10 MIN 22 € MAX 56 €/100 kg/net ( 135 - 2401 20 - Tobacco, partly or wholly stemmed/stripped 2401 20 35 - - Light air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 133 - 2401 20 60 - - Sun-cured Oriental type tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 20 70 - - Dark air-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net - 2401 20 85 - - Flue-cured tobacco 11,2 MIN 22 € MAX 56 €/100 kg/net ( 134 - 2401 20 95 - - Other 11,2 MIN 22 € MAX 56 €/100 kg/net ( 135 - 2401 30 00 - Tobacco refuse 11,2 MIN 22 € MAX 56 €/100 kg/net - 2402 Cigars, cheroots, cigarillos and cigarettes, of tobacco or of tobacco substitutes 2402 10 00 - Cigars, cheroots and cigarillos, containing tobacco 26 1 000 p/st 2402 20 - Cigarettes containing tobacco 2402 20 10 - - Containing cloves 10 1 000 p/st 2402 20 90 - - Other 57,6 1 000 p/st 2402 90 00 - Other 57,6 - 2403 Other manufactured tobacco and manufactured tobacco substitutes; 'homogenised' or 'reconstituted' tobacco; tobacco extracts and essences - Smoking tobacco, whether or not containing tobacco substitutes in any proportion 2403 11 00 - - Water-pipe tobacco specified in subheading note 1 to this chapter 74,9 - 2403 19 - - Other 2403 19 10 - - - In immediate packings of a net content not exceeding 500 g 74,9 - 2403 19 90 - - - Other 74,9 - - Other 2403 91 00 - - 'Homogenised' or 'reconstituted' tobacco 16,6 - 2403 99 - - Other 2403 99 10 - - - Chewing tobacco and snuff (nasal tobacco) 41,6 - 2403 99 90 - - - Other 16,6 -
SECTION V
MINERAL PRODUCTS
CHAPTER 25
```

### Retrieved table: L_1994001EN.01000101 / table_15

```json
{
  "document_id": "L_1994001EN.01000101",
  "table_id": "table_15",
  "row_ids": [
    4
  ],
  "headers": [
    "Tariff heading No",
    "Description of goods"
  ],
  "rows": [
    [
      "ex all tariff chapters",
      "Products which are used as motor fuels"
    ]
  ]
}
```

### Retrieved table: L_202400296EN / table_16

```json
{
  "document_id": "L_202400296EN",
  "table_id": "table_16",
  "row_ids": [
    2
  ],
  "headers": [
    "EPC",
    "CAT",
    "UNIT",
    "Description",
    "A",
    "P",
    "D"
  ],
  "rows": [
    [
      "T400",
      "T",
      "1",
      "Fine-cut tobacco for the rolling of cigarettes, as defined in Article 5(2) of Directive 2011/64/EU",
      "N",
      "N",
      "N"
    ]
  ]
}
```

### Retrieved table: L_2022247EN.01000201 / table_13

```json
{
  "document_id": "L_2022247EN.01000201",
  "table_id": "table_13",
  "row_ids": [
    2
  ],
  "headers": [
    "EPC",
    "CAT",
    "UNIT",
    "Description",
    "A",
    "P",
    "D"
  ],
  "rows": [
    [
      "T400",
      "T",
      "1",
      "Fine-cut tobacco for the rolling of cigarettes, as defined in Article 5(2) of Directive 2011/64/EU",
      "N",
      "N",
      "N"
    ]
  ]
}
```

### Retrieved table: L_202400296EN / table_16

```json
{
  "document_id": "L_202400296EN",
  "table_id": "table_16",
  "row_ids": [
    3
  ],
  "headers": [
    "EPC",
    "CAT",
    "UNIT",
    "Description",
    "A",
    "P",
    "D"
  ],
  "rows": [
    [
      "T500",
      "T",
      "1",
      "Smoking tobacco, as defined in Article 5(1) of Directive 2011/64/EU, other than fine-cut tobacco for the rolling of cigarettes, as defined in Article 5(2) of that Directive, and products treated as smoking tobacco other than fine-cut tobacco for the rolling of cigarettes in accordance with Article 2(2) of that Directive",
      "N",
      "N",
      "N"
    ]
  ]
}
```

### Retrieved table: L_2022247EN.01000201 / table_13

```json
{
  "document_id": "L_2022247EN.01000201",
  "table_id": "table_13",
  "row_ids": [
    3
  ],
  "headers": [
    "EPC",
    "CAT",
    "UNIT",
    "Description",
    "A",
    "P",
    "D"
  ],
  "rows": [
    [
      "T500",
      "T",
      "1",
      "Smoking tobacco, as defined in Article 5(1) of Directive 2011/64/EU, other than fine-cut tobacco for the rolling of cigarettes, as defined in Article 5(2) of that Directive, and products treated as smoking tobacco other than fine-cut tobacco for the rolling of cigarettes in accordance with Article 2(2) of that Directive",
      "N",
      "N",
      "N"
    ]
  ]
}
```

## global_natural_007

How is the country of origin determined for a good or part produced from a blank?

Draft reference: Apply the finishing-country rule only if all paragraph-a conditions are met; otherwise use origin of the blank under paragraph b. Preserve the same-heading, functioning and processing conditions.

Retrieval execution status: success (NOT relevance)

### Expected: L_2015343EN.01000101 / chunk_129

Resolution: document_chunk_sqlite

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

### Retrieved: L_202302429EN / chunk_2

Resolution: document_chunk_sqlite

```text
(7) Given the wide range of varieties of bananas marketed in the Union and of marketing practices, minimum standards should be maintained for unripened green bananas. However, it is appropriate to align the marketing standard for bananas to the Codex Alimentarius and extend to more varieties to avoid unnecessary barriers to trade. In view of reducing food waste and food loss in the context of the Farm to Fork Strategy, notably by improving the flexibility for the portioning, it is appropriate to leave out the minimum of four fingers by hand or cluster set out in the Codex Alimentarius. It is appropriate, in view of the objectives pursued, to allow banana-producing Member States to apply national standards within their territory to their own production provided those rules are not in conflict with Union standards and do not impede the free circulation of bananas in the Union.
(8) Account should be taken of the fact that, climatic factors make production conditions difficult in Madeira, the Azores, the Algarve, Canary Islands, Crete, Lakonia and Cyprus. As a result, certain bananas do not develop to the minimum length laid down in the international standard when produced in those geographical areas. In those cases, such bananas should be allowed to be marketed.
(9) In order to avoid unnecessary barriers to trade, where specific marketing standards are to be laid down for individual products, those standards should be those set out in the standards adopted by the United Nations Economic Commission for Europe (UNECE). Where no specific marketing standard has been adopted at Union level, products should be considered as conforming to the general marketing standard where the holder is able to show that the products are in conformity with any applicable UNECE standard.
(10) In order to take into account the Farm to Fork Strategy and consumers' interests, the marketing standards for all the sectors covered by this Regulation should maintain the high-quality requirements that make international consensus while encouraging alternative uses in order to avoid food loss and food waste when the standard is not complied with. This should be the case for all products that do not comply with the requirements of Class II of the UNECE marketing standards but are still edible. Therefore, exemptions from the application of marketing standards should be provided for in the case of certain products that are intended for processing, or that are sold by the producer directly to consumers.
(11) Certain fruit and vegetable products may have characteristics that do not conform to the applicable marketing standards. A traditional cultivation and local consumption may nonetheless be well-established in respect of those products. To ensure that products which are deemed to be fit for consumption by local communities but which do not conform to the Union marketing standards are not prevented from being marketed locally, those products should be exempted from the Union marketing standards unless this exemption is likely to prevent or distort competition in a substantial part of the internal market, or to jeopardise free trade or the attainment of any of the objectives of Article 39 of the Treaty.
(12) Several fruit and vegetables products may derogate from the marketing standards in view of reducing the administrative burden both for the traders and for the authorities carrying out the controls in accordance with Article 76(4) of Regulation (EU) No 1308/2013. Nonetheless, the labelling of origin is necessary for the consumers and in line with the policy orientation of the Farm to Fork strategy to provide more information to allow consumers to make a better informed choice, the indication of the country of origin should be mandatory for such products.
(13) Marketing standards relative to products for donations should be simplified in order to reduce the administrative burden for the traders without affecting the quality. Provided the product is clearly labelled to inform that it is for donation, other marking particulars should be optional. It should nonetheless conform to the general marketing standard regarding the quality in order to protect the beneficiary of the donation.
(14) In order to ensure that checks may be properly and effectively carried out, invoices and accompanying documents, other than those for consumers, should contain certain basic information included in the marketing standards.
(15) The information particulars required by marketing standards should be clearly displayed on the packaging and/or on the label. To avoid fraud and cases of misleading consumers, the information particulars required by the marketing standards should be available to consumers before purchase, including in case of distance selling, where experience has shown the risks of fraud and avoidance of the consumer protection offered by the standards.
(16) In order to avoid misleading the consumers regarding the class, the information particulars required at retail stage should not include terms such as 'supreme', 'premium' or similar wording which are not regulated for defining an actual quality of the product, notwithstanding the possibility to display any other information such as 'transport by air' or similar factual information which does not mislead the consumer.
```

### Retrieved: L_202302411EN / chunk_20

Resolution: document_chunk_sqlite

```text
1. Without prejudice to Article 44, at the time of registration of the geographical indication, the Office may decide to grant a transitional period of up to five years to allow, for products originating in a Member State or a third country, the designation of which consists of or contains a name that is in breach of Article 40, the continued use of the designation under which they were marketed, provided that an admissible opposition, under Article 15 or 25, to the application for registration of the geographical indication of which the protection is contravened, has shown that:
(a) the registration of the geographical indication would jeopardise the existence of an identical or similar name used in the course of trade for the purposes of product designation; or (b) such products have been legally marketed with that name for the purposes of product designation in the territory concerned for at least five years preceding the date of the publication of the application provided for in Article 22(7).
1. The Office may grant a transitional period of up to 15 years or may decide to extend the transitional period granted under paragraph 1 up to a total period of 15 years, provided it is additionally shown that:
(a) the name referred to in paragraph 1 has been in legal use consistently and fairly for at least 25 years before the application for the registration of the geographical indication concerned was submitted to the Office; (b) the purpose of using the name referred to in paragraph 1 has not, at any time, been to profit from the reputation of the name that has been registered as a geographical indication; and (c) the consumer has not been or could not have been misled as to the true geographical origin of the products.
1. Decisions granting or extending a transitional period, as referred to in paragraphs 1 and 2, shall be published in the Union register.
2. During the transitional period, when using a name referred to in paragraph 1, the indication of the country of origin shall clearly and visibly appear on the labelling and, where applicable, as part of the product description where the product is marketed on an online sales website.
3. With a view to achieving the long-term objective of ensuring that all producers of a product designated by a geographical indication in the geographical area concerned comply with the related product specification, a Member State may grant a transitional period for achieving compliance of up to ten years, taking effect from the date on which the application is submitted to the Office, provided that the operators concerned have legally marketed the product in question, using the name concerned continuously for at least five years preceding the lodging of the application to the competent authority of that Member State and have referred to that fact in the national opposition procedure referred to in Article 15.
4. Paragraph 5 shall apply, mutatis mutandis , to a geographical indication referring to a geographical area situated in a third country. The obligation to refer in the national opposition procedure to the continuous use as referred to in that paragraph shall not apply to geographical indications referring to a geographical area in a third country.
Article 29
Decision of the Office on the application
```

### Retrieved: L_202502652EN / chunk_2

Resolution: document_chunk_sqlite

```text
(9) In order to implement the new Agreement and the EU-Morocco Association Council Decision of 3 October 2025, it is necessary to derogate from Article 76(1) of Regulation (EU) No 1308/2013 and from Article 3 of Delegated Regulation (EU) 2023/2429 to provide that for fruit and vegetables originating in the territory of Western Sahara that are subject to the control of Moroccan custom authorities and are imported and marketed in the Union, the indication of the country of origin is replaced by the indication of the region in which the product originates as indicated in the certificate of origin accompanying those products at the moment of import in the Union.
(10) Article 9(3) of Delegated Regulation (EU) 2023/2429 limits the approval of checks of conformity to marketing standards carried out by certain third countries to products originating in such third countries. In order to allow the Union to grant the Moroccan competent authorities the authorisation to carry out checks of conformity and, consequently, to certify compliance with Union marketing standards for fresh fruit and vegetables originating in the non-self-governing territory of Western Sahara that are subject to the control of Moroccan custom authorities and are imported and marketed in the Union, it is appropriate to include in that Article the possibility for the Commission to approve checks of conformity to marketing standards conducted by Moroccan competent authorities in respect of those products.
(11) To avoid any disruption to trade covered by the extension of preferences provided for by the new Agreement, this Regulation should enter into force on the day following that of its publication in the Official Journal of the European Union
(12) As the new Agreement is provisionally applicable as from 4 October 2025, this Regulation should apply retroactively from the same date.
(13) However, fruit and vegetables originating in the non-self-governing territory of Western Sahara and subject to the control of Moroccan custom authorities that were lawfully imported into the Union before the entry into force of this Regulation bearing the indication of Western Sahara as country of origin, should be allowed to continue to be marketed within the Union after that date, until stocks are exhausted and provided that such products continue to conform with all other requirements of the applicable Union marketing standards.
(14) Delegated Regulation (EU) 2023/2429 should therefore be amended accordingly,
HAS ADOPTED THIS REGULATION:
Article 1
Delegated Regulation (EU) 2023/2429 is amended as follows:
(1) in Article 5, the following paragraph 6 is added: '6. By way of derogation from Article 76(1) of Regulation (EU) No 1308/2013 and from Article 3 of this Regulation, for products referred to in Article 1(2) of this Regulation originating in the non-self-governing territory of Western Sahara that are subject to the control of the Moroccan custom authorities and are imported and marketed in the Union, the indication of the country of origin shall be replaced by the indication of the region in which the concerned product originates as indicated in the certificate of origin accompanying those products when imported into the Union.' (2) in Article 9, paragraph 3 is replaced by the following: '3. The approval shall only apply to products originating in the third country concerned and may be limited to certain products. However, the Commission may approve checks of conformity to marketing standards carried out by Moroccan competent authorities in respect of products originating in the non-self-governing territory of Western Sahara that are subject to the control of Moroccan custom authorities.'
Article 2
Products referred to in Article 1(2) of Delegated Regulation (EU) 2023/2429 originating in the non-self-governing territory of Western Sahara and subject to the control of Moroccan custom authorities that were lawfully imported into the Union before the entry into force of this Regulation bearing the indication of Western Sahara as country of origin, may continue to be marketed within the Union after that date, until stocks are exhausted and provided that they continue to conform with all other requirements of the applicable Union marketing standards.
Article 3
This Regulation shall enter into force on the day following that of its publication in the Official Journal of the European Union .
It shall apply from 4 October 2025.
This Regulation shall be binding in its entirety and directly applicable in all Member States.
Done at Brussels, 16 October 2025.
For the Commission
The President
Ursula VON DER LEYEN
```

### Retrieved: L_202302429EN / chunk_3

Resolution: document_chunk_sqlite

```text
(17) In order to avoid misleading consumers regarding the origin of the products, the indication of the country of origin should be better visible than the indication of the country of the packer.
(18) Packages containing mixes of different products or species of products covered by this Regulation are becoming more common on the market in response to certain consumers demand. Fair trading requires that products or species of products sold in the same package are of uniform quality. For products for which Union standards have not been adopted this can be ensured by recourse to general provisions. Labelling requirements should therefore be laid down for mixes of different products or species of products in the same package. They should be less strict than those laid down by the marketing standards as labelling of mixes is more burdensome and their application risks to obstacle the marketing of those products.
(19) Imports of fruit and vegetables from third countries are to conform to the marketing standards or to standards equivalent to them. Therefore, conditions under which imported products are considered to have an equivalent level of conformity to the Union marketing standards should be laid down.
(20) In order to give operators and the national administrations sufficient time to adapt to the changes introduced by this Regulation, this Regulation should apply as from 1 January 2025.
(21) Given the substantive link between the empowerments in Regulation (EU) No 1308/2013 regarding the rules on marketing standards, on the minimum quality requirements for products of the fruit and vegetables sector and on the conformity of imported products to Union marketing standards, it is appropriate to lay down those rules in the same delegated act,
HAS ADOPTED THIS REGULATION:
CHAPTER I
INTRODUCTORY PROVISIONS
Article 1
Subject matter and scope
1. This Regulation lays down rules supplementing Regulation (EU) No 1308/2013 as regards the marketing standards referred to in Article 75(1) of that Regulation, the minimum marketing requirements for products of the fruit and vegetables sector intended to be sold fresh as referred to in Article 76 of that Regulation, the conformity of imported products to Union marketing standards as referred to in Article 89 of that Regulation.
2. This Regulation applies to the following sectors and products:
(a) the fruit and vegetables sector referred to in Article 1(2), point (i), of Regulation (EU) No 1308/2013; (b) dried fruits of CN codes 0804 20 90, 0806 20 and ex 0813 listed in Part X of Annex I to that Regulation; (c) the bananas of CN code 0803 90 10 listed in Part XI of Annex I to that Regulation.
1. For the purpose of this regulation, the country of origin of a product shall be determined in accordance with Article 60 of Regulation (EU) No 952/2013 of the European Parliament and of the Council [( 7 )](#ntr7-L_202302429EN.000101-E0007) .
CHAPTER II
MARKETING STANDARDS
Article 2
General marketing standard for fruits and vegetables referred to in Article 1(2), point (a)
1. The requirements of Article 76(1) of Regulation (EU) No 1308/2013 shall constitute the general marketing standard for the fruits and vegetables referred to in Article 1(2), point (a).
Fruit and vegetables referred to in Article 1(2), point (a) shall conform to that general marketing standard unless they are subject to a specific marketing standard.
The details of the general marketing standard are set out in Part A of Annex I to this Regulation.
1. Where the holder of fruit and vegetables referred to in paragraph 1 is able to show that the products are in conformity with any applicable standard adopted by the United Nations Economic Commission for Europe (UNECE), they shall be considered as conforming to the general marketing standard referred to in paragraph 1.
2. For the purposes of this Article, 'holder' means any natural or legal person who is in physical possession of the products concerned or offers them for sale at distance or by any digital means.
Article 3
Indication of the origin for certain processed fruit and vegetable products and ripened bananas
The following products shall carry an indication of the country of origin:
```

### Retrieved: L_202302429EN / chunk_25

Resolution: document_chunk_sqlite

```text
The materials used inside the package must be clean and of a quality such as to avoid causing any external or internal damage to the produce. The use of materials, particularly of paper or stamps bearing trade specifications is allowed provided the printing or labelling has been done with non-toxic ink or glue.
Stickers individually affixed on the produce shall be such that, when removed, they neither leave visible traces of glue, nor lead to skin defects. Information lasered on single fruit should not lead to flesh or skin defects.
Packages must be free of all foreign matter.
VI. PROVISIONS CONCERNING MARKING
Each package
[( 31 )](#ntr31-L_202302429EN.001101-E0031)
must bear the following particulars, in letters grouped on the same side, legibly and indelibly marked, and visible from the outside.
A. Identification
Name and physical address of the packer and/or the dispatcher (for example street/city/region/postal code and, if different from the country of origin, the country).
This mention may be replaced:
- for all packages with the exception of pre-packages, by the officially issued or accepted code mark representing the packer and/or the dispatcher, indicated in close connection with the reference 'Packer and/or Dispatcher' (or equivalent abbreviations). The code mark shall be preceded by the ISO 3166 (alpha) country/area code of the recognising country, if not the country of origin; - for pre-packages only, by the name and the address of a seller established within the Union indicated in close connection with the mention 'Packed for:' or an equivalent mention. In this case, the labelling shall also include a code representing the packer and/or the dispatcher. The seller shall give all information deemed necessary by the inspection body as to the meaning of this code.
B. Nature of produce
- 'Pears', if the contents of the package are not visible from the outside. - Name of the variety. In the case of a mixture of pears of distinctly different varieties, names of the different varieties. - The name of the variety may be replaced by a synonym. A trade name ( 32
C. Origin of produce
Country of origin
[( 33 )](#ntr33-L_202302429EN.001101-E0033)
and, optionally, district where grown, or national, regional or local place name.
In the case of a mixture of distinctly different varieties of pears of different origins, the indication of each country of origin shall appear next to the name of the variety concerned.
D. Commercial specifications
- Class. - Size, or for fruit packed in rows and layers, number of units. - If identification is by the size, this should be expressed: (a) for produce subject to the uniformity rules, as minimum and maximum diameters or minimum and maximum weights; (b) optionally, for produce not subject to the uniformity rules, as the diameter or the weight of the smallest fruit in the package followed by 'and over' or equivalent denomination or, where appropriate, the diameter or the weight of the largest fruit in the package.
E. Official control mark (optional)
Packages need not to bear the particulars mentioned in the first subparagraph of point VI, when they contain sales packages, clearly visible from the outside, and all bearing these particulars. These packages shall be free from any indications such as could mislead. When these packages are palletised, the particulars shall be given on a notice placed in an obvious position on at least two sides of the pallet.
Appendix
Non-exhaustive list of large-fruited and summer pear varieties
Small-fruited and other varieties which do not appear in the table may be marketed as long as they meet the size requirements for other varieties as described in Section III of the standard.
Some of the varieties listed in the following table may be marketed under names for which trade mark protection has been sought or obtained in one or more countries. The first and second columns of the table do not intend to include such trade marks. References to known trade marks have been included in the third column for information only.
Legend:
L = Large-fruited variety SP = Summer pear, for which no minimum size is required.
PART 7
Marketing standard for strawberries
I. DEFINITION OF PRODUCE
This standard applies to strawberries of varieties (cultivars) grown from the genus Fragaria L. to be supplied fresh to the consumer, strawberries for industrial processing being excluded.
II. PROVISIONS CONCERNING QUALITY
The purpose of the standard is to define the quality requirements for strawberries, after preparation and packaging.
However, at stages following dispatch products may show in relation to the requirements of the standard:
```

### Retrieved: L_202302429EN / chunk_13

Resolution: document_chunk_sqlite

```text
However, a mixture of apples of distinctly different varieties may be packed together in a sales package provided they are uniform in quality and, for each variety concerned, in origin. Uniformity in size is not required.
The visible part of the contents of the package must be representative of the entire contents. Information lasered on single fruit should not lead to flesh or skin defects.
B. Packaging
The apples must be packed in such a way as to protect the produce properly. In particular, sales packages of a net weight exceeding 3 kg shall be sufficiently rigid to ensure proper protection of the produce.
The materials used inside the package must be clean and of a quality such as to avoid causing any external or internal damage to the produce. The use of materials, particularly of paper or stamps bearing trade specifications is allowed provided the printing or labelling has been done with non-toxic ink or glue.
Stickers individually affixed on the produce shall be such that, when removed, they neither leave visible traces of glue, nor lead to skin defects.
Packages must be free of all foreign matter.
VI. PROVISIONS CONCERNING MARKING
Each package
[( 10 )](#ntr10-L_202302429EN.001101-E0010)
must bear the following particulars, in letters grouped on the same side, legibly and indelibly marked, and visible from the outside.
A. Identification
Name and physical address of the packer and/or the dispatcher (for example street/city/region/postal code and, if different from the country of origin, the country).
This mention may be replaced:
- for all packages with the exception of pre-packages, by the officially issued or accepted code mark representing the packer and/or the dispatcher, indicated in close connection with the reference 'Packer and/or Dispatcher' (or equivalent abbreviations). The code mark shall be preceded by the ISO 3166 (alpha) country/area code of the recognising country, if not the country of origin; - for pre-packages only, by the name and the address of a seller established within the Union indicated in close connection with the mention 'Packed for:' or an equivalent mention. In this case, the labelling shall also include a code representing the packer and/or the dispatcher. The seller shall give all information deemed necessary by the inspection body as to the meaning of this code.
B. Nature of produce
- 'Apples' if the contents are not visible from the outside. - Name of the variety. In the case of a mixture of apples of distinctly different varieties, names of the different varieties. - The name of the variety may be replaced by a synonym. A trade name ( 11 - In the case of mutants with varietal protection, this variety name may replace the basic variety name. In case of mutants without varietal protection, this mutant name may only be indicated in addition to the basic variety name. - 'Miniature variety', where appropriate.
C. Origin of produce
Country of origin
[( 12 )](#ntr12-L_202302429EN.001101-E0012)
and, optionally, district where grown, or national, regional or local place name.
In the case of a mixture of distinctly different varieties of apples of different origins, the indication of each country of origin shall appear next to the name of the variety concerned.
D. Commercial specifications
- Class, - Size, or for fruit packed in rows and layers, number of units.
If identification is by the size, this should be expressed:
(a) for produce subject to the uniformity rules, as minimum and maximum diameters or minimum and maximum weights; (b) optionally, for produce not subject to the uniformity rules, as the diameter or the weight of the smallest fruit in the package followed by 'and over' or equivalent denomination or, where appropriate, followed by the diameter or weight of the largest fruit in the package.
E. Official control mark (optional)
Packages need not to bear the particulars mentioned in the first subparagraph of point VI, when they contain sales packages, clearly visible from the outside, and all bearing these particulars. These packages shall be free from any indications such as could mislead. When these packages are palletised, the particulars shall be given on a notice placed in an obvious position on at least two sides of the pallet.
Appendix
Non-exhaustive list of apple varieties
Fruits of varieties that are not part of the list must be graded according to their varietal characteristics.
Some of the varieties listed in the following table may be marketed under names for which trademark protection has been sought or obtained in one or more countries. The three first columns of the table hereunder do not intend to include such trademarks. References to known trademarks have been included in the fourth column for information only.
Legend:
```

### Retrieved: L_202302429EN / chunk_21

Resolution: document_chunk_sqlite

```text
- 'Lettuces', 'butterhead lettuces', 'batavia', 'crisphead lettuces (Iceberg)', 'cos lettuces', 'leaf lettuce' (or, for example and where appropriate, 'Oak leaf', 'Lollo bionda', 'Lollo rossa'), 'curled-leaved endives', 'broad-leaved (Batavian) endives', or equivalent denomination if the contents are not visible from the outside. - 'Grown under protection', or equivalent denomination where appropriate. - Name of the variety (optional). - 'Mixture of lettuces/endives', or equivalent denomination in the case of a mixture of lettuces and/or endives of distinctly different varieties, commercial types and/or colours. If the produce is not visible from the outside, the varieties, commercial types and/or colours, and the quantity of each in the package must be indicated.
C. Origin of produce
- Country of origin ( 25 - In the case of a mixture of lettuces and/or endives of distinctly different varieties, commercial types and/or colours of different origins, the indication of each country of origin shall appear next to the name of the variety, commercial type and/or colour concerned.
D. Commercial specifications
- Class, - Size, expressed by the minimum weight per unit, or number of units.
E. Official control mark (optional)
Packages need not to bear the particulars mentioned in the first subparagraph of point VI, when they contain sales packages, clearly visible from the outside, and all bearing these particulars. These packages shall be free from any indications such as could mislead. When these packages are palletised, the particulars shall be given on a notice placed in an obvious position on at least two sides of the pallet.
PART 5
Marketing standard for peaches and nectarines
I. DEFINITION OF PRODUCE
This standard applies to peaches and nectarines of varieties (cultivars) grown from Prunus persica Sieb. and Zucc., to be supplied fresh to the consumer, peaches and nectarines for industrial processing being excluded.
II. PROVISIONS CONCERNING QUALITY
The purpose of the standard is to define the quality requirements for peaches and nectarines, after preparation and packaging.
However, at stages following dispatch products may show in relation to the requirements of the standard:
- a slight lack of freshness and turgidity, - for products graded in classes other than the 'Extra' Class, a slight deterioration due to their development and their tendency to perish.
A. Minimum requirements
In all classes, subject to the special provisions for each class and the tolerances allowed, peaches and nectarines must be:
- intact, - sound; produce affected by rotting or deterioration such as to make it unfit for consumption is excluded, - clean, practically free of any visible foreign matter, - practically free from pests, - free from damage caused by pests affecting the flesh, - free of fruit split at the stalk cavity, - free of abnormal external moisture, - free of any foreign smell and/or taste.
The development and condition of peaches and nectarines must be such as to enable them:
- to withstand transportation and handling, and - to arrive in satisfactory condition at the place of destination.
B. Maturity requirements
The fruit must be sufficiently developed and display satisfactory ripeness. The minimum refractometric index of the flesh should be greater than or equal to 8° Brix
[( 26 )](#ntr26-L_202302429EN.001101-E0026)
.
C. Classification
Peaches and nectarines are classified into three classes, defined as follows:
(i) 'Extra' Class
Peaches and nectarines in this class must be of a superior quality. They must be characteristic of the variety.
The flesh must be perfectly sound.
They must be free from defects with the exception of very slight superficial defects, provided that these do not affect the general appearance of the produce, the quality, the keeping quality and presentation in the package.
(ii) Class I
Peaches and nectarines in this class must be of good quality. They must be characteristic of the variety. The flesh must be perfectly sound.
The following slight defects, however, may be allowed provided these do not affect the general appearance of the produce, the quality, the keeping quality and presentation in the package:
- a slight defect in shape, - a slight defect in development, - slight defects in colouring, - slight pressure marks not exceeding 1 cm 2 - slight skin defects which must not extend over more than: - 1,5 cm in length for defects of elongated shape, - 1 cm 2
(iii) Class II
```

### Retrieved: L_202302429EN / chunk_29

Resolution: document_chunk_sqlite

```text
The materials used inside the package must be clean and of a quality such as to avoid causing any external or internal damage to the produce. The use of materials, particularly paper or stamps bearing trade specifications is allowed, provided the printing or labelling has been done with non-toxic ink or glue.
Stickers individually affixed on the produce shall be such that, when removed, they neither leave visible traces of glue, nor lead to skin defects. Information lasered on single fruit should not lead to flesh or skin defect.
Packages must be free of all foreign matter.
VI. PROVISIONS CONCERNING MARKING
Each package
[( 37 )](#ntr37-L_202302429EN.001101-E0037)
must bear the following particulars, in letters grouped on the same side, legibly and indelibly marked, and visible from the outside:
A. Identification
Name and physical address of the packer and/or the dispatcher (for example street/city/region/postal code and, if different from the country of origin, the country).
This mention may be replaced:
- for all packages with the exception of pre-packages, by the officially issued or accepted code mark representing the packer and/or the dispatcher, indicated in close connection with the reference 'Packer and/or Dispatcher' (or equivalent abbreviations). The code mark shall be preceded by the ISO 3166 (alpha) country/area code of the recognising country, if not the country of origin; - for pre-packages only, by the name and the address of a seller established within the Union indicated in close connection with the mention 'Packed for:' or an equivalent mention. In this case, the labelling shall also include a code representing the packer and/or the dispatcher. The seller shall give all information deemed necessary by the inspection body as to the meaning of this code.
B. Nature of produce
- 'Sweet peppers' if the contents are not visible from the outside. - 'Mixture of sweet peppers', or equivalent denomination, in the case of a mixture of distinctly different commercial types and/or colours of sweet peppers. If the produce is not visible from the outside, the commercial types and/or colours and the quantity of each in the package must be indicated.
C. Origin of produce
Country of origin
[( 38 )](#ntr38-L_202302429EN.001101-E0038)
and, optionally, district where grown or national, regional or local place name.
In the case of a mixture of distinctly different commercial types and/or colours of sweet peppers of different origins, the indication of each country of origin shall appear next to the name of the commercial type and/or colour concerned.
D. Commercial specifications
- Class. - Size (if sized) expressed as minimum and maximum diameters or minimum and maximum weights. - Number of units (optional). - 'Hot' or equivalent denomination, where appropriate.
E. Official control mark (optional)
Packages need not to bear the particulars mentioned in the first subparagraph of point VI, when they contain sales packages, clearly visible from the outside, and all bearing these particulars. These packages shall be free from any indications such as could mislead. When these packages are palletised, the particulars shall be given on a notice placed in an obvious position on at least two sides of the pallet.
PART 9
Marketing standard for table grapes
I. DEFINITION OF PRODUCE
This standard applies to table grapes of varieties (cultivars) grown from Vitis vinifera L. to be supplied fresh to the consumer, table grapes for industrial processing being excluded.
II. PROVISIONS CONCERNING QUALITY
The purpose of the standard is to define the quality requirements for table grapes, after preparation and packaging.
However, at stages following dispatch products may show in relation to the requirements of the standard:
- a slight lack of freshness and turgidity, - for products graded in classes other than the 'Extra' Class, a slight deterioration due to their development and their tendency to perish.
A. Minimum requirements
In all classes, subject to the special provisions for each class and the tolerances allowed, bunches and berries must be:
- sound; produce affected by rotting or deterioration such as to make it unfit for consumption is excluded, - clean, practically free of any visible foreign matter, - practically free from pests, - practically free from damage caused by pests, - free of abnormal external moisture, - free of any foreign smell and/or taste.
In addition, berries must be:
- intact, - well formed, - normally developed.
Pigmentation due to sun is not a defect.
The development and condition of the table grapes must be such as to enable them:
```

### Retrieved table: L_202501271EN / table_67

```json
{
  "document_id": "L_202501271EN",
  "table_id": "table_67",
  "row_ids": [
    0
  ],
  "headers": [
    "Declaration of origin",
    "TRQ numbers",
    "TRQ numbers"
  ],
  "rows": [
    [
      "It is hereby certified that above mentioned products originate in the country indicated under Section “Country of origin”.",
      "09.4128 09.4149 09.4181 09.4001 09.4002 09.4004 09.4450 09.4451 09.4452 09.4453 09.4454 09.4455 09.4198 09.4199 09.4200 09.4202 09.4504 09.4505 09.4456 09.4317 09.4318 09.4354 09.4355 09.4319 09.4321 09.4329 09.4330 09.4287 09.4169 09.4211 09.4212 09.4214",
      "09.4215 09.4217 09.4251 09.4252 09.4253 09.4254 09.4255 09.4256 09.4257 09.4258 09.4259 09.4410 09.4411 09.4420 09.4269 09.4283 09.4289 09.4290 09.0090 09.0124 09.0125 09.0126 09.0127 09.0141 09.0165 09.0166 09.0167 09.0168 09.0169 09.0170 09.0171"
    ]
  ]
}
```

### Retrieved table: L_2021302EN.01000101 / table_5

```json
{
  "document_id": "L_2021302EN.01000101",
  "table_id": "table_5",
  "row_ids": [
    0
  ],
  "headers": null,
  "rows": [
    [
      "‘ Origin",
      "All third countries except Brazil, Thailand, Argentina and United Kingdom’"
    ]
  ]
}
```

### Retrieved table: L_2021302EN.01000101 / table_4

```json
{
  "document_id": "L_2021302EN.01000101",
  "table_id": "table_4",
  "row_ids": [
    0
  ],
  "headers": null,
  "rows": [
    [
      "‘ Origin",
      "All third countries except Brazil, Thailand, Argentina and United Kingdom’"
    ]
  ]
}
```

### Retrieved table: L_202501344EN / table_13

```json
{
  "document_id": "L_202501344EN",
  "table_id": "table_13",
  "row_ids": [
    0
  ],
  "headers": null,
  "rows": [
    [
      "‘ Origin",
      "All third countries except Argentina, Belarus, Brazil, Russia, Thailand and the United Kingdom’"
    ]
  ]
}
```

### Retrieved table: L_2021058EN.01001701 / table_15

```json
{
  "document_id": "L_2021058EN.01001701",
  "table_id": "table_15",
  "row_ids": [
    0
  ],
  "headers": null,
  "rows": [
    [
      "‘ Origin",
      "All third countries except Brazil, Thailand and the United Kingdom’"
    ]
  ]
}
```

## global_natural_008

When does the TIR Convention enter into force after the required States have completed the specified signature or ratification steps?

Draft reference: Six months after five eligible States complete the specified steps; further Contracting Parties are covered six months after their deposit. Do not infer actual deposit dates.

Retrieval execution status: success (NOT relevance)

### Expected: L_2009165EN.01000101 / chunk_10

Resolution: document_chunk_sqlite

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

### Retrieved: L_2013207EN.01000101 / chunk_37

Resolution: document_chunk_sqlite

```text
1. The name and full address of the law firm completing the questionnaire. 2. The law firm's relevant experience, which could include experience in legislative and constitutional processes as they relate to the implementation of international treaties in the State, and specific experience in CTC related issues including any experience in advising either a government on implementation and enforcement of the Cape Town Convention or the private sector, or enforcement of creditor's rights in the State which is proposed to be added to the Cape Town List; 3. Whether the law firm is involved or intends to be involved in any transactions that may benefit from a reduction of minimum premium rates if the proposed State is added to the CTC list; ( 21 4. The date on which this questionnaire was completed.
II. QUESTIONS
1. Qualifying declarations
1.1 Has the State ( 22 1.2 Please describe the way in which the declarations made differ, if at all, from the requirements referred to in Question 1.1. 1.3 Please confirm that the State has not made any of the declarations listed in Article 3 of Annex 1 to Appendix II of the ASU.
1. Ratification
1.1 Has the State ratified, accepted, approved or acceded to the Cape Town Convention and Aircraft Protocol ("Convention")? Please could you state the date of ratification/accession and briefly describe the State's process of accession to or ratification of the Convention? 1.2 Do the Convention and Qualifying Declarations ("QD") made have the force of law in the whole territory of the State without any further act, implementing legislation or the passing of any further law or regulation? 1.3 If so, please briefly explain the process that gives the Convention and QDs the force of law.
1. Effect of national and local law
1.1 Describe and list, if applicable, the implementing legislation and regulation(s) with respect to the Convention and each QD made by the State. 1.2 Would the Convention and QDs made, as translated into national law ( 23 ( 24 1.3 Are there any existing gaps in the implementation of the Convention and QDs? If so, please describe. ( 25
1. Court and administrative decisions
1.1. Please describe any matters, including judicial, regulatory, or administrative practice which could be expected to result in the courts, authorities or administrative bodies failing to give full force and effect to the Convention and QDs. ( 26 ( 27 1.2. To your knowledge, has there been any judicial or administrative enforcement action taken by a creditor under the Convention? If so, please describe the action and indicate whether it was successful. 1.3. To your knowledge, since ratification/implementation, have the courts in that State refused in any instance to enforce loan obligations of a debtor or guarantor in the State contrary to the Convention and QDs? 1.4. To your knowledge, are there any other matters that may impact whether courts and administrative bodies should be expected to act in a manner consistent with the Convention and QDs? If so, please specify.
Appendix III
Minimum interest rates
The provision of official financing support shall not offset or compensate, in part or in full, for the appropriate premium rate to be charged for the risk of non-repayment pursuant to the provisions of Appendix II.
1. MINIMUM FLOATING INTEREST RATE
```

### Retrieved: L_2013218EN.01000801 / chunk_2

Resolution: document_chunk_sqlite

```text
(7) Common definitions in this area are important in order to ensure a consistent approach in the Member States to the application of this Directive.
(8) There is a need to achieve a common approach to the constituent elements of criminal offences by introducing common offences of illegal access to an information system, illegal system interference, illegal data interference, and illegal interception.
(9) Interception includes, but is not necessarily limited to, the listening to, monitoring or surveillance of the content of communications and the procuring of the content of data either directly, through access and use of the information systems, or indirectly through the use of electronic eavesdropping or tapping devices by technical means.
(10) Member States should provide for penalties in respect of attacks against information systems. Those penalties should be effective, proportionate and dissuasive and should include imprisonment and/or fines.
(11) This Directive provides for criminal penalties at least for cases which are not minor. Member States may determine what constitutes a minor case according to their national law and practice. A case may be considered minor, for example, where the damage caused by the offence and/or the risk to public or private interests, such as to the integrity of a computer system or to computer data, or to the integrity, rights or other interests of a person, is insignificant or is of such a nature that the imposition of a criminal penalty within the legal threshold or the imposition of criminal liability is not necessary.
(12) The identification and reporting of threats and risks posed by cyber attacks and the related vulnerability of information systems is a pertinent element of effective prevention of, and response to, cyber attacks and to improving the security of information systems. Providing incentives to report security gaps could add to that effect. Member States should endeavour to provide possibilities for the legal detection and reporting of security gaps.
(13) It is appropriate to provide for more severe penalties where an attack against an information system is committed by a criminal organisation, as defined in Council Framework Decision 2008/841/JHA of 24 October 2008 on the fight against organised crime ( 3
(14) Setting up effective measures against identity theft and other identity-related offences constitutes another important element of an integrated approach against cybercrime. Any need for Union action against this type of criminal behaviour could also be considered in the context of evaluating the need for a comprehensive horizontal Union instrument.
(15) The Council Conclusions of 27 to 28 November 2008 indicated that a new strategy should be developed with the Member States and the Commission, taking into account the content of the 2001 Council of Europe Convention on Cybercrime. That Convention is the legal framework of reference for combating cybercrime, including attacks against information systems. This Directive builds on that Convention. Completing the process of ratification of that Convention by all Member States as soon as possible should be considered to be a priority.
(16) Given the different ways in which attacks can be conducted, and given the rapid developments in hardware and software, this Directive refers to tools that can be used in order to commit the offences laid down in this Directive. Such tools could include malicious software, including those able to create botnets, used to commit cyber attacks. Even where such a tool is suitable or particularly suitable for carrying out one of the offences laid down in this Directive, it is possible that it was produced for a legitimate purpose Motivated by the need to avoid criminalisation where such tools are produced and put on the market for legitimate purposes, such as to test the reliability of information technology products or the security of information systems, apart from the general intent requirement, a direct intent requirement that those tools be used to commit one or more of the offences laid down in this Directive must be also fulfilled.
(17) This Directive does not impose criminal liability where the objective criteria of the offences laid down in this Directive are met but the acts are committed without criminal intent, for instance where a person does not know that access was unauthorised or in the case of mandated testing or protection of information systems, such as where a person is assigned by a company or vendor to test the strength of its security system. In the context of this Directive, contractual obligations or agreements to restrict access to information systems by way of a user policy or terms of service, as well as labour disputes as regards the access to and use of information systems of an employer for private purposes, should not incur criminal liability where the access under such circumstances would be deemed unauthorised and thus would constitute the sole basis for criminal proceedings. This Directive is without prejudice to the right of access to information as laid down in national and Union law, while at the same time it may not serve as a justification for unlawful or arbitrary access to information.
```

### Retrieved: L_2004241EN.01002101 / chunk_9

Resolution: document_chunk_sqlite

```text
1. The arbitration tribunal shall lay down its own procedure. Its decisions shall be taken by majority vote. Its award, which shall be based on this Convention, shall be final.
2. The procedure for the settlement of disputes shall not apply to disputes relating to questions within the competence of the European Community or to the definition of the scope of that competence between Parties which are members of the European Community or between such members and the Community.
FINAL CLAUSES
Article 37
Signature, ratification, acceptance, approval
1. This Convention shall be open for signature by the Member States of the Council of Europe and the European Community. It is subject to ratification, acceptance or approval. Instruments of ratification, acceptance or approval shall be deposited with the Secretary-General of the Council of Europe.
2. No State party to the European Convention on the Protection of Animals during International Transport, opened for signature in Paris on 13 December 1968, may deposit its instrument of ratification, acceptance or approval unless it has already denounced the said Convention or denounces it simultaneously.
3. This Convention shall enter into force six months after the date on which four States have expressed their consent to be bound by this Convention in accordance with the provisions of the preceding paragraphs.
4. Whenever, in application of the preceding two paragraphs, the denunciation of the Convention of 13 December 1968 would not become effective simultaneously with the entry into force of this Convention, a Contracting State or the European Community may, when depositing its instrument of ratification, acceptance or approval, declare that it will continue to apply the Convention of 13 December 1968 until the entry into force of this Convention.
5. In respect of any signatory State or the European Community which subsequently expresses its consent to be bound by it, this Convention shall enter into force six months after the date of the deposit of the instrument of ratification, acceptance or approval.
Article 38
Accession of non-Member States
1. After the entry into force of this Convention, the Committee of Ministers of the Council of Europe may invite any other non-Member State of the Council to accede to this Convention by a decision taken by the majority provided for in Article 20.d of the Statute of the Council of Europe and by the unanimous vote of the representatives of the Contracting States entitled to sit on the Committee.
2. In respect of any acceding State, this Convention shall enter into force six months after the date of deposit of the instrument of accession with the Secretary-General of the Council of Europe.
Article 39
Territorial clause
1. Any State or the European Community may, at the time of signature or when depositing its instrument of ratification, acceptance, approval or accession, specify the territory or territories to which this Convention shall apply.
2. Any State or the European Community may at any later date, by a declaration addressed to the Secretary-General of the Council of Europe, extend the application of this Convention to any other territory specified in the declaration. In respect of such territory this Convention shall enter into force six months after the date of receipt of such declaration by the Secretary-General.
3. Any declaration made under the two preceding paragraphs may, in respect of any territory specified in such declaration, be withdrawn by a notification addressed to the Secretary-General. The withdrawal shall become effective six months after the date of receipt of such notification by the Secretary-General.
Article 40
Denunciation
1. Any Party may at any time denounce this Convention by means of a notification addressed to the Secretary-General of the Council of Europe.
2. Such denunciation shall become effective six months following the date of receipt of such notification by the Secretary-General.
Article 41
Notifications
The Secretary-General of the Council of Europe shall notify the Member States of the Council of Europe, the European Community and any State which has acceded or has been invited to accede to this Convention of:
(a) any signature; (b) the deposit of any instrument of ratification, acceptance, approval or accession; (c) any date of entry into force of this Convention in accordance with Articles 37 and 38; (d) any other act, notification or communication relating to this Convention.
In witness whereof the undersigned, being duly authorised thereto, have signed this Convention.
Done at ..., this ... day of ..., in English and French, both texts being equally authentic, in a single copy which shall be deposited in the archives of the Council of Europe. The Secretary-General of the Council of Europe shall transmit certified copies to each Member State of the Council of Europe, to the European Community and to any State invited to accede to this Convention.
EXPLANATORY REPORT
(as adopted by the Committee of Ministers on 11 June 2003)
```

### Retrieved: L_2009121EN.01000301 / chunk_19

Resolution: document_chunk_sqlite

```text
(a) inform all Contracting States of: (i) each new signature or deposit of an instrument of ratification, acceptance, approval or accession, together with the date thereof; (ii) the date of entry into force of this Convention; (iii) each declaration made in accordance with this Convention, together with the date thereof; (iv) the withdrawal or amendment of any declaration, together with the date thereof; and (v) the notification of any denunciation of this Convention together with the date thereof and the date on which it takes effect; (b) transmit certified true copies of this Convention to all Contracting States; (c) provide the Supervisory Authority and the Registrar with a copy of each instrument of ratification, acceptance, approval or accession, together with the date of deposit thereof, of each declaration or withdrawal or amendment of a declaration and of each notification of denunciation, together with the date of notification thereof, so that the information contained therein is easily and fully available; and (d) perform such other functions customary for depositaries.
IN WITNESS WHEREOF the undersigned Plenipotentiaries, having been duly authorised, have signed this Convention.
DONE at Cape Town, this sixteenth day of November, two thousand and one, in a single original in the English, Arabic, Chinese, French, Russian and Spanish languages, all texts being equally authentic, such authenticity to take effect upon verification by the Joint Secretariat of the Conference under the authority of the President of the Conference within ninety days hereof as to the conformity of the texts with one another.
PROTOCOL
to the Convention on international interests in mobile equipment on matters specific to aircraft equipment
THE STATES PARTIES TO THIS PROTOCOL,
CONSIDERING it necessary to implement the Convention on international interests in mobile equipment (hereinafter referred to as 'the Convention') as it relates to aircraft equipment, in the light of the purposes set out in the preamble to the Convention,
MINDFUL of the need to adapt the Convention to meet the particular requirements of aircraft finance and to extend the sphere of application of the Convention to include contracts of sale of aircraft equipment,
MINDFUL of the principles and objectives of the Convention on International Civil Aviation, signed at Chicago on 7 December 1944,
HAVE AGREED upon the following provisions relating to aircraft equipment:
CHAPTER I
SPHERE OF APPLICATION AND GENERAL PROVISIONS
Article I
Defined terms
1. In this Protocol, except where the context otherwise requires, terms used in it have the meanings set out in the Convention.
2. In this Protocol the following terms are employed with the meanings set out below:
```

### Retrieved: 31981D0691en / chunk_8

Resolution: document_chunk_sqlite

```text
This Convention shall enter into force on the 30th day following the date of deposit of the eighth instrument of ratification, acceptance or approval by States referred to in paragraph 1 of Article XXVI of this Convention. 2. With respect to each State or regional economic integration organization which subsequent to the date of entry into force of this Convention deposits an instrument of ratification, acceptance, approval or accession, the Convention shall enter into force on the 30th day following such deposit. Article XXIX 1. This Convention shall be open for accession by any State interested in research or harvesting activities in relation to the marine living resources to which this Convention applies. 2. This Convention shall be open for accession by regional economic integration organizations constituted by sovereign States which include among their members one or more States members of the Commission and to which the States members of the organization have transferred in whole or in part, competences with regard to the matters covered by this Convention. The accession of such regional economic integration organizations shall be the subject of consultations among members of the Commission. Article XXX 1. This Convention may be amended at any time. 2. If one-third of the members of the Commission request a meeting to discuss a proposed amendement, the Depositary shall call such a meeting. 3. An amendment shall enter into force when the Depositary has received instruments of ratification, acceptance or approval thereof from all the members of the Commission. 4. Such amendment shall thereafter enter into force as to any other Contracting Party when notice of ratification, acceptance or approval by it has been received by the Depositary. Any such Contracting Party from which no such notice has been received within a period of one year from the date of entry into force of the amendment in accordance with paragraph 3 above shall be deemed to have withdrawn from this Convention. Article XXXI 1. Any Contracting Party may withdraw from this Convention on 30 June of any year, by giving written notice not later than 1 January of the same year to the Depositary, which, upon receipt of such a notice, shall communicate it forthwith to the other Contracting Parties. 2. Any other Contracting Party may, within 60 days of the receipt of a copy of such a notice from the Depositary, give written notice of withdrawal to the Depositary in which case the Convention shall cease to be in force on 30 June of the same year with respect to the Contracting Party giving such notice. 3. Withdrawal from this Convention by any Member of the Commission shall not affect its financial obligations under this Convention. Article XXXII The Depositary shall notify all Contracting Parties of the following: (a) signatures of this Convention and the deposit of instruments of ratification, acceptance, approval or accession; (b) the date of entry into force of this Convention and of any amendment thereto. Article XXXIII 1. This Convention, of which the English, French, Russian and Spanish texts are equally authentic, shall be deposited with the Government of Australia which shall transmit duly certified copies thereof to all signatory and acceding Parties. 2. This Convention shall be registered by the Depositary pursuant to Article 102 of the Charter of the United Nations. In witness whereof the undersigned, being duly authorized, have signed this Convention. Drawn up at Canberra this 20th day of May 1980. ANNEX ARBITRAL TRIBUNAL The arbitral tribunal referred to in paragraph 3 of Article XXV shall be composed of three arbitrators who shall be appointed as follows: The Party commencing proceedings shall communicate the name of an arbitrator to the other Party which, in turn, within a period of 40 days following such notification, shall communicate the name of the second arbitrator. The Parties shall, within a period of 60 days following the appointment of the second arbitrator, appoint the third arbitrator, who shall not be a national of either Party and shall not be of the same nationality as either of the first two arbitrators. The third arbitrator shall preside over the tribunal. If the second arbitrator has not been appointed within the prescribed period, or if the Parties have not reached agreement within the prescribed period on the appointment of the third arbitrator, that arbitrator shall be appointed, at the request of either Party, by the Secretary-General of the Permanent Court of Arbitration, from among persons of international standing not having the nationality of a State which is a Party to this Convention. The arbitral tribunal shall decide where its headquarters will be located and shall adopt its own rules of procedure. The award of the arbitral tribunal shall be made by a majority of its members, who may not abstain from voting. Any Contracting Party which is not a Party to the dispute may intervene in the proceedings with the consent of the arbitral tribunal.
```

### Retrieved: L_2005032EN.01000101 / chunk_18

Resolution: document_chunk_sqlite

```text
1.55.1. Entry into force 1. This Convention shall enter into force 30 days after the deposit of instruments of ratification, acceptance, approval or accession by: (a) three States situated north of the 20 o (b) seven States situated south of the 20 o 2. If, within three years of its adoption, this Convention has not been ratified by three of the States referred to in paragraph 1(a), this Convention shall enter into force six months after the deposit of the thirteenth instrument of ratification, acceptance, approval or accession or in accordance with paragraph 1, whichever is the earlier. 3. For each State, entity referred to in Article 305(1)(c), (d) and (e) of the 1982 Convention which is situated in the Convention Area, or regional economic integration organisation which ratifies, formally confirms, accepts or approves the Convention or accedes thereto after the entry into force of this Convention, this Convention shall enter into force on the thirtieth day following the deposit of its instrument of ratification, formal confirmation, acceptance, approval or accession.
1.56. Article 37
1.56.1. Reservations and exceptions
No reservations or exceptions may be made to this Convention.
1.57. Article 38
1.57.1. Declarations and statements
Article 37 does not preclude a State, entity referred to in Article 305(1)(c), (d) and (e) of the 1982 Convention which is situated in the Convention Area, or regional economic integration organisation, when signing, ratifying or acceding to this Convention, from making declarations or statements, however phrased or named, with a view, inter alia, to the harmonisation of its laws and regulations with the provisions of this Convention, provided that such declarations or statements do not purport to exclude or to modify the legal effect of the provisions of this Convention in their application to that State, entity or regional economic integration organisation.
1.58. Article 39
1.58.1. Relation to other agreements
This Convention shall not alter the rights and obligations of Contracting Parties, and fishing entities referred to in Article 9(2), which arise from other agreements compatible with this Convention and which do not affect the enjoyment by other Contracting Parties of their rights or the performance of their obligations under this Convention.
1.59. Article 40
1.59.1. Amendment 1. Any member of the Commission may propose amendments to this Convention to be considered by the Commission. Any such proposal shall be made by written communication addressed to the Executive Director at least 60 days before the meeting of the Commission at which it is to be considered. The Executive Director shall promptly circulate such communication to all members of the Commission. 2. Amendments to this Convention shall be considered at the annual meeting of the Commission unless a majority of the members request a special meeting to consider the proposed amendment. A special meeting may be convened on not less than 60 days notice. Amendments to this Convention shall be adopted by consensus. The text of any amendment adopted by the Commission shall be transmitted promptly by the Executive Director to all members of the Commission. 3. Amendments to this Convention shall enter into force for the Contracting Parties ratifying or acceding to them on the 30th day following the deposit of instruments of ratification or accession by a majority of Contracting Parties. Thereafter, for each Contracting Party ratifying or acceding to an amendment after the deposit of the required number of such instruments, the amendment shall enter into force on the thirtieth day following the deposit of its instrument of ratification or accession.
1.60. Article 41
1.60.1. Annexes 1. The Annexes form an integral part of this Convention and, unless expressly provided otherwise, a reference to this Convention or to one of its Parts includes a reference to the Annexes relating thereto. 2. The Annexes to this Convention may be revised from time to time and any member of the Commission may propose revisions to an Annex. Notwithstanding the provisions of Article 40, if a revision to an Annex is adopted by consensus at a meeting of the Commission, it shall be incorporated in this Convention and shall take effect from the date of its adoption or from such other date as may be specified in the revision.
1.61. Article 42
```

### Retrieved: L_2009133EN.01000101 / chunk_7

Resolution: document_chunk_sqlite

```text
1. At the time of signature, acceptance, approval or accession, a Regional Economic Integration Organisation may declare that it exercises competence over all the matters governed by this Convention and that its Member States will not be Parties to this Convention but shall be bound by virtue of the signature, acceptance, approval or accession of the Organisation.
2. In the event that a declaration is made by a Regional Economic Integration Organisation in accordance with paragraph 1, any reference to a 'Contracting State' or 'State' in this Convention shall apply equally, where appropriate, to the Member States of the Organisation.
Article 31
Entry into force
1. This Convention shall enter into force on the first day of the month following the expiration of three months after the deposit of the second instrument of ratification, acceptance, approval or accession referred to in Article 27.
2. Thereafter this Convention shall enter into force:
(a) for each State or Regional Economic Integration Organisation subsequently ratifying, accepting, approving or acceding to it, on the first day of the month following the expiration of three months after the deposit of its instrument of ratification, acceptance, approval or accession; (b) for a territorial unit to which this Convention has been extended in accordance with Article 28(1), on the first day of the month following the expiration of three months after the notification of the declaration referred to in that Article.
Article 32
Declarations
1. Declarations referred to in Articles 19, 20, 21, 22 and 26 may be made upon signature, ratification, acceptance, approval or accession or at any time thereafter, and may be modified or withdrawn at any time.
2. Declarations, modifications and withdrawals shall be notified to the depositary.
3. A declaration made at the time of signature, ratification, acceptance, approval or accession shall take effect simultaneously with the entry into force of this Convention for the State concerned.
4. A declaration made at a subsequent time, and any modification or withdrawal of a declaration, shall take effect on the first day of the month following the expiration of three months after the date on which the notification is received by the depositary.
5. A declaration under Articles 19, 20, 21 and 26 shall not apply to exclusive choice of court agreements concluded before it takes effect.
Article 33
Denunciation
1. This Convention may be denounced by notification in writing to the depositary. The denunciation may be limited to certain territorial units of a non-unified legal system to which this Convention applies.
2. The denunciation shall take effect on the first day of the month following the expiration of 12 months after the date on which the notification is received by the depositary. Where a longer period for the denunciation to take effect is specified in the notification, the denunciation shall take effect upon the expiration of such longer period after the date on which the notification is received by the depositary.
Article 34
Notifications by the depositary
The depositary shall notify the Members of the Hague Conference on Private International Law, and other States and Regional Economic Integration Organisations which have signed, ratified, accepted, approved or acceded in accordance with Articles 27, 29 and 30 of the following:
(a) the signatures, ratifications, acceptances, approvals and accessions referred to in Articles 27, 29 and 30; (b) the date on which this Convention enters into force in accordance with Article 31; (c) the notifications, declarations, modifications and withdrawals of declarations referred to in Articles 19, 20, 21, 22, 26, 28, 29 and 30; (d) the denunciations referred to in Article 33.
In witness whereof the undersigned, being duly authorised thereto, have signed this Convention.
Done at The Hague, on 30 June 2005, in the English and French languages, both texts being equally authentic, in a single copy which shall be deposited in the archives of the Government of the Kingdom of the Netherlands, and of which a certified copy shall be sent, through diplomatic channels, to each of the Member States of the Hague Conference on Private International Law as of the date of its Twentieth Session and to each State which participated in that Session.
ANNEX II
Declaration by the European Community in accordance with Article 30 of the Convention on Choice of Court Agreements
The European Community declares, in accordance with Article 30 of the Convention on Choice of Court Agreements, that it exercises competence over all the matters governed by this Convention. Its Member States will not sign, ratify, accept or approve the Convention, but shall be bound by the Convention by virtue of its conclusion by the European Community.
```

### Retrieved: L_2005015EN.01000901 / chunk_13

Resolution: document_chunk_sqlite

```text
1. This Convention shall enter into force fifteen (15) months after the deposit with the Depositary of the seventh instrument of ratification, acceptance, approval, or accession of the Parties to the 1949 Convention that were Parties to that Convention on the date this Convention was opened for signature.
2. After the date of entry into force of this Convention, with respect to each State or regional economic integration organization that meets the requirements of Article XXVII or Article XXX, this Convention shall enter into force for said State or regional economic integration organization on the thirtieth (30th) day following the deposit of its instrument of ratification, acceptance, approval, or accession.
3. Upon entry into force of this Convention, this Convention shall prevail, as between Parties to this Convention and the 1949 Convention, over the 1949 Convention.
4. Upon the entry into force of this Convention, conservation and management measures and other arrangements adopted by the Commission under the 1949 Convention shall remain in force until such time as they expire, are terminated by a decision of the Commission, or are replaced by other measures or arrangements adopted pursuant to this Convention.
5. Upon entry into force of this Convention, a Party to the 1949 Convention that has not yet consented to be bound by this Convention shall be deemed to remain a member of the Commission unless such Party elects not to remain a member of the Commission by so notifying the Depositary in writing prior to the entry into force of this Convention.
6. Upon entry into force of this Convention for all Parties to the 1949 Convention, the 1949 Convention shall be considered as terminated in accordance with the relevant rules of international law as reflected in Article 59 of the Vienna Convention on the Law of Treaties.
Article XXXII
Provisional application
1. In accordance with its laws and regulations, a State or regional economic integration organization that meets the requirements of Article XXVII or Article XXX of this Convention may apply this Convention provisionally by so notifying the Depositary in writing. Such provisional application shall commence on the later of the date of entry into force of this Convention and the date of receipt of such notification by the Depositary.
2. Provisional application of this Convention by a State or regional economic integration organization referred to in paragraph 1 of this Article shall terminate upon entry into force of this Convention for that State or regional economic integration organization, or upon notification to the Depositary by that State or regional economic integration organization of its intention to terminate its provisional application of this Convention.
Article XXXIII
Reservations
No reservations may be made to this Convention.
Article XXXIV
Amendments
1. Any member of the Commission may propose an amendment to the Convention by providing to the Director the text of a proposed amendment at least sixty (60) days in advance of a meeting of the Commission. The Director shall provide a copy of this text to all other members promptly.
2. Amendments to the Convention shall be adopted in accordance with Article IX, paragraph 2, of this Convention.
3. Amendments to this Convention shall enter into force ninety (90) days after all Parties to the Convention at the time the amendments were approved have deposited their instruments of ratification, acceptance, or approval of such amendments with the Depositary.
4. States or regional economic integration organizations that become Parties to this Convention after the entry into force of amendments to the Convention or its annexes shall be considered to be Party to the Convention as amended.
Article XXXV
Annexes
1. The Annexes to this Convention form an integral part thereof and, unless expressly provided otherwise, a reference to this Convention includes a reference to the Annexes thereto.
2. Any member of the Commission may propose an amendment to an Annex to the Convention by providing to the Director the text of a proposed amendment at least sixty (60) days in advance of a meeting of the Commission. The Director shall provide a copy of this text to all other members promptly.
3. Amendments to the Annexes shall be adopted in accordance with Article IX, paragraph 2, of this Convention.
4. Unless otherwise agreed, amendments to an Annex shall enter into force for all members of the Commission ninety (90) days after their adoption pursuant to paragraph 3 of this Article.
Article XXXVI
Withdrawal
```

### Retrieved table: L_2015250EN.01003801 / table_7

```json
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
}
```

### Retrieved table: L_2020163EN.01000101 / table_34

```json
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
}
```

### Retrieved table: L_2015250EN.01003801 / table_7

```json
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
}
```

### Retrieved table: L_2015250EN.01003801 / table_7

```json
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
}
```

### Retrieved table: L_2015250EN.01003801 / table_7

```json
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
```

## global_natural_009

Who may request a meeting of the Committee on Trade in Goods, and what is it meant to consider?

Draft reference: A Party or the Trade Committee may request the meeting, to consider matters arising under the relevant Chapter; preserve the agreement-specific scope.

Retrieval execution status: success (NOT relevance)

### Expected: L_2011127EN.01000101 / chunk_8

Resolution: document_chunk_sqlite

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

### Retrieved: L_2019293EN.01010501 / chunk_1

Resolution: document_chunk_sqlite

```text
14.11.2019 EN Official Journal of the European Union L 293/105
COUNCIL DECISION (EU) 2019/1905
of 8 November 2019
requesting the Commission to submit a study on the Union's options to update the existing legislation on the production and marketing of plant reproductive material, and a proposal, if appropriate in view of the outcomes of the study
THE COUNCIL OF THE EUROPEAN UNION
Having regard to the Treaty on the Functioning of the European Union, and in particular Article 241 thereof,
Whereas:
(1) On 6 May 2013, the Commission submitted to the European Parliament and to the Council a proposal for a Regulation on the production and making available on the market of plant reproductive material. The proposal aimed to consolidate and update the existing legislation in order to address several areas of concern, such as: the complexity, rigidity and fragmentation of existing legislation; its non-harmonised implementation in Member States, resulting in obstacles to the establishment of a level playing field for all operators; the need to improve its alignment with other legislative acts that concern the sector and its coherence with other policies; the existence of room for cost reductions and efficiency gains; the need to adapt to technical progress in plant breeding and to the evolution of the European and global market of plant reproductive material; and the conservation of agro-biodiversity and plant genetic resources.
(2) On 11 March 2014, the European Parliament rejected the Commission proposal and called on the Commission to withdraw the proposal and submit a new one ( 1
(3) The Council considers that the concerns which the Commission aimed to address through its 2013 proposal are still relevant, and that a study is necessary in order to assess the options to update the existing legislative framework, in accordance with the Interinstitutional Agreement of 13 April 2016 on Better Law-Making ( 2
HAS ADOPTED THIS DECISION:
Article 1
The Council requests the Commission to submit, by 31 December 2020, a study on the options to update the existing legislation on the production and marketing of plant reproductive material.
Article 2
1. The Council requests the Commission to submit a proposal, if appropriate in view of the outcomes of the study, or otherwise to inform the Council of alternative measures required as a follow-up to the study.
2. In accordance with the usual practice, the Council requests the Commission to ensure that the proposal is accompanied by an impact assessment.
Article 3
This Decision shall enter into force on the day of its publication in the Official Journal of the European Union .
Done at Brussels, 8 November 2019.
For the Council
The President
L. ANDERSSON
[( 1 )](#ntc1-L_2019293EN.01010501-E0001)
European Parliament legislative resolution of 11 March 2014 (
[OJ C 378, 9.11.2017, p. 303](http://publications.europa.eu/resource/oj/JOC_2017_378_R_TOC)
).
[( 2 )](#ntc2-L_2019293EN.01010501-E0002)
[OJ L 123, 12.5.2016, p. 1](http://publications.europa.eu/resource/oj/JOL_2016_123_R_TOC)
.
```

### Retrieved: L_2011288EN.01001601 / chunk_3

Resolution: document_chunk_sqlite

```text
1. Draft minutes of each meeting shall be drawn up by the Secretariat of the Trade Committee, normally within 21 days from the end of the meeting.
2. The minutes shall, as a general rule, summarise each item on the agenda, specifying where applicable:
(a) the documents submitted to the Trade Committee; (b) any statement that a member of the Trade Committee has asked to be entered; and (c) the decisions adopted, recommendations made, statements agreed upon and conclusions adopted on specific items.
1. The minutes shall also include a list of members of the Trade Committee or their alternate representatives who took part in the meeting, a list of the members of the delegations accompanying them and a list of any observers or experts to the meeting.
2. The minutes shall be approved in writing by both Parties within 28 days of the date of the meeting or by any other date agreed by the Parties. Once approved, two copies of the minutes shall be signed by the Secretariat of the Trade Committee and each of the Parties shall receive one original copy of these authentic documents. Copies of the signed minutes shall be forwarded to the members of the Trade Committee.
Article 11
Reports
The Trade Committee shall report to the Joint Committee of the Framework Agreement on its activities and those of its Specialised Committees, Working Groups and other bodies at each regular meeting of the Joint Committee as provided in Article 15.1.5 of the Agreement.
Article 12
Decisions and Recommendations
1. The Trade Committee shall adopt decisions and recommendations by agreement between the Parties, as provided for in Article 15.4 of the Agreement.
2. In the period between meetings, the Trade Committee may adopt decisions or recommendations by written procedure if both Parties agree. The written procedure shall consist of an exchange of notes between the Chairpersons of the Trade Committee.
3. Where the Trade Committee is empowered under the Agreement to adopt decisions or recommendations, such acts shall be entitled 'Decision' or 'Recommendation' respectively. The Secretariat of the Trade Committee shall give any decision or recommendation a serial number, the date of adoption and a description of their subject-matter. Each decision shall provide for the date of its entry into force.
4. Decisions and recommendations adopted by the Trade Committee shall be authenticated by two authentic copies signed by the Chairpersons of the Trade Committee.
Article 13
Publicity and Confidentiality
1. Unless otherwise decided, the meetings of the Trade Committee shall not be public.
2. When a Party submits information considered as confidential under its laws and regulations to the Trade Committee, Specialised Committees, Working Groups or any other bodies, the other Party shall treat that information as confidential as provided in Article 15.1.7 of the Agreement.
3. Each Party may decide on the publication of the decisions and recommendations of the Trade Committee in its respective official publication.
Article 14
Expenses
1. Each Party shall meet any expenses it incurs as a result of participating in the meetings of the Trade Committee, both with regard to staff, travel and subsistence expenditure and with regard to postal and telecommunications expenditure.
2. Expenditure in connection with the organisation of meetings and reproduction of documents shall be borne by the Party hosting the meeting.
Article 15
Specialised Committees and Working Groups
1. The Trade Committee shall be assisted in the performance of its duties by the Specialised Committees and Working Groups established under the auspices of the Trade Committee.
2. The Trade Committee shall be informed of the contact points designated by each Specialised Committee and Working Group. All correspondences, documents and communications including the exchange of e-mails between the contact points of each Specialised Committee and Working Group regarding the implementation of the Agreement shall be forwarded to the Secretariat of the Trade Committee simultaneously.
3. The Trade Committee at each regular meeting shall receive reports from each Specialised Committee and Working Group on its activities.
4. Each Specialised Committee and Working Group may establish its own rules of procedure which shall be reported to the Trade Committee.
DRAFT
DECISION No ... OF THE EU-KOREA TRADE COMMITTEE
of
on the establishment of a list of arbitrators referred to in Article 14.18 of the Free Trade Agreement between the European Union and its Member States, of the one part, and the Republic of Korea, of the other part
THE TRADE COMMITTEE,
Having regard to the Free Trade Agreement between the European Union and its Member States, of the one part, and the Republic of Korea, of the other part, signed in Brussels on 6 October 2010 ('the Parties' and 'the Agreement'), and in particular Article 14.18 thereof,
Whereas:
(1) The Agreement provides for a dispute settlement mechanism whereby disputes are solved through recourse to a panel of arbitrators.
```

### Retrieved: L_2011288EN.01001601 / chunk_2

Resolution: document_chunk_sqlite

```text
This Decision shall enter into force on ...
Done at ..., ...
For the Trade Committee
Minister for Trade of the Republic of Korea
Kim JONG-HOON
Commissioner for Trade of the European Commission
Karel DE GUCHT
ANNEX
RULES OF PROCEDURE OF THE TRADE COMMITTEE
Article 1
Composition and Chair
1. The Trade Committee that is established in accordance with Article 15.1 of the Free Trade Agreement between the European Union and its Member States, of the one part, and the Republic of Korea, of the other part, (the Agreement) shall perform its duties as provided in Article 15.1 of the Agreement and take responsibility for general implementation of the Agreement.
2. As provided for in Article 15.1.1 of the Agreement, the Trade Committee shall be composed of the representatives of the EU Party, on the one hand, and representatives of Korea, on the other hand.
3. The Trade Committee shall be co-chaired by the Minister for Trade of Korea and the Member of the European Commission responsible for Trade. The Chairpersons may arrange to be represented by respective designees as provided in Article 15.1.2 of the Agreement.
Article 2
Representation
1. A Party shall notify the other Party of the list of its members of the Trade Committee. The list shall be administered by the Secretariat of the Trade Committee.
2. A member wishing to be represented by an alternate representative shall notify the Chairpersons of the Trade Committee of the name of his or her alternate representative before the meeting at which he or she is to be so represented. The alternate representative of a member of the Trade Committee shall exercise all the rights of that member.
Article 3
Meetings
1. The Trade Committee shall meet once a year or at the request of either Party. The meetings shall be held in Brussels or Seoul alternately, unless the Parties agree otherwise.
2. By way of exception and if both Parties agree, the meetings of the Trade Committee may be held by video or teleconference.
3. Each meeting of the Trade Committee shall be convened by the Secretariat of the Trade Committee at a date and place agreed by both Parties. The convening notice of the meeting shall be issued by the Secretariat of the Trade Committee to the members of the Trade Committee no later than 28 days prior to the start of the session, unless the Parties agree otherwise.
Article 4
Delegation
The members of the Trade Committee may be accompanied by officials. Before each meeting, the Chairpersons of the Trade Committee shall be informed of the intended composition of the delegations attending the meeting.
Article 5
Observers
The Trade Committee may decide to invite observers on an ad hoc basis.
Article 6
Secretariat
The coordinators designated by the Parties in accordance with Article 15.6 of the Agreement shall jointly act as Secretariat of the Trade Committee.
Article 7
Documents
Where the deliberations of the Trade Committee are based on written supporting documents, such documents shall be numbered and circulated by the Secretariat of the Trade Committee as documents of the Trade Committee.
Article 8
Correspondence
1. Correspondence to the Chairpersons of the Trade Committee shall be forwarded to the Secretariat of the Trade Committee for circulation to the members of the Trade Committee.
2. Correspondence from the Chairpersons of the Trade Committee shall be sent to the recipients by the Secretariat of the Trade Committee and be numbered and circulated, where appropriate, to the other members of the Trade Committee.
Article 9
Agenda for the Meetings
1. A provisional agenda for each meeting shall be drawn up by the Secretariat of the Trade Committee. It shall be forwarded, together with the relevant documents, to the members of the Trade Committee as well as the Chairpersons of the Trade Committee no later than 7 days before the beginning of the meeting.
2. The provisional agenda shall include items in respect of which the Secretariat of the Trade Committee has received a request for inclusion in the agenda by a Party, together with the relevant documents, no later than 14 days before the beginning of the meeting.
3. The agenda shall be adopted by the Trade Committee at the beginning of each meeting. Items other than those appearing on the provisional agenda may be placed on the agenda if the Parties so agree.
4. The Chairpersons of the Trade Committee may, upon agreement, invite experts to attend its meetings in order to provide information on specific subjects.
5. The Chairpersons of the Trade Committee may, upon agreement, reduce the time periods specified in paragraphs 1 and 2 in order to take account of the requirements of a particular case.
Article 10
Minutes
```

### Retrieved: L_2022271EN.01001701 / chunk_2

Resolution: document_chunk_sqlite

```text
1. Pursuant to Article 16.1 of the Agreement, the Trade Committee shall comprise representatives of the European Union and of the Republic of Singapore and shall be co-chaired by the Member of the European Commission responsible for Trade and the Minister for Trade and Industry of Singapore, or their respective delegates.
2. Each Party shall notify the other Party of the name, position and contact details of the delegated official who is in charge of co-chairing the Trade Committee for that Party. That delegated official is deemed to have the authorisation to represent the Party until the date the Party has notified the other Party that it has appointed a new Co-chair.
Rule 3
Secretariat
1. Officials from the department responsible for Trade for each Party shall act as the Secretariat of the Trade Committee.
2. Each Party shall notify the other Party of the name, position and contact details of the official who is to be the member of the Secretariat of the Trade Committee for that Party. That official is deemed to continue acting as member of the Secretariat for the Party until the date the Party has notified the other Party that it has appointed a new member.
Rule 4
Meetings
1. In accordance with Article 16.1 of the Agreement, the Trade Committee shall meet every two years or without undue delay at the request of either Party.
2. The meetings shall be held at an agreed date and time alternately in Brussels and in Singapore, unless agreed otherwise by the Co-chairs.
3. The meetings shall be convened by the Co-chair of the Party hosting the meeting.
4. A meeting may be held in person, by videoconference, or by any other means.
Rule 5
Delegations
Before each meeting, each member of the Secretariat of the Trade Committee for each Party shall inform the other member of the intended composition of the delegations of their respective party. The lists shall specify the name and function of each member of the delegation.
Rule 6
Agenda for the meetings
1. At least 15 days in advance of a meeting, a provisional agenda for each meeting shall be drawn up by the Secretariat of the Trade Committee on the basis of a proposal made by the Party hosting the meeting. The other Party shall have the opportunity to provide comments.
2. The agenda shall be adopted by the Trade Committee at the beginning of each meeting. Items not appearing on the provisional agenda may be placed on the agenda by mutual agreement.
Rule 7
Invitation of experts
The Co-chairs of the Trade Committee may, by mutual agreement, invite independent experts to attend the meetings of the Trade Committee in order to provide information on specific subjects and only for the parts of the meeting where such specific subjects are discussed.
Rule 8
Minutes
1. Draft minutes of each meeting shall be drawn up by the member of the Secretariat of the Party hosting the meeting within 21 days from the end of the meeting, unless otherwise decided by the Co-chairs. The draft minutes shall be transmitted for comments to the member of the Secretariat of the other Party.
2. Where these rules of procedure apply to the meetings of specialised committees, the minutes of the specialised committee meetings shall be made available for any subsequent meetings of the Trade Committee.
3. The minutes shall, as a general rule, summarise each item on the agenda, specifying where applicable:
(a) all documents submitted to the Trade Committee; (b) any statement that one of the Co-chairs of the Trade Committee requested to be entered in the minutes; and (c) the decisions taken, recommendations made, statements agreed upon and conclusions adopted on specific items.
1. The minutes shall include a list of all decisions of the Trade Committee, taken by written procedure pursuant to Rule 9.2, since the last meeting of the Committee.
2. An annex to the minutes shall also include a list of the names, titles and capacity of all individuals who attended the meeting of the Trade Committee.
3. The Secretariat shall adjust the draft minutes on the basis of comments received and the draft minutes, as revised, shall be approved by the Parties within 30 days of the date of the meeting, or by any other date agreed by the Co-chairs. Once approved, two original versions of the minutes shall be prepared by the Secretariat and the Parties shall each receive one original version of the minutes.
Rule 9
Decisions and recommendations
```

### Retrieved: L_2011127EN.01000101 / chunk_60

Resolution: document_chunk_sqlite

```text
1. The Trade Committee may decide to establish other specialised committees in order to assist it in the performance of its tasks. The Trade Committee shall determine the composition, duties and functioning of the specialised committees established pursuant to this Article.
2. Unless otherwise provided for in this Agreement, the specialised committees shall normally meet, once a year, at an appropriate level, alternately in Brussels or Seoul, or at the request of either Party or of the Trade Committee and shall be co-chaired by representatives of Korea and the European Union. The specialised committees shall agree on their meeting schedule and set their agenda.
3. The specialised committees shall inform the Trade Committee of their schedule and agenda sufficiently in advance of their meetings. They shall report to the Trade Committee on their activities at each regular meeting of the Trade Committee. The creation or existence of a specialised committee shall not prevent either Party from bringing any matter directly to the Trade Committee.
4. The Trade Committee may decide to change or undertake the task assigned to a specialised committee or dissolve any specialised committee.
Article 15.3
Working Groups
1. The following Working Groups are hereby established under the auspices of the Trade Committee:
(a) the Working Group on Motor Vehicles and Parts in accordance with Article 9.2 (Working Group on Motor Vehicles and Parts) of Annex 2-C (Motor Vehicles and Parts); (b) the Working Group on Pharmaceutical Products and Medical Devices in accordance with Article 5.3 (Regulatory Cooperation) of Annex 2-D (Pharmaceutical Products and Medical Devices); (c) the Working Group on Chemicals in accordance with paragraph 4 of Annex 2-E (Chemicals); (d) the Working Group on Trade Remedy Cooperation in accordance with Article 3.16.1 (Working Group on Trade Remedy Cooperation); (e) the Working Group on MRA in accordance with Article 7.21.6 (Mutual Recognition); (f) the Working Group on Government Procurement in accordance with Article 9.3 (Government Procurement Working Group); and (g) the Working Group on Geographical Indications in accordance with Article 10.25 (Working Group on Geographical Indications).
1. The Trade Committee may decide to establish other working groups for a specific task or subject matter. The Trade Committee shall determine the composition, duties and functioning of working groups. Any regular or ad-hoc meetings between the Parties whose work addresses matters covered by this Agreement shall be considered working groups within the meaning of this Article.
2. Unless otherwise provided for in this Agreement, working groups shall meet, at an appropriate level, when circumstances require, or at the request of either Party or of the Trade Committee. They shall be co-chaired by representatives of Korea and the European Union. Working groups shall agree on their meeting schedule and set their agenda.
3. Working groups shall inform the Trade Committee of their schedule and agenda sufficiently in advance of their meetings. They shall report to the Trade Committee on their activities at each regular meeting of the Trade Committee. The creation or existence of a working group shall not prevent either Party from bringing any matter directly to the Trade Committee.
4. The Trade Committee may decide to change or undertake the task assigned to a working group or dissolve any working group.
Article 15.4
Decision-making
1. The Trade Committee shall, for the purpose of attaining the objectives of this Agreement, have the power to take decisions in respect of all matters in the cases provided by this Agreement.
2. The decisions taken shall be binding on the Parties, which shall take the measures necessary to implement the decisions taken. The Trade Committee may also make appropriate recommendations.
3. The Trade Committee shall draw up its decisions and recommendations by agreement between the Parties.
Article 15.5
Amendments
1. The Parties may agree, in writing, to amend this Agreement. An amendment shall enter into force after the Parties exchange written notifications certifying that they have completed their respective applicable legal requirements and procedures, on such date as the Parties may agree.
2. Notwithstanding paragraph 1, the Trade Committee may decide to amend the Annexes, Appendices, Protocols and Notes to this Agreement. The Parties may adopt the decision subject to their respective applicable legal requirements and procedures.
Article 15.6
Contact points
```

### Retrieved: L_2009319EN.01000101 / chunk_13

Resolution: document_chunk_sqlite

```text
1. The Parties hereby establish a Special Committee on Customs and Trade Facilitation, composed of representatives of the Parties.
2. The functions of the Special Committee on Customs and Trade Facilitation shall, inter alia , be the following:
(a) monitoring the implementation and administration of this Chapter and of the Protocol on Rules of Origin; (b) providing a forum to consult and discuss all issues concerning customs, including rules of origin, general customs procedures, customs valuation, tariff classification, transit and mutual administrative assistance in customs matters; (c) enhancing cooperation on the development, application and enforcement of rules of origin and related customs procedures, general customs procedures and mutual administrative assistance in customs matters; (d) enhancing cooperation on capacity building and technical assistance; (e) follow-up on the implementation of Article 44 of this Agreement; and (f) any other issues agreed by the Parties in respect of this Chapter.
1. The Special Committee on Customs and Trade Facilitation shall meet on a date and with an agenda agreed in advance by the Parties.
2. The Special Committee on Customs and Trade Facilitation shall be chaired alternatively by either Party.
3. The Special Committee on Customs and Trade Facilitation shall report to the Trade and Development Committee.
CHAPTER 8
Technical barriers to trade
Article 48
Multilateral obligations
1. The Parties confirm their commitment to the rights and obligations provided for in the WTO Agreement on Technical Barriers to Trade (hereinafter referred to as 'the TBT Agreement').
2. These rights and obligations shall underlie the activities of the Parties under this Chapter.
Article 49
Objectives
1. The Parties agree to cooperate in order to facilitate and increase trade in goods between them, by identifying, preventing and eliminating unnecessary barriers to trade within the terms of the TBT Agreement.
2. The Parties undertake to cooperate in strengthening regional, and specifically SADC EPA States' integration and cooperation on matters concerning technical barriers to trade.
3. The Parties undertake to establish and enhance SADC EPA States' technical capacity on matters concerning technical barriers to trade.
Article 50
Scope and definitions
1. The provisions of this Chapter shall apply to technical regulations, standards and conformity assessment procedures as defined in the TBT Agreement in so far as they affect trade covered by this Agreement.
2. For the purposes of this Chapter, the definitions used by the TBT Agreement shall apply.
Article 51
Collaboration and regional integration
The Parties agree that collaboration between national and regional authorities dealing with TBT matters, in both the public and private sector, is important to facilitate trade in the region and between the Parties, as well as for the overall process of regional integration and undertake to cooperate to this end.
Article 52
Transparency
The Parties reaffirm the principle of transparency in the application of technical regulations and standards in accordance with the TBT Agreement.
The Parties recognise the importance of effective mechanisms for consultation, notification and exchange of information with respect to technical regulations and standards in accordance with the TBT Agreement.
Article 53
Measures for identifying, preventing and eliminating technical barriers to trade
The Parties agree to identify and implement mechanisms among those supported by the TBT Agreement that are the most appropriate for particular priority issues or sectors. Such mechanisms may include:
```

### Retrieved: L_202302505EN / chunk_3

Resolution: document_chunk_sqlite

```text
1. After the customs authority of the importing Party has notified the customs authority of the exporting Party of its intention to deny the preferential tariff treatment, a Party may submit a request for consultations to the other Party pursuant to Article 63(3), second subparagraph, of the Trade and Cooperation Agreement between the European Union and the European Atomic Energy Community, of the one part, and the United Kingdom of Great Britain and Northern Ireland, of the other part (the 'Agreement').
2. The request shall be made by the member of the Secretariat of the Trade Specialised Committee on Customs Cooperation and Rules of Origin (the 'Committee') of the requesting Party to the member of the Secretariat of the other Party by e-mail or, where appropriate, by any other means of communication that provides a record of the sending thereof. Unless proven otherwise, such request shall be deemed to be received on the date of its sending.
Rule 2
1. Consultations shall be convened and concluded within three months after the date of the notification of the intention referred to in Rule 1, unless the Parties have agreed to extend the period for consultations. During that period, the Parties may meet one or several times.
2. Consultations shall be held in person or by any other means of communication agreed by the Parties. If held in person, consultations shall take place in the territory of the Party to which the consultations requested are addressed, unless the Parties agree otherwise.
Rule 3
15 calendar days in advance of each session of consultation, each Party shall inform the other Party, through the Secretariat, of the intended composition of its delegation and shall specify the name and function of each member thereof.
Rule 4
1. The consultations shall be held in English.
2. Written documents relevant for the consultations shall be circulated, through the Secretariat, to the other Party. They may be in any of the official languages of the Union.
Rule 5
1. Draft minutes of each consultation session shall be drawn up by the official acting as member of the Secretariat of the respondent Party hosting the meeting within 8 calendar days. The draft minutes shall be transmitted for comments to the member of the Secretariat of the other Party, who may submit comments within 8 calendar days.
2. The minutes shall summarise the consultation sessions, specifying where applicable:
(a) the documents submitted; (b) any statement that a Party requested be entered in the minutes; and (c) the conclusions reached, which may include the extension of the duration of the consultations.
1. The minutes shall include as an annex a list of participants setting out for each of the delegations the names and functions of all individuals who attended the meeting.
2. The Secretariat shall adjust the draft minutes on the basis of the comments received. The draft minutes, as revised, shall be approved by the Parties within 28 calendar days of the date of the session, or by any other date agreed by the Parties. Upon approval of the minutes, any agreement reached shall take effect between the Parties at the session of consultations when that conclusion was adopted.
3. If the consultations are held in writing, the result of the written consultations shall be recorded in the minutes of the next meeting of the Committee. Any agreement reached during the written consultations shall take effect between the Parties at the session of consultations when that conclusion was adopted.
Rule 6
1. The Parties shall make every attempt to arrive at a mutually satisfactory resolution of the matter within the period of consultation referred to in Rule 2. If the Parties reach an agreement, it shall be binding upon the Parties.
2. For the purpose of Article 63(3), third subparagraph, of the Agreement, the period of consultation referred to in Rule 2 shall be considered expired when it arrives at its term and the Parties do not agree to extend it, unless the consultation was not held for reasons attributable to the importing Party.
ELI: http://data.europa.eu/eli/dec/2023/2505/oj
ISSN 1977-0677 (electronic edition)
```

### Retrieved: L_2011127EN.01000101 / chunk_19

Resolution: document_chunk_sqlite

```text
1. The Customs Committee established pursuant to Article 15.2.1 (Specialised Committees) shall ensure the proper functioning of this Chapter and the Protocol concerning the Definition of 'Originating Products' and Methods of Administrative Cooperation and the Protocol on Mutual Administrative Assistance in Customs Matters and examine all issues arising from their application. For matters covered by this Agreement, it shall report to the Trade Committee set up under Article 15.1.1 (Trade Committee).
2. The Customs Committee shall consist of representatives of the customs and other competent authorities of the Parties responsible for customs and trade facilitation matters, for the management of the Protocol concerning the Definition of 'Originating Products' and Methods of Administrative Cooperation and the Protocol on Mutual Administrative Assistance in Customs Matters.
3. The Customs Committee shall adopt its rules of procedure and meet annually, the location of the meeting alternating between the Parties.
4. On the request of a Party, the Customs Committee shall meet to discuss and endeavour to resolve any difference that may arise between the Parties on matters as included in this Chapter and the Protocol concerning the Definition of 'Originating Products' and Methods of Administrative Cooperation and the Protocol on Mutual Administrative Assistance in Customs Matters, including trade facilitation, tariff classification, origin of goods and mutual administrative assistance in customs matters, in particular relating to Articles 7 and 8 of the Protocol on Mutual Administrative Assistance in Customs Matters.
5. The Customs Committee may formulate resolutions, recommendations or opinions which it considers necessary for the attainment of the common objectives and sound functioning of the mechanisms established in this Chapter and the Protocol concerning the Definition of 'Originating Products' and Methods of Administrative Cooperation and the Protocol on Mutual Administrative Assistance in Customs Matters.
CHAPTER SEVEN
TRADE IN SERVICES, ESTABLISHMENT AND ELECTRONIC COMMERCE
SECTION A
General provisions
Article 7.1
Objective, scope and coverage
1. The Parties, reaffirming their respective rights and obligations under the WTO Agreement, hereby lay down the necessary arrangements for progressive reciprocal liberalisation of trade in services and establishment and for cooperation on electronic commerce.
2. Nothing in this Chapter shall be construed to impose any obligation with respect to government procurement.
3. This Chapter shall not apply to subsidies or grants provided by a Party, including government-supported loans, guarantees and insurance.
4. Consistent with this Chapter, each Party retains the right to regulate and to introduce new regulations to meet legitimate policy objectives.
5. This Chapter shall not apply to measures affecting natural persons seeking access to the employment market of a Party, nor shall it apply to measures regarding citizenship, residence or employment on a permanent basis.
6 Nothing in this Chapter shall prevent a Party from applying measures to regulate the entry of natural persons into, or their temporary stay in, its territory, including those measures necessary to protect the integrity of, and to ensure the orderly movement of natural persons across, its borders, provided that such measures are not applied in such a manner as to nullify or impair the benefits accruing to the other Party under the terms of a specific commitment in this Chapter and its Annexes
[( 4 )](#ntr4-L_2011127EN.01000601-E0004)
.
Article 7.2
Definitions
For the purposes of this Chapter:
```

### Retrieved table: L_2023231EN.01011801 / table_1

```json
{
  "document_id": "L_2023231EN.01011801",
  "table_id": "table_1",
  "row_ids": [
    0
  ],
  "headers": null,
  "rows": [
    [
      "",
      "UNITED STATES DEPARTMENT OF COMMERCE Secretary of Commerce Washington, D.C. 20230"
    ]
  ]
}
```

### Retrieved table: L_2019010EN.01007101 / table_1

```json
{
  "document_id": "L_2019010EN.01007101",
  "table_id": "table_1",
  "row_ids": [
    0
  ],
  "headers": [
    "Binding tariff information — reference no | 1",
    "Customs authority | 2",
    "Tariff classification | 3"
  ],
  "rows": [
    [
      "PL PL-WIT-2016-00758",
      "",
      "2833 11 00"
    ]
  ]
}
```

### Retrieved table: L_2021269EN.01005801 / table_1

```json
{
  "document_id": "L_2021269EN.01005801",
  "table_id": "table_1",
  "row_ids": [
    1
  ],
  "headers": [
    "A",
    "B | Microdata to be exchanged ( 1 )",
    "C1 | Centralised clearance imports",
    "C2 | Centralised clearance exports",
    "C3 | Goods in quasi- export"
  ],
  "rows": [
    [
      "1.1.",
      "Date of acceptance of the customs declaration",
      "C",
      "C",
      "C"
    ]
  ]
}
```

### Retrieved table: L_2021269EN.01005801 / table_1

```json
{
  "document_id": "L_2021269EN.01005801",
  "table_id": "table_1",
  "row_ids": [
    32
  ],
  "headers": [
    "A",
    "B | Microdata to be exchanged ( 1 )",
    "C1 | Centralised clearance imports",
    "C2 | Centralised clearance exports",
    "C3 | Goods in quasi- export"
  ],
  "rows": [
    [
      "4.2.",
      "Buyer identification number",
      "C",
      "-",
      "-"
    ]
  ]
}
```

### Retrieved table: L_2021269EN.01005801 / table_1

```json
{
  "document_id": "L_2021269EN.01005801",
  "table_id": "table_1",
  "row_ids": [
    5
  ],
  "headers": [
    "A",
    "B | Microdata to be exchanged ( 1 )",
    "C1 | Centralised clearance imports",
    "C2 | Centralised clearance exports",
    "C3 | Goods in quasi- export"
  ],
  "rows": [
    [
      "1.5.",
      "Receiving Member State",
      "M",
      "M",
      "M"
    ]
  ]
}
```

## global_natural_010

When may customs authorities carry out a subsequent verification of a proof of origin?

Draft reference: At random or on reasonable doubts concerning authenticity, originating status or other Protocol requirements; do not silently make every agreement identical.

Retrieval execution status: success (NOT relevance)

### Expected: L_2007345EN.01000101 / chunk_39

Resolution: document_chunk_sqlite

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

### Retrieved: L_202402144EN / chunk_15

Resolution: document_chunk_sqlite

```text
1. The Central African States and the Member States of the European Union shall immediately inform each other of any change in the information referred to in paragraph 1.
2. The authorities referred to in paragraph 1 shall act under the authority of the government of the country concerned. The authorities in charge of control and verification shall be part of the governmental authorities of the country concerned.
Article 34
Other methods of administrative cooperation
1. In order to ensure the proper application of this Protocol, the European Union, the Central Africa Party and the other countries referred to in Articles 6, 7, 8 and 9 shall ensure, through their competent customs authorities, that the authenticity of the movement certificates EUR.1, the origin declarations or the supplier's declarations and the accuracy of the information given in these documents are checked. The Central African States and the Member States of the European Union shall also:
(a) provide each other with the necessary administrative cooperation in the event of a request for the monitoring of the proper management and control of the Protocol in the country concerned, including on-site visits; (b) check, in accordance with Article 35, the originating status of the products and compliance with the other requirements of this Protocol.
1. The authorities consulted shall furnish the relevant information concerning the conditions under which the product has been made, indicating in particular the conditions under which the rules of origin have been complied with in the Central Africa Party, in the European Union and the other countries referred to in Articles 6, 7, 8 and 9.
Article 35
Verification of proof of origin
1. Subsequent verifications of proof of origin shall be carried out on the basis of a risk analysis, by random sampling or whenever the customs authorities of the importing country have reasonable doubts as to the authenticity of such documents, the originating status of the products concerned or compliance with the other requirements of this Protocol.
2. For the purposes of implementing paragraph 1, the customs authorities of the importing country shall return the movement certificate EUR.1 and the invoice, if it has been submitted, the origin declaration, or a copy of these documents, to the customs authorities of the exporting country giving, where appropriate, the reasons for the request for verification. Any documents and information obtained suggesting that the information given on the proof of origin is incorrect shall be forwarded in support of the request for verification.
3. The verification of proof of origin shall be carried out by the customs authorities of the exporting country. For this purpose, they shall have the right to call for any evidence and to carry out any inspection of the exporter's accounts or any other check considered appropriate.
4. If the customs authorities of the importing country decide to suspend the granting of preferential treatment to the products concerned while awaiting the results of the verification of proof of origin, release of the products shall be offered to the importer subject to any precautionary measures deemed necessary.
5. The customs authorities requesting the verification of proof of origin shall be informed of the results thereof as soon as possible. Those results must indicate clearly whether the documents are authentic and whether the products concerned can be considered as products originating in the Central Africa Party, in the European Union or in one of the other countries referred to in Articles 6, 7, 8 and 9 and fulfil the other requirements of this Protocol.
6. If in cases of reasonable doubt there is no reply within 10 months of the date of the verification of proof of origin request or if the reply does not contain sufficient information to determine the authenticity of the document in question or the real origin of the products, the customs authorities that request the verification of proof of origin shall, except in exceptional circumstances, refuse entitlement to the preferences.
7. The parties shall refer to Article 7 of the Protocol on mutual administrative assistance in customs matters for joint investigations concerning proof of origin.
Article 36
Verification of suppliers' declarations
1. Verification of suppliers' declarations shall be carried out on the basis of risk analysis, by random sampling or whenever the customs authorities of the country where such declarations have been taken into account to issue a movement certificate EUR.1 or to make out an origin declaration have reasonable doubts as to the authenticity of the document or the accuracy of the information given in this document.
2. The customs authorities to which a supplier's declaration is submitted may request the customs authorities of the State where the declaration was made out to issue an information certificate, a specimen of which appears in Annex VI. Alternatively, the certifying authorities to which a supplier's declaration is submitted may request that the exporter produce an information certificate issued by the customs authorities of the State where the declaration was made out.
A copy of the information certificate shall be preserved by the office which has issued it for at least three (3) years.
```

### Retrieved: L_2011127EN.01000101 / chunk_137

Resolution: document_chunk_sqlite

```text
(a) direct evidence of the processes carried out by the exporter, supplier or producer to obtain the goods concerned, contained for example in his accounts or internal bookkeeping; (b) documents proving the originating status of materials used, issued or made out in a Party where these documents are used as provided for in its domestic law; (c) documents proving the working or processing of materials in a Party, issued or made out in a Party where these documents are used as provided for in its domestic law; (d) proofs of origin proving the originating status of materials used issued or made out in a Party in accordance with this Protocol; and (e) appropriate evidence concerning working or processing undergone outside territories of the Parties by application of Article 12, proving that the requirements of that Article have been satisfied.
Article 23
Preservation of proof of origin and supporting documents
1. The exporter making out an origin declaration shall keep for five years a copy of this origin declaration as well as the documents referred to in Article 16.3.
2. The importer shall keep all records related to the importation in accordance with laws and regulations of the importing Party.
3. The customs authorities of the importing Party shall keep for five years the origin declarations submitted to them.
4. The records to be kept in accordance with paragraphs 1 through 3 may include electronic records.
Article 24
Discrepancies and formal errors
1. The discovery of slight discrepancies between the statements made in the proof of origin and those made in the documents submitted to the customs authorities for the purpose of carrying out the formalities for importing the products shall not ipso facto render the proof of origin null and void if it is duly established that such document does correspond to the products submitted.
2. Obvious formal errors such as typing errors on a proof of origin should not cause this document to be rejected if these errors are not such as to create doubts concerning the correctness of the statements made in this document.
Article 25
Amounts expressed in euro
1. For the application of the provisions of Article 16.1(b) in cases where products are invoiced in a currency other than euro, amounts in the national currencies of the Member States of the European Union equivalent to the amounts expressed in euro shall be fixed annually by the EU Party and submitted to Korea.
2. A consignment shall benefit from the provisions of Article 16.1(b) by reference to the currency in which the invoice is drawn up, according to the amount fixed by the EU Party.
3. The amounts to be used in any given national currency of the Member States of the European Union shall be the equivalent in that currency of the amounts expressed in euro as at the first working day of October. The European Commission shall notify Korea of these amounts by 15 October and these amounts shall apply from 1 January the following year.
4. The Member States of the European Union may round up or down the amount resulting from the conversion into their national currency of an amount expressed in euro. The rounded-off amount may not differ from the amount resulting from the conversion by more than five percent. The Member States of the European Union may retain unchanged their national currency equivalent of an amount expressed in euro if, at the time of the annual adjustment provided for in paragraph 3, the conversion of that amount, prior to any rounding-off, results in an increase of less than 15 percent in the national currency equivalent. The national currency equivalent may be retained unchanged if the conversion would result in a decrease in that equivalent value.
5. The amounts expressed in euro shall be reviewed by the Customs Committee at the request of a Party. When carrying out this review, the Customs Committee shall consider the desirability of preserving the effects of the limits concerned in real terms. For this purpose, it may decide to modify the amounts expressed in euro.
TITLE VI
Arrangements for administrative cooperation
Article 26
Exchange of addresses
The customs authorities of the Parties shall provide each other, through the European Commission, with the addresses of the customs authorities responsible for verifying proofs of origin.
Article 27
Verification of proofs of origin
```

### Retrieved: L_2015343EN.01055801 / chunk_36

Resolution: document_chunk_sqlite

```text
1. For the purpose of establishing the origin of materials used under bilateral or regional cumulation, the exporter of a product manufactured using materials originating in a country with which cumulation is permitted shall rely on the statement on origin provided by the supplier of those materials. In these cases, the statement on origin made out by the exporter shall, as the case may be, contain the indication 'EU cumulation', 'regional cumulation', 'Cumul UE', 'Cumul regional' or 'Acumulación UE', 'Acumulación regional'.
2. For the purpose of establishing the origin of materials used within the framework of cumulation under Article 54 of Delegated Regulation (EU) 2015/2446, the exporter of a product manufactured using materials originating in Norway, Switzerland or Turkey shall rely on the proof of origin provided by the supplier of those materials on condition that that proof has been issued in accordance with the provisions of the GSP rules of origin of Norway, Switzerland or Turkey, as the case may be. In this case, the statement on origin made out by the exporter shall contain the indication 'Norway cumulation', 'Switzerland cumulation', 'Turkey cumulation', 'Cumul Norvège', 'Cumul Suisse', 'Cumul Turquie' or 'Acumulación Noruega', 'Acumulación Suiza', 'Acumulación Turquía'.
3. For the purpose of establishing the origin of materials used within the framework of extended cumulation under Article 56 of Delegated Regulation (EU) 2015/2446, the exporter of a product manufactured using materials originating in a party with which extended cumulation is permitted shall rely on the proof of origin provided by the supplier of those materials on condition that that proof has been issued in accordance with the provisions of the relevant free-trade agreement between the Union and the party concerned.
In this case, the statement on origin made out by the exporter shall contain the indication 'extended cumulation with country x', 'cumul étendu avec le pays x' or 'Acumulación ampliada con el país x'.
Subsection 6
Procedures at release for free circulation in the Union applicable within the framework of the GSP scheme of the Union until the date of the application of the registered exporter system
Article 94
Submission and validity of certificates of origin Form A or invoice declarations and belated presentation thereof
(Article 64(1) of the Code)
1. Certificates of origin Form A or invoice declarations shall be submitted to the customs authorities of the Member States of importation in accordance with the procedures concerning the customs declaration.
2. A proof of origin shall be valid for 10 months from the date of issue in the exporting country and shall be submitted within the said period to the customs authorities of the importing country.
Proofs of origin submitted to the customs authorities of the importing country after the lapsing of their period of validity may be accepted for the purpose of applying the tariff preferences, where failure to submit these documents by the final date set is due to exceptional circumstances.
In other cases of belated presentation, the customs authorities of the importing country may accept the proofs of origin where the products have been presented to customs before the said final date.
Article 95
Replacement of certificates of origin Form A and invoice declarations
(Article 64(1) of the Code)
1. Where originating products not yet released for free circulation are placed under the control of a customs office of a Member State, that customs office shall, on written request from the re-consignor, replace the initial certificate of origin Form A or invoice declaration by one or more certificates of origin Form A (replacement certificate) for the purposes of sending all or some of these products elsewhere within the Union or to Norway or Switzerland. The re-consignor shall indicate in his request whether a photocopy of the initial proof of origin is to be annexed to the replacement certificate.
2. The replacement certificate shall be drawn up in accordance with Annex 22-19.
The customs office shall verify that the replacement certificate is in conformity with the initial proof of origin.
1. Where the request for a replacement certificate is made by a re-consignor acting in good faith, he shall not be responsible for the accuracy of the particulars entered on the initial proof of origin.
2. The customs office which is requested to issue the replacement certificate shall note on the initial proof of origin or on an attachment thereto the weights, numbers, nature of the products forwarded and their country of destination and indicate thereon the serial numbers of the corresponding replacement certificate or certificates. It shall keep the initial proof of origin for at least 3 years.
3. In the case of products which benefit from the tariff preferences under a derogation granted in accordance with Article 64(6) of the Code, the procedure laid down in this Article shall apply only when such products are intended for the Union.
```

### Retrieved: L_2015343EN.01055801 / chunk_37

Resolution: document_chunk_sqlite

```text
Article 96
Importation by instalments using certificates of origin Form A or invoice declarations
(Article 64(1) of the Code)
1. Where, at the request of the importer and on the conditions laid down by the customs authorities of the importing Member State, unassembled or disassembled products within the meaning of general interpretative rule 2(a) of the Harmonised System and falling within Section XVI or XVII or heading 7308 or 9406 of the Harmonised System are imported by instalments, a single proof of origin for such products may be submitted to the customs authorities on importation of the first instalment.
2. At the request of the importer and having regard to the conditions laid down by the customs authorities of the importing Member State, a single proof of origin may be submitted to the customs authorities at the importation of the first consignment when the goods:
(a) are imported within the framework of frequent and continuous trade flows of a significant commercial value; (b) are the subject of the same contract of sale, the parties of this contract established in the exporting country or in the Member State(s); (c) are classified in the same code (eight digits) of the Combined Nomenclature; (d) come exclusively from the same exporter, are destined for the same importer, and are made the subject of entry formalities at the same customs office of the same Member State.
This procedure shall be applicable for a period determined by the competent customs authorities.
Article 97
Exemptions from the obligation to provide a certificate of origin Form A or an invoice declaration
(Article 64(1) of the Code)
1. Products sent as small packages from private persons to private persons or forming part of travellers' personal luggage shall be admitted as originating products benefiting from GSP tariff preferences without requiring the presentation of a certificate of origin Form A or an invoice declaration, provided that:
(a) such products: (i) are not imported by way of trade; (ii) have been declared as meeting the conditions required for benefiting from the GSP scheme; (b) there is no doubt as to the veracity of the declaration referred to in point (a)(ii).
1. Imports shall not be considered as imports by way of trade if all the following conditions are met:
(a) the imports are occasional; (b) the imports consist solely of products for the personal use of the recipients or travellers or their families; (c) it is evident from the nature and quantity of the products that no commercial purpose is in view.
1. The total value of the products referred to in paragraph 2 shall not exceed EUR 500 in the case of small packages or EUR 1 200 in the case of products forming part of travellers' personal luggage.
Article 98
Discrepancies and formal errors in certificates of origin Form A or invoice declarations
(Article 64(1) of the Code)
1. The discovery of slight discrepancies between the statements made in the certificate of origin Form A or in an invoice declaration, and those made in the documents submitted to the customs office for the purpose of carrying out the formalities for importing the products shall not ipso facto render the certificate or declaration null and void if it is duly established that that document does correspond to the products submitted.
2. Obvious formal errors on a certificate of origin Form A, a movement certificate EUR.1 or an invoice declaration shall not cause this document to be rejected if these errors are not such as to create doubts concerning the correctness of the statements made in that document.
Subsection 7
Procedures at release for free circulation in the Union applicable within the framework of the GSP scheme of the Union from the date of the application of the registered exporter system
Article 99
Validity of statement on origin
(Article 64(1) of the Code)
1. A statement on origin shall be made out for each consignment.
2. A statement on origin shall be valid for 12 months from the date on which it is made out.
3. A single statement on origin may cover several consignments if the goods meet the following conditions:
(a) they are presented unassembled or disassembled within the meaning of General Interpretative rule 2(a) of the Harmonised System; (b) they are falling within Sections XVI or XVII or headings 7308 or 9406 of the Harmonised System; and (c) they are intended to be imported by instalments.
Article 100
Admissibility of a statement on origin
(Article 64(1) of the Code)
```

### Retrieved: L_2013269EN.01000101 / chunk_54

Resolution: document_chunk_sqlite

```text
1. Where only part of the goods covered by a customs declaration is examined, or samples are taken, the results of the partial examination, or of the analysis or examination of the samples, shall be taken to apply to all the goods covered by the same declaration.
However, the declarant may request a further examination or sampling of the goods if he or she considers that the results of the partial examination, or of the analysis or examination of the samples taken, are not valid as regards the remainder of the goods declared. The request shall be granted provided that the goods have not been released or, if they have been released, that the declarant proves that they have not been altered in any way.
1. For the purposes of paragraph 1, where a customs declaration covers goods falling under two or more items, the particulars relating to goods falling under each item shall be deemed to constitute a separate declaration.
Article 191
Results of the verification
1. The results of verifying the customs declaration shall be used for the application of the provisions governing the customs procedure under which the goods are placed.
2. Where the customs declaration is not verified, paragraph 1 shall apply on the basis of the particulars contained in that declaration.
3. The results of the verification made by the customs authorities shall have the same conclusive force throughout the customs territory of the Union.
Article 192
Identification measures
1. The customs authorities or, where appropriate, economic operators authorised to do so by the customs authorities, shall take the measures necessary to identify the goods where identification is required in order to ensure compliance with the provisions governing the customs procedure for which those goods have been declared.
Those identification measures shall have the same legal effect throughout the customs territory of the Union.
1. Means of identification affixed to the goods, packaging or means of transport shall be removed or destroyed only by the customs authorities or, where they are authorised to do so by the customs authorities, by economic operators, unless, as a result of unforeseeable circumstances or force majeure, their removal or destruction is essential to ensure the protection of the goods or the means of transport.
Article 193
Conferral of implementing powers
The Commission shall specify, by means of implementing acts, measures on the verification of the customs declaration, the examination and sampling of goods and the results of the verification.
Those implementing acts shall be adopted in accordance with the examination procedure referred to in Article 285(4).
Section 2
Release
Article 194
Release of the goods
1. Where the conditions for placing the goods under the procedure concerned are fulfilled and provided that any restriction has been applied and the goods are not subject to any prohibition, the customs authorities shall release the goods as soon as the particulars in the customs declaration have been verified or are accepted without verification.
The first subparagraph shall also apply where verification as referred to in Article 188 cannot be completed within a reasonable period of time and the goods are no longer required to be present for verification purposes.
1. All the goods covered by the same declaration shall be released at the same time.
For the purposes of the first subparagraph, where a customs declaration covers goods falling under two or more items the particulars relating to goods falling under each item shall be deemed to constitute a separate customs declaration.
Article 195
Release dependent upon payment of the amount of import or export duty corresponding to the customs debt or provision of a guarantee
1. Where the placing of goods under a customs procedure gives rise to a customs debt, the release of the goods shall be conditional upon the payment of the amount of import or export duty corresponding to the customs debt or the provision of a guarantee to cover that debt.
However, without prejudice to the third subparagraph, the first subparagraph shall not apply to temporary admission with partial relief from import duty.
Where, pursuant to the provisions governing the customs procedure for which the goods are declared, the customs authorities require the provision of a guarantee, those goods shall not be released for the customs procedure in question until such guarantee is provided.
1. In specific cases, the release of the goods shall not be conditional upon the provision of a guarantee in respect of goods which are the subject of a drawing request on a tariff quota.
2. Where a simplification as referred to in Articles 166, 182 and 185 is used and a comprehensive guarantee is provided, release of the goods shall not be conditional upon a monitoring of the guarantee by the customs authorities.
Article 196
Delegation of power
The Commission shall be empowered to adopt delegated acts, in accordance with Article 284, in order to determine the cases referred to in Article 195(2).
CHAPTER 4
Disposal of goods
Article 197
Destruction of goods
```

### Retrieved: L_2011127EN.01000101 / chunk_138

Resolution: document_chunk_sqlite

```text
1. In order to ensure the proper application of this Protocol, the Parties shall assist each other, through the customs authorities, in checking the authenticity of the proofs of origin and the correctness of the information given in these documents.
2. Subsequent verifications of proofs of origin shall be carried out at random or whenever the customs authorities of the importing Party have reasonable doubts as to the authenticity of such documents, the originating status of the products concerned or the fulfilment of the other requirements of this Protocol.
3. For the purposes of implementing the provisions of paragraph 1, the customs authorities of the importing Party shall return the proofs of origin or a copy of these documents, to the customs authorities of the exporting Party giving, where appropriate, the reasons for the enquiry. Any documents and information obtained suggesting that the information given on proof of origin is incorrect shall be forwarded in support of the request for verification.
4. The verification shall be carried out by the customs authorities of the exporting Party. For this purpose, they shall have the right to call for any evidence and to carry out any inspection of the exporter's accounts or any other check considered appropriate.
5. If the customs authorities of the importing Party decide to suspend the granting of preferential treatment to the products concerned while awaiting the results of the verification, release of the products shall be offered to the importer subject to any precautionary measures judged necessary.
6. The customs authorities requesting the verification shall be informed of the results of this verification including findings and facts, as soon as possible. These results must indicate clearly whether the documents are authentic and whether the products concerned can be considered as products originating in a Party and fulfil the other requirements of this Protocol.
7. If in cases of reasonable doubt there is no reply within 10 months of the date of the verification request or if the reply does not contain sufficient information to determine the authenticity of the document in question or the real origin of the products, the requesting customs authorities shall except in exceptional circumstances, refuse entitlement to the preference.
8. Notwithstanding Article 2 of the Protocol on Mutual Administrative Assistance in Customs Matters, the Parties will refer to Article 7 of that Protocol for joint enquiries related to proofs of origin.
Article 28
Dispute settlement
1. Where disputes arise in relation to the verification procedures of Article 27 which cannot be settled between the customs authorities requesting verification and the customs authorities responsible for carrying out this verification or where they raise a question as to the interpretation of this Protocol, they shall be submitted to the Customs Committee.
2. In all cases the settlement of disputes between the importer and the competent authorities of the importing Party shall be under the legislation of the said Party.
Article 29
Penalties
Penalties shall be imposed in accordance with the legislation of the Parties on any person who draws up, or causes to be drawn up, a document which contains incorrect information for the purpose of obtaining preferential treatment for products.
Article 30
Free zones
1. The Parties shall take all necessary steps to ensure that products traded under cover of a proof of origin which in the course of transport use a free zone situated in their territories, are not substituted by other products and do not undergo handling other than normal operations designed to prevent their deterioration.
2. By means of an exemption to the provisions contained in paragraph 1, when products originating in a Party enter into a free zone under cover of a proof of origin and undergo treatment or processing, another proof of origin can be made out if the treatment or processing undergone is in conformity with the provisions of this Protocol.
SECTION C
CEUTA AND MELILLA
TITLE VII
Ceuta and Melilla
Article 31
Application of the Protocol
1. The term 'EU Party' does not cover Ceuta and Melilla.
2. Products originating in Korea, when imported into Ceuta or Melilla, shall enjoy in all respects the same customs regime as that which is applied to products originating in the customs territory of the European Union under Protocol 2 of the Act of Accession of the Kingdom of Spain and the Portuguese Republic to the European Communities. Korea shall grant to imports of products covered by this Agreement and originating in Ceuta and Melilla the same customs regime as that which is granted to products imported from and originating in the EU Party.
3. For the purpose of the application of paragraph 2 concerning products originating in Ceuta and Melilla, this Protocol shall apply mutatis mutandis subject to the special conditions set out in Article 32.
Article 32
Special conditions
1. Providing they have been transported directly in accordance with the provisions of Article 13, the following shall be considered as:
```

### Retrieved: L_2019222EN.01000101 / chunk_17

Resolution: document_chunk_sqlite

```text
1. Subsequent verifications of proof of origin shall be carried out on the basis of a risk analysis, by random sampling or whenever the customs authorities of the importing country have reasonable doubts as to the authenticity of such documents, the originating status of the products concerned or compliance with the other requirements of this Protocol. 2. For the purposes of implementing paragraph 1 of this Article, the customs authorities of the importing country shall return the movement certificate EUR.1 and the invoice, if it has been submitted, the origin declaration, or a copy of these documents, to the customs authorities of the exporting country giving, where appropriate, the reasons for the request for verification. Any documents and information obtained suggesting that the information given on the proof of origin is incorrect shall be forwarded in support of the request for verification. 3. The verification shall be carried out by the customs authorities of the exporting country. For that purpose, they shall have the right to call for any evidence and to carry out any inspection of the exporter's accounts or any other check considered appropriate. 4. If the customs authorities of the importing country decide to suspend the granting of preferential treatment to the products concerned while awaiting the results of the verification, release of the products shall be offered to the importer subject to any precautionary measures deemed necessary. 5. The customs authorities requesting the verification shall be informed of the results thereof as soon as possible. Those results must indicate clearly whether the documents are authentic and whether the products concerned can be considered as products originating in Côte d'Ivoire, in the European Union or in one of the other countries referred to in Articles 6, 7 and 8 of this Protocol and fulfil the other requirements of this Protocol. 6. If in cases of reasonable doubt there is no reply within ten (10) months of the date of the verification request or if the reply does not contain sufficient information to determine the authenticity of the document in question or the real origin of the products, the requesting customs authorities shall, except in exceptional circumstances, refuse entitlement to the preferences. 7. The parties shall refer to Article 7 of Protocol 2 to the Agreement on mutual administrative assistance in customs matters for joint investigations concerning proof of origin.
Article 36
Verification of suppliers' declarations
1. Verification of suppliers' declarations shall be carried out on the basis of risk analysis, by random sampling or whenever the customs authorities of the country where such declarations have been taken into account to issue a movement certificate EUR.1 or to make out an origin declaration have reasonable doubts as to the authenticity of the document or the accuracy of the information given in this document. 2. The customs authorities to which a supplier's declaration is submitted may request the customs authorities of the State where the declaration was made out to issue an information certificate, a specimen of which appears in Annex VI to this Protocol. Alternatively, the certifying authorities to which a supplier's declaration is submitted may request that the exporter produce an information certificate issued by the customs authorities of the State where the declaration was made out. A copy of the information certificate shall be preserved by the office which has issued it for at least three (3) years. 3. The customs authorities requesting the verification shall be informed of the results thereof as soon as possible. The results must indicate clearly whether the information given in the supplier's declaration is correct and make it possible for them to determine whether and to what extent this supplier's declaration could be taken into account for issuing a movement certificate EUR.1 or for making out an origin declaration. 4. The verification shall be carried out by the customs authorities of the country where the supplier's declaration was made out. For this purpose, they shall have the right to call for any evidence or to carry out any inspection of the supplier's account or any other check which they consider appropriate in order to verify the accuracy of the supplier's declaration. 5. Any movement certificate EUR.1 or origin declaration issued or made out on the basis of an inaccurate supplier's declaration shall be considered null and void.
Article 37
Dispute settlement
1. Where disputes arise in relation to the verification procedures of Articles 35 and 36 of this Protocol which cannot be settled between the customs authorities requesting a verification and the customs authorities responsible for carrying out this verification or where they raise a question of interpretation of this Protocol, they shall be submitted to the Committee. 2. In all cases the settlement of disputes between the importer and the customs authorities of the importing country shall take place under the legislation of that country.
Article 38
Penalties
Penalties shall be imposed on any person who draws up, or causes to be drawn up, a document which contains inaccurate information for the purpose of obtaining preferential treatment for products.
Article 39
Free zones
```

### Retrieved: L_2012111EN.01000101 / chunk_36

Resolution: document_chunk_sqlite

```text
1. Subsequent verifications of proofs of origin shall be carried out based on risk analysis and at random or whenever the customs authorities of the importing country have reasonable doubts as to the authenticity of such documents, the originating status of the products concerned or the fulfilment of the other requirements of this Protocol.
2. For the purposes of implementing the provisions of paragraph 1, the customs authorities of the importing country shall return the movement certificate EUR.1 and the invoice, if it has been submitted, the invoice declaration, or a copy of these documents, to the customs authorities of the exporting country giving, where appropriate, the reasons for the request of verification. Any documents and information obtained suggesting that the information given on the proof of origin is incorrect shall be forwarded in support of the request for verification.
3. The verification shall be carried out by the customs authorities of the exporting country. For this purpose, they shall have the right to call for any evidence and to carry out any inspection of the exporter's or manufacturer's accounts or any other check considered appropriate.
4. If the customs authorities of the importing country decide to suspend the granting of preferential treatment to the products concerned while awaiting the results of the verification, release of the products shall be offered to the importer subject to any precautionary measures judged necessary.
5. The customs authorities requesting the verification shall be informed of the results of this verification as soon as possible. These results must indicate clearly whether the documents are authentic and whether the products concerned can be considered as products originating in an ESA State, in the Community or in one of the other countries referred to in Articles 3, 4 and 5 and fulfil the other requirements of this Protocol.
6. If in cases of reasonable doubt there is no reply within 10 months of the date of the verification request or if the reply does not contain sufficient information to determine the authenticity of the document in question or the real origin of the products, the requesting customs authorities shall, except in exceptional circumstances, refuse entitlement to the preferences.
7. Where the verification procedure or any other available information appears to indicate that the provisions of this Protocol are being contravened, the exporting country on its own initiative or at the request of the importing country shall carry out appropriate enquires or arrange for such enquiries to be carried out with due urgency to identify and prevent such contraventions and for this purpose the exporting country concerned may invite the participation of the importing country in these verifications.
Article 37
Verification of suppliers' declarations
1. Verification of suppliers' declarations shall be carried out based on risk analysis and at random or whenever the customs authorities of the country where such declarations have been taken into account to issue a movement certificate EUR.1 or to make out an invoice declaration, have reasonable doubts as to the authenticity of the document or the correctness of the information given in this document.
2. The customs authorities to which a supplier's declaration is submitted may request the customs authorities of the State where the declaration was made to issue an information certificate, a specimen of which appears in Annex VI to this Protocol. Alternatively, the certifying authorities to which a supplier's declaration is submitted may request the exporter to produce an information certificate issued by the customs authorities of the State where the declaration was made.
A copy of the information certificate shall be preserved by the office which has issued it for at least three years.
1. The customs authorities requesting the verification shall be informed of the results thereof as soon as possible. The results must indicate clearly whether the information given in the supplier's declaration is correct and make it possible for them to determine whether and to what extent this supplier's declaration could be taken into account for issuing a movement certificate EUR.1 or for making out an invoice declaration.
2. The verification shall be carried out by the customs authorities of the country where the supplier's declaration was made out. For this purpose, they shall have the right to call for any evidence or to carry out any inspection of the supplier's account or any other check which they consider appropriate in order to verify the correctness of any supplier's declaration.
3. Any movement certificate EUR.1 or invoice declaration issued or made out on the basis of an incorrect supplier's declaration shall be considered null and void.
Article 38
Dispute settlement
Where disputes arise in relation to the verification procedures of Articles 36 and 37 which cannot be settled between the customs authorities requesting a verification and the customs authorities responsible for carrying out this verification or where they raise a question as to the interpretation of this Protocol, they shall be submitted to the Customs Cooperation Committee.
In all cases the settlement of disputes between the importer and the customs authorities of the importing country shall take place under the legislation of that country.
Article 39
Penalties
Penalties shall be imposed on any person who draws up, or causes to be drawn up, a document which contains incorrect information for the purpose of obtaining a preferential treatment for products.
Article 40
Free zones
```

### Retrieved table: L_2019332EN.01001901 / table_12

```json
{
  "document_id": "L_2019332EN.01001901",
  "table_id": "table_12",
  "row_ids": [
    1
  ],
  "headers": null,
  "rows": [
    [
      "The undersigned customs official requests verification of the authenticity and accuracy of this information certificate.",
      "Verification carried out by the undersigned customs official shows that this information certificate:"
    ]
  ]
}
```

### Retrieved table: L_2021355EN.01000601 / table_4

```json
{
  "document_id": "L_2021355EN.01000601",
  "table_id": "table_4",
  "row_ids": [
    1
  ],
  "headers": null,
  "rows": [
    [
      "The undersigned customs official requests verification of the authenticity and accuracy of this information certificate.",
      "Verification carried out shows that this information certificate:"
    ]
  ]
}
```

### Retrieved table: L_202402145EN / table_22

```json
{
  "document_id": "L_202402145EN",
  "table_id": "table_22",
  "row_ids": [
    0
  ],
  "headers": null,
  "rows": [
    [
      "Applicable customs procedures for the verification of the Importer Statement for Cultural Goods",
      "01, 07, 40, 42, 43, 51, 53, 71"
    ]
  ]
}
```

### Retrieved table: L_2019332EN.01001901 / table_12

```json
{
  "document_id": "L_2019332EN.01001901",
  "table_id": "table_12",
  "row_ids": [
    3
  ],
  "headers": null,
  "rows": [
    [
      "",
      "(a) was issued by the customs office indicated and that the information contained therein is accurate( *"
    ]
  ]
}
```

### Retrieved table: L_202402145EN / table_19

```json
{
  "document_id": "L_202402145EN",
  "table_id": "table_19",
  "row_ids": [
    0
  ],
  "headers": null,
  "rows": [
    [
      "Applicable customs procedures for the verification of the Import Licence for Cultural Goods",
      "01, 07, 40, 42, 43, 51, 53, 71"
    ]
  ]
}
```
