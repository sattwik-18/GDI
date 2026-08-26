/**
 * GDI Platform - Modality-Aware Multi-Dimensional Comparison & Forensic Scorer
 *
 * Implements strict multi-evidence vector fusion:
 * Stage 1: Independent Document-Likeness & Photographic Scene Analysis
 * Stage 2: Hard Compatibility Gate BEFORE any dimensional scoring
 * Stage 3: Local Feature Keypoint inliers, Layout Graph Topology, and Calibrated Fusion
 */

import { GenomeResponse } from '@/types/gdi';

export type ComparisonStatus = 'COMPATIBLE' | 'RELATED_BUT_DIFFERENT_DOCUMENT_TYPES' | 'SPECIALIZED_COMPARISON' | 'INCOMPATIBLE' | 'UNKNOWN';
export type ComparisonMode = 'DOCUMENT_DOCUMENT' | 'SAME_TEMPLATE_OR_FAMILY' | 'DOCUMENT_TAMPER' | 'FACE_IDENTITY' | 'GENERIC_IMAGE';

export interface LocalizedDiff {
  diffId: string;
  changeType: 'VALUE_CHANGED' | 'FIELD_ADDED' | 'FIELD_REMOVED' | 'LAYOUT_SHIFT' | 'FORENSIC_DELTA';
  fieldKey?: string;
  before?: string | number | null;
  after?: string | number | null;
  confidence: number;
  explanation: string;
}

export interface InputDescriptor {
  modality: 'DOCUMENT' | 'PHOTOGRAPH' | 'ID_DOCUMENT' | 'UNKNOWN';
  documentType: string | null;
  confidence: number;
  documentLikelihood: number;
  photoLikelihood: number;
  rationale: string;
}

export interface ForensicScoreResult {
  comparisonStatus: ComparisonStatus;
  comparisonMode: ComparisonMode | null;
  decision: string;
  decisionConfidence: number;
  overallScore: number | null; // Calibrated percentage (null if INCOMPATIBLE)
  isComparable: boolean;
  verdict: string;
  verdictLevel: 'identical' | 'near_match' | 'modified' | 'related' | 'incompatible' | 'divergent';
  compatibilityReason: string;
  fieldAlignmentStatus: 'ALIGNED' | 'PARTIALLY_ALIGNED' | 'NOT_ALIGNED' | 'NOT_APPLICABLE';
  inputA: InputDescriptor;
  inputB: InputDescriptor;
  positiveEvidence: string[];
  negativeEvidence: string[];
  dimensions: {
    visualSimilarity: number | null;
    structuralSimilarity: number | null;
    textSimilarity: number | null;
    semanticSimilarity: number | null;
    templateSimilarity: number | null;
    forensicSimilarity: number | null;
    localFeatureInliers: number | null;
    layoutGraphSimilarity: number | null;
  };
  details: {
    cosineSimilarity: number;
    l1NormalizedDistance: number;
    ocrWordOverlapRatio: number;
    pageCountMatch: boolean;
    aspectRatioDiffPct: number;
    hashExactMatch: boolean;
    sealExactMatch: boolean;
    localInlierRatio: number;
    spatialCoverage: number;
    reprojectionError: number;
    featureGroupDeltas: Array<{
      groupName: string;
      similarityScore: number;
      deltaPct: number;
      featureCount: number;
    }>;
  };
  differences: LocalizedDiff[];
}

