/**
 * GDI Platform - Multi-Dimensional Forensic Scoring Engine
 *
 * Computes an overall forensic match score (0.0% - 100.0%) comparing two Document Genomes.
 * Evaluates 4 core forensic dimensions:
 *   1. Canonical Feature Vector Similarity (108 dimensions via Cosine + L1 distance) - 40%
 *   2. OCR / Lexical Text Overlap (Tokens, Jaccard, Sequence match) - 25%
 *   3. Structural & Page Geometry Match (Resolution, Aspect Ratio, Skew, Quality metrics) - 20%
 *   4. Cryptographic Hash & Seal Match (SHA-256 binary hash and Feature Seal digest) - 15%
 */

import { GenomeResponse } from '@/types/gdi';

export interface ForensicScoreResult {
  overallScore: number; // 0 to 100
  verdict: string;
  verdictLevel: 'identical' | 'near_match' | 'modified' | 'partial' | 'divergent';
  vectorDeltaPct: number;
  breakdowns: {
    featureVectorScore: number; // 0 to 100
    textOcrScore: number; // 0 to 100
    structuralScore: number; // 0 to 100
    cryptographicScore: number; // 0 to 100
  };
  details: {
    cosineSimilarity: number;
    l1NormalizedDistance: number;
    ocrWordOverlapRatio: number;
    pageCountMatch: boolean;
    aspectRatioDiffPct: number;
    hashExactMatch: boolean;
    sealExactMatch: boolean;
    featureGroupDeltas: Array<{
      groupName: string;
      similarityScore: number;
      deltaPct: number;
      featureCount: number;
    }>;
  };
}

