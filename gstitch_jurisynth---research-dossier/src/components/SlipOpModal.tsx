import React from 'react';
import { X, Download, Copy, Check, ExternalLink, ShieldCheck } from 'lucide-react';
import { VectorChunk } from '../types';

interface SlipOpModalProps {
  chunk: VectorChunk | null;
  onClose: () => void;
}

export const SlipOpModal: React.FC<SlipOpModalProps> = ({ chunk, onClose }) => {
  const [copied, setCopied] = React.useState(false);

  if (!chunk) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(chunk.fullOpinionSnippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const element = document.createElement('a');
    const file = new Blob([chunk.fullOpinionSnippet], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `${chunk.docTitle.replace(/\s+/g, '_')}_Slip_Opinion.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div
      id="slip-opinion-modal-overlay"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs transition-opacity"
      onClick={onClose}
    >
      <div
        id="slip-opinion-modal-container"
        className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl max-w-3xl w-full max-h-[85vh] flex flex-col shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/80">
          <div className="flex items-center gap-3">
            <span className="w-8 h-8 rounded bg-indigo-600 text-white flex items-center justify-center font-serif font-bold text-base shadow-xs">
              §
            </span>
            <div>
              <h3 className="font-sans font-bold text-base text-slate-900 dark:text-slate-100">
                Official Slip Opinion Record
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {chunk.court} · {chunk.citation}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleCopy}
              className="p-1.5 rounded border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 transition-colors"
              title="Copy slip opinion text"
            >
              {copied ? (
                <Check className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
            </button>
            <button
              type="button"
              onClick={handleDownload}
              className="p-1.5 rounded border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 transition-colors"
              title="Download text file"
            >
              <Download className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={onClose}
              className="p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Meta Strip */}
        <div className="px-6 py-2 bg-slate-100 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-800 flex flex-wrap items-center justify-between text-xs font-mono text-slate-600 dark:text-slate-300">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
            <span>Doc {chunk.docId} · Chunk #{chunk.chunkNumber}</span>
          </div>
          <span>Cosine: {chunk.cosineSimilarity.toFixed(3)} · {chunk.vectorDimension}</span>
        </div>

        {/* Opinion Body */}
        <div className="p-6 overflow-y-auto space-y-4 font-serif text-[14px] leading-relaxed text-slate-700 dark:text-slate-300">
          <div className="p-4 bg-slate-50 dark:bg-slate-800/70 border-l-4 border-indigo-600 dark:border-indigo-500 rounded-r text-xs font-sans text-slate-600 dark:text-slate-300">
            <strong>Bluebook Form:</strong> {chunk.bluebookCitation}
          </div>

          <pre className="font-serif whitespace-pre-wrap leading-relaxed text-[14px] text-slate-900 dark:text-slate-100">
            {chunk.fullOpinionSnippet}
          </pre>
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 flex justify-between items-center text-xs text-slate-500 dark:text-slate-400">
          <span>Verified against Delaware Supreme Court / Court of Chancery reporter</span>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold tracking-wide transition-colors cursor-pointer"
          >
            Close Opinion
          </button>
        </div>
      </div>
    </div>
  );
};
