import React, { useState } from 'react';
import {
  Lock,
  Copy,
  Check,
  ExternalLink,
  Layers,
  FileText,
} from 'lucide-react';
import { VectorChunk } from '../types';

interface ProvenanceDrawerProps {
  activeChunk: VectorChunk;
  secondaryChunks: VectorChunk[];
  onSelectChunk: (chunk: VectorChunk) => void;
  onOpenSlipOp: (chunk: VectorChunk) => void;
  verificationHash: string;
  embeddingModel: string;
}

export const ProvenanceDrawer: React.FC<ProvenanceDrawerProps> = ({
  activeChunk,
  secondaryChunks,
  onSelectChunk,
  onOpenSlipOp,
  verificationHash,
  embeddingModel,
}) => {
  const [copied, setCopied] = useState<boolean>(false);

  const handleCopyBluebook = () => {
    navigator.clipboard.writeText(activeChunk.bluebookCitation);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <aside
      id="evidence-provenance-drawer"
      className="w-[380px] min-w-[380px] border-l border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 flex flex-col justify-between shrink-0 h-[calc(100vh-4rem)] sticky top-16 overflow-y-auto transition-colors duration-200"
    >
      <div className="p-4 space-y-4">
        {/* Drawer Header */}
        <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
          <div>
            <h3 className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest">
              Citation Network &amp; Evidence
            </h3>
            <p className="text-xs font-semibold text-slate-900 dark:text-slate-100 mt-0.5">
              Deterministic Grounding Provenance
            </p>
          </div>
          <div className="text-right">
            <span className="text-xs font-semibold text-indigo-600 dark:text-indigo-400">
              {secondaryChunks.length + 1} Indexed Sources
            </span>
          </div>
        </div>

        {/* Cryptographic Hash Validation */}
        <div className="flex items-center justify-between px-3 py-1.5 rounded bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-[11px] font-mono text-slate-700 dark:text-slate-300 shadow-2xs">
          <div className="flex items-center gap-1.5">
            <Lock className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
            <span className="font-semibold">SHA-256 Validated</span>
          </div>
          <span
            className="text-slate-500 dark:text-slate-400 font-mono truncate max-w-[130px]"
            title={verificationHash}
          >
            {verificationHash.slice(0, 6)}...{verificationHash.slice(-4)}
          </span>
        </div>

        {/* Active Inspect Card */}
        <div
          id="active-target-chunk-card"
          className="border-2 border-indigo-600/40 dark:border-indigo-500/50 rounded-lg p-4 bg-white dark:bg-slate-800/90 space-y-3 shadow-xs transition-all duration-200"
        >
          <div className="flex items-center justify-between">
            <span className="px-2 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 text-[10px] font-bold font-mono uppercase tracking-wider border border-indigo-200 dark:border-indigo-800/50">
              ACTIVE TARGET
            </span>
            <span className="text-[11px] font-mono text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/60 px-2 py-0.5 rounded border border-indigo-200 dark:border-indigo-800/40 font-semibold">
              Cosine: {activeChunk.cosineSimilarity.toFixed(3)}
            </span>
          </div>

          <div>
            <div className="font-serif font-bold text-sm text-slate-900 dark:text-slate-100">
              {activeChunk.docTitle}
            </div>
            <div className="font-mono text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
              Doc {activeChunk.docId} · Chunk #{activeChunk.chunkNumber} · {activeChunk.lexisWestlawId}
            </div>
          </div>

          {/* Metadata table */}
          <div className="space-y-1.5 py-2 border-t border-b border-slate-100 dark:border-slate-700/60 text-[11px]">
            <div className="flex justify-between">
              <span className="text-slate-500 dark:text-slate-400">Token Offset</span>
              <span className="font-mono text-slate-800 dark:text-slate-200 font-medium">
                [{activeChunk.tokenOffset[0]} .. {activeChunk.tokenOffset[1]}]
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 dark:text-slate-400">Vector Dimension</span>
              <span className="font-mono text-slate-800 dark:text-slate-200 font-medium">
                {activeChunk.vectorDimension}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 dark:text-slate-400">Jurisdiction Binding</span>
              <span className="font-mono text-slate-800 dark:text-slate-200 font-medium">
                {activeChunk.jurisdictionBinding}
              </span>
            </div>
          </div>

          {/* Raw Extract Provenance */}
          <div className="space-y-1.5">
            <span className="text-[10px] font-bold text-slate-500 dark:text-slate-400 tracking-wider uppercase">
              RAW EXTRACT PROVENANCE
            </span>
            <div className="p-3 bg-slate-50 dark:bg-slate-900/80 rounded border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 font-serif italic text-[13px] leading-relaxed">
              {activeChunk.rawExtract}
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-2 pt-1">
            <button
              id="btn-copy-bluebook"
              type="button"
              onClick={handleCopyBluebook}
              className="flex-1 py-1.5 px-2 rounded bg-slate-100 dark:bg-slate-700/80 border border-slate-200 dark:border-slate-600 text-[11px] font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors flex items-center justify-center gap-1 cursor-pointer"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                  <span className="text-emerald-700 dark:text-emerald-400">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
                  <span>Copy Bluebook</span>
                </>
              )}
            </button>

            <button
              id="btn-open-slip-op"
              type="button"
              onClick={() => onOpenSlipOp(activeChunk)}
              className="flex-1 py-1.5 px-2 rounded bg-slate-100 dark:bg-slate-700/80 border border-slate-200 dark:border-slate-600 text-[11px] font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors flex items-center justify-center gap-1 cursor-pointer"
            >
              <ExternalLink className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
              <span>Open Slip Op.</span>
            </button>
          </div>
        </div>

        {/* Secondary Chunks */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-[10px] font-bold text-slate-500 dark:text-slate-400 tracking-wider uppercase">
            <span>SECONDARY INDEXED CHUNKS</span>
            <Layers className="w-3 h-3" />
          </div>

          {secondaryChunks.map((chunk, idx) => (
            <div
              key={chunk.id}
              onClick={() => onSelectChunk(chunk)}
              className="border border-slate-200 dark:border-slate-800 rounded p-3 bg-white dark:bg-slate-800/60 hover:bg-slate-100/80 dark:hover:bg-slate-800 transition-all cursor-pointer space-y-1 group"
            >
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 rounded bg-slate-100 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 flex items-center justify-center text-[10px] font-bold text-slate-700 dark:text-slate-300">
                    {idx + 2}
                  </div>
                  <span className="font-serif font-semibold text-slate-900 dark:text-slate-100 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                    {chunk.docTitle}
                  </span>
                </div>
                <span className="font-mono text-slate-500 dark:text-slate-400 text-[10px]">
                  sim: {chunk.cosineSimilarity.toFixed(3)}
                </span>
              </div>
              <div className="text-[11px] font-sans text-slate-600 dark:text-slate-400 line-clamp-2 leading-snug pl-7">
                Doc {chunk.docId} · Chunk #{chunk.chunkNumber} · {chunk.rawExtract.replace(/^"/, '').replace(/"$/, '')}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Drawer Footer Status */}
      <div className="p-3.5 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 transition-colors duration-200">
        <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400">
          <span className="truncate max-w-[200px]" title={embeddingModel}>
            Embeddings: {embeddingModel}
          </span>
          <span className="flex items-center gap-1.5 font-medium shrink-0 text-slate-700 dark:text-slate-300">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Vector DB Synced
          </span>
        </div>
      </div>
    </aside>
  );
};
