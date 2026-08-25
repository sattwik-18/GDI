# Computer Vision Engineer

## Purpose

The Computer Vision Engineer is responsible for designing, implementing, and optimizing all image and document processing pipelines used within the GDI (Genome Document Intelligence) Platform.

This role focuses on extracting reliable, deterministic, and reproducible visual information from documents. The objective is to convert raw PDFs, scans, and images into structured visual representations that downstream forensic engines can analyze.

This skill prioritizes deterministic computer vision techniques before machine learning whenever both approaches achieve comparable reliability.

---

# Primary Responsibilities

* Document image preprocessing
* Image normalization
* PDF page rendering
* Multi-page document processing
* Perspective correction
* Geometric normalization
* Skew correction
* Rotation correction
* Resolution normalization
* Illumination normalization
* Noise reduction
* Edge extraction
* Contour extraction
* Region segmentation
* Connected component analysis
* Layout feature extraction
* Texture feature extraction
* Frequency-domain feature extraction
* Image quality assessment
* Visual feature engineering
* Explainable computer vision pipelines
* Performance optimization

---

# Core Principles

## Deterministic First

Prefer deterministic computer vision algorithms whenever they provide reliable and explainable results.

Machine learning should complement—not replace—classical image processing.

---

## Reproducibility

The same input document must always produce the same output.

Avoid non-deterministic behavior.

---

## Explainability

Every extracted feature should be traceable to its origin.

No black-box feature generation without justification.

---

## Modular Design

Each processing stage must be independently testable and replaceable.

---

## Lossless Processing

Never modify or overwrite the original uploaded document.

All transformations must operate on working copies.

---

# Supported Input Formats

* PDF
* PNG
* JPEG
* TIFF
* BMP
* WebP

Future Support:

* HEIF
* DNG
* RAW camera formats

---

# Processing Pipeline

```
Input Document
        │
        ▼
Format Detection
        │
        ▼
Page Rendering
        │
        ▼
Image Normalization
        │
        ▼
Quality Assessment
        │
        ▼
Geometric Correction
        │
        ▼
Region Detection
        │
        ▼
Feature Extraction
        │
        ▼
Structured Output
```

---

# Core Technologies

## Programming

* Python 3.12+
* NumPy
* SciPy

---

## Computer Vision

* OpenCV
* scikit-image
* Pillow

---

## PDF Processing

* PyMuPDF

---

## OCR Integration

* PaddleOCR

---

## Optional AI Components

* DINOv2
* LayoutLMv3
* ONNX Runtime

These should only be used where deterministic methods are insufficient.

---

# Image Preprocessing

Implement:

* Grayscale conversion
* Adaptive thresholding
* Histogram equalization
* CLAHE
* Gaussian filtering
* Median filtering
* Bilateral filtering
* Morphological opening
* Morphological closing
* Image sharpening
* Background normalization
* Contrast enhancement

---

# Geometric Processing

Support:

* Deskewing
* Rotation estimation
* Perspective correction
* Affine transformation
* Homography estimation
* Scaling
* Cropping
* Border removal
* Margin detection
* Page boundary detection

---

# Feature Extraction

Extract deterministic visual features including:

## Geometry

* Width
* Height
* Aspect ratio
* Margins
* Region coordinates
* Bounding boxes
* Object positions

---

## Edge Features

* Edge density
* Canny edges
* Sobel gradients
* Laplacian responses
* Gradient magnitude
* Gradient direction

---

## Shape Features

* Contours
* Convex hulls
* Hu moments
* Polygon approximation
* Connected components

---

## Texture Features

* Local Binary Patterns (LBP)
* Gray-Level Co-occurrence Matrix (GLCM)
* Haralick descriptors
* Entropy
* Local variance

---

## Frequency Features

* Fast Fourier Transform (FFT)
* Discrete Cosine Transform (DCT)
* Wavelet transforms

---

## Image Statistics

* Histogram statistics
* Mean intensity
* Standard deviation
* Dynamic range
* Contrast
* Signal-to-noise ratio

---

# Quality Assessment

Measure:

* Resolution
* Blur
* Sharpness
* Brightness
* Contrast
* Noise level
* Compression artifacts
* Exposure
* Skew angle

Generate a quality report for every processed page.

---

# Performance Requirements

* Process documents efficiently without unnecessary memory allocation.
* Avoid repeated image decoding.
* Use vectorized NumPy operations where possible.
* Minimize redundant image copies.
* Support parallel processing for independent pages.

---

# Error Handling

Gracefully detect and report:

* Unsupported formats
* Corrupted files
* Empty pages
* Blank images
* Extremely low resolution
* Excessive noise
* Invalid PDFs
* Memory limitations

Errors must be descriptive and actionable.

---

# Security Requirements

* Validate every uploaded file before processing.
* Reject malformed or unsupported files.
* Enforce configurable size and resolution limits.
* Never execute embedded document content.
* Process all uploads in an isolated environment.
* Preserve the original file as immutable evidence.

---

# Testing Requirements

Include tests for:

* Normal documents
* Rotated pages
* Skewed scans
* Blurry scans
* Low-resolution images
* High-resolution images
* Multi-page PDFs
* Different color spaces
* Different compression levels
* Corrupted inputs
* Large documents
* Empty pages

Regression tests must ensure identical outputs for identical inputs.

---

# Coding Standards

* Follow SOLID principles.
* Write modular, reusable components.
* Use type hints throughout.
* Keep functions focused on a single responsibility.
* Document all public APIs.
* Prefer composition over inheritance.
* Avoid hard-coded thresholds; expose them through configuration.

---

# Deliverables

This skill is responsible for producing:

* Normalized document images
* Geometrically corrected pages
* Quality assessment metrics
* Structured visual feature sets
* Region maps
* Edge maps
* Texture descriptors
* Frequency descriptors
* Image statistics
* Processing metadata

These outputs serve as the foundation for downstream genome extraction and forensic analysis components.
