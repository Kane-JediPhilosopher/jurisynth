import React, { useState } from 'react';
import { Sparkles, Filter, X, Send } from 'lucide-react';
import { sampleQueries } from '../data/dossierData';

interface BottomQueryBarProps {
  onSynthesize: (query: string) => void;
  isLoading: boolean;
}

export const BottomQueryBar: React.FC<BottomQueryBarProps> = ({
  onSynthesize,
  isLoading,
}) => {
  const [query, setQuery] = useState<string>('');
  const [activeFilters, setActiveFilters] = useState<string[]>([
    'Precedents only',
    'DE Court 2018–2024',
    'Exclude Settlement Approvals',
  ]);

  const toggleFilter = (filter: string) => {
    if (activeFilters.includes(filter)) {
      setActiveFilters(activeFilters.filter((f) => f !== filter));
    } else {
      setActiveFilters([...activeFilters, filter]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSynthesize(query.trim());
    }
  };

  const handleSelectSample = (sample: string) => {
    setQuery(sample);
  };

  return (
    <div
      id="bottom-query-synthesis-bar"
      className="sticky bottom-0 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border-t border-slate-200 dark:border-slate-800 p-3 md:p-4 z-20 transition-colors duration-200"
    >
      <div className="max-w-4xl mx-auto w-full space-y-2">
        {/* Applied Filters bar */}
        <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar text-[11px] pb-0.5">
          <div className="flex items-center gap-1 text-slate-700 dark:text-slate-300 font-semibold shrink-0">
            <Filter className="w-3 h-3 text-indigo-600 dark:text-indigo-400" />
            <span>Applied Synthesis Filters:</span>
          </div>

          {['Precedents only', 'DE Court 2018–2024', 'Exclude Settlement Approvals', 'DGCL Strict Scope'].map(
            (filter) => {
              const isActive = activeFilters.includes(filter);
              return (
                <button
                  key={filter}
                  type="button"
                  onClick={() => toggleFilter(filter)}
                  className={`px-2 py-0.5 rounded border text-[11px] font-medium transition-colors shrink-0 flex items-center gap-1 cursor-pointer ${
                    isActive
                      ? 'bg-indigo-50 dark:bg-indigo-950/60 border-indigo-200 dark:border-indigo-800 text-indigo-700 dark:text-indigo-300'
                      : 'bg-transparent border-slate-200 dark:border-slate-700 text-slate-400 line-through opacity-60'
                  }`}
                >
                  <span>{filter}</span>
                  {isActive && <X className="w-2.5 h-2.5 opacity-60" />}
                </button>
              );
            }
          )}
        </div>

        {/* Input box */}
        <form onSubmit={handleSubmit} className="relative flex items-center">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isLoading}
            placeholder="Query synthesis graph (e.g. 'Synthesize pleading threshold for officer oversight post-McDonalds with DGCL 102(b)(7) immunity')..."
            className="w-full h-11 pl-4 pr-32 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 placeholder-slate-400 text-xs md:text-sm font-sans focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 shadow-xs transition-colors"
          />

          <div className="absolute right-1.5 flex items-center">
            <button
              id="btn-synthesize-action"
              type="submit"
              disabled={isLoading || !query.trim()}
              className="px-3.5 py-1.5 rounded-md bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-colors shadow-xs flex items-center gap-1.5 disabled:opacity-50 cursor-pointer"
            >
              {isLoading ? (
                <>
                  <Sparkles className="w-3.5 h-3.5 animate-spin" />
                  <span>Synthesizing...</span>
                </>
              ) : (
                <>
                  <Send className="w-3 h-3" />
                  <span>Synthesize</span>
                </>
              )}
            </button>
          </div>
        </form>

        {/* Quick query recommendation chips */}
        <div className="flex items-center gap-2 overflow-x-auto no-scrollbar pt-1 text-[11px]">
          <span className="text-slate-500 dark:text-slate-400 shrink-0">Quick suggestions:</span>
          {sampleQueries.slice(0, 2).map((sample, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSelectSample(sample)}
              className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 hover:underline truncate max-w-xs cursor-pointer text-left shrink-0"
            >
              "{sample.slice(0, 55)}..."
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
