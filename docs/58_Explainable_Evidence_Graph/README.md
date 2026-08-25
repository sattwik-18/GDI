# Document 58 — Explainable Evidence Graph
## GDI: Causal Graph Construction, Counterfactual Reasoning, and Human-Interpretable Forensic Provenance

**Version:** 3.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-22
**Authors:** Principal Architect, Chief Research Engineer, Technical Documentation Lead
**Cross-References:** [42_Evidence_Model], [44_Mathematical_Foundations], [48_Forensic_Ontology], [53_Forensic_Reasoning], [19_Decision_Engine]

---

## Table of Contents

1. [Purpose & Architectural Scope](#1-purpose--architectural-scope)
2. [Explainable Evidence Graph (XEG) Definition](#2-explainable-evidence-graph-xeg-definition)
3. [Causal Attribution Architecture](#3-causal-attribution-architecture)
4. [Counterfactual Reasoning Engine](#4-counterfactual-reasoning-engine)
5. [Human-Interpretable Provenance Chains](#5-human-interpretable-provenance-chains)
6. [Explanation Quality Metrics](#6-explanation-quality-metrics)
7. [XEG Serialization & API Contract](#7-xeg-serialization--api-contract)
8. [Integration with Decision Engine](#8-integration-with-decision-engine)
9. [Fallback Behaviors & Degradation Paths](#9-fallback-behaviors--degradation-paths)

---

## 1. Purpose & Architectural Scope

### 1.1 The Explainability Problem in Forensic AI

A forensic verdict without auditable reasoning is inadmissible in any rigorous legal, regulatory, or scientific context. The GDI platform generates verdicts from the synthesis of hundreds of independent forensic signals. Without explicit causal structure connecting each raw observation to a final verdict, the following failure modes occur:

- **Black-box opacity**: An expert witness cannot explain *why* a document was flagged without referencing a specific chain of evidence.
- **Attribution collapse**: When a verdict is contested, the system cannot isolate which signals drove the decision and which were irrelevant noise.
- **Counterfactual blindness**: The system cannot answer "Would the verdict have changed if Feature X were different?"
- **Selective cherry-picking risk**: Without an explicit graph, an adversarial party can selectively quote individual signals out of their logical context.

The **Explainable Evidence Graph (XEG)** addresses all four failure modes by constructing, for every forensic case, a directed acyclic graph (DAG) that explicitly encodes:

1. **Causal relationships** from raw pixel observations to high-level forensic conclusions.
2. **Evidence provenance** — which extraction module generated which data point.
3. **Counterfactual sensitivities** — how much each node contributes to the final verdict.
4. **Narrative explanations** — natural-language annotations at each graph node, auto-generated to serve both legal and technical audiences.

### 1.2 Architectural Position

The XEG is not a standalone processing pipeline. It is a **post-hoc analytical overlay** constructed after all forensic engines have completed their analysis. It consumes the `EvidenceBundle` (defined in `42_Evidence_Model`) and the hypothesis graph (defined in `53_Forensic_Reasoning`) and synthesizes them into a unified causal graph representation.

```
┌─────────────────────────────────────────────────────────────────┐
│                     XEG Construction Pipeline                   │
│                                                                 │
│  EvidenceBundle ──► EvidenceNode Extractor                     │
│                              │                                  │
│  HypothesisGraph ──► CausalEdge Inferrer                       │
│                              │                                  │
│  UncertaintyModel ──► ConfidenceAnnotator                      │
│                              │                                  │
│  DecisionEngine Output ──► VerdictAnchorNode                   │
│                              │                                  │
│                     XEG DAG Constructor                         │
│                              │                                  │
│              ┌───────────────┼───────────────┐                 │
│              ▼               ▼               ▼                 │
│      Counterfactual    Narrative         Graph                  │
│      Analyzer         Generator          Serializer             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Explainable Evidence Graph (XEG) Definition

### 2.1 Formal Graph Structure

**Definition 58.1** — The Explainable Evidence Graph is defined as a directed acyclic graph:

$$\mathcal{G}_{\text{xeg}} = \langle V, E, \phi, \psi \rangle$$

Where:

- $V = V_{\text{obs}} \cup V_{\text{feat}} \cup V_{\text{hyp}} \cup V_{\text{verdict}}$ is the vertex set
- $E \subseteq V \times V$ is the directed edge set (parent → child = "supports / contributes to")
- $\phi: V \to \mathcal{A}$ is the annotation function mapping each vertex to a structured annotation object
- $\psi: E \to [0,1] \times [-1,1]$ is the edge function mapping each edge to (strength, direction) where direction +1 = corroborating, -1 = contradicting

### 2.2 Vertex Layer Taxonomy

| Layer | Symbol | Description | Example |
|-------|---------|-------------|---------|
| Observation | $V_{\text{obs}}$ | Raw extracted measurements with units | `font_size_px: 11.73 ± 0.02` |
| Feature | $V_{\text{feat}}$ | Derived forensic features from observations | `font_version_inconsistency: TRUE` |
| Hypothesis | $V_{\text{hyp}}$ | Forensic conclusions from feature clusters | `H₁: Digital Fabrication` |
| Verdict | $V_{\text{verdict}}$ | Final case decision node | `VERDICT: FORGED (LR=847.3)` |

### 2.3 Vertex Annotation Schema

Each vertex $v \in V$ carries annotation $\phi(v)$:

```typescript
interface XEGVertexAnnotation {
  vertex_id:         string;           // UUID
  layer:             "OBS" | "FEAT" | "HYP" | "VERDICT";
  label:             string;           // Human-readable signal name
  value:             any;              // The extracted value or computed score
  unit:              string | null;    // Physical unit if applicable
  uncertainty:       UncertaintyPair;  // {aleatoric: σ², epistemic: σ²}
  lr_contribution:   number;           // Log₁₀ likelihood ratio contribution
  source_module:     string;           // Module that generated this vertex
  extraction_ts:     ISO8601String;    // Timestamp of extraction
  narrative_tech:    string;           // Technical explanation (1-2 sentences)
  narrative_legal:   string;           // Legal-grade plain-English explanation
  confidence_level:  "HIGH" | "MEDIUM" | "LOW" | "INSUFFICIENT";
}
```

### 2.4 Edge Semantic Model

**Definition 58.2** — An edge $e = (u, v) \in E$ represents a *support relationship*: vertex $u$ provides evidential support to vertex $v$. The edge carries:

$$\psi(e) = (s_e, d_e)$$

Where $s_e \in [0,1]$ is the **evidential strength** (how much $u$ contributes to $v$'s score), and $d_e \in \{-1, +1\}$ is the **direction** (corroborating vs contradicting the forensic hypothesis chain).

**Computational derivation of** $s_e$:

$$s_e = \frac{\partial \text{LR}(v)}{\partial \text{LR}(u)} \cdot \frac{\text{LR}(u)}{\text{LR}(v)}$$

This is a **logarithmic sensitivity gradient** — the fractional change in $v$'s likelihood ratio per unit fractional change in $u$'s likelihood ratio. It is computed during the forward pass of the fusion engine (Document 18).

---

## 3. Causal Attribution Architecture

### 3.1 Attribution Algorithm

**Algorithm 58.1 — XEG Forward Attribution**

```
Input:  EvidenceBundle B, HypothesisGraph G_hyp, FusionOutput F
Output: XEG G_xeg

1. INITIALIZE G_xeg = empty DAG
2. FOR EACH evidence atom e_i ∈ B:
   a. Create vertex v_obs_i ∈ V_obs with annotation φ(e_i)
   b. ADD v_obs_i to G_xeg
3. FOR EACH derived feature f_j ∈ F.features:
   a. Create vertex v_feat_j ∈ V_feat
   b. FOR EACH contributing evidence e_i:
      - Compute sensitivity s_{ij} = ∂LR(f_j)/∂LR(e_i)
      - IF |s_{ij}| > ε_threshold:
           ADD edge (v_obs_i → v_feat_j, strength=|s_{ij}|, dir=sign(s_{ij}))
4. FOR EACH hypothesis H_k ∈ G_hyp:
   a. Create vertex v_hyp_k ∈ V_hyp
   b. FOR EACH supporting feature f_j:
      - Compute s_{jk} via same gradient method
      - ADD edge (v_feat_j → v_hyp_k, ...)
5. CREATE verdict vertex v_verdict
6. FOR EACH hypothesis H_k:
   - ADD edge (v_hyp_k → v_verdict, strength=weight_k, dir=d_k)
7. VALIDATE G_xeg is acyclic (topological sort check)
8. RETURN G_xeg
```

**Computational complexity**: $\mathcal{O}(|E_{\text{obs}}| \cdot |F| + |F| \cdot |H|)$ — linear in the product of adjacent layer sizes.

### 3.2 Sensitivity Threshold Policy

The threshold $\varepsilon_{\text{threshold}}$ controls the sparsity of the graph:

| Setting | $\varepsilon$ Value | Effect |
|---------|---------------------|--------|
| `FULL_TRACE` | 0.001 | All contributing edges retained (dense graph, maximum traceability) |
| `STANDARD` | 0.05 | Edges contributing ≥5% of parent's LR retained (default) |
| `SUMMARY` | 0.15 | Only dominant evidence chains retained (sparse, for legal summary) |

The setting is configurable per-case and defaults to `STANDARD`.

### 3.3 Topological Ordering & Layered Layout

The XEG is guaranteed acyclic by construction (edges only flow from lower to higher vertex layers). A topological ordering $\sigma(V)$ is computed and used for:

- **Ordered explanation generation**: Explanations are generated layer-by-layer in topological order.
- **Parallel narrative rendering**: Vertices within the same topological rank are independent and can be explained in parallel.
- **Graph layout**: The Sugiyama framework is used for rendering XEGs in visual forensic reports.

---

## 4. Counterfactual Reasoning Engine

### 4.1 Motivation

A forensic expert challenged in court may be asked: *"If the font version discrepancy were absent, would your verdict change?"* The **Counterfactual Reasoning Engine (CRE)** answers such questions systematically and reproducibly.

### 4.2 Counterfactual Query Model

**Definition 58.3** — A *counterfactual query* is a tuple:

$$\mathcal{Q}_{\text{cf}} = \langle v_{\text{target}}, \Delta \rangle$$

Where:
- $v_{\text{target}} \in V_{\text{obs}} \cup V_{\text{feat}}$ is the vertex whose value is hypothetically altered
- $\Delta$ is a perturbation specification: either an absolute replacement value or a signed delta

**Definition 58.4** — The *counterfactual verdict* $V^{\text{cf}}$ is defined as:

$$\text{LR}^{\text{cf}} = \text{LR}_{\text{original}} \cdot \frac{\text{LR}(v_{\text{target}} + \Delta)}{\text{LR}(v_{\text{target}})}$$

This is valid under the **local linearity assumption** — that each evidence node's contribution is approximately linear in a small neighborhood. For large $\Delta$, a full re-evaluation of the affected subgraph is triggered.

### 4.3 Counterfactual Decision Boundary

The **verdict inversion threshold** $\Delta^*$ is the minimum perturbation required to change the verdict class:

$$\Delta^* = \underset{\Delta}{\arg\min} \left\{ |\Delta| : \text{Verdict}(\text{LR}^{\text{cf}}) \neq \text{Verdict}(\text{LR}_{\text{original}}) \right\}$$

A large $\Delta^*$ means the verdict is **robust**. A small $\Delta^*$ indicates a **fragile** verdict dependent on a single narrow observation — which the system flags as a high-risk finding requiring additional corroboration.

### 4.4 Algorithmic Implementation

```
Algorithm 58.2 — Counterfactual Sensitivity Sweep

Input:  XEG G_xeg, verdict node v_verdict, perturbation budget Δ_max
Output: Sensitivity ranking of all observation nodes

1. FOR EACH v_obs_i ∈ V_obs:
   a. Compute path P(v_obs_i, v_verdict) in G_xeg
   b. Compute composite sensitivity:
         S_i = ∏_{e ∈ P} s_e    [product of edge strengths along path]
   c. Compute inversion delta:
         Δ*_i = (log₁₀(θ_verdict) - LR_verdict) / (S_i)
         where θ_verdict is the decision threshold LR
2. RANK observations by ascending |Δ*_i|
3. LABEL top-K observations (K=5 default) as CRITICAL_EVIDENCE
4. LABEL observations with |Δ*_i| > 10 as ROBUST_EVIDENCE
5. RETURN ranked sensitivity list
```

### 4.5 Counterfactual Report Section

Every forensic report (Document 20) includes a **Counterfactual Sensitivity Table**:

| Signal | Current Value | Inversion Threshold | Robustness |
|--------|--------------|---------------------|------------|
| Font kerning delta | 0.73px | Would need to be <0.05px | HIGH |
| JPEG quantization table mismatch | +0.92 | N/A (boolean) | CRITICAL |
| Metadata timestamp skew | 847 days | Would need to be <14 days | MEDIUM |

---

## 5. Human-Interpretable Provenance Chains

### 5.1 Narrative Generation Architecture

Every vertex in the XEG carries two narrative strings:

1. **`narrative_tech`**: A precise, technical statement for forensic engineers and AI model auditors.
2. **`narrative_legal`**: A plain-English statement suitable for court presentation, legal briefs, and non-expert review panels.

These are generated by a **Narrative Generation Module (NGM)** using structured templates parameterized by the vertex's annotation fields.

### 5.2 Template Engine

The NGM uses a deterministic template engine, **not** a generative language model. This ensures:

- **Reproducibility**: The same annotation always produces the same narrative.
- **Auditability**: Templates are version-controlled and human-reviewable.
- **Calibration**: No hallucination risk — narratives are constrained to factual assertions directly derivable from the annotation data.

**Template Example — Observation Layer (Font Version)**:

```
narrative_tech: "Glyph rendering profile extracted from page {page_num} exhibits 
                 {metric_name} of {value} ± {uncertainty}. This metric is 
                 statistically inconsistent with the claimed origin year 
                 {claimed_year} at {confidence_level} confidence (p < {p_value})."

narrative_legal: "The document's text appears to have been produced using software 
                  technology ({software_name}) that was not commercially available 
                  until {earliest_available_year}, which is {delta_years} years 
                  after the document's claimed creation date of {claimed_year}."
```

### 5.3 Chain-of-Custody Provenance

Each XEG vertex also stores a cryptographically-anchored **provenance record**:

```typescript
interface ProvenanceRecord {
  vertex_id:       string;
  extraction_module_id: string;   // Module UUID from service registry
  module_version:  string;        // Semver of the extraction module
  input_hash:      SHA256Hash;    // Hash of raw input data consumed
  output_hash:     SHA256Hash;    // Hash of the output annotation
  timestamp:       ISO8601String;
  operator_id:     string | null; // If human-assisted, operator identity
  signature:       Ed25519Signature; // Module signing key signature
}
```

This ensures that the provenance of every evidence node can be independently verified, and any tampering with the XEG data is cryptographically detectable.

---

## 6. Explanation Quality Metrics

### 6.1 XEG Completeness Score

**Definition 58.5** — The *XEG completeness score* $C_{\text{xeg}}$ measures what fraction of the final LR is traceable to observation nodes:

$$C_{\text{xeg}} = \frac{\sum_{v \in V_{\text{obs}}} s_v \cdot \text{LR}(v)}{\text{LR}(v_{\text{verdict}})}$$

Where $s_v$ is the cumulative path strength from $v$ to the verdict node.

**Requirement**: $C_{\text{xeg}} \geq 0.90$ for any case to be released to a court-admissible report. Cases with $C_{\text{xeg}} < 0.90$ are flagged as `EXPLANATION_INCOMPLETE`.

### 6.2 Explanation Faithfulness

**Definition 58.6** — *Faithfulness* measures whether removing a vertex marked as CRITICAL would change the verdict:

$$\text{Faithful}(v) = \mathbb{1}\left[\text{Verdict}\left(\text{LR}_{\text{original}}\right) \neq \text{Verdict}\left(\text{LR}_{\text{original}} - \text{LR}(v) \cdot s_v\right)\right]$$

A vertex labeled CRITICAL must satisfy `Faithful(v) = 1`. If a CRITICAL-labeled vertex fails this test, a **narrative inconsistency alert** is raised.

### 6.3 Redundancy Index

$$R_{\text{xeg}} = 1 - \frac{|\{e \in E : s_e > \varepsilon\}|}{|V_{\text{obs}}| \cdot |V_{\text{feat}}|}$$

High redundancy ($R \to 1$) indicates that many evidence paths are essentially independent, strengthening the verdict. Low redundancy indicates that multiple features are actually rooted in the same underlying observation — a potential overcount risk that is flagged.

---

## 7. XEG Serialization & API Contract

### 7.1 JSON-LD Serialization

The XEG is serialized in JSON-LD format aligned with the Forensic Ontology (`48_Forensic_Ontology`):

```json
{
  "@context": "https://gdi.platform/ontology/xeg/v3",
  "@type":    "ExplainableEvidenceGraph",
  "case_id":  "uuid",
  "version":  "3.0.0",
  "generated_at": "ISO8601",
  "vertices": [
    {
      "@id":   "xeg:vertex:uuid",
      "@type": "ObservationVertex",
      "label": "Font Kerning Delta",
      "value": 0.73,
      "unit":  "px",
      "lr_contribution": 1.42,
      "uncertainty": {"aleatoric": 0.002, "epistemic": 0.01},
      "narrative_tech":  "...",
      "narrative_legal": "..."
    }
  ],
  "edges": [
    {
      "@id":     "xeg:edge:uuid",
      "@type":   "EvidenceEdge",
      "source":  "xeg:vertex:uuid_a",
      "target":  "xeg:vertex:uuid_b",
      "strength": 0.78,
      "direction": 1
    }
  ],
  "completeness_score": 0.96,
  "counterfactual_summary": { ... }
}
```

### 7.2 REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/cases/{id}/xeg` | Retrieve full XEG for a case |
| `GET` | `/cases/{id}/xeg/summary` | Retrieve top-K evidence chain summary |
| `POST` | `/cases/{id}/xeg/counterfactual` | Submit counterfactual query |
| `GET` | `/cases/{id}/xeg/narrative?audience=legal` | Retrieve narrative-only view |
| `GET` | `/cases/{id}/xeg/graph?format=svg` | Retrieve rendered graph image |

---

## 8. Integration with Decision Engine

### 8.1 Bidirectional Coupling

The XEG maintains a bidirectional relationship with the Decision Engine (Document 19):

1. **Decision Engine → XEG**: The Decision Engine's fusion weights, LR components, and verdict threshold values are consumed as inputs to the XEG construction pipeline.

2. **XEG → Decision Engine**: The XEG's completeness score and critical-evidence set are fed back to the Decision Engine as **explanation coverage constraints**. A verdict may not be finalized as `COURT_ADMISSIBLE` until $C_{\text{xeg}} \geq 0.90$.

### 8.2 Verdict Qualification States

| XEG State | Decision Engine Output |
|-----------|------------------------|
| $C_{\text{xeg}} \geq 0.90$ AND all CRITICAL faithful | `COURT_ADMISSIBLE` |
| $0.75 \leq C_{\text{xeg}} < 0.90$ | `EXPERT_REVIEW_REQUIRED` |
| $C_{\text{xeg}} < 0.75$ | `EXPLANATION_INCOMPLETE — NOT RELEASABLE` |
| Narrative inconsistency detected | `FLAGGED — CRITICAL EVIDENCE MISLABELED` |

---

## 9. Fallback Behaviors & Degradation Paths

| Failure Condition | Fallback Behavior |
|-------------------|-------------------|
| Sensitivity gradient computation fails | Fall back to feature importance from Shapley approximation |
| Gradient produces non-DAG (cycle detected) | Break lowest-weight back-edge; log structural warning |
| Narrative template parameter missing | Insert `[DATA_UNAVAILABLE]` token; flag vertex as `NARRATIVE_INCOMPLETE` |
| Counterfactual query out of perturbation range | Return `DELTA_EXCEEDS_MODEL_VALIDITY`; do not extrapolate |
| Completeness score < 0.75 | Block report generation; raise `CASE_HOLD` event |
| Ed25519 signature verification fails on any ProvenanceRecord | Raise `CHAIN_OF_CUSTODY_BREACH`; escalate to security audit |

---

*Document 58 — End of Specification*
*GDI Platform Version 3.0.0 — INTERNAL ENGINEERING CONFIDENTIAL*
