# Document 11 — Frequency Analysis Engine
## GDI: DCT, Wavelet, and Frequency-Domain Forensics

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21

---

## Table of Contents

1. [Purpose and Forensic Rationale](#1-purpose-and-forensic-rationale)
2. [Feature Groups and Definitions](#2-feature-groups-and-definitions)
3. [DCT Coefficient Analysis](#3-dct-coefficient-analysis)
4. [Wavelet Energy Analysis](#4-wavelet-energy-analysis)
5. [Periodogram Analysis](#5-periodogram-analysis)
6. [Double JPEG Compression Detection](#6-double-jpeg-compression-detection)
7. [Copy-Move Detection via Frequency Domain](#7-copy-move-detection-via-frequency-domain)
8. [Mathematical Foundations](#8-mathematical-foundations)
9. [Implementation](#9-implementation)

---

## 1. Purpose and Forensic Rationale

Frequency-domain analysis transforms the document image from the spatial domain (pixel values at positions) into the frequency domain (sinusoidal components at different frequencies). This transformation reveals forensic signals that are invisible in the spatial domain:

1. **JPEG Quantization Artifacts**: JPEG compression quantizes DCT coefficients using a quantization matrix. The specific quantization matrix used is a forensic fingerprint of the compression settings and software.

2. **Double Compression**: If a JPEG image is compressed, manipulated, and re-compressed, the re-quantization leaves distinctive artifacts in the DCT coefficient distribution (periodic zeros in the histogram) that reveal the prior compression history.

3. **Periodicity Artifacts**: Copy-move forgeries (where a region is copied and pasted within the same document) produce periodic similarity patterns in the frequency domain.

4. **Frequency Signature of Rendering**: Different rendering engines produce characteristic energy distributions across frequency bands. A document region with a different frequency signature from its surroundings was likely produced by a different rendering process.

### Established Basis

Frequency-domain forensics is a mature academic sub-field:
- Farid (2009) demonstrated double JPEG compression detection via DCT statistics
- Popescu & Farid (2004) demonstrated copy-move detection via phase correlation
- Lue et al. (2010) showed frequency signatures as rendering fingerprints

---

## 2. Feature Groups and Definitions

| Group | Features (std) | Features (deep) | Significance |
|-------|----------------|-----------------|-------------|
| DCT Coefficient Statistics | 20 | 30 | FS2 (Major) |
| Wavelet Energy Bands | 15 | 20 | FS2 (Major) |
| Periodogram Features | 10 | 10 | FS2 (Major) |
| **Total** | **45** | **60** | — |

---

## 3. DCT Coefficient Analysis

### 3.1 Feature Definitions

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `freq.dct.quantization_matrix` | Estimated JPEG quantization matrix | int[64] | FS2 |
| `freq.dct.quality_factor` | Estimated JPEG quality factor (1–100) | int | FS2 |
| `freq.dct.coefficient_histogram` | Histogram of AC DCT coefficients for each of 63 positions | float[63×16] | FS2 |
| `freq.dct.double_compression_score` | Score indicating double JPEG compression | 0–1 | FS2 |
| `freq.dct.primary_quality_estimate` | Estimated quality of primary compression (before double-compression) | int | FS2 |
| `freq.dct.energy_ratio_low_high` | Ratio of energy in low-frequency vs. high-frequency DCT coefficients | float | FS2 |
| `freq.dct.blockiness_periodic_score` | 8×8 periodic structure score in DCT domain | float | FS2 |

### 3.2 Quantization Matrix Estimation

For JPEG images: the quantization matrix is directly readable from the JPEG header (DQT marker segments). This gives exact knowledge of the compression settings.

For other formats that were previously JPEG (e.g., a JPEG saved as PNG): the quantization matrix can be estimated by analyzing the distribution of DCT coefficients:
1. Divide the image into 8×8 blocks
2. Compute the DCT of each block
3. For each coefficient position (u,v): build the histogram of coefficient values
4. The quantization step Q(u,v) = argmin of the fit between the histogram and a periodic-zero Gaussian mixture model
5. The estimated quantization matrix = {Q(u,v)}

### 3.3 DCT Coefficient Histogram Analysis

The distribution of DCT coefficients carries forensic information:

For an uncompressed image: AC DCT coefficients follow approximately a Laplacian distribution centered at 0.

For a JPEG-compressed image: coefficients are quantized to multiples of Q(u,v), producing a "comb" distribution with non-zero bins only at multiples of Q(u,v).

For a double-compressed image: the histogram has periodic zeros at the boundaries of the primary quantization bins — a distinctive signature of prior compression.

---

## 4. Wavelet Energy Analysis

### 4.1 Why Wavelets?

While the DCT decomposes an image into globally supported frequency components, wavelet analysis provides **localized frequency information**: it measures frequency content at different scales AND at different spatial locations simultaneously (multi-resolution analysis). This localization makes wavelets superior for detecting spatially localized manipulation.

### 4.2 Wavelet Transform

GDI uses the 2D Discrete Wavelet Transform (DWT) with the Daubechies-8 (db8) wavelet basis:

1. Apply 3-level 2D DWT: each level produces 4 subbands (LL, LH, HL, HH)
2. Level 1: captures fine details (8px features at 300 DPI → ~0.6mm)
3. Level 2: captures medium details (~1.2mm)
4. Level 3: captures coarse structures (~2.4mm)

### 4.3 Feature Definitions

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `freq.wavelet.energy_LL3` | Energy in level-3 low-frequency subband | float | FS2 |
| `freq.wavelet.energy_LH1` | Energy in level-1 horizontal detail | float | FS2 |
| `freq.wavelet.energy_HL1` | Energy in level-1 vertical detail | float | FS2 |
| `freq.wavelet.energy_HH1` | Energy in level-1 diagonal detail | float | FS2 |
| `freq.wavelet.energy_LH2` | Energy in level-2 horizontal detail | float | FS2 |
| `freq.wavelet.energy_HL2` | Energy in level-2 vertical detail | float | FS2 |
| `freq.wavelet.energy_HH2` | Energy in level-2 diagonal detail | float | FS2 |
| `freq.wavelet.energy_LH3` | Energy in level-3 horizontal detail | float | FS2 |
| `freq.wavelet.energy_HL3` | Energy in level-3 vertical detail | float | FS2 |
| `freq.wavelet.energy_HH3` | Energy in level-3 diagonal detail | float | FS2 |
| `freq.wavelet.energy_ratios` | Ratios of subband energies | float[9] | FS2 |
| `freq.wavelet.local_energy_map` | Per-region wavelet energy map (8×8 grid) | float[64] | FS1 |
| `freq.wavelet.anisotropy` | Ratio of horizontal to vertical wavelet energy | float | FS2 |
| `freq.wavelet.entropy` | Wavelet entropy (distribution of energy across subbands) | float | FS2 |
| `freq.wavelet.localized_anomaly_score` | Score from region-specific wavelet comparison | float | FS1 |

### 4.4 Energy Computation

For each wavelet subband W:
```
Energy(W) = (1/N) × Σ_{i,j} W[i,j]²
```
where N is the number of coefficients in the subband.

The local energy map divides each subband into an 8×8 grid and computes energy per cell, enabling spatial localization of energy anomalies.

---

## 5. Periodogram Analysis

### 5.1 Feature Definitions

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `freq.periodogram.dominant_frequencies` | Top-5 spatial frequencies by power | cycles/mm[5] | FS2 |
| `freq.periodogram.spectral_entropy` | Entropy of the power spectrum | float | FS2 |
| `freq.periodogram.anisotropy_ratio` | Power ratio horizontal vs. vertical frequencies | float | FS2 |
| `freq.periodogram.noise_floor` | Estimated noise floor power level | float | FS2 |
| `freq.periodogram.signal_to_noise` | Signal-to-noise ratio in frequency domain | dB | FS2 |
| `freq.periodogram.aliasing_score` | Evidence of frequency aliasing (from resampling) | 0–1 | FS2 |
| `freq.periodogram.periodic_pattern_score` | Score for unexpected periodic patterns | 0–1 | FS1 |
| `freq.periodogram.radial_mean_spectrum` | Radially averaged power spectrum (50 bins) | float[50] | FS2 |
| `freq.periodogram.phase_coherence` | Phase coherence across document regions | 0–1 | FS2 |
| `freq.periodogram.spectral_flatness` | Spectral flatness measure (≈0 tonal, ≈1 noise) | 0–1 | FS2 |

---

## 6. Double JPEG Compression Detection

### 6.1 Algorithm

Double JPEG compression detection exploits the characteristic distribution of DCT coefficients that results from two sequential JPEG compressions with different quantization steps:

**Theory**: If Q₁ is the primary quantization step and Q₂ is the secondary (re-compression) step:
- Primary compression quantizes coefficients to multiples of Q₁
- Re-compression with Q₂ causes periodic zeros in the histogram at every Q₁-th bin boundary

This creates a "comb-like" pattern in the DCT coefficient histogram that is not present in single-compressed images.

**Implementation**:
1. Extract all DCT coefficients from 8×8 image blocks
2. For each coefficient position (u,v), build a histogram with fine resolution (bin width = 1)
3. Apply the Benford-Fourier (Farid, 2009) method: compute the DFT of the coefficient histogram
4. The presence of a strong peak in the histogram DFT at frequency 1/Q₁ indicates double compression
5. Double compression score = normalized peak height at the estimated primary quantization frequency

### 6.2 Localized Double Compression Detection

The detection can be localized to specific image regions:
1. Divide the image into non-overlapping 64×64 pixel regions
2. Apply double compression detection to each region independently
3. A region that was manipulated and re-saved will show double compression while the surrounding authentic region may not

This localized detection is the primary tool for detecting JPEG-manipulation within a document.

---

## 7. Copy-Move Detection via Frequency Domain

### 7.1 Phase Correlation

Copy-move forgeries (copy a region from one location and paste to another within the same image) can be detected via phase correlation:

1. Divide image into overlapping blocks
2. Compute DFT of each block
3. For all pairs of blocks: compute phase correlation
   ```
   PhaseCorr(B₁, B₂) = IDFT(DFT(B₁) × conj(DFT(B₂)) / |DFT(B₁) × conj(DFT(B₂))|)
   ```
4. Blocks that are copies of each other have a sharp peak in the phase correlation at the offset vector between them
5. Collect all significant peaks (height > threshold) and their offsets
6. Cluster similar offsets (DBSCAN clustering) — a cluster of many pairs with the same offset vector is evidence of copy-move

### 7.2 Limitation

Phase correlation-based copy-move detection has quadratic complexity in the number of blocks, making it computationally expensive for large documents. GDI applies this analysis to suspicious regions identified by the texture and noise engines, rather than to the entire document, to maintain performance within SLA.

---

## 8. Mathematical Foundations

### 8.1 2D Discrete Cosine Transform (Type-II)

For an N×N image block:
```
DCT(u,v) = (4/N²) × c(u) × c(v) × Σ_{x=0}^{N-1} Σ_{y=0}^{N-1} I(x,y) × cos(π(2x+1)u/2N) × cos(π(2y+1)v/2N)
```
where c(0) = 1/√2, c(k>0) = 1.

### 8.2 2D Discrete Wavelet Transform

The 2D DWT is implemented as two 1D DWTs (separable):
1. Apply 1D DWT to each row: produces L (low-frequency) and H (high-frequency) components
2. Apply 1D DWT to each column of the result: produces LL, LH, HL, HH subbands

The Daubechies-8 wavelet (db8) has 8 vanishing moments, providing smooth reconstruction and good separation of frequency content across levels.

### 8.3 Wavelet Entropy

Wavelet entropy measures the distribution of energy across subbands:
```
WE = -Σ_s p_s × log(p_s)
where p_s = Energy(subband_s) / Total_energy
```
Higher entropy → energy distributed across many subbands (complex texture). Lower entropy → energy concentrated (uniform background).

### 8.4 Spectral Flatness

```
SFM = geometric_mean(PSD) / arithmetic_mean(PSD)
```
SFM ≈ 0 for tonal signals (periodic patterns), SFM ≈ 1 for white noise. Documents should have intermediate SFM values characteristic of their content type.

---

## 9. Implementation

| Task | Algorithm | Library |
|------|-----------|---------|
| 2D DCT | scipy.fft.dctn | SciPy |
| 2D DWT | pywt.dwt2 | PyWavelets |
| Quantization matrix estimation | Custom MLE fitting | NumPy/SciPy |
| Double compression detection | Benford-Fourier method | Custom NumPy |
| Phase correlation | FFT-based cross-correlation | SciPy `signal.fftconvolve` |
| DBSCAN clustering | DBSCAN | scikit-learn |
| Power spectral density | Welch's method | SciPy `signal.welch` |

**Processing time**: P50 1.5s, P95 4s per page at 300 DPI.

---

*Previous: [10_Texture_Analysis](../10_Texture_Analysis/README.md)*
*Next: [12_Noise_Analysis](../12_Noise_Analysis/README.md)*
*Return to: [Master Index](../README.md)*
