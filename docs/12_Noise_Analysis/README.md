# Document 12 — Noise Analysis Engine
## GDI: Sensor Noise, Compression Artifacts, and Noise Forensics

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [05_Genome_Extraction_Engine], [11_Frequency_Analysis], [15_Micro_DNA_Engine]

---

## Table of Contents

1. [Purpose and Forensic Rationale](#1-purpose-and-forensic-rationale)
2. [Feature Groups and Definitions](#2-feature-groups-and-definitions)
3. [Sensor Noise Model Analysis](#3-sensor-noise-model-analysis)
4. [Photo Response Non-Uniformity (PRNU)](#4-photo-response-non-uniformity-prnu)
5. [JPEG Artifact Profile](#5-jpeg-artifact-profile)
6. [Compression History Detection](#6-compression-history-detection)
7. [CFA Pattern and Demosaicing Analysis](#7-cfa-pattern-and-demosaicing-analysis)
8. [Noise Inconsistency Detection](#8-noise-inconsistency-detection)
9. [Mathematical Foundations](#9-mathematical-foundations)
10. [Implementation](#10-implementation)

---

## 1. Purpose and Forensic Rationale

Noise analysis exploits the fact that every image acquisition device leaves a distinctive, measurable noise signature in the images it produces. This signature has two components:

**Fixed Pattern Noise (FPN)**: Systematic, repeatable noise that is the same for every image captured by a specific device. Caused by pixel-to-pixel sensitivity variations in the sensor and fixed defects. The Photo Response Non-Uniformity (PRNU) is the dominant component.

**Random Noise**: Shot noise and read noise that vary randomly between captures. Characterized by statistical properties (distribution, spatial correlation) that reflect the device and processing pipeline.

When a document is manipulated:
- Regions from different sources have different device noise signatures
- A digitally modified region has no sensor noise (or has noise inconsistent with the surrounding authentic region)
- A region that was re-photographed or re-scanned has a different noise signature than the rest of the document

Noise analysis can localize such manipulations with high spatial precision, often at the pixel level.

### 1.1 Established Basis

PRNU-based camera identification is a well-established forensic technique:
- Lukas et al. (2006) demonstrated device identification via PRNU with near-perfect accuracy
- Chen et al. (2008) extended PRNU analysis to forgery detection
- Goljan et al. (2009) demonstrated PRNU-based manipulation detection

GDI applies these techniques to document forensics.

---

## 2. Feature Groups and Definitions

| Group | Features (std) | Features (deep) | Significance |
|-------|----------------|-----------------|-------------|
| Sensor Noise Model | 20 | 35 | FS2 (Major) |
| JPEG Artifact Profile | 15 | 20 | FS2 (Major) |
| Compression History | 10 | 15 | FS2 (Major) |
| CFA Pattern / Demosaicing | 8 | 20 | FS2 (Major) |
| **Total** | **53** | **90** | — |

---

## 3. Sensor Noise Model Analysis

### 3.1 Feature Definitions

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `noise.sensor.sigma_mean` | Mean noise standard deviation across image | float | FS2 |
| `noise.sensor.sigma_spatial_variation` | Spatial variation of noise level | float | FS2 |
| `noise.sensor.distribution_type` | Identified noise distribution (Gaussian/Poisson/mixed) | enum | FS2 |
| `noise.sensor.poisson_factor` | Signal-dependent noise factor (Poisson component weight) | float | FS2 |
| `noise.sensor.gaussian_sigma` | Gaussian noise component std deviation | float | FS2 |
| `noise.sensor.spatial_correlation` | Spatial correlation of noise (neighboring pixels) | float[5] | FS2 |
| `noise.sensor.striping_pattern` | Evidence of row-striping (fixed pattern noise) | 0–1 | FS2 |
| `noise.sensor.column_striping_pattern` | Evidence of column-striping | 0–1 | FS2 |
| `noise.sensor.local_noise_map` | Per-region noise level map (8×8 grid) | float[64] | FS1 |
| `noise.sensor.noise_inconsistency_score` | Score for spatial inconsistency of noise | 0–1 | FS1 |

### 3.2 Noise Estimation Algorithm

GDI uses the **Median Absolute Deviation (MAD) estimator** for noise estimation (Donoho & Johnstone, 1994):

1. Apply single-level wavelet transform (Haar wavelet)
2. Extract the high-frequency diagonal detail subband (HH1)
3. Noise estimate: `σ = median(|HH1|) / 0.6745`

The division by 0.6745 converts the MAD to an estimate of the Gaussian noise standard deviation.

This estimator is robust because:
- It operates in the HH1 subband where image content energy is minimal (most energy is noise)
- The median is robust to outliers (edges, strong features)
- It is computationally efficient (O(N log N) via wavelet + median)

### 3.3 Noise Model Fitting

The observed noise distribution is fit to a heteroscedastic noise model:
```
σ²(I) = a × I + b
```
where I is the local mean image intensity, a is the Poisson component factor (signal-dependent), and b is the Gaussian component variance (signal-independent).

Parameters a and b are estimated via least-squares fitting of (local_mean, local_variance) pairs across the image. The fitted parameters characterize the device's noise model.

---

## 4. Photo Response Non-Uniformity (PRNU)

### 4.1 PRNU as a Device Fingerprint

PRNU is caused by pixel-level variations in sensor sensitivity. It appears as a weak, spatially fixed pattern superimposed on every image captured by a specific device.

For document forensics, PRNU is used to:
1. Identify the specific scanner or camera used to produce a scanned document
2. Detect regions of a document that were acquired by a different device (by showing inconsistent PRNU)

### 4.2 PRNU Extraction Algorithm

PRNU is extracted using the following procedure (Lukas et al., 2006):

1. **Denoise the image**: Apply a denoising filter (wavelet denoising with Wiener filtering, or BM3D) to obtain a "clean" estimate of the image content Î
2. **Extract noise residual**: W = I - Î (noise residual ≈ PRNU + random noise)
3. **Reduce content contribution**: Apply Wiener filter to W to suppress non-random content artifacts
4. **PRNU estimate**: K ≈ W/Î (normalized noise residual)

For template documents: PRNU is estimated and stored as part of the template genome.

For submitted documents: PRNU is extracted and correlated with the template's PRNU (see §4.3).

### 4.3 Feature Definitions

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `noise.prnu.correlation_coefficient` | Pearson correlation between submitted PRNU and template PRNU | -1 to 1 | FS2 |
| `noise.prnu.pce` | Peak-to-Correlation Energy ratio (device match score) | float | FS1 |
| `noise.prnu.spatial_consistency` | Spatial consistency of PRNU across document | 0–1 | FS1 |
| `noise.prnu.localized_pce_map` | Per-region PCE map (8×8 grid) | float[64] | FS1 |
| `noise.prnu.anomalous_region_count` | Regions with significantly different PRNU | count | FS1 |

**Peak-to-Correlation Energy (PCE)**:
```
PCE = |corr(K₁, K₂)[peak]|² / (mean(|corr(K₁, K₂)|²) - |corr(K₁, K₂)[peak]|²)
```

PCE > 60 is considered a strong match; PCE < 30 suggests different devices. The spatial PCE map localizes regions where the submitted document's PRNU diverges from the template's — directly identifying manipulated regions.

---

## 5. JPEG Artifact Profile

### 5.1 Feature Definitions

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `noise.jpeg.quality_factor` | Estimated JPEG quality factor | int[1–100] | FS2 |
| `noise.jpeg.quantization_table_luminance` | Estimated luminance quantization table | int[64] | FS2 |
| `noise.jpeg.quantization_table_chrominance` | Estimated chrominance quantization table | int[64] | FS2 |
| `noise.jpeg.blocking_strength` | Strength of 8×8 block boundary artifacts | float | FS2 |
| `noise.jpeg.ringing_strength` | Strength of JPEG ringing artifacts | float | FS2 |
| `noise.jpeg.artifact_inconsistency` | Spatial inconsistency in JPEG artifact level | 0–1 | FS1 |

### 5.2 Artifact Inconsistency Detection

If a document has been compressed at a specific JPEG quality level, the compression artifacts should be spatially uniform throughout the document. A region with significantly different artifact level was either:
- Manipulated at a different quality setting
- Added from a source compressed at a different quality

The artifact inconsistency score measures the coefficient of variation (CV) of the blocking strength across 8×8 analysis windows:
```
artifact_inconsistency = CV(blocking_strength across all windows)
                       = std(blocking_strength) / mean(blocking_strength)
```

---

## 6. Compression History Detection

### 6.1 Compression Chain Reconstruction

The goal is to reconstruct the sequence of compression operations that a document has undergone. The forensic evidence includes:

1. **JPEG quantization trace**: If the current image is JPEG, the quantization table identifies the final compression step
2. **Double-compression signature**: As described in [11_Frequency_Analysis §6], reveals prior JPEG compression
3. **Block offset inconsistency**: If the 8×8 DCT blocks are misaligned with the expected grid, the image has been cropped or padded since compression, suggesting editing

### 6.2 Feature Definitions

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `noise.history.estimated_compression_count` | Estimated number of compression cycles | count | FS2 |
| `noise.history.primary_quality_estimate` | Quality of earliest detected compression step | int | FS2 |
| `noise.history.secondary_quality_estimate` | Quality of second compression step (if double) | int | FS2 |
| `noise.history.block_offset` | Estimated block grid offset (crop detection) | (int,int) | FS2 |
| `noise.history.resize_evidence` | Evidence of prior resize operation | 0–1 | FS2 |

---

## 7. CFA Pattern and Demosaicing Analysis

### 7.1 Background

Digital cameras capture images using a Color Filter Array (CFA) — typically the Bayer pattern (RGGB) — where each pixel captures only one color channel. Demosaicing algorithms reconstruct the missing channels. Different demosaicing algorithms leave distinctive artifacts in the final image.

For documents photographed with a camera (rather than scanned), CFA demosaicing artifacts can:
1. Identify the camera model (different cameras use different demosaicing algorithms)
2. Detect regions that were not captured by a camera (e.g., a digitally inserted element has no demosaicing artifacts)

### 7.2 CFA Detection Algorithm (Ferrara et al., 2012)

CFA demosaicing produces inter-channel correlations at specific spatial frequencies. Detection:
1. Compute the DFT of each color channel
2. Look for peaks at specific frequencies corresponding to the CFA pattern (typically f=0.5 cycles/pixel for Bayer)
3. Compute the inter-channel correlation at the CFA frequency
4. Regions without CFA artifacts are inconsistent with camera capture

### 7.3 Feature Definitions

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `noise.cfa.pattern_detected` | CFA pattern detected in image | boolean | FS2 |
| `noise.cfa.pattern_type` | Detected CFA pattern type (RGGB/BGGR/GRBG/GBRG) | enum | FS2 |
| `noise.cfa.correlation_strength` | Strength of inter-channel CFA correlation | float | FS2 |
| `noise.cfa.consistency_map` | Per-region CFA consistency score (8×8) | float[64] | FS1 |
| `noise.cfa.anomalous_region_fraction` | Fraction of regions without expected CFA artifacts | 0–1 | FS1 |

---

## 8. Noise Inconsistency Detection

### 8.1 Algorithm

Noise inconsistency detection is the primary forensic output of the Noise Analysis Engine:

1. Divide document into 50×50 pixel analysis windows
2. For each window: estimate local noise level σ_local
3. Build expected noise model E[σ_local] from template's noise map
4. Compute deviation: D(w) = |σ_local(w) - E[σ_local(w)]| / std(σ_local across authentic samples)
5. Windows with D(w) > 3.0 are flagged as noise anomalies
6. Cluster anomalous windows using connected-component analysis
7. Report anomaly clusters with bounding boxes and anomaly scores

### 8.2 Forensic Interpretation

| Noise Pattern | Forensic Interpretation |
|---------------|------------------------|
| Region with significantly lower noise than surroundings | Digitally smoothed region (content removal, filtering) |
| Region with significantly higher noise | Added from a noisier source; scan artifact |
| Abrupt noise boundary along a straight line | Sharp cut-paste boundary |
| Uniform very low noise throughout | AI-generated or CGI document (no physical acquisition) |
| Noise level increase in one color channel | Channel-specific manipulation |

---

## 9. Mathematical Foundations

### 9.1 Heteroscedastic Noise Model

The Poisson-Gaussian noise model:
```
I_observed = I_true + Poisson(a × I_true) + Gaussian(0, b)
≈ I_true + N(0, a × I_true + b)  [for large signal]
```

Parameters a (gain) and b (read noise variance) are estimated by:
```
Minimize Σ_windows (var(window) - a × mean(window) - b)²
```
over all image windows.

### 9.2 PRNU Correlation Test

The hypothesis test for PRNU matching:
- H₀: The submitted document was NOT acquired by the same device as the template
- H₁: The submitted document WAS acquired by the same device

Test statistic:
```
PCE = max(|ρ(K₁, K₂)|²) / σ²_corr
```
where ρ is the spatial cross-correlation of PRNU estimates K₁ (submitted) and K₂ (template), and σ²_corr is the expected variance of the correlation under H₀.

PCE follows an approximately exponential distribution under H₀, enabling p-value computation.

---

## 10. Implementation

| Task | Algorithm | Library |
|------|-----------|---------|
| Wavelet noise estimation | MAD estimator, Haar wavelet | PyWavelets |
| Noise model fitting | Least squares | SciPy |
| Image denoising (PRNU) | BM3D algorithm | bm3d library (C extension) |
| PRNU correlation | Normalized cross-correlation | NumPy FFT |
| DCT quantization estimation | Maximum likelihood | Custom NumPy |
| CFA detection | FFT cross-channel correlation | NumPy FFT |
| Anomaly clustering | DBSCAN | scikit-learn |

**Processing time**: P50 4s, P95 10s per page at 300 DPI (BM3D denoising dominates).

---

*Previous: [11_Frequency_Analysis](../11_Frequency_Analysis/README.md)*
*Next: [13_Metadata_Analysis](../13_Metadata_Analysis/README.md)*
*Return to: [Master Index](../README.md)*
