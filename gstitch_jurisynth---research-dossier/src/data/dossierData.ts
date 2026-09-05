import { VectorChunk, SynthesizedClaim, ConflictAlertItem, DossierMetadata } from '../types';

export const initialDossierMeta: DossierMetadata = {
  court: 'Delaware Court of Chancery',
  matterId: 'Matter 2024-DE-Caremark',
  matterName: 'In re SolarWinds Derivative',
  corpusVersion: '2024.11-DE-CH',
  verificationHash: 'e7f4c9a8120d9e83fa244199c0bb18a',
  embeddingModel: 'OpenAI text-3-large (1536-dim)',
  systemHealth: '99.9%',
};

export const indexedChunks: VectorChunk[] = [
  {
    id: 'chunk-stone-14',
    docId: '#402',
    docTitle: 'Stone v. Ritter (Del. 2006)',
    citation: '911 A.2d 362 (Del. 2006)',
    year: 2006,
    court: 'Delaware Supreme Court',
    chunkNumber: 14,
    tokenOffset: [1420, 1804],
    vectorDimension: '1536-dim (Text-Embedding-3)',
    jurisdictionBinding: 'Supreme Court of DE',
    cosineSimilarity: 0.941,
    rawExtract:
      '"...liability requires bad faith. Where directors utterly fail to implement a reporting system or consciously fail to oversee operations, they violate the fiduciary duty of loyalty."',
    bluebookCitation: 'Stone v. Ritter, 911 A.2d 362, 370 (Del. 2006).',
    lexisWestlawId: 'Lexis 911 A.2d 362',
    fullOpinionSnippet: `IN THE SUPREME COURT OF THE STATE OF DELAWARE
WILLIAM J. STONE, et al., Plaintiffs Below, Appellants,
v.
PATRICIA A. RITTER, et al., Defendants Below, Appellees.
No. 93, 2006. Decided: November 6, 2006.

HOLLAND, Justice:
This is an appeal from a final judgment of the Court of Chancery dismissing a shareholder derivative complaint. The complaint alleged that the defendant directors failed to implement adequate anti-money laundering monitoring controls under the Bank Secrecy Act at AmSouth Bancorporation.

[Chunk #14 - 911 A.2d at 370]
"Where a claim of directorial liability for corporate loss is predicated upon ignorance of liability creating activities within the corporation... only a sustained or systematic failure of the board to exercise oversight—such as an utter failure to attempt to assure a reasonable information and reporting system exists—will establish the lack of good faith that is a necessary condition to liability. The fiduciary duty of loyalty encompasses the duty of oversight; thus, a failure to act in good faith results in a breach of the duty of loyalty, precluding exculpation under 8 Del. C. § 102(b)(7)."`,
  },
  {
    id: 'chunk-boeing-32',
    docId: '#118',
    docTitle: 'In re Boeing Co. Deriv. Litig.',
    citation: '2021 WL 4059934 (Del. Ch. 2021)',
    year: 2021,
    court: 'Delaware Court of Chancery',
    chunkNumber: 32,
    tokenOffset: [2104, 2580],
    vectorDimension: '1536-dim (Text-Embedding-3)',
    jurisdictionBinding: 'Del. Court of Chancery',
    cosineSimilarity: 0.887,
    rawExtract:
      '"Airplane safety constitutes an essential, non-delegable compliance imperative. The board failed to establish any safety committee, received no regular reports regarding 737 MAX safety, and treated regulatory compliance as ordinary business risk."',
    bluebookCitation: "In re Boeing Co. Deriv. Litig., No. 2019-0907-MTZ, 2021 WL 4059934, at *25 (Del. Ch. Sept. 7, 2021).",
    lexisWestlawId: '2021 Del. Ch. LEXIS 201',
    fullOpinionSnippet: `IN THE COURT OF CHANCERY OF THE STATE OF DELAWARE
IN RE THE BOEING COMPANY DERIVATIVE LITIGATION
Consolidated C.A. No. 2019-0907-MTZ. Decided: September 7, 2021.

ZURN, Vice Chancellor:
[Chunk #32]
"When a board faces mission-critical compliance responsibilities—here, the physical safety of commercial passenger aircraft—directors must rigorously establish board-level systems to monitor safety. Mission-critical safety oversight at board level cannot be satisfied by general audit committee reviews that focus strictly on financial accounting. The failure to put safety protocols on the formal board agenda or receive scheduled updates constitutes conscious disregard sufficient to support a Caremark prong-one claim at the pleading stage."`,
  },
  {
    id: 'chunk-marchand-08',
    docId: '#094',
    docTitle: 'Marchand v. Barnhill (Del. 2019)',
    citation: '212 A.3d 805 (Del. 2019)',
    year: 2019,
    court: 'Delaware Supreme Court',
    chunkNumber: 8,
    tokenOffset: [980, 1312],
    vectorDimension: '1536-dim (Text-Embedding-3)',
    jurisdictionBinding: 'Supreme Court of DE',
    cosineSimilarity: 0.862,
    rawExtract:
      '"Under Caremark, to satisfy their duty of loyalty, directors must make a good faith effort to implement an oversight system and monitor it. At Blue Bell Creameries, food safety was the core business risk, yet the board had no committee, no regular reporting, and no protocol to address listeria red flags."',
    bluebookCitation: 'Marchand v. Barnhill, 212 A.3d 805, 822 (Del. 2019).',
    lexisWestlawId: 'Lexis 212 A.3d 805',
    fullOpinionSnippet: `IN THE SUPREME COURT OF THE STATE OF DELAWARE
JACK L. MARCHAND II, Plaintiff Below, Appellant,
v.
PAUL W. BARNHILL, JR., et al., Defendants Below, Appellees.
No. 533, 2018. Decided: June 18, 2019.

STRINE, Chief Justice:
[Chunk #08 - 212 A.3d at 822]
"Although Caremark is a steep hurdle, when a monoline company manufactures food products where contamination poses life-or-death hazards, food safety is mission-critical. The board has a non-delegable obligation to institute board-level reporting. Relying solely on operational management with no board-level monitoring system in place constitutes an utter failure to attempt oversight."`,
  },
  {
    id: 'chunk-mcdonalds-19',
    docId: '#512',
    docTitle: "In re McDonald's Corp. (Del. Ch. 2023)",
    citation: '289 A.3d 343 (Del. Ch. 2023)',
    year: 2023,
    court: 'Delaware Court of Chancery',
    chunkNumber: 19,
    tokenOffset: [3410, 3890],
    vectorDimension: '1536-dim (Text-Embedding-3)',
    jurisdictionBinding: 'Del. Court of Chancery',
    cosineSimilarity: 0.824,
    rawExtract:
      '"Corporate officers owe fiduciary duties of oversight within their areas of responsibility equivalent to those owed by directors. An executive Vice President who consciously ignores widespread sexual harassment breaches the duty of loyalty."',
    bluebookCitation: "In re McDonald's Corp. S'holder Deriv. Litig., 289 A.3d 343, 365 (Del. Ch. 2023).",
    lexisWestlawId: '2023 Del. Ch. LEXIS 23',
    fullOpinionSnippet: `IN THE COURT OF CHANCERY OF THE STATE OF DELAWARE
IN RE MCDONALD'S CORPORATION SHAREHOLDER DERIVATIVE LITIGATION
C.A. No. 2021-0324-JTL. Decided: January 26, 2023.

LASTER, Vice Chancellor:
[Chunk #19 - 289 A.3d at 365]
"This decision clarifies that corporate officers owe the same fiduciary duties of care and loyalty as directors, including the duty of oversight established under Caremark. However, an officer's oversight obligation is contextual: while the CEO and Chief Legal Officer have firm-wide scope, other officers are bound within their delegated spheres of authority. When an officer with oversight over human resources consciously ignores rampant misconduct, that officer acts in bad faith."`,
  },
  {
    id: 'chunk-caremark-01',
    docId: '#001',
    docTitle: "In re Caremark Int'l Inc. Deriv. Litig.",
    citation: '698 A.2d 959 (Del. Ch. 1996)',
    year: 1996,
    court: 'Delaware Court of Chancery',
    chunkNumber: 1,
    tokenOffset: [800, 1150],
    vectorDimension: '1536-dim (Text-Embedding-3)',
    jurisdictionBinding: 'Del. Court of Chancery',
    cosineSimilarity: 0.912,
    rawExtract:
      '"...a sustained or systematic failure of the board to exercise oversight will establish the lack of good faith that is a necessary condition to liability."',
    bluebookCitation: "In re Caremark Int'l Inc. Deriv. Litig., 698 A.2d 959, 971 (Del. Ch. 1996).",
    lexisWestlawId: 'Lexis 698 A.2d 959',
    fullOpinionSnippet: `IN THE COURT OF CHANCERY OF THE STATE OF DELAWARE
IN RE CAREMARK INTERNATIONAL INC. DERIVATIVE LITIGATION
Civil Action No. 13670. Decided: September 25, 1996.

ALLEN, Chancellor:
"In order to satisfy their supervisory obligations, directors must ensure that information and reporting systems exist that are reasonably designed to provide senior management and the board itself timely, accurate information sufficient to allow them each to reach informed judgments concerning the corporation's compliance with law and business performance."`,
  },
];

