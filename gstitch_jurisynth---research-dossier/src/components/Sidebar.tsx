import React from 'react';
import {
  FolderOpen,
  FileCheck,
  Network,
  ShieldAlert,
  CheckCircle2,
  Settings,
  Plus,
} from 'lucide-react';

export type SidebarTab =
  | 'dossier'
  | 'evidence'
  | 'graph'
  | 'audit';

interface SidebarProps {
  activeTab: SidebarTab;
  onSelectTab: (tab: SidebarTab) => void;
  onNewSynthesis: () => void;
  onOpenSettings: () => void;
  systemHealth: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onSelectTab,
  onNewSynthesis,
  onOpenSettings,
  systemHealth,
}) => {
  return (
    <aside
      id="jurisynth-left-sidebar"
      className="flex flex-col justify-between w-64 min-w-[16rem] border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4 shrink-0 transition-colors duration-200"
    >
      <div>
        {/* Monogram branding */}
        <div className="flex items-center gap-2.5 px-1 mb-4">
          <div
            className="w-7 h-7 rounded bg-indigo-600 flex items-center justify-center text-white font-bold text-xs shadow-xs select-none"
            title="Jurisynth Monogram Scale Emblem"
          >
            JS
          </div>
          <div>
            <div className="text-xs font-bold font-sans text-slate-900 dark:text-slate-100 leading-tight tracking-tight uppercase">
              Jurisynth
            </div>
            <div className="text-[10px] text-slate-500 dark:text-slate-400 tracking-wider uppercase font-medium">
              Enterprise Statutory Core
            </div>
          </div>
        </div>

        {/* New Legal Synthesis CTA */}
        <button
          id="btn-new-synthesis"
          type="button"
          onClick={onNewSynthesis}
          className="w-full mb-4 py-2 px-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 text-xs font-semibold rounded shadow-xs hover:bg-slate-50 dark:hover:bg-slate-700/60 transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
        >
          <Plus className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
          <span>New Legal Synthesis</span>
        </button>

        {/* Nav Links */}
        <div className="px-1 mb-2">
          <h2 className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest">
            Research Dossier Structure
          </h2>
        </div>

        <nav className="space-y-1">
          <button
            type="button"
            onClick={() => onSelectTab('dossier')}
            className={`w-full flex items-center gap-2.5 px-3 py-2 text-xs rounded transition-colors text-left ${
              activeTab === 'dossier'
                ? 'text-indigo-700 dark:text-indigo-400 bg-slate-50 dark:bg-slate-800/80 border-l-4 border-indigo-600 font-semibold rounded-r'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-slate-200'
            }`}
          >
            <FolderOpen
              className={`w-4 h-4 ${
                activeTab === 'dossier'
                  ? 'text-indigo-600 dark:text-indigo-400'
                  : 'text-slate-400 dark:text-slate-500'
              }`}
            />
            <span>Dossier Workspace</span>
          </button>

          <button
            type="button"
            onClick={() => onSelectTab('evidence')}
            className={`w-full flex items-center gap-2.5 px-3 py-2 text-xs rounded transition-colors text-left ${
              activeTab === 'evidence'
                ? 'text-indigo-700 dark:text-indigo-400 bg-slate-50 dark:bg-slate-800/80 border-l-4 border-indigo-600 font-semibold rounded-r'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-slate-200'
            }`}
          >
            <FileCheck
              className={`w-4 h-4 ${
                activeTab === 'evidence'
                  ? 'text-indigo-600 dark:text-indigo-400'
                  : 'text-slate-400 dark:text-slate-500'
              }`}
            />
            <span>Evidence &amp; Provenance</span>
          </button>

          <button
            type="button"
            onClick={() => onSelectTab('graph')}
            className={`w-full flex items-center gap-2.5 px-3 py-2 text-xs rounded transition-colors text-left ${
              activeTab === 'graph'
                ? 'text-indigo-700 dark:text-indigo-400 bg-slate-50 dark:bg-slate-800/80 border-l-4 border-indigo-600 font-semibold rounded-r'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-slate-200'
            }`}
          >
            <Network
              className={`w-4 h-4 ${
                activeTab === 'graph'
                  ? 'text-indigo-600 dark:text-indigo-400'
                  : 'text-slate-400 dark:text-slate-500'
              }`}
            />
            <span>Knowledge Graph</span>
          </button>

          <button
            type="button"
            onClick={() => onSelectTab('audit')}
            className={`w-full flex items-center gap-2.5 px-3 py-2 text-xs rounded transition-colors text-left ${
              activeTab === 'audit'
                ? 'text-indigo-700 dark:text-indigo-400 bg-slate-50 dark:bg-slate-800/80 border-l-4 border-indigo-600 font-semibold rounded-r'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-slate-200'
            }`}
          >
            <ShieldAlert
              className={`w-4 h-4 ${
                activeTab === 'audit'
                  ? 'text-indigo-600 dark:text-indigo-400'
                  : 'text-slate-400 dark:text-slate-500'
              }`}
            />
            <span>Model Audit</span>
          </button>
        </nav>
      </div>

      {/* Sidebar Footer */}
      <div className="pt-3 border-t border-slate-200 dark:border-slate-800 space-y-2">
        <div className="bg-indigo-50 dark:bg-indigo-950/40 p-3 rounded-lg border border-indigo-100 dark:border-indigo-900/50">
          <div className="text-[10px] font-bold text-indigo-800 dark:text-indigo-300 uppercase tracking-wider mb-1">
            Dossier Status
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-medium text-slate-700 dark:text-slate-300">
              Fully Synthesized
            </span>
          </div>
        </div>

        <button
          id="btn-sidebar-settings"
          type="button"
          onClick={onOpenSettings}
          className="w-full flex items-center gap-2.5 px-3 py-2 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-slate-200 rounded text-xs transition-colors text-left cursor-pointer"
        >
          <Settings className="w-4 h-4 text-slate-400 dark:text-slate-500" />
          <span>Settings</span>
        </button>
      </div>
    </aside>
  );
};