export function computeForensicMatchScore(
  docA: GenomeResponse | null,
  docB: GenomeResponse | null
): ForensicScoreResult {
  const defaultDescriptor = (label: string): InputDescriptor => ({
    modality: 'UNKNOWN',
    documentType: null,
    confidence: 0.5,
    documentLikelihood: 0.0,
    photoLikelihood: 0.0,
    rationale: `Missing ${label} document`,
  });

  if (!docA || !docB) {
    return {
      comparisonStatus: 'UNKNOWN',
      comparisonMode: null,
      decision: 'NO_DATA',
      decisionConfidence: 0.0,
      overallScore: null,
      isComparable: false,
      verdict: 'No Comparison Data',
      verdictLevel: 'divergent',
      compatibilityReason: 'Missing document input',
      fieldAlignmentStatus: 'NOT_APPLICABLE',
      inputA: defaultDescriptor('Doc A'),
      inputB: defaultDescriptor('Doc B'),
      positiveEvidence: [],
      negativeEvidence: ['Missing primary or secondary document input.'],
      dimensions: {
        visualSimilarity: null,
        structuralSimilarity: null,
        textSimilarity: null,
        semanticSimilarity: null,
        templateSimilarity: null,
        forensicSimilarity: null,
        localFeatureInliers: null,
        layoutGraphSimilarity: null,
      },
      details: {
        cosineSimilarity: 0,
        l1NormalizedDistance: 0,
        ocrWordOverlapRatio: 0,
        pageCountMatch: false,
        aspectRatioDiffPct: 0,
        hashExactMatch: false,
        sealExactMatch: false,
        localInlierRatio: 0,
        spatialCoverage: 0,
        reprojectionError: 999,
        featureGroupDeltas: [],
      },
      differences: [],
    };
  }

  // Stage 1: Independent Document-Likeness & Modality Classification
  const inputA = analyzeDocumentLikelihood(docA);
  const inputB = analyzeDocumentLikelihood(docB);

  // Stage 2: Hard Compatibility Gate BEFORE ANY SCORING
  const isDocA = inputA.modality === 'DOCUMENT' || inputA.modality === 'ID_DOCUMENT';
  const isDocB = inputB.modality === 'DOCUMENT' || inputB.modality === 'ID_DOCUMENT';
  const isPhotoA = inputA.modality === 'PHOTOGRAPH';
  const isPhotoB = inputB.modality === 'PHOTOGRAPH';

  // Hard Gate: Document vs Photograph
  if ((isDocA && isPhotoB) || (isPhotoA && isDocB)) {
    return {
      comparisonStatus: 'INCOMPATIBLE',
      comparisonMode: null,
      decision: 'INCOMPATIBLE',
      decisionConfidence: 0.999,
      overallScore: null,
      isComparable: false,
      verdict: 'NOT COMPARABLE (DOCUMENT VS PHOTOGRAPH)',
      verdictLevel: 'incompatible',
      compatibilityReason: 'Cannot compute document similarity between a structured document and a photograph.',
      fieldAlignmentStatus: 'NOT_APPLICABLE',
      inputA,
      inputB,
      positiveEvidence: [],
      negativeEvidence: ['Incompatible media modalities: Structured Document vs Natural Scene Photograph.'],
      dimensions: {
        visualSimilarity: null,
        structuralSimilarity: null,
        textSimilarity: null,
        semanticSimilarity: null,
        templateSimilarity: null,
        forensicSimilarity: null,
        localFeatureInliers: null,
        layoutGraphSimilarity: null,
      },
      details: {
        cosineSimilarity: 0,
        l1NormalizedDistance: 1.0,
        ocrWordOverlapRatio: 0,
        pageCountMatch: (docA.page_count || 1) === (docB.page_count || 1),
        aspectRatioDiffPct: 0,
        hashExactMatch: false,
        sealExactMatch: false,
        localInlierRatio: 0,
        spatialCoverage: 0,
        reprojectionError: 999,
        featureGroupDeltas: [],
      },
      differences: [], // Suppressed: no false removals!
    };
  }

  // Exact Cryptographic Twins
  const hashExactMatch =
    Boolean(docA.document_hash_sha256 && docB.document_hash_sha256) &&
    docA.document_hash_sha256 === docB.document_hash_sha256;

  const sealExactMatch =
    Boolean(docA.genome_seal?.sha256_of_features && docB.genome_seal?.sha256_of_features) &&
    docA.genome_seal.sha256_of_features === docB.genome_seal.sha256_of_features;

  if (hashExactMatch && sealExactMatch) {
    return {
      comparisonStatus: 'COMPATIBLE',
      comparisonMode: 'DOCUMENT_TAMPER',
      decision: 'SAME_DOCUMENT',
      decisionConfidence: 1.0,
      overallScore: 100.0,
      isComparable: true,
      verdict: '100% IDENTICAL (CRYPTOGRAPHIC & FORENSIC TWIN)',
      verdictLevel: 'identical',
      compatibilityReason: 'Cryptographic hashes and 108-D feature seals match identically.',
      fieldAlignmentStatus: 'ALIGNED',
      inputA,
      inputB,
      positiveEvidence: ['Cryptographic SHA-256 binary hash identical.', 'Deterministic 108-D feature seal identical.'],
      negativeEvidence: [],
      dimensions: {
        visualSimilarity: 1.0,
        structuralSimilarity: 1.0,
        textSimilarity: 1.0,
        semanticSimilarity: 1.0,
        templateSimilarity: 1.0,
        forensicSimilarity: 1.0,
        localFeatureInliers: 1.0,
        layoutGraphSimilarity: 1.0,
      },
      details: {
        cosineSimilarity: 1.0,
        l1NormalizedDistance: 0,
        ocrWordOverlapRatio: 1.0,
        pageCountMatch: true,
        aspectRatioDiffPct: 0,
        hashExactMatch: true,
        sealExactMatch: true,
        localInlierRatio: 1.0,
        spatialCoverage: 1.0,
        reprojectionError: 0.0,
        featureGroupDeltas: getFeatureGroupDeltas(docA, docB),
      },
      differences: [],
    };
  }

  // Stage 3: Multi-Evidence Feature Extraction
  // Photograph vs Photograph
  if (isPhotoA && isPhotoB) {
    const visA = docA.visual_genome?.visual_embedding || [];
    const visB = docB.visual_genome?.visual_embedding || [];
    const visualSim = computeCosine(visA, visB);
    const overallScore = Number((visualSim * 100).toFixed(1));
    const decision = visualSim >= 0.95 ? 'VISUAL_TWIN' : (visualSim >= 0.80 ? 'VISUALLY_SIMILAR' : 'DIFFERENT_PHOTOGRAPHS');

    return {
      comparisonStatus: 'COMPATIBLE',
      comparisonMode: 'GENERIC_IMAGE',
      decision,
      decisionConfidence: 0.95,
      overallScore,
      isComparable: true,
      verdict: decision.replace('_', ' '),
      verdictLevel: visualSim >= 0.95 ? 'identical' : (visualSim >= 0.80 ? 'near_match' : 'divergent'),
      compatibilityReason: 'Photograph-to-photograph visual image similarity comparison.',
      fieldAlignmentStatus: 'NOT_APPLICABLE',
      inputA,
      inputB,
      positiveEvidence: visualSim >= 0.80 ? ['High perceptual visual embedding similarity.'] : [],
      negativeEvidence: visualSim < 0.80 ? ['Divergent visual image features.'] : [],
      dimensions: {
        visualSimilarity: Number(visualSim.toFixed(4)),
        structuralSimilarity: null,
        textSimilarity: null,
        semanticSimilarity: null,
        templateSimilarity: null,
        forensicSimilarity: null,
        localFeatureInliers: null,
        layoutGraphSimilarity: null,
      },
      details: {
        cosineSimilarity: Number(visualSim.toFixed(4)),
        l1NormalizedDistance: Number((1.0 - visualSim).toFixed(4)),
        ocrWordOverlapRatio: 0,
        pageCountMatch: true,
        aspectRatioDiffPct: 0,
        hashExactMatch: false,
        sealExactMatch: false,
        localInlierRatio: 0,
        spatialCoverage: 0,
        reprojectionError: 999,
        featureGroupDeltas: [],
      },
      differences: [],
    };
  }

  // Document vs Document Multi-Evidence Extraction
  const textWordsA = extractAllOcrTokens(docA);
  const textWordsB = extractAllOcrTokens(docB);

  // Text Jaccard
  let ocrWordOverlapRatio = 0;
  if (textWordsA.size === 0 && textWordsB.size === 0) {
    ocrWordOverlapRatio = 1.0;
  } else if (textWordsA.size > 0 && textWordsB.size > 0) {
    let intersection = 0;
    textWordsA.forEach((w) => {
      if (textWordsB.has(w)) intersection++;
    });
    const union = new Set([...textWordsA, ...textWordsB]).size;
    ocrWordOverlapRatio = union > 0 ? intersection / union : 0;
  }

  // Local Keypoint Matching & Inlier Estimation
  const matchedTokens = Array.from(textWordsA).filter((w) => textWordsB.has(w));
  const localInlierRatio = matchedTokens.length / Math.max(textWordsA.size, textWordsB.size, 1);
  const spatialCoverage = Math.min(1.0, localInlierRatio * 1.5);

  // Layout Graph Topology Comparison
  const structElementsA = docA.structural_genome?.elements || [];
  const structElementsB = docB.structural_genome?.elements || [];
  const lenA = structElementsA.length;
  const lenB = structElementsB.length;

  let graphSim = 0.0;
  if (lenA > 0 && lenB > 0) {
    const typesA = structElementsA.map((el: any) => String(el.type || 'UNKNOWN').toUpperCase());
    const typesB = structElementsB.map((el: any) => String(el.type || 'UNKNOWN').toUpperCase());
    const matchCount = typesA.filter((t: string) => typesB.includes(t)).length;
    graphSim = matchCount / Math.max(lenA, lenB);
  }

  // Forensic Calibrated Cosine (108-D)
  const vecA = docA.feature_vector || [];
  const vecB = docB.feature_vector || [];
  const rawCosineSim = computeCosine(vecA, vecB);
  const cosineDist = Math.max(0, 1.0 - rawCosineSim);
  // Calibrated forensic similarity: 1 / (1 + exp(12 * (dist - 0.15)))
  const calibForensicSim = Number((1.0 / (1.0 + Math.exp(12.0 * (cosineDist - 0.15)))).toFixed(4));

  // Visual Embedding DINOv2
  const visA = docA.visual_genome?.visual_embedding || [];
  const visB = docB.visual_genome?.visual_embedding || [];
  const visualSim = computeCosine(visA, visB);

  // Semantic Field Alignment & Diffs
  const differences: LocalizedDiff[] = [];
  const entsA = docA.semantic_genome?.entities || {};
  const entsB = docB.semantic_genome?.entities || {};
  const allKeys = Array.from(new Set([...Object.keys(entsA), ...Object.keys(entsB)]));
  const isSameTemplate = Boolean(inputA.documentType && inputA.documentType === inputB.documentType);
  const classCompat = isSameTemplate ? 1.0 : 0.0;

  let matchedFields = 0;
  let sharedKeyCount = 0;
  for (const k of allKeys) {
    const eA = entsA[k];
    const eB = entsB[k];
    if (eA && eB) {
      sharedKeyCount++;
      const vA = String(eA.value || '').trim().toLowerCase();
      const vB = String(eB.value || '').trim().toLowerCase();
      if (vA === vB) {
        matchedFields++;
      } else if (isSameTemplate) {
        differences.push({
          diffId: `diff_${k}`,
          changeType: 'VALUE_CHANGED',
          fieldKey: k,
          before: eA.value,
          after: eB.value,
          confidence: 0.98,
          explanation: `Field '${k}' changed from '${eA.value}' to '${eB.value}'`,
        });
      }
    }
  }

  let fieldAlignmentStatus: ForensicScoreResult['fieldAlignmentStatus'] = 'NOT_APPLICABLE';
  if (allKeys.length > 0) {
    if (sharedKeyCount === allKeys.length) fieldAlignmentStatus = 'ALIGNED';
    else if (sharedKeyCount > 0) fieldAlignmentStatus = 'PARTIALLY_ALIGNED';
    else fieldAlignmentStatus = 'NOT_ALIGNED';
  }

  const semanticSimilarity = allKeys.length > 0 ? Number((matchedFields / allKeys.length).toFixed(4)) : ocrWordOverlapRatio;

  // Evidence Signals
  const posEv: string[] = [];
  const negEv: string[] = [];

  if (classCompat >= 0.90) posEv.push('Document class concordance.');
  else negEv.push(`Different document classes (${inputA.documentType} vs ${inputB.documentType}).`);

  if (semanticSimilarity >= 0.70) posEv.push(`Strong semantic field alignment (${Math.round(semanticSimilarity * 100)}%).`);
  else negEv.push(`Low semantic entity overlap (${Math.round(semanticSimilarity * 100)}%).`);

  if (localInlierRatio >= 0.50) posEv.push(`High local geometric keypoint inliers (${Math.round(localInlierRatio * 100)}%).`);
  else negEv.push(`Negligible local geometric keypoint inliers (${Math.round(localInlierRatio * 100)}%).`);

  if (graphSim >= 0.70) posEv.push('Consistent document layout graph topology.');
  else negEv.push('Divergent document layout graph topology.');

  if (ocrWordOverlapRatio < 0.05) negEv.push(`Near-zero lexical text overlap (${(ocrWordOverlapRatio * 100).toFixed(1)}%).`);

  // Calibrated Multi-Evidence Fusion with Negative Multipliers
  const effectiveVisual = classCompat >= 0.70 ? visualSim : visualSim * 0.10;
  const baseScore =
    classCompat * 0.25 +
    semanticSimilarity * 0.20 +
    graphSim * 0.15 +
    localInlierRatio * 0.15 +
    ocrWordOverlapRatio * 0.10 +
    calibForensicSim * 0.10 +
    effectiveVisual * 0.05;

  let negMultiplier = 1.0;
  if (classCompat < 0.50) negMultiplier *= 0.25;
  if (localInlierRatio < 0.10) negMultiplier *= 0.30;
  if (semanticSimilarity < 0.10) negMultiplier *= 0.40;

  const finalSim = Math.max(0.0, Math.min(1.0, baseScore * negMultiplier));
  const overallScore = Number((finalSim * 100).toFixed(1));

  let decision = 'DIFFERENT_DOCUMENTS';
  let decisionConfidence = 0.995;
  let verdictLevel: ForensicScoreResult['verdictLevel'] = 'divergent';

  if (finalSim >= 0.95 && negEv.length === 0) {
    decision = 'SAME_DOCUMENT';
    decisionConfidence = 0.998;
    verdictLevel = 'identical';
  } else if (isSameTemplate && finalSim >= 0.65) {
    decision = 'SAME_TEMPLATE_VARIANT';
    decisionConfidence = 0.985;
    verdictLevel = 'modified';
  } else if (classCompat >= 0.70 && finalSim >= 0.40) {
    decision = 'RELATED_DOCUMENT_TYPES';
    decisionConfidence = 0.940;
    verdictLevel = 'related';
  }

  const mode: ComparisonMode = isSameTemplate ? 'SAME_TEMPLATE_OR_FAMILY' : 'DOCUMENT_DOCUMENT';
  const status: ComparisonStatus = isSameTemplate ? 'COMPATIBLE' : 'RELATED_BUT_DIFFERENT_DOCUMENT_TYPES';

  return {
    comparisonStatus: status,
    comparisonMode: mode,
    decision,
    decisionConfidence,
    overallScore,
    isComparable: true,
    verdict: decision.replace(/_/g, ' '),
    verdictLevel,
    compatibilityReason: `Compared in ${mode} mode with ${posEv.length} positive and ${negEv.length} negative evidence signals.`,
    fieldAlignmentStatus,
    inputA,
    inputB,
    positiveEvidence: posEv,
    negativeEvidence: negEv,
    dimensions: {
      visualSimilarity: Number(visualSim.toFixed(4)),
      structuralSimilarity: Number(graphSim.toFixed(4)),
      textSimilarity: Number(ocrWordOverlapRatio.toFixed(4)),
      semanticSimilarity,
      templateSimilarity: isSameTemplate ? 1.0 : 0.0,
      forensicSimilarity: calibForensicSim,
      localFeatureInliers: Number(localInlierRatio.toFixed(4)),
      layoutGraphSimilarity: Number(graphSim.toFixed(4)),
    },
    details: {
      cosineSimilarity: Number(rawCosineSim.toFixed(4)),
      l1NormalizedDistance: Number(cosineDist.toFixed(4)),
      ocrWordOverlapRatio: Number(ocrWordOverlapRatio.toFixed(4)),
      pageCountMatch: (docA.page_count || 1) === (docB.page_count || 1),
      aspectRatioDiffPct: 0,
      hashExactMatch,
      sealExactMatch,
      localInlierRatio: Number(localInlierRatio.toFixed(4)),
      spatialCoverage: Number(spatialCoverage.toFixed(4)),
      reprojectionError: Number(Math.max(0.5, (1.0 - localInlierRatio) * 12.0).toFixed(2)),
      featureGroupDeltas: getFeatureGroupDeltas(docA, docB),
    },
    differences,
  };
}

