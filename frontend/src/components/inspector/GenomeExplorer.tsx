'use client';

import React, { useState, useMemo, useCallback, useRef, useEffect } from 'react';
import {
  ChevronRight, ChevronDown, Search, Bookmark, BookmarkCheck,
  Copy, Check, X, Code2, FlaskConical, User, ArrowLeft,
  AlertTriangle, Info, Target, Filter, Link, FileText
} from 'lucide-react';
import { GenomeResponse, DebugInspectionResponse } from '@/types/gdi';

// ─────────────────────────────────────────────────────────────
// TYPES
// ─────────────────────────────────────────────────────────────

import type {
  EvidenceDomain,
  EvidenceStatus,
  ForensicImportance,
  VizType,
  DeterminismLevel,
  InspectorMode,
  EvidenceDef,
  EvidenceDomainDef,
} from '@/core/domain/types';
import { GENOME_REGISTRY } from '@/core/registry/GenomeRegistry';

// HELPERS
// ─────────────────────────────────────────────────────────────

/**
 * Build a flat key→value map from genome.pages[0].feature_groups.
 * The genome assembler stores all extracted features here by their actual key names.
 */
function buildFeatureMap(genome: GenomeResponse | null): Record<string, number> {
  const map: Record<string, number> = {};
  const fgs = genome?.pages?.[0]?.feature_groups;
  if (!fgs) return map;
  for (const fg of fgs) {
    if (fg.features) {
      for (const [k, v] of Object.entries(fg.features)) {
        if (typeof v === 'number') map[k] = v;
      }
    }
  }
  return map;
}

const FEATURE_KEY_ALIASES: Record<string, string[]> = {
  // Geometry
  'geo_total_pixels': ['p1_edge_canny_edge_count', 'p1_geom_width_px'],
  'geo_ink_coverage': ['p1_edge_canny_edge_density'],
  'geo_content_density': ['p1_stat_variance'],
  'geo_whitespace_ratio': ['p1_stat_mean'],
  'geo_noise_level': ['p1_edge_sobel_std'],
  'geo_ocr_element_count': ['p1_ocr_element_count', 'p1_geom_bbox_count'],

  // OCR
  'ocr_mean_confidence': ['p1_ocr_mean_confidence'],
  'ocr_max_bbox_area': ['p1_geom_mean_bbox_width'],
  'ocr_word_density': ['p1_ocr_word_count', 'p1_ocr_text_density'],
  'ocr_line_count': ['p1_ocr_line_count'],

  // Typography
  'typo_char_height_mean': ['p1_geom_mean_bbox_height'],
  'typo_char_width_mean': ['p1_geom_mean_bbox_width'],

  // Texture
  'tex_glcm_contrast': ['p1_tex_glcm_contrast'],
  'tex_glcm_energy': ['p1_tex_glcm_energy'],
  'tex_glcm_homogeneity': ['p1_tex_glcm_homogeneity'],
  'tex_glcm_correlation': ['p1_tex_glcm_correlation'],

  // Frequency
  'freq_fft_mean': ['p1_freq_fft_mean'],
  'freq_fft_std': ['p1_freq_fft_std'],
  'freq_dct_energy': ['p1_freq_dct_energy_concentration'],

  // Statistics
  'stat_mean_intensity': ['p1_stat_mean'],
  'stat_std_intensity': ['p1_stat_std'],
  'stat_skewness': ['p1_stat_skewness'],
  'stat_kurtosis': ['p1_stat_kurtosis'],
  'stat_shannon_entropy': ['p1_stat_shannon_entropy'],
};

function getValueFromGenome(
  def: EvidenceDef,
  genome: GenomeResponse | null,
  debugData: DebugInspectionResponse | null,
  featureMap?: Record<string, number>
): number | string | null {
  const page0 = genome?.pages?.[0];
  const quality = page0?.quality_metrics || debugData?.page_quality_reports?.[0] || null;
  const pageMeta = page0?.metadata || null;

  // 1. Well-known top-level fields (not in feature_groups)
  switch (def.id) {
    case 'meta_sharpness': return quality?.sharpness_score ?? null;
    case 'meta_contrast': return quality?.contrast_score ?? null;
    case 'meta_noise': return quality?.noise_score ?? null;
    case 'meta_skew_angle': return pageMeta?.skew_angle_deg ?? null;
    case 'meta_dpi': return pageMeta?.dpi ?? null;
    case 'sec_document_hash': return genome?.document_hash_sha256 ?? null;
    case 'sec_genome_seal': return genome?.genome_seal?.sha256_of_features ?? null;
    case 'layout_region_count': return page0?.layout_region_count ?? debugData?.layout_results?.[0]?.region_count ?? null;
    case 'layout_reading_order_len': return debugData?.layout_results?.[0]?.reading_order_len ?? null;
  }

  const fm = featureMap ?? buildFeatureMap(genome);

  // 2. Direct featureKey lookup
  if (def.featureKey && fm[def.featureKey] !== undefined) {
    return fm[def.featureKey];
  }

  // 3. Direct ID lookup in fm
  if (fm[def.id] !== undefined) {
    return fm[def.id];
  }

  // 4. Known Aliases lookup
  const aliases = FEATURE_KEY_ALIASES[def.id];
  if (aliases) {
    for (const alias of aliases) {
      if (fm[alias] !== undefined) {
        return fm[alias];
      }
    }
  }

  // 5. Substring / suffix match fallback
  const strippedId = def.id.replace(/^(geo|ocr|typo|tex|freq|stat|meta|sec|layout)_/, '');
  for (const [k, v] of Object.entries(fm)) {
    if (k.endsWith(strippedId) || k.includes(strippedId)) {
      return v;
    }
  }

  // 6. Fallback to raw feature_vector array by index if available
  const vec = page0?.feature_vector || (genome as any)?.feature_vector;
  if (Array.isArray(vec) && def.vectorIndex !== undefined && def.vectorIndex < vec.length) {
    const v = vec[def.vectorIndex];
    if (typeof v === 'number' && !isNaN(v)) return v;
  }

  return null;
}



