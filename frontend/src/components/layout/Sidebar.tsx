'use client';

import React from 'react';
import { 
  FolderOpen,
  ChevronRight,
  ChevronDown,
  FileCode,
  Settings,
  Pin
} from 'lucide-react';
import { GenomeResponse } from '@/types/gdi';

interface SidebarProps {
  currentGenome: GenomeResponse | null;
  recentGenomes: GenomeResponse[];
  onSelectGenome: (g: GenomeResponse) => void;
  onOpenFileUpload: () => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentGenome,
  recentGenomes,
  onSelectGenome,
  onOpenFileUpload,
  isCollapsed,
  onToggleCollapse,
}) => {
  const [recentOpen, setRecentOpen] = React.useState(true);
  const [pinnedOpen, setPinnedOpen] = React.useState(true);

  if (isCollapsed) {
    return (
      <aside className="w-10 bg-[#171a21] border-r border-[#2a2f3a] flex flex-col items-center py-2 gap-3 select-none shrink-0">
        <button onClick={onToggleCollapse} className="p-1 hover:bg-[#1f232d] text-slate-400 hover:text-slate-200 rounded-[2px]" title="Expand">
          <ChevronRight className="w-4 h-4" />
        </button>
        <button onClick={onOpenFileUpload} className="p-1.5 hover:bg-[#1f232d] text-[#3b82f6] rounded-[2px]" title="Open Document">
          <FolderOpen className="w-4 h-4" />
        </button>
      </aside>
    );
  }

  // Static recent docs shown when no real genomes loaded (matches reference.png)
  const staticRecent = [
    { name: 'domain_bill.pdf', time: 'Today 17:43', active: true },
    { name: 'cert_degree.pdf', time: 'Today 16:12', active: false },
    { name: 'invoice_sample.jpg', time: 'Today 14:05', active: false },
    { name: 'document_01.pdf', time: 'Yesterday 22:18', active: false },
  ];

  const staticPinned = [
    'University_Certificate.pdf',
    'Company_Invoice.pdf',
  ];

  return (
    <aside className="w-[220px] bg-[#171a21] border-r border-[#2a2f3a] flex flex-col select-none shrink-0 font-sans text-[12px]">
      {/* Header */}
      <div className="h-9 border-b border-[#2a2f3a] px-3 flex items-center justify-between">
        <span className="text-slate-400 text-[11px] font-medium uppercase tracking-wider font-mono">Workspace</span>
        <button onClick={onToggleCollapse} className="p-0.5 hover:bg-[#1f232d] text-slate-500 hover:text-slate-300 rounded-[2px]">
          <ChevronRight className="w-3.5 h-3.5 rotate-180" />
        </button>
      </div>

      {/* Open Document Button */}
      <div className="p-3 border-b border-[#2a2f3a]">
        <button
          onClick={onOpenFileUpload}
          className="w-full flex items-center gap-2 justify-center bg-[#1f232d] hover:bg-[#2a2f3a] border border-[#2a2f3a] text-slate-200 py-1.5 px-3 rounded-[2px] font-medium text-[12px] transition-colors"
        >
          <FolderOpen className="w-3.5 h-3.5 text-[#3b82f6]" />
          Open Document
        </button>
      </div>

      {/* Tree Content */}
      <div className="flex-1 overflow-y-auto py-2">

        {/* Recent Documents Section */}
        <div>
          <button
            onClick={() => setRecentOpen(!recentOpen)}
            className="w-full flex items-center justify-between px-3 py-1 text-slate-400 hover:text-slate-200 text-[11px] font-medium"
          >
            <span>Recent Documents</span>
            {recentOpen ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
          </button>

          {recentOpen && (
            <div className="mt-0.5">
              {recentGenomes.length > 0 ? recentGenomes.map((item, idx) => (
                <button
                  key={item.genome_id}
                  onClick={() => onSelectGenome(item)}
                  className={`w-full text-left px-3 py-2 flex items-start gap-2 transition-colors border-l-2 ${
                    currentGenome?.genome_id === item.genome_id
                      ? 'bg-[#1f232d] border-[#3b82f6] text-slate-100'
                      : 'border-transparent text-slate-300 hover:bg-[#1a1e27] hover:text-slate-100'
                  }`}
                >
                  <FileCode className="w-3.5 h-3.5 text-slate-400 mt-0.5 shrink-0" />
                  <div className="truncate">
                    <div className="font-medium truncate text-[12px]">{item.genome_id.substring(0, 18)}...</div>
                    <div className="text-[10px] text-slate-500 mt-0.5">Today 17:43</div>
                  </div>
                </button>
              )) : staticRecent.map((item) => (
                <div
                  key={item.name}
                  className={`w-full text-left px-3 py-2 flex items-start gap-2 transition-colors border-l-2 cursor-pointer ${
                    item.active
                      ? 'bg-[#1f232d] border-[#3b82f6] text-slate-100'
                      : 'border-transparent text-slate-300 hover:bg-[#1a1e27] hover:text-slate-100'
                  }`}
                >
                  <FileCode className="w-3.5 h-3.5 text-slate-400 mt-0.5 shrink-0" />
                  <div className="truncate">
                    <div className="font-medium truncate text-[12px]">{item.name}</div>
                    <div className="text-[10px] text-slate-500 mt-0.5">{item.time}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Pinned Section */}
        <div className="mt-2">
          <button
            onClick={() => setPinnedOpen(!pinnedOpen)}
            className="w-full flex items-center justify-between px-3 py-1 text-slate-400 hover:text-slate-200 text-[11px] font-medium"
          >
            <span>Pinned</span>
            {pinnedOpen ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
          </button>

          {pinnedOpen && (
            <div className="mt-0.5">
              {staticPinned.map((name) => (
                <div
                  key={name}
                  className="px-3 py-1.5 flex items-center gap-2 text-slate-300 hover:bg-[#1a1e27] hover:text-slate-100 cursor-pointer border-l-2 border-transparent"
                >
                  <Pin className="w-3 h-3 text-slate-500 shrink-0" />
                  <span className="truncate text-[12px]">{name}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Settings at bottom */}
      <div className="border-t border-[#2a2f3a] p-2">
        <button className="w-full text-left px-2 py-1.5 text-slate-400 hover:text-slate-200 hover:bg-[#1f232d] rounded-[2px] flex items-center gap-2 text-[12px]">
          <Settings className="w-3.5 h-3.5" />
          Settings
        </button>
      </div>
    </aside>
  );
};
