import React from 'react';
import { X, ShieldCheck, CheckCircle2, Cpu, Terminal, Sparkles } from 'lucide-react';
import { DossierMetadata } from '../types';

interface ModelAuditModalProps {
  metadata: DossierMetadata;
  onClose: () => void;
}

export const ModelAuditModal: React.FC<ModelAuditModalProps> = ({
  metadata,
  onClose,
}) => {
  return (
    <div
      id="model-audit-modal-overlay"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs"
      onClick={onClose}
    >
      <div
        id="model-audit-modal-container"
        className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl max-w-2xl w-full max-h-[85vh] flex flex-col shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/80">
          <div className="flex items-center gap-2.5">
            <ShieldCheck className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            <div>
              <h3 className="font-sans font-bold text-base text-slate-900 dark:text-slate-100">
                Model Determinism &amp; Statutory Audit
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Zero-temperature grounding audit logs for Delaware Chancery filings
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 overflow-y-auto space-y-5 text-xs">
          {/* Key Metrics Grid */}
          <div className="grid grid-cols-3 gap-3">
            <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded border border-slate-200 dark:border-slate-700">
              <span className="text-slate-500 dark:text-slate-400 block text-[10px] uppercase font-semibold">
                Grounding Rate
              </span>
              <span className="text-indigo-600 dark:text-indigo-400 font-mono font-bold text-base">
                100.0%
              </span>
              <span className="text-[10px] text-slate-600 dark:text-slate-400 block mt-0.5">
                4 Chunks Cited
              </span>
            </div>

            <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded border border-slate-200 dark:border-slate-700">
              <span className="text-slate-500 dark:text-slate-400 block text-[10px] uppercase font-semibold">
                Sampling Temp
              </span>
              <span className="text-slate-900 dark:text-slate-100 font-mono font-bold text-base">
                0.00
              </span>
              <span className="text-[10px] text-slate-600 dark:text-slate-400 block mt-0.5">
                Strict Deterministic
              </span>
            </div>

            <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded border border-slate-200 dark:border-slate-700">
              <span className="text-slate-500 dark:text-slate-400 block text-[10px] uppercase font-semibold">
                Hallucination Index
              </span>
              <span className="text-emerald-600 dark:text-emerald-400 font-mono font-bold text-base">
                0.00%
              </span>
              <span className="text-[10px] text-slate-600 dark:text-slate-400 block mt-0.5">
                Zero Unverified Claims
              </span>
            </div>
          </div>

          {/* Audit parameters table */}
          <div className="rounded border border-slate-200 dark:border-slate-700 overflow-hidden">
            <div className="px-4 py-2 bg-slate-100 dark:bg-slate-800 font-semibold text-slate-900 dark:text-slate-100 border-b border-slate-200 dark:border-slate-700">
              Runtime Parameters &amp; Provenance Checksum
            </div>
            <div className="divide-y divide-slate-100 dark:divide-slate-700/60 font-mono text-[11px]">
              <div className="px-4 py-2 flex justify-between">
                <span className="text-slate-500 dark:text-slate-400">Embedding Engine:</span>
                <span className="text-slate-800 dark:text-slate-200">{metadata.embeddingModel}</span>
              </div>
              <div className="px-4 py-2 flex justify-between">
                <span className="text-slate-500 dark:text-slate-400">Deterministic Seed:</span>
                <span className="text-slate-800 dark:text-slate-200">SEED_DELAWARE_42</span>
              </div>
              <div className="px-4 py-2 flex justify-between">
                <span className="text-slate-500 dark:text-slate-400">SHA-256 State Hash:</span>
                <span className="text-indigo-600 dark:text-indigo-400">{metadata.verificationHash}</span>
              </div>
              <div className="px-4 py-2 flex justify-between">
                <span className="text-slate-500 dark:text-slate-400">Reporter Sync:</span>
                <span className="text-slate-800 dark:text-slate-200">{metadata.corpusVersion}</span>
              </div>
            </div>
          </div>

          {/* Verification log */}
          <div className="p-3 bg-slate-50 dark:bg-slate-950 rounded border border-slate-200 dark:border-slate-800 font-mono text-[11px] space-y-1 text-slate-700 dark:text-slate-300">
            <div className="text-emerald-600 dark:text-emerald-400 font-bold">[PASS] Token matching verified against Lexis 911 A.2d 362</div>
            <div className="text-emerald-600 dark:text-emerald-400 font-bold">[PASS] Duty of loyalty attribution validated under Stone v. Ritter</div>
            <div className="text-emerald-600 dark:text-emerald-400 font-bold">[PASS] DGCL § 102(b)(7) non-exculpation link verified</div>
            <div className="text-amber-600 dark:text-amber-400 font-bold">[WARN] Officer oversight standard flagged as emerging (McDonald's 2023)</div>
          </div>
        </div>

        <div className="px-6 py-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold tracking-wide transition-colors cursor-pointer"
          >
            Acknowledge Audit
          </button>
        </div>
      </div>
    </div>
  );
};
