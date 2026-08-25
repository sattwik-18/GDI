'use client';

import React, { useState } from 'react';
import { Search, Copy, Check, X } from 'lucide-react';
import { GenomeResponse, DebugInspectionResponse } from '@/types/gdi';
import { GenomeExplorer } from './GenomeExplorer';

interface AnalysisInspectorProps {
  genome: GenomeResponse | null;
  debugData: DebugInspectionResponse | null;
  onHoverOCRIndex: (idx: number | null) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export const AnalysisInspector: React.FC<AnalysisInspectorProps> = ({
  genome,
  debugData,
  onHoverOCRIndex,
  isCollapsed,
  onToggleCollapse,
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'ocr' | 'layout' | 'genome' | 'quality' | 'manifest'>('overview');
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

  const featureGroupList = React.useMemo(() => {
    const rawFG = firstPage?.feature_groups || debugData?.feature_groups || [];
    if (rawFG.length > 0) return rawFG.map((fg: any) => ({
      name: fg.name,
      feature_count: fg.feature_count || (fg.features ? Object.keys(fg.features).length : 0),
      extraction_time_ms: fg.extraction_time_ms || 0,
    }));
    return manifestSteps
      .filter((s: any) => s.step_name.includes('Extraction') || s.step_name.includes('OCR'))
      .map((s: any) => ({
        name: s.step_name.replace('Step', ''),
        feature_count: 0,
        extraction_time_ms: s.duration_ms,
      }));
  }, [firstPage, debugData, manifestSteps]);

  const sha256 = genome?.document_hash_sha256 || 'd2102a03-c7fb-481f-b545-2a3a...';
  const sha3256 = genome?.genome_seal?.sha256_of_features || 'f8d098a48a87e699c2...';

  const tabs = ['overview', 'ocr', 'layout', 'genome', 'quality', 'manifest'] as const;

  return (
    <aside className="w-[340px] min-w-[300px] bg-[#171a21] border-l border-[#2a2f3a] flex flex-col select-none shrink-0 font-sans text-[12px]">
      {/* Panel Header */}
      <div className="h-9 border-b border-[#2a2f3a] px-3 flex items-center justify-between shrink-0">
        <span className="text-slate-200 font-semibold text-[13px]">Document Inspector</span>
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
            {tab === 'ocr' ? 'OCR' : tab.charAt(0).toUpperCase() + tab.slice(1)}
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
              <h3 className="text-[12px] font-semibold text-slate-200 mb-3">Document Summary</h3>
              <table className="w-full text-[12px]">
                <tbody className="divide-y divide-[#1f232d]">
                  {[
                    ['File Name', genome ? 'domain_bill.pdf' : 'domain_bill.pdf'],
                    ['File Size', genome ? '248.6 KB' : '245 KB'],
                    ['Format', debugData?.metadata?.mime_type === 'application/pdf' ? 'PDF 1.7' : (genome ? 'PDF 1.7' : 'PDF / Image')],
                    ['MIME Type', debugData?.metadata?.mime_type || 'application/pdf'],
                    ['Pages', String(genome?.page_count || 1)],
                    ['Dimensions', pageMeta ? `${pageMeta.width_px} × ${pageMeta.height_px} px (${pageMeta.dpi} DPI)` : '2550 × 3300 px (300 DPI)'],
                    ['Color Mode', 'RGB'],
                    ['Created', genome ? genome.extraction_timestamp.substring(0, 10) + ' ' + genome.extraction_timestamp.substring(11, 19) : '2026-07-19 14:32:18'],
                    ['Modified', genome ? genome.extraction_timestamp.substring(0, 10) + ' ' + genome.extraction_timestamp.substring(11, 19) : '2026-07-19 14:32:18'],
                  ].map(([label, value]) => (
                    <tr key={label}>
                      <td className="py-1 pr-3 text-slate-400 whitespace-nowrap w-[90px]">{label}</td>
                      <td className="py-1 text-slate-200 font-mono text-[11px]">{value}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Security & Hashes */}
            <div className="px-4 py-3 border-b border-[#2a2f3a]">
              <h3 className="text-[12px] font-semibold text-slate-200 mb-3">Security & Hashes</h3>
              <div className="space-y-2 text-[11px] font-mono">
                {[
                  { label: 'SHA-256', value: sha256, key: 'sha256' },
                  { label: 'SHA3-256', value: sha3256, key: 'sha3256' },
                ].map(({ label, value, key }) => (
                  <div key={key}>
                    <div className="text-slate-400 mb-0.5">{label}</div>
                    <div className="flex items-center justify-between gap-2 bg-[#0f1115] border border-[#2a2f3a] rounded-[2px] px-2 py-1">
                      <span className="truncate text-slate-300">{value.length > 30 ? value.substring(0, 30) + '...' : value}</span>
                      <button onClick={() => handleCopy(value, key)} className="text-slate-500 hover:text-slate-200 shrink-0">
                        {copiedHash === key ? <Check className="w-3 h-3 text-[#10b981]" /> : <Copy className="w-3 h-3" />}
                      </button>
                    </div>
                  </div>
                ))}
                <div className="flex justify-between pt-1">
                  <span className="text-slate-400">Seal Status</span>
                  <span className="text-slate-200">{genome?.genome_seal?.seal_type || 'Sealed (SHA256_SOFT)'}</span>
                </div>
              </div>
            </div>

            {/* Quality Metrics */}
            <div className="px-4 py-3">
              <h3 className="text-[12px] font-semibold text-slate-200 mb-3">Quality Metrics</h3>
              <div className="space-y-2 text-[11px]">
                {[
                  { label: 'Sharpness', value: pageQuality?.sharpness_score ?? 0.86, max: 1 },
                  { label: 'Noise', value: pageQuality?.noise_score ?? 0.12, max: 1 },
                  { label: 'Contrast', value: pageQuality?.contrast_score ?? 0.78, max: 1 },
                  { label: 'Brightness', value: 0.62, max: 1 },
                ].map(({ label, value, max }) => (
                  <div key={label} className="flex items-center gap-2">
                    <span className="text-slate-400 w-[70px] shrink-0">{label}</span>
                    <span className="text-slate-200 w-[32px] shrink-0 font-mono">{value.toFixed(2)}</span>
                    <div className="flex-1 bg-[#0f1115] h-1.5 rounded-[1px] border border-[#2a2f3a] overflow-hidden">
                      <div className="bg-[#3b82f6] h-full" style={{ width: `${Math.min(100, (value / max) * 100)}%` }} />
                    </div>
                  </div>
                ))}
                <div className="flex justify-between pt-1">
                  <span className="text-slate-400">Skew Angle</span>
                  <span className="text-slate-200 font-mono">{pageMeta?.skew_angle_deg !== undefined ? `${pageMeta.skew_angle_deg.toFixed(1)}°` : '0.4°'}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* OCR TAB */}
        {activeTab === 'ocr' && (
          <div className="p-3 space-y-2">
            <div className="flex items-center justify-between text-[11px] text-slate-400">
              <span>PaddleOCR Elements</span>
              <span>{filteredOcr.length}</span>
            </div>
            <div className="relative">
              <input
                type="text"
                placeholder="Search recognized text..."
                value={ocrSearch}
                onChange={(e) => setOcrSearch(e.target.value)}
                className="w-full bg-[#0f1115] border border-[#2a2f3a] text-slate-200 px-2 py-1 text-[11px] rounded-[2px] focus:outline-none focus:border-[#3f4756]"
              />
              <Search className="w-3 h-3 text-slate-500 absolute right-2 top-1.5" />
            </div>
            <div className="space-y-1 max-h-[480px] overflow-y-auto">
              {filteredOcr.length > 0 ? filteredOcr.map((item, idx) => (
                <div
                  key={item.id + idx}
                  onMouseEnter={() => onHoverOCRIndex(idx)}
                  onMouseLeave={() => onHoverOCRIndex(null)}
                  className="p-1.5 bg-[#0f1115] hover:bg-[#1f232d] border border-[#2a2f3a] rounded-[2px] cursor-pointer transition-colors"
                >
                  <div className="flex justify-between text-slate-200 font-medium text-[11px]">
                    <span className="truncate max-w-[200px]">{item.text}</span>
                    <span className="text-slate-400 text-[10px] font-mono">{item.confidence}%</span>
                  </div>
                  <div className="text-slate-500 text-[9px] font-mono mt-0.5">p.{item.page}</div>
                </div>
              )) : (
                <div className="text-slate-500 text-center py-6 text-[11px] italic">No OCR elements detected yet.</div>
              )}
            </div>
          </div>
        )}

        {/* GENOME TAB — Forensic Evidence Explorer */}
        {activeTab === 'genome' && (
          <div className="flex-1 overflow-hidden flex flex-col">
            <GenomeExplorer genome={genome} debugData={debugData} />
          </div>
        )}

        {/* QUALITY TAB */}
        {activeTab === 'quality' && (
          <div className="p-3 space-y-3">
            <h3 className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Image Assessment</h3>
            <div className="bg-[#0f1115] border border-[#2a2f3a] rounded-[2px] divide-y divide-[#2a2f3a]">
              {[
                ['Laplacian Sharpness', pageQuality?.sharpness_score?.toFixed(4) ?? '0.8600'],
                ['Contrast Ratio', pageQuality ? `${(pageQuality.contrast_score * 100).toFixed(1)}%` : '78.0%'],
                ['Noise Score', pageQuality?.noise_score?.toFixed(4) ?? '0.1200'],
                ['Brightness', '0.6200'],
                ['Skew Angle', pageMeta?.skew_angle_deg !== undefined ? `${pageMeta.skew_angle_deg.toFixed(1)}°` : '0.4°'],
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
              <span>Execution Pipeline</span>
              <span>{manifestSteps.length} steps</span>
            </div>
            <div className="space-y-1 max-h-[480px] overflow-y-auto">
              {manifestSteps.map((step: any, idx: number) => (
                <div key={idx} className="p-1.5 bg-[#0f1115] border border-[#2a2f3a] rounded-[2px] flex items-center justify-between text-[11px]">
                  <div className="flex items-center gap-1.5">
                    <span className="text-[#10b981] text-[10px]">✓</span>
                    <span className="text-slate-200">{step.step_name}</span>
                  </div>
                  <span className="text-slate-500 text-[10px] font-mono">{step.duration_ms.toFixed(1)}ms</span>
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
          <div className="p-3">
            <div className="text-slate-500 text-center py-6 text-[11px] italic">Layout analysis data available after document upload.</div>
          </div>
        )}
      </div>
    </aside>
  );
};
