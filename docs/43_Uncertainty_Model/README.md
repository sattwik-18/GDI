# Document 43 — Uncertainty Model
## GDI: Epistemic and Aleatoric Uncertainty Propagation Framework

**Version:** 2.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Authors:** Principal Architect, Chief Research Engineer, Technical Documentation Lead
**Cross-References:** [02_Core_Principles §8], [18_Fusion_Engine], [19_Decision_Engine], [42_Evidence_Model], [44_Mathematical_Foundations]

---

## Table of Contents

1. [Purpose & Scientific Rationale](#1-purpose--scientific-rationale)
2. [Taxonomy of Uncertainty](#2-taxonomy-of-uncertainty)
    - [2.1 Aleatoric Uncertainty (Physical / Systemic Noise)](#21-aleatoric-uncertainty-physical--systemic-noise)
    - [2.2 Epistemic Uncertainty (Model / Sample Ignorance)](#22-epistemic-uncertainty-model--sample-ignorance)
3. [Quantification & Modeling Mechanisms](#3-quantification--modeling-mechanisms)
4. [Uncertainty Propagation Rules](#4-uncertainty-propagation-rules)
5. [Calibration & Bayesian Credible Intervals](#5-calibration--bayesian-credible-intervals)
6. [Uncertainty-Driven Routing & Decision Overrides](#6-uncertainty-driven-routing--decision-overrides)
7. [Failure Modes, Edge Cases, and Validation](#7-failure-modes-edge-cases-and-validation)

---

## 1. Purpose & Scientific Rationale

In high-stakes forensic document analysis, emitting a point-estimate authenticity score (e.g., $0.82$) without disclosing the **uncertainty bounds** is scientifically invalid and legally indefensible.

Simplistic weighted averaging of scores reduces variance artificially (the "central limit delusion"), giving a false impression of high confidence on low-quality or corrupted documents.

The **GDI Uncertainty Framework** explicitly decouples and quantifies:
- **Aleatoric Uncertainty ($\sigma^2_{\text{alea}}$)**: Physical randomness (scanner noise, low resolution, paper aging).
- **Epistemic Uncertainty ($\sigma^2_{\text{epis}}$)**: Lack of system knowledge (small template sample size $N$, missing engine outputs, unseen font families).

---

## 2. Taxonomy of Uncertainty

### 2.1 Aleatoric Uncertainty (Physical / Systemic Noise)
Inherent, irreducible variability in physical document acquisition:
- Low-DPI rasterization blur.
- High sensor noise ($\text{SNR} < 20\text{ dB}$).
- Compressed JPEG ringing artifacts.

### 2.2 Epistemic Uncertainty (Model / Sample Ignorance)
Reducible uncertainty caused by missing information or model limitations:
- Template Digital Twin trained on few authentic samples ($N < 10$).
- Engine execution failure or network timeout.
- Unseen font family missing from the typographic checksum database.

---

## 3. Quantification & Modeling Mechanisms

```
┌────────────────────────────────────────────────────────────────────────┐
│                        RAW FEATURE MEASUREMENT                         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┴───────────────────────────────┐
    ▼                                                               ▼
┌───────────────────────────────────────┐       ┌───────────────────────────────────────┐
│     ALEATORIC VARIANCE ESTIMATOR      │       │     EPISTEMIC VARIANCE ESTIMATOR      │
│   (Local MAD Noise, Acutance SNR)     │       │  (MC Dropout, Sample Size Penalty)    │
│    $\sigma^2_{\text{alea, } i}$       │       │     $\sigma^2_{\text{epis, } i}$      │
└───────────────────┬───────────────────┘       └───────────────────┬───────────────────┘
                    │                                               │
                    └───────────────────────┬───────────────────────┘
                                            ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     COMBINED COVARIANCE TENSOR $\mathbf{\Sigma}_i$      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│               TREE-BASED VARIANCE PROPAGATION ENGINE                   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│             BAYESIAN 95% CREDIBLE INTERVAL & DECISION OVERRIDE           │
└────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Aleatoric Variance Estimation
Estimated directly from input signal quality:
$$\sigma^2_{\text{alea, } i} = \frac{k_1}{\text{SNR}_i} + k_2 \cdot (1 - \text{Resolution\_Factor}_i)$$

### 3.2 Epistemic Variance Estimation
Estimated using Monte Carlo (MC) Dropout across AI Expert models ($T=50$ stochastic forward passes) and Digital Twin sample penalties:
$$\sigma^2_{\text{epis, } i} = \frac{1}{T} \sum_{t=1}^T \left(\hat{y}_t - \bar{y}\right)^2 + \frac{\gamma}{\sqrt{N_{\text{samples}}}}$$

---

## 4. Uncertainty Propagation Rules

When fusing feature scores $S_1, \dots, S_K$ with weights $w_1, \dots, w_K$:

### 4.1 Fused Variance Calculation
$$\sigma^2_{\text{fused, alea}} = \sum_{k=1}^K w_k^2 \cdot \sigma^2_{\text{alea, } k}$$

$$\sigma^2_{\text{fused, epis}} = \sum_{k=1}^K w_k^2 \cdot \sigma^2_{\text{epis, } k} + 2 \sum_{i < j} w_i w_j \cdot \text{Cov}_{\text{epis}}(i, j)$$

$$\sigma^2_{\text{total}} = \sigma^2_{\text{fused, alea}} + \sigma^2_{\text{fused, epis}}$$

Notice that covariance $\text{Cov}_{\text{epis}}(i, j)$ is explicitly included: if two engines fail or lack training data in similar domains, their epistemic uncertainties reinforce rather than cancel out.

---

## 5. Calibration & Bayesian Credible Intervals

The final authenticity score $A_{\text{fused}}$ is paired with a **95% Bayesian Credible Interval**:

$$[A_{\text{lower}}, A_{\text{upper}}] = \left[ A_{\text{fused}} - 1.96 \cdot \sqrt{\sigma^2_{\text{total}}}, \quad A_{\text{fused}} + 1.96 \cdot \sqrt{\sigma^2_{\text{total}}} \right]$$

Uncertainty Margin: $\Delta U = A_{\text{upper}} - A_{\text{lower}}$.

---

## 6. Uncertainty-Driven Routing & Decision Overrides

The Decision Engine enforces strict **Uncertainty Overrides**:

```
If ΔU > 0.25 (High Total Uncertainty)
  ↳ Override Verdict: INDETERMINATE_HUMAN_REVIEW
  ↳ Flag Reason: UNCERTAINTY_BOUND_EXCEEDED

If σ^2_epis > 2.0 * σ^2_alea (High Epistemic / Lack of Knowledge)
  ↳ Trigger Action: INITIATE_TEMPLATE_ENRICHMENT_REQUEST
```

---

## 7. Failure Modes, Edge Cases, and Validation

- **Zero Variance Edge Case**: When $N$ is very large and noise is 0, $\sigma^2_{\text{total}} \to 0$. *Protection*: Minimum variance floor $\epsilon = 10^{-4}$ enforced.
- **Validation KPI**: Empirically, 95% of ground-truth authentic documents must fall within their computed $[A_{\text{lower}}, A_{\text{upper}}]$ interval bounds.

---

*Previous: [42_Evidence_Model](../42_Evidence_Model/README.md)*
*Next: [44_Mathematical_Foundations](../44_Mathematical_Foundations/README.md)*
*Return to: [Master Index](../README.md)*
