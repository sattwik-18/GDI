# Document 17 — Similarity Engine
## GDI: Multi-Dimensional Similarity and Distance Computation

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [05_Genome_Extraction_Engine], [18_Fusion_Engine], [24_Vector_Database]

---

## Table of Contents

1. [Purpose and Architecture](#1-purpose-and-architecture)
2. [Natural Variation Normalization](#2-natural-variation-normalization)
3. [Distance Metric Taxonomy](#3-distance-metric-taxonomy)
4. [Per-Engine Similarity Computation](#4-per-engine-similarity-computation)
5. [Global Genome Similarity Metrics](#5-global-genome-similarity-metrics)
6. [Threshold Calibration and Z-Score Mapping](#6-threshold-calibration-and-z-score-mapping)
7. [Algorithms and Computational Complexity](#7-algorithms-and-computational-complexity)

---

## 1. Purpose and Architecture

The Similarity Engine compares the extracted Document Genome ($G_{\text{sub}}$) of a submitted document against the reference Document Genome ($G_{\text{tmpl}}$) of an authenticated template, incorporating the Natural Variation Model ($\mathcal{M}_{\text{var}}$).

Rather than computing a naive Euclidean distance, the Similarity Engine evaluates **hundreds of specialized distance metrics** tailored to the mathematical domain of each feature group (continuous, categorical, spatial, spectral, embedding).

---

## 2. Natural Variation Normalization

For every continuous feature $f \in G$, raw distance $|f_{\text{sub}} - f_{\text{tmpl}}|$ is non-informative without considering expected authentic variance. 

### 2.1 Z-Score Transformation
Using the Natural Variation Model parameters $(\mu_f, \sigma_f)$ trained on authentic samples:
$$Z_f = \frac{|f_{\text{sub}} - \mu_f|}{\sigma_f + \epsilon}$$

### 2.2 Gaussian Similarity Mapping
Each Z-score is converted into a bounded similarity score $S_f \in (0, 1]$:
$$S_f = \exp\left( -\frac{Z_f^2}{2 \cdot \tau^2} \right)$$
where $\tau$ is a tolerance scaling factor ($\tau = 1.0$ default).

---

## 3. Distance Metric Taxonomy

Different feature spaces require specific metric formulations:

| Feature Domain | Distance Metric | Mathematical Formulation |
|----------------|-----------------|--------------------------|
| Vector Embeddings (AI) | Cosine Distance | $d_{\text{cos}}(u, v) = 1 - \frac{u \cdot v}{\|u\|_2 \|v\|_2}$ |
| Histograms (LBP, DCT, Color) | Chi-Square / Earth Mover's | $d_{\chi^2}(P, Q) = \frac{1}{2} \sum \frac{(P_i - Q_i)^2}{P_i + Q_i}$ |
| Spatial Bounding Boxes | IoU / Generalized IoU | $d_{\text{GIoU}}(A, B) = 1 - \text{IoU}(A, B) + \frac{|C \setminus (A \cup B)|}{|C|}$ |
| Categorical (Fonts, Software) | Hamming / Jaccard | $d_{\text{Jaccard}}(A, B) = 1 - \frac{|A \cap B|}{|A \cup B|}$ |
| Graph Spectral Features | Riemannian Distance | $d_{\text{Rie}}(\lambda_1, \lambda_2) = \|\log(\lambda_1^{-1/2} \lambda_2 \lambda_1^{-1/2})\|_F$ |

---

## 4. Per-Engine Similarity Computation

For each of the forensic engines $E_k$ ($k=1 \dots K$), the Similarity Engine computes an aggregated engine similarity score $S_{E_k}$:

$$S_{E_k} = \frac{\sum_{f \in E_k} w_f \cdot c_f \cdot S_f}{\sum_{f \in E_k} w_f \cdot c_f}$$

where:
- $w_f$: Static forensic weight of feature $f$ (FS1 = 3.0, FS2 = 2.0, FS3 = 1.0)
- $c_f$: Extracted confidence score of feature $f$ ($c_f \in [0, 1]$)
- $S_f$: Gaussian similarity score of feature $f$

---

## 5. Global Genome Similarity Metrics

In addition to per-engine scores, global similarity metrics capture cross-engine alignment:

1. **Mahalanobis Distance**: Evaluates multivariate feature distance considering inter-feature covariances $\Sigma$:
   $$D_M(G_{\text{sub}}, \mu) = \sqrt{(G_{\text{sub}} - \mu)^T \Sigma^{-1} (G_{\text{sub}} - \mu)}$$
2. **Wasserstein Distance**: Measures structural distribution shift across multidimensional feature clouds.

---

## 6. Threshold Calibration and Z-Score Mapping

Similarity scores are calibrated to risk levels:
- $S_{E_k} \ge 0.95 \implies Z_f < 1.0$: High Similarity (Authentic Range)
- $0.70 \le S_{E_k} < 0.95 \implies 1.0 \le Z_f < 3.0$: Moderate Variation
- $S_{E_k} < 0.70 \implies Z_f \ge 3.0$: Significant Anomaly

---

## 7. Algorithms and Computational Complexity

- **Input**: Submitted Genome ($1,391$ or $3,168$ features), Template Genome, Variation Model.
- **Computation**: Vectorized matrix operations using NumPy/SciPy.
- **Time Complexity**: $O(D)$ where $D$ is feature vector length.
- **Execution Time**: **< 15ms** per document comparison.

---

*Previous: [16_Multi_Model_AI](../16_Multi_Model_AI/README.md)*
*Next: [18_Fusion_Engine](../18_Fusion_Engine/README.md)*
*Return to: [Master Index](../README.md)*
