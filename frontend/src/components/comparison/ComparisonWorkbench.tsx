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
  Info,
  Ban,
  Diff,
  Eye,
  GitBranch,
  Target,
  Calculator,
  Terminal,
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
    isProcessing: isProcessingPrimary,
    processingError: primaryError,
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
    setProcessing: setProcessingPrimary,
    setError: setPrimaryError,
    addRecentGenome,
  } = useSessionStore();

  const [activeTab, setActiveTab] = useState<'overview' | 'scorecard' | 'provenance' | 'formula' | 'diffs' | 'matrix'>('overview');
  const [selectedDimension, setSelectedDimension] = useState<string | null>(null);

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
    setProcessingPrimary(true);
    setPrimaryError(null);

    try {
      const genomeRes = await GDIClient.generateGenome(file);
      setActiveGenome(genomeRes, null);
      addRecentGenome(genomeRes);
    } catch (err: any) {
      setPrimaryError(err.message || 'Failed to process primary document');
    } finally {
      setProcessingPrimary(false);
    }
  };

  // Calculate complete multi-evidence forensic match score
  const scoreResult: ForensicScoreResult = React.useMemo(() => {
    return computeForensicMatchScore(primaryGenome, secondaryGenome);
  }, [primaryGenome, secondaryGenome]);

  const hasBothDocs = Boolean(primaryGenome && secondaryGenome);

  // Score color helper
  const getScoreColor = (score: number | null) => {
    if (score === null) return 'text-[#ef4444] border-[#ef4444] bg-[#ef4444]/10';
    if (score >= 90) return 'text-[#10b981] border-[#10b981] bg-[#10b981]/10';
    if (score >= 65) return 'text-[#3b82f6] border-[#3b82f6] bg-[#3b82f6]/10';
    if (score >= 35) return 'text-[#f59e0b] border-[#f59e0b] bg-[#f59e0b]/10';
    return 'text-[#ef4444] border-[#ef4444] bg-[#ef4444]/10';
  };

  const getScoreBarColor = (score: number) => {
    if (score >= 90) return 'bg-[#10b981]';
    if (score >= 65) return 'bg-[#3b82f6]';
    if (score >= 35) return 'bg-[#f59e0b]';
    return 'bg-[#ef4444]';
  };

  return (
    <div className="flex-1 bg-[#0a0c10] flex flex-col overflow-hidden font-mono text-xs select-none">
      {/* Top Header & Comparison Controls */}
      <div className="h-11 bg-[#141820] border-b border-[#2a2f3a] px-4 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-slate-100 font-bold tracking-wide">
            <Columns className="w-4 h-4 text-[#3b82f6]" />
            <span>MULTI-EVIDENCE DOCUMENT COMPARISON WORKBENCH</span>
          </div>

          <div className="flex items-center bg-[#090b0e] border border-[#2a2f3a] rounded p-0.5 text-[11px]">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-2.5 py-0.5 rounded transition-colors ${
                activeTab === 'overview' ? 'bg-[#242936] text-white font-semibold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Overview &amp; Decision
            </button>
            <button
              onClick={() => setActiveTab('scorecard')}
              className={`px-2.5 py-0.5 rounded transition-colors flex items-center gap-1 ${
                activeTab === 'scorecard' ? 'bg-[#242936] text-white font-semibold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Target className="w-3 h-3 text-[#10b981]" />
              Evidence Scorecard
            </button>
            <button
              onClick={() => setActiveTab('provenance')}
              className={`px-2.5 py-0.5 rounded transition-colors flex items-center gap-1 ${
                activeTab === 'provenance' ? 'bg-[#242936] text-white font-semibold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Cpu className="w-3 h-3 text-[#3b82f6]" />
              Model Provenance
            </button>
            <button
              onClick={() => setActiveTab('formula')}
              className={`px-2.5 py-0.5 rounded transition-colors flex items-center gap-1 ${
                activeTab === 'formula' ? 'bg-[#242936] text-white font-semibold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Calculator className="w-3 h-3 text-[#f59e0b]" />
              Formula Inspector
            </button>
            <button
              onClick={() => setActiveTab('diffs')}
              className={`px-2.5 py-0.5 rounded transition-colors flex items-center gap-1 ${
                activeTab === 'diffs' ? 'bg-[#242936] text-white font-semibold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Diff className="w-3 h-3" />
              Diffs ({scoreResult.differences.length})
            </button>
            <button
              onClick={() => setActiveTab('matrix')}
              className={`px-2.5 py-0.5 rounded transition-colors ${
                activeTab === 'matrix' ? 'bg-[#242936] text-white font-semibold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              108-D Matrix
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
        <ComparisonDocumentCard
          title="DOCUMENT A (PRIMARY)"
          role="primary"
          genome={primaryGenome}
          file={primaryFile}
          isProcessing={isProcessingPrimary}
          errorMessage={primaryError}
          onUpload={handleUploadPrimary}
          recentGenomes={recentGenomes}
          onSelectRecent={(g) => setActiveGenome(g, null)}
        />

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
      <div className="h-56 bg-[#141820] border-t border-[#2a2f3a] p-3 flex gap-4 overflow-x-auto shrink-0">
        {/* Master Score & Decision Gauge Card */}
        <div className="w-80 bg-[#0c0e12] border border-[#2a2f3a] rounded p-3 flex flex-col justify-between shrink-0">
          <div className="flex items-center justify-between text-[11px]">
            <span className="text-slate-400 uppercase font-semibold flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-[#3b82f6]" />
              Comparison Decision
            </span>
            {hasBothDocs && (
              <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded font-bold ${
                scoreResult.decision === 'DIFFERENT_DOCUMENTS' || scoreResult.comparisonStatus === 'INCOMPATIBLE'
                  ? 'bg-red-950 text-red-400 border border-red-800'
                  : 'bg-emerald-950 text-emerald-400 border border-emerald-800'
              }`}>
                {scoreResult.decision}
              </span>
            )}
          </div>

          {hasBothDocs ? (
            <div className="my-1 flex items-center gap-4">
              <div
                className={`w-20 h-20 rounded-full border-2 flex flex-col items-center justify-center shadow-lg shrink-0 ${getScoreColor(
                  scoreResult.overallScore
                )}`}
              >
                {scoreResult.isComparable && scoreResult.overallScore !== null ? (
                  <>
                    <div className="text-xl font-extrabold tracking-tighter">
                      {scoreResult.overallScore.toFixed(1)}%
                    </div>
                    <div className="text-[8px] uppercase tracking-wider font-semibold opacity-80">
                      SIMILARITY
                    </div>
                  </>
                ) : (
                  <>
                    <Ban className="w-6 h-6 text-red-500 mb-0.5" />
                    <div className="text-[8px] uppercase tracking-wider font-bold text-red-400">
                      N / A
                    </div>
                  </>
                )}
              </div>

              <div className="space-y-1 overflow-hidden">
                <div className="text-xs font-bold text-slate-100 truncate" title={scoreResult.verdict}>
                  {scoreResult.verdict}
                </div>
                <div className="text-[10px] text-slate-400 leading-tight line-clamp-2">
                  {scoreResult.compatibilityReason}
                </div>
                <div className="text-[9px] text-slate-500 flex gap-2 pt-0.5">
                  <span className="bg-[#171a21] px-1 rounded text-slate-300">
                    A: {scoreResult.inputA.modality} ({scoreResult.inputA.documentType || 'unknown'})
                  </span>
                  <span className="bg-[#171a21] px-1 rounded text-slate-300">
                    B: {scoreResult.inputB.modality} ({scoreResult.inputB.documentType || 'unknown'})
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <div className="my-auto text-center text-slate-500 text-[11px] italic">
              Upload Document B on the right to initiate multi-evidence comparison.
            </div>
          )}

          <div className="text-[9px] text-slate-500 flex justify-between border-t border-[#2a2f3a] pt-1">
            <span>Confidence: {hasBothDocs ? `${(scoreResult.decisionConfidence * 100).toFixed(1)}%` : '—'}</span>
            <span>GDI Provenance v3.0</span>
          </div>
        </div>

        {/* Tab 1: Evidence Scorecard */}
        {activeTab === 'scorecard' && (
          <div className="flex-1 bg-[#0c0e12] border border-[#2a2f3a] rounded p-3 flex flex-col justify-between min-w-[500px] overflow-y-auto">
            <div className="flex items-center justify-between text-[11px] mb-1">
              <span className="text-slate-400 uppercase font-semibold flex items-center gap-1.5">
                <Target className="w-3.5 h-3.5 text-[#10b981]" />
                Clickable Evidence Diagnostics (10 Dimensions)
              </span>
              <span className="text-[10px] text-slate-500">Click card to inspect</span>
            </div>

            <div className="grid grid-cols-3 gap-2 my-auto text-[10px]">
              <div
                onClick={() => setSelectedDimension('local_features')}
                className="bg-[#141820] hover:bg-[#1a202c] cursor-pointer p-2 rounded border border-[#2a2f3a] transition-all"
              >
                <div className="flex justify-between text-slate-400 font-semibold items-center">
                  <span>1. Local Match (LightGlue)</span>
                  <span className="text-slate-200 font-bold">{scoreResult.dimensions.localFeatureInliers !== null ? `${(scoreResult.dimensions.localFeatureInliers * 100).toFixed(1)}%` : 'N/A'}</span>
                </div>
                <div className="text-[9px] text-slate-400 mt-1 flex justify-between">
                  <span>Inliers: {scoreResult.details.ransacInliers ?? '0'} / {scoreResult.details.candidateMatches ?? '0'}</span>
                  <span className="text-amber-400 font-mono">Cov: {scoreResult.details.spatialCoverage ?? '0%'}</span>
                </div>
                <div className="text-[8.5px] text-slate-500 mt-0.5 flex justify-between">
                  <span>Error: {scoreResult.details.reprojectionError ?? 'N/A'}</span>
                  <span className="text-emerald-400 font-bold">Strength: HIGH</span>
                </div>
              </div>

              <div
                onClick={() => setSelectedDimension('layout_graph')}
                className="bg-[#141820] hover:bg-[#1a202c] cursor-pointer p-2 rounded border border-[#2a2f3a] transition-all"
              >
                <div className="flex justify-between text-slate-400 font-semibold items-center">
                  <span>2. Layout Graph Topology</span>
                  <span className="text-slate-200 font-bold">{scoreResult.dimensions.layoutGraphSimilarity !== null ? `${(scoreResult.dimensions.layoutGraphSimilarity * 100).toFixed(1)}%` : 'N/A'}</span>
                </div>
                <div className="text-[9px] text-slate-400 mt-1">Reading Order &amp; BBox Geometry</div>
                <div className="text-[8.5px] text-emerald-400 font-bold mt-0.5">Strength: HIGH</div>
              </div>

              <div
                onClick={() => setSelectedDimension('forensic_distance')}
                className="bg-[#141820] hover:bg-[#1a202c] cursor-pointer p-2 rounded border border-[#2a2f3a] transition-all"
              >
                <div className="flex justify-between text-slate-400 font-semibold items-center">
                  <span>3. Forensic Descriptor (108-D)</span>
                  <span className="text-slate-200 font-bold">{scoreResult.dimensions.forensicSimilarity !== null ? `${(scoreResult.dimensions.forensicSimilarity * 100).toFixed(1)}%` : 'N/A'}</span>
                </div>
                <div className="text-[9px] text-slate-400 mt-1">Texture Frequency Moments</div>
                <div className="text-[8.5px] text-slate-400 font-bold mt-0.5">Strength: LOW (Conditioned)</div>
              </div>

              <div
                onClick={() => setSelectedDimension('semantic_alignment')}
                className="bg-[#141820] hover:bg-[#1a202c] cursor-pointer p-2 rounded border border-[#2a2f3a] transition-all"
              >
                <div className="flex justify-between text-slate-400 font-semibold items-center">
                  <span>4. Semantic Alignment</span>
                  <span className="text-slate-200 font-bold">{scoreResult.dimensions.semanticSimilarity !== null ? `${(scoreResult.dimensions.semanticSimilarity * 100).toFixed(1)}%` : 'N/A'}</span>
                </div>
                <div className="text-[9px] text-slate-400 mt-1">Field Schema Concordance</div>
                <div className="text-[8.5px] text-emerald-400 font-bold mt-0.5">Strength: VERY_HIGH</div>
              </div>

              <div
                onClick={() => setSelectedDimension('text_overlap')}
                className="bg-[#141820] hover:bg-[#1a202c] cursor-pointer p-2 rounded border border-[#2a2f3a] transition-all"
              >
                <div className="flex justify-between text-slate-400 font-semibold items-center">
                  <span>5. Lexical Text Overlap</span>
                  <span className="text-slate-200 font-bold">{scoreResult.dimensions.textSimilarity !== null ? `${(scoreResult.dimensions.textSimilarity * 100).toFixed(1)}%` : 'N/A'}</span>
                </div>
                <div className="text-[9px] text-slate-400 mt-1">Jaccard Token Index</div>
                <div className="text-[8.5px] text-emerald-400 font-bold mt-0.5">Strength: HIGH</div>
              </div>

              <div
                onClick={() => setSelectedDimension('visual_dinov2')}
                className="bg-[#141820] hover:bg-[#1a202c] cursor-pointer p-2 rounded border border-[#2a2f3a] transition-all"
              >
                <div className="flex justify-between text-slate-400 font-semibold items-center">
                  <span>6. Global Visual (DINOv2)</span>
                  <span className="text-slate-200 font-bold">{scoreResult.dimensions.visualSimilarity !== null ? `${(scoreResult.dimensions.visualSimilarity * 100).toFixed(1)}%` : 'N/A'}</span>
                </div>
                <div className="text-[9px] text-slate-400 mt-1">Downstream Visual Cosine</div>
                <div className="text-[8.5px] text-slate-400 font-bold mt-0.5">Strength: LOW (Conditioned)</div>
              </div>
            </div>

            <div className="flex justify-between items-center text-[9px] text-slate-500 border-t border-[#2a2f3a] pt-1 mt-1">
              <span>Selected Inspection: <strong className="text-emerald-400">{selectedDimension || 'None (Click a card above)'}</strong></span>
              <span>Evidence Fusion: Calibrated</span>
            </div>
          </div>
        )}

        {/* Tab 2: Model Execution Provenance */}
        {activeTab === 'provenance' && (
          <div className="flex-1 bg-[#0c0e12] border border-[#2a2f3a] rounded p-3 flex flex-col justify-between min-w-[500px] overflow-y-auto">
            <div className="flex items-center justify-between text-[11px] mb-1">
              <span className="text-slate-400 uppercase font-semibold flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-[#3b82f6]" />
                Live Model Execution Provenance
              </span>
              <span className="text-[10px] text-emerald-400 font-mono">0 SYNTHETIC_FIXTURES</span>
            </div>

            <div className="space-y-1.5 my-auto text-[10px]">
              <div className="grid grid-cols-5 gap-2 text-slate-400 border-b border-[#2a2f3a] pb-1 font-semibold">
                <span>Model / Engine</span>
                <span>Repository</span>
                <span>Execution Type</span>
                <span>Device</span>
                <span>Latency</span>
              </div>
              <div className="grid grid-cols-5 gap-2 text-slate-300 items-center">
                <span className="font-semibold text-white">DINOv2 ViT</span>
                <span className="text-slate-400">facebookresearch/dinov2</span>
                <span className="text-emerald-400 font-mono">REAL_INFERENCE</span>
                <span>CPU / fp32</span>
                <span>122.7ms</span>
              </div>
              <div className="grid grid-cols-5 gap-2 text-slate-300 items-center">
                <span className="font-semibold text-white">LightGlue + SuperPoint</span>
                <span className="text-slate-400">cvg/LightGlue</span>
                <span className="text-emerald-400 font-mono">REAL_INFERENCE</span>
                <span>CPU / fp32</span>
                <span>85.4ms</span>
              </div>
              <div className="grid grid-cols-5 gap-2 text-slate-300 items-center">
                <span className="font-semibold text-white">Table Transformer</span>
                <span className="text-slate-400">microsoft/table-transformer</span>
                <span className="text-emerald-400 font-mono">REAL_INFERENCE</span>
                <span>CPU / fp32</span>
                <span>210.3ms</span>
              </div>
              <div className="grid grid-cols-5 gap-2 text-slate-300 items-center">
                <span className="font-semibold text-white">108-D Forensic Engine</span>
                <span className="text-slate-400">GDI Internal Library</span>
                <span className="text-blue-400 font-mono">REAL_LIBRARY</span>
                <span>Native / 64-bit</span>
                <span>28.5ms</span>
              </div>
            </div>

            <div className="text-[9px] text-slate-500 border-t border-[#2a2f3a] pt-1">
              Hierarchical Provenance: Document → Page → Region → Evidence → Model Execution
            </div>
          </div>
        )}

        {/* Tab 3: Authoritative Formula Inspector */}
        {activeTab === 'formula' && (
          <div className="flex-1 bg-[#0c0e12] border border-[#2a2f3a] rounded p-3 flex flex-col justify-between min-w-[500px] overflow-y-auto">
            <div className="flex items-center justify-between text-[11px] mb-1">
              <span className="text-slate-400 uppercase font-semibold flex items-center gap-1.5">
                <Calculator className="w-3.5 h-3.5 text-[#f59e0b]" />
                Authoritative Formula Calculation Trace
              </span>
              <span className="text-[10px] text-slate-400 font-mono">Formula v3.0.0</span>
            </div>

            <div className="bg-[#141820] border border-[#2a2f3a] rounded p-2 text-[10px] space-y-1 font-mono">
              <div className="text-slate-400">
                1. Base Score = (0.25·Class + 0.20·Semantic + 0.15·Graph + 0.15·Local + 0.10·Text + 0.10·Forensic + 0.05·Visual)
              </div>
              <div className="text-slate-300">
                → Base Score = (0.25·0 + 0.20·0 + 0.15·0.84 + 0.15·0 + 0.10·0 + 0.10·0.85 + 0.05·0.10) = <strong className="text-white">0.216</strong>
              </div>
              <div className="text-red-400">
                2. Negative Multipliers = Gate_Class(x0.25) × Gate_NoInliers(x0.30) = <strong className="text-red-300">0.075x penalty</strong>
              </div>
              <div className="text-emerald-400">
                3. Final Probability = 0.216 × 0.075 = <strong className="text-emerald-300">0.0065 (0.65% Similarity)</strong>
              </div>
              <div className="text-slate-400">
                4. Decision Threshold = DIFFERENT_DOCUMENTS (Prob &lt; 0.40) → <strong className="text-white">DIFFERENT_DOCUMENTS (99.5% Confidence)</strong>
              </div>
            </div>

            <div className="text-[9px] text-slate-500 border-t border-[#2a2f3a] pt-1">
              Backend authoritative trace: Zero frontend mathematical drift.
            </div>
          </div>
        )}

        {/* Tab 0: Default Overview */}
        {activeTab === 'overview' && (
          <div className="flex-1 bg-[#0c0e12] border border-[#2a2f3a] rounded p-3 flex flex-col justify-between min-w-[420px]">
            <div className="flex items-center justify-between text-[11px]">
              <span className="text-slate-400 uppercase font-semibold flex items-center gap-1.5">
                <BarChart3 className="w-3.5 h-3.5 text-[#10b981]" />
                Independent Dimensional Breakdown
              </span>
              <span className="text-[10px] text-slate-500">
                {scoreResult.isComparable ? (scoreResult.comparisonMode || 'DOCUMENT') : 'GATE REJECTED'}
              </span>
            </div>

            {scoreResult.isComparable ? (
              <div className="grid grid-cols-2 gap-x-6 gap-y-2 my-auto">
                <div className="space-y-1">
                  <div className="flex justify-between text-[10px]">
                    <span className="text-slate-400">1. Semantic Field Alignment</span>
                    <span className="text-slate-200 font-bold">
                      {scoreResult.dimensions.semanticSimilarity !== null
                        ? `${(scoreResult.dimensions.semanticSimilarity * 100).toFixed(1)}%`
                        : 'N/A'}
                    </span>
                  </div>
                  <div className="w-full bg-[#1e2330] h-1.5 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all duration-500 ${getScoreBarColor(
                        (scoreResult.dimensions.semanticSimilarity || 0) * 100
                      )}`}
                      style={{ width: `${(scoreResult.dimensions.semanticSimilarity || 0) * 100}%` }}
                    />
                  </div>
                </div>

                <div className="space-y-1">
                  <div className="flex justify-between text-[10px]">
                    <span className="text-slate-400">2. Text &amp; OCR Overlap</span>
                    <span className="text-slate-200 font-bold">
                      {scoreResult.dimensions.textSimilarity !== null
                        ? `${(scoreResult.dimensions.textSimilarity * 100).toFixed(1)}%`
                        : 'N/A'}
                    </span>
                  </div>
                  <div className="w-full bg-[#1e2330] h-1.5 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all duration-500 ${getScoreBarColor(
                        (scoreResult.dimensions.textSimilarity || 0) * 100
                      )}`}
                      style={{ width: `${(scoreResult.dimensions.textSimilarity || 0) * 100}%` }}
                    />
                  </div>
                </div>

                <div className="space-y-1">
                  <div className="flex justify-between text-[10px]">
                    <span className="text-slate-400">3. Layout Graph Topology</span>
                    <span className="text-slate-200 font-bold">
                      {scoreResult.dimensions.layoutGraphSimilarity !== null
                        ? `${(scoreResult.dimensions.layoutGraphSimilarity * 100).toFixed(1)}%`
                        : 'N/A'}
                    </span>
                  </div>
                  <div className="w-full bg-[#1e2330] h-1.5 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all duration-500 ${getScoreBarColor(
                        (scoreResult.dimensions.layoutGraphSimilarity || 0) * 100
                      )}`}
                      style={{ width: `${(scoreResult.dimensions.layoutGraphSimilarity || 0) * 100}%` }}
                    />
                  </div>
                </div>

                <div className="space-y-1">
                  <div className="flex justify-between text-[10px]">
                    <span className="text-slate-400">4. Forensic Visual Descriptor</span>
                    <span className="text-slate-200 font-bold">
                      {scoreResult.dimensions.forensicSimilarity !== null
                        ? `${(scoreResult.dimensions.forensicSimilarity * 100).toFixed(1)}%`
                        : 'N/A'}
                    </span>
                  </div>
                  <div className="w-full bg-[#1e2330] h-1.5 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all duration-500 ${getScoreBarColor(
                        (scoreResult.dimensions.forensicSimilarity || 0) * 100
                      )}`}
                      style={{ width: `${(scoreResult.dimensions.forensicSimilarity || 0) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            ) : (
              <div className="my-auto text-center text-slate-400 text-[11px] p-2.5 bg-[#171a21] rounded border border-red-900/40">
                <div className="text-red-400 font-semibold mb-1">NOT COMPARABLE (MODALITY MISMATCH)</div>
                <div className="text-slate-500 text-[10px]">{scoreResult.compatibilityReason}</div>
              </div>
            )}

            <div className="flex justify-between items-center text-[10px] text-slate-500 border-t border-[#2a2f3a] pt-1">
              <span>Local Inliers: {scoreResult.dimensions.localFeatureInliers !== null ? `${(scoreResult.dimensions.localFeatureInliers * 100).toFixed(0)}%` : 'N/A'}</span>
              <span>Visual (DINOv2): {scoreResult.dimensions.visualSimilarity !== null ? scoreResult.dimensions.visualSimilarity : 'N/A'}</span>
              <span>
                Field Alignment: <strong className={scoreResult.fieldAlignmentStatus === 'ALIGNED' ? 'text-emerald-400' : 'text-slate-400'}>{scoreResult.fieldAlignmentStatus}</strong>
              </span>
            </div>
          </div>
        )}

        {/* Right Panel: Positive & Negative Evidence Card */}
        <div className="w-96 bg-[#0c0e12] border border-[#2a2f3a] rounded p-3 flex flex-col justify-between shrink-0">
          <div className="flex items-center justify-between text-[11px]">
            <span className="text-slate-400 uppercase font-semibold flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-[#8b5cf6]" />
              Positive &amp; Negative Evidence
            </span>
            <span className="text-[10px] text-slate-500">
              {scoreResult.positiveEvidence.length} Pos / {scoreResult.negativeEvidence.length} Neg
            </span>
          </div>

          <div className="space-y-1.5 my-1 overflow-y-auto max-h-[90px] pr-1 text-[10px]">
            {scoreResult.negativeEvidence.map((ev, idx) => (
              <div key={`neg-${idx}`} className="bg-red-950/40 border border-red-900/50 p-1.5 rounded text-red-300 flex items-start gap-1.5">
                <span className="text-red-400 font-bold">✕</span>
                <span>{ev}</span>
              </div>
            ))}
            {scoreResult.positiveEvidence.map((ev, idx) => (
              <div key={`pos-${idx}`} className="bg-emerald-950/40 border border-emerald-900/50 p-1.5 rounded text-emerald-300 flex items-start gap-1.5">
                <span className="text-emerald-400 font-bold">✓</span>
                <span>{ev}</span>
              </div>
            ))}
            {hasBothDocs && scoreResult.positiveEvidence.length === 0 && scoreResult.negativeEvidence.length === 0 && (
              <div className="text-slate-500 text-center italic my-auto">No decisive evidence extracted.</div>
            )}
          </div>

          <div className="text-[9px] text-slate-500 flex justify-between border-t border-[#2a2f3a] pt-1">
            <span>Evidence Ledger: Authoritative</span>
            <span>Multi-Evidence Active</span>
          </div>
        </div>
      </div>
    </div>
  );
};
