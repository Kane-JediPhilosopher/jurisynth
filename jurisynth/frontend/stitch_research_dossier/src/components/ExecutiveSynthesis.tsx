import React from 'react';
import { BookOpenText } from 'lucide-react';

interface ExecutiveSynthesisProps {
  onSelectCitation: (chunkId: string) => void;
  overview?: string;
}

export const ExecutiveSynthesis: React.FC<ExecutiveSynthesisProps> = ({
  onSelectCitation,
  overview,
}) => {
  return (
    <section
      id="executive-synthesis-card"
      className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs transition-colors duration-200"
    >
      <div className="flex flex-wrap items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3 mb-4 gap-2">
        <div className="flex items-center gap-2">
          <BookOpenText className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
          <h2 className="text-sm font-bold text-slate-900 dark:text-slate-100 tracking-tight uppercase">
            AI Executive Summary
          </h2>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300">
            High Traceability
          </span>
          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-200 dark:border-emerald-800/40 text-emerald-700 dark:text-emerald-400">
            4 Verified Chunks
          </span>
          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-amber-50 dark:bg-amber-950/50 border border-amber-200 dark:border-amber-800/40 text-amber-800 dark:text-amber-300 flex items-center gap-1">
            <span>Δ</span> 1 Ambiguity flagged
          </span>
        </div>
      </div>

      {overview ? (
        <p className="text-slate-600 dark:text-slate-400 text-sm md:text-[15px] leading-relaxed">{overview}</p>
      ) : <div className="space-y-3 text-slate-600 dark:text-slate-400 text-sm md:text-[15px] leading-relaxed">
        <p>
          Under the settled doctrine of{' '}
          <button
            type="button"
            onClick={() => onSelectCitation('chunk-caremark-01')}
            className="font-semibold text-indigo-600 dark:text-indigo-400 underline decoration-indigo-200 dark:decoration-indigo-800 hover:text-indigo-800 dark:hover:text-indigo-300 transition-colors cursor-pointer text-left inline"
            title="Inspect Caremark citation"
          >
            In re Caremark Int'l Inc. Deriv. Litig.
          </button>
          , 698 A.2d 959 (Del. Ch. 1996), director liability for systemic failure
          of oversight represents the most difficult theory of recovery in
          corporation law. Grounding in{' '}
          <button
            type="button"
            onClick={() => onSelectCitation('chunk-stone-14')}
            className="font-semibold text-indigo-600 dark:text-indigo-400 underline decoration-indigo-200 dark:decoration-indigo-800 hover:text-indigo-800 dark:hover:text-indigo-300 transition-colors cursor-pointer text-left inline"
            title="Inspect Stone v. Ritter citation"
          >
            Stone v. Ritter
          </button>
          , 911 A.2d 362 (Del. 2006) confirms that oversight liability strictly
          derives from bad-faith breaches of the duty of loyalty, disabling
          exculpatory protection under{' '}
          <span
            className="font-mono text-xs bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 select-all cursor-help font-semibold"
            title="Delaware General Corporation Law § 102(b)(7) (Exculpation clause)"
          >
            DGCL § 102(b)(7)
          </span>
          .
        </p>

        <p className="text-xs md:text-sm text-slate-500 dark:text-slate-400 border-t border-slate-100 dark:border-slate-800 pt-3">
          The Court requires sustained or systematic failure to attempt any
          reporting system, or conscious failure to monitor known compliance
          red flags. Recent evolution emphasizes rigorous scrutiny over
          "mission-critical" regulatory regimes.
        </p>
      </div>}
    </section>
  );
};
