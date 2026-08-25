'use client';

import React, { useState } from 'react';
import {
  Columns,
  ShieldCheck,
  ShieldAlert,
  ArrowRightLeft,
  FileCheck,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Activity,
  BarChart3,
  Cpu,
  RefreshCw,
  Sparkles,
  Info
} from 'lucide-react';
import { GenomeResponse } from '@/types/gdi';
import { GDIClient } from '@/services/api';
import { useSessionStore } from '@/state/session.store';
import { ComparisonDocumentCard } from './ComparisonDocumentCard';
import { computeForensicMatchScore, ForensicScoreResult } from '@/core/comparison/forensicScorer';

interface ComparisonWorkbenchProps {
  primaryGenome: GenomeResponse | null;
  recentGenomes: GenomeResponse[];
}

export const ComparisonWorkbench: React.FC<ComparisonWorkbenchProps> = ({
  primaryGenome,
  recentGenomes,
}) => {
  const {
    uploadedFile: primaryFile,
    secondaryGenome,
    secondaryFile,
    isProcessingSecondary,
    secondaryError,
    setSecondaryGenome,
    setSecondaryFile,
    setProcessingSecondary,
    setSecondaryError,
    setActiveGenome,
    setUploadedFile,
    addRecentGenome,
  } = useSessionStore();

  const [activeTab, setActiveTab] = useState<'overview' | 'matrix' | 'manifest'>('overview');

  // Auto-initialize secondary genome from recent genomes if not already set and more than 1 exist
  React.useEffect(() => {
    if (!secondaryGenome && recentGenomes.length > 1) {
      const fallback = recentGenomes.find((g) => g.genome_id !== primaryGenome?.genome_id) || recentGenomes[1];
      if (fallback) {
        setSecondaryGenome(fallback, null);
      }
    }
  }, [recentGenomes, primaryGenome, secondaryGenome, setSecondaryGenome]);

  // Handle uploading Document B
  const handleUploadSecondary = async (file: File) => {
    setSecondaryFile(file);
    setProcessingSecondary(true);
    setSecondaryError(null);

    try {
      const genomeRes = await GDIClient.generateGenome(file);
      setSecondaryGenome(genomeRes, file);
      addRecentGenome(genomeRes);
    } catch (err: any) {
      setSecondaryError(err.message || 'Failed to process secondary document');
    } finally {
      setProcessingSecondary(false);
    }
  };

  // Handle uploading Document A directly in this tab if empty
  const handleUploadPrimary = async (file: File) => {
    setUploadedFile(file);
    try {
      const genomeRes = await GDIClient.generateGenome(file);
      setActiveGenome(genomeRes, null);
      addRecentGenome(genomeRes);
    } catch (err: any) {
      console.error('Failed to upload primary document:', err);
    }
  };

  // Calculate complete multi-dimensional forensic match score
  const scoreResult: ForensicScoreResult = React.useMemo(() => {
    return computeForensicMatchScore(primaryGenome, secondaryGenome);
  }, [primaryGenome, secondaryGenome]);

  const hasBothDocs = Boolean(primaryGenome && secondaryGenome);

  // Score color helper
  const getScoreColor = (score: number) => {
    if (score >= 95) return 'text-[#10b981] border-[#10b981] bg-[#10b981]/10';
    if (score >= 80) return 'text-[#3b82f6] border-[#3b82f6] bg-[#3b82f6]/10';
    if (score >= 60) return 'text-[#f59e0b] border-[#f59e0b] bg-[#f59e0b]/10';
    return 'text-[#ef4444] border-[#ef4444] bg-[#ef4444]/10';
  };

  const getScoreBarColor = (score: number) => {
    if (score >= 95) return 'bg-[#10b981]';
    if (score >= 80) return 'bg-[#3b82f6]';
    if (score >= 60) return 'bg-[#f59e0b]';
    return 'bg-[#ef4444]';
  };

  return (
    <div className="flex-1 bg-[#0a0c10] flex flex-col overflow-hidden font-mono text-xs select-none">
      {/* Top Header & Comparison Controls */}
      <div className="h-11 bg-[#141820] border-b border-[#2a2f3a] px-4 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-slate-100 font-bold tracking-wide">
            <Columns className="w-4 h-4 text-[#3b82f6]" />
            <span>REAL-TIME FORENSIC COMPARISON WORKBENCH</span>
          </div>

          <div className="flex items-center bg-[#090b0e] border border-[#2a2f3a] rounded p-0.5 text-[11px]">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-2.5 py-0.5 rounded transition-colors ${
                activeTab === 'overview' ? 'bg-[#242936] text-white font-semibold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Overview &amp; Score
            </button>
            <button
              onClick={() => setActiveTab('matrix')}
              className={`px-2.5 py-0.5 rounded transition-colors ${
                activeTab === 'matrix' ? 'bg-[#242936] text-white font-semibold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              108 Feature Vector Matrix
            </button>
          </div>
        </div>

        {/* Secondary Document Selector & Quick Switch */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 bg-[#090b0e] border border-[#2a2f3a] px-2.5 py-1 rounded text-[11px]">
            <span className="text-slate-400">Target Secondary:</span>
            <select
              value={secondaryGenome?.genome_id || ''}
              onChange={(e) => {
                const found = recentGenomes.find((g) => g.genome_id === e.target.value);
                if (found) setSecondaryGenome(found, null);
              }}
              className="bg-transparent text-slate-200 font-mono focus:outline-none cursor-pointer"
            >
              <option value="" disabled>-- Select target document --</option>
              {recentGenomes.map((g) => (
                <option key={g.genome_id} value={g.genome_id} className="bg-[#171a21] text-slate-200">
                  {g.genome_id.substring(0, 12)}... ({g.page_count || 1}p)
                </option>
              ))}
            </select>
          </div>

          {secondaryGenome && (
            <button
              onClick={() => setSecondaryGenome(null, null)}
              className="text-slate-400 hover:text-red-400 text-[10px] underline"
            >
              Clear Target
            </button>
          )}
        </div>
      </div>

      {/* Main Dual Document Side-by-Side Area */}
      <div className="flex-1 flex overflow-hidden p-3 gap-3">
        {/* Left Side: Document A (Primary) */}
        <ComparisonDocumentCard
          title="DOCUMENT A (PRIMARY)"
          role="primary"
          genome={primaryGenome}
          file={primaryFile}
          isProcessing={false}
          errorMessage={null}
          onUpload={handleUploadPrimary}
          recentGenomes={recentGenomes}
          onSelectRecent={(g) => setActiveGenome(g, null)}
        />

        {/* Right Side: Document B (Target / Comparison) */}
        <ComparisonDocumentCard
          title="DOCUMENT B (TARGET / COMPARISON)"
          role="secondary"
          genome={secondaryGenome}
          file={secondaryFile}
          isProcessing={isProcessingSecondary}
          errorMessage={secondaryError}
          onUpload={handleUploadSecondary}
          recentGenomes={recentGenomes}
          onSelectRecent={(g) => setSecondaryGenome(g, null)}
        />
      </div>

      {/* Bottom Forensic Match Score & Dimensional Breakdown Dashboard */}
      <div className="h-44 bg-[#141820] border-t border-[#2a2f3a] p-3 flex gap-4 overflow-x-auto shrink-0">
        {/* Master Score Gauge Card */}
        <div className="w-80 bg-[#0c0e12] border border-[#2a2f3a] rounded p-3 flex flex-col justify-between shrink-0">
          <div className="flex items-center justify-between text-[11px]">
            <span className="text-slate-400 uppercase font-semibold flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-[#3b82f6]" />
              Forensic Match Score
            </span>
            {hasBothDocs && (
              <span className="text-[10px] text-slate-500 font-mono">
                {scoreResult.vectorDeltaPct.toFixed(2)}% Delta
              </span>
            )}
          </div>

          {hasBothDocs ? (
            <div className="my-1 flex items-center gap-4">
              {/* Radial Big Score Badge */}
              <div
                className={`w-20 h-20 rounded-full border-2 flex flex-col items-center justify-center shadow-lg shrink-0 ${getScoreColor(
                  scoreResult.overallScore
                )}`}
              >
                <div className="text-xl font-extrabold tracking-tighter">
                  {scoreResult.overallScore.toFixed(1)}%
                </div>
                <div className="text-[8px] uppercase tracking-wider font-semibold opacity-80">
                  MATCH
                </div>
              </div>

              <div className="space-y-1 overflow-hidden">
                <div className="text-xs font-bold text-slate-100 truncate" title={scoreResult.verdict}>
                  {scoreResult.verdict}
                </div>
                <div className="text-[10px] text-slate-400 leading-tight">
                  {scoreResult.overallScore >= 99.5
                    ? 'Exact cryptographic seal and canonical feature match.'
                    : scoreResult.overallScore >= 90
                    ? 'Nearly identical document genome with minimal variance.'
                    : scoreResult.overallScore >= 70
                    ? 'Shared layout geometry with content or text differences.'
                    : 'Substantial structural and feature divergence detected.'}
                </div>
              </div>
            </div>
          ) : (
            <div className="my-auto text-center text-slate-500 text-[11px] italic">
              Upload Document B on the right to compute full 100% forensic match score.
            </div>
          )}

          <div className="text-[9px] text-slate-500 flex justify-between border-t border-[#2a2f3a] pt-1">
            <span>Deterministic 108-Dim Scoring</span>
            <span>GDI v1.0.0</span>
          </div>
        </div>

        {/* 4 Dimension Sub-Scores Progress Bars */}
        <div className="flex-1 bg-[#0c0e12] border border-[#2a2f3a] rounded p-3 flex flex-col justify-between min-w-[420px]">
          <div className="flex items-center justify-between text-[11px]">
            <span className="text-slate-400 uppercase font-semibold flex items-center gap-1.5">
              <BarChart3 className="w-3.5 h-3.5 text-[#10b981]" />
              Forensic Dimension Sub-Scores
            </span>
            <span className="text-[10px] text-slate-500">Weighted Multi-Scale Index</span>
          </div>

          <div className="grid grid-cols-2 gap-x-6 gap-y-2 my-auto">
            {/* Dimension 1: Feature Vector (40%) */}
            <div className="space-y-1">
              <div className="flex justify-between text-[10px]">
                <span className="text-slate-400">1. Feature Vector Sim (40%)</span>
                <span className="text-slate-200 font-bold">
                  {hasBothDocs ? `${scoreResult.breakdowns.featureVectorScore}%` : '—'}
                </span>
              </div>
              <div className="w-full bg-[#1e2330] h-1.5 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 ${getScoreBarColor(
                    scoreResult.breakdowns.featureVectorScore
                  )}`}
                  style={{ width: `${hasBothDocs ? scoreResult.breakdowns.featureVectorScore : 0}%` }}
                />
              </div>
            </div>

            {/* Dimension 2: Text / OCR Overlap (25%) */}
            <div className="space-y-1">
              <div className="flex justify-between text-[10px]">
                <span className="text-slate-400">2. Text &amp; OCR Overlap (25%)</span>
                <span className="text-slate-200 font-bold">
                  {hasBothDocs ? `${scoreResult.breakdowns.textOcrScore}%` : '—'}
                </span>
              </div>
              <div className="w-full bg-[#1e2330] h-1.5 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 ${getScoreBarColor(
                    scoreResult.breakdowns.textOcrScore
                  )}`}
                  style={{ width: `${hasBothDocs ? scoreResult.breakdowns.textOcrScore : 0}%` }}
                />
              </div>
            </div>

            {/* Dimension 3: Structural & Quality (20%) */}
            <div className="space-y-1">
              <div className="flex justify-between text-[10px]">
                <span className="text-slate-400">3. Structure &amp; Quality (20%)</span>
                <span className="text-slate-200 font-bold">
                  {hasBothDocs ? `${scoreResult.breakdowns.structuralScore}%` : '—'}
                </span>
              </div>
              <div className="w-full bg-[#1e2330] h-1.5 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 ${getScoreBarColor(
                    scoreResult.breakdowns.structuralScore
                  )}`}
                  style={{ width: `${hasBothDocs ? scoreResult.breakdowns.structuralScore : 0}%` }}
                />
              </div>
            </div>

            {/* Dimension 4: Cryptographic & Seal (15%) */}
            <div className="space-y-1">
              <div className="flex justify-between text-[10px]">
                <span className="text-slate-400">4. Cryptographic Seal (15%)</span>
                <span className="text-slate-200 font-bold">
                  {hasBothDocs ? `${scoreResult.breakdowns.cryptographicScore}%` : '—'}
                </span>
              </div>
              <div className="w-full bg-[#1e2330] h-1.5 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 ${getScoreBarColor(
                    scoreResult.breakdowns.cryptographicScore
                  )}`}
                  style={{ width: `${hasBothDocs ? scoreResult.breakdowns.cryptographicScore : 0}%` }}
                />
              </div>
            </div>
          </div>

          <div className="flex justify-between items-center text-[10px] text-slate-500 border-t border-[#2a2f3a] pt-1">
            <span>Cosine Sim: {hasBothDocs ? scoreResult.details.cosineSimilarity : '—'}</span>
            <span>L1 Distance: {hasBothDocs ? scoreResult.details.l1NormalizedDistance : '—'}</span>
            <span>
              SHA-256 Match: {hasBothDocs ? (scoreResult.details.hashExactMatch ? 'EXACT' : 'DIFFERENT') : '—'}
            </span>
          </div>
        </div>

        {/* Feature Groups Quick Delta Matrix */}
        <div className="w-96 bg-[#0c0e12] border border-[#2a2f3a] rounded p-3 flex flex-col justify-between shrink-0">
          <div className="flex items-center justify-between text-[11px]">
            <span className="text-slate-400 uppercase font-semibold flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-[#8b5cf6]" />
              Feature Groups Delta
            </span>
            <span className="text-[10px] text-slate-500">6 Domains</span>
          </div>

          {hasBothDocs && scoreResult.details.featureGroupDeltas.length > 0 ? (
            <div className="grid grid-cols-2 gap-1.5 my-1 text-[10px]">
              {scoreResult.details.featureGroupDeltas.slice(0, 6).map((grp, idx) => (
                <div key={idx} className="bg-[#141820] p-1.5 rounded border border-[#2a2f3a] flex justify-between items-center">
                  <span className="text-slate-400 truncate max-w-[100px]">{grp.groupName.split(' ')[0]}:</span>
                  <span
                    className={`font-bold font-mono ${
                      grp.similarityScore >= 90 ? 'text-[#10b981]' : grp.similarityScore >= 70 ? 'text-[#3b82f6]' : 'text-[#f59e0b]'
                    }`}
                  >
                    {grp.similarityScore.toFixed(0)}%
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="my-auto text-center text-slate-500 text-[10px] italic">
              Group deltas will calculate upon loading Doc B.
            </div>
          )}

          <div className="text-[9px] text-slate-500 flex justify-between border-t border-[#2a2f3a] pt-1">
            <span>Canonical Vector Dimensions: 108</span>
            <span>Status: Evaluated</span>
          </div>
        </div>
      </div>
    </div>
  );
};
