# Document 10 — Texture Analysis Engine
## GDI: Surface, Paper, and Ink Texture Forensics

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [05_Genome_Extraction_Engine], [06_Document_Reconstruction_Engine], [11_Frequency_Analysis]

---

## Table of Contents

1. [Purpose and Forensic Rationale](#1-purpose-and-forensic-rationale)
2. [Feature Groups and Definitions](#2-feature-groups-and-definitions)
3. [Paper Grain Analysis (GLCM)](#3-paper-grain-analysis-glcm)
4. [Local Binary Pattern (LBP) Analysis](#4-local-binary-pattern-lbp-analysis)
5. [Ink Texture Analysis](#5-ink-texture-analysis)
6. [Region-Specific Texture Analysis](#6-region-specific-texture-analysis)
7. [Texture Inconsistency Detection](#7-texture-inconsistency-detection)
8. [Implementation and Algorithms](#8-implementation-and-algorithms)
9. [Mathematical Foundations](#9-mathematical-foundations)

---

## 1. Purpose and Forensic Rationale

Texture analysis operates on the micro-structure of the document surface. For physical documents that have been scanned or photographed, the document texture captures:

- **Paper grain**: The characteristic micro-structure of the paper substrate (fiber direction, coating roughness, surface irregularities)
- **Ink texture**: The microscopic appearance of ink on paper (spread, absorption, grain interaction)
- **Print pattern**: For laser-printed documents, the halftone pattern and toner distribution; for inkjet, the droplet pattern
- **Surface wear**: Scratches, folds, smudges, and aging artifacts

For digital-native documents (PDFs rendered to screen), texture analysis captures:
- **Compression artifact texture**: The distinctive block patterns and ringing of JPEG compression
- **Rendering surface**: Background and whitespace texture from the rendering pipeline

### 1.1 Forensic Value

When a physical document is manipulated:
- A region covered with opaque white and re-typed produces locally different paper and ink texture (the cover-up material and new ink have different absorption and surface properties)
- A region digitally manipulated in a scan produces different compression artifacts and noise texture
- A forged document printed on different paper has different substrate texture throughout

Texture anomalies are among the most difficult to eliminate for a sophisticated forger because they are invisible to the naked eye and require sub-millimeter imaging to detect.

---

## 2. Feature Groups and Definitions

| Group | Features (std) | Features (deep) | Significance |
|-------|----------------|-----------------|-------------|
| Paper Grain Statistics | 20 | 30 | FS2 (Major) |
| Ink Texture | 15 | 20 | FS2 (Major) |
| GLCM Descriptors | 13 | 13 | FS2 (Major) |
| LBP Histograms | 16 | 17 | FS2 (Major) |
| **Total** | **64** | **80** | — |

---

## 3. Paper Grain Analysis (GLCM)

### 3.1 Gray-Level Co-occurrence Matrix (GLCM)

The GLCM is a statistical method for examining texture. It describes the frequency with which pairs of pixels with specific gray-level values occur at a specified spatial relationship (distance d, angle θ).

**Formal definition**:
```
GLCM[i,j] = count{(p,q) : I(p)=i AND I(q)=j AND (q-p)=d}
```
where I is the grayscale image, and d is the displacement vector.

GDI computes GLCMs at four angles (0°, 45°, 90°, 135°) and three distances (1, 2, 3 pixels), then averages over angles for rotational invariance.

### 3.2 GLCM Feature Definitions

From the GLCM, 13 Haralick features (Haralick et al., 1973) are computed:

| Feature ID | Description | Formula |
|------------|-------------|---------|
| `texture.glcm.energy` | Angular Second Moment (uniformity) | Σ GLCM[i,j]² |
| `texture.glcm.entropy` | Information content | -Σ GLCM[i,j] × log(GLCM[i,j]) |
| `texture.glcm.contrast` | Intensity difference moment | Σ (i-j)² × GLCM[i,j] |
| `texture.glcm.homogeneity` | Inverse difference moment | Σ GLCM[i,j] / (1 + |i-j|) |
| `texture.glcm.correlation` | Linear dependency of gray levels | Σ (i-μ_i)(j-μ_j)GLCM[i,j] / (σ_i σ_j) |
| `texture.glcm.dissimilarity` | Weighted contrast | Σ |i-j| × GLCM[i,j] |
| `texture.glcm.asm` | Alternate second moment | Σ GLCM[i,j]² |
| `texture.glcm.variance` | Variance | Σ (i-μ)² × GLCM[i,j] |
| `texture.glcm.idm` | Inverse Difference Moment | Σ GLCM[i,j] / (1 + (i-j)²) |
| `texture.glcm.savg` | Sum Average | mean of GLCM marginal sums |
| `texture.glcm.svar` | Sum Variance | variance of GLCM marginal sums |
| `texture.glcm.sentropy` | Sum Entropy | -Σ p_s log(p_s) |
| `texture.glcm.imc2` | Information Measure of Correlation 2 | sqrt(1 - exp(-2×(H_XY2 - H_XY))) |

### 3.3 Extraction Region

GLCM features are computed on the document's **whitespace regions** (non-content areas): these regions expose the paper/substrate texture without contamination from ink or toner. For color images, the analysis is performed on the grayscale luminance channel within whitespace regions.

For documents with very little whitespace (densely packed text), GLCM is computed on the background of character inter-strokes (the white space within letters like 'o', 'e').

---

## 4. Local Binary Pattern (LBP) Analysis

### 4.1 LBP Definition

Local Binary Patterns (Ojala et al., 2002) encode the local texture structure of each pixel:

For each pixel p with intensity I(p), examine P equally spaced neighbors on a circle of radius R:
```
LBP(p) = Σ_{k=0}^{P-1} s(I(neighbor_k) - I(p)) × 2^k
where s(x) = 1 if x ≥ 0, else 0
```

GDI uses the **uniform LBP** variant (P=8, R=1 and P=16, R=2), which counts only LBP values with at most 2 bit transitions (circular). Uniform patterns account for ~90% of texture patterns in natural images and are rotationally invariant.

### 4.2 LBP Feature Definitions

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `texture.lbp.histogram_r1_p8` | Normalized histogram of uniform LBP codes (R=1, P=8) | float[59] | FS2 |
| `texture.lbp.histogram_r2_p16` | Normalized histogram (R=2, P=16) | float[243] | FS2 |
| `texture.lbp.uniformity_score` | Fraction of uniform patterns in LBP | 0–1 | FS2 |
| `texture.lbp.dominant_pattern` | Most frequent LBP code | int | FS2 |
| `texture.lbp.chi_square_distance` | Chi-square distance between submitted and template LBP histograms | float | FS1 |

The chi-square distance is the primary LBP-based comparison metric:
```
χ²(submitted, template) = Σ_k (h_s(k) - h_t(k))² / (h_s(k) + h_t(k))
```

A large chi-square distance indicates different surface texture characteristics.

---

## 5. Ink Texture Analysis

### 5.1 Feature Definitions

Ink texture analysis characterizes the micro-structure of ink/toner application:

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `texture.ink.density_mean` | Mean ink density in text strokes | 0–1 | FS2 |
| `texture.ink.density_std` | Std dev of ink density within strokes | 0–1 | FS2 |
| `texture.ink.density_uniformity` | Spatial uniformity of ink within strokes | 0–1 | FS2 |
| `texture.ink.boundary_sharpness` | Mean gradient magnitude at ink-paper boundaries | float | FS2 |
| `texture.ink.fiber_absorption` | Evidence of ink absorption into paper fibers (feathering) | 0–1 | FS2 |
| `texture.ink.toner_satellite` | Count of toner satellite dots around strokes | count/mm² | FS2 |
| `texture.ink.color_consistency` | Color consistency of ink across document | 0–1 | FS2 |
| `texture.ink.age_signature` | Evidence of ink aging (chemical shift, fading) | 0–1 | FS3 |

### 5.2 Ink Density Analysis

Within each text stroke (identified by thresholded binary mask):
1. Measure the actual pixel intensities (inverted: 255 = max ink, 0 = no ink)
2. Within the stroke mask: compute mean and std of intensity
3. High std within a stroke indicates uneven ink application (consistent with inkjet, inconsistent for laser)

### 5.3 Toner Satellite Detection

Laser printers produce characteristic "satellite dots" — small, isolated toner deposits adjacent to main strokes. These are caused by electrostatic charge dispersion during the fusing process.

Detection:
1. Apply binary threshold to identify all ink pixels
2. Label connected components (OpenCV `connectedComponentsWithStats`)
3. Filter components with area < 4 px² (typical satellite size range)
4. Count satellites per unit area (satellites/mm²)
5. This is printer-type specific: high satellite count → laser; very low → inkjet

---

## 6. Region-Specific Texture Analysis

For forensic localization, texture analysis is also performed independently on a grid of document regions:

1. Divide the document into an N×M grid (N=8, M=8 for standard; N=16, M=16 for deep)
2. For each grid cell: compute a texture fingerprint (abbreviated GLCM + LBP)
3. Compare each cell's texture fingerprint to the corresponding cell in the template document
4. Cells with high texture divergence (χ² distance > threshold) are flagged as anomalous

This grid-based analysis is particularly effective for detecting paste-over manipulations, where a region of the document has been covered and replaced, leaving different texture characteristics in that specific region.

---

## 7. Texture Inconsistency Detection

### 7.1 Anomaly Algorithm

1. Compute texture fingerprint for every non-overlapping 100×100 pixel window (sliding with 50px step)
2. Cluster windows into texture groups using k-means (k=3: background, text, mixed)
3. For background windows: compute χ² distance against template's background texture model
4. Flag windows where χ² distance > threshold (adaptive, based on template variance)
5. Produce anomaly score map at window resolution, upsampled to full resolution with bilinear interpolation

### 7.2 Interpretation

Texture anomaly clusters correspond to:
- **Isolated high-anomaly regions**: Local manipulation (paste-over, digital erasure)
- **Anomaly along horizontal lines**: Scan seam or composite image
- **Overall high texture deviation**: Document scanned on different scanner, or from different paper
- **Anomaly in specific character groups**: Character-level substitution (covered with white paint, retyped)

---

## 8. Implementation and Algorithms

| Task | Algorithm | Library |
|------|-----------|---------|
| GLCM computation | Custom vectorized NumPy implementation | NumPy |
| Haralick features | Computed from GLCM | Custom Python |
| LBP computation | Ojala uniform LBP | scikit-image `feature.local_binary_pattern` |
| Chi-square distance | Standard formula | SciPy |
| Connected components | Two-pass labeling | OpenCV `connectedComponentsWithStats` |
| Ink density analysis | Masked intensity statistics | NumPy |
| Grid texture analysis | Sliding window + k-means | scikit-learn |

---

## 9. Mathematical Foundations

### 9.1 GLCM Normalization

Before feature computation, the GLCM is normalized to a probability matrix:
```
P[i,j] = GLCM[i,j] / Σ_{i,j} GLCM[i,j]
```

### 9.2 LBP Texture Similarity

The histogram intersection similarity between two LBP histograms h_1 and h_2:
```
K_int(h_1, h_2) = Σ_k min(h_1(k), h_2(k))
```
This measure ranges [0,1] and is preferred over Euclidean distance for histogram comparison because it is more robust to small histogram perturbations.

### 9.3 Texture Distance for Anomaly Scoring

For each grid cell c, the texture anomaly score is:
```
A_texture(c) = 1 - exp(-χ²(cell_texture, template_texture_model) / λ)
```
where λ is a calibration parameter derived from the template's natural variation model (specifically the χ² distance distribution observed across authentic document samples).

---

*Previous: [09_Rendering_Analysis](../09_Rendering_Analysis/README.md)*
*Next: [11_Frequency_Analysis](../11_Frequency_Analysis/README.md)*
*Return to: [Master Index](../README.md)*
