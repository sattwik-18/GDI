# Document 06 — Document Reconstruction Engine
## GDI: Document Rendering and Structural Reconstruction

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [04_Data_Flow §4], [05_Genome_Extraction_Engine §5], [07_Layout_Analysis], [09_Rendering_Analysis]

---

## Table of Contents

1. [Purpose and Rationale](#1-purpose-and-rationale)
2. [Input Formats and Preprocessing](#2-input-formats-and-preprocessing)
3. [Document Normalization Pipeline](#3-document-normalization-pipeline)
4. [Multi-Modality Rendering](#4-multi-modality-rendering)
5. [PDF Vector Extraction](#5-pdf-vector-extraction)
6. [Skew and Perspective Correction](#6-skew-and-perspective-correction)
7. [Color Space Normalization](#7-color-space-normalization)
8. [Resolution and Quality Assessment](#8-resolution-and-quality-assessment)
9. [Reconstruction Manifest](#9-reconstruction-manifest)
10. [Error Handling and Edge Cases](#10-error-handling-and-edge-cases)
11. [Performance Characteristics](#11-performance-characteristics)
12. [Security Considerations](#12-security-considerations)

---

## 1. Purpose and Rationale

The Document Reconstruction Engine (DRE) is the first forensic processing step after ingestion. Its purpose is to transform the raw, potentially noisy, and format-diverse submitted document into a set of normalized, standardized analysis modalities that all downstream forensic engines can consume consistently.

**Why a separate reconstruction step?**

Different document formats (PDF, TIFF, JPEG, scanned image) represent document content in fundamentally different ways. PDF stores text as vector glyphs and graphics; TIFF stores a raster bitmap; JPEG applies lossy compression with quantization tables. Without normalization, each forensic engine would need to handle all input formats independently, creating a combinatorial explosion in complexity and reducing consistency.

The DRE decouples format handling from forensic analysis. Every forensic engine receives a standardized modality set, regardless of the original format.

**Alternative approaches considered**:
- *Engine-level format handling*: Each engine handles its own format parsing. Rejected because it creates code duplication, inconsistent rendering parameters, and makes it impossible to ensure that all engines analyze the same effective representation of the document.
- *Single shared rendering library*: All engines call a shared library at analysis time. Rejected because it creates temporal coupling between engines (they all need the document loaded simultaneously) and prevents result caching.

---

## 2. Input Formats and Preprocessing

### 2.1 Supported Formats

| Format | Parser | Notes |
|--------|--------|-------|
| PDF 1.0–2.0 | PyMuPDF (MuPDF) | Handles embedded fonts, forms, annotations, encrypted PDFs |
| TIFF (single/multi-page) | Pillow + libtiff | Handles LZW, JPEG-in-TIFF, CCITT Group 4 |
| JPEG | libjpeg-turbo | Preserves original JPEG tables for compression analysis |
| PNG | libpng | Full metadata extraction including tEXt chunks |
| JPEG2000 | OpenJPEG | Handles multi-layer progressive files |
| BMP | Pillow | Includes old uncompressed formats |
| HEIF/HEIC | libheif | Modern mobile document photography format |
| DNG/CR2 | rawpy (LibRaw) | Camera raw files from document photography |

**Format detection**: Format is detected by magic bytes (file header inspection), not file extension. File extension mismatch is flagged as a metadata anomaly.

### 2.2 Encrypted Document Handling

- PDF documents with user-level password encryption: If a decryption password is provided in submission metadata, decryption is attempted. Otherwise, a metadata_anomaly is flagged and the document is analyzed in encrypted form.
- Documents with owner-level password restrictions only: Restrictions are ignored for forensic analysis (rendering is always performed).

### 2.3 Malformed Document Handling

Documents with structural errors (corrupt PDF objects, truncated TIFF data, invalid JPEG streams) are processed with best-effort recovery:
- PyMuPDF's repair mode is engaged for corrupt PDFs
- Pillow's ImageFile.LOAD_TRUNCATED_IMAGES is set for truncated raster files
- The degree of corruption is quantified and reported as a reconstruction_quality_score

---

## 3. Document Normalization Pipeline

### 3.1 Pipeline Stages

```
Stage 1: Format Detection and Parsing
  ─ Read magic bytes (first 512 bytes of file)
  ─ Identify format from signature table
  ─ Instantiate appropriate parser
  ─ Parse document structure (pages, objects, metadata)

Stage 2: Page Enumeration
  ─ Identify all pages (for multi-page documents)
  ─ Determine page dimensions (width × height in points or pixels)
  ─ Identify natural page orientation

Stage 3: Geometry Analysis (per page)
  ─ Rasterize page at 2× target DPI for geometry analysis
  ─ Detect document boundaries (content bounding box)
  ─ Estimate scan orientation (for photographed/scanned documents)
  ─ Detect skew angle (see §6)
  ─ Detect perspective distortion (see §6)

Stage 4: Geometric Correction (per page)
  ─ Apply deskew transform (rotate to correct skew angle)
  ─ Apply perspective correction (homography)
  ─ Crop to content bounding box
  ─ Normalize to target canvas size (pad with white if needed)

Stage 5: Color Correction
  ─ Detect and convert to sRGB color space
  ─ Apply ICC profile conversion if embedded
  ─ Apply illumination normalization (adaptive white balance for photographed docs)
  ─ Store pre-correction and post-correction versions

Stage 6: Resolution Normalization
  ─ Resample to analysis DPI (bilinear interpolation for downsample, Lanczos for upsample)
  ─ Assess effective resolution (actual information content vs. nominal DPI)
  ─ Store quality assessment metrics

Stage 7: Multi-Modality Generation
  ─ Generate all required modalities (see §4)
  ─ Store each modality in Object Storage
  ─ Produce reconstruction manifest
```

---

## 4. Multi-Modality Rendering

Each modality captures a different representation of the document content:

### 4.1 Standard Modalities

| Modality ID | Description | Format | Purpose |
|-------------|-------------|--------|---------|
| `rgb_300dpi` | Full-color RGB raster at 300 DPI | PNG (16-bit) | Primary analysis image |
| `gray_300dpi` | Grayscale luminance at 300 DPI | PNG (16-bit) | Texture, noise, frequency analysis |
| `lab_300dpi` | CIE-Lab color space at 300 DPI | PNG (16-bit) | Color-invariant comparison |
| `binary_adaptive` | Adaptive binarization (Sauvola) | PNG (1-bit) | Layout analysis, text extraction |
| `binary_global` | Global Otsu threshold binarization | PNG (1-bit) | Alternative layout analysis |
| `edge_canny` | Canny edge detection result | PNG (8-bit) | Edge-based feature extraction |
| `gradient_magnitude` | Sobel gradient magnitude | PNG (16-bit) | Typography and rendering analysis |

### 4.2 Enhanced Modalities (Enhanced/Deep Tiers)

| Modality ID | Description | Format | Purpose |
|-------------|-------------|--------|---------|
| `rgb_600dpi` | Full-color RGB raster at 600 DPI | PNG (16-bit) | High-resolution micro-DNA analysis |
| `channel_r`, `channel_g`, `channel_b` | Individual RGB channels | PNG (16-bit) | Chromatic aberration analysis |
| `uv_simulated` | UV fluorescence simulation (if EXIF indicates UV scan) | PNG | Document security feature detection |
| `ir_simulated` | Near-IR simulation (if applicable) | PNG | Ink layer analysis |

### 4.3 PDF-Specific Modalities

| Modality ID | Description | Format | Purpose |
|-------------|-------------|--------|---------|
| `pdf_objects_xml` | PDF object graph (text elements, images, paths) | XML | PDF structure forensics |
| `pdf_font_map` | Per-glyph font identity map | JSON | Typography analysis |
| `pdf_render_nofont` | Rendered with system fonts replacing embedded fonts | PNG | Font substitution detection |
| `pdf_xobjects` | Extracted image XObjects | PNG collection | Embedded image forensics |

---

## 5. PDF Vector Extraction

For PDF documents, the DRE performs deep object graph extraction using PyMuPDF's `page.get_text("rawdict")` and `page.get_drawings()` APIs.

### 5.1 Extracted PDF Elements

**Text elements**:
- Per-character: character value, bounding box (x, y, width, height), font name, font size, color, origin point
- Per-word: word string, bounding box, font statistics
- Per-line: line string, bounding box, baseline y-coordinate

**Vector graphics**:
- Paths: fill color, stroke color, line width, path points
- Rectangles: geometry, fill, stroke
- Lines: start/end points, width, color

**Embedded images (XObjects)**:
- Image bounding box within page
- Image dimensions
- Color space
- Compression method
- Raw image data extraction

**Annotations and form fields**:
- Annotation type, bounding box, content, creation date

### 5.2 Object Provenance Tracking

Each extracted PDF object carries its PDF object ID (obj_id, gen_id), enabling cross-reference with the raw PDF structure for metadata forensics. This object-level provenance is used by the Object Relationship Graph engine (see [14_Object_Relationship_Graph]).

---

## 6. Skew and Perspective Correction

### 6.1 Skew Detection Algorithm

Skew in scanned documents is detected using the Hough Line Transform:

1. Apply Canny edge detection to the grayscale image
2. Apply Probabilistic Hough Line Transform (OpenCV `HoughLinesP`)
3. Collect all detected lines with length > minimum_line_length (adaptive based on document size)
4. Compute the angle of each detected line relative to horizontal
5. Compute the histogram of line angles (1-degree bins)
6. The dominant angle cluster corresponds to the document skew
7. Skew angle = weighted mean of angles in the dominant cluster

**Accuracy**: ±0.1 degrees for typical document scans with 300 DPI input.

**Correction**: Rotate the image by the negative of the detected skew angle using `cv2.warpAffine` with `INTER_LANCZOS4` interpolation. Fill with white (document background color estimated from corner pixels).

### 6.2 Perspective Correction (Photographed Documents)

For documents photographed with a camera at an angle (keystoning):

1. Detect document boundaries using a combination of:
   - Canny edge detection
   - Contour finding (`cv2.findContours`)
   - Polygon approximation (`cv2.approxPolyDP`)
   - Selection of the largest quadrilateral contour
2. Identify the four corner points of the document quadrilateral
3. Compute target rectangle dimensions (preserve aspect ratio of detected quadrilateral)
4. Compute homography matrix (`cv2.getPerspectiveTransform`)
5. Apply perspective transformation (`cv2.warpPerspective`)

**Limitation**: Perspective correction is only applied when a clear quadrilateral boundary is detected with confidence > 0.8. For ambiguous boundaries, reconstruction proceeds without perspective correction, and the forensic report notes this limitation.

---

## 7. Color Space Normalization

### 7.1 sRGB Linearization

All color images are normalized to the sRGB color space using the ICC profile embedded in the document (if present) or the assumption of sRGB input (for documents without ICC profiles).

**ICC Profile Handling**: PyMuPDF extracts embedded ICC profiles. Python's `colour-science` library (or `Little CMS` via `pycms`) converts to sRGB with D50 illuminant chromatic adaptation.

**Illumination Normalization (for photographed documents)**:
For documents photographed under non-standard lighting, adaptive white balance correction is applied:
1. Estimate the illuminant color from white/near-white regions of the document
2. Apply von Kries chromatic adaptation to neutralize the illuminant

This step is flagged in the reconstruction quality report: it modifies the image and may affect color-based forensic features. Color forensics downstream accounts for this correction.

### 7.2 Dynamic Range Assessment

Documents scanned with incorrect exposure settings may have clipped highlights or crushed shadows. The DRE computes:
- **Highlight clipping fraction**: pixels at or above 255 (8-bit) or 65535 (16-bit) / total pixels
- **Shadow clipping fraction**: pixels at 0 / total pixels

High clipping fractions reduce the reliability of color and texture forensic features and are reported in the reconstruction quality assessment.

---

## 8. Resolution and Quality Assessment

### 8.1 Effective Resolution Estimation

The nominal DPI provided by a file does not always reflect the actual information content. A JPEG image can be upsampled to 600 DPI while containing only 72 DPI of actual detail. GDI measures the effective resolution:

**Algorithm**: Acutance-based resolution estimation
1. Compute the Laplacian of Gaussian (LoG) response across scales
2. Find the scale at which the LoG response peaks for text edges
3. Convert peak scale to effective DPI estimate

This effective DPI is used to determine which genome features can be reliably computed.

### 8.2 Quality Metrics

| Metric | Formula | Range | Threshold |
|--------|---------|-------|-----------|
| Sharpness (Laplacian variance) | var(Laplacian(image)) | 0–∞ | < 100 → low quality warning |
| Noise level (σ²) | Median absolute deviation in smooth regions | 0–255 | > 20 → high noise warning |
| Contrast (RMS contrast) | std(grayscale) | 0–127 | < 30 → low contrast warning |
| Compression artifact score | Mean block-boundary discontinuity | 0–100 | > 40 → severe JPEG artifacts |

These metrics are stored in the genome header as reconstruction_quality and influence per-feature confidence downstream.

---

## 9. Reconstruction Manifest

The Reconstruction Manifest is a structured JSON document produced by the DRE, listing all generated modalities and their Object Storage locations:

```json
{
  "job_id": "uuid-v4",
  "document_format": "PDF",
  "page_count": 2,
  "reconstruction_quality": {
    "sharpness": 450.2,
    "noise_level": 3.1,
    "contrast": 78.5,
    "compression_artifact_score": 12.3,
    "effective_dpi": 308,
    "highlight_clipping_fraction": 0.002,
    "shadow_clipping_fraction": 0.001,
    "skew_corrected": true,
    "skew_angle_degrees": -0.85,
    "perspective_corrected": false
  },
  "modalities": [
    {
      "modality_id": "rgb_300dpi",
      "page": 1,
      "object_key": "tenants/t123/jobs/j456/reconstructed/page1_rgb_300dpi.png",
      "width_px": 2480,
      "height_px": 3508,
      "bit_depth": 16,
      "color_space": "sRGB",
      "size_bytes": 52428800
    }
  ],
  "pdf_specifics": {
    "object_map_key": "tenants/t123/jobs/j456/reconstructed/pdf_objects.xml",
    "font_map_key": "tenants/t123/jobs/j456/reconstructed/pdf_font_map.json",
    "embedded_image_count": 3
  }
}
```

---

## 10. Error Handling and Edge Cases

| Edge Case | Handling Strategy |
|-----------|------------------|
| Blank document | Detected by low content coverage (<2% non-white pixels). Flagged as blank. Layout features extracted but no typography/text features. |
| All-black document | Detected by high dark coverage. Flagged. Potential scan error. |
| Extremely small document (< 1/4 A4) | Processed but resolution warning issued; micro-DNA features may be unreliable. |
| Extremely large document (> 10,000 × 14,000 px) | Downsampled to maximum supported size; original preserved in storage. Warning issued. |
| Corrupted file (unrecoverable) | DRE returns RECONSTRUCTION_FAILED status. Job routes to human review with raw binary available. |
| Encrypted PDF (unknown password) | Best-effort metadata extraction only. Flagged as encrypted. |
| Multi-page document with mixed orientations | Each page processed independently with orientation detection. |
| Document with embedded video/audio | AV content ignored. Flagged as anomalous (unexpected embedded content). |
| Zero-byte file | Rejected immediately with HTTP 400 at ingestion layer (pre-reconstruction). |

---

## 11. Performance Characteristics

| Document Type | Reconstruction Time (P50) | Reconstruction Time (P95) |
|---------------|--------------------------|--------------------------|
| Single-page PDF, text only | 2.1 s | 5.0 s |
| Single-page scanned image (JPEG, 300 DPI) | 1.5 s | 3.5 s |
| Multi-page PDF (10 pages) | 8.5 s | 20.0 s |
| Complex PDF with images | 4.0 s | 12.0 s |
| Camera photograph (DNG, 12 MP) | 3.5 s | 8.0 s |
| TIFF, 600 DPI, single page | 3.0 s | 7.0 s |

**Memory**: Peak RSS ~4–8 GB for typical documents at 300 DPI. High-DPI (600+) documents can reach 16 GB for large page sizes.

---

## 12. Security Considerations

### 12.1 Code Execution Risk in Document Parsing

PDF documents can contain active content (JavaScript, forms, embedded executables). The DRE mitigates this:
- PyMuPDF's rendering mode disables JavaScript execution at the rendering layer
- PDF parsing runs in a sandboxed container with no network access and restricted filesystem access (seccomp profile)
- Any exception in the parser that could indicate malicious content is logged as a security event

### 12.2 Steganography Detection

The DRE performs basic LSB (Least Significant Bit) steganography detection on raster images:
- Analyze LSB plane for non-random statistical patterns (chi-square test)
- Flag if LSB plane shows significantly non-random distribution
- This is a preliminary screen; specialized stego analysis is outside the current scope

### 12.3 Resource Exhaustion Protection

- Memory allocation is bounded: large files are processed in streaming chunks where possible
- Processing time is bounded by a hard timeout (configurable per tier; default 120s for reconstruction)
- Timeout triggers job suspension with RECONSTRUCTION_TIMEOUT status

---

*Previous: [05_Genome_Extraction_Engine](../05_Genome_Extraction_Engine/README.md)*
*Next: [07_Layout_Analysis](../07_Layout_Analysis/README.md)*
*Return to: [Master Index](../README.md)*
