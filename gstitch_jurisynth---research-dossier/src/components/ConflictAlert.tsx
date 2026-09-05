import React from 'react';
import { AlertTriangle, ArrowUpRight } from 'lucide-react';
import { ConflictAlertItem } from '../types';

interface ConflictAlertProps {
  alert: ConflictAlertItem;
  onInspectChunk: (chunkId: string) => void;
}

export const ConflictAlert: React.FC<ConflictAlertProps> = ({
  alert,
  onInspectChunk,
}) => {
  return (
    <div
      id="conflict-alert-card"
      className="border border-amber-200 dark:border-amber-900/60 bg-amber-50/70 dark:bg-amber-950/20 rounded-xl p-5 shadow-xs transition-colors"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
          <h4 className="font-serif font-semibold text-base text-slate-900 dark:text-slate-100 leading-snug">
            {alert.title}
          </h4>
        </div>
        <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-amber-100 dark:bg-amber-900/40 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800/40 shrink-0">
          {alert.tag}
        </span>
      </div>

      <p className="pl-8 pt-2 text-sm font-sans text-slate-600 dark:text-slate-400 leading-relaxed">
        {alert.description}
      </p>

      {alert.chunkId && (
        <div className="pl-8 pt-3 flex items-center gap-3">
          <button
            type="button"
            onClick={() => onInspectChunk(alert.chunkId!)}
            className="text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 hover:underline font-semibold inline-flex items-center gap-1 cursor-pointer font-sans"
          >
            <span>Inspect cited precedent: {alert.recentCase}</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}
    </div>
  );
};