export function computeForensicMatchScore(
  docA: GenomeResponse | null,
  docB: GenomeResponse | null
): ForensicScoreResult {
  if (!docA || !docB) {
    return {
      overallScore: 0,
      verdict: 'No Comparison Data',
      verdictLevel: 'divergent',
      vectorDeltaPct: 0,
      breakdowns: {
        featureVectorScore: 0,
        textOcrScore: 0,
        structuralScore: 0,
        cryptographicScore: 0,
      },
      details: {
        cosineSimilarity: 0,
        l1NormalizedDistance: 0,
        ocrWordOverlapRatio: 0,
        pageCountMatch: false,
        aspectRatioDiffPct: 0,
        hashExactMatch: false,
        sealExactMatch: false,
        featureGroupDeltas: [],
      },
    };
  }

  // 1. Exact Cryptographic Check
  const hashExactMatch =
    Boolean(docA.document_hash_sha256 && docB.document_hash_sha256) &&
    docA.document_hash_sha256 === docB.document_hash_sha256;

  const sealExactMatch =
    Boolean(docA.genome_seal?.sha256_of_features && docB.genome_seal?.sha256_of_features) &&
    docA.genome_seal.sha256_of_features === docB.genome_seal.sha256_of_features;

  if (hashExactMatch && sealExactMatch) {
    return {
      overallScore: 100,
      verdict: '100% IDENTICAL (CRYPTOGRAPHIC TWIN)',
      verdictLevel: 'identical',
      vectorDeltaPct: 0,
      breakdowns: {
        featureVectorScore: 100,
        textOcrScore: 100,
        structuralScore: 100,
        cryptographicScore: 100,
      },
      details: {
        cosineSimilarity: 1.0,
        l1NormalizedDistance: 0,
        ocrWordOverlapRatio: 1.0,
        pageCountMatch: true,
        aspectRatioDiffPct: 0,
        hashExactMatch: true,
        sealExactMatch: true,
        featureGroupDeltas: getFeatureGroupDeltas(docA, docB),
      },
    };
  }

  // 2. Feature Vector Dimension Comparison (Cosine Similarity + L1)
  const vecA = docA.feature_vector || [];
  const vecB = docB.feature_vector || [];
  const minLen = Math.min(vecA.length, vecB.length);

  let dotProduct = 0;
  let normA = 0;
  let normB = 0;
  let sumDiff = 0;
  let sumMag = 0;

  for (let i = 0; i < minLen; i++) {
    const a = vecA[i] || 0;
    const b = vecB[i] || 0;
    dotProduct += a * b;
    normA += a * a;
    normB += b * b;
    sumDiff += Math.abs(a - b);
    sumMag += Math.abs(a) + Math.abs(b) + 1e-6;
  }

  const cosineSim =
    normA > 0 && normB > 0
      ? Math.max(0, Math.min(1, dotProduct / (Math.sqrt(normA) * Math.sqrt(normB))))
      : 0;

  const l1DeltaRatio = minLen > 0 ? sumDiff / sumMag : 1.0;
  const vectorDeltaPct = l1DeltaRatio * 100;
  const featureVectorScore = Math.max(0, Math.min(100, (cosineSim * 0.7 + (1 - l1DeltaRatio) * 0.3) * 100));

  // 3. OCR / Text Overlap Comparison
  const textWordsA = extractAllOcrTokens(docA);
  const textWordsB = extractAllOcrTokens(docB);
  let ocrWordOverlapRatio = 0;

  if (textWordsA.size === 0 && textWordsB.size === 0) {
    ocrWordOverlapRatio = 1.0; // Both non-text or visual only
  } else if (textWordsA.size === 0 || textWordsB.size === 0) {
    ocrWordOverlapRatio = 0.0;
  } else {
    let intersection = 0;
    textWordsA.forEach((word) => {
      if (textWordsB.has(word)) intersection++;
    });
    const union = new Set([...textWordsA, ...textWordsB]).size;
    ocrWordOverlapRatio = union > 0 ? intersection / union : 0;
  }
  const textOcrScore = Math.max(0, Math.min(100, ocrWordOverlapRatio * 100));

  // 4. Structural & Page Geometry Match
  const pageCountA = docA.page_count || docA.pages?.length || 1;
  const pageCountB = docB.page_count || docB.pages?.length || 1;
  const pageCountMatch = pageCountA === pageCountB;
  const pageRatioScore = Math.min(pageCountA, pageCountB) / Math.max(pageCountA, pageCountB);

  const page1MetaA = docA.pages?.[0]?.metadata || {};
  const page1MetaB = docB.pages?.[0]?.metadata || {};
  const aspectA = page1MetaA.width_px && page1MetaA.height_px ? page1MetaA.width_px / page1MetaA.height_px : 1;
  const aspectB = page1MetaB.width_px && page1MetaB.height_px ? page1MetaB.width_px / page1MetaB.height_px : 1;
  const aspectRatioDiffPct = Math.abs(aspectA - aspectB) / Math.max(aspectA, aspectB);
  const aspectScore = Math.max(0, 1 - aspectRatioDiffPct);

  const structuralScore = (pageRatioScore * 0.6 + aspectScore * 0.4) * 100;

  // 5. Cryptographic Score
  let cryptographicScore = 0;
  if (hashExactMatch) cryptographicScore += 50;
  if (sealExactMatch) cryptographicScore += 50;
  if (!hashExactMatch && !sealExactMatch) {
    cryptographicScore = featureVectorScore > 90 ? 30 : 0;
  }

  // 6. Weighted Final Score
  // Weights: Feature Vector (40%), OCR (25%), Structure (20%), Cryptographic (15%)
  const overallScore = Number(
    (
      featureVectorScore * 0.40 +
      textOcrScore * 0.25 +
      structuralScore * 0.20 +
      cryptographicScore * 0.15
    ).toFixed(2)
  );

  let verdict = 'DIVERGENT (DISTINCT DOCUMENT)';
  let verdictLevel: ForensicScoreResult['verdictLevel'] = 'divergent';

  if (overallScore >= 99.5) {
    verdict = '100% IDENTICAL (CRYPTOGRAPHIC TWIN)';
    verdictLevel = 'identical';
  } else if (overallScore >= 90.0) {
    verdict = 'HIGH INTEGRITY MATCH (NEAR-DUPLICATE)';
    verdictLevel = 'near_match';
  } else if (overallScore >= 70.0) {
    verdict = 'MODIFIED DOCUMENT (SHARED TEMPLATE)';
    verdictLevel = 'modified';
  } else if (overallScore >= 40.0) {
    verdict = 'PARTIAL SIMILARITY (STRUCTURAL MATCH)';
    verdictLevel = 'partial';
  }

  return {
    overallScore,
    verdict,
    verdictLevel,
    vectorDeltaPct: Number(vectorDeltaPct.toFixed(4)),
    breakdowns: {
      featureVectorScore: Number(featureVectorScore.toFixed(1)),
      textOcrScore: Number(textOcrScore.toFixed(1)),
      structuralScore: Number(structuralScore.toFixed(1)),
      cryptographicScore: Number(cryptographicScore.toFixed(1)),
    },
    details: {
      cosineSimilarity: Number(cosineSim.toFixed(4)),
      l1NormalizedDistance: Number(l1DeltaRatio.toFixed(4)),
      ocrWordOverlapRatio: Number(ocrWordOverlapRatio.toFixed(4)),
      pageCountMatch,
      aspectRatioDiffPct: Number((aspectRatioDiffPct * 100).toFixed(2)),
      hashExactMatch,
      sealExactMatch,
      featureGroupDeltas: getFeatureGroupDeltas(docA, docB),
    },
  };
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
