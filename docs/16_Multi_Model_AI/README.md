# Document 16 — Multi-Model AI Engine
## GDI: AI Model Ensemble, Inference Pipeline, and MLOps

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [05_Genome_Extraction_Engine], [17_Similarity_Engine], [18_Fusion_Engine], [34_AI_Model_Management]

---

## Table of Contents

1. [Purpose and Architecture](#1-purpose-and-architecture)
2. [Model Zoo and Ensemble Topology](#2-model-zoo-and-ensemble-topology)
3. [Vision Foundation Model Integration](#3-vision-foundation-model-integration)
4. [Document Structure and Layout AI Models](#4-document-structure-and-layout-ai-models)
5. [Generative and Diffusion Forgery Detectors](#5-generative-and-diffusion-forgery-detectors)
6. [Inference Pipeline and Optimization](#6-inference-pipeline-and-optimization)
7. [Explainability Mechanisms](#7-explainability-mechanisms)
8. [Hardware Sizing and GPU Allocation](#8-hardware-sizing-and-gpu-allocation)

---

## 1. Purpose and Architecture

The Multi-Model AI Engine encapsulates all deep learning models used within GDI. Rather than relying on a single end-to-end black-box classifier, GDI employs a **decoupled ensemble of specialized AI models**, each tasked with extracting specific latent representations or detecting specific manipulation signatures.

All AI model outputs are mapped into canonical genome feature vectors or spatial heatmap layers, which are subsequently processed by the deterministic, interpretable Fusion and Decision Engines.

---

## 2. Model Zoo and Ensemble Topology

The platform integrates five primary model families:

```
                          ┌────────────────────────┐
                          │  Reconstructed Image   │
                          └───────────┬────────────┘
                                      │
        ┌─────────────────┬───────────┼───────────┬─────────────────┐
        ▼                 ▼           ▼           ▼                 ▼
┌───────────────┐ ┌──────────────┐ ┌─────┐ ┌──────────────┐ ┌──────────────┐
│ Vision        │ │ Layout /     │ │ Font│ │ Generative / │ │ Adversarial  │
│ Foundation    │ │ Structure    │ │ Classifier│ Deepfake     │ │ Anomaly      │
│ Embeddings    │ │ Transformer  │ │ CNN │ │ Detector     │ │ Autoencoder  │
└───────┬───────┘ └───────┬──────┘ └─┬───┘ └──────┬───────┘ └──────┬───────┘
        │                 │          │            │                │
        ▼                 ▼          ▼            ▼                ▼
   512-d Vector      Layout Map   Font ID    Diffusion Map    Anomaly Vector
        │                 │          │            │                │
        └─────────────────┴──────────┼────────────┴────────────────┘
                                     ▼
                        [ Genome Extraction Pipeline ]
```

| Model ID | Model Family | Backbone / Architecture | Output Dimension | Primary Task |
|----------|--------------|-------------------------|------------------|--------------|
| `M-VFM-01` | Vision Foundation | DINOv2 / ViT-L/14 | 1024-d Float32 | Deep visual similarity embeddings |
| `M-LAY-01` | Layout Transformer | LayoutLMv3-Large | Token BBoxes & Labels | Layout structural understanding |
| `M-FNT-01` | Font Classifier | ResNet-50 Fine-Tuned | 2000-class Probabilities | Visual font family identification |
| `M-GEN-01` | Deepfake/Diffusion | Patch-based ResNet + Frequency Head | Spatial Heatmap ($H \times W$) | Detection of AI-generated / in-painted regions |
| `M-AE-01` | Anomaly Autoencoder | Swin UNETR Autoencoder | Reconstruction Error Map | Unsupervised anomaly discovery |

---

## 3. Vision Foundation Model Integration (`M-VFM-01`)

GDI integrates DINOv2 (Vision Transformer with self-supervised learning) to extract semantic and visual features invariant to non-fraudulent illumination shifts.

### 3.1 Inference Flow
1. Crop document image into overlapping $224 \times 224$ patches (stride 112).
2. Pass patches through DINOv2 ViT-L/14 backbone.
3. Extract `CLS` token embedding for global representation ($1024\text{-d}$).
4. Extract patch-level tokens for local dense spatial feature maps ($14 \times 14$ grid per patch).

---

## 4. Document Structure and Layout AI Models (`M-LAY-01`)

LayoutLMv3 is utilized to analyze multimodal information (text, visual, spatial position):
- **Inputs**: Bounding boxes $[x_0, y_0, x_1, y_1]$, OCR text tokens, image patch.
- **Task**: Classify document hierarchy components (Header, Subheader, Field Label, Field Value, Footer, Logo).
- **Forensic Signal**: Discrepancies between expected semantic label sequence and detected structure flag structural insertion/deletion.

---

## 5. Generative and Diffusion Forgery Detectors (`M-GEN-01`)

With the rise of generative AI tools (e.g., Stable Diffusion, ControlNet, Photoshop Generative Fill), fraudsters can seamlessly synthesize document regions.

### 5.1 Artifact Detection Strategy
Generative models leave distinct spectral and gradient artifacts:
- **Spectrum Discrepancy**: Loss of high-frequency texture details in generated patches.
- **Color Swatches / Artifact Correlation**: Cross-channel gradient anomalies.

`M-GEN-01` runs a sliding-window classifier ($64 \times 64$ patch size) trained on synthetic document alterations, producing a continuous probability map $P_{\text{AI-Gen}}(x,y) \in [0, 1]$.

---

## 6. Inference Pipeline and Optimization

### 6.1 TorchServe Integration
AI models run within isolated TorchServe containers managed by Kubernetes.
- Dynamic Batching: Aggregates inference requests up to `max_batch_size=8` within a $10\text{ms}$ latency window.
- TensorRT Acceleration: PyTorch models are compiled to TensorRT engine binaries, achieving $3.2\times$ inference speedup on NVIDIA A100 GPUs.
- FP16 Mixed Precision: All inference operates in FP16 precision, reducing VRAM usage by 50%.

---

## 7. Explainability Mechanisms

Every deep learning model in GDI must expose its decision basis:

- **Integrated Gradients**: Computed for CNN classifiers (`M-FNT-01`, `M-GEN-01`) to map pixel attribution scores.
- **Attention Rollout**: Computed across ViT transformer layers (`M-VFM-01`) to generate visual attention heatmaps.
- **Reconstruction Error Residuals**: Computed for Autoencoder (`M-AE-01`) as $|I_{\text{input}} - I_{\text{reconstructed}}|^2$.

---

## 8. Hardware Sizing and GPU Allocation

- **Primary GPU Target**: NVIDIA A100 (80GB VRAM) or NVIDIA H100 (80GB VRAM).
- **VRAM Allocation**:
  - `M-VFM-01` (DINOv2): 6 GB VRAM
  - `M-LAY-01` (LayoutLMv3): 4 GB VRAM
  - `M-GEN-01` & `M-AE-01`: 8 GB VRAM
  - Concurrent Batch Buffers & TensorRT Workspace: 12 GB VRAM
- **Total VRAM Footprint per GPU Worker**: ~30 GB (permitting 2 model worker replicas per A100 GPU).

---

*Previous: [15_Micro_DNA_Engine](../15_Micro_DNA_Engine/README.md)*
*Next: [17_Similarity_Engine](../17_Similarity_Engine/README.md)*
*Return to: [Master Index](../README.md)*
