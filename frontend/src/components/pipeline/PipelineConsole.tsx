'use client';

import React, { useState } from 'react';
import { GenomeResponse } from '@/types/gdi';
import { ChevronUp, ChevronDown } from 'lucide-react';

interface PipelineConsoleProps {
  genome: GenomeResponse | null;
}

// Matches design/reference.png pipeline stage layout exactly
const STAGE_COLORS = ['#10b981', '#10b981', '#10b981', '#10b981', '#10b981', '#10b981', '#10b981'];

export const PipelineConsole: React.FC<PipelineConsoleProps> = ({ genome }) => {
  const [activeTab, setActiveTab] = useState<'pipeline' | 'logs' | 'jobs'>('pipeline');
  const [isExpanded, setIsExpanded] = useState(true);

  const steps = genome?.processing_manifest?.steps?.slice(0, 7) ?? [
    { step_name: 'Ingest', duration_ms: 42 },
    { step_name: 'PDF Render', duration_ms: 128 },
    { step_name: 'OCR', duration_ms: 412 },
    { step_name: 'Layout', duration_ms: 96 },
    { step_name: 'Features', duration_ms: 87 },
    { step_name: 'Genome', duration_ms: 34 },
    { step_name: 'Seal', duration_ms: 5 },
  ];

  return (
    <div className="bg-[#171a21] border-t border-[#2a2f3a] shrink-0 select-none font-sans text-[11px]">
      {/* Tab Bar Header */}
      <div className="flex items-center justify-between px-3 border-b border-[#2a2f3a] bg-[#12151b]">
        <div className="flex items-center">
          {(['pipeline', 'logs', 'jobs'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-3 py-1.5 text-[11px] font-medium capitalize border-b-2 transition-colors ${
                activeTab === tab
                  ? 'border-[#3b82f6] text-slate-200'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              {tab === 'jobs' ? 'Jobs (0)' : tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
        <button onClick={() => setIsExpanded(!isExpanded)} className="text-slate-500 hover:text-slate-300 p-0.5">
          {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
        </button>
      </div>

      {/* Stage Cards — matches reference.png exactly */}
      {isExpanded && activeTab === 'pipeline' && (
        <div className="flex items-stretch overflow-x-auto">
          {steps.map((step, idx) => (
            <React.Fragment key={idx}>
              <div className="flex items-center gap-3 px-5 py-3 bg-[#171a21] hover:bg-[#1a1e27] transition-colors cursor-default min-w-[140px] flex-1">
                {/* Step number circle */}
                <div
                  className="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold text-white shrink-0"
                  style={{ backgroundColor: '#10b981', opacity: 0.9 }}
                >
                  {idx + 1}
                </div>
                <div>
                  <div className="text-slate-200 font-medium text-[12px]">
                    {step.step_name.replace('Step', '').trim()}
                  </div>
                  <div className="text-slate-500 text-[11px] font-mono">{step.duration_ms.toFixed(0)}ms</div>
                </div>
              </div>
              {idx < steps.length - 1 && (
                <div className="flex items-center text-slate-600 text-[14px] px-1 shrink-0">→</div>
              )}
            </React.Fragment>
          ))}
        </div>
      )}

      {isExpanded && activeTab === 'logs' && (
        <div className="px-4 py-2 space-y-0.5 font-mono text-[10px] text-slate-400 max-h-16 overflow-y-auto">
          <div>[INFO] Pipeline started for document: {genome?.document_id || 'domain_bill.pdf'}</div>
          <div>[OK] PaddleOCR detection complete. ({genome?.page_count || 1} page)</div>
          <div>[OK] 108-dimensional genome feature vector sealed.</div>
        </div>
      )}

      {isExpanded && activeTab === 'jobs' && (
        <div className="px-4 py-2 text-slate-500 text-[11px] italic">No active background jobs.</div>
      )}
    </div>
  );
};