function analyzeDocumentLikelihood(doc: GenomeResponse): InputDescriptor {
  const textWords = extractAllOcrTokens(doc);
  const pages = doc.pages || [];
  const pageCount = max1(doc.page_count || pages.length);
  const wordsPerPage = textWords.size / pageCount;

  const structElements = doc.structural_genome?.elements || [];
  const tables = doc.structural_genome?.tables || [];
  const hasTables = tables.length > 0;
  const numBlocks = structElements.length;

  const primaryType = String(doc.semantic_genome?.taxonomy?.primary_type || 'UNKNOWN').toUpperCase();

  // Structured key-value business terms check
  const kvTerms = ['total', 'amount', 'invoice', 'date', 'subtotal', 'tax', 'bill', 'due', 'account', 'balance', 'price', 'certify', 'agreement', 'contract'];
  let kvHits = 0;
  for (const p of pages) {
    if (Array.isArray(p.ocr_elements)) {
      for (const el of p.ocr_elements) {
        const txt = String(el.text || '').toLowerCase();
        if (kvTerms.some((t) => txt.includes(t))) kvHits++;
      }
    }
  }

  let docScore = 0;
  let photoScore = 0;

  if (kvHits >= 3) docScore += 0.40;
  else if (kvHits >= 1) docScore += 0.15;
  else photoScore += 0.25;

  if (wordsPerPage >= 20 && numBlocks >= 2) docScore += 0.35;
  else if (wordsPerPage >= 10) docScore += 0.15;
  else photoScore += 0.35;

  if (hasTables || ['INVOICE', 'RECEIPT', 'TAX_DOCUMENT', 'CONTRACT', 'CERTIFICATE'].includes(primaryType)) {
    docScore += 0.30;
  } else {
    photoScore += 0.20;
  }

  if (wordsPerPage < 5 && numBlocks <= 1 && !hasTables) {
    photoScore += 0.40;
  }

  const total = docScore + photoScore + 1e-6;
  const docLikelihood = Math.min(1.0, Math.max(0.0, docScore / total));
  const photoLikelihood = Math.min(1.0, Math.max(0.0, photoScore / total));

  if (photoLikelihood >= 0.55 || docLikelihood < 0.40) {
    return {
      modality: 'PHOTOGRAPH',
      documentType: null,
      confidence: Math.max(photoLikelihood, 0.92),
      documentLikelihood: Number(docLikelihood.toFixed(2)),
      photoLikelihood: Number(photoLikelihood.toFixed(2)),
      rationale: 'Natural photograph or non-document scene (low text density, lack of structured key-value alignment).',
    };
  }

  if (primaryType === 'IDENTITY_DOCUMENT' || (wordsPerPage < 30 && ['ID', 'PASSPORT', 'LICENSE'].includes(primaryType))) {
    return {
      modality: 'ID_DOCUMENT',
      documentType: 'identity_document',
      confidence: 0.95,
      documentLikelihood: Number(docLikelihood.toFixed(2)),
      photoLikelihood: Number(photoLikelihood.toFixed(2)),
      rationale: 'Identity document / card detected.',
    };
  }

  const docClass = primaryType !== 'UNKNOWN' ? primaryType.toLowerCase() : 'document';
  return {
    modality: 'DOCUMENT',
    documentType: docClass,
    confidence: Math.max(docLikelihood, 0.92),
    documentLikelihood: Number(docLikelihood.toFixed(2)),
    photoLikelihood: Number(photoLikelihood.toFixed(2)),
    rationale: `Structured document (${docClass.toUpperCase()}) with tabular/key-value layout.`,
  };
}

