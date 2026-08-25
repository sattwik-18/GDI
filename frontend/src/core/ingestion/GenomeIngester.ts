/**
 * GDI Platform v2 - Genome Ingester Engine
 *
 * Responsible for ingesting a raw backend GenomeResponse (and optional DebugInspectionResponse),
 * resolving feature definitions against the canonical GenomeRegistry, normalizing values,
 * computing formatting, detecting anomaly/impossible bounds, and transforming them into
 * typed IngestedEvidence objects.
 */

import { GENOME_REGISTRY } from '@/core/registry/GenomeRegistry';
import type { EvidenceDef, EvidenceStatus } from '@/core/domain/types';
import type { GenomeResponse, DebugInspectionResponse } from '@/types/gdi';
import type { IngestedEvidence } from '@/state/evidence.store';

export class GenomeIngester {
  /**
   * Ingest a DocumentGenome and optional debug inspection data into normalized Evidence objects.
   */
  public static ingest(
    genome: GenomeResponse | null,
    debugData: DebugInspectionResponse | null = null
  ): IngestedEvidence[] {
    if (!genome) {
      return [];
    }

    const featureMap = this.buildFeatureMap(genome);
    const results: IngestedEvidence[] = [];

    for (const domainDef of GENOME_REGISTRY) {
      for (const def of domainDef.features) {
        const val = this.extractRawValue(def, genome, debugData, featureMap);
        const isImpossible = this.isValueImpossible(val, def);
        const norm = this.getNormalized(val, def);
        const formatted = this.formatValue(val, def, isImpossible);
        const status = this.determineStatus(val, def, isImpossible);

        results.push({
          def,
          value: val,
          normalizedValue: norm,
          formattedValue: formatted,
          isImpossible,
          computedStatus: status,
        });
      }
    }

    return results;
  }

  /**
   * Builds a flat lookup dictionary of all extracted feature keys from the primary page.
   */
  public static buildFeatureMap(genome: GenomeResponse | null): Record<string, number> {
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


  private static FEATURE_KEY_ALIASES: Record<string, string[]> = {
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

  private static extractRawValue(
    def: EvidenceDef,
    genome: GenomeResponse | null,
    debugData: DebugInspectionResponse | null,
    featureMap: Record<string, number>
  ): number | string | null {
    const page0 = genome?.pages?.[0];
    const quality = page0?.quality_metrics || debugData?.page_quality_reports?.[0] || null;
    const pageMeta = page0?.metadata || null;

    // Top-level well-known metadata mapping
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

    // 1. Direct featureKey lookup
    if (def.featureKey && featureMap[def.featureKey] !== undefined) {
      return featureMap[def.featureKey];
    }

    // 2. Direct ID lookup in featureMap
    if (featureMap[def.id] !== undefined) {
      return featureMap[def.id];
    }

    // 3. Known Aliases lookup
    const aliases = this.FEATURE_KEY_ALIASES[def.id];
    if (aliases) {
      for (const alias of aliases) {
        if (featureMap[alias] !== undefined) {
          return featureMap[alias];
        }
      }
    }

    // 4. Substring / suffix match fallback
    const strippedId = def.id.replace(/^(geo|ocr|typo|tex|freq|stat|meta|sec|layout)_/, '');
    for (const [k, v] of Object.entries(featureMap)) {
      if (k.endsWith(strippedId) || k.includes(strippedId)) {
        return v;
      }
    }

    // 5. Fallback to raw feature_vector array by index if available
    const vec = page0?.feature_vector || (genome as any)?.feature_vector;
    if (Array.isArray(vec) && def.vectorIndex !== undefined && def.vectorIndex < vec.length) {
      const v = vec[def.vectorIndex];
      if (typeof v === 'number' && !isNaN(v)) return v;
    }

    return null;
  }

  public static isPercentScale(def: EvidenceDef): boolean {
    if (!def.typicalRange) return false;
    return def.typicalRange[1] > 1.5;
  }

  public static isValueImpossible(val: number | string | null, def: EvidenceDef): boolean {
    if (val === null || typeof val === 'string') return false;
    const n = val as number;

    if (def.unit === 'score' || def.unit.startsWith('score')) {
      const maxExpected = this.isPercentScale(def) ? 100 : 1.0;
      if (n < 0 || n > maxExpected * 1.05) return true;
    }

    if (def.unit === 'ratio') {
      if (n < -0.01 || n > 1.05) return true;
    }

    if (def.unit === 'degrees') {
      if (Math.abs(n) > 180) return true;
    }

    return false;
  }

  public static formatValue(val: number | string | null, def: EvidenceDef, isImpossible: boolean): string {
    if (val === null) return '\u2014';
    if (typeof val === 'string') return val.length > 20 ? val.slice(0, 20) + '\u2026' : val;
    const n = val as number;

    if (isImpossible) return '\u26a0 ERR';
    if (def.unit === 'degrees') return `${n.toFixed(2)}\u00b0`;
    if (def.unit === 'ratio') return n.toFixed(5);

    if (def.unit === 'score' || def.unit.startsWith('score')) {
      if (this.isPercentScale(def)) {
        return n.toFixed(1) + '%';
      } else {
        return (n * 100).toFixed(1) + '%';
      }
    }

    if (['px\u00b2', 'px', 'DPI', 'count', 'lines', 'regions', 'elements', 'words/cm\u00b2'].includes(def.unit)) {
      return Math.round(n).toLocaleString();
    }


    return n.toFixed(4);
  }

  public static getNormalized(val: number | string | null, def: EvidenceDef): number {
    if (val === null || typeof val === 'string') return 0;
    if (!def.typicalRange) return 0;
    const [lo, hi] = def.typicalRange;
    if (hi === lo) return 0;
    return Math.min(1, Math.max(0, ((val as number) - lo) / (hi - lo)));
  }

  private static determineStatus(
    val: number | string | null,
    def: EvidenceDef,
    isImpossible: boolean
  ): EvidenceStatus {
    if (val === null) return 'unavailable';
    if (isImpossible) return 'experimental';
    return def.status;
  }
}
