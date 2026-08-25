# Document 18 — Fusion Engine
## GDI: Evidence Aggregation and Score Fusion

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [02_Core_Principles §7], [05_Genome_Extraction_Engine], [17_Similarity_Engine], [19_Decision_Engine]

---

## Table of Contents

1. [Purpose and Architecture](#1-purpose-and-architecture)
2. [Evidence Hierarchy Weighting](#2-evidence-hierarchy-weighting)
3. [Bayesian Reliability Model](#3-bayesian-reliability-model)
4. [Engine Divergence Scoring](#4-engine-divergence-scoring)
5. [Score Fusion Algorithm](#5-score-fusion-algorithm)
6. [Spatial Anomaly Heatmap Compositing](#6-spatial-anomaly-heatmap-compositing)
7. [Mathematical Specifications](#7-mathematical-specifications)

---

## 1. Purpose and Architecture

The Fusion Engine aggregates heterogeneous, multi-dimensional outputs from all active forensic engines into a single, cohesive **Evidence Record**. 

Adhering to **Axiom 2** (Explainability) and **Axiom 3** (Multi-Engine Defense), the Fusion Engine prohibits black-box machine learning for final score aggregation. Instead, it utilizes a **transparent, mathematically rigorous Bayesian evidence fusion framework** that incorporates evidence hierarchy weights, engine reliability priors, and inter-engine divergence signals.

---

## 2. Evidence Hierarchy Weighting

Not all forensic signals carry equal evidential weight. The Fusion Engine enforces a strict 5-tier evidence hierarchy (first defined in [02_Core_Principles §7]):

| Level | Evidence Category | Multiplier ($M_L$) | Forensic Engines Included |
|-------|-------------------|-------------------|---------------------------|
| **L1** | Cryptographic | 3.0× | Metadata (Digital Signatures, Hash Mismatches) |
| **L2** | Structural | 2.0× | Layout, Object Relationship Graph, PDF Vector |
| **L3** | Statistical | 1.5× | Typography, Noise, Frequency, Micro-DNA |
| **L4** | AI-Inferred | 1.0× | Multi-Model AI (DINOv2, LayoutLMv3, Diffusion) |
| **L5** | Heuristic | 0.5× | Basic Color Histograms, Coarse Aspect Ratios |

---

## 3. Bayesian Reliability Model

Each engine $E_k$ is assigned an effective dynamic weight $\alpha_k$:

$$\alpha_k = M_{L(k)} \times \beta_k \times C_k \times (1 - \text{Fail}_k)$$

where:
- $M_{L(k)}$: Hierarchy multiplier for engine $E_k$
- $\beta_k$: Historical engine reliability prior (evaluated continuously on ground-truth benchmarks)
- $C_k$: Measurement confidence score emitted by engine $E_k$ ($C_k \in [0, 1]$)
- $\text{Fail}_k$: Binary flag ($1$ if engine failed/timed out, $0$ otherwise)

---

## 4. Engine Divergence Scoring

When forensic engines disagree (e.g., Typography reports 98% similarity, but Noise reports 25% similarity), this divergence is a strong indicator of targeted manipulation.

### 4.1 Divergence Formulation
Let $S_k$ be the similarity score of engine $E_k$. The weighted mean score is:
$$\bar{S} = \frac{\sum \alpha_k S_k}{\sum \alpha_k}$$

The **Engine Divergence Index ($D_{\text{engine}}$)** is defined as:
$$D_{\text{engine}} = \frac{\sum_{k=1}^K \alpha_k (S_k - \bar{S})^2}{\sum_{k=1}^K \alpha_k}$$

High divergence ($D_{\text{engine}} > 0.08$) penalizes the final authenticity score and lowers overall decision confidence.

---

## 5. Score Fusion Algorithm

The Fusion Engine computes three primary fused metrics:

### 5.1 Fused Authenticity Score ($A_{\text{fused}}$)
$$A_{\text{fused}} = \sigma \left( \sum_{k=1}^K \alpha_k \cdot \text{logit}(S_k) \right) \times (1 - \gamma \cdot D_{\text{engine}})$$
where $\sigma(z) = \frac{1}{1 + e^{-z}}$ is the logistic sigmoid, $\text{logit}(p) = \log\frac{p}{1-p}$, and $\gamma=1.5$ is the divergence penalty factor.

### 5.2 Fused Anomaly Score ($R_{\text{fused}}$)
$$R_{\text{fused}} = \max_{k} \left( \alpha_k \cdot \text{Anomaly}_k \right) \times \left(1 + \frac{1}{K}\sum \text{Anomaly}_k \right)$$

### 5.3 Fused Confidence Score ($C_{\text{fused}}$)
$$C_{\text{fused}} = \left( \frac{\sum \alpha_k}{\sum M_{L(k)} \beta_k} \right) \times \exp\left( - \lambda \cdot D_{\text{engine}} \right)$$

---

## 6. Spatial Anomaly Heatmap Compositing

The Fusion Engine combines individual engine 2D anomaly maps into a unified master heatmap:

$$M_{\text{master}}(x, y) = \max_{k} \left( \alpha_k \cdot M_k(x, y) \right)$$

The resulting composite heatmap is rendered using a standardized cool-to-warm colormap (Blue=0.0, Yellow=0.5, Red=1.0) and exported as an immutable 16-bit PNG artifact.

---

## 7. Mathematical Specifications

- **Input**: Per-engine similarity scores $S_k$, confidences $C_k$, anomaly maps $M_k$.
- **Output**: Fused Authenticity ($A_{\text{fused}}$), Fused Anomaly ($R_{\text{fused}}$), Fused Confidence ($C_{\text{fused}}$), Master Heatmap ($M_{\text{master}}$).
- **Execution Time**: **< 20ms** (excluding image compositing); **< 150ms** (including master heatmap PNG render).

---

*Previous: [17_Similarity_Engine](../17_Similarity_Engine/README.md)*
*Next: [19_Decision_Engine](../19_Decision_Engine/README.md)*
*Return to: [Master Index](../README.md)*
