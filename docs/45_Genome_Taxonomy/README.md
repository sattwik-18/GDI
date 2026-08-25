# Document 45 — Genome Taxonomy
## GDI: Complete Sub-Genome Taxonomy and Forensic Hierarchy

**Version:** 2.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Authors:** Principal Architect, Chief Research Engineer, Technical Documentation Lead
**Cross-References:** [05_Genome_Extraction_Engine], [38_Genome_Hierarchy], [44_Mathematical_Foundations]

---

## Table of Contents

1. [Taxonomy Overview](#1-taxonomy-overview)
2. [Chromosome 1: Layout Sub-Genomes](#2-chromosome-1-layout-sub-genomes)
3. [Chromosome 2: Typography Sub-Genomes](#3-chromosome-2-typography-sub-genomes)
4. [Chromosome 3: Rendering Sub-Genomes](#4-chromosome-3-rendering-sub-genomes)
5. [Chromosome 4: Texture Sub-Genomes](#5-chromosome-4-texture-sub-genomes)
6. [Chromosome 5: Frequency Sub-Genomes](#6-chromosome-5-frequency-sub-genomes)
7. [Chromosome 6: Noise Sub-Genomes](#7-chromosome-6-noise-sub-genomes)
8. [Chromosome 7: Metadata Sub-Genomes](#8-chromosome-7-metadata-sub-genomes)
9. [Chromosome 8: Object Relationship Graph Sub-Genomes](#9-chromosome-8-object-relationship-graph-sub-genomes)
10. [Chromosome 9: Micro-DNA Sub-Genomes](#10-chromosome-9-micro-dna-sub-genomes)
11. [Chromosome 10: AI Semantic Sub-Genomes](#11-chromosome-10-ai-semantic-sub-genomes)

---

## 1. Taxonomy Overview

In GDI Version 2.0, every major forensic engine is expanded from a single feature group into a structured **Sub-Genome Taxonomy**. Each Chromosome contains specialized Sub-Genomes, which encompass specific Genes, Traits, and Measurements.

---

## 2. Chromosome 1: Layout Sub-Genomes
- `SubGen_Layout_Margin`: Top, bottom, left, right margin vectors and variance.
- `SubGen_Layout_Grid`: Column gutter widths, grid cell geometry, alignment scores.
- `SubGen_Layout_LineSpacing`: Inter-line spacing distributions, leading consistency, paragraph gaps.
- `SubGen_Layout_BoundingBox`: Bounding box statistics, aspect ratios, overlap counts.
- `SubGen_Layout_Whitespace`: Horizontal/vertical whitespace run-length histograms.

## 3. Chromosome 2: Typography Sub-Genomes
- `SubGen_Typo_Glyph`: Character glyph height, width, area, stroke width, Hu moments.
- `SubGen_Typo_Kerning`: Letter-pair kerning deviations (AV, To, Ty, etc.).
- `SubGen_Typo_Baseline`: Character baseline linear regression residual variances.
- `SubGen_Typo_Ligature`: Specialized multi-character ligature metrics.
- `SubGen_Typo_Hinting`: Native vs autohinting structural profiles.
- `SubGen_Typo_Stroke`: Stroke Width Transform (SWT) distributions, thick/thin ratios.
- `SubGen_Typo_Rasterization`: Glyph edge pixel transition widths.
- `SubGen_Typo_Distribution`: Unigram and bigram character spatial density maps.

## 4. Chromosome 3: Rendering Sub-Genomes
- `SubGen_Rend_AntiAliasing`: Grayscale transition profiles, gamma estimates.
- `SubGen_Rend_Subpixel`: ClearType subpixel ordering (RGB vs BGR), fringing strength.
- `SubGen_Rend_InkSpread`: Ink/toner spread beyond nominal vector boundaries.
- `SubGen_Rend_EdgeSharpness`: Gradient magnitude histograms, local Laplacian variance maps.
- `SubGen_Rend_Artifacts`: Banding frequency, moiré interference, 8×8 JPEG blockiness.

## 5. Chromosome 4: Texture Sub-Genomes
- `SubGen_Text_PaperGrain`: Whitespace GLCM Haralick descriptors (Energy, Entropy, Contrast).
- `SubGen_Text_InkTexture`: Intra-stroke density variance, stroke boundary feathering.
- `SubGen_Text_LBP`: Uniform Local Binary Pattern histograms ($R=1, P=8$ and $R=2, P=16$).
- `SubGen_Text_TonerSatellite`: Microscopic toner satellite dot counts per $\text{mm}^2$.

## 6. Chromosome 5: Frequency Sub-Genomes
- `SubGen_Freq_DCT`: 8×8 block AC DCT coefficient histograms, quantization matrices.
- `SubGen_Freq_Wavelet`: 3-level Daubechies-8 (db8) subband energies (LL, LH, HL, HH).
- `SubGen_Freq_Periodogram`: Radial power spectral density, spectral entropy, phase coherence.
- `SubGen_Freq_DoubleJPEG`: Benford-Fourier DCT comb artifact indicators.

## 7. Chromosome 6: Noise Sub-Genomes
- `SubGen_Noise_Sensor`: Signal-dependent Poisson-Gaussian noise parameters $(a, b)$.
- `SubGen_Noise_PRNU`: Photo Response Non-Uniformity correlation maps ($PCE$).
- `SubGen_Noise_JPEGProfile`: Artifact inconsistency scores, quantization quality estimates.
- `SubGen_Noise_CFA`: Color Filter Array demosaicing pattern indicators (RGGB, BGGR).

## 8. Chromosome 7: Metadata Sub-Genomes
- `SubGen_Meta_PDFInfo`: PDF version, object graph count, incremental updates.
- `SubGen_Meta_EXIF`: Camera/scanner make, model, exposure, EXIF thumbnail hash.
- `SubGen_Meta_XMP`: Adobe XMP modification history sequence, software agents.
- `SubGen_Meta_DigitalSignature`: PKCS#7/CMS certificate chain validation, DocMDP coverage.

## 9. Chromosome 8: Object Relationship Graph Sub-Genomes
- `SubGen_Graph_Topology`: Delaunay triangulation density, clustering coefficients, diameter.
- `SubGen_Graph_Spectral`: Normalized Laplacian eigenvalues, Fiedler value, spectral radius.
- `SubGen_Graph_SpatialMatrix`: Pairwise distance and orientation angle matrices $R_{ij}$.
- `SubGen_Graph_Semantic`: Functional label-value pair rules, orphaned label counts.

## 10. Chromosome 9: Micro-DNA Sub-Genomes
- `SubGen_Micro_SubpixelEdge`: Order-7 Zernike moment edge jitter, curvature derivatives.
- `SubGen_Micro_DotPattern`: Halftone line screen frequency (LPI), screen angles ($\theta_{\text{screen}}$).
- `SubGen_Micro_DetailPreservation`: Microprint legibility scores, fine security line continuity.

## 11. Chromosome 10: AI Semantic Sub-Genomes
- `SubGen_AI_VisionEmbedding`: DINOv2 ViT-L/14 CLS embedding vector ($1024\text{-d}$).
- `SubGen_AI_LayoutStructure`: LayoutLMv3 multimodal token classification probabilities.
- `SubGen_AI_DiffusionForgery`: Generative AI in-painting spatial probability map.
- `SubGen_AI_AutoencoderAnomaly`: Swin UNETR reconstruction error map.

---

*Previous: [44_Mathematical_Foundations](../44_Mathematical_Foundations/README.md)*
*Next: [46_Template_Evolution](../46_Template_Evolution/README.md)*
*Return to: [Master Index](../README.md)*
