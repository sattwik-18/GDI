# Document 08 — Typography Analysis Engine
## GDI: Font, Glyph, Kerning, and Typographic Forensics

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [05_Genome_Extraction_Engine], [06_Document_Reconstruction_Engine], [09_Rendering_Analysis], [17_Similarity_Engine]

---

## Table of Contents

1. [Purpose and Forensic Rationale](#1-purpose-and-forensic-rationale)
2. [Feature Groups and Definitions](#2-feature-groups-and-definitions)
3. [Font Identification](#3-font-identification)
4. [Glyph Metrics Analysis](#4-glyph-metrics-analysis)
5. [Kerning Analysis](#5-kerning-analysis)
6. [Baseline Consistency](#6-baseline-consistency)
7. [Inter-word and Inter-character Spacing](#7-inter-word-and-inter-character-spacing)
8. [Rendering Quality and Hinting](#8-rendering-quality-and-hinting)
9. [Typographic Anomaly Detection](#9-typographic-anomaly-detection)
10. [Algorithms and Implementation](#10-algorithms-and-implementation)
11. [Mathematical Foundations](#11-mathematical-foundations)
12. [Performance Characteristics](#12-performance-characteristics)

---

## 1. Purpose and Forensic Rationale

Typography is the highest-resolution forensic signal available in text documents. The specific way in which characters are shaped, sized, spaced, and rendered reflects:

- The specific font (typeface, weight, style, version)
- The rendering engine (operating system font renderer, PDF producer, printer controller)
- The hinting instructions embedded in the font file
- The specific version of the rendering software
- The output device characteristics (screen, printer type, DPI)

These typographic characteristics are extremely difficult to replicate exactly. Even changing from one version of the same font to another (e.g., Times New Roman 5.01 vs. 5.02) produces subtly different glyph outlines that are measurable at 300+ DPI. Using a different rendering engine (Windows GDI vs. DirectWrite vs. Cairo) produces measurably different anti-aliasing patterns for identical font/size combinations.

**Forensic capability**: The Typography Analysis Engine can detect:
1. Font substitution (wrong font used in replacement text)
2. Font version mismatch (correct font name but different version)
3. Renderer substitution (different rendering software than the original)
4. Individual character replacement (single glyph replaced from different source)
5. Text scaling or distortion (characters stretched or compressed after rasterization)
6. Copy-paste from differently configured source (different DPI, different hinting mode)

---

## 2. Feature Groups and Definitions

| Group | Features (std) | Features (deep) | Significance |
|-------|----------------|-----------------|-------------|
| Font Identification | 30 | 50 | FS1 (Critical) |
| Glyph Metrics | 50 | 100 | FS1 (Critical) |
| Kerning Statistics | 40 | 60 | FS1 (Critical) |
| Baseline Consistency | 20 | 30 | FS1 (Critical) |
| Inter-word Spacing | 25 | 35 | FS2 (Major) |
| Rendering Quality | 25 | 25 | FS2 (Major) |
| **Total** | **190** | **300** | — |

---

## 3. Font Identification

### 3.1 Font Feature Definitions

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `typo.font.names` | Font names detected in document | list[string] | FS1 |
| `typo.font.unique_count` | Number of distinct fonts used | count | FS2 |
| `typo.font.size_distribution` | Histogram of font sizes (6pt–72pt, 20 bins) | float[20] | FS1 |
| `typo.font.weight_distribution` | Histogram of font weights (100–900) | float[9] | FS2 |
| `typo.font.style_flags` | Presence of bold/italic/underline/strikethrough | bit flags | FS2 |
| `typo.font.embedding_type` | Font embedding type in PDF (Type1, TrueType, OpenType, CIDFont) | enum | FS1 |
| `typo.font.embedding_subset` | Whether font is subsetted | boolean | FS1 |
| `typo.font.checksum` | CRC32 of embedded font program bytes | uint32 | FS1 |
| `typo.font.glyph_count` | Number of glyphs in embedded font subset | count | FS2 |
| `typo.font.metrics_match` | Whether glyph metrics match expected for declared font | 0–1 | FS1 |
| `typo.font.x_height_ratio` | Ratio of x-height to cap-height | dimensionless | FS1 |
| `typo.font.ascender_ratio` | Ascender height / cap-height | dimensionless | FS1 |
| `typo.font.descender_ratio` | Descender depth / cap-height | dimensionless | FS1 |

### 3.2 Font Identification Algorithm

**For PDF documents** (with embedded fonts):
1. Extract all font objects from the PDF using PyMuPDF `page.get_fonts()`
2. For each font: extract name, BaseFont, Encoding, font program bytes
3. If font program is embedded: compute CRC32 of font program bytes
4. Compare CRC32 against GDI's font fingerprint database (pre-computed checksums for common fonts and their versions)
5. If CRC32 matches: `font_identified = True`, `font_version = {match}`
6. If CRC32 not in database: attempt metric-based identification (see §3.3)

**For raster documents** (scanned, photographed):
1. Isolate text regions using adaptive binarization + connected components
2. Extract individual character images (glyphs) from detected text lines
3. For each character: run font classification CNN (see [16_Multi_Model_AI §4])
4. Aggregate character-level predictions to document-level font confidence map

### 3.3 Metric-Based Font Identification

When font programs are not embedded or are not in the checksum database, font identification uses typographic metrics:

1. Measure x-height (from lowercase 'x'), cap-height, ascender, descender, em-width for extracted glyphs
2. Compute ratios: x-height/cap-height, ascender/cap-height, descender/cap-height
3. Compare ratios against GDI's typographic metrics database (compiled from 2,000+ commercial fonts)
4. Return top-3 candidate fonts with confidence scores

This metric-based identification achieves ~92% top-1 accuracy for common business fonts (Arial, Times New Roman, Helvetica, Calibri) and ~78% accuracy across the broader font catalog.

### 3.4 Font Inconsistency Detection

**Critical anomaly**: Font inconsistency within what should be a uniformly formatted text region.

Detection method:
1. For each text block, identify the dominant font (most common font name + size)
2. Flag any character or word using a different font name, size (>0.5pt deviation), or weight
3. Report the location (bounding box) of each inconsistency
4. Compute the fraction of characters with inconsistent fonts: `font_inconsistency_rate`

A `font_inconsistency_rate > 0.01` (>1% of characters using wrong font) is a significant forensic anomaly, particularly if the inconsistent characters form a coherent word or phrase (suggesting text replacement).

---

## 4. Glyph Metrics Analysis

### 4.1 Feature Definitions

Glyph metrics characterize the shape and dimensions of individual character glyphs:

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `typo.glyph.width_mean` | Mean glyph advance width | em fractions | FS1 |
| `typo.glyph.width_std` | Std dev of glyph widths | em fractions | FS1 |
| `typo.glyph.height_mean` | Mean glyph height | em fractions | FS1 |
| `typo.glyph.height_std` | Std dev of glyph heights | em fractions | FS1 |
| `typo.glyph.ink_density_mean` | Mean ink coverage fraction per glyph | 0–1 | FS2 |
| `typo.glyph.ink_density_std` | Std dev of ink density | 0–1 | FS2 |
| `typo.glyph.stroke_width_mean` | Mean stroke width (for letters) | pixels | FS1 |
| `typo.glyph.stroke_width_std` | Std dev of stroke width | pixels | FS1 |
| `typo.glyph.stroke_contrast` | Ratio of thick to thin strokes | dimensionless | FS1 |
| `typo.glyph.roundness_mean` | Mean corner roundness of glyphs | 0–1 | FS2 |
| `typo.glyph.serif_detected` | Presence of serif features detected | boolean | FS2 |
| `typo.glyph.per_char_profiles` | Statistical profile per character class (a–z, A–Z, 0–9) | float[62×5] | FS1 |

### 4.2 Per-Character Profile Analysis

For each alphanumeric character class (62 classes: a–z, A–Z, 0–9), the engine extracts:
- Mean width in pixels
- Mean height in pixels  
- Mean ink density (fraction of bounding box covered by ink)
- Mean stroke width
- Shape descriptor vector (Hu moments, 7 values)

This produces a 62 × 12 = 744-dimensional character profile matrix.

**Anomaly detection**: For each character class, compute the deviation of the submitted document's profile from the template's profile. Characters with Z-score > 3.0 on any metric are flagged as potentially replaced or from a different source.

### 4.3 Stroke Width Transform

Stroke width analysis uses the **Stroke Width Transform (SWT)** (Epshtein et al., 2010):
1. Compute Canny edges of each glyph
2. Cast rays from edge pixels in the gradient direction
3. For each valid ray (connecting two parallel edges), record the stroke width
4. Aggregate stroke widths: mean, std, and thick/thin contrast ratio

SWT-based stroke width is robust to scale variation and is a strong discriminator between font families (sans-serif vs. serif) and within font families (regular vs. bold).

---

## 5. Kerning Analysis

### 5.1 Why Kerning is a Strong Forensic Signal

Kerning is the adjustment of spacing between specific pairs of letters to achieve visually balanced text. Every professional font includes a kerning table specifying adjustments for hundreds of letter pairs (e.g., AV, To, Ty). These adjustments are highly specific to each font version and rendering engine.

When text is manipulated:
- Replaced characters rarely have correctly computed kerning with adjacent characters
- Characters copied from different documents have different kerning contexts
- Manual position adjustment of characters leaves kerning artifacts

### 5.2 Feature Definitions

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `typo.kerning.pair_deviations` | Per-pair kerning deviation from expected | points[top50] | FS1 |
| `typo.kerning.global_mean` | Mean kerning across all letter pairs | points | FS1 |
| `typo.kerning.global_std` | Std dev of kerning values | points | FS1 |
| `typo.kerning.pair_consistency` | Fraction of pairs with consistent kerning | 0–1 | FS1 |
| `typo.kerning.anomalous_pairs` | Letter pairs with kerning deviation > 2σ | list | FS1 |
| `typo.kerning.direction_histogram` | Histogram of kerning direction (negative/zero/positive) | float[3] | FS2 |

### 5.3 Kerning Extraction Algorithm

**For PDF documents**:
1. For each consecutive character pair in the PDF text stream:
   - Extract the X advance position of character N
   - Extract the X position of character N+1
   - Actual inter-character gap = X(N+1) - (X(N) + advance_width(N))
2. Compare against expected kerning for the font+pair combination (from font kerning table or lookup in GDI's kerning database)
3. Kerning deviation = actual_gap - expected_gap

**For raster documents**:
1. Extract character bounding boxes using connected components analysis
2. Compute measured inter-character gaps from bounding box edges
3. For each character pair: look up expected advance width + kerning from identified font
4. Kerning deviation = measured_gap - expected_gap_for_font

Precision: ±0.3 points for PDF, ±0.5 pixels for raster.

---

## 6. Baseline Consistency

### 6.1 Feature Definitions

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `typo.baseline.y_std_within_line` | Std dev of character baseline Y within each line | pixels | FS1 |
| `typo.baseline.max_deviation` | Maximum baseline deviation in any line | pixels | FS1 |
| `typo.baseline.anomalous_line_count` | Lines with baseline std > threshold | count | FS1 |
| `typo.baseline.drift_linear` | Linear drift coefficient (baseline slope) | pixels/char | FS2 |
| `typo.baseline.vertical_offset_histogram` | Histogram of per-character vertical offsets from baseline | float[20] | FS1 |

### 6.2 Baseline Extraction

For each detected text line:
1. Extract per-character bounding boxes (bottom-Y coordinate = baseline estimate)
2. Fit a linear model to baseline positions: baseline(x) = a + bx
3. Compute residuals: deviation_i = bottom_Y(char_i) - baseline(x_i)
4. Statistics: std(deviation_i), max(|deviation_i|)

A std deviation > 1.5 pixels at 300 DPI within a single text line indicates characters from different sources or positions.

---

## 7. Inter-word and Inter-character Spacing

### 7.1 Feature Definitions

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `typo.spacing.word_gap_mean` | Mean inter-word gap | points | FS2 |
| `typo.spacing.word_gap_std` | Std dev of inter-word gaps | points | FS2 |
| `typo.spacing.word_gap_cv` | Coefficient of variation | dimensionless | FS2 |
| `typo.spacing.justification_score` | Score measuring consistent right-edge alignment for justified text | 0–1 | FS2 |
| `typo.spacing.hyphenation_consistency` | Consistency of hyphenation at line breaks | 0–1 | FS3 |
| `typo.spacing.punctuation_gap_mean` | Mean gap before/after punctuation | points | FS2 |

### 7.2 Justification Analysis

For justified text, every line (except the last in a paragraph) should extend to the same right margin. The inter-word spaces are stretched uniformly to achieve this. The exact stretching algorithm varies by typesetter, producing a characteristic spacing distribution.

Comparing the spacing distribution of the submitted document against the template's spacing distribution can detect:
- Text re-typeset by a different justification algorithm
- Lines with replaced content that fails to justify correctly

---

## 8. Rendering Quality and Hinting

### 8.1 Feature Definitions

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `typo.rendering.antialiasing_mode` | Detected anti-aliasing mode (grayscale/ClearType/none) | enum | FS2 |
| `typo.rendering.hinting_strength` | Estimated hinting strength | 0–1 | FS2 |
| `typo.rendering.edge_sharpness_mean` | Mean edge sharpness (gradient magnitude at glyph edges) | 0–1 | FS2 |
| `typo.rendering.edge_sharpness_std` | Std dev of edge sharpness | 0–1 | FS2 |
| `typo.rendering.subpixel_pattern` | Detected subpixel rendering pattern (BGR/RGB) | enum | FS2 |
| `typo.rendering.compression_ringing` | JPEG ringing artifact level at glyph edges | 0–1 | FS2 |

### 8.2 Anti-aliasing Detection

Anti-aliasing mode (grayscale AA, ClearType/subpixel AA, or no AA) is detected by:
1. Analyzing the pixel color distribution at glyph edges
2. Grayscale AA: edges have smooth gray gradient, equal in all channels
3. ClearType/subpixel: edges have color fringing (RGB or BGR channel offset)
4. No AA: edges are binary (pure black/white)

This is forensically significant because a document rendered on Windows (typically ClearType) will have different glyph edge characteristics than one rendered on Linux (typically grayscale AA via Cairo) or macOS (Quartz AA). Mixing of AA modes within a document indicates potential manipulation.

---

## 9. Typographic Anomaly Detection

The Typography Engine generates the following anomaly signals:

| Anomaly Signal | Detection Method | Forensic Implication |
|----------------|-----------------|----------------------|
| Font substitution | CRC mismatch + metric mismatch | Wrong font used for replacement text |
| Glyph outlier | Z-score > 3.0 on per-char profile | Character replaced from different source |
| Kerning anomaly | Pair deviation > 2σ | Incorrect kerning at replacement boundary |
| Baseline disruption | Line std > 1.5px | Characters from different rasterizations |
| Mixed AA modes | Different AA mode regions | Parts of document from different renders |
| Rendering sharpness mismatch | Local edge sharpness outlier | Region from different resolution/renderer |

---

## 10. Algorithms and Implementation

| Task | Algorithm | Library |
|------|-----------|---------|
| Font program extraction | Direct PDF object access | PyMuPDF |
| Font checksum | CRC32 | Python stdlib `binascii` |
| Glyph extraction (raster) | Connected components | OpenCV |
| Stroke Width Transform | Custom CUDA/Python implementation | NumPy + CuPy (GPU optional) |
| Kerning measurement | PDF glyph position delta analysis | PyMuPDF |
| Baseline fitting | Linear regression (least squares) | NumPy `polyfit` |
| Anti-aliasing detection | Channel-wise edge analysis | NumPy/SciPy |
| Font classification CNN | Pre-trained ResNet-18 fine-tuned on font corpus | PyTorch |

---

## 11. Mathematical Foundations

### 11.1 Stroke Width Transform (SWT)

For each edge pixel p:
1. Compute gradient direction d_p = (∇I_x, ∇I_y) / ||(∇I_x, ∇I_y)||
2. Cast ray from p in direction d_p until hitting another edge pixel q
3. Check: d_q ≈ -d_p (antiparallel gradients → opposite sides of a stroke)
4. If check passes: stroke width = ||q - p||₂; assign to all pixels on ray

Mean stroke width SWT_mean = E[stroke_width]
Stroke contrast = SWT_max / SWT_min (thick/thin ratio)

### 11.2 Kerning Deviation Model

For letter pair (c₁, c₂) in font F:
```
expected_gap(c₁, c₂, F) = advance_width(c₁, F) + kern_table(c₁, c₂, F)
actual_gap(c₁, c₂) = measured from document
deviation(c₁, c₂) = actual_gap - expected_gap
```

Z-score: `Z(c₁,c₂) = |deviation(c₁,c₂) - μ_kern| / σ_kern`

where μ_kern and σ_kern are the mean and std of kerning deviations for this font across the natural variation corpus.

---

## 12. Performance Characteristics

| Metric | Value |
|--------|-------|
| Processing time P50 | 8 seconds (single page, ~500 characters) |
| Processing time P95 | 18 seconds |
| Memory peak | 2.1 GB |
| Characters processed/second | ~80 (with full glyph analysis) |
| Font identification accuracy (PDF, known fonts) | 99.5% |
| Font identification accuracy (raster, common fonts) | 92.0% |
| Glyph replacement detection TPR at 1% FPR | 94% |

---

*Previous: [07_Layout_Analysis](../07_Layout_Analysis/README.md)*
*Next: [09_Rendering_Analysis](../09_Rendering_Analysis/README.md)*
*Return to: [Master Index](../README.md)*
