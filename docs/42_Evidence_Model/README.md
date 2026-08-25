# Document 42 — Evidence Model
## GDI: Formal Evidence Representation, Calibration, and Propagation

**Version:** 2.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Authors:** Principal Architect, Chief Research Engineer, Technical Documentation Lead
**Cross-References:** [02_Core_Principles §7], [05_Genome_Extraction_Engine], [18_Fusion_Engine], [43_Uncertainty_Model], [44_Mathematical_Foundations]

---

## Table of Contents

1. [Purpose & Scientific Rationale](#1-purpose--scientific-rationale)
2. [Evidence Object Taxonomy & Schema](#2-evidence-object-taxonomy--schema)
3. [Likelihood Ratio & Bayes Factor Formulation](#3-likelihood-ratio--bayes-factor-formulation)
4. [Evidence Hierarchy Calibration](#4-evidence-hierarchy-calibration)
5. [Reliability and Measurement Quality Fitting](#5-reliability-and-measurement-quality-fitting)
6. [Evidence Propagation Pipeline](#6-evidence-propagation-pipeline)
7. [Explainability Audit Map Generation](#7-explainability-audit-map-generation)

---

## 1. Purpose & Scientific Rationale

In forensic science (ENFSI, SWGDE, NIST OSAC standards), raw data metrics cannot be presented directly as legal proof of forgery. Data metrics must be transformed into formal **Forensic Evidence Objects** governed by **Likelihood Ratios ($\text{LR}$)** and **Bayes Factors**.

Version 2.0 establishes a unified **Evidence Model** across all 10 forensic chromosomes. Every engine output is encapsulated in a standardized, immutable `EvidenceObject` carrying:
- The measured hypothesis likelihood under authentic ($\mathcal{H}_a$) vs. fraudulent ($\mathcal{H}_f$) hypotheses.
- Calibrated Bayes factors.
- Spatial localization bounds.
- Measurement reliability metrics.

---

## 2. Evidence Object Taxonomy & Schema

```protobuf
syntax = "proto3";
package gdi.v2.evidence;

message EvidenceObject {
  string evidence_id = 1;
  string engine_id = 2;
  string chromosome_id = 3;
  string trait_id = 4;
  
  // Likelihood Ratio Framework
  double likelihood_authentic = 5;   // P(E | H_a)
  double likelihood_fraudulent = 6;  // P(E | H_f)
  double log_likelihood_ratio = 7;   // LLR = ln( P(E|H_a) / P(E|H_f) )
  
  // Hierarchy & Calibration
  EvidenceLevel level = 8;
  double level_weight = 9;           // Multiplier (L1=3.0, L2=2.0, etc.)
  double calibrated_bayes_factor = 10;
  
  // Spatial Localization
  BoundingBox bounding_box = 11;
  double anomaly_intensity = 12;      // [0.0, 1.0]
  
  // Quality & Reliability
  double reliability_score = 13;
  google.protobuf.Timestamp generated_at = 14;
}

enum EvidenceLevel {
  LEVEL_1_CRYPTOGRAPHIC = 0;
  LEVEL_2_STRUCTURAL = 1;
  LEVEL_3_STATISTICAL = 2;
  LEVEL_4_AI_INFERRED = 3;
  LEVEL_5_HEURISTIC = 4;
}

message BoundingBox {
  double x_min = 1;
  double y_min = 2;
  double x_max = 3;
  double y_max = 4;
  int32 page_number = 5;
}
```

---

## 3. Likelihood Ratio & Bayes Factor Formulation

The forensic core evaluates two mutually exclusive hypotheses:
- $\mathcal{H}_a$: The candidate document is a genuine authentic instance of the template class.
- $\mathcal{H}_f$: The candidate document is forged, altered, or fraudulent.

For an observed trait measurement $e_i$:

$$\text{LR}(e_i) = \frac{P(e_i \mid \mathcal{H}_a)}{P(e_i \mid \mathcal{H}_f)}$$

The **Log-Likelihood Ratio ($\text{LLR}$)** is:

$$\text{LLR}(e_i) = \ln\left( \text{LR}(e_i) \right)$$

- $\text{LLR}(e_i) > 0$: Evidence supports Authenticity ($\mathcal{H}_a$).
- $\text{LLR}(e_i) < 0$: Evidence supports Forgery ($\mathcal{H}_f$).
- $\text{LLR}(e_i) = 0$: Inconclusive neutral evidence.

---

## 4. Evidence Hierarchy Calibration

Per **Document 02**, evidence levels modulate the raw log-likelihood ratios using calibrated multipliers:

$$\text{LLR}_{\text{calibrated}}(e_i) = w_{\text{level}} \cdot \text{LLR}(e_i) \cdot R(e_i)$$

where $w_{\text{level}}$ is defined as:
- $w_{\text{L1}} = 3.0$ (Cryptographic)
- $w_{\text{L2}} = 2.0$ (Structural & Constraints)
- $w_{\text{L3}} = 1.5$ (Statistical & Physical)
- $w_{\text{L4}} = 1.0$ (AI-Inferred)
- $w_{\text{L5}} = 0.5$ (Heuristics)

and $R(e_i) \in [0, 1]$ is the **Reliability Metric**.

---

## 5. Reliability and Measurement Quality Fitting

Reliability $R(e_i)$ reflects data quality and engine performance:

$$R(e_i) = \text{SignalNoiseRatio}_{\text{norm}} \times (1 - \text{DegradationFactor}) \times \beta_{\text{engine}}$$

where $\beta_{\text{engine}}$ is the engine's historical precision on the ground-truth benchmark corpus.

---

## 6. Evidence Propagation Pipeline

```
[Raw Engine Traits] ──▶ [LLR Evaluator] ──▶ [Reliability Fitter] ──▶ [Hierarchy Multiplier]
                                                                             │
[Master Forensic Report] ◄── [Explainability Map] ◄── [Bayesian Aggregator] ◄┘
```

---

## 7. Explainability Audit Map Generation

All `EvidenceObject` records with $\text{LLR} < -2.0$ (strong evidence for forgery) are collected and rendered into the **Explainability Audit Map**:
1. Spatial bounding boxes are overlaid on document previews.
2. The exact $\text{LLR}$ value and contributing physical features are documented in legal report callouts.

---

*Previous: [41_Constraint_Engine](../41_Constraint_Engine/README.md)*
*Next: [43_Uncertainty_Model](../43_Uncertainty_Model/README.md)*
*Return to: [Master Index](../README.md)*
