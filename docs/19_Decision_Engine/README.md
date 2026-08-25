# Document 19 — Decision Engine
## GDI: Verdict Computation, Thresholds, and Uncertainty

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [01_Product_Requirements §7], [02_Core_Principles §7-8], [18_Fusion_Engine], [20_Forensic_Report_Generator]

---

## Table of Contents

1. [Purpose and Operating Philosophy](#1-purpose-and-operating-philosophy)
2. [Verdict Category Topology](#2-verdict-category-topology)
3. [Decision Matrix and Calibration](#3-decision-matrix-and-calibration)
4. [Platt Scaling Calibration](#4-platt-scaling-calibration)
5. [Uncertainty Quantification](#5-uncertainty-quantification)
6. [Human Review Routing Rules](#6-human-review-routing-rules)
7. [Tenant-Specific Policy Engine](#7-tenant-specific-policy-engine)

---

## 1. Purpose and Operating Philosophy

The Decision Engine is the final analytical arbiter in the GDI platform. It ingests the fused authenticity, anomaly, and confidence scores from the Fusion Engine and evaluates them against tenant policy thresholds to issue a definitive **Verdict Record**.

Adhering to **Axiom 9** (Fail Safe, Not Fail Open), the Decision Engine defaults to routing ambiguous or low-confidence cases to human expert review rather than issuing automated pass/fail determinations.

---

## 2. Verdict Category Topology

The system assigns every processed document to one of five discrete verdict states:

```
                      ┌───────────────────────────┐
                      │   Fused Score Ingestion   │
                      └─────────────┬─────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           ▼                        ▼                        ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│  AUTHENTIC_HIGH_CONF│  │    HUMAN_REVIEW     │  │  FRAUDULENT_HIGH_C  │
│  (Score >= 0.85,    │  │ (Borderline Score / │  │  (Score <= 0.20,    │
│   Conf >= 0.80)     │  │  Low Confidence)    │  │   Conf >= 0.80)     │
└─────────────────────┘  └──────────┬──────────┘  └─────────────────────┘
                                    │
                         ┌──────────┴──────────┐
                         ▼                     ▼
              ┌────────────────────┐ ┌────────────────────┐
              │  LIKELY_AUTHENTIC  │ │ LIKELY_FRAUDULENT  │
              │  (Score >= 0.70)   │ │  (Score <= 0.35)   │
              └────────────────────┘ └────────────────────┘
```

1. **`AUTHENTIC_HIGH_CONFIDENCE`**: Automated pass. Document exhibits negligible anomaly across all forensic dimensions.
2. **`LIKELY_AUTHENTIC`**: Low-risk pass. Minor natural variation detected; no evidence of malicious tampering.
3. **`INDETERMINATE_HUMAN_REVIEW`**: Ambiguous verdict. Dispatched immediately to human forensic queue.
4. **`LIKELY_FRAUDULENT`**: High-risk flag. Significant anomaly detected in one or more critical engines.
5. **`FRAUDULENT_HIGH_CONFIDENCE`**: Automated fail / rejection. Irrefutable forensic evidence of manipulation or structural forgery.

---

## 3. Decision Matrix and Calibration

Default system decision boundaries (configurable per tenant):

$$\text{Verdict} = 
\begin{cases} 
\text{FRAUDULENT\_HIGH\_CONFIDENCE} & \text{if } A_{\text{cal}} \le 0.15 \text{ AND } C_{\text{fused}} \ge 0.75 \\
\text{AUTHENTIC\_HIGH\_CONFIDENCE} & \text{if } A_{\text{cal}} \ge 0.85 \text{ AND } C_{\text{fused}} \ge 0.75 \\
\text{INDETERMINATE\_HUMAN\_REVIEW} & \text{if } C_{\text{fused}} < 0.60 \text{ OR } D_{\text{engine}} > 0.10 \\
\text{LIKELY\_FRAUDULENT} & \text{if } 0.15 < A_{\text{cal}} \le 0.40 \\
\text{LIKELY\_AUTHENTIC} & \text{if } 0.70 \le A_{\text{cal}} < 0.85 \\
\text{INDETERMINATE\_HUMAN\_REVIEW} & \text{otherwise } (0.40 < A_{\text{cal}} < 0.70)
\end{cases}$$

---

## 4. Platt Scaling Calibration

Raw fusion scores $A_{\text{fused}}$ are transformed into true empirical probabilities $A_{\text{cal}} = P(\text{Authentic} \mid A_{\text{fused}})$ using logistic Platt scaling:

$$A_{\text{cal}} = \frac{1}{1 + \exp(A \cdot A_{\text{fused}} + B)}$$

Parameters $A$ and $B$ are fitted using Maximum Likelihood Estimation on GDI's ground-truth validation corpus ($>100,000$ documents).

---

## 5. Uncertainty Quantification

Every verdict includes a 95% Credible Interval $[A_{\text{lower}}, A_{\text{upper}}]$ derived via non-parametric bootstrap resampling ($B=1,000$ iterations) over engine feature distributions:

$$\text{Uncertainty Margin } \Delta U = A_{\text{upper}} - A_{\text{lower}}$$

If $\Delta U > 0.25$, the Decision Engine automatically escalates the job to `INDETERMINATE_HUMAN_REVIEW` due to epistemic uncertainty.

---

## 6. Human Review Routing Rules

A document is routed to human review if ANY of the following conditions trigger:

- **Rule HR-01**: $C_{\text{fused}} < \text{Tenant\_Conf\_Threshold}$ (Default $0.65$)
- **Rule HR-02**: Score falls in Borderline Band ($0.40 < A_{\text{cal}} < 0.70$)
- **Rule HR-03**: Critical L1 Engine Failure (Digital signature missing/corrupted when expected)
- **Rule HR-04**: High Engine Divergence ($D_{\text{engine}} > 0.10$)
- **Rule HR-05**: Micro-DNA / High-Resolution Engine failure during Deep Tier analysis

---

## 7. Tenant-Specific Policy Engine

Tenants can override default decision boundaries via JSON configuration:

```json
{
  "tenant_id": "t-bank-compliance-01",
  "policy_version": "1.2",
  "auto_pass_threshold": 0.88,
  "auto_reject_threshold": 0.12,
  "min_confidence_for_auto_verdict": 0.80,
  "force_human_review_on_l1_failure": true,
  "max_allowed_divergence": 0.06
}
```

---

*Previous: [18_Fusion_Engine](../18_Fusion_Engine/README.md)*
*Next: [20_Forensic_Report_Generator](../20_Forensic_Report_Generator/README.md)*
*Return to: [Master Index](../README.md)*
