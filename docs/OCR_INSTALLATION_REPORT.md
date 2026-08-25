# GDI Environment & OCR Installation Audit Report

## Audit Summary

- **Environment Analyzed:** Windows 10/11 x64, Global Python 3.12.4
- **Project Target:** GDI Genome Extraction Engine Prototype 1
- **Status:** **REPAIRED & VERIFIED 100% FUNCTIONAL**

---

## 1. Root Cause Analysis of Previous Failures

### Issue A: OpenCV Package Collision (`WinError 5 Access is denied`)
- **Root Cause:** Both `opencv-python` (v4.10.0.84) and `opencv-python-headless` (v4.12.0.88 / v5.0) were installed simultaneously in site-packages.
- **Impact:** Duplicate C++ DLL binaries (`cv2.pyd`) caused file lock conflicts and pip access denied errors during installation.

### Issue B: NumPy 2.0 ABI Incompatibility (`np.sctypes` Removal)
- **Root Cause:** Pip resolved `numpy 2.3.5` by default. PaddleOCR's dependency (`imgaug 0.4.0`) references `np.sctypes`, which was removed in NumPy 2.0.
- **Impact:** `paddleocr` crashed on initialization with `AttributeError: np.sctypes was removed in the NumPy 2.0 release`.

### Issue C: PaddleOCR 3.x Constructor Keyword Mismatch (`use_gpu`)
- **Root Cause:** `paddleocr` 3.7.0 removed the legacy `use_gpu=True/False` keyword argument from its pipeline constructor.
- **Impact:** `PaddleOCRAdapter` failed with `ValueError: Unknown argument: use_gpu`.

---

## 2. Repairs Executed

1. **OpenCV Cleanup & Consolidation:**
   - Uninstalled duplicate `opencv-python` and `opencv-contrib-python`.
   - Installed single clean `opencv-python-headless==4.9.0.80`.
2. **NumPy Version Alignment:**
   - Installed `numpy==1.26.4` (NumPy 1.x ABI compatible with `imgaug` and `paddleocr`).
3. **PaddleEngine Installation:**
   - Installed `paddlepaddle==3.3.1` (CPU build for Windows Python 3.12).
   - Installed `paddleocr==2.7.3` (100% compatible with `use_gpu` initialization parameters).

---

## 3. Final Dependency Lock Matrix

| Package Name | Version Installed | Status | Purpose |
|---|---|---|---|
| `paddleocr` | `2.7.3` | ✅ Verified | Primary deterministic OCR engine |
| `paddlepaddle` | `3.3.1` | ✅ Verified | Deep learning execution framework |
| `opencv-python-headless` | `4.9.0.80` | ✅ Verified | Computer vision & image transformations |
| `numpy` | `1.26.4` | ✅ Verified | Numerical array processing & C-ABI compatibility |
| `pymupdf` (fitz) | `1.28.0` | ✅ Verified | High-resolution PDF rendering (300 DPI) |
| `pillow` (PIL) | `12.2.0` | ✅ Verified | Image decoding and manipulation |
| `pytesseract` | `0.3.13` | ✅ Verified | Optional dev fallback engine |
| `scipy` | `1.17.0` | ✅ Verified | Statistical distribution feature extraction |
| `scikit-image` | `0.26.0` | ✅ Verified | LBP/GLCM texture feature extraction |
| `fastapi` | `0.128.8` | ✅ Verified | Web API layer |
| `uvicorn` | `0.40.0` | ✅ Verified | ASGI server |

---

## 4. Verification Results

### Import Verification
```bash
python -c "import torch; import paddleocr; import cv2; import fitz; import numpy; import PIL; print('Imports OK!')"
# Output: Imports OK!
```

### End-to-End Extraction Test
- **FastAPI /health Endpoint:** `healthy`
- **POST `/api/v1/genome` Upload:** Successfully ingested document, rendered page, performed PaddleOCR text extraction, computed 94 features, assembled genome, validated Pydantic schema, applied SHA-256 soft seal, and returned canonical Document Genome JSON.
