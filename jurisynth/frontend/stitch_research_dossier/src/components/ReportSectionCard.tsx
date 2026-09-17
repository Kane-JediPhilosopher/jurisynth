import React, { useState } from 'react';
import { ChevronDown, FileSearch, Image as ImageIcon } from 'lucide-react';
import { AuxiliaryImage, ReportSection } from '../api';

interface Props {
  section: ReportSection;
  onInspectImage: (image: AuxiliaryImage) => void;
}

export const ReportSectionCard: React.FC<Props> = ({ section, onInspectImage }) => {
  const [openClaims, setOpenClaims] = useState<Set<string>>(new Set());
  const toggle = (id: string) => setOpenClaims((previous) => {
    const next = new Set(previous);
    next.has(id) ? next.delete(id) : next.add(id);
    return next;
  });
  return <section className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-5 space-y-4">
    <div>
      <h3 className="font-semibold text-slate-900 dark:text-slate-100">{section.title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-slate-600 dark:text-slate-300">{section.answer_text}</p>
    </div>
    {section.claims.map((claim) => <div key={claim.claim_id} className="rounded-lg border border-slate-200 dark:border-slate-700">
      <button type="button" onClick={() => toggle(claim.claim_id)} className="w-full p-3 text-left flex gap-2 items-start hover:bg-slate-50 dark:hover:bg-slate-800">
        <ChevronDown className={`mt-0.5 h-4 w-4 shrink-0 text-indigo-600 transition-transform ${openClaims.has(claim.claim_id) ? 'rotate-180' : ''}`} />
        <span className="text-sm text-slate-800 dark:text-slate-200">{claim.text}</span>
      </button>
      {openClaims.has(claim.claim_id) && <div className="border-t border-slate-200 dark:border-slate-700 p-3 space-y-3">
        {claim.evidence.length === 0 ? <p className="text-xs text-amber-700 dark:text-amber-300">No directly linked evidence was returned for this claim.</p> : claim.evidence.map((evidence) => <div key={evidence.evidence_id} className="text-xs space-y-2">
          <div className="flex gap-2 text-slate-500 dark:text-slate-400"><FileSearch className="h-4 w-4 shrink-0" /><span className="font-mono">{evidence.evidence_id}</span></div>
          {evidence.sources.map((source) => <blockquote key={`${evidence.evidence_id}-${source.chunk_id}`} className="border-l-2 border-indigo-400 pl-3 text-slate-700 dark:text-slate-300">
            <p>{source.excerpt}</p><footer className="mt-1 font-mono text-[10px] text-slate-500">{source.document_id} / {source.chunk_id}</footer>
          </blockquote>)}
        </div>)}
      </div>}
    </div>)}
    {section.child_sections.map((child) => <div key={child.section_id} className="ml-3 border-l-2 border-slate-200 dark:border-slate-700 pl-3"><ReportSectionCard section={child} onInspectImage={onInspectImage} /></div>)}
  </section>;
};

export const AuxiliaryImages: React.FC<{ images: AuxiliaryImage[]; onInspect: (image: AuxiliaryImage) => void }> = ({ images, onInspect }) => {
  if (images.length === 0) return null;
  return <section className="rounded-xl border border-sky-200 dark:border-sky-900 bg-sky-50/40 dark:bg-sky-950/20 p-5">
    <div className="flex gap-2 text-sm font-semibold text-sky-900 dark:text-sky-100"><ImageIcon className="h-4 w-4" /> Auxiliary visual context</div>
    <p className="mt-1 text-xs text-sky-800 dark:text-sky-300">Images are contextual only and do not independently support legal claims.</p>
    <div className="mt-3 space-y-2">{images.map((image) => <button key={image.image_id} type="button" onClick={() => onInspect(image)} className="w-full rounded border border-sky-200 dark:border-sky-800 bg-white/80 dark:bg-slate-900 p-3 text-left hover:bg-white">
      <p className="text-sm text-slate-800 dark:text-slate-100">{image.description}</p><p className="mt-1 text-xs text-slate-500">{image.document_id}</p>
    </button>)}</div>
  </section>;
};
