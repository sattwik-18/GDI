# Document 15 — Micro DNA Engine
## GDI: Sub-Pixel and Microscopic Feature Extraction

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [05_Genome_Extraction_Engine], [06_Document_Reconstruction_Engine], [08_Typography_Analysis], [09_Rendering_Analysis]

---

## Table of Contents

1. [Purpose and Forensic Rationale](#1-purpose-and-forensic-rationale)
2. [Feature Groups and Definitions](#2-feature-groups-and-definitions)
3. [Sub-Pixel Edge Profiles](#3-sub-pixel-edge-profiles)
4. [Micro-Texture Fingerprinting](#4-micro-texture-fingerprinting)
5. [Printing Dot Pattern Statistics](#5-printing-dot-pattern-statistics)
6. [Micro-Detail Preservation Analysis](#6-micro-detail-preservation-analysis)
7. [Sub-Pixel Anomaly Mapping](#7-sub-pixel-anomaly-mapping)
8. [Algorithms and Mathematical Foundations](#8-algorithms-and-mathematical-foundations)
9. [Performance and Resource Requirements](#9-performance-and-resource-requirements)

---

## 1. Purpose and Forensic Rationale

The Micro DNA Engine operates at the physical limits of optical and digital resolution. Operating at 600+ DPI (or sub-pixel interpolated representations derived from high-resolution scans), this engine analyzes **microscopic structural anomalies** that cannot be detected by conventional macro-level analysis.

**Forensic Rationale**:
Even the most sophisticated digital forgeries or physical high-resolution copy prints leave microscopic artifacts:
- **Sub-pixel edge jitter**: Human-edited stroke edges suffer from interpolation artifacts, anti-aliasing irregularities, or vector-to-raster quantization errors at sub-pixel scales.
- **Toner Halftone/Dot Pattern Anomalies**: Laser printers emit specific microscopic halftone screening patterns (screen angle, dot shape, dot frequency). Inkjet printers emit characteristic microscopic spray satellite distributions. Re-printing or editing introduces secondary halftone interference (Moiré) or pattern disruption.
- **Micro-edge curvature continuous derivative**: Authentic printed glyphs exhibit physical fluid-dynamics or electrostatic toner dispersion profiles along stroke edges. Digital modifications disrupt these continuous boundary derivatives.

---

## 2. Feature Groups and Definitions

| Group | Features (std) | Features (deep) | Significance |
|-------|----------------|-----------------|-------------|
| Sub-Pixel Edge Profiles | 40 | 70 | FS1 (Critical) |
| Micro-Texture Fingerprints | 30 | 50 | FS1 (Critical) |
| Printing Dot Pattern Stats | 20 | 40 | FS1 (Critical) |
| Micro-Detail Preservation | 15 | 40 | FS2 (Major) |
| **Total** | **105** | **200** | — |

---

## 3. Sub-Pixel Edge Profiles

Sub-pixel edge analysis localizes edge boundaries with sub-pixel accuracy ($<0.1 \text{ pixel}$) using moment-based or gradient-fitting techniques.

### 3.1 Sub-Pixel Edge Detection Algorithm
Using Partial Area Effect and Zernike Moments ($M_{p,q}$):
1. For an edge pixel $p(x,y)$, compute 2D Zernike moments up to order 7 over a localized disk window.
2. Determine sub-pixel edge parameters:
   - Edge orientation angle $\phi = \arctan2(\text{Im}(Z_{11}), \text{Re}(Z_{11}))$
   - Sub-pixel distance from pixel center $l = \frac{Z_{20}}{Z_{11}'}$
   - Background intensity $k$, Foreground intensity $h$
3. Compute the sub-pixel edge coordinate: $(x_s, y_s) = (x + l \cos\phi, y + l \sin\phi)$.

### 3.2 Feature Definitions

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `microdna.edge.subpixel_jitter_std` | Standard deviation of sub-pixel edge placement along linear strokes | sub-pixels | FS1 |
| `microdna.edge.curvature_derivative` | Mean absolute 2nd derivative of edge curvature $d^2\kappa / ds^2$ | $1/\text{px}^2$ | FS1 |
| `microdna.edge.gradient_transition_width` | Sub-pixel width of 10%-to-90% intensity transition | sub-pixels | FS1 |
| `microdna.edge.acutance` | Micro-acutance (integrated squared gradient across edge) | float | FS1 |
| `microdna.edge.edge_roughness_spectrum` | Fourier power spectrum of edge boundary roughness (10 bins) | float[10] | FS1 |

---

## 4. Micro-Texture Fingerprinting

Micro-texture fingerprinting models the microscopic interaction between ink/toner and paper fibers.

### 4.1 Feature Definitions

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `microdna.texture.fiber_ink_interlock` | Degree of ink boundary conformity to paper fiber structure | 0–1 | FS1 |
| `microdna.texture.toner_fusing_quality` | Microscopic toner void ratio within solid fill regions | 0–1 | FS1 |
| `microdna.texture.inkjet_satellite_density` | Count of sub-resolution satellite micro-droplets per $\text{mm}^2$ | $\text{count}/\text{mm}^2$ | FS1 |
| `microdna.texture.micro_roughness_index` | High-frequency surface variation index | float | FS2 |

---

## 5. Printing Dot Pattern Statistics

Physical printing processes use microscopic screening methods to render shades. The Micro DNA Engine measures screen parameters using 2D spatial frequency analysis.

### 5.1 Halftone Screen Parameter Extraction
1. Compute local 2D Fast Fourier Transform (FFT) on high-resolution ($600\text{ DPI}+$) sub-windows.
2. Locate dominant non-DC spectral peaks $(f_{x1}, f_{y1})$ and $(f_{x2}, f_{y2})$.
3. Calculate Screen Angle: $\theta_{screen} = \arctan2(f_{y1}, f_{x1})$.
4. Calculate Line Screen Frequency (LPI): $\text{LPI} = \sqrt{f_{x1}^2 + f_{y1}^2} \times \text{DPI}$.

### 5.2 Feature Definitions

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `microdna.dots.screen_frequency_lpi` | Measured lines per inch (LPI) of halftone screen | LPI | FS1 |
| `microdna.dots.screen_angle_deg` | Measured halftone screen angle | degrees | FS1 |
| `microdna.dots.dot_ellipticity` | Mean aspect ratio of individual halftone dots | ratio | FS1 |
| `microdna.dots.dot_area_variance` | Variance in dot area for uniform gray fills | float | FS1 |
| `microdna.dots.moire_interference_power` | Energy in secondary inter-screen interference frequencies | float | FS1 |

---

## 6. Micro-Detail Preservation Analysis

When a document undergoes digital editing, compression, or re-scanning, fine micro-details (such as guilloche security patterns, micro-printing, or fine linework) suffer degradation.

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `microdna.detail.microprint_legibility` | Cross-correlation score of microprint characters vs template | 0–1 | FS1 |
| `microdna.detail.guilloche_continuity` | Continuity metric of fine security lines (number of breaks per cm) | count/cm | FS1 |
| `microdna.detail.high_freq_preservation` | Ratio of ultra-high frequency energy ($>150\text{ cycles/inch}$) vs total | float | FS2 |

---

## 7. Sub-Pixel Anomaly Mapping

Sub-pixel anomalies are rendered into a high-precision heat map:
1. For every $16 \times 16$ pixel block at $600\text{ DPI}$, compute sub-pixel edge jitter and dot pattern deviation relative to the natural variation model.
2. If deviation $Z > 3.5$, mark block as a micro-anomaly.
3. Generate high-resolution spatial overlay indicating exact regions where microscopic physics diverge from authentic baselines.

---

## 8. Algorithms and Mathematical Foundations

### 8.1 Zernike Moment Sub-Pixel Edge Formula
The $n, m$ order Zernike moment over a unit disk is:
$$Z_{nm} = \frac{n+1}{\pi} \iint_{x^2+y^2 \le 1} I(x,y) V_{nm}^*(\rho, \theta) \, dx \, dy$$
where $V_{nm}(\rho, \theta) = R_{nm}(\rho) e^{i m \theta}$ is the Zernike complex polynomial.

Sub-pixel parameters are solved analytically from $Z_{00}, Z_{11}, Z_{20}$, enabling $0.05\text{ pixel}$ location accuracy.

---

## 9. Performance and Resource Requirements

- **Compute**: Requires CPU C++ extensions or CUDA kernels for Zernike moment calculation and high-resolution FFTs.
- **Memory**: Peak RSS ~3.5 GB per 600 DPI page image.
- **Execution Time**: Standard tier: 15s; Deep tier: 35s.

---

*Previous: [14_Object_Relationship_Graph](../14_Object_Relationship_Graph/README.md)*
*Next: [16_Multi_Model_AI](../16_Multi_Model_AI/README.md)*
*Return to: [Master Index](../README.md)*
