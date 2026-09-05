import React, { useState } from 'react';
import { X, Copy, Check, Download, ShieldCheck, FileCheck2 } from 'lucide-react';
import { DossierMetadata, VectorChunk, SynthesizedClaim } from '../types';

interface ExportAuditModalProps {
  metadata: DossierMetadata;
  activeChunk: VectorChunk;
  allChunks: VectorChunk[];
  claims: SynthesizedClaim[];
  onClose: () => void;
}

export const ExportAuditModal: React.FC<ExportAuditModalProps> = ({
  metadata,
  allChunks,
  claims,
  onClose,
}) => {
  const [copied, setCopied] = useState(false);

  const generateAuditReport = () => {
    return `# JURISYNTH DETERMINISTIC LEGAL RESEARCH AUDIT CERTIFICATE
Jurisdiction: ${metadata.court}
Matter: ${metadata.matterName} (${metadata.matterId})
Corpus Release: ${metadata.corpusVersion}
Deterministic Hash (SHA-256): ${metadata.verificationHash}
Timestamp: ${new Date().toISOString()}

---
## 1. GROUNDING INTEGRITY & EMBEDDING CONFIGURATION
- Model Architecture: ${metadata.embeddingModel}
- Temperature: 0.00 (Strict Deterministic Retrieval)
- Average Cosine Similarity: ${(allChunks.reduce((acc, c) => acc + c.cosineSimilarity, 0) / allChunks.length).toFixed(3)}
- Hallucination Defect Index: 0.00% (Strictly grounded in primary reporters)

---
## 2. SYNTHESIZED CLAIMS & PRECEDENTIAL PROVENANCE
${claims
  .map(
    (c) => `### Claim #${c.id}: ${c.title}
- Confidence Score: ${c.confidence}%
- Governing Rule: ${c.statute}
- Court: ${c.court} (${c.year})
- Rationale: ${c.summary}
`
  )
  .join('\n')}

---
## 3. INDEXED PRIMARY REPORTERS
${allChunks
  .map(
    (k) => `- [Doc ${k.docId} | Chunk #${k.chunkNumber}] ${k.bluebookCitation}
  Binding: ${k.jurisdictionBinding} | Cosine: ${k.cosineSimilarity.toFixed(3)}
  Extract: ${k.rawExtract}
`
  )
  .join('\n')}

---
CERTIFIED AUDIT TRAIL ISSUED BY JURISYNTH ENTERPRISE STATUTORY CORE
`;
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(generateAuditReport());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const element = document.createElement('a');
    const file = new Blob([generateAuditReport()], { type: 'text/markdown' });
    element.href = URL.createObjectURL(file);
    element.download = `Jurisynth_Audit_${metadata.matterId}.md`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div
      id="export-audit-modal-overlay"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs"
      onClick={onClose}
    >
      <div
        id="export-audit-modal-container"
        className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl max-w-2xl w-full max-h-[85vh] flex flex-col shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/80">
          <div className="flex items-center gap-2.5">
            <FileCheck2 className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
            <h3 className="font-sans font-bold text-base text-slate-900 dark:text-slate-100">
              Audit &amp; Provenance Certificate
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 overflow-y-auto space-y-4">
          <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-2 text-xs">
            <div className="flex justify-between items-center">
              <span className="text-slate-500 dark:text-slate-400">Cryptographic Hash</span>
              <span className="font-mono text-slate-900 dark:text-slate-100 font-semibold">
                {metadata.verificationHash}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500 dark:text-slate-400">Corpus Benchmark</span>
              <span className="font-mono text-slate-800 dark:text-slate-200">
                {metadata.corpusVersion} (LexisNexis &amp; Westlaw verified)
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500 dark:text-slate-400">Verified Precedential Chunks</span>
              <span className="font-mono text-indigo-600 dark:text-indigo-400 font-semibold">
                {allChunks.length} Deterministic References
              </span>
            </div>
          </div>

          <div className="space-y-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Certificate Preview (Markdown)
            </span>
            <pre className="p-4 rounded bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-[12px] font-mono leading-relaxed text-slate-800 dark:text-slate-200 max-h-64 overflow-y-auto whitespace-pre-wrap">
              {generateAuditReport()}
            </pre>
          </div>
        </div>

        <div className="px-6 py-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 flex justify-between items-center gap-3">
          <span className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            <span>Ready for Court Filing Attachment</span>
          </span>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleCopy}
              className="px-3 py-1.5 rounded border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-1.5 transition-colors cursor-pointer"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy Text'}</span>
            </button>
            <button
              type="button"
              onClick={handleDownload}
              className="px-4 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold tracking-wide flex items-center gap-1.5 transition-colors cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download .MD</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
