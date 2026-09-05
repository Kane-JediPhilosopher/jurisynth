import React from 'react';
import {
  ShieldCheck,
  GitFork,
  SlidersHorizontal,
  Moon,
  Sun,
  Play,
  Share2,
} from 'lucide-react';
import { DossierMetadata } from '../types';

interface HeaderProps {
  metadata: DossierMetadata;
  isDark: boolean;
  onToggleTheme: () => void;
  onOpenAudit: () => void;
  onOpenKnowledgeGraph: () => void;
  onOpenTuners: () => void;
  onRunSynthesis: () => void;
  isRunningSynthesis: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  metadata,
  isDark,
  onToggleTheme,
  onOpenAudit,
  onOpenKnowledgeGraph,
  onOpenTuners,
  onRunSynthesis,
  isRunningSynthesis,
}) => {
  return (
    <header
      id="jurisynth-top-header"
      className="flex justify-between items-center w-full px-5 md:px-6 h-16 bg-slate-900 text-white shadow-md border-b border-slate-800 sticky top-0 z-40 transition-colors duration-200"
    >
      {/* Left: Brand monogram and Breadcrumbs */}
      <div className="flex items-center gap-4 md:gap-5 min-w-0">
        <div className="flex items-center gap-3 shrink-0">
          <span
            id="jurisynth-logo-monogram"
            className="w-8 h-8 rounded bg-indigo-500 text-white flex items-center justify-center font-bold text-base shadow-sm select-none"
          >
            J
          </span>
          <div className="flex flex-col">
            <h1 className="text-sm font-bold tracking-tight uppercase leading-tight text-white">
              Jurisynth
            </h1>
            <span className="text-[10px] text-slate-400 font-medium tracking-wide">
              Legal Research Intelligence
            </span>
          </div>
        </div>

        <div className="h-5 w-px bg-slate-700 shrink-0 hidden sm:block" />

        {/* Court and Matter breadcrumbs */}
        <div className="flex items-center gap-2.5 md:gap-3 text-xs overflow-x-auto no-scrollbar py-1">
          <button
            type="button"
            className="text-indigo-400 border-b-2 border-indigo-500 font-semibold text-[11px] md:text-xs tracking-wide uppercase whitespace-nowrap hover:text-indigo-300 transition-colors"
            title="Active Jurisdiction"
          >
            {metadata.court}
          </button>
          <span className="text-slate-500 text-xs">/</span>
          <span className="text-slate-300 text-[11px] md:text-xs font-medium whitespace-nowrap">
            {metadata.matterName}
          </span>
          <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 text-[11px] font-medium whitespace-nowrap">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-slate-300">
              Verified Evidentiary State
            </span>
          </div>
        </div>
      </div>

      {/* Right: Toolbelt & Action Controls */}
      <div className="flex items-center gap-2 md:gap-3 shrink-0">
        <div className="flex items-center gap-1">
          <button
            id="btn-verified-authority"
            type="button"
            onClick={onOpenAudit}
            className="w-8 h-8 flex items-center justify-center rounded text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            title="Grounding & Evidence Audit"
          >
            <ShieldCheck className="w-[18px] h-[18px] text-indigo-400" />
          </button>
          <button
            id="btn-knowledge-graph-toggle"
            type="button"
            onClick={onOpenKnowledgeGraph}
            className="w-8 h-8 flex items-center justify-center rounded text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            title="Precedent Knowledge Graph"
          >
            <GitFork className="w-[18px] h-[18px]" />
          </button>
          <button
            id="btn-synthesis-tuners"
            type="button"
            onClick={onOpenTuners}
            className="w-8 h-8 flex items-center justify-center rounded text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            title="Synthesis Tuners & Corpus Filters"
          >
            <SlidersHorizontal className="w-[18px] h-[18px]" />
          </button>

          {/* Dark / Light Mode Switch */}
          <button
            id="themeToggleBtn"
            type="button"
            onClick={onToggleTheme}
            aria-label="Toggle light and dark color mode"
            className="w-8 h-8 flex items-center justify-center rounded border border-slate-700 bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-all ml-0.5"
            title={isDark ? 'Switch to Crisp Slate Light Mode' : 'Switch to Slate Dark Mode'}
          >
            {isDark ? (
              <Sun className="w-4 h-4 text-amber-400" />
            ) : (
              <Moon className="w-4 h-4 text-indigo-300" />
            )}
          </button>
        </div>

        <div className="h-5 w-px bg-slate-700" />

        <button
          id="btn-export-audit"
          type="button"
          onClick={onOpenAudit}
          className="hidden sm:inline-flex px-3 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold tracking-wider uppercase transition-colors items-center gap-1.5 shadow-sm cursor-pointer"
        >
          <Share2 className="w-3.5 h-3.5 opacity-90" />
          <span>Export Dossier</span>
        </button>

        <button
          id="btn-run-synthesis-header"
          type="button"
          onClick={onRunSynthesis}
          disabled={isRunningSynthesis}
          className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white text-xs font-semibold tracking-wide transition-colors flex items-center gap-1.5 shadow-sm disabled:opacity-75 cursor-pointer"
        >
          <Play className={`w-3.5 h-3.5 text-indigo-400 ${isRunningSynthesis ? 'animate-spin' : ''}`} />
          <span>{isRunningSynthesis ? 'Synthesizing...' : 'Run Synthesis'}</span>
        </button>

        <div
          id="counsel-analyst-avatar"
          className="w-8 h-8 rounded-full bg-slate-700 border border-slate-600 flex items-center justify-center text-xs font-semibold text-slate-200 select-none shadow-xs"
          title="Counsel Analyst Avatar (CA - Delaware Bar)"
        >
          CA
        </div>
      </div>
    </header>
  );
};
