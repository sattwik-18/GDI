# Document 47 — AI Expert Architecture
## GDI: Decoupled Specialist AI Expert Network Architecture

**Version:** 2.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Authors:** Principal Architect, Chief Research Engineer, Principal AI Engineer
**Cross-References:** [05_Genome_Extraction_Engine], [16_Multi_Model_AI], [18_Fusion_Engine], [34_AI_Model_Management]

---

## Table of Contents

1. [Architectural Redesign Rationale](#1-architectural-redesign-rationale)
2. [Strict Decoupling Invariants](#2-strict-decoupling-invariants)
3. [Specialist AI Expert Taxonomy](#3-specialist-ai-expert-taxonomy)
    - [3.1 Layout Expert](#31-layout-expert)
    - [3.2 Typography Expert](#32-typography-expert)
    - [3.3 Rendering Expert](#33-rendering-expert)
    - [3.4 Texture Expert](#34-texture-expert)
    - [3.5 Frequency Expert](#35-frequency-expert)
    - [3.6 Noise Expert](#36-noise-expert)
    - [3.7 Metadata Expert](#37-metadata-expert)
    - [3.8 Graph Expert](#38-graph-expert)
    - [3.9 Printer Hardware Expert](#39-printer-hardware-expert)
    - [3.10 Scanner Hardware Expert](#310-scanner-hardware-expert)
    - [3.11 Semantic Expert](#311-semantic-expert)
4. [Expert Container Orchestration & Scaling](#4-expert-container-orchestration--scaling)
5. [Disagreement & Divergence Handling](#5-disagreement--divergence-handling)
6. [Fallback & Degraded Mode Execution](#6-fallback--degraded-mode-execution)
7. [Explainability Output Formats](#7-explainability-output-formats)

---

## 1. Architectural Redesign Rationale

In GDI Version 1.0, deep learning models were grouped into a generic AI pipeline (`ai-engine-svc`). This created inter-model dependencies, shared latency bottlenecks, and risks of cross-talk bias where one model's visual embeddings could corrupt another model's structural analysis.

Version 2.0 replaces generic AI pipelines with **11 Decoupled Specialist AI Experts**. Each expert is a self-contained, domain-specific deep learning microservice focused exclusively on a single physical, visual, or structural dimension.

---

## 2. Strict Decoupling Invariants

The AI Expert Architecture enforces three strict system invariants:

1. **Zero Direct Inter-Expert Communication**: No AI Expert may call, query, or share memory with any other AI Expert.
2. **Standardized Evidence Output**: Every expert emits outputs strictly as `EvidenceObject` records (containing Log-Likelihood Ratios, spatial bounding boxes, and MC-dropout epistemic variances).
3. **Single Consumer Destination**: All AI Expert outputs are routed **only to the Evidence Fusion Engine**.

```
                           ┌───────────────────────────┐
                           │   Reconstructed Modalities│
                           └─────────────┬─────────────┘
                                         │
     ┌───────────┬───────────┬───────────┼───────────┬───────────┬───────────┐
     ▼           ▼           ▼           ▼           ▼           ▼           ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ Layout  │ │  Typo   │ │ Render  │ │ Texture │ │ Noise   │ │ Printer │ │ Semantic│
│ Expert  │ │ Expert  │ │ Expert  │ │ Expert  │ │ Expert  │ │ Expert  │ │ Expert  │
└────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
     │           │           │           │           │           │           │
     └───────────┴───────────┴─────┬─────┴───────────┴───────────┴───────────┘
                                   │  (Strictly Decoupled Output)
                                   ▼
                   ┌───────────────────────────────┐
                   │    EVIDENCE FUSION ENGINE     │
                   └───────────────────────────────┘
```

---

## 3. Specialist AI Expert Taxonomy

### 3.1 Layout Expert
- **Backbone**: Fine-tuned LayoutLMv3-Large + Vision Transformer.
- **Role**: Evaluates visual/textual structural alignment and flags layout component insertion/deletion.

### 3.2 Typography Expert
- **Backbone**: ResNet-50 Font Classifier + Custom Glyph Contour ViT.
- **Role**: Identifies font families, measures character stroke width anomalies, and detects font substitutions.

### 3.3 Rendering Expert
- **Backbone**: Multi-scale CNN trained on rendering engine edge transitions.
- **Role**: Classifies anti-aliasing profiles, ClearType subpixel order, and rendering gamma inconsistencies.

### 3.4 Texture Expert
- **Backbone**: EfficientNet-B4 trained on paper fiber micro-textures and GLCM representations.
- **Role**: Detects paper grain anomalies, cover-up paint materials, and surface roughness shifts.

### 3.5 Frequency Expert
- **Backbone**: 2D Spectrogram ResNet + Fourier DCT Comb Analyzer.
- **Role**: Identifies double JPEG compression artifacts, spectral energy shifts, and periodograms.

### 3.6 Noise Expert
- **Backbone**: Custom CNN Denoising Residual Network (DnCNN).
- **Role**: Evaluates spatial sensor noise consistency, PRNU cross-correlation, and noise level shifts.

### 3.7 Metadata Expert
- **Backbone**: XGBoost / Transformer Sequence Model on PDF Object Streams.
- **Role**: Analyzes XMP edit histories, PDF incremental update trees, and flags metadata spoofing.

### 3.8 Graph Expert
- **Backbone**: Graph Neural Network (GNN / Graph Attention Network - GAT).
- **Role**: Embeds Object Relationship Graphs and predicts structural Graph Edit Distances.

### 3.9 Printer Hardware Expert
- **Backbone**: Microscopic Patch CNN Classifier ($600\text{ DPI}$).
- **Role**: Classifies print technology (Monochrome Laser, Color Laser, Inkjet, Thermal) and estimates halftone LPI.

### 3.10 Scanner Hardware Expert
- **Backbone**: PRNU Noise Pattern Correlation Network.
- **Role**: Identifies acquisition hardware fingerprints (Flatbed vs Feeder vs Mobile Camera).

### 3.11 Semantic Expert
- **Backbone**: Fine-tuned RoBERTa / DeBERTa NLP Transformer.
- **Role**: Evaluates semantic textual consistency (e.g., verifying date format validity and cross-field logic).

---

## 4. Expert Container Orchestration & Scaling

- Each expert runs in a dedicated Kubernetes deployment with GPU request limits (`nvidia.com/gpu: 1`).
- Autoscaling is managed via KEDA based on Kafka topic consumer lag.

---

## 5. Disagreement & Divergence Handling

If Expert A (Typography) reports $\text{LLR} = +3.5$ (Authentic) while Expert B (Noise) reports $\text{LLR} = -4.2$ (Fraudulent):
- The experts do not interact or reconcile.
- The Evidence Fusion Engine receives both raw `EvidenceObject` records, calculates the Engine Divergence Index $D_{\text{engine}}$, penalizes global score confidence, and maps the localized discrepancy to the final report.

---

## 6. Fallback & Degraded Mode Execution

If an AI Expert times out or crashes:
- The Genome Orchestrator sets `Fail_k = 1` for that expert.
- The Fusion Engine re-balances remaining expert weights using the Bayesian Reliability Model without failing the pipeline.

---

## 7. Explainability Output Formats

Every expert emits Integrated Gradients or Attention Map tensors alongside raw scores, ensuring 100% explainability coverage.

---

*Previous: [46_Template_Evolution](../46_Template_Evolution/README.md)*
*Next: [48_Forensic_Ontology](../48_Forensic_Ontology/README.md)*
*Return to: [Master Index](../README.md)*
