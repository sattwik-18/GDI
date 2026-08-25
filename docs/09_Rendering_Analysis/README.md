# Document 09 — Rendering Analysis Engine
## GDI: Rasterization, Anti-aliasing, and Rendering Forensics

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [05_Genome_Extraction_Engine], [08_Typography_Analysis], [12_Noise_Analysis]

---

## Table of Contents

1. [Purpose and Forensic Rationale](#1-purpose-and-forensic-rationale)
2. [Feature Groups and Definitions](#2-feature-groups-and-definitions)
3. [Anti-aliasing Profile Analysis](#3-anti-aliasing-profile-analysis)
4. [Subpixel Rendering Analysis](#4-subpixel-rendering-analysis)
5. [Ink and Toner Spread Analysis](#5-ink-and-toner-spread-analysis)
6. [Edge Sharpness Statistics](#6-edge-sharpness-statistics)
7. [Rasterization Artifact Detection](#7-rasterization-artifact-detection)
8. [Rendering Engine Fingerprinting](#8-rendering-engine-fingerprinting)
9. [Algorithms and Implementation](#9-algorithms-and-implementation)
10. [Mathematical Foundations](#10-mathematical-foundations)

---

## 1. Purpose and Forensic Rationale

Every digital document rendering process leaves a distinctive fingerprint in how it converts vector information (font outlines, geometric shapes) into rasterized pixels. This fingerprint reflects:

- The specific rendering engine (Windows GDI, GDI+, DirectWrite, Quartz, Cairo, FreeType)
- The anti-aliasing algorithm used
- The hinting mode (autohint, native TrueType hints, CFF hinting)
- The output device characteristics (DPI, dot gain, ink spread)
- For physically printed documents: the printer type (laser, inkjet, offset), print resolution, and ink/toner formulation

When a document is digitally manipulated, the manipulated regions are typically rendered by a different engine or at a different time, leaving rendering characteristics inconsistent with the rest of the document.

### Established Basis

Rendering artifact analysis is a well-established sub-field of digital forensics:
- Farid & Lyu (2003) demonstrated printer fingerprinting via rasterization artifacts
- Comesa & Gloe (2013) demonstrated scanner model identification via noise artifacts
- Mikkilineni et al. (2010) demonstrated printer identification via banding patterns

GDI formalizes and extends these approaches into a systematic, quantitative forensic engine.

---

## 2. Feature Groups and Definitions

| Group | Features (std) | Features (deep) | Significance |
|-------|----------------|-----------------|-------------|
| Anti-aliasing Profile | 15 | 25 | FS2 (Major) |
| Subpixel Rendering | 12 | 20 | FS2 (Major) |
| Ink/Toner Spread | 10 | 15 | FS2 (Major) |
| Edge Sharpness Statistics | 15 | 25 | FS1 (Critical) |
| Rasterization Artifacts | 8 | 15 | FS2 (Major) |
| **Total** | **60** | **100** | — |

---

## 3. Anti-aliasing Profile Analysis

### 3.1 Feature Definitions

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `rendering.aa.mode` | Detected anti-aliasing mode | enum{NONE,GRAYSCALE,SUBPIXEL} | FS2 |
| `rendering.aa.transition_width_mean` | Mean transition width at glyph edges (in pixels) | pixels | FS2 |
| `rendering.aa.transition_width_std` | Std dev of transition widths | pixels | FS2 |
| `rendering.aa.gamma_estimate` | Estimated rendering gamma | float | FS2 |
| `rendering.aa.consistency_score` | Fraction of edges with consistent AA mode | 0–1 | FS1 |
| `rendering.aa.mixed_mode_count` | Number of regions with mixed AA modes | count | FS1 |

### 3.2 Anti-aliasing Characterization

**Algorithm**:
1. Extract glyph edge pixels (from gradient magnitude map, top 10% of magnitude)
2. For each edge pixel e, extract a 1D intensity profile perpendicular to the edge
3. Characterize the profile:
   - Measure the transition width (distance from 10% to 90% of intensity change)
   - Check for color fringing (difference between R, G, B channel transitions)
4. Classify:
   - Transition width < 1.5 px + no fringing → NO_AA
   - Transition width 1.5–3.5 px + no fringing → GRAYSCALE_AA
   - Transition width 1.5–3.5 px + color fringing → SUBPIXEL_AA

### 3.3 Gamma Estimation

Rendering gamma affects how the intensity gradient at edges is shaped. Different rendering engines use different gamma values (typically 1.0–2.2). 

Estimation method: Fit a gamma-adjusted transition function I(x) = 255 × (x/w)^γ to the measured edge profile by minimizing least-squares error over γ. The estimated γ is a rendering fingerprint.

---

## 4. Subpixel Rendering Analysis

### 4.1 Feature Definitions

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `rendering.subpixel.detected` | Whether subpixel rendering is detected | boolean | FS2 |
| `rendering.subpixel.orientation` | Subpixel stripe orientation (horizontal=ClearType/BGR/RGB, vertical=BGRA) | enum | FS2 |
| `rendering.subpixel.color_order` | Detected subpixel color order (RGB vs BGR) | enum | FS2 |
| `rendering.subpixel.strength` | Magnitude of subpixel color fringing | 0–1 | FS2 |
| `rendering.subpixel.consistency` | Consistency of subpixel order across document | 0–1 | FS1 |

### 4.2 Subpixel Color Order Detection

ClearType (Microsoft's subpixel AA) arranges RGB subpixels left-to-right. This produces characteristic color fringing at text edges:
- Left edges: blue fringe on left, red fringe on right (for RGB order)
- Right edges: red fringe on left, blue fringe on right

Detection:
1. Identify vertical text edges (transitions from text to background)
2. For each edge: measure R, G, B channel values at ±2 pixels from edge center
3. R_left_mean - R_right_mean and B_left_mean - B_right_mean indicate color order
4. Positive ΔR_left and negative ΔB_left → BGR order (more common on non-Windows)
5. Negative ΔR_left and positive ΔB_left → RGB order (common on Windows with ClearType)

---

## 5. Ink and Toner Spread Analysis

### 5.1 Feature Definitions

This group analyzes physical printing characteristics (for scanned physical documents):

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `rendering.ink.spread_mean` | Mean ink spread beyond nominal glyph boundary | pixels | FS2 |
| `rendering.ink.spread_std` | Std dev of ink spread | pixels | FS2 |
| `rendering.ink.dot_gain` | Estimated dot gain percentage | percentage | FS2 |
| `rendering.ink.bleeding` | Evidence of ink bleeding into paper fibers | 0–1 | FS2 |
| `rendering.ink.density_uniformity` | Uniformity of ink density within strokes | 0–1 | FS2 |
| `rendering.ink.saturation_profile` | Channel-wise ink saturation histogram | float[3×20] | FS2 |

### 5.2 Ink Spread Measurement

Ink spread (physical spreading of ink beyond the intended boundary) is measured by:
1. For each glyph: compute the "ideal" boundary from the font's vector outline (if PDF) or from a template rendering
2. Compare the actual ink boundary in the scanned image against the ideal boundary
3. Ink spread = area of ink pixels outside the ideal boundary / total ideal boundary length (in pixels per linear unit)

Ink spread is printer-specific: inkjet printers have more spread than laser printers; lower-quality paper has more spread; certain ink/toner formulations have characteristic spread profiles.

### 5.3 Dot Gain Estimation

Dot gain is the increase in halftone dot area during printing (pressure, ink absorption). It can be estimated from:
- The measured stroke width vs. the expected stroke width from the font at the given size
- Dot gain (%) = (measured_stroke_width - expected_stroke_width) / expected_stroke_width × 100

---

## 6. Edge Sharpness Statistics

### 6.1 Feature Definitions

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `rendering.sharpness.gradient_mean` | Mean gradient magnitude at content edges | 0–255 | FS1 |
| `rendering.sharpness.gradient_std` | Std dev of gradient magnitude | 0–255 | FS1 |
| `rendering.sharpness.laplacian_var` | Laplacian variance (overall sharpness metric) | float | FS1 |
| `rendering.sharpness.local_sharpness_map` | 8×8 grid of local sharpness values | float[64] | FS1 |
| `rendering.sharpness.cross_region_variation` | Coefficient of variation of sharpness across regions | dimensionless | FS1 |
| `rendering.sharpness.mtu_estimate` | Modulation Transfer Unit estimate at Nyquist frequency | float | FS2 |

### 6.2 Local Sharpness Map

The local sharpness map is a key forensic feature: it divides the document into an 8×8 grid of regions and measures the sharpness of each region independently.

**Forensic use**: If one region has significantly different sharpness from surrounding regions, it was likely produced by a different rendering process (different scanner pass, different digital region, different compression settings). This is a localized anomaly signal that maps directly to the heatmap.

**Computation**:
1. Divide document image into 8×8 grid cells
2. For each cell: compute Laplacian variance = var(Laplacian(cell_pixels))
3. The local sharpness map = {cell → Laplacian_variance}
4. Cross-region variation = std(all_cell_variances) / mean(all_cell_variances)

---

## 7. Rasterization Artifact Detection

### 7.1 Feature Definitions

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `rendering.artifacts.banding_detected` | Whether printer banding patterns detected | boolean | FS2 |
| `rendering.artifacts.banding_frequency` | Spatial frequency of detected banding | cycles/inch | FS2 |
| `rendering.artifacts.moire_detected` | Whether moiré patterns detected | boolean | FS2 |
| `rendering.artifacts.moire_frequency` | Spatial frequency of moiré pattern | cycles/inch | FS2 |
| `rendering.artifacts.halftone_detected` | Whether halftone screening detected | boolean | FS2 |
| `rendering.artifacts.halftone_frequency` | Lines per inch of halftone screen | lpi | FS2 |
| `rendering.artifacts.blockiness_score` | 8×8 block boundary artifact score (JPEG blocking) | 0–1 | FS2 |

### 7.2 Banding Detection

Printer banding is a periodic horizontal pattern caused by inconsistent head movement or mechanical vibration in inkjet printers, or by contamination in laser printer drums.

Detection:
1. Compute horizontal 1D power spectrum of gray channel: PSD_horizontal(f)
2. Identify peaks in PSD_horizontal above noise floor
3. Banding frequency = frequency of dominant peak
4. Banding detected = True if peak SNR > 10 dB

### 7.3 Moiré Detection

Moiré patterns appear when a halftone-screened document is rescanned, creating an interference pattern between the halftone screen and the scanner's sampling grid.

Detection:
1. Compute 2D Fourier transform of gray channel image
2. Examine the power spectrum for periodic structures beyond the fundamental document content
3. Identify radially symmetric peaks at unexpected frequencies
4. Moiré frequency = spatial frequency of dominant moiré component

---

## 8. Rendering Engine Fingerprinting

The combination of AA mode, subpixel order, edge sharpness, and artifact patterns forms a **rendering engine fingerprint**.

GDI maintains a rendering engine fingerprint database with profiles for:
- Windows GDI (Windows XP/Vista/7/10/11)
- Windows GDI+ 
- Windows DirectWrite
- macOS Quartz (versions 10.6+)
- Cairo (Linux, various versions)
- FreeType (various rendering modes)
- PDF viewers: Adobe Acrobat 9/X/XI/DC, PDFium, Okular, Preview.app
- Printer types: HP LaserJet series, Canon imageRUNNER, Konica Minolta bizhub, Epson inkjet

**Fingerprint matching** uses nearest-neighbor classification in the rendering feature space, producing:
- Top-3 candidate rendering engines with confidence scores
- Composite rendering engine label: `{OS}/{RenderingAPI}/{Version}`

**Forensic significance**: If the rendering engine fingerprint of a submitted document is inconsistent with what would be expected from the document's claimed origin (e.g., a government form supposedly produced by a specific government system shows macOS Quartz rendering characteristics), this is a significant forensic anomaly.

---

## 9. Algorithms and Implementation

| Task | Algorithm | Library |
|------|-----------|---------|
| Gradient computation | Sobel operator, 3×3 kernel | NumPy/SciPy |
| Edge profile extraction | Line profile interpolation | scikit-image `profile_line` |
| Gamma estimation | Nonlinear least squares | SciPy `curve_fit` |
| Power spectral density | Welch's method | SciPy `signal.welch` |
| 2D FFT | Fast Fourier Transform | NumPy FFT |
| Laplacian variance | 3×3 Laplacian kernel | OpenCV `Laplacian` |
| Local sharpness map | Grid partitioning + Laplacian | NumPy + SciPy |
| Rendering fingerprint matching | k-NN in rendering feature space | scikit-learn `KNeighborsClassifier` |

---

## 10. Mathematical Foundations

### 10.1 Anti-aliasing Transition Model

The intensity profile across an anti-aliased edge is modeled as:
```
I(x) = I_bg + (I_fg - I_bg) × Φ((x - x₀) / σ)
```
where Φ is the cumulative normal distribution function, x₀ is the edge center, and σ is the transition width parameter.

Parameters are estimated by fitting this model to observed intensity profiles using maximum likelihood estimation.

### 10.2 Edge Sharpness Metric

The Laplacian variance for a region R is:
```
V(R) = (1/N) × Σ_p (L(p) - μ_L)²
```
where L(p) = Laplacian(image)(p) = ∇²I(p) and μ_L = mean(L) over region R.

Higher V → sharper region. Comparison: V_submitted_region vs. V_template_region gives relative sharpness.

### 10.3 JPEG Blocking Artifact Score

The 8×8 block boundary artifact score is computed as:
```
BAS = (mean horizontal boundary discontinuity + mean vertical boundary discontinuity) / 2
boundary_discontinuity(b) = |mean(row_b) - mean(row_{b-1})|  for every 8th row b
```

---

*Previous: [08_Typography_Analysis](../08_Typography_Analysis/README.md)*
*Next: [10_Texture_Analysis](../10_Texture_Analysis/README.md)*
*Return to: [Master Index](../README.md)*