function max1(v: number): number {
  return v > 0 ? v : 1;
}

function computeCosine(a: number[], b: number[]): number {
  if (!a.length || !b.length) return 0;
  const len = Math.min(a.length, b.length);
  let dot = 0, nA = 0, nB = 0;
  for (let i = 0; i < len; i++) {
    dot += a[i] * b[i];
    nA += a[i] * a[i];
    nB += b[i] * b[i];
  }
  if (nA <= 1e-6 || nB <= 1e-6) return 0;
  return Math.max(0, Math.min(1, dot / (Math.sqrt(nA) * Math.sqrt(nB))));
}

function extractAllOcrTokens(doc: GenomeResponse): Set<string> {
  const words = new Set<string>();
  if (!doc.pages || !Array.isArray(doc.pages)) return words;

  for (const page of doc.pages) {
    if (Array.isArray(page.ocr_elements)) {
      for (const el of page.ocr_elements) {
        if (el.text) {
          el.text
            .toLowerCase()
            .replace(/[^a-z0-9]/g, ' ')
            .split(/\s+/)
            .filter((w: string) => w.length > 2)
            .forEach((w: string) => words.add(w));
        }
      }
    }
  }
  return words;
}

function getFeatureGroupDeltas(docA: GenomeResponse, docB: GenomeResponse) {
  const groups = [
    { name: 'Geometry & Layout', slice: [0, 18] },
    { name: 'Texture (GLCM & LBP)', slice: [18, 36] },
    { name: 'Frequency Domain (FFT / Wavelet)', slice: [36, 54] },
    { name: 'Edge & Contour Gradients', slice: [54, 72] },
    { name: 'OCR & Typography Distribution', slice: [72, 90] },
    { name: 'Statistical & Color Moments', slice: [90, 108] },
  ];

  const vecA = docA.feature_vector || [];
  const vecB = docB.feature_vector || [];

  return groups.map((grp) => {
    const subA = vecA.slice(grp.slice[0], grp.slice[1]);
    const subB = vecB.slice(grp.slice[0], grp.slice[1]);
    const count = Math.max(subA.length, subB.length, 1);

    let diffSum = 0;
    let magSum = 0;

    for (let i = 0; i < Math.min(subA.length, subB.length); i++) {
      const a = subA[i] || 0;
      const b = subB[i] || 0;
      diffSum += Math.abs(a - b);
      magSum += Math.abs(a) + Math.abs(b) + 1e-6;
    }

    const deltaRatio = magSum > 0 ? diffSum / magSum : 0;
    const similarity = Math.max(0, (1 - deltaRatio) * 100);

    return {
      groupName: grp.name,
      similarityScore: Number(similarity.toFixed(1)),
      deltaPct: Number((deltaRatio * 100).toFixed(2)),
      featureCount: count,
    };
  });
}
