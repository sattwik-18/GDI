# Document 59 — Trust Computation
## GDI: Multi-Dimensional Trust Scoring, Source Reliability, and Epistemic Credibility Framework

**Version:** 3.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-22
**Authors:** Principal Architect, Chief Research Engineer, Technical Documentation Lead
**Cross-References:** [42_Evidence_Model], [43_Uncertainty_Model], [44_Mathematical_Foundations], [53_Forensic_Reasoning], [58_Explainable_Evidence_Graph]

---

## Table of Contents

1. [Purpose & Architectural Scope](#1-purpose--architectural-scope)
2. [Trust Taxonomy](#2-trust-taxonomy)
3. [Evidence Source Trust Model](#3-evidence-source-trust-model)
4. [Signal-Level Trust Computation](#4-signal-level-trust-computation)
5. [Module Trust Profiling](#5-module-trust-profiling)
6. [Dynamic Trust Updating](#6-dynamic-trust-updating)
7. [Trust-Weighted Fusion](#7-trust-weighted-fusion)
8. [Trust Audit Trail](#8-trust-audit-trail)
9. [Fallback Behaviors & Degradation Paths](#9-fallback-behaviors--degradation-paths)

---

## 1. Purpose & Architectural Scope

### 1.1 Why Trust is a First-Class Forensic Primitive

Every piece of evidence in a forensic case has a *reliability*. This reliability is not the same as the evidence's *discriminative power*. A highly discriminative signal (one that strongly differentiates genuine from forged documents) may be produced by an unreliable extraction module, applied on a document type it was not validated on, or derived from a corrupted input region. In such cases, treating the signal at face value leads to overconfident — and potentially incorrect — verdicts.

The **Trust Computation Framework (TCF)** introduces a formal, multi-dimensional trust score $\tau \in [0,1]$ for every evidence atom, extraction module, data source, and forensic conclusion. Trust scores are propagated through the evidence hierarchy and used to weight the fusion process, preventing unreliable signals from dominating verdicts.

**Trust differs from uncertainty** (Document 43) in the following critical way:
- **Uncertainty** ($\sigma^2$) describes randomness in a *given* measurement — how much the measured value might vary if measurement were repeated.
- **Trust** ($\tau$) describes *confidence in the measurement process itself* — how likely the module is to report the correct value regardless of measurement noise.

Both must be modeled independently and combined in fusion.

### 1.2 Architectural Position

```
┌───────────────────────────────────────────────────────────────┐
│                    Trust Computation Layer                    │
│                                                               │
│  Module Registry ──► ModuleTrustProfiler                     │
│  Evidence Atoms  ──► SignalTrustEvaluator                    │
│  Case History    ──► DynamicTrustUpdater                     │
│                              │                                │
│                    TrustWeightedFusion                        │
│                              │                                │
│              Feeds into: FusionEngine (Doc 18)                │
│              Feeds into: XEG (Doc 58)                         │
│              Feeds into: DecisionEngine (Doc 19)              │
└───────────────────────────────────────────────────────────────┘
```

---

## 2. Trust Taxonomy

### 2.1 Four Orthogonal Trust Dimensions

Trust is not a single scalar. The TCF decomposes trust into four orthogonal dimensions:

| Dimension | Symbol | Description |
|-----------|--------|-------------|
| **Module Reliability** | $\tau_M$ | Historical accuracy of the extraction module |
| **Domain Coverage** | $\tau_D$ | How well the module is validated for this document type |
| **Data Quality** | $\tau_Q$ | Quality of the raw input data consumed by the module |
| **Temporal Stability** | $\tau_T$ | Age-adjusted reliability (older modules degrade over time) |

**Composite Trust Score**:

$$\tau_{\text{composite}} = \tau_M^{w_M} \cdot \tau_D^{w_D} \cdot \tau_Q^{w_Q} \cdot \tau_T^{w_T}$$

Where $w_M + w_D + w_Q + w_T = 1$ are the trust dimension weights (default: $w_M = 0.40$, $w_D = 0.30$, $w_Q = 0.20$, $w_T = 0.10$).

The geometric mean form is used rather than arithmetic because a catastrophic failure in any single dimension (e.g., $\tau_D \to 0$ for an out-of-domain document) should collapse the composite trust to near zero, not merely reduce it linearly.

### 2.2 Trust Level Classification

| $\tau_{\text{composite}}$ Range | Trust Level | Action |
|----------------------------------|-------------|--------|
| $[0.85, 1.00]$ | **HIGH** | Signal used with full weight |
| $[0.65, 0.85)$ | **MEDIUM** | Signal used with reduced weight; flagged in report |
| $[0.40, 0.65)$ | **LOW** | Signal treated as corroborating only; not used as primary evidence |
| $[0.00, 0.40)$ | **UNTRUSTED** | Signal excluded from fusion; logged as `UNRELIABLE_SIGNAL` |

---

## 3. Evidence Source Trust Model

### 3.1 Source Categories

Evidence atoms in GDI are sourced from distinct provenance categories, each with different baseline trust profiles:

| Source Category | Baseline $\tau$ | Rationale |
|----------------|-----------------|-----------|
| Raw pixel extraction (deterministic) | 0.95 | Direct physical measurement, minimal processing |
| Frequency-domain transform (FFT/DCT) | 0.92 | Mathematically exact; only floating-point rounding |
| Statistical model inference | 0.75 | Subject to model distribution shift |
| Neural network classification | 0.70 | Susceptible to adversarial inputs and OOD shift |
| Metadata parsing | 0.85 | Vulnerable to legitimate metadata manipulation by authors |
| External database lookup | 0.80 | Dependent on database currency and completeness |
| Human operator annotation | 0.90 | High reliability but requires operator credentialing |

Baseline trust values are stored in the Module Registry and updated quarterly through systematic validation campaigns.

### 3.2 Contextual Trust Degradation

Baseline trust is degraded by contextual risk factors:

$$\tau_{\text{adjusted}} = \tau_{\text{baseline}} \cdot \prod_{k} (1 - r_k)$$

Where $r_k \in [0,1]$ are risk degradation factors:

| Risk Factor | Symbol | Typical Value |
|-------------|--------|---------------|
| Input image resolution below minimum | $r_{\text{res}}$ | 0.15 if DPI < 150 |
| Document type not in module training set | $r_{\text{ood}}$ | 0.25 |
| Module version mismatch (not latest validated) | $r_{\text{ver}}$ | 0.10 per major version behind |
| Input region partially occluded or corrupted | $r_{\text{qual}}$ | 0.20–0.50 depending on corruption % |
| Adversarial perturbation detected in input | $r_{\text{adv}}$ | 0.45 |

---

## 4. Signal-Level Trust Computation

### 4.1 Signal Trust Scoring Algorithm

```
Algorithm 59.1 — Signal Trust Evaluation

Input:  Evidence atom e = {value, source_module, input_region, document_type}
Output: τ_composite(e)

1. LOOKUP baseline trust τ_M from Module Registry for source_module
2. EVALUATE domain coverage:
   - domain_match_score = lookup(document_type, module.validated_domains)
   - τ_D = sigmoid(5 · domain_match_score - 2.5)  [soft thresholding]
3. EVALUATE data quality:
   - τ_Q = quality_score(input_region)
   - quality_score evaluates: {resolution, SNR, occlusion_fraction, compression_ratio}
4. EVALUATE temporal stability:
   - τ_T = exp(-λ · age_months / 12)
   - λ = 0.15 (decay constant; modules lose ~14% trust per year without re-validation)
5. COMPUTE τ_composite = τ_M^0.40 · τ_D^0.30 · τ_Q^0.20 · τ_T^0.10
6. APPLY contextual degradation factors from Section 3.2
7. CLAMP τ_composite ∈ [0.01, 1.00]
8. RETURN τ_composite
```

### 4.2 Data Quality Sub-Scoring

The data quality score $\tau_Q$ for an input region is computed from four sub-metrics:

$$\tau_Q = \frac{1}{4}\left(\tau_{\text{res}} + \tau_{\text{snr}} + \tau_{\text{occ}} + \tau_{\text{comp}}\right)$$

| Sub-Metric | Computation |
|------------|-------------|
| $\tau_{\text{res}}$ | $\min(1.0, \text{DPI} / 300)$ — normalized resolution score |
| $\tau_{\text{snr}}$ | $\text{sigmoid}(0.5 \cdot \text{SNR}_{\text{dB}} - 5)$ |
| $\tau_{\text{occ}}$ | $1 - f_{\text{occluded}}$ where $f$ is fraction of region occluded |
| $\tau_{\text{comp}}$ | $1 - \max(0, (\text{compression\_ratio} - 20) / 80)$ |

---

## 5. Module Trust Profiling

### 5.1 Module Reliability Tracking

Every extraction module maintains a **Trust Profile** stored in the Module Registry:

```typescript
interface ModuleTrustProfile {
  module_id:           string;
  module_name:         string;
  module_version:      string;
  validated_domains:   DocumentType[];
  baseline_accuracy:   number;         // Measured on validation corpus
  precision:           number;         // Precision on positive class
  recall:              number;         // Recall on positive class
  calibration_error:   number;         // Expected Calibration Error (ECE)
  last_validated_at:   ISO8601String;
  validation_corpus_size: number;
  trust_baseline:      number;         // τ_M derived from above metrics
  trust_history:       TrustDataPoint[];
}
```

### 5.2 Module Reliability Derivation

$\tau_M$ is derived from the module's validation metrics:

$$\tau_M = \text{F}_1 \cdot (1 - \text{ECE}) \cdot \sqrt{\frac{N_{\text{valid}}}{N_{\text{valid}} + N_0}}$$

Where:
- $\text{F}_1 = 2 \cdot \frac{P \cdot R}{P + R}$ is the harmonic mean of precision and recall
- $\text{ECE} \in [0,1]$ is the Expected Calibration Error (0 = perfectly calibrated)
- $N_{\text{valid}}$ is the validation corpus size
- $N_0 = 1000$ is the reference corpus size (penalizes modules with small validation sets)

### 5.3 Cross-Module Consistency as Trust Signal

If two independent modules $M_a$ and $M_b$ measure the same physical property, their agreement can be used to update trust:

$$\text{Agreement}(M_a, M_b) = 1 - \frac{|v_a - v_b|}{\sigma_a + \sigma_b}$$

If $\text{Agreement} < 0.5$ (conflicting results beyond combined uncertainty), both modules' trust scores are penalized by a factor of 0.85 for this case — but neither is discarded, as disagreement itself carries forensic information.

---

## 6. Dynamic Trust Updating

### 6.1 Case-Level Trust Learning

The TCF maintains a **running trust calibration** that updates module trust based on case outcomes. When cases are resolved (ground truth established), the outcome is used to update trust:

**Bayesian Trust Update**:

$$\tau_M^{(t+1)} = \frac{\tau_M^{(t)} \cdot P(E | \text{reliable}) + (1 - \tau_M^{(t)}) \cdot P(E | \text{unreliable})}{P(E)}$$

Where $E$ is the event "module predicted correctly on this case."

This is a **Beta-Binomial Bayesian update** where the prior $\tau_M^{(t)}$ is the current trust estimate and the posterior $\tau_M^{(t+1)}$ incorporates the new outcome.

### 6.2 Trust Drift Detection

Trust scores are monitored for unexpected drift using **CUSUM (Cumulative Sum) control charts**:

$$S_n = \max(0, S_{n-1} + (\text{correct}_n - \tau_M - k))$$

Where $k = 0.5 \cdot \sigma_{\text{trust}}$ is the slack parameter and $\text{correct}_n \in \{0, 1\}$ is whether the module was correct on case $n$.

A drift alert is triggered when $S_n > h = 5 \cdot \sigma_{\text{trust}}$. This triggers a mandatory re-validation of the module before further forensic cases can proceed.

### 6.3 Privacy Constraints on Trust Learning

Trust learning must not leak case-specific information. The TCF enforces:
- Trust updates are aggregated over a minimum batch of 50 cases before being applied.
- Per-case trust contributions are bounded: no single case can shift $\tau_M$ by more than 0.02.
- Updates respect $(\varepsilon=1.0, \delta=10^{-6})$-differential privacy (see Document 56).

---

## 7. Trust-Weighted Fusion

### 7.1 Trust as a Fusion Weight

In the Fusion Engine (Document 18), evidence scores are combined as:

$$\text{LR}_{\text{fused}} = \sum_{i} w_i \cdot \text{LR}(e_i)$$

In trust-weighted fusion, weights $w_i$ are derived from trust scores:

$$w_i = \frac{\tau_i \cdot w_i^{\text{base}}}{\sum_j \tau_j \cdot w_j^{\text{base}}}$$

Where $w_i^{\text{base}}$ is the base discriminative weight of evidence $e_i$ (from the Fusion Engine's trained weight matrix) and $\tau_i$ is the signal's composite trust score.

This means a highly discriminative but low-trust signal gets automatically down-weighted relative to a moderately discriminative but high-trust signal — which is the correct forensic behavior.

### 7.2 Effective Evidence Count

The **effective evidence count** $N_{\text{eff}}$ accounts for trust:

$$N_{\text{eff}} = \frac{\left(\sum_i \tau_i\right)^2}{\sum_i \tau_i^2}$$

This is the standard **effective sample size** formula applied to trust scores. When all modules are fully trusted ($\tau_i = 1$), $N_{\text{eff}} = N$. When one module dominates with trust = 1 and all others have $\tau \to 0$, $N_{\text{eff}} \to 1$.

A minimum $N_{\text{eff}} \geq 3$ is required for a court-admissible verdict, preventing verdicts driven by a single source.

---

## 8. Trust Audit Trail

### 8.1 Trust Chain Record

Every trust computation generates an immutable **Trust Chain Record (TCR)**:

```protobuf
message TrustChainRecord {
  string        case_id         = 1;
  string        evidence_atom_id = 2;
  string        module_id       = 3;
  float         tau_module      = 4;
  float         tau_domain      = 5;
  float         tau_quality     = 6;
  float         tau_temporal    = 7;
  float         tau_composite   = 8;
  string        trust_level     = 9;   // HIGH / MEDIUM / LOW / UNTRUSTED
  repeated RiskFactor risk_factors = 10;
  string        computed_at     = 11;  // ISO8601
  bytes         record_hash     = 12;  // SHA-256 of fields 1-11
}
```

### 8.2 Aggregated Trust Report

Every forensic report includes a **Trust Summary Table** showing, for each major evidence category:

| Evidence Category | Module | $\tau_M$ | $\tau_D$ | $\tau_Q$ | $\tau_T$ | Composite | Level |
|-------------------|--------|----------|----------|----------|----------|-----------|-------|
| Font kerning metrics | FontForensicEngine v2.3 | 0.91 | 0.88 | 0.94 | 0.97 | **0.92** | HIGH |
| JPEG quantization | FrequencyAnalysisEngine v3.1 | 0.89 | 0.95 | 0.76 | 0.99 | **0.86** | HIGH |
| Metadata timestamps | MetadataEngine v1.8 | 0.85 | 0.90 | 0.99 | 0.93 | **0.90** | HIGH |
| Neural classification | AIExpert #7 v2.0 | 0.71 | 0.62 | 0.88 | 0.96 | **0.73** | MEDIUM |

---

## 9. Fallback Behaviors & Degradation Paths

| Failure Condition | Fallback Behavior |
|-------------------|-------------------|
| Module not registered in Trust Registry | Assign $\tau_M = 0.50$ (neutral); flag `UNREGISTERED_MODULE` |
| Validation corpus size < 100 | Apply 50% penalty to $\tau_M$; flag `LOW_VALIDATION_COVERAGE` |
| Input region quality uncomputable | Set $\tau_Q = 0.50$; flag `QUALITY_SCORE_UNAVAILABLE` |
| $N_{\text{eff}} < 3$ | Block verdict issuance; raise `INSUFFICIENT_INDEPENDENT_EVIDENCE` |
| Trust drift alert triggered | Suspend module from new cases; require re-validation |
| Trust Chain Record hash mismatch | Raise `TRUST_CHAIN_INTEGRITY_BREACH`; escalate to security audit |
| All evidence atoms in category UNTRUSTED | Exclude category from fusion; note category absence in report |

---

*Document 59 — End of Specification*
*GDI Platform Version 3.0.0 — INTERNAL ENGINEERING CONFIDENTIAL*
