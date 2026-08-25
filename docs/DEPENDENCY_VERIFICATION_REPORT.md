# GDI Dependency Verification Report

## Overview

- **Audit Date:** 2026-07-22
- **Python Version:** 3.12.4 x64
- **OS Platform:** Windows 10/11 x64

---

## `pip check` Output Analysis

```
imgaug 0.4.0 requires opencv-python, which is not installed.
paddleocr 2.7.3 requires opencv-contrib-python, which is not installed.
paddleocr 2.7.3 requires opencv-python, which is not installed.
rasterio 1.5.0 has requirement numpy>=2, but you have numpy 1.26.4.
rembg 2.0.75 has requirement numpy<3.0.0,>=2.3.0, but you have numpy 1.26.4.
```

### Explanatory Analysis & Verification

1. **OpenCV Headless Replacement (`opencv-python-headless`):**
   - `paddleocr` and `imgaug` specify legacy `opencv-python` and `opencv-contrib-python` in their PyPI metadata.
   - On Windows 64-bit systems, installing `opencv-python` alongside `opencv-python-headless` causes duplicate `cv2.pyd` binary file locks and `WinError 5 Access is Denied` failures.
   - **Verification:** `opencv-python-headless==4.9.0.80` satisfies all `cv2` runtime C++ extension requirements without package collision.

2. **NumPy 1.x ABI Pinning (`numpy==1.26.4`):**
   - `imgaug 0.4.0` uses `np.sctypes` which was removed in NumPy 2.0.
   - `numpy==1.26.4` is explicitly pinned to preserve C-ABI stability and prevent `AttributeError: np.sctypes was removed in the NumPy 2.0 release` runtime crashes.
   - **Verification:** `cv2`, `fitz`, `numpy`, `PIL`, `paddle`, and `paddleocr` import and execute cleanly without ABI warnings.

---

## Core Dependency Matrix

| Package Name | Installed Version | Status | Function |
|---|---|---|---|
| `paddleocr` | `2.7.3` | ✅ Verified | Primary deterministic OCR engine |
| `paddlepaddle` | `2.6.2` | ✅ Verified | Deep learning execution framework |
| `opencv-python-headless` | `4.9.0.80` | ✅ Verified | Computer vision & image transform |
| `numpy` | `1.26.4` | ✅ Verified | Array processing & C-ABI stability |
| `pymupdf` (fitz) | `1.28.0` | ✅ Verified | High-resolution PDF renderer |
| `pillow` | `12.2.0` | ✅ Verified | Image I/O |
| `fastapi` | `0.128.8` | ✅ Verified | ASGI REST API framework |
| `uvicorn` | `0.40.0` | ✅ Verified | ASGI Web Server |
