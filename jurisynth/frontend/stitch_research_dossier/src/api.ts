export interface SourceEvidence {
  chunk_id: string;
  document_id: string;
  excerpt: string;
  similarity: number | null;
}

export interface EvidenceItem {
  evidence_id: string;
  assertion: { subject: string; predicate: string; object: string };
  sources: SourceEvidence[];
  retrieval_origins: string[];
  community_ids: string[];
}

export interface ReportClaim {
  claim_id: string;
  text: string;
  status: string;
  evidence: EvidenceItem[];
}

export interface ReportSection {
  section_id: string;
  title: string;
  answer_text: string;
  claims: ReportClaim[];
  child_sections: ReportSection[];
}

export interface AuxiliaryImage {
  image_id: string;
  document_id: string;
  description: string;
  expanded_description: string | null;
  visual_findings: string[];
  similarity: number | null;
  expansion_relevance: number | null;
  source_url: string | null;
  alt: string | null;
  auxiliary_only: true;
}

export interface JurisynthDossier {
  query: string | null;
  overview: string;
  sections: ReportSection[];
  contradiction_refs: string[];
  auxiliary_images: AuxiliaryImage[];
  ast: unknown | null;
  status: 'ready' | 'complete' | 'partial';
  disclaimer: string;
}

const API_BASE = import.meta.env.VITE_JURISYNTH_API_BASE ?? 'http://127.0.0.1:8000';

export const imageEndpoint = (imageId: string) => `${API_BASE}/api/v1/images/${encodeURIComponent(imageId)}`;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail ?? `Jurisynth API request failed (${response.status}).`);
  }
  return response.json() as Promise<T>;
}

export const getDemoDossier = () => request<JurisynthDossier>('/api/v1/demo-dossier');

export const submitQuery = (query: string) => request<JurisynthDossier>('/api/v1/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query }),
});
