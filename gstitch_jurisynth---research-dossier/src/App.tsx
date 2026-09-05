import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Sidebar, SidebarTab } from './components/Sidebar';
import { ExecutiveSynthesis } from './components/ExecutiveSynthesis';
import { ClaimCard } from './components/ClaimCard';
import { ConflictAlert } from './components/ConflictAlert';
import { ProvenanceDrawer } from './components/ProvenanceDrawer';
import { BottomQueryBar } from './components/BottomQueryBar';
import { SlipOpModal } from './components/SlipOpModal';
import { ExportAuditModal } from './components/ExportAuditModal';
import { KnowledgeGraphModal } from './components/KnowledgeGraphModal';
import { ModelAuditModal } from './components/ModelAuditModal';
import { NewSynthesisModal } from './components/NewSynthesisModal';
import { SettingsModal } from './components/SettingsModal';
import {
  initialDossierMeta,
  indexedChunks,
  initialClaims,
  conflictAlert,
} from './data/dossierData';
import { VectorChunk, SynthesizedClaim, DossierMetadata } from './types';
import { Info, CheckCircle2 } from 'lucide-react';

export default function App() {
  // Theme state
  const [isDark, setIsDark] = useState<boolean>(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('jurisynth_theme');
      if (stored) return stored === 'dark';
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    return false;
  });

  // Metadata & Content state
  const [metadata, setMetadata] = useState<DossierMetadata>(initialDossierMeta);
  const [allChunks] = useState<VectorChunk[]>(indexedChunks);
  const [activeChunk, setActiveChunk] = useState<VectorChunk>(indexedChunks[0]);
  const [claims, setClaims] = useState<SynthesizedClaim[]>(initialClaims);
  const [activeTab, setActiveTab] = useState<SidebarTab>('dossier');

  // Interactive Modals
  const [slipOpChunk, setSlipOpChunk] = useState<VectorChunk | null>(null);
  const [showExportAudit, setShowExportAudit] = useState<boolean>(false);
  const [showKnowledgeGraph, setShowKnowledgeGraph] = useState<boolean>(false);
  const [showModelAudit, setShowModelAudit] = useState<boolean>(false);
  const [showNewSynthesis, setShowNewSynthesis] = useState<boolean>(false);
  const [showSettings, setShowSettings] = useState<boolean>(false);

  // Status & notifications
  const [isRunningSynthesis, setIsRunningSynthesis] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Apply dark mode class to document
  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      root.classList.add('dark');
      localStorage.setItem('jurisynth_theme', 'dark');
    } else {
      root.classList.remove('dark');
      localStorage.setItem('jurisynth_theme', 'light');
    }
  }, [isDark]);

  const toggleTheme = () => {
    setIsDark((prev) => !prev);
  };

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(null);
    }, 3200);
  };

  // Inspect or select a chunk by its unique ID
  const handleSelectChunkById = (chunkId: string) => {
    const found = allChunks.find((c) => c.id === chunkId);
    if (found) {
      setActiveChunk(found);
      showToast(`Selected authority: ${found.docTitle}`);
    }
  };

  // Trigger interactive synthesis query
  const handleSynthesizeQuery = (query: string) => {
    setIsRunningSynthesis(true);
    showToast(`Synthesizing against Delaware Chancery corpus: "${query.slice(0, 40)}..."`);

    setTimeout(() => {
      setIsRunningSynthesis(false);

      // If query mentions officer or McDonald's, highlight the McDonald's chunk
      if (
        query.toLowerCase().includes('officer') ||
        query.toLowerCase().includes('mcdonald') ||
        query.toLowerCase().includes('employee')
      ) {
        const mcdChunk = allChunks.find((c) => c.id === 'chunk-mcdonalds-19');
        if (mcdChunk) setActiveChunk(mcdChunk);
      } else if (
        query.toLowerCase().includes('safety') ||
        query.toLowerCase().includes('boeing') ||
        query.toLowerCase().includes('mission')
      ) {
        const boeingChunk = allChunks.find((c) => c.id === 'chunk-boeing-32');
        if (boeingChunk) setActiveChunk(boeingChunk);
      }

      showToast('Research synthesis completed with 100% evidentiary grounding.');
    }, 1200);
  };

  const handleRunFullSynthesis = () => {
    setIsRunningSynthesis(true);
    showToast('Re-indexing Delaware statutory claims and vector grounding...');
    setTimeout(() => {
      setIsRunningSynthesis(false);
      showToast('Synthesis refreshed: 4 chunks validated against Lexis/Westlaw.');
    }, 1100);
  };

  const handleSelectMatter = (matterTitle: string, matterId: string) => {
    setMetadata((prev) => ({
      ...prev,
      matterName: matterTitle,
      matterId: matterId,
    }));
    showToast(`Loaded dossier: ${matterTitle}`);
  };

  // Filter secondary chunks
  const secondaryChunks = allChunks.filter((c) => c.id !== activeChunk.id);

  return (
    <div className="bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans antialiased overflow-x-hidden min-h-screen transition-colors duration-200 selection:bg-indigo-600 selection:text-white flex flex-col">
      {/* Top Application Header */}
      <Header
        metadata={metadata}
        isDark={isDark}
        onToggleTheme={toggleTheme}
        onOpenAudit={() => setShowExportAudit(true)}
        onOpenKnowledgeGraph={() => setShowKnowledgeGraph(true)}
        onOpenTuners={() => setShowSettings(true)}
        onRunSynthesis={handleRunFullSynthesis}
        isRunningSynthesis={isRunningSynthesis}
      />

      {/* Main 3-Column Layout */}
      <div className="flex w-full flex-1 min-h-[calc(100vh-4rem)]">
        {/* Left Sidebar */}
        <Sidebar
          activeTab={activeTab}
          onSelectTab={(tab) => {
            setActiveTab(tab);
            if (tab === 'graph') setShowKnowledgeGraph(true);
            if (tab === 'audit') setShowModelAudit(true);
            if (tab === 'evidence') {
              showToast('Evidence & Provenance inspection drawer is open on the right.');
            }
          }}
          onNewSynthesis={() => setShowNewSynthesis(true)}
          onOpenSettings={() => setShowSettings(true)}
          systemHealth={metadata.systemHealth}
        />

        {/* Central Dossier Workspace */}
        <main
          id="jurisynth-central-workspace"
          className="flex-1 min-w-0 bg-white dark:bg-slate-900 flex flex-col justify-between transition-colors duration-200"
        >
          <div className="p-6 md:p-8 space-y-6 max-w-4xl mx-auto w-full">
            {/* Advisory Banner */}
            <div
              id="corpus-advisory-banner"
              className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 py-2.5 px-4 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 rounded-lg"
            >
              <div className="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-400">
                <Info className="w-4 h-4 text-indigo-600 dark:text-indigo-400 shrink-0" />
                <span>
                  Informational legal research synthesis • Verified against Lexis/Westlaw Delaware Chancery corpus
                </span>
              </div>
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-500 dark:text-slate-400 shrink-0 font-semibold">
                CORPUS VER: {metadata.corpusVersion}
              </span>
            </div>

            {/* Dossier Heading Area */}
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-xs mb-2">
                <span>Delaware Chancery</span>
                <span>/</span>
                <span>Fiduciary Oversight</span>
                <span>/</span>
                <span className="font-semibold text-slate-700 dark:text-slate-300">Case Ref: {metadata.matterId}</span>
              </div>

              <h1 className="font-serif text-2xl md:text-3xl font-bold text-slate-900 dark:text-slate-100 tracking-tight leading-tight">
                Case Study: Director Fiduciary Obligations under Caremark standards
              </h1>

              <div className="flex flex-wrap items-center gap-2 pt-1 pb-2">
                <span className="px-2 py-0.5 bg-red-100 text-red-700 dark:bg-red-950/60 dark:text-red-300 rounded text-[10px] font-bold uppercase tracking-wider">
                  HIGH RISK PRECEDENT
                </span>
                <span className="px-2 py-0.5 bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 rounded text-[10px] font-bold uppercase tracking-wider">
                  DELAWARE CHANCERY
                </span>
                <span className="ml-auto inline-flex items-center gap-1.5 text-[11px] font-medium text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/50 px-2.5 py-0.5 rounded-full">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Grounding 100% Verified</span>
                </span>
              </div>

              <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
                Synthesis of board-level oversight duties, systemic failure criteria, and mission-critical enterprise risk thresholds under settled and emerging Delaware jurisprudence.
              </p>
            </div>

            {/* Executive Synthesis Section */}
            <ExecutiveSynthesis onSelectCitation={handleSelectChunkById} />

            {/* Synthesized Claims & Grounding Cards */}
            <section className="space-y-4">
              <div className="border-b border-slate-100 dark:border-slate-800 pb-2 mb-3 flex items-center justify-between">
                <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100 tracking-tight uppercase">
                  Synthesized Precedential Grounding
                </h3>
                <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                  3 Discrete Claims Indexed
                </span>
              </div>

              {/* Claim 1 */}
              <ClaimCard
                claim={claims[0]}
                isActiveChunk={activeChunk.id === claims[0].chunkId}
                onInspectChunk={handleSelectChunkById}
                defaultExpanded={true}
              />

              {/* Claim 2 */}
              <ClaimCard
                claim={claims[1]}
                isActiveChunk={activeChunk.id === claims[1].chunkId}
                onInspectChunk={handleSelectChunkById}
                defaultExpanded={false}
              />

              {/* Claim 3 (Conflict Alert) */}
              <ConflictAlert
                alert={conflictAlert}
                onInspectChunk={handleSelectChunkById}
              />
            </section>

            <div className="h-16" />
          </div>

          {/* Sticky Bottom Prompt & Filter Bar */}
          <BottomQueryBar
            onSynthesize={handleSynthesizeQuery}
            isLoading={isRunningSynthesis}
          />
        </main>

        {/* Right Evidence & Provenance Drawer */}
        <ProvenanceDrawer
          activeChunk={activeChunk}
          secondaryChunks={secondaryChunks}
          onSelectChunk={(chunk) => {
            setActiveChunk(chunk);
            showToast(`Inspecting: ${chunk.docTitle}`);
          }}
          onOpenSlipOp={(chunk) => setSlipOpChunk(chunk)}
          verificationHash={metadata.verificationHash}
          embeddingModel={metadata.embeddingModel}
        />
      </div>

      {/* Floating Toast Notification */}
      {toastMessage && (
        <div
          id="jurisynth-status-toast"
          className="fixed bottom-20 left-1/2 -translate-x-1/2 z-50 px-4 py-2.5 rounded-lg bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900 text-xs font-semibold shadow-lg border border-slate-800 dark:border-slate-200 flex items-center gap-2 animate-in fade-in slide-in-from-bottom-3 duration-200"
        >
          <span className="w-2 h-2 rounded-full bg-emerald-400 dark:bg-emerald-600 animate-ping" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Slip Opinion Modal */}
      {slipOpChunk && (
        <SlipOpModal
          chunk={slipOpChunk}
          onClose={() => setSlipOpChunk(null)}
        />
      )}

      {/* Export Audit Modal */}
      {showExportAudit && (
        <ExportAuditModal
          metadata={metadata}
          activeChunk={activeChunk}
          allChunks={allChunks}
          claims={claims}
          onClose={() => setShowExportAudit(false)}
        />
      )}

      {/* Knowledge Graph Modal */}
      {showKnowledgeGraph && (
        <KnowledgeGraphModal
          onClose={() => setShowKnowledgeGraph(false)}
          onSelectChunkById={handleSelectChunkById}
        />
      )}

      {/* Model Audit Modal */}
      {showModelAudit && (
        <ModelAuditModal
          metadata={metadata}
          onClose={() => setShowModelAudit(false)}
        />
      )}

      {/* New Legal Synthesis Modal */}
      {showNewSynthesis && (
        <NewSynthesisModal
          onClose={() => setShowNewSynthesis(false)}
          onSelectMatter={handleSelectMatter}
        />
      )}

      {/* Settings Modal */}
      {showSettings && (
        <SettingsModal
          metadata={metadata}
          onUpdateMetadata={(updated) => {
            setMetadata((prev) => ({ ...prev, ...updated }));
            showToast('Synthesis configuration updated.');
          }}
          onClose={() => setShowSettings(false)}
        />
      )}
    </div>
  );
}
