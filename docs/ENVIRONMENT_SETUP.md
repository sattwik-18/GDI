# GDI Genome Engine — Development Environment & Setup Guide

## Operating System & System Requirements

- **Supported Operating Systems:** Windows 10/11 x64, Linux (Ubuntu 22.04+), macOS 12+
- **Python Version:** 3.12+ (Tested on 3.12.4 x64)
- **OCR Subsystem:** PaddleOCR 2.7.3 (Primary Deterministic Engine) + Tesseract OCR (Fallback/Dev)
- **C++ Runtime / System Dependencies (Linux/Docker):**
  - `libgl1-mesa-glx`
  - `libglib2.0-0`
  - `libgomp1`
  - `tesseract-ocr`

---

## Step-by-Step Installation

### 1. Environment Setup

```bash
# Clone repository
cd d:\GDI

# Create virtual environment (Optional but recommended)
python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate # Linux/macOS
```

### 2. Dependency Installation

```bash
# Install locked production and development dependencies
pip install -r requirements-dev.txt
```

### 3. Verification Commands

Run the following single-line validation command to verify all required C++ bindings and OCR modules load cleanly:

```bash
python -c "import torch; import paddleocr; import cv2; import fitz; import numpy; import PIL; print('All imports SUCCESS!')"
```

---

## Environment Configuration (`.env`)

Copy `.env.example` to `.env`:

```env
OCR_ENGINE_PROVIDER=paddleocr
DEV_OCR_FALLBACK=false
OCR_USE_GPU=false
OCR_LANG=en
OCR_CONFIDENCE_THRESHOLD=0.5
```

---

## Known Environment Issues & Solutions

### 1. OpenCV Dual Installation (`cv2.pyd` Access Denied / WinError 5)
- **Symptom:** `WinError 5 Access is denied: cv2.pyd`
- **Cause:** Installing both `opencv-python` and `opencv-python-headless` causes file collisions.
- **Solution:** Uninstall both `opencv-python` and `opencv-contrib-python`. Use strictly `opencv-python-headless==4.9.0.80`.

### 2. NumPy 2.0 ABI Mismatch (`AttributeError: np.sctypes`)
- **Symptom:** `AttributeError: np.sctypes was removed in the NumPy 2.0 release`
- **Cause:** `imgaug` (imported by `paddleocr` 2.7.3) relies on NumPy 1.x C-ABI features.
- **Solution:** Pin `numpy==1.26.4`.

### 3. PyTorch `shm.dll` Search Order on Windows
- **Symptom:** `OSError: [WinError 127] Error loading shm.dll` when importing modelscope/torch after paddle.
- **Solution:** In environments where `torch` is present, `import torch` prior to `import paddleocr` initializes Windows DLL search paths.
