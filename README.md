# GDI Prototype 1 — Genome Extraction Engine

## Status & Status Legend

> [!NOTE]
> This repository contains Prototype 1 of the Genome Extraction Engine.
> Status indicators:
> - `[IMPL]` Implemented
> - `[TEST]` Tested in development environment
> - `[BENCH]` Benchmarked with synthetic metrics
> - `[PLAN]` Planned for future versions

---

## Overview

**GDI Prototype 1** is the first working prototype of the Document Genome Intelligence (GDI) Platform.

Its sole responsibility is to **reliably generate a deterministic Document Genome** from an uploaded document.

**Input formats:** `[IMPL]` PDF · PNG · JPEG · TIFF · BMP · WebP

**Output:**
- `[IMPL]` Canonical Document Genome (structured JSON)
- `[IMPL]` Per-page feature vectors (geometry, texture, frequency, edge, OCR, statistical)
- `[IMPL]` Processing Manifest (step-by-step execution log w/ CPU/memory metrics)
- `[IMPL]` Quality Report (blur, sharpness, noise, contrast per page)
- `[IMPL]` PostgreSQL persistence of all entities

---

## Operating Environment

- **Supported Python:** 3.12+ `[TEST]`
- **Recommended OS:** Linux / Docker `[TEST]` (Full PaddleOCR deterministic support)
- **Windows Support:** Development/testing mode supported via `DEV_OCR_FALLBACK=true` `[TEST]`

---

## Architecture & Clean Boundaries

This application is built as a **modular monolith** following Clean Architecture principles:

```
Presentation  →  Application  →  Domain  →  Infrastructure
 (FastAPI)       (Pipeline)     (Pure Py)   (SQLAlchemy / OpenCV / PaddleOCR)
```

### Key Design Abstractions
| Abstraction | Status | Purpose |
|---|---|---|
| `ProcessingContext` | `[IMPL]` | Single state carrier across all steps |
| `PipelineStep` | `[IMPL]` | Standard `execute(context)` step contract |
| `FeatureExtractor` | `[IMPL]` | Standard interface for feature groups |
| `FeatureRegistry` | `[IMPL]` | Dynamic registration & discovery of extractors |
| `PipelineRegistry` | `[IMPL]` | Configurable pipeline step assembly |
| `StorageProvider` | `[IMPL]` | Abstract file storage interface |
| `ErrorCatalog` | `[IMPL]` | Centralized structured error codes |

---

## Quick Start (Docker)

```bash
cp .env.example .env
docker compose up --build
```

API available at http://localhost:8000. Interactive docs at http://localhost:8000/docs.

---

## Quick Start (Local Development)

```bash
# 1. Create environment
python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate # Linux/Mac

# 2. Install pinned dependencies
pip install -r requirements-dev.txt

# 3. Environment configuration
cp .env.example .env

# 4. Database setup
alembic upgrade head

# 5. Run API server
uvicorn src.main:app --reload
```

---

## Testing & Quality Assurance

```bash
# Run full test suite with coverage
pytest tests/ -v --cov=src

# Run static analysis
black --check src/ tests/
isort --check src/ tests/
ruff check src/ tests/
mypy src/

# Run determinism regression test (10 runs)
pytest tests/regression/ -v -s

# Run benchmarks
python benchmarks/run_benchmarks.py
```

---

## What Is NOT Implemented (Out of Scope for Prototype 1)

The following features are **explicitly out of scope** for Prototype 1 `[PLAN]`:
- Similarity scoring / Z-score comparison
- Bayesian evidence fusion engine
- Trust computation
- Digital twin verification
- Explainable Evidence Graphs (EEG)
- Qdrant vector database / Redis cache
- ECDSA hardware cryptographic sealing (uses `SHA256_SOFT` instead)
- AI semantic embeddings (DINOv2)
