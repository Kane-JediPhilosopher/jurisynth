import React from 'react';
import { BookOpenText } from 'lucide-react';

interface ExecutiveSynthesisProps {
  overview?: string;
}

export const ExecutiveSynthesis: React.FC<ExecutiveSynthesisProps> = ({ overview }) => {
  return (
    <section
      id="executive-synthesis-card"
      className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs transition-colors duration-200"
    >
      <div className="flex flex-wrap items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3 mb-4 gap-2">
        <div className="flex items-center gap-2">
          <BookOpenText className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
          <h2 className="text-sm font-bold text-slate-900 dark:text-slate-100 tracking-tight uppercase">
            Research overview
          </h2>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300">Evidence-linked output</span>
        </div>
      </div>

      {overview ? (
        <p className="text-slate-600 dark:text-slate-400 text-sm md:text-[15px] leading-relaxed">{overview}</p>
      ) : <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">Submit a question to generate a source-grounded report. Open a claim to inspect its retrieved source excerpts.</p>}
    </section>
  );
};
