# Document 54 — Lifecycle Reconstruction
## GDI: Probabilistic Directed Graph Creation History Engine

**Version:** 3.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Authors:** Principal Architect, Chief Research Engineer, Technical Documentation Lead
**Cross-References:** [06_Document_Reconstruction_Engine], [40_Reverse_Engineering], [53_Forensic_Reasoning]

---

## Table of Contents

1. [Purpose & Architectural Evolution](#1-purpose--architectural-evolution)
2. [Probabilistic Directed Lifecycle Graph ($\mathcal{G}_{\text{life}}$)](#2-probabilistic-directed-lifecycle-graph-g_textlife)
3. [Lifecycle Node & Edge Taxonomy](#3-lifecycle-node--edge-taxonomy)
4. [Evidence-to-Lifecycle Mapping Rules](#4-evidence-to-lifecycle-mapping-rules)
5. [Graph Construction Algorithm](#5-graph-construction-algorithm)
6. [Alternative Path & Counterfactual Analysis](#6-alternative-path--counterfactual-analysis)
7. [Uncertainty & Limitation Boundaries](#7-uncertainty--limitation-boundaries)

---

## 1. Purpose & Architectural Evolution

Version 2.0 introduced the Reverse Engineering Engine (Document 40), which inferred a single linear creation timeline. In reality, physical and digital documents often undergo complex, non-linear processing paths (e.g., authored digitally, exported to PDF, printed, signed physically, scanned, digitally edited in Photoshop, re-exported, and uploaded).

Version 3.0 evolves timeline reconstruction into a **Probabilistic Directed Lifecycle Graph ($\mathcal{G}_{\text{life}}$)**.

Instead of asserting a single fixed timeline, the system constructs a DAG of competing state transitions, assigning edge transition probabilities $P(e_{uv})$ based on physical and digital evidence.

---

## 2. Probabilistic Directed Lifecycle Graph ($\mathcal{G}_{\text{life}}$)

```
                       ┌─────────────────────────┐
                       │   [Node 0: Authoring]   │
                       │   (MS Word 365, P=0.98) │
                       └────────────┬────────────┘
                                    │
                       ┌────────────▼────────────┐
                       │   [Node 1: PDF Export]  │
                       │   (Quartz PDF, P=0.96)  │
                       └────────────┬────────────┘
                                    │
           ┌────────────────────────┴────────────────────────┐
           ▼                                                 ▼
┌─────────────────────┐                           ┌─────────────────────┐
│ [Node 2A: Direct    │                           │ [Node 2B: Print]    │
│  Digital Edit]      │                           │ (HP Laser, P=0.72)  │
│  (Photoshop P=0.28) │                           └──────────┬──────────┘
└──────────┬──────────┘                                      │
           │                                      ┌──────────┴──────────┐
           │                                      ▼                     ▼
           │                           ┌───────────────────┐ ┌───────────────────┐
           │                           │ [Node 3B1: Flatbed│ │ [Node 3B2: Camera │
           │                           │  Scanner P=0.68]  │ │  Photo P=0.04]    │
           │                           └─────────┬─────────┘ └─────────┬─────────┘
           │                                     │                     │
           └────────────────────────┬────────────┴─────────────────────┘
                                    ▼
                       ┌─────────────────────────┐
                       │ [Node 4: Submission]    │
                       │ (Final Uploaded Binary) │
                       └─────────────────────────┘
```

---

## 3. Lifecycle Node & Edge Taxonomy

### 3.1 Node Taxonomy (Document States)
- `STATE_AUTHORING`: Text and graphic composition in desktop software.
- `STATE_VECTOR_EXPORT`: Compilation into vector PDF/PostScript stream.
- `STATE_PHYSICAL_PRINT`: Deposition of ink/toner onto physical paper substrate.
- `STATE_PHYSICAL_MARKING`: Addition of wet ink signature or physical rubber stamp.
- `STATE_PHYSICAL_ACQUISITION`: Digitization via scanner or camera sensor.
- `STATE_DIGITAL_EDITING`: Manipulation in image raster editor (Photoshop, GIMP).
- `STATE_TRANSMISSION_COMPRESSION`: Re-compression via web upload or messaging service (WhatsApp, Email).

### 3.2 Edge Taxonomy (State Transitions)
- Edge $e_{u \to v}$: State transition with transition probability $P(e_{u \to v}) \in [0, 1]$ and transition evidence $\mathcal{E}_{u \to v}$.

---

## 4. Evidence-to-Lifecycle Mapping Rules

| Transition Edge | Required Supporting Evidence | Extraction Engine |
|-----------------|------------------------------|-------------------|
| `Authoring` $\to$ `VectorExport` | PDF Producer tags, XMP Creator tool, PDF stream structure | Metadata, Object Graph |
| `VectorExport` $\to$ `PhysicalPrint` | Halftone LPI/angle, toner satellite dots, paper fiber interlock | Micro-DNA, Texture |
| `PhysicalPrint` $\to$ `PhysicalAcquisition` | PRNU noise pattern, CCD striping, optical lens distortion | Noise, Frequency |
| `PhysicalAcquisition` $\to$ `DigitalEditing` | Double JPEG DCT combs, localized noise variance shifts | Frequency, Noise |

---

## 5. Graph Construction Algorithm

1. Initialize graph $\mathcal{G}_{\text{life}} = (V, E)$ with start node `STATE_AUTHORING` and terminal node `STATE_SUBMISSION`.
2. Evaluate evidence across all 10 Chromosomes to identify candidate physical/digital transitions.
3. For each candidate transition $u \to v$, compute transition likelihood $P(e_{u \to v} \mid \mathcal{E})$ using Bayesian network probability tables.
4. Prune transitions with $P(e_{u \to v}) < 0.01$.
5. Normalize outgoing edge probabilities for each node: $\sum_{v} P(e_{u \to v}) = 1.0$.

---

## 6. Alternative Path & Counterfactual Analysis

The lifecycle engine computes the **Most Probable Path (MPP)** using the Viterbi / Dijkstra algorithm over log-probabilities:

$$\text{MPP} = \arg\max_{\text{path} \in \mathcal{G}_{\text{life}}} \sum_{e \in \text{path}} \ln P(e)$$

If an alternative path has comparable likelihood ($\text{Likelihood}(\text{Path}_2) \ge 0.8 \times \text{Likelihood}(\text{MPP})$), both paths are preserved and exported in the final report to prevent premature path closure.

---

## 7. Uncertainty & Limitation Boundaries

- **Uncertainty Quantification**: Graph path entropy $H(\mathcal{G}_{\text{life}}) = -\sum P(\text{path}) \ln P(\text{path})$ quantifies path ambiguity. High entropy $H > 1.5$ triggers an **Ambiguous Lifecycle Warning**.

---

*Previous: [53_Forensic_Reasoning](../53_Forensic_Reasoning/README.md)*
*Next: [55_Multi_Scale_Analysis](../55_Multi_Scale_Analysis/README.md)*
*Return to: [Master Index](../README.md)*
