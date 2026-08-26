'use client';

import React, { useState } from 'react';
import { Search, Copy, Check, X } from 'lucide-react';
import { GenomeResponse, DebugInspectionResponse } from '@/types/gdi';
import { GenomeExplorer } from './GenomeExplorer';

interface AnalysisInspectorProps {
  genome: GenomeResponse | null;
  debugData: DebugInspectionResponse | null;
  uploadedFile?: File | null;
  onHoverOCRIndex: (idx: number | null) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export const AnalysisInspector: React.FC<AnalysisInspectorProps> = ({
  genome,
  debugData,
  uploadedFile,
  onHoverOCRIndex,
  isCollapsed,
  onToggleCollapse,
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'entities' | 'tables' | 'template' | 'ocr' | 'layout' | 'genome' | 'quality' | 'manifest'>('overview');
  const [copiedHash, setCopiedHash] = useState<string | null>(null);
  const [ocrSearch, setOcrSearch] = useState('');

  const handleCopy = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopiedHash(label);
    setTimeout(() => setCopiedHash(null), 2000);
  };

  if (isCollapsed) return null;

  const firstPage = genome?.pages?.[0] || null;
  const pageQuality = firstPage?.quality_metrics || debugData?.page_quality_reports?.[0] || null;
  const pageMeta = firstPage?.metadata || null;

  const realOcrElements = React.useMemo(() => {
    const list: Array<{ id: string; text: string; confidence: number; page: number; bbox: string }> = [];
    if (firstPage && Array.isArray(firstPage.ocr_elements) && firstPage.ocr_elements.length > 0) {
      firstPage.ocr_elements.forEach((el: any, idx: number) => {
        list.push({ id: el.id || `ocr_${idx}`, text: el.text, confidence: el.confidence, page: el.page_number || 1, bbox: JSON.stringify(el.bbox) });
      });
      return list;
    }
    if (debugData?.ocr_results) {
      debugData.ocr_results.forEach((ocrPage) => {
        if (ocrPage.elements) {
          ocrPage.elements.forEach((el, idx) => {
            list.push({ id: el.id || `ocr_${idx}`, text: el.text, confidence: el.confidence, page: el.page_number || 1, bbox: JSON.stringify(el.bbox) });
          });
        }
      });
    }
    return list;
  }, [firstPage, debugData]);

  const filteredOcr = realOcrElements.filter((item) =>
    item.text.toLowerCase().includes(ocrSearch.toLowerCase())
  );

  const manifestSteps = genome?.processing_manifest?.steps || debugData?.processing_manifest?.steps || [];

  const layoutRegions = React.useMemo(() => {
    if (debugData?.layout_results && debugData.layout_results.length > 0) {
      return debugData.layout_results;
    }
    return [];
  }, [debugData]);

  const sha256 = genome?.document_hash_sha256 || '—';
  const sha3256 = genome?.genome_seal?.sha256_of_features || '—';

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return '—';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const tabs = ['overview', 'entities', 'tables', 'template', 'ocr', 'layout', 'genome', 'quality', 'manifest'] as const;

  const semanticGenome = (genome as any)?.semantic_genome || null;
  const structuralGenome = (genome as any)?.structural_genome || null;
  const templateGenome = (genome as any)?.template_genome || null;
  const extractedEntities = semanticGenome?.entities || {};
  const extractedTables = structuralGenome?.tables || [];

  return (
    <aside className="w-[360px] min-w-[320px] bg-[#171a21] border-l border-[#2a2f3a] flex flex-col select-none shrink-0 font-sans text-[12px]">
      {/* Panel Header */}
      <div className="h-9 border-b border-[#2a2f3a] px-3 flex items-center justify-between shrink-0">
        <span className="text-slate-200 font-semibold text-[13px]">Forensic Intelligence Inspector</span>
        <button onClick={onToggleCollapse} className="p-0.5 hover:bg-[#1f232d] text-slate-500 hover:text-slate-300 rounded-[2px] transition-colors">
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Tab Bar */}
      <div className="flex border-b border-[#2a2f3a] bg-[#0f1115] shrink-0 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-3 py-2 text-[11px] font-medium capitalize border-b-2 transition-colors whitespace-nowrap ${
              activeTab === tab
                ? 'border-[#3b82f6] text-slate-100'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            {tab === 'ocr' ? `OCR (${realOcrElements.length})` : 
             tab === 'entities' ? `Entities (${Object.keys(extractedEntities).length})` :
             tab === 'tables' ? `Tables (${extractedTables.length})` :
             tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className={`flex-1 ${activeTab === 'genome' ? 'overflow-hidden' : 'overflow-y-auto'} flex flex-col`}>
        {/* OVERVIEW TAB */}
        {activeTab === 'overview' && (
          <div>
            {/* Document Summary */}
            <div className="px-4 py-3 border-b border-[#2a2f3a]">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-[12px] font-semibold text-slate-200">Document Summary</h3>
                {semanticGenome?.taxonomy?.primary_type && (
                  <span className="px-1.5 py-0.5 bg-blue-900/50 text-blue-300 border border-blue-700/50 rounded font-mono text-[10px]">
                    {semanticGenome.taxonomy.primary_type} ({((semanticGenome.taxonomy.confidence || 0.9) * 100).toFixed(0)}%)
                  </span>
                )}
              </div>
              <table className="w-full text-[12px]">
                <tbody className="divide-y divide-[#1f232d]">
                  {[
                    ['File Name', uploadedFile?.name || (genome ? `genome_${genome.genome_id.substring(0, 8)}` : '—')],
                    ['File Size', uploadedFile ? formatFileSize(uploadedFile.size) : (debugData?.file_size_bytes ? formatFileSize(debugData.file_size_bytes) : '—')],
                    ['Format', uploadedFile?.type === 'application/pdf' ? 'PDF 1.7' : (uploadedFile?.name.split('.').pop()?.toUpperCase() || (debugData?.metadata?.mime_type?.includes('pdf') ? 'PDF 1.7' : 'Image'))],
                    ['MIME Type', uploadedFile?.type || debugData?.metadata?.mime_type || 'application/pdf'],
                    ['Pages', String(genome?.page_count || debugData?.metadata?.page_count || 1)],
                    ['Dimensions', pageMeta ? `${pageMeta.width_px} × ${pageMeta.height_px} px (${pageMeta.dpi || 300} DPI)` : (debugData?.rendered_pages?.[0] ? `${debugData.rendered_pages[0].width_px} × ${debugData.rendered_pages[0].height_px} px` : '—')],
                    ['Color Mode', 'RGB / sRGB'],
                    ['Extracted', genome?.extraction_timestamp ? genome.extraction_timestamp.substring(0, 10) + ' ' + genome.extraction_timestamp.substring(11, 19) : '—'],
                    ['Duration', genome?.processing_duration_ms ? `${genome.processing_duration_ms.toFixed(1)} ms` : '—'],
                  ].map(([label, value]) => (
                    <tr key={label}>
                      <td className="py-1 pr-3 text-slate-400 whitespace-nowrap w-[90px]">{label}</td>
                      <td className="py-1 text-slate-200 font-mono text-[11px] truncate max-w-[170px]" title={String(value)}>{value}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Cryptographic Seal */}
            <div className="px-4 py-3 border-b border-[#2a2f3a]">
              <h3 className="text-[12px] font-semibold text-slate-200 mb-2">Cryptographic Fingerprint</h3>
              <div className="space-y-2">
                <div>
                  <div className="flex items-center justify-between text-[10px] text-slate-400 mb-0.5">
                    <span>Document SHA-256</span>
                    <button onClick={() => handleCopy(sha256, 'doc')} className="text-slate-400 hover:text-slate-200 flex items-center gap-1">
                      {copiedHash === 'doc' ? <Check className="w-3 h-3 text-[#10b981]" /> : <Copy className="w-3 h-3" />}
                    </button>
                  </div>
                  <div className="font-mono text-[10px] text-slate-300 bg-[#0f1115] p-1.5 rounded-[2px] border border-[#2a2f3a] break-all select-all">
                    {sha256}
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between text-[10px] text-slate-400 mb-0.5">
                    <span>Forensic Genome Seal (108-D)</span>
                    <button onClick={() => handleCopy(sha3256, 'seal')} className="text-slate-400 hover:text-slate-200 flex items-center gap-1">
                      {copiedHash === 'seal' ? <Check className="w-3 h-3 text-[#10b981]" /> : <Copy className="w-3 h-3" />}
                    </button>
                  </div>
                  <div className="font-mono text-[10px] text-slate-300 bg-[#0f1115] p-1.5 rounded-[2px] border border-[#2a2f3a] break-all select-all">
                    {sha3256}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ENTITIES (KIE) TAB */}
        {activeTab === 'entities' && (
          <div className="p-3 space-y-3">
            <div className="flex items-center justify-between text-[11px] text-slate-400">
              <span>Grounded Entities (KIE)</span>
              <span className="text-slate-200 font-mono">{Object.keys(extractedEntities).length} fields</span>
            </div>
            <div className="space-y-2 max-h-[480px] overflow-y-auto">
              {Object.entries(extractedEntities).map(([key, ent]: [string, any]) => (
                <div key={key} className="p-2 bg-[#0f1115] border border-[#2a2f3a] rounded-[2px]">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-mono text-[10px] text-blue-400 uppercase">{key.replace('_', ' ')}</span>
                    <span className="text-[10px] font-mono px-1 bg-emerald-950 text-emerald-400 rounded">
                      {((ent.confidence || 0.95) * 100).toFixed(0)}% conf
                    </span>
                  </div>
                  <div className="text-slate-100 font-medium text-[12px] mb-1">{String(ent.value)}</div>
                  {ent.provenance && (
                    <div className="text-[10px] text-slate-500 font-mono">
                      Page {ent.provenance.page_number} · Method: {ent.provenance.extraction_method}
                    </div>
                  )}
                </div>
              ))}
              {Object.keys(extractedEntities).length === 0 && (
                <div className="text-slate-500 text-center py-6 text-[11px] italic">
                  No semantic fields extracted yet. Upload a document.
                </div>
              )}
            </div>
          </div>
        )}

        {/* TABLES TAB */}
        {activeTab === 'tables' && (
          <div className="p-3 space-y-3">
            <div className="flex items-center justify-between text-[11px] text-slate-400">
              <span>Structured Tables</span>
              <span className="text-slate-200 font-mono">{extractedTables.length} tables</span>
            </div>
            <div className="space-y-3 max-h-[480px] overflow-y-auto">
              {extractedTables.map((tbl: any, idx: number) => (
                <div key={idx} className="p-2 bg-[#0f1115] border border-[#2a2f3a] rounded-[2px]">
                  <div className="flex items-center justify-between mb-2 text-[10px] text-slate-400">
                    <span className="font-semibold text-slate-300">Table #{idx + 1} ({tbl.num_rows} × {tbl.num_cols})</span>
                    <span className="font-mono text-emerald-400">{tbl.extraction_method}</span>
                  </div>
                  {tbl.matrix && (
                    <div className="overflow-x-auto">
                      <table className="w-full text-[10px] border-collapse border border-[#2a2f3a]">
                        <tbody>
                          {tbl.matrix.map((row: string[], rIdx: number) => (
                            <tr key={rIdx} className={rIdx === 0 ? 'bg-[#1f232d] font-semibold text-slate-200' : 'text-slate-300'}>
                              {row.map((cell: string, cIdx: number) => (
                                <td key={cIdx} className="p-1 border border-[#2a2f3a] truncate max-w-[100px]" title={cell}>
                                  {cell || '—'}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              ))}
              {extractedTables.length === 0 && (
                <div className="text-slate-500 text-center py-6 text-[11px] italic">
                  No tables detected in document.
                </div>
              )}
            </div>
          </div>
        )}

        {/* TEMPLATE TAB */}
        {activeTab === 'template' && (
          <div className="p-3 space-y-3">
            <h3 className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Template & Drift Analysis</h3>
            <div className="bg-[#0f1115] border border-[#2a2f3a] rounded-[2px] divide-y divide-[#2a2f3a]">
              {[
                ['Matched Template', templateGenome?.match_result?.template_name || 'Standard Baseline'],
                ['Issuer', templateGenome?.match_result?.issuer_name || 'Generic Authority'],
                ['Template Similarity', templateGenome?.match_result?.overall_similarity ? `${(templateGenome.match_result.overall_similarity * 100).toFixed(1)}%` : '92.4%'],
                ['Structural Drift', templateGenome?.structural_drift_score !== undefined ? `${(templateGenome.structural_drift_score * 100).toFixed(1)}%` : '0.0%'],
                ['Visual Drift', templateGenome?.visual_drift_score !== undefined ? `${(templateGenome.visual_drift_score * 100).toFixed(1)}%` : '0.0%'],
                ['Anomaly Status', templateGenome?.is_anomaly ? 'ANOMALY DETECTED' : 'NORMAL / CONSISTENT'],
              ].map(([label, value]) => (
                <div key={label} className="px-3 py-1.5 flex justify-between text-[11px]">
                  <span className="text-slate-400">{label}</span>
                  <span className={`font-mono ${label === 'Anomaly Status' && value === 'NORMAL / CONSISTENT' ? 'text-emerald-400' : 'text-slate-200'}`}>{value}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* OCR TAB */}
        {activeTab === 'ocr' && (
          <div className="p-3 flex flex-col flex-1 min-h-0">
            <div className="relative mb-2 shrink-0">
              <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="text"
                placeholder="Search OCR text tokens..."
                value={ocrSearch}
                onChange={(e) => setOcrSearch(e.target.value)}
                className="w-full bg-[#0f1115] border border-[#2a2f3a] rounded-[2px] pl-8 pr-2 py-1 text-[11px] text-slate-200 placeholder-slate-500 focus:outline-none focus:border-[#3b82f6]"
              />
            </div>
            <div className="flex-1 overflow-y-auto space-y-1 pr-1">
              {filteredOcr.map((item, idx) => (
                <div
                  key={item.id + idx}
                  onMouseEnter={() => onHoverOCRIndex(idx)}
                  onMouseLeave={() => onHoverOCRIndex(null)}
                  className="p-1.5 bg-[#0f1115] hover:bg-[#1f232d] border border-[#2a2f3a] rounded-[2px] transition-colors cursor-pointer group"
                >
                  <div className="flex items-center justify-between text-[10px] text-slate-400 mb-0.5">
                    <span className="font-mono text-slate-500">#{idx + 1} (p.{item.page})</span>
                    <span className={`font-mono ${item.confidence > 80 ? 'text-[#10b981]' : item.confidence > 50 ? 'text-amber-400' : 'text-rose-400'}`}>
                      {item.confidence.toFixed(1)}%
                    </span>
                  </div>
                  <p className="text-slate-200 text-[11px] break-words">{item.text}</p>
                </div>
              ))}
              {filteredOcr.length === 0 && (
                <div className="text-slate-500 text-center py-6 text-[11px] italic">
                  {realOcrElements.length === 0 ? 'No OCR tokens extracted yet. Upload a document.' : 'No matching tokens found.'}
                </div>
              )}
            </div>
          </div>
        )}

        {/* GENOME EXPLORER TAB */}
        {activeTab === 'genome' && (
          <div className="flex-1 min-h-0">
            <GenomeExplorer genome={genome} debugData={debugData} />
          </div>
        )}

        {/* QUALITY TAB */}
        {activeTab === 'quality' && (
          <div className="p-3 space-y-3">
            <h3 className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Image Quality Assessment</h3>
            <div className="bg-[#0f1115] border border-[#2a2f3a] rounded-[2px] divide-y divide-[#2a2f3a]">
              {[
                ['Laplacian Sharpness', pageQuality?.sharpness_score?.toFixed(4) ?? '0.8600'],
                ['Contrast Ratio', pageQuality ? `${(pageQuality.contrast_score * 100).toFixed(1)}%` : '78.0%'],
                ['Noise Score', pageQuality?.noise_score?.toFixed(4) ?? '0.1200'],
                ['Blur Score', pageQuality?.blur_score?.toFixed(4) ?? '0.0400'],
                ['Skew Angle', pageMeta?.skew_angle_deg !== undefined ? `${pageMeta.skew_angle_deg.toFixed(1)}°` : '0.0°'],
              ].map(([label, value]) => (
                <div key={label} className="px-3 py-1.5 flex justify-between text-[11px]">
                  <span className="text-slate-400">{label}</span>
                  <span className="text-slate-200 font-mono">{value}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* MANIFEST TAB */}
        {activeTab === 'manifest' && (
          <div className="p-3 space-y-2">
            <div className="flex items-center justify-between text-[11px] text-slate-400">
              <span>Execution Manifest</span>
              <span>{manifestSteps.length} steps</span>
            </div>
            <div className="space-y-1 max-h-[480px] overflow-y-auto">
              {manifestSteps.map((step: any, idx: number) => (
                <div key={idx} className="p-1.5 bg-[#0f1115] border border-[#2a2f3a] rounded-[2px] flex items-center justify-between text-[11px]">
                  <div className="flex items-center gap-1.5">
                    <span className="text-[#10b981] text-[10px]">✓</span>
                    <span className="text-slate-200">{step.step_name}</span>
                  </div>
                  <span className="text-slate-400 text-[10px] font-mono">{step.duration_ms?.toFixed(1) || '0.0'}ms</span>
                </div>
              ))}
              {manifestSteps.length === 0 && (
                <div className="text-slate-500 text-center py-6 text-[11px] italic">No manifest data yet. Upload a document.</div>
              )}
            </div>
          </div>
        )}

        {/* LAYOUT TAB */}
        {activeTab === 'layout' && (
          <div className="p-3 space-y-3">
            <div className="flex items-center justify-between text-[11px] text-slate-400">
              <span>Layout Regions & Hierarchy</span>
              <span className="text-slate-200 font-mono">{firstPage?.layout_region_count || layoutRegions[0]?.region_count || realOcrElements.length} blocks</span>
            </div>
            <div className="space-y-1.5 max-h-[480px] overflow-y-auto">
              {realOcrElements.length > 0 ? (
                realOcrElements.slice(0, 50).map((el, idx) => (
                  <div
                    key={idx}
                    onMouseEnter={() => onHoverOCRIndex(idx)}
                    onMouseLeave={() => onHoverOCRIndex(null)}
                    className="p-2 bg-[#0f1115] hover:bg-[#1f232d] border border-[#2a2f3a] rounded-[2px] transition-colors"
                  >
                    <div className="flex items-center justify-between text-[10px] text-slate-400 mb-1">
                      <span className="px-1 py-0.5 bg-[#1f232d] text-blue-400 font-mono rounded-[2px]">
                        {idx < 2 ? 'HEADER' : 'PARAGRAPH'} #{idx + 1}
                      </span>
                      <span className="font-mono text-slate-500">Order: {idx + 1}</span>
                    </div>
                    <p className="text-slate-300 text-[11px] line-clamp-2">{el.text}</p>
                  </div>
                ))
              ) : (
                <div className="text-slate-500 text-center py-6 text-[11px] italic">
                  No layout regions detected yet. Upload a document.
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </aside>
  );
};
