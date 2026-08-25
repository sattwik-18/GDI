# Changelog

All notable changes to the **GDI Genome Extraction Engine** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-22

### Added
- Canonical 17-stage Document Genome Extraction pipeline (`ProcessingContext` carrier architecture).
- Multi-format ingestion support for PDF, PNG, JPEG, TIFF, BMP, and WebP documents.
- Deterministic 108-feature vector generation (Geometry, LBP/GLCM Texture, FFT Frequency, Intensity Statistics, OCR/Layout Structure).
- PaddleOCR 2.7.3 primary OCR engine integration (`paddlepaddle 2.6.2` CPU backend).
- `DATABASE_OPTIONAL` setting in `DatabaseSettings` supporting graceful fallback in local development and strict enforcement in production.
- Environment fingerprinting utility (`compute_config_fingerprint`) recording system, CPU, Python, and dependency library hashes.
- CI/CD Smoke Test runner script (`scripts/smoke_test.py`).
- Clean Architecture Boundary Validator (`scripts/validate_architecture.py`).
- Golden Reference regression dataset in `tests/golden/` (`sample_certificate`, `sample_invoice`, `sample_degree`).
- Development-only pipeline artifact inspection endpoint (`POST /api/v1/genome/debug`).
- Comprehensive error catalog (`docs/errors/README.md`) and error response schemas.
- Dataset provenance manifest (`datasets/dataset.json`).

### Changed
- Refined `PersistenceStep` to handle unconfigured database connections safely when `DATABASE_OPTIONAL=true`.
- Consolidated region segmentation and layout analysis into a single `LayoutAnalysisStep`.
- Standardized floating point sanitization in `FeatureGroup` to prevent `NaN`/`Inf` serialization failures.

### Fixed
- Fixed OpenCV dual-installation package collision (`cv2.pyd` access denied errors).
- Fixed NumPy 2.0 ABI incompatibility by pinning `numpy==1.26.4`.
- Fixed PaddlePaddle 3.x dynamic graph C++ oneDNN `fused_conv2d` error on Windows CPU by installing `paddlepaddle==2.6.2`.
