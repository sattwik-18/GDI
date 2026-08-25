# Document 41 — Constraint Engine
## GDI: Structural, Geometric, and Typographic Constraint Modeling

**Version:** 2.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Authors:** Principal Architect, Chief Research Engineer, Technical Documentation Lead
**Cross-References:** [07_Layout_Analysis], [08_Typography_Analysis], [14_Object_Relationship_Graph], [18_Fusion_Engine], [44_Mathematical_Foundations]

---

## Table of Contents

1. [Purpose & Architectural Rationale](#1-purpose--architectural-rationale)
2. [Constraint Modeling Framework](#2-constraint-modeling-framework)
3. [Taxonomy of Document Constraints](#3-taxonomy-of-document-constraints)
    - [3.1 Geometric & Spatial Alignment Constraints](#31-geometric--spatial-alignment-constraints)
    - [3.2 Typographic & Font Consistency Constraints](#32-typographic--font-consistency-constraints)
    - [3.3 Relational & Containment Constraints](#33-relational--containment-constraints)
    - [3.4 Semantic & Format Constraints](#34-semantic--format-constraints)
4. [Mathematical Formulation of Constraints](#4-mathematical-formulation-of-constraints)
5. [Constraint Violation Penalty Functions](#5-constraint-violation-penalty-functions)
6. [Constraint Satisfaction Solver Engine](#6-constraint-satisfaction-solver-engine)
7. [Integration with Evidence Fusion Engine](#7-integration-with-evidence-fusion-engine)
8. [Performance, Complexity, and Failure Modes](#8-performance-complexity-and-failure-modes)

---

## 1. Purpose & Architectural Rationale

In GDI Version 1.0, document comparison was largely statistical (evaluating mean feature values and variances). However, real-world documents are bound by strict **Structural and Mathematical Constraints**.

For example:
- All column text blocks in a 3-column newsletter must have their left edges aligned to exact X-coordinates $\pm \delta$.
- A table row's height must equal the maximum height of its constituent cell contents plus fixed padding.
- The baseline of every character in a text line must lie on a single continuous affine line $y = m x + c$.
- A form label and its input box must satisfy an un-intersecting bounding box relationship where $\text{bbox}_{\text{label}} \cap \text{bbox}_{\text{value}} = \emptyset$.

The **Document Constraint Engine (DCE)** formalizes these physical, visual, and logical rules into a system of mathematical equations and inequalities $\mathcal{C} = \{c_1, c_2, \dots, c_K\}$.

Rather than asking *"How close is feature $X$ to average?"*, the Constraint Engine asks: ***"Does this candidate document violate any hard or soft mathematical invariants established by the document template?"***

---

## 2. Constraint Modeling Framework

A **Constraint** $c_k \in \mathcal{C}$ is defined as a tuple:

$$c_k = \langle \mathcal{V}_k, f_k, \text{type}_k, w_k, \text{tol}_k \rangle$$

where:
- $\mathcal{V}_k \subset V$: Subset of document objects involved in the constraint.
- $f_k(\mathcal{V}_k)$: Constraint evaluation function ($f_k \to \mathbb{R}$).
- $\text{type}_k \in \{\text{HARD}, \text{SOFT}\}$: Constraint classification.
- $w_k$: Forensic weight multiplier.
- $\text{tol}_k$: Permissible tolerance band.

---

## 3. Taxonomy of Document Constraints

### 3.1 Geometric & Spatial Alignment Constraints
- **Collinearity Constraint ($c_{\text{align}}$)**: Left, right, top, or bottom edges of objects $\{v_1, \dots, v_m\}$ must lie on a single line $x = k$ or $y = k$.
- **Equal Spacing Constraint ($c_{\text{space}}$)**: Inter-element gaps $\Delta x_i = x_{i+1} - x_i$ must be equal across all items in a list or column.
- **Symmetry Constraint ($c_{\text{symm}}$)**: Margins or header/footer elements must exhibit bilateral symmetry across the document vertical center line $x = W/2$.

### 3.2 Typographic & Font Consistency Constraints
- **Baseline Invariant Constraint ($c_{\text{base}}$)**: Characters $g_1, \dots, g_n$ in a line must share a single baseline equation $y = m x + c$ with residual variance $\sigma^2_{\text{res}} \le \epsilon$.
- **Font Scale Proportionality ($c_{\text{scale}}$)**: Font height and advance width must satisfy the font's metric scale ratio $W / H = k_{\text{font}}$.

### 3.3 Relational & Containment Constraints
- **Disjoint Bounding Box Constraint ($c_{\text{disjoint}}$)**: Non-overlapping text blocks must satisfy $\text{Area}(v_i \cap v_j) = 0$.
- **Parent Containment Constraint ($c_{\text{contain}}$)**: Child elements (table cell text) must be strictly contained within parent boundaries ($\text{bbox}_{\text{child}} \subset \text{bbox}_{\text{parent}}$).

### 3.4 Semantic & Format Constraints
- **Regex Format Invariant ($c_{\text{regex}}$)**: Text string values for structured fields (e.g., SSN, Date, Account Number) must satisfy domain-specific regular expressions.
- **Date Ordering Invariant ($c_{\text{date}}$)**: $\text{Date}_{\text{issue}} \le \text{Date}_{\text{expiration}}$.

---

## 4. Mathematical Formulation of Constraints

### 4.1 Collinearity (Left-Edge Alignment)
For $m$ objects with left coordinates $x_1, x_2, \dots, x_m$:

$$f_{\text{collinear}}(x_1, \dots, x_m) = \sum_{i=1}^m (x_i - \bar{x})^2$$

Constraint satisfied if $f_{\text{collinear}} \le \text{tol}_{\text{align}}$.

### 4.2 Baseline Affine Invariant
For character baseline points $(x_i, y_i)_{i=1}^n$:

$$f_{\text{baseline}} = \min_{m, c} \sum_{i=1}^n (y_i - (m x_i + c))^2$$

Constraint satisfied if $f_{\text{baseline}} / n \le \text{tol}_{\text{base}}$.

---

## 5. Constraint Violation Penalty Functions

When a candidate document evaluates constraint $c_k$, the **Violation Severity Index ($V_k$)** is computed via a smooth penalty function:

$$V_k = \begin{cases} 
0 & \text{if } f_k(\mathcal{V}_k) \le \text{tol}_k \\
1 - \exp\left( -\frac{(f_k(\mathcal{V}_k) - \text{tol}_k)^2}{2 \sigma_k^2} \right) & \text{if } f_k(\mathcal{V}_k) > \text{tol}_k 
\end{cases}$$

- $V_k = 0$: Constraint fully satisfied.
- $V_k \to 1$: Severe constraint violation (indicates structural forgery).

---

## 6. Constraint Satisfaction Solver Engine

The DCE evaluates document structural integrity using a **Constraint Satisfaction Solver**:

1. Extract all objects $V$ from candidate document.
2. Load active constraint set $\mathcal{C}_{\text{template}}$ from template Digital Twin.
3. Evaluate $V_k$ for each constraint $c_k \in \mathcal{C}_{\text{template}}$.
4. Calculate Global Constraint Violation Score ($S_{\text{constraint}}$):
   $$S_{\text{constraint}} = \frac{\sum_{k=1}^K w_k \cdot V_k}{\sum_{k=1}^K w_k}$$

---

## 7. Integration with Evidence Fusion Engine

The Global Constraint Violation Score $S_{\text{constraint}}$ feeds directly into the Fusion Engine as an **L2 Structural Evidence Signal**:
- If any HARD constraint is violated ($V_k > 0.9$ for a HARD constraint):
  - Fusion Engine triggers an automatic L2 structural anomaly override.
  - Overall document authenticity score is capped at $A_{\text{fused}} \le 0.20$.

---

## 8. Performance, Complexity, and Failure Modes

- **Complexity**: $O(K \cdot M)$ where $K$ is number of constraints and $M$ is max objects per constraint.
- **Evaluation Time**: **< 10ms** for 500 constraints on single page.
- **Failure Mode**: Complex warped scan distorts geometric alignment constraints. *Mitigation*: DCE uses deskewed/unwarped modalities from Document Reconstruction Engine (`reconstruct-svc`).

---

*Previous: [40_Reverse_Engineering](../40_Reverse_Engineering/README.md)*
*Next: [42_Evidence_Model](../42_Evidence_Model/README.md)*
*Return to: [Master Index](../README.md)*
