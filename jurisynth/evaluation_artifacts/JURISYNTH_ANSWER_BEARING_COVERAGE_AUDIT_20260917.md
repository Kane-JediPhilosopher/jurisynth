# Jurisynth answer-bearing coverage audit

Date: 2026-09-17  
Mode: read-only; no production code, prompt, threshold, ranking, scope, or artifact changes were made.

## Executive finding

The corpus is not the cause of the audited failures. Every named expected legal document is present in the repaired v2 document sidecar, chunk index, and Oxigraph store, and every one contributes graph-qualified quads.

The observed failures divide into four materially different groups:

1. Six global-suite cases use ambiguous, temporally incoherent, or cross-agreement expected-source assumptions. Several of them retrieved an answer-bearing alternate source and answered correctly despite receiving zero strict expected-document credit.
2. Multi-regime AI-medical leaves are scoped too narrowly when they name `AI Act` plus `GDPR`: only the AI Act resolves. The `gdpr` alias is ambiguous in the metadata sidecar, and the resolver returns the direct leaf scope without consulting contextual constraints once any direct key exists.
3. Some AI Act provisions are genuinely missed by retrieval even though their document, chunks, and KG assertions are present. The most consequential examples are Article 6, Article 72, and complete Article 73/79 context.
4. One clear downstream failure exists: organized q004 received the Article 25 role-change rule in its EvidenceBundle but still returned `insufficient_evidence`.

The image-primary smoke also exposes one deterministic implementation defect: aggregated image metadata paths contain `batch_xxxx/image_store/file`, while the global expander root is already `.../images/image_store`. `ImageExpander._expand_one` therefore constructs a non-existent path, silently returns the unexpanded caption, and `RetrievalMechanism` still increments `image_expanded_count`.

## Evidence inventory

All expected documents below are present in `jurisynth/global_artifacts_source_uri_v2`.

| Document | Canonical identity available | Chunks | Graph-qualified quads | Tables | Images |
|---|---|---:|---:|---:|---:|
| `L_1994001EN.01000101` | title only | 311 | 5,351 | 109 | 48 |
| `L_2016119EN.01000101` | Regulation (EU) 2016/679 | 73 | 2,427 | 0 | 0 |
| `L_202401689EN` | Regulation (EU) 2024/1689; ELI `http://data.europa.eu/eli/reg/2024/1689/oj` | 127 | 3,669 | 0 | 0 |
| `L_2011282EN.01000101` | Regulation (EU) 1006/2011 | 599 | 14,674 | 27 | 3 |
| `L_2008291EN.01000101` | Regulation (EC) 1031/2008 | 598 | 14,662 | 41 | 3 |
| `L_2016294EN.01000101` | Regulation (EU) 2016/1821 | 625 | 14,380 | 26 | 3 |
| `L_2007345EN.01000101` | title only | 60 | 1,413 | 54 | 10 |
| `L_2011127EN.01000101` | title only | 159 | 4,727 | 74 | 264 |
| `L_2008289EN.01000101` | title only | 147 | 4,096 | 23 | 93 |
| `L_2008142EN.01000101` | Regulation (EC) 440/2008 | 405 | 13,451 | 228 | 339 |
| `L_2017175EN.01000101` | Regulation (EU) 2017/1151 | 249 | 5,366 | 301 | 720 |
| `L_2017117EN.01000101` | Regulation (EU) 2017/745 (MDR) | 137 | 4,635 | 1 | 1 |
| `L_2017117EN.01017601` | Regulation (EU) 2017/746 (IVDR) | 118 | 3,854 | 1 | 1 |

The sidecar has no CELEX value for these records. The canonical values above come from ELI or deterministic citation keys extracted from the primary title; no identity was inferred from a filename.

## Case-by-case audit

Legend: `Y` = answer-bearing hit; `P` = partial/related material; `N` = no answer-bearing hit; `—` = modality not relevant. Stage numbers correspond to the owner’s six-stage taxonomy.