/**
 * Determine whether a score-unit value is already in percent scale (0–100)
 * vs fractional scale (0–1), using the evidence's typicalRange as the signal.
 */
function isPercentScale(def: EvidenceDef): boolean {
  if (!def.typicalRange) return false;
  return def.typicalRange[1] > 1.5; // e.g. [80, 100] → percent scale
}

/**
 * Format a single range bound (lo or hi of typicalRange) using the
 * same unit-aware logic as formatValue — so ranges display in the
 * same units as the value itself.
 */
function formatRangeBound(n: number, def: EvidenceDef): string {
  if (def.unit === 'degrees') return `${n}\u00b0`;
  if (def.unit === 'ratio') return n.toFixed(3);
  if (def.unit === 'score' || def.unit.startsWith('score')) {
    if (isPercentScale(def)) return `${n}%`;
    // Fractional score: display as percent
    return `${(n * 100).toFixed(0)}%`;
  }
  if (['px\u00b2', 'px', 'DPI', 'count', 'lines', 'regions', 'elements', 'words/cm\u00b2'].includes(def.unit))
    return Math.round(n).toLocaleString();
  // For small floats, show 3 decimals; for large numbers, show integers
  return Math.abs(n) >= 10 ? Math.round(n).toLocaleString() : n.toFixed(3);
}

/**
 * Detect whether a numeric value is clearly outside plausible bounds.
 * Used to show a warning indicator instead of a nonsensical formatted string.
 */
function isValueImpossible(val: number | string | null, def: EvidenceDef): boolean {
  if (val === null || typeof val === 'string') return false;
  const n = val as number;
  // Score units: must be 0–100 (percent scale) or 0–1 (fractional scale)
  if (def.unit === 'score' || def.unit.startsWith('score')) {
    const maxExpected = isPercentScale(def) ? 100 : 1.0;
    if (n < 0 || n > maxExpected * 1.05) return true; // 5% tolerance for float precision
  }
  // Ratio units: must be 0–1
  if (def.unit === 'ratio') {
    if (n < -0.01 || n > 1.05) return true;
  }
  // Angular: beyond ±180° is impossible
  if (def.unit === 'degrees') {
    if (Math.abs(n) > 180) return true;
  }
  return false;
}

function formatValue(val: number | string | null, def: EvidenceDef): string {
  if (val === null) return '\u2014';
  if (typeof val === 'string') return val.length > 20 ? val.slice(0, 20) + '\u2026' : val;
  const n = val as number;
  if (isValueImpossible(n, def)) return '\u26a0 ERR';
  if (def.unit === 'degrees') return `${n.toFixed(2)}\u00b0`;
  if (def.unit === 'ratio') return n.toFixed(5);
  // 'score' or 'score [0–1]': determine if already percent or fractional
  if (def.unit === 'score' || def.unit.startsWith('score')) {
    if (isPercentScale(def)) {
      // Already 0–100: just display with one decimal
      return n.toFixed(1) + '%';
    } else {
      // Fractional 0–1: convert to percent
      return (n * 100).toFixed(1) + '%';
    }
  }
  if (['px\u00b2', 'px', 'DPI', 'count', 'lines', 'regions', 'elements', 'words/cm\u00b2'].includes(def.unit))
    return Math.round(n).toLocaleString();
  return n.toFixed(4);
}

function getNormalized(val: number | string | null, def: EvidenceDef): number {
  if (val === null || typeof val === 'string') return 0;
  if (!def.typicalRange) return 0;
  const [lo, hi] = def.typicalRange;
  if (hi === lo) return 0;
  // For percent-scale scores, normalize within 0–100
  return Math.min(1, Math.max(0, ((val as number) - lo) / (hi - lo)));
}


