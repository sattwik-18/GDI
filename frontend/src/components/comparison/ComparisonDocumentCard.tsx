'use client';

import React, { useRef, useState, useEffect } from 'react';
import {
  Upload,
  FileCheck,
  ZoomIn,
  ZoomOut,
  Maximize2,
  FileText,
  Loader2,
  ChevronLeft,
  ChevronRight,
  Shield,
  Layers,
  Sparkles,
  AlertCircle
} from 'lucide-react';
import { GenomeResponse } from '@/types/gdi';

interface ComparisonDocumentCardProps {
  title: string;
  role: 'primary' | 'secondary';
  genome: GenomeResponse | null;
  file: File | null;
  isProcessing: boolean;
  errorMessage: string | null;
  onUpload: (file: File) => void;
  recentGenomes: GenomeResponse[];
  onSelectRecent?: (genome: GenomeResponse) => void;
}

export const ComparisonDocumentCard: React.FC<ComparisonDocumentCardProps> = ({
  title,
  role,
  genome,
  file,
  isProcessing,
  errorMessage,
  onUpload,
  recentGenomes,
  onSelectRecent,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const pdfCanvasRef = useRef<HTMLCanvasElement>(null);
  const [zoom, setZoom] = useState(100);
  const [pdfPage, setPdfPage] = useState(1);
  const [pdfNumPages, setPdfNumPages] = useState(1);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isPdf, setIsPdf] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  const isPrimary = role === 'primary';
  const accentColor = isPrimary ? '#3b82f6' : '#10b981';
  const badgeBg = isPrimary ? 'bg-[#3b82f6]/20 text-[#3b82f6]' : 'bg-[#10b981]/20 text-[#10b981]';

  // Handle preview object URL creation
  useEffect(() => {
    if (!file) {
      setPreviewUrl(null);
      setIsPdf(false);
      return;
    }

    const checkPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
    setIsPdf(checkPdf);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);

    return () => URL.revokeObjectURL(url);
  }, [file]);

  // Render PDF using pdfjs-dist if file is PDF
  useEffect(() => {
    if (!isPdf || !file || !previewUrl) return;

    let isCancelled = false;

    const renderPdf = async () => {
      try {
        const pdfjsLib = await import('pdfjs-dist');
        pdfjsLib.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjsLib.version}/build/pdf.worker.min.mjs`;

        const buffer = await file.arrayBuffer();
        if (isCancelled) return;

        const pdfDoc = await pdfjsLib.getDocument({ data: new Uint8Array(buffer) }).promise;
        if (isCancelled) return;

        setPdfNumPages(pdfDoc.numPages);
        const page = await pdfDoc.getPage(pdfPage);
        if (isCancelled) return;

        const viewport = page.getViewport({ scale: 1.5 });
        const canvas = pdfCanvasRef.current;
        if (canvas) {
          canvas.width = viewport.width;
          canvas.height = viewport.height;
          const ctx = canvas.getContext('2d');
          if (ctx) {
            ctx.imageSmoothingEnabled = true;
            ctx.imageSmoothingQuality = 'high';
            await page.render({ canvasContext: ctx, viewport, canvas }).promise;
          }
        }
      } catch (e) {
        console.warn('Comparison PDF preview fallback:', e);
      }
    };

    renderPdf();

    return () => {
      isCancelled = true;
    };
  }, [isPdf, file, previewUrl, pdfPage]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) onUpload(f);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const f = e.dataTransfer.files?.[0];
    if (f) onUpload(f);
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-[#12151b] border border-[#2a2f3a] rounded-[2px]">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept=".pdf,.png,.jpg,.jpeg,.tiff,.bmp,.webp"
        className="hidden"
      />

      {/* Card Header */}
      <div className="h-10 bg-[#171a21] border-b border-[#2a2f3a] px-3 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <FileCheck className="w-4 h-4" style={{ color: accentColor }} />
          <span className="font-bold text-slate-200 text-xs tracking-wide">{title}</span>
        </div>

        <div className="flex items-center gap-2">
          {genome ? (
            <span className={`text-[10px] px-2 py-0.5 rounded font-mono font-semibold ${badgeBg}`}>
              {genome.genome_id.substring(0, 10)}...
            </span>
          ) : (
            <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded font-mono">
              NO DOCUMENT
            </span>
          )}

          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center gap-1 bg-[#242936] hover:bg-[#2e3547] text-slate-200 px-2 py-1 rounded text-[11px] font-mono transition-colors border border-[#3b4252]"
            title="Upload new file for this slot"
          >
            <Upload className="w-3 h-3 text-slate-300" />
            <span>{genome ? 'Replace' : 'Upload'}</span>
          </button>
        </div>
      </div>

      {/* Card Body */}
      <div className="flex-1 flex flex-col overflow-hidden relative">
        {/* Processing Overlay */}
        {isProcessing && (
          <div className="absolute inset-0 bg-[#0f1115]/90 backdrop-blur-sm z-30 flex flex-col items-center justify-center space-y-3">
            <Loader2 className="w-8 h-8 animate-spin" style={{ color: accentColor }} />
            <div className="text-xs font-mono text-slate-200">
              Extracting 108 Feature Vector & OCR Genome...
            </div>
            <div className="text-[11px] font-mono text-slate-400">
              Deterministic 16-stage pipeline executing
            </div>
          </div>
        )}

        {/* Error Alert */}
        {errorMessage && (
          <div className="bg-[#ef4444]/20 border-b border-[#ef4444]/40 p-2 text-[#ef4444] text-[11px] font-mono flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span className="truncate">{errorMessage}</span>
          </div>
        )}

        {genome ? (
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Visual Canvas Area */}
            <div
              className="flex-1 bg-[#090b0e] overflow-auto p-4 flex items-center justify-center relative select-none"
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
            >
              {previewUrl ? (
                isPdf ? (
                  <div
                    className="shadow-2xl border border-[#2a2f3a] bg-white transition-transform origin-center"
                    style={{ transform: `scale(${zoom / 100})` }}
                  >
                    <canvas ref={pdfCanvasRef} className="max-w-full max-h-full block" />
                  </div>
                ) : (
                  <div
                    className="shadow-2xl border border-[#2a2f3a] bg-white transition-transform origin-center"
                    style={{ transform: `scale(${zoom / 100})` }}
                  >
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={previewUrl}
                      alt={file?.name || 'Document'}
                      className="max-h-[380px] object-contain block"
                    />
                  </div>
                )
              ) : (
                <div className="text-center p-6 space-y-3 max-w-sm">
                  <FileText className="w-12 h-12 mx-auto text-slate-600" />
                  <div className="text-xs font-bold text-slate-300">
                    {genome.genome_id.substring(0, 16)}...
                  </div>
                  <div className="text-[11px] text-slate-500 font-mono">
                    Genome cached in active session. Upload raw file to view visual canvas.
                  </div>
                </div>
              )}

              {/* Zoom & Page Controls Floating Bar */}
              <div className="absolute bottom-3 left-1/2 -translate-x-1/2 bg-[#171a21]/90 backdrop-blur border border-[#2a2f3a] px-3 py-1 rounded-full flex items-center gap-3 text-slate-300 text-[11px] font-mono z-20">
                {isPdf && pdfNumPages > 1 && (
                  <div className="flex items-center gap-1 border-r border-[#2a2f3a] pr-2">
                    <button
                      disabled={pdfPage <= 1}
                      onClick={() => setPdfPage((p) => Math.max(1, p - 1))}
                      className="hover:text-white disabled:opacity-30"
                    >
                      <ChevronLeft className="w-3.5 h-3.5" />
                    </button>
                    <span>{pdfPage}/{pdfNumPages}</span>
                    <button
                      disabled={pdfPage >= pdfNumPages}
                      onClick={() => setPdfPage((p) => Math.min(pdfNumPages, p + 1))}
                      className="hover:text-white disabled:opacity-30"
                    >
                      <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                )}
                <div className="flex items-center gap-1.5">
                  <button onClick={() => setZoom((z) => Math.max(25, z - 20))} className="hover:text-white">
                    <ZoomOut className="w-3.5 h-3.5" />
                  </button>
                  <span className="w-10 text-center">{zoom}%</span>
                  <button onClick={() => setZoom((z) => Math.min(250, z + 20))} className="hover:text-white">
                    <ZoomIn className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>

            {/* Quick Metadata Bar */}
            <div className="bg-[#171a21] border-t border-[#2a2f3a] p-3 space-y-2 text-xs font-mono">
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-slate-400">Document SHA-256:</span>
                <span className="text-slate-200 font-bold truncate max-w-[200px]" title={genome.document_hash_sha256}>
                  {genome.document_hash_sha256 ? `${genome.document_hash_sha256.substring(0, 16)}...` : 'N/A'}
                </span>
              </div>
              <div className="grid grid-cols-3 gap-2 text-[10px]">
                <div className="bg-[#0f1115] p-1.5 rounded border border-[#2a2f3a]">
                  <span className="text-slate-500 block">Pages:</span>
                  <span className="text-slate-200 font-bold">{genome.page_count || 1}</span>
                </div>
                <div className="bg-[#0f1115] p-1.5 rounded border border-[#2a2f3a]">
                  <span className="text-slate-500 block">Features:</span>
                  <span className="text-slate-200 font-bold">{genome.feature_vector?.length || 108}</span>
                </div>
                <div className="bg-[#0f1115] p-1.5 rounded border border-[#2a2f3a]">
                  <span className="text-slate-500 block">Duration:</span>
                  <span className="text-[#10b981] font-bold">{genome.processing_duration_ms.toFixed(0)}ms</span>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Empty Dropzone State */
          <div
            className={`flex-1 p-6 flex flex-col items-center justify-center text-center space-y-4 border-2 border-dashed m-4 rounded transition-all cursor-pointer ${
              isDragging
                ? 'border-[#3b82f6] bg-[#3b82f6]/10'
                : 'border-[#2a2f3a] hover:border-slate-500 bg-[#0f1115]'
            }`}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="w-14 h-14 rounded-full bg-[#171a21] border border-[#2a2f3a] flex items-center justify-center shadow-lg">
              <Upload className="w-6 h-6" style={{ color: accentColor }} />
            </div>

            <div className="space-y-1">
              <div className="text-sm font-bold text-slate-200 font-mono">
                {isPrimary ? 'Upload Primary Document (Doc A)' : 'Upload Comparison Document (Doc B)'}
              </div>
              <div className="text-xs text-slate-400">
                Drag & drop PDF, PNG, JPG, TIFF or click to browse
              </div>
            </div>

            {/* Quick Pick from Recent Genomes if available */}
            {recentGenomes.length > 0 && onSelectRecent && (
              <div
                className="w-full max-w-xs pt-4 border-t border-[#2a2f3a] text-left"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="text-[10px] font-mono text-slate-500 mb-1.5 uppercase">
                  Or select existing processed document:
                </div>
                <select
                  defaultValue=""
                  onChange={(e) => {
                    const found = recentGenomes.find((g) => g.genome_id === e.target.value);
                    if (found) onSelectRecent(found);
                  }}
                  className="w-full bg-[#171a21] border border-[#2a2f3a] text-slate-200 text-xs rounded p-1.5 font-mono focus:outline-none focus:border-[#3b82f6]"
                >
                  <option value="" disabled>-- Choose recent document --</option>
                  {recentGenomes.map((g) => (
                    <option key={g.genome_id} value={g.genome_id}>
                      {g.genome_id.substring(0, 16)}... ({g.page_count || 1}p)
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
