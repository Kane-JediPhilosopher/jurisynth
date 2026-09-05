export interface JurisynthDossier {
  query: string | null;
  overview: string;
  sections: unknown[];
  contradiction_refs: string[];
  status: 'ready' | 'complete';
  disclaimer: string;
}

const API_BASE = import.meta.env.VITE_JURISYNTH_API_BASE ?? 'http://127.0.0.1:8000';

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