function getStatusColor(s: EvidenceStatus): string {
  const map: Record<EvidenceStatus, string> = {
    measured: '#10b981',
    calculated: '#3b82f6',
    derived: '#8b5cf6',
    estimated: '#f59e0b',
    unavailable: '#6b7280',
    experimental: '#ec4899',
    interpolated: '#6b7280',
    deprecated: '#6b7280',
  };
  return map[s] ?? '#6b7280';
}

function getImportanceColor(i: ForensicImportance): string {
  return { critical: '#ef4444', high: '#f59e0b', medium: '#3b82f6', low: '#6b7280' }[i];
}

function matchesSearch(def: EvidenceDef, domain: EvidenceDomainDef, query: string): boolean {
  if (!query.trim()) return true;
  const q = query.toLowerCase().trim();
  if (q.startsWith('domain:') || q.startsWith('group:')) return domain.id.includes(q.split(':')[1]) || domain.label.toLowerCase().includes(q.split(':')[1]);
  if (q.startsWith('importance:')) return def.forensicImportance.includes(q.split(':')[1]);
  if (q.startsWith('status:')) return def.status.includes(q.split(':')[1]);
  if (q.startsWith('tag:')) return def.tags.some(t => t.includes(q.split(':')[1]));
  return def.label.toLowerCase().includes(q) || def.description.toLowerCase().includes(q) || def.id.toLowerCase().includes(q) || def.tags.some(t => t.includes(q)) || domain.label.toLowerCase().includes(q);
}

// ─────────────────────────────────────────────────────────────
// VISUAL HELPERS
// ─────────────────────────────────────────────────────────────

function ScalarBar({ value, color = '#3b82f6' }: { value: number; color?: string }) {
  return (
    <div className="h-1 bg-[#0f1115] border border-[#2a2f3a] rounded-[1px] overflow-hidden">
      <div className="h-full transition-all duration-300" style={{ width: `${Math.round(Math.min(1, value) * 100)}%`, background: color }} />
    </div>
  );
}

function ConfidenceRing({ value, size = 34, color = '#10b981' }: { value: number; size?: number; color?: string }) {
  const r = (size - 6) / 2;
  const circ = 2 * Math.PI * r;
  return (
    <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#1f232d" strokeWidth={4} />
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth={4}
        strokeDasharray={`${value * circ} ${circ - value * circ}`} strokeLinecap="round" />
    </svg>
  );
}

function AngleViz({ angleDeg }: { angleDeg: number }) {
  const rad = (angleDeg * Math.PI) / 180;
  const cx = 17, cy = 17, r = 11;
  return (
    <svg width={34} height={34} style={{ background: '#0f1115', borderRadius: 2, border: '1px solid #2a2f3a' }}>
      <line x1={cx} y1={4} x2={cx} y2={30} stroke="#2a2f3a" strokeWidth={1} />
      <line x1={4} y1={cy} x2={30} y2={cy} stroke="#2a2f3a" strokeWidth={1} />
      <line x1={cx} y1={cy} x2={cx + r * Math.sin(rad)} y2={cy - r * Math.cos(rad)} stroke="#f59e0b" strokeWidth={2} strokeLinecap="round" />
      <circle cx={cx} cy={cy} r={2} fill="#f59e0b" />
    </svg>
  );
}

// ─────────────────────────────────────────────────────────────
// GENOME STATS BAR
// ─────────────────────────────────────────────────────────────

