'use client';

import React from 'react';
import { 
  FileSearch, 
  Columns, 
  Terminal, 
  Database, 
  FileText, 
  Settings, 
  Upload, 
  Search,
  Activity,
  Minus,
  Square,
  X
} from 'lucide-react';
import { ActiveWorkspace } from '@/types/gdi';

interface HeaderProps {
  activeWorkspace: ActiveWorkspace;
  setActiveWorkspace: (w: ActiveWorkspace) => void;
  isBackendHealthy: boolean;
  backendStatus?: 'healthy' | 'degraded' | 'offline';
  latencyMs?: number | null;
  onOpenFileUpload: () => void;
  onToggleCommandPalette: () => void;
  onToggleGlobalSearch: () => void;
  documentName?: string;
}

export const Header: React.FC<HeaderProps> = ({
  activeWorkspace,
  setActiveWorkspace,
  isBackendHealthy,
  backendStatus = isBackendHealthy ? 'healthy' : 'offline',
  latencyMs,
  onOpenFileUpload,
  onToggleCommandPalette,
}) => {
  return (
    <header className="h-10 bg-[#171a21] border-b border-[#2a2f3a] px-3 flex items-center select-none shrink-0 text-xs">
      {/* System Logo */}
      <div className="flex items-center gap-2 mr-5 shrink-0">
        <Activity className="w-4 h-4 text-[#3b82f6]" />
        <div className="flex flex-col leading-none">
          <span className="font-bold text-slate-100 text-[13px] tracking-tight">GDI</span>
          <span className="text-slate-500 text-[9px] font-normal tracking-tight leading-tight">Genome Document Intelligence</span>
        </div>
        <span className="text-slate-500 text-[10px] font-mono ml-1">v1.0.0</span>
      </div>

      {/* Workspace Switcher Tabs */}
      <nav className="flex items-center gap-0.5 flex-1">
        {([
          { key: 'analysis', label: 'Analysis', icon: FileSearch, active: true },
          { key: 'comparison', label: 'Compare', icon: Columns },
          { key: 'manifest', label: 'Manifest', icon: Terminal },
          { key: 'datasets', label: 'Datasets', icon: Database },
          { key: 'reports', label: 'Reports', icon: FileText },
          { key: 'settings', label: 'Settings', icon: Settings },
        ] as const).map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setActiveWorkspace(key as ActiveWorkspace)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-[2px] text-[12px] font-medium transition-colors ${
              activeWorkspace === key
                ? 'bg-[#1f232d] text-slate-100 border border-[#3f4756]'
                : 'text-slate-400 hover:text-slate-200 hover:bg-[#1f232d]/60'
            }`}
          >
            <Icon className="w-3.5 h-3.5" />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      {/* Right Controls */}
      <div className="flex items-center gap-2 shrink-0">
        <button
          onClick={onToggleCommandPalette}
          className="flex items-center gap-2 bg-[#0f1115] hover:bg-[#1f232d] border border-[#2a2f3a] text-slate-300 px-2.5 py-1 rounded-[2px] text-[11px] transition-colors"
        >
          <Search className="w-3.5 h-3.5 text-slate-400" />
          <span className="font-mono">Search...</span>
          <kbd className="bg-[#171a21] border border-[#2a2f3a] px-1 text-[9px] text-slate-400 rounded-[2px]">Ctrl+K</kbd>
        </button>

        <button
          onClick={onOpenFileUpload}
          className="flex items-center gap-1.5 bg-[#3b82f6] hover:bg-[#2563eb] text-white px-2.5 py-1 rounded-[2px] font-medium text-[11px] transition-colors"
        >
          <Upload className="w-3.5 h-3.5" />
          <span>Upload File</span>
        </button>

        {/* Backend Status */}
        <div className="flex items-center gap-1.5 text-[11px] font-mono pl-2 text-slate-400 border-l border-[#2a2f3a]">
          <span
            className={`w-1.5 h-1.5 rounded-full ${
              backendStatus === 'healthy'
                ? 'bg-[#10b981]'
                : backendStatus === 'degraded'
                ? 'bg-[#f59e0b]'
                : 'bg-[#ef4444]'
            }`}
          />
          <span>
            Backend:{' '}
            {backendStatus === 'healthy'
              ? `Connected (${latencyMs !== null && latencyMs !== undefined ? latencyMs : '--'} ms)`
              : backendStatus === 'degraded'
              ? `Degraded (${latencyMs !== null && latencyMs !== undefined ? latencyMs : '--'} ms)`
              : 'Offline'}
          </span>
        </div>

        {/* Window Controls */}
        <div className="flex items-center gap-2.5 pl-3 text-slate-500">
          <button className="hover:text-slate-300 transition-colors" title="Minimize"><Minus className="w-3 h-3" /></button>
          <button className="hover:text-slate-300 transition-colors" title="Maximize"><Square className="w-2.5 h-2.5" /></button>
          <button className="hover:text-[#ef4444] transition-colors" title="Close"><X className="w-3 h-3" /></button>
        </div>
      </div>
    </header>
  );
};
