# Document 50 — Engineering Decision Records
## GDI: Master Architectural Decision Records (v2.0 Extension)

**Version:** 2.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Authors:** Principal Architect, Chief Research Engineer, Technical Documentation Lead
**Cross-References:** [03_System_Architecture §10], All Platform Documents (00 through 49)

---

## Table of Contents

1. [Architectural Governance & ADR Framework](#1-architectural-governance--adr-framework)
2. [ADR-005: Transition from Flat Genome Vectors to 9-Layer Biological Hierarchy](#2-adr-005-transition-from-flat-genome-vectors-to-9-layer-biological-hierarchy)
3. [ADR-006: Introduction of the Document Digital Twin Framework](#3-adr-006-introduction-of-the-document-digital-twin-framework)
4. [ADR-007: Adoption of 11 Decoupled Specialist AI Experts with Zero Inter-Expert Communication](#4-adr-007-adoption-of-11-decoupled-specialist-ai-experts-with-zero-inter-expert-communication)
5. [ADR-008: Mathematical Formalization of Structural Constraints via Solver Engines](#5-adr-008-mathematical-formalization-of-structural-constraints-via-solver-engines)
6. [ADR-009: Decoupled Aleatoric and Epistemic Uncertainty Propagation](#6-adr-009-decoupled-aleatoric-and-epistemic-uncertainty-propagation)
7. [ADR-010: Template Family Lineage Modeling for Legitimate Evolution](#7-adr-010-template-family-lineage-modeling-for-legitimate-evolution)

---

## 1. Architectural Governance & ADR Framework

Architectural Decision Records (ADRs) document key engineering choices, rejected alternatives, trade-offs, and consequences governing the GDI platform. All decisions must align with the 10 Core Engineering Axioms ([02_Core_Principles]).

---

## 2. ADR-005: Transition from Flat Genome Vectors to 9-Layer Biological Hierarchy

- **Context**: Version 1.0 represented the Document Genome as a flat concatenated vector. This obscured local anomalies and limited explainability.
- **Decision**: Replace flat vectors with a 9-layer directed tree genome structure ($\mathcal{T}_{\text{genome}}$).
- **Consequences**: Significantly improved explainability and localized anomaly detection; minor increase in serialization overhead (handled via Protobuf v3 binary format).

---

## 3. ADR-006: Introduction of the Document Digital Twin Framework

- **Context**: Static reference template matching flagged authentic document variation as forgery.
- **Decision**: Build an object-oriented, probabilistic Document Digital Twin ($\mathcal{DT}$) for every template class, continuously enriched using Welford's online statistical algorithm.
- **Consequences**: Reduces false positives on legitimate authentic document variation by $>90\%$.

---

## 4. ADR-007: Adoption of 11 Decoupled Specialist AI Experts with Zero Inter-Expert Communication

- **Context**: Generic AI model pipelines created inter-model latency dependencies and risk of cross-talk bias.
- **Decision**: Deploy 11 isolated, domain-specific AI Expert microservices. Prohibit all direct inter-expert communication. All outputs route exclusively to the Evidence Fusion Engine.
- **Consequences**: Guarantees modular model upgrades and strict explainability boundaries.

---

## 5. ADR-008: Mathematical Formalization of Structural Constraints via Solver Engines

- **Context**: Statistical feature comparison failed to detect subtle structural or layout violations (e.g., misaligned text baselines).
- **Decision**: Implement a Document Constraint Engine (DCE) evaluating hard and soft mathematical equations/inequalities.
- **Consequences**: Enables deterministic detection of structural forgeries.

---

## 6. ADR-009: Decoupled Aleatoric and Epistemic Uncertainty Propagation

- **Context**: Averaging confidence scores created a false sense of certainty on low-quality or corrupted documents.
- **Decision**: Explicitly model physical noise (Aleatoric) and model/sample ignorance (Epistemic) separately, propagating variance tensors up the genome tree.
- **Consequences**: Enables automatic uncertainty-driven overrides to human review queues.

---

## 7. ADR-010: Template Family Lineage Modeling for Legitimate Evolution

- **Context**: Legitimate redesigns of templates were treated as un-related entities.
- **Decision**: Model templates as Directed Acyclic Graphs ($\mathcal{F}_{\text{tmpl}}$) with inheritance rules and mutation delta manifests.
- **Consequences**: Supports seamless cross-generational verification.

---

*Previous: [49_Data_Model_Specification](../49_Data_Model_Specification/README.md)*
*Return to: [Master Index](../README.md)*
