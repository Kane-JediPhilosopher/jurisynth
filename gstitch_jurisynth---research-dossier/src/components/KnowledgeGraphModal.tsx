import React, { useState } from 'react';
import { X, Network, Info, ArrowRight } from 'lucide-react';
import { VectorChunk } from '../types';

interface KnowledgeGraphModalProps {
  onClose: () => void;
  onSelectChunkById: (chunkId: string) => void;
}

interface Node {
  id: string;
  chunkId: string;
  name: string;
  court: string;
  year: number;
  doctrine: string;
  color: string;
  x: number;
  y: number;
}

export const KnowledgeGraphModal: React.FC<KnowledgeGraphModalProps> = ({
  onClose,
  onSelectChunkById,
}) => {
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  const nodes: Node[] = [
    {
      id: 'caremark',
      chunkId: 'chunk-caremark-01',
      name: "In re Caremark Int'l",
      court: 'Del. Ch.',
      year: 1996,
      doctrine: 'Root oversight doctrine; high hurdle requiring sustained/systematic failure.',
      color: '#7e562e',
      x: 100,
      y: 160,
    },
    {
      id: 'stone',
      chunkId: 'chunk-stone-14',
      name: 'Stone v. Ritter',
      court: 'Del. Supreme Court',
      year: 2006,
      doctrine: 'Anchors oversight strictly in Duty of Loyalty / bad faith; disables DGCL 102(b)(7) exculpation.',
      color: '#93000a',
      x: 270,
      y: 110,
    },
    {
      id: 'marchand',
      chunkId: 'chunk-marchand-08',
      name: 'Marchand v. Barnhill',
      court: 'Del. Supreme Court',
      year: 2019,
      doctrine: 'Establishes mission-critical compliance imperative (food safety in ice-cream manufacturing).',
      color: '#2b1a12',
      x: 430,
      y: 80,
    },
    {
      id: 'boeing',
      chunkId: 'chunk-boeing-32',
      name: 'In re Boeing Co.',
      court: 'Del. Court of Chancery',
      year: 2021,
      doctrine: 'Extends mission-critical doctrine to aircraft safety; board-level monitoring required.',
      color: '#2b1a12',
      x: 430,
      y: 220,
    },
    {
      id: 'mcdonalds',
      chunkId: 'chunk-mcdonalds-19',
      name: "In re McDonald's Corp.",
      court: 'Del. Court of Chancery',
      year: 2023,
      doctrine: 'Landmark holding that corporate officers owe equivalent oversight duties in their domains.',
      color: '#633f19',
      x: 580,
      y: 160,
    },
  ];

  const edges = [
    { from: 'caremark', to: 'stone', label: 'Codified & Rooted in Loyalty' },
    { from: 'stone', to: 'marchand', label: 'Prong-1 Failure Established' },
    { from: 'stone', to: 'boeing', label: 'Mission-Critical Scope' },
    { from: 'stone', to: 'mcdonalds', label: 'Extended to Officers' },
    { from: 'marchand', to: 'boeing', label: 'Precedential Reliance' },
  ];

  return (
    <div
      id="knowledge-graph-modal-overlay"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs"
      onClick={onClose}
    >
      <div
        id="knowledge-graph-modal-container"
        className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/80">
          <div className="flex items-center gap-2.5">
            <Network className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
            <div>
              <h3 className="font-sans font-bold text-base text-slate-900 dark:text-slate-100">
                Precedential Jurisprudence Graph
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Delaware Caremark Doctrine Lineage &amp; Citation Relationships
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

        {/* Visual Graph Canvas Container */}
        <div className="p-6 overflow-y-auto space-y-4">
          <div className="relative w-full h-[320px] bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg p-4 overflow-hidden select-none">
            <svg className="w-full h-full" viewBox="0 0 700 320">
              {/* Render edges */}
              {edges.map((edge, i) => {
                const source = nodes.find((n) => n.id === edge.from)!;
                const target = nodes.find((n) => n.id === edge.to)!;
                return (
                  <g key={i}>
                    <line
                      x1={source.x}
                      y1={source.y}
                      x2={target.x}
                      y2={target.y}
                      stroke="#94a3b8"
                      strokeWidth="2"
                      strokeDasharray="4 2"
                      className="opacity-50 dark:opacity-40"
                    />
                  </g>
                );
              })}

              {/* Render nodes */}
              {nodes.map((node) => {
                const isSelected = selectedNode?.id === node.id;
                return (
                  <g
                    key={node.id}
                    transform={`translate(${node.x}, ${node.y})`}
                    onClick={() => setSelectedNode(node)}
                    className="cursor-pointer group"
                  >
                    <circle
                      r={isSelected ? '24' : '20'}
                      fill={isSelected ? '#4f46e5' : '#0f172a'}
                      stroke={isSelected ? '#818cf8' : '#cbd5e1'}
                      strokeWidth="2"
                      className="transition-all duration-150 group-hover:scale-110"
                    />
                    <text
                      textAnchor="middle"
                      dy="4"
                      fill="#ffffff"
                      fontSize="10"
                      fontFamily="sans-serif"
                      fontWeight="bold"
                    >
                      {node.year}
                    </text>
                    <text
                      textAnchor="middle"
                      dy="36"
                      fill="#0f172a"
                      className="dark:fill-slate-200 text-[11px] font-sans font-semibold"
                    >
                      {node.name}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>

          {/* Node detail display */}
          {selectedNode ? (
            <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/70 border border-slate-200 dark:border-slate-700 space-y-2 animate-in fade-in duration-150">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-serif font-bold text-sm text-slate-900 dark:text-slate-100">
                    {selectedNode.name} ({selectedNode.year})
                  </h4>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    {selectedNode.court}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    onSelectChunkById(selectedNode.chunkId);
                    onClose();
                  }}
                  className="px-3 py-1 text-xs rounded bg-indigo-600 hover:bg-indigo-500 text-white font-semibold transition-colors flex items-center gap-1 cursor-pointer"
                >
                  <span>Inspect in Dossier</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
              <p className="text-xs font-sans text-slate-600 dark:text-slate-300 leading-relaxed">
                {selectedNode.doctrine}
              </p>
            </div>
          ) : (
            <div className="p-3 text-xs text-slate-500 dark:text-slate-400 flex items-center gap-2 bg-slate-50 dark:bg-slate-800/50 rounded border border-slate-200 dark:border-slate-700">
              <Info className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              <span>Click any case precedent node to view its doctrinal impact and jump directly to its vector extract.</span>
            </div>
          )}
        </div>

        <div className="px-6 py-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold tracking-wide transition-colors cursor-pointer"
          >
            Close Graph
          </button>
        </div>
      </div>
    </div>
  );
};