export const initialClaims: SynthesizedClaim[] = [
  {
    id: 1,
    title: 'Oversight liability requires systemic failure of information reporting systems',
    confidence: 94.2,
    summary:
      'To satisfy the second prong of Caremark/Stone, plaintiffs must prove that directors knowingly failed to exercise oversight by failing to implement any reporting or information systems, or conscious inaction regarding red flags.',
    quote:
      '“Where a claim of directorial liability for corporate loss is predicated upon ignorance of liability creating activities within the corporation... only a sustained or systematic failure of the board to exercise oversight—such as an utter failure to attempt to assure a reasonable information and reporting system exists—will establish the lack of good faith that is a necessary condition to liability.”',
    statute: '§ 12(b)(6) · Stone v. Ritter, 911 A.2d 362 · Chunk #14',
    precedentRef: 'Stone v. Ritter',
    chunkId: 'chunk-stone-14',
    court: 'Del. Supreme Court',
    year: 2006,
  },
  {
    id: 2,
    title: 'In re Boeing Co., 2021 — Distinguishing mission-critical regulatory compliance from business risk management',
    confidence: 89.0,
    summary:
      'Airplane safety constitutes an essential, non-delegable compliance imperative. Failure of the board to establish a specialized safety committee or agenda items qualifies as breach of oversight duty.',
    quote:
      '“Mission-critical safety oversight at board level cannot be satisfied by general audit committee reviews that focus strictly on financial accounting. The failure to put safety protocols on the formal board agenda... constitutes conscious disregard.”',
    statute: 'Del. Ch. · In re Boeing Co., 2021 WL 4059934 · Chunk #32',
    precedentRef: 'In re Boeing Co.',
    chunkId: 'chunk-boeing-32',
    court: 'Del. Court of Chancery',
    year: 2021,
  },
];

export const conflictAlert: ConflictAlertItem = {
  title: 'Uncertainty & Conflict Alert: Scope of officer vs. director oversight standards in recent dicta (Marchand v. Barnhill)',
  tag: 'Potential Split',
  description:
    "Judicial ambiguity remains regarding whether non-director executive officers share the identical bad-faith requirement or if negligence suffices under agency fiduciary standards following In re McDonald's Corp. S'holder Deriv. Litig. (2023).",
  primaryPrecedent: 'Marchand v. Barnhill (Del. 2019)',
  recentCase: "In re McDonald's Corp. S'holder Deriv. Litig. (2023)",
  chunkId: 'chunk-mcdonalds-19',
};

export const sampleQueries = [
  'Synthesize pleading threshold for officer oversight post-McDonalds with DGCL 102(b)(7) immunity',
  'Compare Caremark prong-one system failures vs. prong-two red flag conscious disregard',
  'Evaluate board duty of oversight in cybersecurity and mission-critical data breaches (SolarWinds)',
  'Application of Rule 23.1 demand futility in Caremark claims under Zuckerberg three-part test',
];
