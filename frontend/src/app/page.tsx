'use client';

/**
 * GDI Platform v2 - ForensicWorkstationPage
 *
 * Application shell. State is managed by Zustand stores (see src/state/).
 * Health polling has moved to PlatformProvider.
 * This component is now a thin orchestrator: route workspaces, trigger uploads.
 */

import React, { useRef } from 'react';
import { Header } from '@/components/layout/Header';
import { Sidebar } from '@/components/layout/Sidebar';
import { StatusBar } from '@/components/layout/StatusBar';
import { DocumentCanvas } from '@/components/viewer/DocumentCanvas';
import { AnalysisInspector } from '@/components/inspector/AnalysisInspector';
import { PipelineConsole } from '@/components/pipeline/PipelineConsole';
import { ComparisonWorkbench } from '@/components/comparison/ComparisonWorkbench';
import { ManifestExecutionExplorer } from '@/components/manifest/ManifestExecutionExplorer';
import { CommandPalette } from '@/components/command/CommandPalette';
import { GlobalSearchModal } from '@/components/search/GlobalSearchModal';
import { PlatformProvider } from '@/platform/PlatformProvider';
import { GDIClient } from '@/services/api';

import { useSystemStore } from '@/state/system.store';
import { useSessionStore } from '@/state/session.store';
import { useUIStore } from '@/state/ui.store';

import { Upload, FileText, Activity, AlertCircle } from 'lucide-react';

// ---- Inner workstation (consumes stores) ----------------------------------

