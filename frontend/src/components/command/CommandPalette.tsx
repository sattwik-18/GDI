'use client';

import React, { useState, useEffect } from 'react';
import { Command, Search, FileSearch, Columns, Terminal, Database, Settings, Upload, Copy, X } from 'lucide-react';
import { ActiveWorkspace } from '@/types/gdi';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  setActiveWorkspace: (w: ActiveWorkspace) => void;
  onOpenFileUpload: () => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({
  isOpen,
  onClose,
  setActiveWorkspace,
  onOpenFileUpload,
}) => {
  const [query, setQuery] = useState('');

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) {
        e.preventDefault();
        isOpen ? onClose() : null;
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const commands = [
    {
      title: 'Workspaces: Switch to Analysis Workstation',
      icon: FileSearch,
      action: () => { setActiveWorkspace('analysis'); onClose(); },
      shortcut: 'Ctrl+1',
    },
    {
      title: 'Workspaces: Switch to Comparison Workbench',
      icon: Columns,
      action: () => { setActiveWorkspace('comparison'); onClose(); },
      shortcut: 'Ctrl+2',
    },
    {
      title: 'Workspaces: Switch to Manifest Execution Explorer',
      icon: Terminal,
      action: () => { setActiveWorkspace('manifest'); onClose(); },
      shortcut: 'Ctrl+3',
    },
    {
      title: 'Workspaces: Switch to Datasets Manager',
      icon: Database,
      action: () => { setActiveWorkspace('datasets'); onClose(); },
      shortcut: 'Ctrl+4',
    },
    {
      title: 'Workspaces: Switch to Settings',
      icon: Settings,
      action: () => { setActiveWorkspace('settings'); onClose(); },
      shortcut: 'Ctrl+S',
    },
    {
      title: 'Document: Open Local File Upload...',
      icon: Upload,
      action: () => { onOpenFileUpload(); onClose(); },
      shortcut: 'Ctrl+O',
    },
  ];

  const filteredCommands = commands.filter((c) =>
    c.title.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-start justify-center pt-20 p-4 select-none font-mono">
      <div className="w-full max-w-xl bg-[#171a21] border border-[#2a2f3a] rounded-lg shadow-2xl overflow-hidden flex flex-col">
        {/* Search Header Input */}
        <div className="p-3 border-b border-[#2a2f3a] flex items-center gap-2">
          <Command className="w-4 h-4 text-[#3b82f6]" />
          <input
            type="text"
            placeholder="Type a command or search actions..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
            className="flex-1 bg-transparent text-slate-100 placeholder-slate-500 text-xs focus:outline-none"
          />
          <button onClick={onClose} className="text-slate-500 hover:text-slate-200">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Command List */}
        <div className="max-h-80 overflow-y-auto p-2 space-y-1 text-xs">
          {filteredCommands.length > 0 ? (
            filteredCommands.map((cmd, idx) => {
              const Icon = cmd.icon;
              return (
                <button
                  key={idx}
                  onClick={cmd.action}
                  className="w-full p-2 rounded flex items-center justify-between text-slate-200 hover:bg-[#1f232d] hover:text-white transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <Icon className="w-4 h-4 text-[#3b82f6]" />
                    <span>{cmd.title}</span>
                  </div>
                  <kbd className="bg-[#0f1115] border border-[#2a2f3a] px-1.5 py-0.5 text-[9px] text-slate-400 rounded">
                    {cmd.shortcut}
                  </kbd>
                </button>
              );
            })
          ) : (
            <div className="text-slate-500 p-4 text-center">No matching commands found.</div>
          )}
        </div>
      </div>
    </div>
  );
};
