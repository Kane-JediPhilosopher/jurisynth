import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Sidebar, SidebarTab } from './components/Sidebar';
import { ExecutiveSynthesis } from './components/ExecutiveSynthesis';
import { AuxiliaryImages, ReportSectionCard } from './components/ReportSectionCard';
import { BottomQueryBar } from './components/BottomQueryBar';
import { SettingsModal } from './components/SettingsModal';
import { initialDossierMeta } from './data/dossierData';
import { DossierMetadata } from './types';
import { Info, CheckCircle2 } from 'lucide-react';
import { AuxiliaryImage, getDemoDossier, imageEndpoint, submitQuery, JurisynthDossier } from './api';

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
  const [dossier, setDossier] = useState<JurisynthDossier | null>(null);
  const [activeTab, setActiveTab] = useState<SidebarTab>('dossier');

  // Interactive Modals
  const [activeImage, setActiveImage] = useState<AuxiliaryImage | null>(null);
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

  useEffect(() => {
    getDemoDossier().then(setDossier).catch(() => {
      showToast('Jurisynth API is offline; showing the imported design placeholder.');
    });
  }, []);

  const toggleTheme = () => {
    setIsDark((prev) => !prev);
  };

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(null);
    }, 3200);
  };

  // Trigger interactive synthesis query
  const handleSynthesizeQuery = async (query: string) => {
    setIsRunningSynthesis(true);
    showToast(`Submitting Jurisynth research query: "${query.slice(0, 40)}..."`);
    try {
      const result = await submitQuery(query);
      setDossier(result);
      showToast(result.status === 'complete' ? 'Research report received.' : 'Jurisynth is ready for your query.');
    } catch (error) {
      showToast(error instanceof Error ? error.message : 'Jurisynth query failed.');
    } finally {
      setIsRunningSynthesis(false);
    }
  };

  const handleRunFullSynthesis = () => {
    setIsRunningSynthesis(true);
    showToast('Submit a question below to run Jurisynth research.');
    setTimeout(() => {
      setIsRunningSynthesis(false);
      showToast('No local re-index operation is exposed from the browser.');
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

  return (
    <div className="bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans antialiased overflow-x-hidden min-h-screen transition-colors duration-200 selection:bg-indigo-600 selection:text-white flex flex-col">
      {/* Top Application Header */}
      <Header
        metadata={metadata}
        isDark={isDark}
        onToggleTheme={toggleTheme}
        onOpenAudit={() => showToast('Detailed evidence is available by expanding a report claim.')}
        onOpenKnowledgeGraph={() => showToast('Community exploration will be enabled when global artifacts are available.')}
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
            if (tab === 'graph') showToast('Community exploration will be enabled when global artifacts are available.');
            if (tab === 'audit') showToast('Model diagnostics remain server-side.');
            if (tab === 'evidence') {
              showToast('Evidence & Provenance inspection drawer is open on the right.');
            }
          }}
          onNewSynthesis={() => showToast('Enter a new research question below.')}
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
                  {dossier?.disclaimer ?? 'Informational legal research synthesis; verify primary sources before relying on any result.'}
                </span>
              </div>
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-500 dark:text-slate-400 shrink-0 font-semibold">
                CORPUS VER: {metadata.corpusVersion}
              </span>
            </div>

            {/* Dossier Heading Area */}
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-xs mb-2">
                <span>Jurisynth</span><span>/</span><span>EU legislation pilot</span><span>/</span>
                <span className="font-semibold text-slate-700 dark:text-slate-300">Case Ref: {metadata.matterId}</span>
              </div>

              <h1 className="font-serif text-2xl md:text-3xl font-bold text-slate-900 dark:text-slate-100 tracking-tight leading-tight">
                {dossier?.query ?? 'Evidence-grounded legal research'}
              </h1>

              <div className="flex flex-wrap items-center gap-2 pt-1 pb-2">
                <span className="px-2 py-0.5 bg-red-100 text-red-700 dark:bg-red-950/60 dark:text-red-300 rounded text-[10px] font-bold uppercase tracking-wider">
                  HIGH RISK PRECEDENT
                </span>
                <span className="px-2 py-0.5 bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 rounded text-[10px] font-bold uppercase tracking-wider">
                  BATCH 0009 PILOT
                </span>
                <span className="ml-auto inline-flex items-center gap-1.5 text-[11px] font-medium text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/50 px-2.5 py-0.5 rounded-full">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Evidence-linked output</span>
                </span>
              </div>

              <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
                {dossier?.overview ?? 'Submit a question to retrieve a Jurisynth report with claim and source provenance.'}
              </p>

              {dossier?.ast && (
                <details className="rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 p-3 text-xs">
                  <summary className="cursor-pointer font-semibold text-indigo-700 dark:text-indigo-300">Query decomposition (QCompiler AST)</summary>
                  <pre className="mt-3 max-h-64 overflow-auto whitespace-pre-wrap font-mono text-[11px] text-slate-700 dark:text-slate-200">
                    {JSON.stringify(dossier.ast, null, 2)}
                  </pre>
                </details>
              )}
            </div>

            {/* Executive Synthesis Section */}
            <ExecutiveSynthesis overview={dossier?.overview} />

            {/* Synthesized Claims & Grounding Cards */}
            <section className="space-y-4">
              <div className="border-b border-slate-100 dark:border-slate-800 pb-2 mb-3 flex items-center justify-between">
                <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100 tracking-tight uppercase">
                  Grounded report
                </h3>
                <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                  {dossier?.sections.length ?? 0} report sections
                </span>
              </div>

              {dossier?.sections.length ? dossier.sections.map((section) => <ReportSectionCard key={section.section_id} section={section} onInspectImage={setActiveImage} />) : <p className="text-sm text-slate-500">No report sections yet.</p>}
            </section>
            <AuxiliaryImages images={dossier?.auxiliary_images ?? []} onInspect={setActiveImage} />

            <div className="h-16" />
          </div>

          {/* Sticky Bottom Prompt & Filter Bar */}
          <BottomQueryBar
            onSynthesize={handleSynthesizeQuery}
            isLoading={isRunningSynthesis}
          />
        </main>

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

      {activeImage && <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/50 p-4" onClick={() => setActiveImage(null)}><div className="max-w-xl rounded-xl bg-white p-6 shadow-xl dark:bg-slate-900" onClick={(event) => event.stopPropagation()}><h2 className="font-semibold">Auxiliary image context</h2><img className="mt-3 max-h-80 w-full rounded object-contain" src={imageEndpoint(activeImage.image_id)} alt={activeImage.alt ?? activeImage.description} onError={(event) => { event.currentTarget.hidden = true; }} /><p className="mt-3 text-sm">{activeImage.expanded_description ?? activeImage.description}</p>{activeImage.visual_findings.length > 0 && <ul className="mt-3 list-disc pl-5 text-sm">{activeImage.visual_findings.map((finding) => <li key={finding}>{finding}</li>)}</ul>}<p className="mt-4 text-xs text-slate-500">This visual context does not independently support a legal claim.</p><button type="button" className="mt-4 rounded bg-indigo-600 px-3 py-1.5 text-sm text-white" onClick={() => setActiveImage(null)}>Close</button></div></div>}


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
