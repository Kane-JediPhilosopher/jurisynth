export interface VectorChunk {
  id: string;
  docId: string;
  docTitle: string;
  citation: string;
  year: number;
  court: string;
  chunkNumber: number;
  tokenOffset: [number, number];
  vectorDimension: string;
  jurisdictionBinding: string;
  cosineSimilarity: number;
  rawExtract: string;
  bluebookCitation: string;
  lexisWestlawId: string;
  fullOpinionSnippet: string;
}

export interface SynthesizedClaim {
  id: number;
  title: string;
  confidence: number;
  summary: string;
  quote?: string;
  statute: string;
  precedentRef: string;
  chunkId: string;
  court: string;
  year: number;
}

export interface ConflictAlertItem {
  title: string;
  tag: string;
  description: string;
  primaryPrecedent: string;
  recentCase: string;
  chunkId?: string;
}

export interface DossierMetadata {
  court: string;
  matterId: string;
  matterName: string;
  corpusVersion: string;
  verificationHash: string;
  embeddingModel: string;
  systemHealth: string;
}
