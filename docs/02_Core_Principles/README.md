# Document 02 — Core Principles
## GDI: Engineering Philosophy and Design Axioms

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [00_Project_Vision §12], [03_System_Architecture], [26_Security], [19_Decision_Engine]

---

## Table of Contents

1. [Purpose of This Document](#1-purpose-of-this-document)
2. [The Ten Engineering Axioms](#2-the-ten-engineering-axioms)
3. [Forensic Science Principles Applied to Software](#3-forensic-science-principles-applied-to-software)
4. [The Multi-Engine Defense Principle](#4-the-multi-engine-defense-principle)
5. [The Natural Variation Modeling Principle](#5-the-natural-variation-modeling-principle)
6. [Explainability as Engineering Constraint](#6-explainability-as-engineering-constraint)
7. [Evidence Hierarchy](#7-evidence-hierarchy)
8. [Uncertainty Quantification Principle](#8-uncertainty-quantification-principle)
9. [Adversarial Resistance Principle](#9-adversarial-resistance-principle)
10. [Data Minimization and Privacy Principle](#10-data-minimization-and-privacy-principle)
11. [Technology Selection Criteria](#11-technology-selection-criteria)
12. [API Design Principles](#12-api-design-principles)
13. [Operational Principles](#13-operational-principles)
14. [Code and Architecture Standards](#14-code-and-architecture-standards)
15. [Evolution and Backward Compatibility Principles](#15-evolution-and-backward-compatibility-principles)

---

## 1. Purpose of This Document

This document establishes the engineering axioms, design philosophy, and architectural principles that govern every decision made in building the GDI platform. It is a normative document: all architectural, engineering, and product decisions must be consistent with these principles.

When an engineering decision conflicts with one of these principles, the engineer must:
1. Document the conflict explicitly
2. Seek architecture review
3. Either resolve the conflict by finding a compliant approach, or propose a principle amendment with full justification

Principles are not suggestions. They are the invariants of the system's design.

---

## 2. The Ten Engineering Axioms

These axioms were introduced in [00_Project_Vision §12]. Here they are formally specified with engineering implications.

---

### Axiom 1: Reproducibility Over Efficiency

**Statement**: Every forensic computation must produce identical results given identical inputs and pipeline version, regardless of the infrastructure environment in which it runs.

**Engineering Implications**:
- Stochastic algorithms (e.g., random sampling, probabilistic data structures) must use deterministic seeding when used in the forensic pipeline
- Floating-point operations must use consistent precision modes (IEEE 754 double precision, no extended precision)
- OS-level and hardware-level sources of non-determinism (e.g., NUMA topology affecting floating-point result order) must be mitigated through architectural choices (e.g., fixed computation graphs, consistent operation ordering)
- Any exceptions to determinism must be explicitly documented, labeled, and isolated from the primary verdict computation

**Validation**: The testing framework includes a determinism test suite that reruns every genome extraction test 10 times and asserts byte-level identity of deterministic features.

---

### Axiom 2: Explainability as a First-Class Output

**Statement**: No score is emitted without an accompanying decomposition of contributing evidence. Black-box aggregation is architecturally prohibited in the decision layer.

**Engineering Implications**:
- Every model used in the forensic pipeline must provide feature attribution (via native interpretability mechanisms, SHAP, LIME, or gradient-based attribution)
- Models that do not provide interpretable attribution are only permitted in ensemble roles where their output is one of many inputs to an interpretable aggregation function
- The fusion engine and decision engine are fully deterministic and interpretable; they do not use learned black-box models for final score production
- Explainability output format is a first-class schema item defined in [22_API_Design], not an afterthought

---

### Axiom 3: Defense in Depth for Fraud Resistance

**Statement**: No single forensic engine's verdict is sufficient. Ensemble agreement is required for high-confidence verdicts. Divergence between engines is itself forensically significant.

**Engineering Implications**:
- The decision engine uses a Bayesian fusion of engine outputs, not a simple weighted average
- Engine disagreement scores are computed explicitly and fed into the confidence model
- Any configuration that disables more than one forensic engine simultaneously requires administrative authorization
- Engine failure is treated as evidence reduction, not as a pass-through; failed engines contribute to confidence reduction, not to authenticity score

---

### Axiom 4: Natural Variation Is Not Fraud

**Statement**: The system must explicitly model and account for legitimate variation before issuing any anomaly signal.

**Engineering Implications**:
- The natural variation model (populated from verified authentic sample documents) is a required input to every similarity and anomaly computation
- Similarity scores are computed as Z-scores relative to the natural variation distribution, not as raw feature distances
- False positives on authentic documents due to natural variation are tracked as P0 bugs
- The natural variation model is periodically updated as more authentic samples are enrolled

---

### Axiom 5: Immutability of Evidence

**Statement**: All forensic artifacts (source documents, intermediate computations, final reports) are immutable after creation. No forensic record can be modified.

**Engineering Implications**:
- Object storage is configured with write-once (WORM) semantics for all forensic artifacts
- The database schema uses append-only patterns for forensic records; updates are represented as new versioned records
- Every forensic artifact carries a cryptographic hash; any tampering is detectable
- Deletion of forensic records requires multi-party authorization and is itself an audited, documented event

---

### Axiom 6: Security by Design

**Statement**: Security is an architectural constraint, evaluated at design time for every component. It is not a post-hoc addition.

**Engineering Implications**:
- Every new component undergoes threat modeling (STRIDE) before implementation begins
- The threat model is documented and maintained in [26_Security]
- OWASP Top 10 mitigations are verified for all public-facing interfaces
- Dependencies are tracked with automated vulnerability scanning (Trivy, Snyk)
- Security failures are treated as critical defects

---

### Axiom 7: Human Review Is Always Available

**Statement**: For any verdict below a configurable confidence threshold, the system routes to human review rather than issuing an automated determination.

**Engineering Implications**:
- The human review queue is a core platform component, not an optional feature
- No confidence threshold configuration can remove the human review option; it can only widen or narrow the auto-pass and auto-reject bands
- The human review interface has the same access to forensic evidence as the automated decision engine
- Human reviewer verdicts are stored separately from automated verdicts; they do not overwrite or modify automated analysis

---

### Axiom 8: Pipeline Versioning Is Non-Negotiable

**Statement**: Every genome carries the version of the pipeline that produced it. Cross-version comparisons require explicit validation.

**Engineering Implications**:
- Pipeline version is a semantic version (MAJOR.MINOR.PATCH) with documented breaking change semantics
- MAJOR version changes indicate breaking changes to the genome schema (features removed or redefined)
- MINOR version changes indicate additive changes (new features, improved algorithms that don't change existing features)
- PATCH version changes indicate bug fixes that do not affect genome values
- Cross-version comparison is only permitted between compatible versions (documented in a version compatibility matrix)

---

### Axiom 9: Fail Safe, Not Fail Open

**Statement**: On system error, the default behavior is conservative (indeterminate result → human review). The system never fails open to a pass verdict.

**Engineering Implications**:
- Error handling code paths are verified to produce indeterminate results, not pass verdicts
- Infrastructure failures (GPU unavailable, database connection lost) trigger job suspension, not job completion with partial results
- The system has no code path that emits an authenticated verdict in response to a system exception
- Recovery from failure always resumes processing; it never skips to verdict

---

### Axiom 10: Modularity Enables Evolution

**Statement**: Every forensic engine is independently deployable, testable, and upgradeable.

**Engineering Implications**:
- Each forensic engine runs in an independent container/pod
- Engines communicate via well-defined interfaces (protobuf-defined gRPC contracts)
- A new engine can be added without modifying any existing engine or orchestration logic
- Engine interfaces are versioned; old engines and new engines can coexist during transitions

---

## 3. Forensic Science Principles Applied to Software

GDI applies established forensic science principles, as defined by bodies including the SWGDE (Scientific Working Group on Digital Evidence), ENFSI (European Network of Forensic Science Institutes), and NIST's OSAC (Organization of Scientific Area Committees):

### 3.1 Locard's Exchange Principle (Digital Adaptation)
*"Every contact leaves a trace."*
Applied digitally: every document creation, modification, and production step leaves detectable forensic traces in the document's physical and digital characteristics. GDI systematically recovers these traces.

### 3.2 Principle of Individuality
*"No two objects are exactly alike."*
Applied digitally: every document production event — even producing two "identical" copies — leaves subtly different characteristics. GDI measures these individual differences. The presence of characteristics that are too perfectly identical can itself be anomalous.

### 3.3 Principle of Comparison
*"Comparison requires a known standard."*
Applied digitally: GDI always requires a verified original template as the known standard for comparison. Analyses without a comparison standard produce characterization only, not authenticity determination.

### 3.4 Chain of Custody
*"Evidence integrity requires an unbroken chain of custody."*
Applied digitally: every operation on a forensic artifact is logged, timestamped, and cryptographically linked. The chain of custody is a cryptographic chain, not merely a logbook entry.

### 3.5 Scientific Method
*"Forensic conclusions are probabilistic, not absolute."*
Applied digitally: GDI always expresses verdicts as probabilities with confidence intervals. The system never claims absolute certainty; it reports the best probabilistic assessment given the available evidence.

---

## 4. The Multi-Engine Defense Principle

### 4.1 Why Multiple Independent Engines?

A fraudster attempting to defeat a single-engine system needs only to understand and fool that one engine. A multi-engine system requires that the fraudster simultaneously defeat every engine without their manipulations in one dimension leaving artifacts visible to another engine.

This is analogous to multi-factor authentication: defeating one factor is not sufficient.

### 4.2 Engine Independence Requirement

Engines must be **statistically independent** in their measurements. This means:
- They must measure different physical or mathematical properties of the document
- Their measurements must not be derived from the same intermediate computation
- Their results must be processed separately and only fused at the final stage

This independence is verified empirically: for a population of authentic documents and known forgeries, engine outputs should have low inter-engine correlation on authentic documents and divergent patterns on forgeries.

### 4.3 Engine Divergence as Forensic Signal

When engines disagree — e.g., the typography engine reports high similarity but the rendering engine reports low similarity — this divergence is itself forensically significant. Legitimate documents (and even legitimate variations) tend to produce correlated engine scores. Targeted manipulation often affects only a subset of forensic dimensions, producing engine divergence.

Engine divergence scoring is explicitly computed and weighted in the fusion engine (see [18_Fusion_Engine]).

---

## 5. The Natural Variation Modeling Principle

### 5.1 The Problem of Legitimate Variation

Every authentic document produced by a given template will exhibit variation due to:
- **Printer variation**: Different printers (or the same printer at different times) produce subtly different output in terms of ink density, font rendering sharpness, and alignment
- **Scan variation**: Different scanners, scan angles, lighting conditions, and compression settings produce different digital representations of the same physical document
- **Paper aging**: Physical documents change over time (yellowing, ink fading, mechanical distortion)
- **Copy generation**: A photocopy of an authentic document is technically different from the original, though it may be legitimately produced

If these variations are not modeled, they produce false positives (authentic documents flagged as fraudulent).

### 5.2 Statistical Variation Modeling

For each forensic feature F extracted from document type T:
- Let μ_F be the mean value of F across N authenticated authentic samples of type T
- Let σ_F be the standard deviation of F across the same samples
- The natural variation model is the distribution N(μ_F, σ_F²) for each feature F

The similarity score for a submitted document on feature F is expressed as:
```
Z_F = |value_F(submitted) - μ_F| / σ_F
```

A Z-score of 0 indicates perfect match to the expected mean. A Z-score of 3 indicates the submitted value is 3 standard deviations from the authentic mean — a significant but not impossible deviation for legitimate variation.

Threshold calibration for Z-scores is documented in [17_Similarity_Engine].

### 5.3 Minimum Sample Requirements

Natural variation modeling requires a minimum sample size to be statistically valid:
- ≥ 30 samples: Basic statistical validity; moderate confidence in variation model
- ≥ 100 samples: Good statistical validity; high confidence in variation model
- ≥ 1,000 samples: Excellent statistical validity; very high confidence in variation model

The forensic report always discloses the number of samples used for variation modeling. Reports based on fewer than 30 samples include a prominently labeled confidence limitation notice.

---

## 6. Explainability as Engineering Constraint

### 6.1 What "Explainability" Means in GDI

In GDI, explainability is a property of the system's outputs, not of any individual model. The system produces explainable outputs because:

1. Forensic engines produce interpretable measurements with defined semantics (e.g., "the kerning deviation between the letter pair 'AV' is 0.3 points, compared to an expected 0.1 ± 0.05 points from the template")
2. The fusion engine combines engine outputs using a documented, interpretable algorithm (weighted Bayesian fusion)
3. The decision engine produces a verdict with an explicit decomposition of the top contributing features

### 6.2 Attribution Methods

For AI models embedded within individual forensic engines:
- **Gradient-based attribution**: Integrated Gradients (Sundararajan et al., 2017) for CNN-based vision models
- **Perturbation-based attribution**: SHAP (Lundberg and Lee, 2017) for tabular feature models
- **Attention attribution**: Attention rollout (Abnar and Zuidema, 2020) for Transformer-based vision models
- **Engine-native attribution**: Pixel-level anomaly maps for specialized detection models

No engine may use attribution methods that are purely post-hoc approximations with poor fidelity (e.g., vanilla LIME on complex vision models). Attribution fidelity is tested as part of engine validation.

---

## 7. Evidence Hierarchy

GDI uses an evidence hierarchy to weight the contributions of different forensic signals:

| Level | Name | Description | Example |
|-------|------|-------------|---------|
| L1 | Cryptographic Evidence | Mathematically provable, binary | Digital signature verification, hash mismatch |
| L2 | Structural Evidence | High-dimensional, deterministic | PDF object graph anomaly, metadata inconsistency |
| L3 | Statistical Evidence | Probabilistic, high reliability | Font glyph deviation, noise pattern mismatch |
| L4 | AI-Inferred Evidence | Probabilistic, model-dependent | Vision model anomaly score, semantic anomaly |
| L5 | Heuristic Evidence | Low reliability, supporting only | Color histogram deviation, overall layout similarity |

**Decision Rule**: Higher-level evidence takes precedence in verdict computation. L1 evidence (e.g., a verifiable digital signature failure) is determinative regardless of L4/L5 scores. L5 evidence alone cannot drive a high-confidence verdict.

This hierarchy is enforced in the fusion engine (see [18_Fusion_Engine §4]).

---

## 8. Uncertainty Quantification Principle

### 8.1 All Outputs Include Uncertainty

Every numeric output from GDI includes:
- **Point estimate**: The best single-value estimate
- **Confidence interval**: 95% credible interval (Bayesian) or confidence interval (frequentist)
- **Uncertainty source**: What drives the uncertainty (measurement noise, model uncertainty, sample size, engine failure)

### 8.2 Types of Uncertainty

**Aleatoric uncertainty** (irreducible): Inherent variability in the measurement (e.g., natural variation in print quality). Modeled and incorporated into the natural variation model.

**Epistemic uncertainty** (reducible): Uncertainty due to lack of information (e.g., few samples in the natural variation model, a forensic engine failed). Reduced by providing more data. Reported explicitly in the forensic report's limitations section.

**Model uncertainty**: Uncertainty arising from the choice and parameterization of AI models. Quantified through ensemble methods (disagreement between ensemble members).

---

## 9. Adversarial Resistance Principle

### 9.1 Threat Model for GDI

GDI assumes a sophisticated adversary who:
- Knows the general class of forensic techniques in use (but not specific hyperparameters or thresholds)
- Has access to the GDI API as a legitimate customer (black-box access)
- Can iteratively probe the system with many document variants
- Can produce high-quality forgeries using professional equipment and software

GDI does NOT assume the adversary has:
- White-box access to model weights or algorithms
- Access to the natural variation model parameters
- Access to the threshold configuration
- Insider access to the system

### 9.2 Multi-Engine Robustness Guarantee

Under the adversarial threat model, defeating GDI requires simultaneously manipulating documents to pass all active forensic engines without leaving cross-engine artifacts. This is quantifiably harder than defeating a single-engine system.

Formal robustness analysis is performed during [35_Patent_Notes §3] (novel technique identification).

### 9.3 Adversarial Testing

The platform is continuously tested against adversarial document samples:
- **Synthetic adversaries**: Automated perturbation of known authentic documents to probe engine sensitivity
- **Human adversaries**: Red team exercises by professional document forgery specialists
- **Academic collaboration**: Research partnerships with forensic document examination programs

---

## 10. Data Minimization and Privacy Principle

### 10.1 Personal Data in Documents

Forensic documents frequently contain personal data. GDI applies data minimization:
- Document content (including any personal data) is processed in-memory for analysis; it is stored only when required for human review or legal hold
- Storage of document content beyond the job lifecycle requires explicit customer configuration
- Personal data extracted from documents (for metadata analysis) is handled under GDPR Article 9 (special categories) requirements where applicable

### 10.2 Genome Privacy

The genome is a derived representation of a document, not the document itself. However, genomes of identity documents may still constitute personal data under GDPR if they can be used to re-identify an individual. GDI treats document genomes as personal data by default and applies appropriate controls.

---

## 11. Technology Selection Criteria

Every technology choice in GDI must be justified against the following criteria:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Forensic Suitability | High | Does the technology support the forensic precision required? |
| Production Maturity | High | Is the technology used in production by comparable-scale systems? |
| Security Track Record | High | Does the technology have an acceptable CVE history and security maintenance? |
| Explainability Support | High | Does the technology support interpretable outputs? |
| Licensing | Medium | Is the license compatible with commercial use and government deployment? |
| Performance | Medium | Does the technology meet performance requirements? |
| Community and Support | Medium | Is the ecosystem active? Is commercial support available? |
| Vendor Lock-in Risk | Low | How difficult is replacement if needed? |

Technologies are not selected for novelty. Established, well-tested technologies are preferred over cutting-edge alternatives when they meet requirements.

---

## 12. API Design Principles

1. **Backward compatibility**: API changes are additive. Breaking changes require a major version bump and a deprecation period of ≥ 6 months.
2. **Idempotency**: All write operations (document submission, template upload) are idempotent given the same idempotency key.
3. **Error specificity**: Errors always identify: what failed, why it failed, and what the caller should do.
4. **Pagination**: All list endpoints support cursor-based pagination.
5. **Rate limit transparency**: Rate limit headers (remaining, reset time) are always included in responses.
6. **Webhook reliability**: Webhook deliveries include retry logic with exponential backoff; failed deliveries are logged and retried for 72 hours.

---

## 13. Operational Principles

1. **Runbook for every alert**: Every alert has a corresponding runbook with diagnosis and remediation steps.
2. **No manual database operations in production**: All production database changes go through migration scripts executed by the CI/CD pipeline.
3. **Chaos engineering**: Regular chaos experiments (controlled failure injection) validate resilience assumptions.
4. **Incident postmortems**: Every P0/P1 incident produces a blameless postmortem within 48 hours.
5. **Capacity planning**: Capacity forecasts are reviewed monthly against actual usage trends.

---

## 14. Code and Architecture Standards

1. **Service boundaries are contract boundaries**: Services communicate through versioned API contracts, never through shared databases or in-memory state.
2. **Data schemas are versioned**: All database schemas, message schemas, and API schemas are versioned using semantic versioning.
3. **Secrets are never in code**: All secrets are managed through the platform's secret management system; no secret values exist in code, configuration files, or container images.
4. **Idiomatic code by language**: Python code follows PEP 8 + Black formatting; Go code follows `gofmt` + Effective Go; type annotations are mandatory for all Python function signatures.
5. **Logging is structured**: All log output is structured JSON. No format-string logs in production code.

---

## 15. Evolution and Backward Compatibility Principles

### 15.1 Genome Schema Evolution

Adding new genome features: MINOR version bump; existing comparisons continue to work (new feature is absent/null in older genomes and excluded from comparison).

Redefining existing genome features: MAJOR version bump; existing genomes with the old feature definition are not automatically comparable with genomes using the new definition.

Removing genome features: MAJOR version bump; deprecation period of at least 2 pipeline versions.

### 15.2 API Evolution

API evolution follows OpenAPI semantic versioning:
- `/v1/...` for all current production endpoints
- New capabilities added as new endpoints or optional fields
- Deprecated fields/endpoints marked with `deprecated: true` in the OpenAPI spec and maintained for ≥ 6 months

### 15.3 Model Evolution

Model updates are classified:
- **Hotfix**: Bug fix that does not change model outputs; no version bump
- **Improvement**: Better accuracy/performance; MINOR bump; genome comparisons remain valid
- **Redefinition**: Fundamentally different model or feature space; MAJOR bump; re-enrollment may be required

---

*Previous: [01_Product_Requirements](../01_Product_Requirements/README.md)*
*Next: [03_System_Architecture](../03_System_Architecture/README.md)*
*Return to: [Master Index](../README.md)*
