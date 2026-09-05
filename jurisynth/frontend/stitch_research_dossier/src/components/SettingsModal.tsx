import React, { useState } from 'react';
import { X, Sliders, Check, RotateCcw } from 'lucide-react';
import { DossierMetadata } from '../types';

interface SettingsModalProps {
  metadata: DossierMetadata;
  onUpdateMetadata: (updated: Partial<DossierMetadata>) => void;
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  metadata,
  onUpdateMetadata,
  onClose,
}) => {
  const [minConfidence, setMinConfidence] = useState<number>(85);
  const [corpusRelease, setCorpusRelease] = useState<string>(metadata.corpusVersion);
  const [embeddingModel, setEmbeddingModel] = useState<string>(metadata.embeddingModel);
  const [strictProngVerification, setStrictProngVerification] = useState<boolean>(true);

  const handleSave = () => {
    onUpdateMetadata({
      corpusVersion: corpusRelease,
      embeddingModel: embeddingModel,
    });
    onClose();
  };

  return (
    <div
      id="settings-modal-overlay"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs"
      onClick={onClose}
    >
      <div
        id="settings-modal-container"
        className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl max-w-lg w-full max-h-[85vh] flex flex-col shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/80">
          <div className="flex items-center gap-2.5">
            <Sliders className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
            <h3 className="font-sans font-bold text-base text-slate-900 dark:text-slate-100">
              Synthesis Configuration &amp; Tuners
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 overflow-y-auto space-y-4 text-xs font-sans">
          {/* Min Confidence Threshold */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center">
              <label className="font-semibold text-slate-900 dark:text-slate-100">
                Cosine Relevance Threshold: {minConfidence}%
              </label>
              <span className="font-mono text-indigo-600 dark:text-indigo-400 font-semibold">
                &gt;= 0.{minConfidence}
              </span>
            </div>
            <input
              type="range"
              min="70"
              max="98"
              value={minConfidence}
              onChange={(e) => setMinConfidence(Number(e.target.value))}
              className="w-full accent-indigo-600 cursor-pointer"
            />
            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              Excludes jurisprudential chunks with cosine similarity below this cutoff.
            </p>
          </div>

          {/* Corpus Release */}
          <div className="space-y-1.5 pt-2 border-t border-slate-200 dark:border-slate-800">
            <label className="font-semibold text-slate-900 dark:text-slate-100 block">
              Lexis/Westlaw Delaware Corpus Target
            </label>
            <select
              value={corpusRelease}
              onChange={(e) => setCorpusRelease(e.target.value)}
              className="w-full h-9 px-3 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs text-slate-900 dark:text-slate-100 focus:outline-none focus:border-indigo-500"
            >
              <option value="2024.11-DE-CH">2024.11-DE-CH (Latest Chancery &amp; Supreme Court)</option>
              <option value="2023.12-DE-CH">2023.12-DE-CH (Annual Restatement Archive)</option>
              <option value="2021.09-DE-BOEING">2021.09-DE-BOEING (Post-737 MAX Benchmark)</option>
            </select>
          </div>

          {/* Embedding Dimension */}
          <div className="space-y-1.5 pt-2 border-t border-slate-200 dark:border-slate-800">
            <label className="font-semibold text-slate-900 dark:text-slate-100 block">
              Vector Embedding Engine
            </label>
            <select
              value={embeddingModel}
              onChange={(e) => setEmbeddingModel(e.target.value)}
              className="w-full h-9 px-3 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs text-slate-900 dark:text-slate-100 focus:outline-none focus:border-indigo-500"
            >
              <option value="OpenAI text-3-large (1536-dim)">OpenAI text-3-large (1536-dim)</option>
              <option value="Cohere Embed v3 - Legal English (1024-dim)">Cohere Embed v3 - Legal English (1024-dim)</option>
              <option value="Gemini Text-Embedding-004 (768-dim)">Gemini Text-Embedding-004 (768-dim)</option>
            </select>
          </div>

          {/* Strict Prong-1/Prong-2 Checking */}
          <div className="pt-2 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between">
            <div>
              <span className="font-semibold text-slate-900 dark:text-slate-100 block">
                Enforce Dual-Prong Caremark Classification
              </span>
              <span className="text-[11px] text-slate-500 dark:text-slate-400">
                Differentiate systemic absence of controls from red-flag inaction
              </span>
            </div>
            <input
              type="checkbox"
              checked={strictProngVerification}
              onChange={(e) => setStrictProngVerification(e.target.checked)}
              className="w-4 h-4 rounded accent-indigo-600 cursor-pointer"
            />
          </div>
        </div>

        <div className="px-6 py-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 flex justify-between items-center">
          <button
            type="button"
            onClick={() => {
              setMinConfidence(85);
              setCorpusRelease('2024.11-DE-CH');
            }}
            className="text-xs text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 flex items-center gap-1 cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Defaults</span>
          </button>

          <div className="flex gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 rounded border border-slate-200 dark:border-slate-700 text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSave}
              className="px-4 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold tracking-wide transition-colors cursor-pointer"
            >
              Save Configuration
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
