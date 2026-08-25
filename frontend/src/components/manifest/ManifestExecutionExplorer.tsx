'use client';

import React from 'react';
import { Terminal, CheckCircle2, Clock, Cpu, HardDrive, AlertTriangle } from 'lucide-react';
import { GenomeResponse } from '@/types/gdi';

interface ManifestExecutionExplorerProps {
  genome: GenomeResponse | null;
}

export const ManifestExecutionExplorer: React.FC<ManifestExecutionExplorerProps> = ({ genome }) => {
  const steps = genome?.processing_manifest?.steps || [];

  return (
    <div className="flex-1 bg-[#0f1115] flex flex-col font-mono text-xs select-none overflow-hidden">
      {/* Header */}
      <div className="h-10 bg-[#171a21] border-b border-[#2a2f3a] px-4 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2 text-slate-200 font-bold">
          <Terminal className="w-4 h-4 text-[#3b82f6]" />
          <span>PIPELINE BUILD EXECUTION MANIFEST EXPLORER</span>
        </div>
        <div className="text-[11px] text-slate-400">
          Job ID: <span className="text-slate-200">{genome?.job_id || 'N/A'}</span>
        </div>
      </div>

      {/* Step Execution Table */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        <div className="bg-[#171a21] border border-[#2a2f3a] rounded overflow-hidden">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0f1115] text-slate-400 border-b border-[#2a2f3a] text-[10px] uppercase font-mono">
              <tr>
                <th className="py-2 px-3">Step #</th>
                <th className="py-2 px-3">Pipeline Stage Name</th>
                <th className="py-2 px-3">Status</th>
                <th className="py-2 px-3">Duration (ms)</th>
                <th className="py-2 px-3">CPU %</th>
                <th className="py-2 px-3">Memory (MB)</th>
                <th className="py-2 px-3">Warnings / Output</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#2a2f3a] text-slate-200 font-mono text-[11px]">
              {steps.map((step, idx) => (
                <tr key={idx} className="hover:bg-[#1f232d] transition-colors">
                  <td className="py-2 px-3 text-slate-500">{String(idx + 1).padStart(2, '0')}</td>
                  <td className="py-2 px-3 font-semibold text-slate-200">{step.step_name}</td>
                  <td className="py-2 px-3">
                    <span className="inline-flex items-center gap-1 bg-[#10b981]/20 text-[#10b981] border border-[#10b981]/30 px-1.5 py-0.5 rounded text-[10px]">
                      <CheckCircle2 className="w-3 h-3" />
                      <span>{step.status}</span>
                    </span>
                  </td>
                  <td className="py-2 px-3 text-[#10b981] font-bold">{step.duration_ms.toFixed(1)}ms</td>
                  <td className="py-2 px-3 text-slate-300">{step.cpu_percent}%</td>
                  <td className="py-2 px-3 text-slate-300">{step.memory_rss_mb} MB</td>
                  <td className="py-2 px-3 text-slate-400 truncate max-w-xs">
                    {step.warnings && step.warnings.length > 0 ? (
                      <span className="text-[#f59e0b] flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3" />
                        <span>{step.warnings[0]}</span>
                      </span>
                    ) : (
                      <span>Clean stage completion</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
