'use client';

import React, { useRef, useState, useEffect } from 'react';
import { 
  ZoomIn, 
  ZoomOut, 
  RotateCw, 
  Maximize2, 
  Eye, 
  EyeOff, 
  Grid, 
  ChevronLeft,
  ChevronRight,
  Upload,
  MousePointer,
  Hand,
  Scaling,
  Split
} from 'lucide-react';
import { GenomeResponse, DebugInspectionResponse } from '@/types/gdi';

interface DocumentCanvasProps {
  genome: GenomeResponse | null;
  debugData: DebugInspectionResponse | null;
  uploadedFile: File | null;
  zoomLevel: number;
  setZoomLevel: (z: number | ((prev: number) => number)) => void;
  onCursorMove: (pos: { x: number; y: number }) => void;
  highlightedTextIndex: number | null;
}

export const DocumentCanvas: React.FC<DocumentCanvasProps> = ({
  genome,
  debugData,
  uploadedFile,
  zoomLevel,
  setZoomLevel,
  onCursorMove,
  highlightedTextIndex,
}) => {
  const [rotation, setRotation] = useState(0);
  const [showOCROverlay, setShowOCROverlay] = useState(true);
  const [showGrid, setShowGrid] = useState(false);
  const [activeTool, setActiveTool] = useState<'select' | 'hand'>('select');
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isPdf, setIsPdf] = useState(false);
  const [pdfNumPages, setPdfNumPages] = useState(1);
  const [pdfPage, setPdfPage] = useState(1);

  // Resolution dimensions for pixel-perfect relative scaling
  const [docDimensions, setDocDimensions] = useState<{ width: number; height: number }>({ width: 2550, height: 3300 });

  const pdfCanvasRef = useRef<HTMLCanvasElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);

  // Compute canonical backend image resolution
  const canonicalW = genome?.pages?.[0]?.metadata?.width_px || debugData?.rendered_pages?.[0]?.width_px || docDimensions.width || 2550;
  const canonicalH = genome?.pages?.[0]?.metadata?.height_px || debugData?.rendered_pages?.[0]?.height_px || docDimensions.height || 3300;

  // State for hover & badge visibility mode
  const [hoveredBoxIdx, setHoveredBoxIdx] = useState<number | null>(null);
  const [badgeMode, setBadgeMode] = useState<'hover' | 'always' | 'never'>('hover');

  // 1. Handle uploaded file object URL creation & type check
  useEffect(() => {
    if (!uploadedFile) {
      setIsPdf(false);
      setPreviewUrl(null);
      return;
    }

    const checkPdf = uploadedFile.type === 'application/pdf' || uploadedFile.name.toLowerCase().endsWith('.pdf');
    setIsPdf(checkPdf);
    const url = URL.createObjectURL(uploadedFile);
    setPreviewUrl(url);

    return () => URL.revokeObjectURL(url);
  }, [uploadedFile]);

  // 2. Render PDF to canvas when isPdf, uploadedFile, pdfPage or canonicalW changes (guaranteeing canvas ref is mounted)
  useEffect(() => {
    if (!isPdf || !uploadedFile || !previewUrl) return;

    let isCancelled = false;

    const renderPdfPage = async () => {
      try {
        const pdfjsLib = await import('pdfjs-dist');
        pdfjsLib.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjsLib.version}/build/pdf.worker.min.mjs`;

        const arrayBuffer = await uploadedFile.arrayBuffer();
        if (isCancelled) return;

        const pdfDoc = await pdfjsLib.getDocument({ data: new Uint8Array(arrayBuffer) }).promise;
        if (isCancelled) return;
        setPdfNumPages(pdfDoc.numPages);

        const page = await pdfDoc.getPage(pdfPage);
        if (isCancelled) return;

        const unscaledViewport = page.getViewport({ scale: 1.0 });

        // Scale PDF canvas to match 300 DPI backend image width
        const targetW = canonicalW > 0 ? canonicalW : 2550;
        const desiredScale = targetW / unscaledViewport.width;
        const viewport = page.getViewport({ scale: desiredScale });

        setDocDimensions({ width: viewport.width, height: viewport.height });

        const canvas = pdfCanvasRef.current;
        if (canvas) {
          canvas.width = viewport.width;
          canvas.height = viewport.height;
          canvas.style.width = '100%';
          canvas.style.height = '100%';

          const ctx = canvas.getContext('2d');
          if (ctx) {
            ctx.imageSmoothingEnabled = true;
            ctx.imageSmoothingQuality = 'high';
            await page.render({ canvasContext: ctx, viewport, canvas }).promise;
            if (canvas) {
              canvas.style.width = '100%';
              canvas.style.height = '100%';
            }
          }
        }
      } catch (err) {
        console.warn("PDF.js rendering fallback:", err);
      }
    };

    renderPdfPage();

    return () => {
      isCancelled = true;
    };
  }, [isPdf, uploadedFile, previewUrl, pdfPage, canonicalW]);

  // Sync docDimensions when backend metadata arrives
  useEffect(() => {
    const firstPageMeta = genome?.pages?.[0]?.metadata;
    const renderedPageMeta = debugData?.rendered_pages?.[0];

    if (firstPageMeta?.width_px && firstPageMeta?.height_px) {
      setDocDimensions({ width: firstPageMeta.width_px, height: firstPageMeta.height_px });
    } else if (renderedPageMeta?.width_px && renderedPageMeta?.height_px) {
      setDocDimensions({ width: renderedPageMeta.width_px, height: renderedPageMeta.height_px });
    }
  }, [genome, debugData]);

  const handleImageLoad = () => {
    if (imageRef.current) {
      const nw = imageRef.current.naturalWidth;
      const nh = imageRef.current.naturalHeight;
      if (nw > 0 && nh > 0) {
        setDocDimensions({ width: nw, height: nh });
      }
    }
  };

  const handleZoomIn = () => setZoomLevel((z) => Math.min(z + 25, 400));
  const handleZoomOut = () => setZoomLevel((z) => Math.max(z - 25, 25));
  const handleResetZoom = () => setZoomLevel(100);
  const handleRotate = () => setRotation((r) => (r + 90) % 360);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = Math.round((e.clientX - rect.left) * (100 / zoomLevel));
    const y = Math.round((e.clientY - rect.top) * (100 / zoomLevel));
    onCursorMove({ x, y });
  };

  // Compute 100% pixel-accurate percentage coordinates for every bounding box
  const realOCRElements = React.useMemo(() => {
    const rawElements: any[] = [];
    const firstPage = genome?.pages?.[0];

    if (firstPage && Array.isArray(firstPage.ocr_elements) && firstPage.ocr_elements.length > 0) {
      rawElements.push(...firstPage.ocr_elements);
    } else if (debugData && debugData.ocr_results) {
      debugData.ocr_results.forEach((ocrPage) => {
        if (ocrPage.elements) {
          rawElements.push(...ocrPage.elements);
        }
      });
    }

    const elements: Array<{ id: string; text: string; confidence: number; leftPct: number; topPct: number; widthPct: number; heightPct: number }> = [];

    rawElements.forEach((el, idx) => {
      let left = 0, top = 0, width = 0, height = 0;
      if (Array.isArray(el.bbox) && el.bbox.length > 0) {
        const pts = el.bbox.map((pt: any) => (Array.isArray(pt) ? pt : [pt, 0]));
        const xs = pts.map((pt: any) => Number(pt[0]) || 0);
        const ys = pts.map((pt: any) => Number(pt[1]) || 0);
        const minX = Math.min(...xs);
        const maxX = Math.max(...xs);
        const minY = Math.min(...ys);
        const maxY = Math.max(...ys);
        left = minX;
        top = minY;
        width = maxX - minX;
        height = maxY - minY;
      }

      // Use exact 300 DPI image resolution processed by OCR engine
      const imgW = el.img_width || canonicalW;
      const imgH = el.img_height || canonicalH;

      const leftPct = (left / imgW) * 100;
      const topPct = (top / imgH) * 100;
      const widthPct = (width / imgW) * 100;
      const heightPct = (height / imgH) * 100;

      elements.push({
        id: el.id || `ocr_${idx}`,
        text: el.text || '',
        confidence: el.confidence || 0,
        leftPct: Math.max(0, Math.min(100, leftPct)),
        topPct: Math.max(0, Math.min(100, topPct)),
        widthPct: Math.max(0.1, Math.min(100, widthPct)),
        heightPct: Math.max(0.1, Math.min(100, heightPct)),
      });
    });

    return elements;
  }, [genome, debugData, canonicalW, canonicalH]);

  const renderBBoxes = () => {
    return realOCRElements.map((box, idx) => {
      const isSelected = highlightedTextIndex === idx;
      const isHovered = hoveredBoxIdx === idx;
      const shouldShowBadge =
        badgeMode === 'always' ||
        (badgeMode === 'hover' && (isHovered || isSelected));

      return (
        <div
          key={box.id + idx}
          onMouseEnter={() => setHoveredBoxIdx(idx)}
          onMouseLeave={() => setHoveredBoxIdx(null)}
          className={`absolute pointer-events-auto transition-all duration-150 rounded-[1px] ${
            isSelected
              ? 'border-2 border-[#3b82f6] bg-[#3b82f6]/25 z-30 shadow-lg shadow-[#3b82f6]/20'
              : isHovered
              ? 'border-2 border-[#10b981] bg-[#10b981]/20 z-20 shadow-md shadow-[#10b981]/10'
              : 'border border-[#10b981]/30 bg-[#10b981]/[0.03] hover:border-[#10b981]/80 hover:bg-[#10b981]/15'
          }`}
          style={{
            left: `${box.leftPct}%`,
            top: `${box.topPct}%`,
            width: `${box.widthPct}%`,
            height: `${box.heightPct}%`,
          }}
        >
          {shouldShowBadge && (
            <div className="absolute -top-5 left-0 z-40 px-1.5 py-0.5 bg-[#0f1115]/95 text-[#10b981] border border-[#10b981]/40 rounded-[2px] text-[9px] font-mono shadow-xl flex items-center gap-1.5 pointer-events-none whitespace-nowrap">
              <span className="font-bold">{box.confidence}%</span>
              {box.text && (
                <span className="text-slate-200 max-w-[160px] truncate border-l border-slate-700 pl-1.5">
                  {box.text}
                </span>
              )}
            </div>
          )}
        </div>
      );
    });
  };

  return (
    <div className="flex-1 flex flex-col bg-[#0f1115] overflow-hidden select-none relative font-mono text-xs">
      {/* Document Viewer Sub-Header Toolbar */}
      <div className="h-9 bg-[#171a21] border-b border-[#2a2f3a] px-3 flex items-center justify-between z-10 shrink-0">
        {/* Left Toolbar Controls */}
        <div className="flex items-center gap-1.5">
          {/* Select & Hand Tools */}
          <button
            onClick={() => setActiveTool('select')}
            className={`p-1 rounded-[2px] border ${
              activeTool === 'select'
                ? 'bg-[#1f232d] text-slate-100 border-[#3f4756]'
                : 'text-slate-400 hover:text-slate-200 border-transparent hover:bg-[#1f232d]/60'
            }`}
            title="Selection Tool"
          >
            <MousePointer className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setActiveTool('hand')}
            className={`p-1 rounded-[2px] border ${
              activeTool === 'hand'
                ? 'bg-[#1f232d] text-slate-100 border-[#3f4756]'
                : 'text-slate-400 hover:text-slate-200 border-transparent hover:bg-[#1f232d]/60'
            }`}
            title="Hand Pan Tool"
          >
            <Hand className="w-3.5 h-3.5" />
          </button>

          <div className="w-[1px] h-4 bg-[#2a2f3a] mx-1" />

          {/* Zoom Controls */}
          <button
            onClick={handleZoomOut}
            className="p-1 hover:bg-[#1f232d] text-slate-300 rounded-[2px] border border-[#2a2f3a]"
            title="Zoom Out (Ctrl+-)"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <span className="w-12 text-center text-slate-200 text-[11px] font-mono">
            {zoomLevel}%
          </span>
          <button
            onClick={handleZoomIn}
            className="p-1 hover:bg-[#1f232d] text-slate-300 rounded-[2px] border border-[#2a2f3a]"
            title="Zoom In (Ctrl++)"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={handleResetZoom}
            className="p-1 hover:bg-[#1f232d] text-slate-300 rounded-[2px] border border-[#2a2f3a] text-[10px]"
            title="Fit to Page (Ctrl+0)"
          >
            <Maximize2 className="w-3.5 h-3.5" />
          </button>

          <div className="w-[1px] h-4 bg-[#2a2f3a] mx-1" />

          {/* Rotate & Split Controls */}
          <button
            onClick={handleRotate}
            className="p-1 hover:bg-[#1f232d] text-slate-300 rounded-[2px] border border-[#2a2f3a]"
            title="Rotate 90° Right"
          >
            <RotateCw className="w-3.5 h-3.5" />
          </button>

          {/* PDF Page Navigation */}
          <div className="w-[1px] h-4 bg-[#2a2f3a] mx-1" />
          <div className="flex items-center gap-1 text-[11px]">
            <button
              disabled={pdfPage <= 1}
              onClick={() => setPdfPage((p) => Math.max(1, p - 1))}
              className="p-1 hover:bg-[#1f232d] disabled:opacity-30 text-slate-300 rounded-[2px] border border-[#2a2f3a]"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            <span className="text-slate-200 font-mono px-1">
              {pdfPage} / {isPdf ? pdfNumPages : (genome?.page_count || 1)}
            </span>
            <button
              disabled={pdfPage >= (isPdf ? pdfNumPages : (genome?.page_count || 1))}
              onClick={() => setPdfPage((p) => Math.min(isPdf ? pdfNumPages : (genome?.page_count || 1), p + 1))}
              className="p-1 hover:bg-[#1f232d] disabled:opacity-30 text-slate-300 rounded-[2px] border border-[#2a2f3a]"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Right Toolbar Layer Toggles */}
        <div className="flex items-center gap-2">
          {/* Badge Display Mode Toggle */}
          {showOCROverlay && (
            <div className="flex items-center gap-1 bg-[#12151b] p-0.5 border border-[#2a2f3a] rounded-[2px] text-[10px]">
              <span className="text-slate-400 px-1">Badges:</span>
              <button
                onClick={() => setBadgeMode('hover')}
                className={`px-1.5 py-0.5 rounded-[1px] ${
                  badgeMode === 'hover' ? 'bg-[#3b82f6] text-white font-medium' : 'text-slate-400 hover:text-slate-200'
                }`}
                title="Show confidence badges on hover"
              >
                Hover
              </button>
              <button
                onClick={() => setBadgeMode('always')}
                className={`px-1.5 py-0.5 rounded-[1px] ${
                  badgeMode === 'always' ? 'bg-[#3b82f6] text-white font-medium' : 'text-slate-400 hover:text-slate-200'
                }`}
                title="Show all confidence badges"
              >
                All
              </button>
              <button
                onClick={() => setBadgeMode('never')}
                className={`px-1.5 py-0.5 rounded-[1px] ${
                  badgeMode === 'never' ? 'bg-[#3b82f6] text-white font-medium' : 'text-slate-400 hover:text-slate-200'
                }`}
                title="Hide confidence badges"
              >
                Off
              </button>
            </div>
          )}

          <button
            onClick={() => setShowOCROverlay(!showOCROverlay)}
            className={`flex items-center gap-1.5 px-2 py-0.5 rounded-[2px] border text-[10px] transition-colors ${
              showOCROverlay
                ? 'bg-[#1f232d] border-[#3f4756] text-slate-200'
                : 'bg-[#12151b] border-[#2a2f3a] text-slate-400'
            }`}
            title="Toggle Real OCR Bounding Box Overlay Layer"
          >
            {showOCROverlay ? <Eye className="w-3 h-3 text-[#10b981]" /> : <EyeOff className="w-3 h-3 text-slate-500" />}
            <span>OCR BBoxes ({realOCRElements.length})</span>
          </button>

          <button
            onClick={() => setShowGrid(!showGrid)}
            className={`flex items-center gap-1.5 px-2 py-0.5 rounded-[2px] border text-[10px] transition-colors ${
              showGrid
                ? 'bg-[#1f232d] border-[#3f4756] text-slate-200'
                : 'bg-[#12151b] border-[#2a2f3a] text-slate-400'
            }`}
            title="Toggle Measurement Grid"
          >
            <Grid className="w-3 h-3" />
            <span>Grid</span>
          </button>
        </div>
      </div>

      {/* Main Document Viewport Area */}
      <div 
        className="flex-1 overflow-auto p-8 flex items-center justify-center relative canvas-crosshair"
        onMouseMove={handleMouseMove}
      >
        {/* Background Grid Pattern */}
        {showGrid && (
          <div 
            className="absolute inset-0 pointer-events-none opacity-20"
            style={{
              backgroundImage: 'radial-gradient(#3f4756 1px, transparent 1px)',
              backgroundSize: '20px 20px',
            }}
          />
        )}

        {/* 1:1 Tight Document Container Wrapper with High-DPI Anti-Aliasing */}
        <div
          className="relative transition-transform duration-100 shadow-2xl bg-white border border-[#2a2f3a] inline-block"
          style={{
            transform: `scale(${zoomLevel / 100}) rotate(${rotation}deg)`,
            transformOrigin: 'center center',
            width: '800px',
            maxWidth: '100%',
          }}
        >
          {previewUrl ? (
            isPdf ? (
              /* Real PDF Document Preview Render */
              <div className="w-full relative bg-white" style={{ aspectRatio: `${docDimensions.width} / ${docDimensions.height}` }}>
                <canvas
                  ref={pdfCanvasRef}
                  className="w-full h-full block"
                  style={{ imageRendering: 'smooth' }}
                />
                <object
                  data={previewUrl}
                  type="application/pdf"
                  className="w-full h-full absolute inset-0 pointer-events-none opacity-0"
                >
                  <embed src={previewUrl} type="application/pdf" className="w-full h-full" />
                </object>

                {/* REAL Interactive OCR Bounding Box Overlay Layer */}
                {showOCROverlay && realOCRElements.length > 0 && (
                  <div className="absolute inset-0 pointer-events-none overflow-hidden">
                    {renderBBoxes()}
                  </div>
                )}
              </div>
            ) : (
              /* Real Image Document Preview Render */
              <div className="w-full relative bg-white">
                <img
                  ref={imageRef}
                  src={previewUrl}
                  alt="Uploaded Real Document Viewport"
                  onLoad={handleImageLoad}
                  className="w-full h-auto block"
                  style={{ imageRendering: 'smooth' }}
                />

                {/* REAL Interactive OCR Bounding Box Overlay Layer */}
                {showOCROverlay && realOCRElements.length > 0 && (
                  <div className="absolute inset-0 pointer-events-none overflow-hidden">
                    {renderBBoxes()}
                  </div>
                )}
              </div>
            )
          ) : (
            <div className="w-full h-[800px] flex flex-col items-center justify-center p-8 bg-[#f8fafc] text-slate-500 font-mono text-xs text-center">
              <Upload className="w-8 h-8 text-slate-400 mb-2" />
              <span>Select or upload a document to render canvas</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

