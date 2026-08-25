# Document 62 — Research Directions
## GDI: Open Problems, Emerging Capabilities, and Long-Horizon Research Agenda

**Version:** 3.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-22
**Authors:** Principal Architect, Chief Research Engineer, Technical Documentation Lead
**Cross-References:** [36_Future_Roadmap], [35_Patent_Notes], [44_Mathematical_Foundations], [61_Mathematical_Extensions], [50_Engineering_Decision_Records]

---

## Table of Contents

1. [Purpose & Scope](#1-purpose--scope)
2. [Open Problems in Forensic Signal Processing](#2-open-problems-in-forensic-signal-processing)
3. [AI and Deep Learning Research Frontiers](#3-ai-and-deep-learning-research-frontiers)
4. [Fundamental Scientific Open Questions](#4-fundamental-scientific-open-questions)
5. [Emerging Document Production Technologies](#5-emerging-document-production-technologies)
6. [Cross-Disciplinary Research Opportunities](#6-cross-disciplinary-research-opportunities)
7. [Long-Horizon Speculative Directions](#7-long-horizon-speculative-directions)
8. [Research Prioritization Framework](#8-research-prioritization-framework)
9. [Collaboration & Publication Policy](#9-collaboration--publication-policy)

---

## 1. Purpose & Scope

### 1.1 Why a Research Directions Document

This document serves three critical functions:

1. **Institutional knowledge preservation**: Documents what the team currently does not know — preventing future teams from re-discovering the same limitations or repeating failed research directions.

2. **Research agenda communication**: Communicates to external academic collaborators, hired research engineers, and grant agencies what problems GDI is actively investigating.

3. **Intellectual property foresight**: Identifies research directions that, if successful, would generate patentable new capabilities — enabling proactive IP filing strategy.

### 1.2 Epistemic Honesty Standard

Every item in this document represents a **genuinely open problem** as of the writing date. Claims about future capabilities are stated as research hypotheses, not engineering commitments. The following language conventions apply:

- **"We believe"** → research hypothesis with plausibility argument but no empirical support.
- **"We hypothesize"** → theoretical argument supporting feasibility, no implementation attempted.
- **"We have preliminary evidence"** → informal experiments conducted; results not yet peer-reviewed.
- **"Open question"** → no current hypothesis; genuinely unknown.

---

## 2. Open Problems in Forensic Signal Processing

### 2.1 The Signal Floor Problem

**Problem Statement**: For any forensic signal $S$, there exists a detection threshold below which the forensic system cannot reliably distinguish signal from noise. This **signal floor** $\delta_{\min}$ is:

$$\delta_{\min}(S) = f(\sigma_{\text{noise}}, N_{\text{samples}}, \text{sensor\_properties})$$

Current forensic pipelines operate well above this floor for high-quality scanned documents. However, as document capture moves to mobile devices (lower SNR, irregular illumination, motion blur), many of our current signals approach their detection floor.

**Research Question**: Can we derive tight information-theoretic lower bounds on the signal floor for each forensic signal category? Specifically:

$$\delta_{\min}^*(S) = \sqrt{\frac{2 \sigma_{\text{noise}}^2}{N_{\text{samples}}}} \cdot z_{\alpha/2}$$

And does any practical extraction algorithm achieve this Cramér-Rao bound?

**Known Partial Results**: For 1D signals (noise patterns, frequency spectra), the matched filter achieves the CRLB. For 2D spatial patterns (layout geometry), the achievable bound is unknown.

### 2.2 The Reference Distribution Problem

**Problem Statement**: The GDI likelihood ratio framework requires a reference distribution $P_{\text{genuine}}$ against which query documents are scored. This distribution is estimated from the template database. However:

- For rare document types (unusual languages, regional formatting standards, historical documents), the reference corpus is sparse.
- For novel document types (emerging digital-native formats), no reference corpus exists.
- The reference distribution shifts as legitimate document production technology evolves.

**Research Question**: How do we perform principled forensic inference when the reference distribution is unknown or poorly characterized? Can Bayesian non-parametric methods (Dirichlet Process Mixtures, Gaussian Process priors) provide calibrated posteriors under sparse reference data?

**Hypothesis**: We believe a **few-shot forensic calibration** approach is feasible — using 5–10 reference documents to calibrate forensic signals for a new document type, with uncertainty inflated proportionally to the sparsity of the reference set.

### 2.3 The Counterfactual Ground Truth Problem

**Problem Statement**: The Counterfactual Reasoning Engine (Document 58) computes inversion thresholds assuming local linearity of the evidence fusion function. This assumption fails for:

- Non-monotone decision boundaries.
- Features with extreme outlier distributions.
- Interactions between features that are non-linear in combination.

**Research Question**: What is the correct mathematical framework for computing exact (non-approximate) counterfactual inversion thresholds for the full GDI scoring function?

**Current Approach Limitation**: The current gradient-based approach has error bounds proportional to the second-order derivative of the fusion function. For highly non-linear neural network classifiers, this bound can be loose.

**Candidate Approach**: **Integrated Gradients** (Sundararajan et al., 2017) provides a path-integral formulation that satisfies axioms of implementation invariance and completeness. Integration into the XEG framework is a planned research task.

---

## 3. AI and Deep Learning Research Frontiers

### 3.1 Foundation Model Fine-Tuning for Forensic Signals

**Current State**: GDI uses specialized forensic models trained from scratch on forensic-specific datasets. Foundation models (CLIP, Dino-v2, SAM) are used only for general visual feature extraction.

**Hypothesis**: Fine-tuning foundation models on forensic discrimination tasks — rather than training specialized models from scratch — may yield:
- Better generalization to out-of-distribution document types.
- Better few-shot performance on rare document categories.
- Improved robustness to adversarial perturbations (due to larger training diversity).

**Open Question**: Does forensic fine-tuning of foundation models compromise their general capabilities in ways that reduce forensic utility? This is unknown and requires empirical investigation.

**Research Program**: Design a controlled experiment fine-tuning Dino-v2 on the GDI forensic corpus. Compare AUROC on the Tier-0 benchmark against the current specialized model baseline.

### 3.2 Self-Supervised Forensic Pretraining

**Hypothesis**: Forensic pretraining objectives can be designed that do not require labeled forged documents:

1. **Consistency Pretraining**: Two randomly augmented views of the same document must produce similar representations; two documents from different sources must produce different representations.

2. **Reconstruction Pretraining**: Predict masked regions of a document — genuine documents should be more predictable from their context than forged documents with inconsistent copy-pasted regions.

3. **Physical Invariance Pretraining**: Representations should be invariant to known physical transformations (rotation, rescaling, benign compression) and variant to adversarial manipulations.

**Challenge**: Defining precise augmentation distributions that preserve genuine identity while distinguishing forged characteristics is non-trivial and is an open research problem.

### 3.3 Causal Representation Learning for Forensics

**Problem Statement**: Current GDI models learn **correlational** representations: features that are statistically associated with forgery. We hypothesize that **causal** representations — those reflecting the actual physical mechanisms of forgery — would be more robust and generalizable.

**Research Direction**: Apply causal representation learning frameworks (IRM, CausalVAE) to learn representations that are invariant to spurious correlations (e.g., document topic, page count) while capturing genuine causal forgery mechanisms (e.g., re-rasterization introduces specific artifacts *because* of specific physical processes).

**Key Challenge**: The forensic causal graph is partially unknown. We know that "scan-then-print-then-scan" causes double JPEG rounding artifacts — but the complete causal graph of all document production steps is not fully charted. Constructing this causal model is a prerequisite for causal representation learning.

### 3.4 Adversarial Robustness as a Research Priority

**Problem Statement**: Adversarial examples — inputs crafted to fool forensic classifiers while appearing genuine to human inspectors — represent a fundamental and unsolved vulnerability.

**Known Limitations of Current Defenses**:
- Adversarial training improves robustness to seen attack types but degrades performance on clean inputs.
- Certified defenses (randomized smoothing) provide provable robustness guarantees but reduce discriminative power significantly.
- Detection of adversarial inputs is itself an arms race with no provably secure solution.

**Research Hypothesis**: **Ensemble diversity** — using forensic models trained with sufficiently different architectures, training data, and objectives — may provide robustness without the clean-performance penalty. We hypothesize that a perfectly diverse ensemble would require an adversary to simultaneously fool all models, which is computationally harder than fooling any one.

**Open Question**: What formal diversity metric captures the property that two models are "sufficiently different" from an adversarial robustness perspective? No satisfactory answer exists in the literature as of 2026.

---

## 4. Fundamental Scientific Open Questions

### 4.1 The Limit of Forensic Detection

**Theoretical Question**: Is there a theoretical lower bound on the fraction of forged documents that *cannot* be detected by any forensic system, regardless of sophistication?

**Partial Answer from Information Theory**: By Shannon's channel capacity arguments, if the information lost during forgery is below the noise floor of the forensic extraction channel, detection is information-theoretically impossible. This implies there exists a class of "perfect forgeries" — those that preserve all detectable signal channels exactly — that are undetectable in principle.

**Engineering Implication**: GDI must be designed to acknowledge this limit honestly. Every verdict report should include a statement of which forgery classes are within the system's detection range and which are not.

### 4.2 The Uniqueness of Document Identity

**Scientific Question**: Do sufficient forensic signals exist to uniquely identify a physical document instance (as opposed to merely its template class)?

**Current Evidence**: 
- Inkjet printers introduce banding patterns unique to individual print heads.
- Paper grain orientation is statistically unique at sub-millimeter scales.
- Scanner CCD noise patterns are device-specific.

**Open Question**: Is the combination of these signals sufficient for **1-in-10^9** document uniqueness (comparable to fingerprint identification standards), or only for 1-in-10^3 or 1-in-10^6 uniqueness? The answer has direct legal implications for how strongly a specific document can be tied to a specific production device.

### 4.3 Temporal Signal Decay

**Scientific Question**: At what rate do forensic signals degrade in aging documents? 

Known decay processes:
- Paper yellowing follows first-order kinetics: $y(t) = y_0 \cdot e^{-k_y t}$ with $k_y$ dependent on paper composition and storage conditions.
- Ink fading follows similar kinetics with material-dependent constants.
- EXIF metadata is immutable (digital), but storage medium degradation may introduce bit errors.

**Open Question**: What is the minimum time period $T_{\min}$ after which forensic signals become insufficiently reliable for court-admissible evidence? This is currently unknown and likely varies across document types, storage environments, and signal categories.

---

## 5. Emerging Document Production Technologies

### 5.1 AI-Generated Documents

**Challenge**: Large multimodal models (GPT-4o, Gemini, Claude) can now generate visually authentic-looking documents — PDFs, contracts, invoices — that have never been printed or scanned. These documents:

- Have no physical substrate (no paper grain, scanner noise, or ink bleeding).
- Are produced by neural networks that can be fine-tuned to match the statistical signature of authentic documents.
- May produce metadata consistent with real software tools.

**Research Priority**: Developing a detection framework specifically for AI-generated documents requires fundamentally different signals from those used for scanned-document forensics. Current hypotheses:

1. **Semantic coherence analysis**: AI-generated text may exhibit statistical patterns (unusual word distributions, specific positional biases) detectable via language model perplexity analysis.
2. **Pixel-level generation artifacts**: Diffusion models and GAN-based generators introduce specific high-frequency artifacts detectable in the frequency domain.
3. **Font rendering inconsistencies**: AI-rendered text may not perfectly replicate the sub-pixel rendering engine of real PDF producers.

**Caveat**: As generative AI improves, any specific artifact-based detection technique will become obsolete. A research program focused on theoretically grounded, artifact-independent detection is needed.

### 5.2 Post-Quantum Cryptographic Signatures in Documents

**Emerging Standard**: Post-quantum digital signatures (CRYSTALS-Dilithium, FALCON) are beginning to be embedded in document formats for authentication. As these become standard, the forensic value of detecting *absence* of a valid signature will increase.

**Research Direction**: Integrate post-quantum signature verification as a primary forensic signal. A document claiming to be from a post-2028 enterprise source that lacks a valid post-quantum signature would be highly anomalous.

### 5.3 AR/Holographic Documents

**Speculative**: Several jurisdictions are exploring holographic or augmented-reality document formats that embed forensic anti-counterfeiting features in light-field or holographic substrates. GDI's current signal framework does not address these formats.

**Long-Term Research**: Extending the Genome Extraction Engine (Document 05) to support light-field forensics requires entirely new physical models of holographic media.

---

## 6. Cross-Disciplinary Research Opportunities

### 6.1 Forensic Linguistics Integration

**Opportunity**: Document authenticity is not only a visual forensic question. The *linguistic* characteristics of document text — vocabulary, syntactic patterns, phraseology, discourse structure — carry authorship signals that are complementary to visual forensics.

**Integration Hypothesis**: A unified authorship attribution module, operating in the Forensic Ontology layer, would enable:
- Cross-referencing visual forgery signals with linguistic anomaly signals.
- Detecting documents whose text is machine-generated or translated but visual appearance is authentic.
- Verifying consistency between claimed author identity and known linguistic fingerprints.

**Complexity**: NLP-based authorship attribution requires sufficient document text length ($\geq$ 500 words for reliable inference). Many forensic documents (invoices, forms, identification documents) are below this threshold.

### 6.2 Materials Science Collaboration

**Opportunity**: Document 51 (Document Physics) models the document as a physical system but uses simplified energy functions. A collaboration with materials scientists specializing in paper, ink, and printing physics would allow:

- Calibrated physical models of ink penetration depth (affecting texture analysis).
- Quantitative models of aging-induced paper deformation.
- Precise spectroscopic predictions of ink spectral reflectance curves.

These would transform the Document Physics engine from a heuristic analog into a first-principles physical model.

### 6.3 Epidemiological Methods for Forgery Pattern Analysis

**Analogy**: Forgery techniques, like pathogens, spread through populations: specific forgery methods are learned, shared, and adapted within forgery communities. Epidemiological models (SIR, SIS) may be applicable to modeling the spread and mutation of forgery techniques over time.

**Research Hypothesis**: If the prevalence of a specific forgery artifact type follows logistic growth followed by exponential decline (as the technique becomes known and countermeasures are deployed), predictive models could anticipate emerging forgery methods before they become widespread.

---

## 7. Long-Horizon Speculative Directions

These items are included for intellectual completeness. They represent possibilities that are theoretically interesting but currently have no clear path to implementation.

### 7.1 Quantum Forensics

If quantum sensors become practical for document scanning, quantum measurement offers potentially sub-atomic precision in measuring paper surface topology. Whether this precision provides forensically relevant information above current sensor capabilities is unknown. Expected timeline: 15–20+ years.

### 7.2 Biological Embedding Detection

Some research programs are exploring embedding biological markers (DNA, synthetic biology constructs) in paper or ink as authentication mechanisms. If such mechanisms become commercially adopted, forensic authentication would shift to biological rather than purely physical/digital signals. GDI would require an entirely new biosensor-based input layer.

### 7.3 Decentralized Forensic Networks

**Concept**: A network of GDI instances, each processing documents in their jurisdiction, could share forensic intelligence (anonymized signal statistics, template population data) without sharing the underlying documents. This would expand the effective reference corpus globally while preserving jurisdictional data sovereignty.

**Challenge**: Federated learning for forensic intelligence raises fundamental questions about how forensic models can be jointly trained across jurisdictions with different legal definitions of "authentic" and "forged."

---

## 8. Research Prioritization Framework

### 8.1 Priority Matrix

Research directions are evaluated on two axes:

| Axis | Description |
|------|-------------|
| **Forensic Impact** | How much would this improve detection capability, calibration, or coverage? |
| **Feasibility** | How tractable is this with current tools, methods, and personnel? |

```
                    HIGH IMPACT
                         │
  [AI-Generated Doc     │  [Causal Representation
   Detection]           │   Learning]
   High Priority →      │   → Medium Priority
                         │
LOW ─────────────────────┼──────────────────── HIGH
FEASIBILITY              │                  FEASIBILITY
                         │
  [Quantum Forensics]    │  [Foundation Model
   → Speculative         │   Fine-Tuning]
                         │   → High Priority
                    LOW IMPACT
```

### 8.2 Research Horizon Classification

| Horizon | Timeline | Examples |
|---------|----------|---------|
| **H1 — Near Term** | 0–18 months | Foundation model fine-tuning, Integrated Gradients for XEG |
| **H2 — Medium Term** | 18 months – 4 years | Causal representation learning, AI-generated document detection |
| **H3 — Long Term** | 4–10 years | Federated forensic networks, materials science models |
| **H4 — Speculative** | 10+ years | Quantum forensics, biological embedding detection |

### 8.3 Current Funded Research Programs

| Program | Horizon | Lead | Status |
|---------|---------|------|--------|
| AI-Generated Document Detection | H1 | AI Research Team | **Active** |
| Foundation Model Forensic Fine-Tuning | H1 | ML Engineering | **Active** |
| Few-Shot Calibration for Rare Documents | H2 | Research Engineering | **Planning** |
| Causal Representation Learning | H2 | Research Science | **Planning** |
| Integrated Gradients for XEG | H1 | Core Engineering | **Active** |
| Federated Forensic Intelligence | H3 | Architecture | **Concept** |

---

## 9. Collaboration & Publication Policy

### 9.1 External Collaboration Guidelines

GDI research may be conducted in collaboration with academic institutions under the following constraints:

1. **No disclosure of production system architecture** to external collaborators without executed NDA and IP assignment agreement.
2. **No disclosure of client case data** regardless of anonymization.
3. **Benchmark corpus access** may be granted to vetted academic collaborators for reproducibility purposes, under data use agreement.
4. All collaborative research results are reviewed by Legal and IP counsel before submission for publication.

### 9.2 Publication Strategy

GDI targets publication of research results that:
- Do not disclose novel detection signals before they are patented.
- Advance the theoretical foundations of forensic science without revealing operational capabilities.
- Build academic credibility that supports enterprise sales and regulatory trust.

Priority publication venues: *TIFS* (IEEE Transactions on Information Forensics and Security), *WIFS*, *ICASSP*, *CVPR* (workshop tracks), *USENIX Security*.

### 9.3 Open Source Contribution Strategy

Non-core, non-proprietary tooling (calibration utilities, benchmark evaluation harnesses, visualization tools) may be released as open source. This builds community goodwill and attracts research talent without disclosing competitive IP.

Core forensic algorithms, extraction signal implementations, and reference corpus content are **never** open-sourced.

---

*Document 62 — End of Specification*
*GDI Platform Version 3.0.0 — INTERNAL ENGINEERING CONFIDENTIAL*
