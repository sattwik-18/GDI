# Document 07 — Layout Analysis Engine
## GDI: Spatial, Geometric, and Structural Layout Forensics

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [05_Genome_Extraction_Engine], [06_Document_Reconstruction_Engine], [14_Object_Relationship_Graph], [17_Similarity_Engine]

---

## Table of Contents

1. [Purpose and Forensic Rationale](#1-purpose-and-forensic-rationale)
2. [Feature Groups and Definitions](#2-feature-groups-and-definitions)
3. [Margin Analysis](#3-margin-analysis)
4. [Column and Grid Structure Analysis](#4-column-and-grid-structure-analysis)
5. [Line Spacing Analysis](#5-line-spacing-analysis)
6. [Object Bounding Box Statistics](#6-object-bounding-box-statistics)
7. [Whitespace Distribution Analysis](#7-whitespace-distribution-analysis)
8. [Geometric Alignment Analysis](#8-geometric-alignment-analysis)
9. [Implementation Algorithms](#9-implementation-algorithms)
10. [Spatial Anomaly Detection](#10-spatial-anomaly-detection)
11. [Forensic Interpretation of Layout Anomalies](#11-forensic-interpretation-of-layout-anomalies)
12. [Performance and Complexity](#12-performance-and-complexity)

---

## 1. Purpose and Forensic Rationale

### 1.1 Why Layout Analysis?

Every document is produced by a formatting system (word processor, desktop publishing, form generator, printer controller) that applies consistent spatial layout rules. These rules determine:
- Where text regions begin and end (margins)
- How text is organized in columns
- How lines are spaced within paragraphs
- How different elements (text, images, signatures) are positioned relative to each other

When a document is manipulated — a field value changed, an element replaced, content repositioned — the manipulator must precisely replicate the original layout system's behavior to avoid leaving spatial artifacts. This is extremely difficult in practice:

- Manual repositioning of elements almost never exactly matches the original formatter's pixel-level placement
- Copy-paste operations import objects from different layout contexts
- Re-typed text uses different font metrics, affecting word wrapping and line breaks
- Added or replaced images have different inherent dimensions, causing subtle shifts in surrounding content

The Layout Analysis Engine measures dozens of spatial characteristics with sub-point precision, making layout-level manipulation reliably detectable.

### 1.2 Established Forensic Basis

Layout analysis as a forensic technique is established in the academic and professional forensic community:
- ASTM E2288 (Standard Guide for Examination of Handwritten Items) references spatial consistency in handwritten documents
- The SWGDOC (Scientific Working Group for Forensic Document Examination) standard references spatial measurement in printed document examination
- Academic literature (Lyu & Farid, 2005; Stamm & Liu, 2010) demonstrates spatial inconsistency as a reliable forgery indicator

GDI extends these established approaches with automation, sub-pixel precision, and statistical comparison against the natural variation model.

---

## 2. Feature Groups and Definitions

The Layout Analysis Engine produces features organized into 6 groups:

| Group | Feature Count (std) | Feature Count (deep) | Forensic Significance |
|-------|---------------------|----------------------|-----------------------|
| Margin Measurements | 12 | 20 | FS2 (Major) |
| Column Structure | 8 | 15 | FS2 (Major) |
| Line Spacing | 6 | 12 | FS1 (Critical) |
| Object Bounding Box Statistics | 20 | 40 | FS2 (Major) |
| Whitespace Distribution | 15 | 20 | FS3 (Supporting) |
| Geometric Alignment | 12 | 13 | FS1 (Critical) |
| **Total** | **73** | **120** | — |

---

## 3. Margin Analysis

### 3.1 Feature Definitions

Margins are the regions between the document's content bounding box and the physical page boundary.

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `layout.margin.top` | Top margin width | points (1/72 inch) | FS2 |
| `layout.margin.bottom` | Bottom margin width | points | FS2 |
| `layout.margin.left` | Left margin width | points | FS2 |
| `layout.margin.right` | Right margin width | points | FS2 |
| `layout.margin.top_cv` | Coefficient of variation of top margin across multiple content blocks | dimensionless | FS2 |
| `layout.margin.symmetry_horizontal` | |left_margin - right_margin| / (left + right) | dimensionless | FS2 |
| `layout.margin.symmetry_vertical` | |top_margin - bottom_margin| / (top + bottom) | dimensionless | FS3 |
| `layout.margin.content_to_page_ratio` | Content area / Total page area | dimensionless | FS3 |
| `layout.margin.text_runoff` | Number of text characters detected in margin regions | count | FS1 |
| `layout.margin.image_runoff` | Number of image pixels in margin regions | fraction | FS1 |
| `layout.margin.footer_y` | Y-coordinate of footer region top boundary | points | FS2 |
| `layout.margin.header_y` | Y-coordinate of header region bottom boundary | points | FS2 |

### 3.2 Margin Extraction Algorithm

For raster documents (scanned images):
1. Apply Sauvola adaptive binarization to produce a binary document image
2. Compute horizontal and vertical projection profiles:
   - `H_profile(y) = sum(binary_row[y, :])` — horizontal projection (row-wise content density)
   - `V_profile(x) = sum(binary_column[:, x])` — vertical projection (column-wise content density)
3. Detect content boundaries:
   - Left margin: smallest x where V_profile(x) > content_threshold
   - Right margin: page_width minus largest x where V_profile(x) > content_threshold
   - Top margin: smallest y where H_profile(y) > content_threshold
   - Bottom margin: page_height minus largest y where H_profile(y) > content_threshold

For PDF documents:
- Extract text bounding boxes from PDF object map
- Compute convex hull of all content bounding boxes
- Margin = distance from hull to page boundary

**Precision**: For 300 DPI analysis, each pixel represents 72/300 = 0.24 points. Margin measurements are accurate to ±0.24 points for raster, and to the PDF coordinate precision (usually 0.001 points) for vector documents.

---

## 4. Column and Grid Structure Analysis

### 4.1 Feature Definitions

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `layout.columns.count` | Number of text columns detected | count | FS2 |
| `layout.columns.gutter_width` | Width of inter-column gutter | points | FS2 |
| `layout.columns.widths` | Width of each column (mean, std) | points | FS2 |
| `layout.columns.alignment_score` | Consistency of column left edges | 0–1 | FS1 |
| `layout.grid.detected` | Whether a grid structure is detected | boolean | FS2 |
| `layout.grid.cell_width` | Grid cell width (if detected) | points | FS2 |
| `layout.grid.cell_height` | Grid cell height (if detected) | points | FS2 |
| `layout.grid.alignment_score` | Content-to-grid alignment score | 0–1 | FS2 |

### 4.2 Column Detection Algorithm

Column structure is detected using the X-Y cut algorithm (Nazif & Levine, 1984) adapted for modern documents:

1. Compute vertical projection profile V_profile
2. Identify valleys (local minima) in V_profile where V_profile(x) < valley_threshold
3. Wide valleys (width > minimum_gutter_width) indicate column boundaries
4. Merge narrow valleys (within word spacing range) to avoid false column splits
5. Validate detected columns against expected column count range for document type

**Grid detection**: For form-style documents (tax forms, identity cards), a regular grid structure is detected via:
- Horizontal and vertical line detection (Hough transform on binary image)
- Periodicity analysis of line spacings using autocorrelation
- Grid cell identification at line intersections

---

## 5. Line Spacing Analysis

### 5.1 Feature Definitions

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `layout.linespacing.mean` | Mean inter-line spacing | points | FS1 |
| `layout.linespacing.std` | Standard deviation of inter-line spacing | points | FS1 |
| `layout.linespacing.cv` | Coefficient of variation of spacing | dimensionless | FS1 |
| `layout.linespacing.min` | Minimum inter-line spacing | points | FS2 |
| `layout.linespacing.max` | Maximum inter-line spacing | points | FS2 |
| `layout.linespacing.anomaly_count` | Lines with spacing > 2σ from mean | count | FS1 |

### 5.2 Forensic Significance of Line Spacing

Line spacing is one of the most forensically significant layout features because:

1. **Formatter determinism**: Word processors compute line spacing from precise typographic rules (line height = font size × line height ratio). These rules produce sub-point-precision spacing.

2. **Manipulation signature**: When content is replaced in one region of a document, the replacing content's line spacing reflects the new content's typographic properties, not the original formatter's rules. This creates a localized spacing anomaly.

3. **Natural variation bounds**: For a given font and font size, line spacing should vary by less than 0.5 points within the same paragraph. Larger variation is anomalous.

### 5.3 Line Detection Algorithm

For raster documents:
1. Apply horizontal projection profile to binary image
2. Find peaks in projection (rows with high ink density = text lines)
3. Identify peak positions (y-coordinates of text lines)
4. Compute inter-line gaps: spacing_i = y_{i+1} - y_i for consecutive text lines
5. Exclude section gaps (paragraph breaks, heading spacing) using change-point detection

For PDF documents:
- Use per-character y-coordinate from PDF object map
- Group characters into lines by y-coordinate proximity (within half line height)
- Compute baseline y-coordinates of each line
- Compute inter-baseline spacing

---

## 6. Object Bounding Box Statistics

### 6.1 Feature Definitions

These features describe the statistical distribution of all content objects (text blocks, images, graphics, form fields) in the document:

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `layout.bbox.count` | Total number of distinct content objects | count | FS3 |
| `layout.bbox.area_mean` | Mean bounding box area | sq. points | FS2 |
| `layout.bbox.area_std` | Std dev of bounding box areas | sq. points | FS2 |
| `layout.bbox.aspect_ratio_mean` | Mean aspect ratio (width/height) | dimensionless | FS2 |
| `layout.bbox.aspect_ratio_std` | Std dev of aspect ratios | dimensionless | FS2 |
| `layout.bbox.x_positions` | Histogram of left edge X positions (10 bins) | float[10] | FS2 |
| `layout.bbox.y_positions` | Histogram of top edge Y positions (10 bins) | float[10] | FS2 |
| `layout.bbox.overlap_count` | Number of overlapping bounding boxes | count | FS1 |
| `layout.bbox.text_image_ratio` | Ratio of text area to image area | dimensionless | FS3 |
| `layout.bbox.alignment_histogram` | Histogram of alignment distances to grid | float[5] | FS2 |

### 6.2 Anomaly Significance

**Unexpected overlapping bounding boxes** are highly anomalous: professional document formatters rarely produce overlapping content. Overlaps usually indicate that an element was added from a different document (copy-paste) without proper layout adjustment.

**Outlier bounding box dimensions** relative to the template indicate replacement elements with different sizes.

---

## 7. Whitespace Distribution Analysis

### 7.1 Feature Definitions

Whitespace analysis measures the distribution of empty (non-content) regions:

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `layout.whitespace.fraction` | Fraction of page area that is whitespace | 0–1 | FS3 |
| `layout.whitespace.horizontal_runs.mean` | Mean horizontal run length of whitespace | points | FS3 |
| `layout.whitespace.horizontal_runs.std` | Std dev of horizontal whitespace runs | points | FS3 |
| `layout.whitespace.vertical_runs.mean` | Mean vertical run length of whitespace | points | FS3 |
| `layout.whitespace.gap_histogram` | Histogram of inter-object gaps | float[10] | FS3 |
| `layout.whitespace.paragraph_gap_mean` | Mean inter-paragraph spacing | points | FS2 |
| `layout.whitespace.paragraph_gap_std` | Std dev of inter-paragraph spacing | points | FS2 |
| `layout.whitespace.leading` | Leading (space before first text line) | points | FS2 |

---

## 8. Geometric Alignment Analysis

### 8.1 Feature Definitions

Geometric alignment measures how precisely content objects align to common reference lines and axes:

| Feature ID | Description | Unit | Significance |
|------------|-------------|------|-------------|
| `layout.alignment.text_blocks_left_edge_std` | Std dev of left edges of text blocks in same column | points | FS1 |
| `layout.alignment.text_blocks_right_edge_std` | Std dev of right edges (for justified text) | points | FS1 |
| `layout.alignment.baseline_consistency` | Max deviation from linear baseline | points | FS1 |
| `layout.alignment.image_margin_delta` | Deviation of image edges from nearest text edge | points | FS2 |
| `layout.alignment.horizontal_symmetry` | Ratio of content on left vs. right of vertical center | 0–1 | FS3 |
| `layout.alignment.vertical_balance` | Ratio of content in top vs. bottom half | 0–1 | FS3 |
| `layout.alignment.table_column_alignment` | Std dev of table column edges (for form documents) | points | FS1 |
| `layout.alignment.ruler_consistency` | Consistency of tab stops across lines | points | FS2 |

### 8.2 Baseline Consistency: Forensic Significance

The text baseline is the invisible horizontal line on which the bases of characters rest. In professional typography, characters in the same line must have identical baseline y-coordinates (within rasterization precision).

**Manipulation signature**: When characters are manually positioned or when text is reconstructed character-by-character from different sources, baseline alignment is disrupted. A standard deviation of baseline y-coordinates within a single line exceeding 0.5 points is a significant forensic anomaly.

---

## 9. Implementation Algorithms

### 9.1 Software Stack

| Task | Library | Algorithm |
|------|---------|-----------|
| Binarization | scikit-image | Sauvola adaptive, Otsu global |
| Projection profiles | NumPy | Array summation |
| Line detection | OpenCV | HoughLinesP |
| Contour detection | OpenCV | findContours + approxPolyDP |
| PDF object parsing | PyMuPDF | get_text("rawdict") |
| Statistical analysis | SciPy | Mann-Whitney, Shapiro-Wilk |
| Change-point detection | ruptures | Pelt algorithm |

### 9.2 Computational Complexity

- Projection profiles: O(W × H) — linear in pixel count
- HoughLinesP: O(W × H × θ_resolution) — approximately O(WH log(WH))
- Object bounding box statistics: O(N) where N = number of objects
- Overall layout engine: O(W × H × log(W × H)) — dominated by Hough transform

For a 300 DPI A4 page (2480 × 3508 pixels), expected processing time: 2.5–6 seconds on a standard CPU.

---

## 10. Spatial Anomaly Detection

The Layout Analysis Engine generates a spatial anomaly map (heatmap) at the same resolution as the analysis image.

**Anomaly map generation**:
For each detected spatial anomaly (e.g., a text line with anomalous spacing, a misaligned object):
1. The anomaly region is identified as a bounding rectangle
2. An anomaly intensity value is assigned based on the Z-score of the measured deviation
3. The anomaly intensity is painted onto the anomaly map (additive, with Gaussian blur σ=3px to smooth boundaries)
4. The map is stored as a 16-bit grayscale PNG (anomaly intensity 0–65535)

The anomaly map for each engine is stored in Object Storage and later composited with maps from other engines by the Heatmap Generator.

---

## 11. Forensic Interpretation of Layout Anomalies

| Anomaly Pattern | Possible Interpretation | Confidence |
|-----------------|------------------------|------------|
| Single text line with anomalous spacing | Character replacement in that line | Medium-High |
| Cluster of misaligned objects in one region | Paste operation from different source | High |
| Inconsistent column widths | Column structure manipulation | Medium |
| Overlapping bounding boxes in one area | Element insertion from different document | High |
| Baseline deviation in isolated characters | Individual character replacement | High |
| Overall layout matches but all spacings slightly off | Document re-typeset from scratch (forgery via retyping) | Medium |
| Anomalous whitespace in one region | Element deletion / region erasure | Medium-High |

These interpretations are documented in the forensic report's evidence narrative section.

---

## 12. Performance and Complexity

**CPU Complexity**: O(W×H×log(W×H)) per page
**Memory**: Peak 1.2 GB for standard A4 at 300 DPI
**Processing Time**: P50 2.5s, P95 6s (single page, standard tier)
**Parallelization**: Multi-page documents are processed with per-page parallelism (Python multiprocessing)

**Testing KPIs**:
- Margin measurement accuracy: ±0.25 points (verified against ground truth documents)
- Line spacing detection accuracy: ±0.1 points
- Column detection accuracy: > 98% for documents with clear column boundaries
- Anomaly detection rate on manipulation test corpus: > 95% TPR at 5% FPR for layout-level manipulations

---

*Previous: [06_Document_Reconstruction_Engine](../06_Document_Reconstruction_Engine/README.md)*
*Next: [08_Typography_Analysis](../08_Typography_Analysis/README.md)*
*Return to: [Master Index](../README.md)*