| Case / missing issue | Expected source | In corpus? | In scope? | Assertion hit? | Chunk hit? | Table hit? | Image hit? | Entered EvidenceBundle? | Root-cause stage |
|---|---|---|---|---|---|---|---|---|---|
| `parallel_ai_act_gdpr` — GDPR Article 13 | `L_2016119EN.01000101` | Y | Y as target, but uncovered | N | N; unrelated sectoral controller texts only | N | N | N | **3** — the single explicit GDPR target was not retrieved; source recovery is restricted to multi-target leaves |
| `image_primary` — Image 1 | `L_1994001EN.01000101` | Y; Image 1 is indexed and captioned as two signatures | N; document ID in leaf text produced `scope=none` | N | N | N | N; five unrelated global images | N | **2**, then **3** — explicit source ID never became document scope; expected image was outside top 5 |
| `global_natural_001` | `L_1994001EN.01000101:chunk_50` | Y | unscoped | P | **Y alternate:** `L_2009107EN.01016501:chunk_76`, rank 2, score 0.6310 | N | N | Y | **6** — strict source miss, but semantically equivalent answer-bearing law was retrieved and used |
| `global_natural_005` | `L_2011282EN.01000101:chunk_271` | Y | unscoped | P | **Y alternate:** `L_2013290EN.01000101:chunk_270`, rank 1, score 0.6929; other editions also hit | N | N | Y | **6** — expected edition miss, not answer-bearing failure |
| `global_natural_013` — vinegar + water-pipe tobacco | 2008 and 2016 CN editions | Y | unscoped | P | Water-pipe exact source rank 2, score 0.7287; vinegar rule supplied by another edition | N | P | Y | **6** — temporal/version coherence is not specified; the compound gold is ambiguous |
| `global_natural_015` — denial + origin verification | EEA decision + Montenegro agreement | Y | unscoped | P | Origin rule retrieved; denial/reasons answer-bearing alternate fell outside the retained top-8 in this wording | N | N | partial | **6** primary (incoherent agreements); **4** secondary (answer-bearing customs chunk not retained) |
| `global_natural_016` — trade committee + IP injunction | EU–Korea + CARIFORUM | Y | unscoped | P | IP injunction alternate at rank 3, score 0.6461; trade-committee provision missed | N | N | partial | **6** — the question falsely treats distinct agreement frameworks as jointly applicable |
| `global_natural_017` — toxicology + road-load data | REACH test-method + vehicle regulation | Y | unscoped | P | Neither exact answer-bearing chunk was retrieved | P; `L_2017175...` tables only exposed a generic road-load subject row | N | N | **6** primary (artificial join); **3** secondary (both answer-bearing chunks missed) |
| Organized/messy — statutory AI Act role definitions and multi-role rule | AI Act `chunk_44`; Article 25 spans `chunks_60–61` | Y | AI Act in scope | P | Organized q001 retrieved authorised-representative material, not definitions; messy q001 similar | N | N | partial | **3** — required definition/multi-role chunks did not reach these leaves |
| Organized/messy — high-risk medical-device criterion | AI Act Article 6 `chunk_50`; MDR/IVDR classification context | Y | AI Act only; MDR contextual | P | Article 43 and Annex III material reached q002, but Article 6’s two-part rule did not | N | N | partial | **3** — complementary Article 6/MDR evidence absent from bundle |
| Organized — provider role change after modification | AI Act Article 25 `chunks_60–61` | Y | Y | P | **Y:** `C_44d17aacd4923a7b` is `L_202401689EN:chunk_61` | N | N | **Y** | **5** — Leaf Answer ignored/mishandled the exact rule and returned `insufficient_evidence` |
| Messy — provider role change after modification | AI Act Article 25 `chunks_60–61` | Y | Y | P | Only authorised-representative and general provider material was preserved; exact Article 25 rule was absent | N | N | N | **3** — run-to-run query/decomposition differences changed candidate coverage |
| Organized/messy — GDPR Articles 6 and 9 | GDPR `chunks_32–33` | Y | **N in multi-regime leaves** | N | N | — | — | N | **2** — explicit `GDPR` alias did not resolve, so no GDPR source recovery occurred |
| Organized/messy — purpose limitation / further processing | GDPR `chunks_32–33` | Y | N | N | N | — | — | N | **2** — same narrow scope; needed GDPR chunks never entered retrieval |
| Organized/messy — automated decision-making | GDPR Article 22 in `chunk_39` (with related disclosure text in `chunk_36`) | Y | N | N | N | — | — | N | **2** — same narrow scope; unrelated UK/sectoral material was retrieved instead |
| Organized/messy — AI Act/GDPR overlap and lawful-basis separation | AI Act `chunks_3` and `35`; GDPR Articles 5/6/9/22 | Y | AI Act only | P | AI Act overlap recital was retrieved in related traces; GDPR half was missing | — | — | partial | **2** primary; **3** complementary — scope prevented the required two-regime evidence set |
| Organized/messy — monitoring, corrective action, recall/withdrawal, serious incident | AI Act `chunks_57–58`, `62`, `89–90`, `93–96`; MDR vigilance provisions | Y | AI Act only; MDR contextual | P | Some importer/distributor and serious-incident material reached bundles, but complete Articles 72/73/79 and MDR sequence did not | N | N | partial | **3** — answer correctly refused to invent the missing responsibility chain |

## Scope-resolution audit

Running the current deterministic `DocumentMetadataStore.resolve_request_scope` against the saved leaves produced:

- organized q001–q007: only `citation:regulation:2024:1689`;
- messy q001–q004: only `citation:regulation:2024:1689`;
- `parallel_ai_act_gdpr` q002: correctly resolved `citation:regulation:2016:679` because the full citation appeared in the leaf;
- `image_primary`: no scope, despite the exact document ID appearing in the leaf.

The cause is deterministic:

