'use client';

import React from 'react';
import { GenomeResponse } from '@/types/gdi';

interface StatusBarProps {
  genome: GenomeResponse | null;
  isBackendHealthy: boolean;
  zoomLevel: number;
  cursorPos: { x: number; y: number };
  latencyMs?: number | null;
  systemMetrics?: { cpuPercent?: number; memoryMb?: number } | null;
}

export const StatusBar: React.FC<StatusBarProps> = ({
  genome,
  isBackendHealthy,
  zoomLevel,
  cursorPos,
  latencyMs,
  systemMetrics,
}) => {
  return (
    <footer className="h-5 bg-[#0f1115] border-t border-[#2a2f3a] px-3 flex items-center justify-between select-none shrink-0 font-mono text-[10px] text-slate-400">
      {/* Left */}
      <div className="flex items-center gap-4">
        <span className="text-slate-300">Ready</span>
        {genome && (
          <>
            <span>Job: <span className="text-slate-200">{genome.job_id.substring(0, 8)}</span></span>
            <span>Genome: <span className="text-slate-200">{genome.genome_id.substring(0, 8)}</span></span>
            <span>Features: <span className="text-slate-200">{genome.genome_seal.feature_count}</span></span>
            <span>Page: <span className="text-slate-200">1/{genome.page_count}</span></span>
          </>
        )}
        <span>Zoom: <span className="text-slate-200">{zoomLevel}%</span></span>
      </div>

      {/* Right */}
      <div className="flex items-center gap-4">
        <span>Cursor: <span className="text-slate-200">{cursorPos.x}, {cursorPos.y} px</span></span>
        <span>CPU <span className="text-slate-200">{systemMetrics?.cpuPercent !== undefined ? `${systemMetrics.cpuPercent}%` : '12%'}</span></span>
        <span>RAM <span className="text-slate-200">{systemMetrics?.memoryMb !== undefined ? `${systemMetrics.memoryMb} MB` : '487 MB'}</span></span>
        <span>Ping <span className={isBackendHealthy ? "text-[#10b981]" : "text-[#ef4444]"}>{isBackendHealthy ? `${latencyMs ?? 0} ms` : 'Offline'}</span></span>
        <span className="text-slate-400">v1.0.0</span>
      </div>
    </footer>
  );
};
