import React, { useState } from 'react';
import { X, Plus, Sparkles, FolderKanban, ArrowRight } from 'lucide-react';

interface NewSynthesisModalProps {
  onClose: () => void;
  onSelectMatter: (matterTitle: string, matterId: string) => void;
}

export const NewSynthesisModal: React.FC<NewSynthesisModalProps> = ({
  onClose,
  onSelectMatter,
}) => {
  const [customMatter, setCustomMatter] = useState('');

  const standardMatters = [
    {
      id: 'Matter 2024-DE-Caremark',
      title: 'In re SolarWinds Derivative',
      subtitle: 'Board oversight and cybersecurity compliance obligations under Caremark doctrine',
      active: true,
    },
    {
      id: 'Matter 2024-DE-Officer-Oversight',
      title: "In re McDonald's Corp. S'holder Deriv. Litig.",
      subtitle: 'Officer fiduciary duties, executive oversight thresholds, and human capital risk',
      active: false,
    },
    {
      id: 'Matter 2023-DE-MissionCritical',
      title: 'In re Boeing Co. Deriv. Litig.',
      subtitle: 'Board-level safety committees vs. ordinary business risk in product manufacturing',
      active: false,
    },
    {
      id: 'Matter 2024-DE-DemandFutility',
      title: 'United Food & Com. Workers Union v. Zuckerberg',
      subtitle: 'Universal three-part test for Rule 23.1 demand futility in Chancery derivative actions',
      active: false,
    },
  ];

  const handleCustomSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (customMatter.trim()) {
      onSelectMatter(customMatter.trim(), 'Matter 2024-DE-CUSTOM');
      onClose();
    }
  };

  return (
    <div
      id="new-synthesis-modal-overlay"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs"
      onClick={onClose}
    >
      <div
        id="new-synthesis-modal-container"
        className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl max-w-2xl w-full max-h-[85vh] flex flex-col shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/80">
          <div className="flex items-center gap-2.5">
            <FolderKanban className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
            <div>
              <h3 className="font-sans font-bold text-base text-slate-900 dark:text-slate-100">
                Initiate Legal Research Synthesis
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Select an active Delaware Chancery matter or initiate fresh statutory query
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

        <div className="p-6 overflow-y-auto space-y-5">
          {/* Custom Matter Input */}
          <form onSubmit={handleCustomSubmit} className="space-y-2">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              New Corporate Matter Query
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={customMatter}
                onChange={(e) => setCustomMatter(e.target.value)}
                placeholder="e.g. 'Tornetta v. Musk compensation clawback & entire fairness review'..."
                className="flex-1 h-10 px-3 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs font-sans text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
              <button
                type="submit"
                disabled={!customMatter.trim()}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg disabled:opacity-50 transition-colors flex items-center gap-1.5 cursor-pointer shadow-xs"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Initialize</span>
              </button>
            </div>
          </form>

          {/* Standard Indexed Matters List */}
          <div className="space-y-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Pre-Indexed Delaware Chancery Dockets
            </span>
            <div className="space-y-2">
              {standardMatters.map((item) => (
                <div
                  key={item.id}
                  onClick={() => {
                    onSelectMatter(item.title, item.id);
                    onClose();
                  }}
                  className="p-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer transition-all flex items-center justify-between group"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-serif font-bold text-sm text-slate-900 dark:text-slate-100 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                        {item.title}
                      </span>
                      {item.active && (
                        <span className="text-[10px] bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 px-1.5 py-0.5 rounded font-mono font-semibold">
                          Current Dossier
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-400 font-sans mt-0.5">
                      {item.subtitle}
                    </p>
                    <span className="text-[10px] text-slate-400 dark:text-slate-500 font-mono">
                      {item.id}
                    </span>
                  </div>
                  <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors" />
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="px-6 py-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-1.5 rounded border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 text-xs font-semibold hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};
