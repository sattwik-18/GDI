'use client';

import React, { useState, useEffect } from 'react';
import { Search, X, FileText, Database, ShieldCheck, Cpu } from 'lucide-react';
import { GenomeResponse } from '@/types/gdi';

interface GlobalSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  genome: GenomeResponse | null;
}

export const GlobalSearchModal: React.FC<GlobalSearchModalProps> = ({
  isOpen,
  onClose,
  genome,
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'f' || e.key === 'F')) {
        e.preventDefault();
        isOpen ? onClose() : null;
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const mockIndexResults = [
    { type: 'OCR recognized text', text: 'CERTIFICATE OF AUTHENTICITY', match: 'Certificate' },
    { type: 'OCR recognized text', text: 'DETERMINISTIC SHA-256 HASH VERIFIED', match: 'SHA-256' },
    { type: 'Canonical Feature', text: 'Geometry Group [width_px, height_px, aspect_ratio]', match: 'Geometry' },
    { type: 'Canonical Feature', text: 'Statistical Group [mean, std, skewness, kurtosis]', match: 'skewness' },
    { type: 'Pipeline Step', text: 'PaddleOCRStep (180.2ms - PASSED)', match: 'PaddleOCR' },
    { type: 'Seal Hash', text: genome?.genome_seal.sha256_of_features || '2f7e30a0...', match: 'Seal' },
  ];

  const filtered = mockIndexResults.filter(
    (item) =>
      item.text.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-start justify-center pt-20 p-4 select-none font-mono">
      <div className="w-full max-w-2xl bg-[#171a21] border border-[#2a2f3a] rounded-lg shadow-2xl overflow-hidden flex flex-col">
        {/* Search Input Bar */}
        <div className="p-3 border-b border-[#2a2f3a] flex items-center gap-2">
          <Search className="w-4 h-4 text-[#3b82f6]" />
          <input
            type="text"
            placeholder="Universal Index Search (Genome features, OCR, Hashes, Metadata, Manifest steps)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            autoFocus
            className="flex-1 bg-transparent text-slate-100 placeholder-slate-500 text-xs focus:outline-none"
          />
          <button onClick={onClose} className="text-slate-500 hover:text-slate-200">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Search Results */}
        <div className="max-h-96 overflow-y-auto p-3 space-y-2 text-xs">
          <div className="text-[10px] uppercase text-slate-500 font-mono tracking-wider">
            Search Index Matches ({filtered.length})
          </div>

          {filtered.length > 0 ? (
            filtered.map((res, idx) => (
              <div
                key={idx}
                className="p-2 bg-[#0f1115] border border-[#2a2f3a] hover:border-[#3b82f6] rounded flex items-center justify-between text-slate-200"
              >
                <div className="space-y-0.5">
                  <span className="text-[9px] bg-[#2a2f3a] text-[#3b82f6] px-1 py-0.2 rounded uppercase">
                    {res.type}
                  </span>
                  <div className="font-semibold text-slate-200 text-[11px] truncate max-w-md">
                    {res.text}
                  </div>
                </div>
                <span className="text-[10px] text-[#10b981] font-mono">MATCH</span>
              </div>
            ))
          ) : (
            <div className="text-slate-500 p-6 text-center">No indexed terms found matching &quot;{searchTerm}&quot;.</div>
          )}
        </div>
      </div>
    </div>
  );
};