function GenomeStatsBar({ genome, mode }: { genome: GenomeResponse | null; mode: InspectorMode }) {
  const featureCount = genome?.genome_seal?.feature_count ?? 0;
  const validFeatures = genome?.feature_vector?.filter(v => v !== 0 && v !== undefined).length ?? 0;
  const extractionMs = genome?.processing_duration_ms ?? 0;
  return (
    <div className="border-b border-[#2a2f3a] bg-[#0f1115] px-2 py-1.5 shrink-0">
      <div className="flex items-center justify-between text-[9px] font-mono mb-1">
        <span className="text-slate-400 font-semibold tracking-wider">GENOME REGISTRY</span>
        {genome && <span className="text-[#10b981] font-semibold">\u2713 SEALED</span>}
        {!genome && <span className="text-slate-600">NO DOCUMENT</span>}
      </div>
      <div className="grid grid-cols-4 gap-1">
        {[
          { label: 'Dimensions', value: featureCount || (genome?.feature_vector?.length ?? '\u2014'), accent: false },
          { label: 'Valid', value: genome ? validFeatures : '\u2014', accent: true },
          { label: 'Domains', value: GENOME_REGISTRY.length, accent: false },
          { label: 'Runtime', value: genome ? `${extractionMs.toFixed(0)}ms` : '\u2014', accent: false },
        ].map(({ label, value, accent }) => (
          <div key={label} className="bg-[#171a21] border border-[#2a2f3a] px-1 py-1 rounded-[2px] text-center">
            <div className={`text-[11px] font-bold font-mono ${accent ? 'text-[#10b981]' : 'text-slate-200'}`}>{value}</div>
            <div className="text-[9px] text-slate-600">{label}</div>
          </div>
        ))}
      </div>
      {mode === 'developer' && genome && (
        <div className="mt-1 space-y-0.5 text-[9px] font-mono text-slate-600">
          <div>Pipeline v{genome.pipeline_version} \u00b7 Schema v{genome.schema_version}</div>
          <div className="truncate">Job: {genome.job_id}</div>
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// CONTEXT MENU
// ─────────────────────────────────────────────────────────────

interface CtxState { x: number; y: number; def: EvidenceDef; value: number | string | null }

function ContextMenu({ ctx, onClose, onCopy, onPin }: { ctx: CtxState; onClose: () => void; onCopy: (t: string, l: string) => void; onPin: (id: string) => void }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const h = (e: MouseEvent) => { if (ref.current && !ref.current.contains(e.target as Node)) onClose(); };
    document.addEventListener('mousedown', h);
    return () => document.removeEventListener('mousedown', h);
  }, [onClose]);
  const fv = formatValue(ctx.value, ctx.def);
  const items = [
    { label: 'Copy Value', action: () => { onCopy(fv, 'v'); onClose(); } },
    { label: 'Copy JSON', action: () => { onCopy(JSON.stringify({ id: ctx.def.id, label: ctx.def.label, value: ctx.value, unit: ctx.def.unit }), 'j'); onClose(); } },
    { label: 'Copy Evidence Path', action: () => { onCopy(`genome.${ctx.def.domain}.${ctx.def.id}`, 'p'); onClose(); } },
    { label: 'Copy Description', action: () => { onCopy(ctx.def.description, 'd'); onClose(); } },
    null,
    { label: 'Bookmark Evidence', action: () => { onPin(ctx.def.id); onClose(); } },
  ];
  return (
    <div ref={ref} className="fixed z-50 bg-[#1f232d] border border-[#3f4756] shadow-xl py-1 rounded-[2px] min-w-[155px]" style={{ left: ctx.x, top: ctx.y }}>
      {items.map((item, i) =>
        item === null
          ? <div key={i} className="my-0.5 border-t border-[#2a2f3a]" />
          : <button key={i} onClick={item.action} className="w-full flex items-center px-3 py-1.5 text-[10px] text-slate-300 hover:bg-[#2a2f3a] hover:text-slate-100 transition-colors text-left">{item.label}</button>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// EVIDENCE DETAIL PANEL
// ─────────────────────────────────────────────────────────────

function EvidenceDetailPanel({
  def, domain, value, genome, mode, isBookmarked, onBack, onToggleBookmark, onCopy, copied
}: {
  def: EvidenceDef; domain: EvidenceDomainDef; value: number | string | null;
  genome: GenomeResponse | null; mode: InspectorMode;
  isBookmarked: boolean; onBack: () => void; onToggleBookmark: () => void;
  onCopy: (t: string, l: string) => void; copied: string | null;
}) {
  const norm = getNormalized(value, def);
  const fv = formatValue(value, def);
  const [section, setSection] = useState<'overview' | 'provenance' | 'documentation'>('overview');

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="px-2 pt-2 pb-1.5 border-b border-[#2a2f3a] bg-[#0f1115] shrink-0">
        <div className="flex items-center justify-between mb-1.5">
          <button onClick={onBack} className="flex items-center gap-1 text-[9px] text-slate-500 hover:text-slate-300 transition-colors font-mono">
            \u2190 EVIDENCE TREE
          </button>
          <div className="flex items-center gap-1.5">
            <button onClick={onToggleBookmark} className={`transition-colors ${isBookmarked ? 'text-[#f59e0b]' : 'text-slate-600 hover:text-slate-400'}`}>
              <Bookmark className="w-3 h-3" />
            </button>
            <button onClick={() => onCopy(fv, 'val')} className="text-slate-600 hover:text-slate-300 transition-colors">
              {copied === 'val' ? <Check className="w-3 h-3 text-[#10b981]" /> : <Copy className="w-3 h-3" />}
            </button>
          </div>
        </div>
        {/* Domain + importance tags */}
        <div className="flex items-center gap-1 mb-1">
          <span className="px-1 py-0.5 text-[8px] font-mono font-bold rounded-[2px]"
            style={{ background: domain.color + '20', color: domain.color, border: `1px solid ${domain.color}40` }}>
            {domain.label}
          </span>
          <span className="px-1 py-0.5 text-[8px] font-mono rounded-[2px]"
            style={{ background: getImportanceColor(def.forensicImportance) + '20', color: getImportanceColor(def.forensicImportance), border: `1px solid ${getImportanceColor(def.forensicImportance)}40` }}>
            {def.forensicImportance}
          </span>
          <span className="px-1 py-0.5 text-[8px] font-mono rounded-[2px]"
            style={{ background: getStatusColor(def.status) + '20', color: getStatusColor(def.status), border: `1px solid ${getStatusColor(def.status)}40` }}>
            {def.status}
          </span>
        </div>
        <div className="text-[12px] font-semibold text-slate-100 leading-tight">{def.label}</div>
        {mode !== 'analyst' && <div className="text-[9px] font-mono text-slate-600 mt-0.5">{def.id}</div>}

        <div className="mt-2 bg-[#171a21] border border-[#2a2f3a] rounded-[2px] px-2 py-1.5 flex items-center justify-between gap-2">
          <div className="min-w-0">
            <div className="text-[8px] text-slate-600 mb-0.5 font-mono">CURRENT VALUE</div>
            {value === null
              ? <div className="text-[10px] text-slate-600 italic">No data — upload document</div>
              : isValueImpossible(value, def)
                ? (
                  <div className="text-[12px] font-bold font-mono text-[#ef4444] flex items-center gap-1">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>INVALID DATA</span>
                  </div>
                )
                : <div className="text-[14px] font-bold font-mono text-slate-100 truncate">{fv}</div>
            }
            {value !== null && !isValueImpossible(value, def) && (
              <div className="text-[8px] text-slate-600 mt-0.5 font-mono">{def.unit}</div>
            )}
            {value !== null && isValueImpossible(value, def) && (
              <div className="text-[8px] text-[#ef4444] mt-0.5 font-mono">
                Raw: {typeof value === 'number' ? value.toFixed(4) : value} · Expected: {def.typicalRange ? `${def.typicalRange[0]}–${def.typicalRange[1]}` : 'unknown'}
              </div>
            )}
          </div>
          {value !== null && !isValueImpossible(value, def) && (
            <div className="shrink-0">
              {def.vizType === 'confidence_ring' && (
                <ConfidenceRing value={norm} color={domain.color} size={34} />
              )}
              {def.vizType === 'angle_dial' && <AngleViz angleDeg={value as number} />}
              {def.vizType === 'scalar_bar' && (
                <div className="text-[8px] text-slate-600 text-right">
                  <div className="mb-0.5">{(norm * 100).toFixed(0)}% of range</div>
                  <div className="w-14"><ScalarBar value={norm} color={domain.color} /></div>
                </div>
              )}
              {def.vizType === 'binary' && (
                <div className="w-5 h-5 rounded-full flex items-center justify-center" style={{ background: '#10b98130', border: '1px solid #10b98160' }}>
                  <Check className="w-3 h-3 text-[#10b981]" />
                </div>
              )}
            </div>
          )}
        </div>

        {/* Determinism */}
        {mode !== 'analyst' && (
          <div className="flex items-center gap-2 mt-1 text-[8px] font-mono text-slate-600">
            <span>{def.determinism}</span>
            <span>\u00b7</span>
            <span>{def.dataType}</span>
            {def.vectorIndex !== undefined && mode === 'developer' && <><span>\u00b7</span><span>[{def.vectorIndex}]</span></>}
          </div>
        )}
      </div>

      {/* Section tabs */}
      <div className="flex border-b border-[#2a2f3a] bg-[#171a21] shrink-0">
        {(['overview', 'provenance', 'documentation'] as const).map(s => (
          <button key={s} onClick={() => setSection(s)}
            className={`flex-1 py-1.5 text-[9px] font-medium capitalize transition-colors border-b-2 ${section === s ? 'border-[#3b82f6] text-slate-200' : 'border-transparent text-slate-600 hover:text-slate-400'}`}>
            {s}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto text-[10px]">
        {section === 'overview' && (
          <div className="p-2 space-y-2">
            <div className="bg-[#0a0c10] border border-[#1f232d] rounded-[2px] p-2">
              <div className="text-[8px] font-semibold text-slate-600 uppercase tracking-wider mb-1">Interpretation</div>
              <p className="text-slate-300 leading-relaxed text-[10px]">{def.interpretation}</p>
            </div>
            <table className="w-full">
              <tbody className="divide-y divide-[#1a1d24]">
                {(([
                  ['Expected Range', def.typicalRange ? `${formatRangeBound(def.typicalRange[0], def)} \u2013 ${formatRangeBound(def.typicalRange[1], def)}` : 'N/A'],
                  mode !== 'analyst' && ['Extractor', def.extractor],
                  mode !== 'analyst' && ['Pipeline Stage', def.pipelineStage],
                  mode === 'developer' && def.vectorIndex !== undefined && ['Vector Index', `[${def.vectorIndex}]`],
                  mode === 'developer' && ['Evidence ID', def.id],
                ] as any[]).filter(Boolean) as [string, string][]).map(([label, val]) => (
                  <tr key={label}>
                    <td className="py-1 pr-2 text-slate-600 w-[90px] shrink-0 align-top">{label}</td>
                    <td className="py-1 text-slate-300 font-mono break-all">{val}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {value !== null && typeof value === 'number' && def.typicalRange && def.typicalRange[1] > 0 && (
              <div>
                <div className="flex justify-between text-[8px] text-slate-600 mb-1 font-mono">
                  <span>{formatRangeBound(def.typicalRange[0], def)}</span><span>typical range</span><span>{formatRangeBound(def.typicalRange[1], def)}</span>
                </div>
                <ScalarBar value={norm} color={domain.color} />
              </div>
            )}
            {def.relatedIds.length > 0 && (
              <div>
                <div className="text-[8px] text-slate-600 uppercase tracking-wider mb-1 font-semibold">Related Evidence</div>
                <div className="flex flex-wrap gap-1">
                  {def.relatedIds.map(id => (
                    <span key={id} className="px-1 py-0.5 bg-[#171a21] border border-[#2a2f3a] text-slate-500 text-[8px] rounded-[2px] font-mono">{id}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {section === 'provenance' && (
          <div className="p-2 space-y-2">
            <div className="bg-[#0a0c10] border border-[#1f232d] rounded-[2px] p-2">
              <div className="text-[8px] font-semibold text-slate-600 uppercase tracking-wider mb-1.5">Chain of Custody</div>
              <table className="w-full">
                <tbody className="divide-y divide-[#1a1d24]">
                  {(([
                    ['Computed By', def.extractor],
                    ['Pipeline Stage', def.pipelineStage],
                    ['Determinism', def.determinism],
                    ['Status', def.status],
                    ['Data Type', def.dataType],
                    genome && ['Pipeline v', genome.pipeline_version],
                    genome && ['Schema v', genome.schema_version],
                    genome && ['Extracted', genome.extraction_timestamp.slice(0, 19).replace('T', ' ')],
                    genome?.config_fingerprint && ['Config Hash', genome.config_fingerprint.slice(0, 16) + '\u2026'],
                    mode === 'developer' && def.vectorIndex !== undefined && ['Vector idx', `feature_vector[${def.vectorIndex}]`],
                  ] as any[]).filter(Boolean) as [string, string][]).map(([label, val]) => (
                    <tr key={label}>
                      <td className="py-1 pr-2 text-slate-600 w-[90px] shrink-0 align-top">{label}</td>
                      <td className="py-1 text-slate-300 font-mono break-all">{val}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {def.derivedFrom.length > 0 && (
              <div className="bg-[#0a0c10] border border-[#1f232d] rounded-[2px] p-2">
                <div className="text-[8px] font-semibold text-slate-600 uppercase tracking-wider mb-1">Derived From</div>
                {def.derivedFrom.map(id => (
                  <div key={id} className="text-[9px] font-mono text-[#8b5cf6]">\u2192 {id}</div>
                ))}
              </div>
            )}
          </div>
        )}

        {section === 'documentation' && (
          <div className="p-2 space-y-2">
            {[
              { title: 'Definition', content: def.description },
              { title: 'Purpose', content: def.purpose },
              { title: 'Calculation Method', content: def.calculationMethod },
              { title: 'Known Limitations', content: def.knownLimitations },
              { title: 'Edge Cases', content: def.edgeCases },
            ].map(({ title, content }) => (
              <div key={title} className="bg-[#0a0c10] border border-[#1f232d] rounded-[2px] p-2">
                <div className="text-[8px] font-semibold text-slate-600 uppercase tracking-wider mb-1">{title}</div>
                <p className="text-slate-300 leading-relaxed">{content}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// EVIDENCE ROW
// ─────────────────────────────────────────────────────────────

function EvidenceRow({ def, domain, value, mode, isBookmarked, isSelected, onSelect, onContextMenu }: {
  def: EvidenceDef; domain: EvidenceDomainDef; value: number | string | null;
  mode: InspectorMode; isBookmarked: boolean; isSelected: boolean;
  onSelect: () => void; onContextMenu: (e: React.MouseEvent) => void;
}) {
  const fv = formatValue(value, def);
  const norm = getNormalized(value, def);
  const hasValue = value !== null;
  return (
    <div
      className={`flex items-start gap-1.5 px-2 py-1.5 cursor-pointer transition-colors border-l-2 ${isSelected ? 'bg-[#192236] border-[#3b82f6]' : 'border-transparent hover:bg-[#151820] hover:border-[#2a2f3a]'}`}
      onClick={onSelect}
      onContextMenu={onContextMenu}
    >
      <div className="mt-1 shrink-0 w-1.5 h-1.5 rounded-full" style={{ background: getStatusColor(def.status) }} />
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-1">
          <span className={`text-[10px] font-medium truncate ${isSelected ? 'text-slate-100' : 'text-slate-400 hover:text-slate-300'}`}>{def.label}</span>
          <div className="flex items-center gap-1 shrink-0">
            {isBookmarked && <Bookmark className="w-2.5 h-2.5 text-[#f59e0b]" />}
            {(def.forensicImportance === 'critical' || def.forensicImportance === 'high') && (
              <div className="w-1 h-1 rounded-full" style={{ background: getImportanceColor(def.forensicImportance) }} />
            )}
          </div>
        </div>
        <div className="flex items-center gap-1.5 mt-0.5">
          <span className={`text-[10px] font-mono ${hasValue ? 'text-slate-200' : 'text-slate-700 italic'} truncate`}>
            {hasValue ? fv : 'no data'}
          </span>
          {mode !== 'analyst' && hasValue && <span className="text-[8px] text-slate-600 shrink-0">{def.unit}</span>}
        </div>
        {hasValue && def.vizType === 'scalar_bar' && typeof value === 'number' && (
          <div className="mt-1"><ScalarBar value={norm} color={domain.color} /></div>
        )}
        {mode === 'developer' && def.vectorIndex !== undefined && (
          <div className="text-[8px] font-mono text-slate-700 mt-0.5">[{def.vectorIndex}] {def.id}</div>
        )}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// GENOME EXPLORER MAIN
// ─────────────────────────────────────────────────────────────

interface GenomeExplorerProps {
  genome: GenomeResponse | null;
  debugData: DebugInspectionResponse | null;
}

export const GenomeExplorer: React.FC<GenomeExplorerProps> = ({ genome, debugData }) => {
  const [mode, setMode] = useState<InspectorMode>('analyst');
  const [search, setSearch] = useState('');
  const [expandedDomains, setExpandedDomains] = useState<Set<string>>(new Set(['geometry', 'ocr', 'metadata', 'security']));
  const [selectedDef, setSelectedDef] = useState<{ def: EvidenceDef; domain: EvidenceDomainDef } | null>(null);
  const [bookmarks, setBookmarks] = useState<Set<string>>(new Set());
  const [contextMenu, setContextMenu] = useState<CtxState | null>(null);
  const [copied, setCopied] = useState<string | null>(null);
  const [filterImportance, setFilterImportance] = useState<ForensicImportance | 'all'>('all');

  const handleCopy = useCallback((text: string, label: string) => {
    navigator.clipboard.writeText(text).catch(() => {});
    setCopied(label);
    setTimeout(() => setCopied(null), 2000);
  }, []);

  const toggleDomain = useCallback((id: string) => {
    setExpandedDomains(prev => { const n = new Set(prev); n.has(id) ? n.delete(id) : n.add(id); return n; });
  }, []);

  const toggleBookmark = useCallback((id: string) => {
    setBookmarks(prev => { const n = new Set(prev); n.has(id) ? n.delete(id) : n.add(id); return n; });
  }, []);

  // Build feature map once per genome change — O(1) lookup for all feature rows
  const featureMap = useMemo(() => buildFeatureMap(genome), [genome]);
  const getVal = useCallback(
    (def: EvidenceDef) => getValueFromGenome(def, genome, debugData, featureMap),
    [genome, debugData, featureMap]
  );

  const filteredRegistry = useMemo(() =>
    GENOME_REGISTRY.map(domain => ({
      ...domain,
      features: domain.features.filter(def => {
        const imp = filterImportance === 'all' || def.forensicImportance === filterImportance;
        return imp && matchesSearch(def, domain, search);
      }),
    })).filter(d => d.features.length > 0),
    [search, filterImportance]
  );

  const pinnedFeatures = useMemo(() => {
    const result: { def: EvidenceDef; domain: EvidenceDomainDef }[] = [];
    GENOME_REGISTRY.forEach(domain => domain.features.forEach(def => {
      if (bookmarks.has(def.id)) result.push({ def, domain });
    }));
    return result;
  }, [bookmarks]);

  const modes: { id: InspectorMode; label: string; color: string }[] = [
    { id: 'analyst', label: 'Analyst', color: '#10b981' },
    { id: 'research', label: 'Research', color: '#3b82f6' },
    { id: 'developer', label: 'Dev', color: '#8b5cf6' },
  ];

  return (
    <div className="flex flex-col h-full select-none">
      <GenomeStatsBar genome={genome} mode={mode} />

      {/* Toolbar */}
      <div className="px-2 py-1.5 border-b border-[#2a2f3a] bg-[#0c0e13] shrink-0 space-y-1.5">
        <div className="relative">
          <Search className="w-3 h-3 text-slate-600 absolute left-2 top-1.5" />
          <input
            type="text" value={search} onChange={e => setSearch(e.target.value)}
            placeholder="tag:texture  importance:high  status:estimated"
            className="w-full bg-[#171a21] border border-[#2a2f3a] text-slate-300 pl-6 pr-6 py-1 text-[9px] rounded-[2px] focus:outline-none focus:border-[#3b82f6] placeholder:text-slate-700 font-mono"
          />
          {search && (
            <button onClick={() => setSearch('')} className="absolute right-1.5 top-1.5 text-slate-600 hover:text-slate-400">
              <X className="w-3 h-3" />
            </button>
          )}
        </div>
        <div className="flex items-center justify-between gap-1">
          {/* Mode switcher */}
          <div className="flex items-center bg-[#0f1115] border border-[#2a2f3a] rounded-[2px] overflow-hidden">
            {modes.map(m => (
              <button key={m.id} onClick={() => setMode(m.id)}
                className="px-2 py-0.5 text-[9px] font-medium transition-colors"
                style={mode === m.id ? { background: m.color + '25', color: m.color } : { color: '#4b5563' }}>
                {m.label}
              </button>
            ))}
          </div>
          {/* Filter */}
          <select value={filterImportance} onChange={e => setFilterImportance(e.target.value as any)}
            className="bg-[#0f1115] border border-[#2a2f3a] text-slate-500 text-[9px] px-1.5 py-0.5 rounded-[2px] focus:outline-none">
            <option value="all">All</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      {/* Main — Tree or Detail */}
      {selectedDef ? (
        <div className="flex-1 overflow-hidden">
          <EvidenceDetailPanel
            def={selectedDef.def} domain={selectedDef.domain}
            value={getVal(selectedDef.def)} genome={genome} mode={mode}
            isBookmarked={bookmarks.has(selectedDef.def.id)}
            onBack={() => setSelectedDef(null)}
            onToggleBookmark={() => toggleBookmark(selectedDef.def.id)}
            onCopy={handleCopy} copied={copied}
          />
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto">
          {/* No genome banner */}
          {!genome && (
            <div className="mx-2 mt-2 mb-1 px-2 py-1.5 bg-[#131200] border border-[#3a2f00] rounded-[2px] flex items-start gap-1.5">
              <AlertTriangle className="w-3 h-3 text-[#f59e0b] shrink-0 mt-0.5" />
              <p className="text-[9px] text-[#78603a] leading-relaxed">Registry definitions shown. Upload a document to populate evidence values.</p>
            </div>
          )}

          {/* Bookmarks */}
          {pinnedFeatures.length > 0 && (
            <div>
              <button onClick={() => toggleDomain('__bookmarks')}
                className="w-full flex items-center gap-1.5 px-2 py-1.5 bg-[#0f1108] border-b border-[#2a2f3a] text-[9px] font-semibold text-[#f59e0b] hover:bg-[#141500] transition-colors">
                {expandedDomains.has('__bookmarks') ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
                <Bookmark className="w-3 h-3" />
                <span>Bookmarks ({pinnedFeatures.length})</span>
              </button>
              {expandedDomains.has('__bookmarks') && pinnedFeatures.map(({ def, domain }) => (
                <EvidenceRow key={def.id} def={def} domain={domain} value={getVal(def)} mode={mode}
                  isBookmarked={true} isSelected={false}
                  onSelect={() => setSelectedDef({ def, domain })}
                  onContextMenu={e => { e.preventDefault(); setContextMenu({ x: e.clientX, y: e.clientY, def, value: getVal(def) }); }}
                />
              ))}
            </div>
          )}

          {/* Domains */}
          {filteredRegistry.map(domain => {
            const isExpanded = expandedDomains.has(domain.id);
            return (
              <div key={domain.id}>
                <button onClick={() => toggleDomain(domain.id)}
                  className="w-full flex items-center gap-1.5 px-2 py-1.5 border-b border-[#1f232d] hover:bg-[#111318] transition-colors"
                  style={{ background: isExpanded ? domain.color + '08' : undefined }}>
                  <span className="text-slate-600">{isExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}</span>
                  <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: domain.color }} />
                  <span className="text-[10px] font-semibold flex-1 text-left transition-colors" style={{ color: isExpanded ? domain.color : '#64748b' }}>{domain.label}</span>
                  <span className="text-[8px] font-mono text-slate-700">{domain.features.length}</span>
                </button>
                {isExpanded && mode !== 'analyst' && (
                  <div className="px-2 py-1 bg-[#090b0f] border-b border-[#1a1d24] text-[8px] text-slate-700 italic">{domain.description}</div>
                )}
                {isExpanded && domain.features.map(def => (
                  <EvidenceRow key={def.id} def={def} domain={domain} value={getVal(def)} mode={mode}
                    isBookmarked={bookmarks.has(def.id)} isSelected={false}
                    onSelect={() => setSelectedDef({ def, domain })}
                    onContextMenu={e => { e.preventDefault(); setContextMenu({ x: e.clientX, y: e.clientY, def, value: getVal(def) }); }}
                  />
                ))}
              </div>
            );
          })}

          {filteredRegistry.length === 0 && (
            <div className="p-4 text-center">
              <Search className="w-5 h-5 text-slate-700 mx-auto mb-2" />
              <div className="text-[10px] text-slate-600">No evidence matching</div>
              <div className="text-[9px] text-slate-700 font-mono mt-0.5">"{search}"</div>
              <button onClick={() => { setSearch(''); setFilterImportance('all'); }}
                className="mt-2 text-[9px] text-[#3b82f6] hover:underline">Clear filters</button>
            </div>
          )}
        </div>
      )}

      {contextMenu && (
        <ContextMenu ctx={contextMenu} onClose={() => setContextMenu(null)} onCopy={handleCopy} onPin={toggleBookmark} />
      )}
    </div>
  );
};