1. `document_metadata.py:95–105` returns as soon as the leaf query yields any target key and does not then consider contextual facts/constraints.
2. `gdpr` has three alias rows: the GDPR itself and its corrigendum map to Regulation 2016/679, but an EEA Joint Committee decision whose title contains “General Data Protection Regulation” maps to Decision 2018/893. The conservative intersection at `document_metadata.py:180–189` therefore resolves no stable GDPR key.
3. Because `AI Act` resolves successfully, the scope becomes AI-Act-only even when the same leaf explicitly says GDPR.
4. `mechanism.py:89–96` performs deterministic source recovery only when more than one target key already resolved. That means the missing GDPR key cannot trigger recovery, and a single uncovered target such as the Article 13 leaf does not trigger recovery either.

This confirms that current scoping is too narrow for the audited AI Act + GDPR + MDR questions. Cross-instrument evidence is preserved when normal retrieval happens to find it, so the defect is not deletion of already-retrieved evidence; it is failure to identify all explicitly required instruments and therefore failure to run the bounded source pass for them.

## Image-path audit

`image_primary` did execute image FAISS retrieval:

- pass 1 raw candidates: 5;
- pass 2 raw candidates: 5, but none belonged to the expected document;
- merged images: five unrelated documents;
- trace field `image_expanded_count`: 2;
- actual expanded descriptions: 0;
- expansion latency: 4.083 ms, which is inconsistent with a live vision request.

The expected indexed record exists:

- image ID: `L_1994001EN.01000101:image:001`;
- caption: two black-ink signatures on a white background;
- stored metadata relative path begins `batch_0001/image_store/...`.

The definitive path defect is:

- global construction passes `.../images/image_store` as the expander root (`main.py:113`);
- `_expand_one` appends the metadata relative path directly (`image_expander.py:64`), producing `.../images/image_store/batch_0092/image_store/file.jpg`;
- the real file is `.../images/image_store/batch_0092/file.jpg`;
- `_expand_one` silently returns the original item when the constructed path is absent (`image_expander.py:65–66`);
- `mechanism.py:169–172` nevertheless counts the returned unchanged items as expanded.

Therefore the latest global suite exercised image-caption FAISS retrieval but **did not actually exercise vision parsing/ImageExpander inference**.

Smallest future fix (not implemented): normalize aggregate `relative_path` values against the aggregate store root, or make `_expand_one` resolve both the canonical aggregate path and the legacy nested path; then count only items whose `expanded_description` was populated. Add a path-resolution regression test using a real aggregate-style record.

## Root-cause counts

Using one primary classification for each of the 16 rows above:

- Stage 1 — absent from corpus: **0**
- Stage 2 — scoping failure: **5**
- Stage 3 — retrieval-channel failure: **4**
- Stage 4 — merge/ranking loss: **0 primary**, **1 secondary** (`global_natural_015`)
- Stage 5 — downstream interpretation failure: **1 primary**, plus one secondary messy-q002 inconsistency (the answer said there was no AI Act material although AI Act evidence IDs were present)
- Stage 6 — wrong/ambiguous expected-source assumption: **6**

These are not one single defect. They are four independent limitations:

1. benchmark/gold coherence problems in six global cases;
2. a systematic multi-regime scope-resolution gap;
3. ordinary retrieval recall gaps for complementary provisions;
4. downstream leaf-answer conservatism/mishandling in at least one decisive case.

The image expander path mismatch is a separate deterministic implementation bug.

## Auditability limitation

The global-suite case files preserve full EvidenceBundles, scores, and modality traces. The organized/messy complex artifacts preserve leaf answers and compact evidence IDs, but not the complete EvidenceBundle payload or Query Interpreter concepts for every leaf. The older zero-NIM replay preserves full q001–q004 bundles and was used only to resolve stable repeated evidence IDs; it was not treated as proof that every latest-run candidate was identical. Where the latest compact artifact did not preserve a candidate score or source payload, this report says `partial`, `absent from retained trace`, or `unknown` rather than inventing a rank.

## Inspected artifacts

- `jurisynth/run_outputs/global_agentic_temporary_super_20260917/*.json`
- `jurisynth/run_outputs/global_complex_ai_medical_organized_super_20260917.json`
- `jurisynth/run_outputs/global_complex_ai_medical_messy_super_20260917.json`
- `jurisynth/run_outputs/zero_nim_replay_20260917.json`
- `jurisynth/reasoning_logs/global_smoke_2223.jsonl`
- `jurisynth/reasoning_logs/global_smoke_844.jsonl`
- `jurisynth/evaluation_artifacts/global_natural_candidate_packet.json`
- `jurisynth/global_artifacts_source_uri_v2/document_metadata.sqlite`
- `jurisynth/global_artifacts_source_uri_v2/chunk_index/chunk_metadata.sqlite`
- `jurisynth/global_artifacts_source_uri_v2/oxigraph`
- `jurisynth/global_artifacts_source_uri_v2/tables`
- `jurisynth/global_artifacts_source_uri_v2/images`

