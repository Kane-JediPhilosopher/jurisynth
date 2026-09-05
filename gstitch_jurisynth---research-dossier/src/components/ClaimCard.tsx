import React, { useState } from 'react';
import { ChevronDown, ChevronUp, FileSearch } from 'lucide-react';
import { SynthesizedClaim } from '../types';

interface ClaimCardProps {
  claim: SynthesizedClaim;
  isActiveChunk: boolean;
  onInspectChunk: (chunkId: string) => void;
  defaultExpanded?: boolean;
}

export const ClaimCard: React.FC<ClaimCardProps> = ({
  claim,
  isActiveChunk,
  onInspectChunk,
  defaultExpanded = false,
}) => {
  const [isExpanded, setIsExpanded] = useState<boolean>(defaultExpanded);

  return (
    <div
      id={`claim-card-${claim.id}`}
      className={`border rounded-xl bg-white dark:bg-slate-900 p-5 shadow-xs transition-all duration-200 ${
        isActiveChunk
          ? 'border-indigo-600 dark:border-indigo-500 ring-1 ring-indigo-600/20 dark:ring-indigo-500/20'
          : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700'
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div
          className="flex items-start gap-3 cursor-pointer select-none flex-1"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <span
            className={`w-6 h-6 rounded-md flex items-center justify-center text-xs font-bold mt-0.5 shrink-0 ${
              isActiveChunk
                ? 'bg-indigo-600 text-white shadow-xs'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700'
            }`}
          >
            {claim.id}
          </span>
          <h4 className="font-serif font-semibold text-base text-slate-900 dark:text-slate-100 leading-snug">
            {claim.title}
          </h4>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <span
            className={`text-xs px-2.5 py-0.5 rounded font-mono border ${
              claim.confidence >= 90
                ? 'text-indigo-700 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/60 border-indigo-200 dark:border-indigo-800/40 font-semibold'
                : 'text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 border-slate-200 dark:border-slate-700'
            }`}
          >
            Confidence: {claim.confidence.toFixed(1)}%
          </span>

          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors p-0.5 cursor-pointer"
            aria-label={isExpanded ? 'Collapse claim details' : 'Expand claim details'}
          >
            {isExpanded ? (
              <ChevronUp className="w-[18px] h-[18px]" />
            ) : (
              <ChevronDown className="w-[18px] h-[18px]" />
            )}
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="pl-9 pt-3 space-y-3 font-serif">
          <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed font-sans">
            {claim.summary}
          </p>

          {claim.quote && (
            <blockquote className="bg-slate-50 dark:bg-slate-800/70 border-l-4 border-indigo-600 dark:border-indigo-500 p-4 rounded-r text-slate-800 dark:text-slate-200 italic text-[14px] leading-relaxed">
              {claim.quote}
            </blockquote>
          )}

          <div className="flex flex-wrap items-center justify-between pt-2 gap-2">
            <div className="flex items-center gap-2 text-xs font-sans flex-wrap">
              <span className="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 font-mono text-xs">
                {claim.statute}
              </span>
              <span className="text-slate-500 dark:text-slate-400">
                | {claim.court} {claim.year}
              </span>
            </div>

            <button
              type="button"
              onClick={() => onInspectChunk(claim.chunkId)}
              className="px-3 py-1.5 text-xs rounded bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 font-semibold flex items-center gap-1.5 transition-colors font-sans cursor-pointer shadow-2xs"
            >
              <FileSearch className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
              <span>Inspect Vector Chunk</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