function ForensicWorkstation() {
  const fileInputRef = useRef<HTMLInputElement>(null);

  // System store
  const { status: backendStatus, isHealthy: isBackendHealthy, latencyMs, cpuPercent, memoryMb } = useSystemStore();

  // Session store
  const {
    activeGenome: currentGenome,
    debugData,
    uploadedFile,
    recentGenomes,
    isProcessing,
    processingError,
    setActiveGenome,
    setUploadedFile,
    setProcessing,
    setError,
    addRecentGenome,
  } = useSessionStore();

  // UI store
  const {
    activeWorkspace,
    isLeftCollapsed,
    isRightCollapsed,
    isCommandPaletteOpen,
    isGlobalSearchOpen,
    zoomLevel,
    cursorPos,
    highlightedTextIndex,
    setActiveWorkspace,
    setLeftCollapsed,
    setRightCollapsed,
    setCommandPaletteOpen,
    setGlobalSearchOpen,
    setZoomLevel,
    setCursorPos,
    setHighlightedTextIndex,
  } = useUIStore();

  const systemMetrics =
    cpuPercent !== undefined || memoryMb !== undefined
      ? { cpuPercent, memoryMb }
      : null;

  const processFile = async (file: File) => {
    setUploadedFile(file);
    setProcessing(true);
    setError(null);

    try {
      const genomeRes = await GDIClient.generateGenome(file);
      setActiveGenome(genomeRes, null);
      addRecentGenome(genomeRes);

      try {
        const debugRes = await GDIClient.inspectDebugPipeline(file);
        setActiveGenome(genomeRes, debugRes);
      } catch (debugErr) {
        console.warn('Pipeline debug inspection bypassed:', debugErr);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to process document');
    } finally {
      setProcessing(false);
    }
  };

  const triggerFileUpload = () => fileInputRef.current?.click();

  return (
    <div className="h-screen w-screen flex flex-col bg-[#0f1115] text-[#e2e8f0] overflow-hidden select-none font-sans">
      <input
        type="file"
        ref={fileInputRef}
        onChange={(e) => { const f = e.target.files?.[0]; if (f) processFile(f); }}
        accept=".pdf,.png,.jpg,.jpeg,.tiff,.bmp,.webp"
        className="hidden"
      />

      <Header
        activeWorkspace={activeWorkspace}
        setActiveWorkspace={setActiveWorkspace}
        isBackendHealthy={isBackendHealthy}
        backendStatus={backendStatus}
        latencyMs={latencyMs}
        onOpenFileUpload={triggerFileUpload}
        onToggleCommandPalette={() => setCommandPaletteOpen(true)}
        onToggleGlobalSearch={() => setGlobalSearchOpen(true)}
        documentName={uploadedFile?.name || (currentGenome ? `genome_${currentGenome.genome_id.substring(0, 8)}` : undefined)}
      />

      {isProcessing && (
        <div className="bg-[#1f232d] border-b border-[#2a2f3a] text-slate-200 font-mono text-[11px] px-4 py-1 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2">
            <Activity className="w-3.5 h-3.5 text-[#3b82f6] animate-spin" />
            <span>Executing 16-Stage Deterministic Document Genome Extraction Pipeline...</span>
          </div>
          <span>PaddleOCR Engine &amp; 108 Feature Vector Extractors Active</span>
        </div>
      )}

      {processingError && (
        <div className="bg-[#ef4444]/20 border-b border-[#ef4444]/40 text-[#ef4444] font-mono text-[11px] px-4 py-1 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>Pipeline Execution Error: {processingError}</span>
          </div>
          <button onClick={() => setError(null)} className="underline hover:text-white">Dismiss</button>
        </div>
      )}

      <div className="flex-1 flex overflow-hidden relative">
        <Sidebar
          currentGenome={currentGenome}
          recentGenomes={recentGenomes}
          onSelectGenome={(g) => setActiveGenome(g, debugData)}
          onOpenFileUpload={triggerFileUpload}
          isCollapsed={isLeftCollapsed}
          onToggleCollapse={() => setLeftCollapsed(!isLeftCollapsed)}
        />

        {activeWorkspace === 'analysis' && (
          <div className="flex-1 flex flex-col overflow-hidden relative">
            <div className="flex-1 flex overflow-hidden">
              <DocumentCanvas
                genome={currentGenome}
                debugData={debugData}
                uploadedFile={uploadedFile}
                zoomLevel={zoomLevel}
                setZoomLevel={setZoomLevel}
                onCursorMove={setCursorPos}
                highlightedTextIndex={highlightedTextIndex}
                onOpenFileUpload={triggerFileUpload}
                onUploadFile={processFile}
              />
              <AnalysisInspector
                genome={currentGenome}
                debugData={debugData}
                uploadedFile={uploadedFile}
                onHoverOCRIndex={setHighlightedTextIndex}
                isCollapsed={isRightCollapsed}
                onToggleCollapse={() => setRightCollapsed(!isRightCollapsed)}
              />
            </div>
            <PipelineConsole genome={currentGenome} />
          </div>
        )}

        {activeWorkspace === 'comparison' && (
          <ComparisonWorkbench primaryGenome={currentGenome} recentGenomes={recentGenomes} />
        )}

        {activeWorkspace === 'manifest' && (
          <ManifestExecutionExplorer genome={currentGenome} />
        )}

        {activeWorkspace === 'datasets' && (
          <div className="flex-1 p-6 font-mono text-xs text-slate-300 overflow-y-auto space-y-4">
            <h2 className="text-sm font-semibold text-slate-100 uppercase tracking-wider">
              Golden Benchmark Corpus &amp; Dataset Manager
            </h2>
            <div className="bg-[#171a21] border border-[#2a2f3a] p-4 rounded-[2px] space-y-3">
              <div className="flex justify-between items-center text-[11px]">
                <span className="font-semibold text-slate-200">Processed Document Ingestion Corpus</span>
                <span className="text-[#10b981] text-[10px]">{recentGenomes.length} Documents Indexed</span>
              </div>
              <div className="divide-y divide-[#2a2f3a]">
                {recentGenomes.map((item, idx) => (
                  <div key={idx} className="py-2 flex items-center justify-between text-[11px]">
                    <div className="flex items-center gap-2">
                      <FileText className="w-3.5 h-3.5 text-[#3b82f6]" />
                      <span className="text-slate-200 font-medium">{item.genome_id}</span>
                    </div>
                    <span className="text-slate-400">{item.processing_duration_ms.toFixed(1)}ms</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeWorkspace === 'reports' && (
          <div className="flex-1 p-6 font-mono text-xs text-slate-300 overflow-y-auto space-y-4">
            <h2 className="text-sm font-semibold text-slate-100 uppercase tracking-wider">
              Forensic Audit Package &amp; Chain of Custody Generator
            </h2>
            {currentGenome ? (
              <div className="bg-[#171a21] border border-[#2a2f3a] p-4 rounded-[2px] space-y-3 max-w-xl">
                <div className="font-semibold text-slate-200">Export Report Package for Genome: {currentGenome.genome_id}</div>
                <div className="space-y-2 text-slate-400 text-[11px]">
                  <div>Document SHA-256: <span className="text-slate-200">{currentGenome.document_hash_sha256}</span></div>
                  <div>Cryptographic Seal: <span className="text-[#10b981]">{currentGenome.genome_seal.sha256_of_features}</span></div>
                  <div>Canonical Vector Dimensions: <span className="text-slate-200">{currentGenome.genome_seal.feature_count} Features</span></div>
                </div>
                <button
                  onClick={() => alert(`Report generated for Genome ${currentGenome.genome_id}`)}
                  className="bg-[#3b82f6] hover:bg-[#2563eb] text-white px-3 py-1 rounded-[2px] font-medium text-[11px] transition-colors"
                >
                  Generate Audit Package (PDF)
                </button>
              </div>
            ) : (
              <div className="text-slate-500 italic p-4">No active document loaded. Upload a document to generate a forensic audit report.</div>
            )}
          </div>
        )}

        {activeWorkspace === 'settings' && (
          <div className="flex-1 p-6 font-mono text-xs text-slate-300 overflow-y-auto space-y-4">
            <h2 className="text-sm font-semibold text-slate-100 uppercase tracking-wider">
              System Settings & OCR Engine Configuration
            </h2>
            <div className="bg-[#171a21] border border-[#2a2f3a] p-4 rounded-[2px] space-y-4 max-w-xl">
              <div>
                <label className="block text-slate-400 mb-1">Primary OCR Engine</label>
                <input type="text" readOnly value="PaddleOCR 2.7.3 (production_deterministic)"
                  className="w-full bg-[#0f1115] border border-[#2a2f3a] p-2 rounded-[2px] text-slate-200" />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Database Mode</label>
                <input type="text" readOnly value="DATABASE_OPTIONAL=true (Graceful Local Disk Fallback)"
                  className="w-full bg-[#0f1115] border border-[#2a2f3a] p-2 rounded-[2px] text-[#10b981]" />
              </div>
            </div>
          </div>
        )}
      </div>

      <StatusBar
        genome={currentGenome}
        isBackendHealthy={isBackendHealthy}
        zoomLevel={zoomLevel}
        cursorPos={cursorPos}
        latencyMs={latencyMs}
        systemMetrics={systemMetrics}
      />

      <CommandPalette
        isOpen={isCommandPaletteOpen}
        onClose={() => setCommandPaletteOpen(false)}
        setActiveWorkspace={setActiveWorkspace}
        onOpenFileUpload={triggerFileUpload}
      />

      <GlobalSearchModal
        isOpen={isGlobalSearchOpen}
        onClose={() => setGlobalSearchOpen(false)}
        genome={currentGenome}
      />
    </div>
  );
}

// ---- Page export: wrapped with PlatformProvider --------------------------

export default function ForensicWorkstationPage() {
  return (
    <PlatformProvider>
      <ForensicWorkstation />
    </PlatformProvider>
  );
}
