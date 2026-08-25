# Document 40 — Reverse Engineering Engine
## GDI: Document Creation Pipeline Reconstruction

**Version:** 2.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Authors:** Principal Architect, Chief Research Engineer, Technical Documentation Lead
**Cross-References:** [06_Document_Reconstruction_Engine], [08_Typography_Analysis], [09_Rendering_Analysis], [12_Noise_Analysis], [13_Metadata_Analysis]

---

## Table of Contents

1. [Purpose & Scientific Rationale](#1-purpose--scientific-rationale)
2. [Observable Evidence Taxonomy](#2-observable-evidence-taxonomy)
3. [Reverse Engineering Architecture](#3-reverse-engineering-architecture)
4. [Inference Pipeline & State Machine](#4-inference-pipeline--state-machine)
5. [Inferred Creation Pipeline Stages](#5-inferred-creation-pipeline-stages)
    - [5.1 Stage A: Authoring & Typesetting Software](#51-stage-a-authoring--typesetting-software)
    - [5.2 Stage B: Vector PDF Producer & Font Engine](#52-stage-b-vector-pdf-producer--font-engine)
    - [5.3 Stage C: Physical Print Hardware](#53-stage-c-physical-print-hardware)
    - [5.4 Stage D: Physical Scan / Acquisition Hardware](#54-stage-d-physical-scan--acquisition-hardware)
    - [5.5 Stage E: Digital Post-Processing & Manipulation](#55-stage-e-digital-post-processing--manipulation)
6. [Bayesian Pipeline Inference Algorithm](#6-bayesian-pipeline-inference-algorithm)
7. [Output Schema & Evidence Graph](#7-output-schema--evidence-graph)
8. [Confidence, Limitations, and Uncertainty Estimation](#8-confidence-limitations-and-uncertainty-estimation)
9. [Failure Modes & Fallback Strategies](#9-failure-modes--fallback-strategies)

---

## 1. Purpose & Scientific Rationale

Traditional document verification asks a binary question: *"Does this document match the template?"*

The **Document Reverse Engineering Engine (DREE)** addresses the deeper forensic question: ***"How was this document produced, step-by-step, from initial creation to final digital submission?"***

Rather than relying solely on pairwise feature comparison, the DREE analyzes microscopic, rendering, noise, frequency, and metadata artifacts to reconstruct the probable **Document Creation & Processing Pipeline**.

**Scientific Guardrails**:
- The DREE does not invent unobservable history.
- Every inferred pipeline stage must be explicitly supported by observable physical/digital evidence.
- Every inference includes a quantitative confidence bound and discloses inherent limitations (e.g., distinguishing whether a PDF was exported directly from Microsoft Word 2019 vs. Word 2021 when both use identical PDF Producer libraries).

---

## 2. Observable Evidence Taxonomy

| Pipeline Phase | Observable Artifacts | Extracting Engine |
|----------------|----------------------|-------------------|
| **Authoring** | Document layout grids, margin definitions, font selection, line spacing rules | Layout, Typography |
| **PDF Export** | PDF version, object graph structure, font embedding types, XMP metadata history | Metadata, Object Graph |
| **Rendering** | Anti-aliasing gamma, ClearType subpixel order, edge sharpness, hinting profile | Rendering |
| **Physical Printing** | Halftone LPI/angle, toner satellite density, ink spread, paper grain interaction | Micro-DNA, Texture |
| **Physical Scanning** | PRNU sensor noise, CCD row/column striping, Moiré interference, optical distortion | Noise, Frequency |
| **Digital Editing** | Double-compression DCT combs, localized noise variance shifts, edge jitter | Frequency, Noise, Micro-DNA |

---

## 3. Reverse Engineering Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        HIERARCHICAL GENOME & MODALITIES                │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│               REVERSE ENGINEERING INFERENCE ORCHESTRATOR               │
└───────┬──────────────┬──────────────┬──────────────┬──────────────┬────┘
        │              │              │              │              │
        ▼              ▼              ▼              ▼              ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
│ Software     ││ PDF Producer ││ Print        ││ Acquisition  ││ Editing &    │
│ Inferencer   ││ Inferencer   ││ Inferencer   ││ Inferencer   ││ Manipulation │
└───────┬──────┘└───────┬──────┘└───────┬──────┘└───────┬──────┘└───────┬──────┘
        │              │              │              │              │
        └──────────────┴──────────────┼──────────────┴──────────────┘
                                      ▼
┌────────────────────────────────────────────────────────────────────────┐
│                BAYESIAN PIPELINE GRAPH RECONSTRUCTION                  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│            RECONSTRUCTED CREATION PIPELINE REPORT & PROVENANCE         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Inference Pipeline & State Machine

```
[DOCUMENT INGESTED] ──▶ [EXTRACT GENOME] ──▶ [CLASSIFY MODALITY (DIGITAL vs PHYSICAL)]
                                                           │
              ┌────────────────────────────────────────────┴────────────────────────────────────────────┐
              ▼                                                                                         ▼
   [DIGITAL NATIVE BRANCH]                                                                 [PHYSICAL ACQUISITION BRANCH]
   ├── Infer Authoring SW                                                                  ├── Infer Scanner / Camera Make/Model
   ├── Infer PDF Engine                                                                    ├── Infer Print Hardware (Laser vs Inkjet)
   └── Detect Incremental Edits                                                            └── Detect Rescan / Composite Multi-pass
              │                                                                                         │
              └────────────────────────────────────────────┬────────────────────────────────────────────┘
                                                           ▼
                                         [RECONSTRUCT PIPELINE GRAPH & ESTIMATE CONFIDENCE]
```

---

## 5. Inferred Creation Pipeline Stages

### 5.1 Stage A: Authoring & Typesetting Software
- **Evidence**: Font metrics, kerning table structure, default paragraph line spacing ratios, XMP Creator tags.
- **Inference Target**: Microsoft Word (v2016/2019/365), Adobe InDesign (v17–19), LibreOffice Writer, LaTeX.

### 5.2 Stage B: Vector PDF Producer & Font Engine
- **Evidence**: PDF Producer string, PDF cross-reference table format, stream compression algorithms, font subset naming conventions (`[A-Z]{6}\+FontName`).
- **Inference Target**: Adobe PDF Library, Quartz PDFContext (macOS), Cairo, pdfTeX, Skia/PDFium.

### 5.3 Stage C: Physical Print Hardware
- **Evidence**: Halftone screen frequency (LPI), screen angle ($\theta_{\text{screen}}$), toner satellite count per $\text{mm}^2$, ink bleeding into paper fibers.
- **Inference Target**: Monochrome Laser (HP/Brother), Color Laser (Xerox/Canon), Thermal Inkjet (HP/Epson), Offset Commercial Printing.

### 5.4 Stage D: Physical Scan / Acquisition Hardware
- **Evidence**: PRNU sensor noise correlation ($PCE$), CCD/CMOS striping, optical radial distortion, resolution acutance.
- **Inference Target**: Flatbed Scanner (Epson/Fujitsu), Document Feeder, Mobile Camera (iPhone/Android).

### 5.5 Stage E: Digital Post-Processing & Manipulation
- **Evidence**: DCT double-compression coefficient combs, localized noise variance discrepancies, sub-pixel edge jitter, mixed anti-aliasing profiles.
- **Inference Target**: Photoshop editing, Acrobat form fill, GIMP, Generative AI in-painting.

---

## 6. Bayesian Pipeline Inference Algorithm

For a candidate pipeline stage $S_i$ with observable evidence vector $\mathbf{E}$:

$$P(S_i \mid \mathbf{E}) = \frac{P(\mathbf{E} \mid S_i) \cdot P(S_i)}{\sum_j P(\mathbf{E} \mid S_j) \cdot P(S_j)}$$

where $P(S_i)$ is the prior likelihood of pipeline stage $S_i$ within the target document class, and $P(\mathbf{E} \mid S_i)$ is the likelihood of observing evidence $\mathbf{E}$ given stage $S_i$.

---

## 7. Output Schema & Evidence Graph

```json
{
  "reconstructed_pipeline": {
    "pipeline_id": "pip-88a7b6c5-d4e3-2f1a",
    "modality_classified": "PHYSICAL_SCAN_OF_PRINTED_DOCUMENT",
    "stages": [
      {
        "stage_number": 1,
        "stage_name": "AUTHORING_SOFTWARE",
        "inferred_value": "Microsoft Word for Office 365",
        "confidence": 0.94,
        "supporting_evidence": [
          {"feature": "typo.linespacing.ratio", "observed": 1.15, "matches_profile": "MS_WORD_DEFAULT"},
          {"feature": "meta.pdf.creator", "observed": "Microsoft® Word for Microsoft 365"}
        ],
        "limitations": "Cannot distinguish Office 365 build 2208 vs 2209 based solely on layout."
      },
      {
        "stage_number": 2,
        "stage_name": "PRINT_HARDWARE",
        "inferred_value": "Monochrome Laser Printer (HP LaserJet Series)",
        "confidence": 0.88,
        "supporting_evidence": [
          {"feature": "microdna.dots.screen_frequency_lpi", "observed": 141.2, "expected_range": [140.0, 145.0]},
          {"feature": "microdna.texture.toner_satellite_density", "observed": 42.1, "unit": "count/mm2"}
        ]
      }
    ]
  }
}
```

---

## 8. Confidence, Limitations, and Uncertainty Estimation

Every inferred stage includes an explicit **Limitation Disclosure**:
- If evidence is ambiguous between two candidate tools (e.g., Adobe Acrobat DC vs. Adobe InDesign exporting via the same underlying PDF library), both candidates are reported with split confidence ($P(S_1)=0.51, P(S_2)=0.49$).
- Aleatoric uncertainty (irreducible physical scan noise) and Epistemic uncertainty (lack of evidence tags) are reported separately.

---

## 9. Failure Modes & Fallback Strategies

- **Stripped Metadata**: Document metadata is completely absent. *Fallback*: Shift weighting to physical rendering, typography, and noise analysis.
- **Multiple Rescans**: Document was printed, scanned, re-printed, and re-scanned. *Fallback*: Flag high multi-pass artifact score; restrict pipeline inference to final acquisition layer.

---

*Previous: [39_Digital_Twin](../39_Digital_Twin/README.md)*
*Next: [41_Constraint_Engine](../41_Constraint_Engine/README.md)*
*Return to: [Master Index](../README.md)*
