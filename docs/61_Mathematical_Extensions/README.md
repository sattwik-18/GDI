# Document 61 — Mathematical Extensions
## GDI: Advanced Mathematical Formalisms for v3.0 Forensic Intelligence Framework

**Version:** 3.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-22
**Authors:** Principal Architect, Chief Research Engineer, Technical Documentation Lead
**Cross-References:** [44_Mathematical_Foundations], [43_Uncertainty_Model], [51_Document_Physics], [53_Forensic_Reasoning], [55_Multi_Scale_Analysis], [58_Explainable_Evidence_Graph]

---

## Table of Contents

1. [Purpose & Scope](#1-purpose--scope)
2. [Information-Theoretic Extensions](#2-information-theoretic-extensions)
3. [Topological Data Analysis](#3-topological-data-analysis)
4. [Optimal Transport for Document Comparison](#4-optimal-transport-for-document-comparison)
5. [Spectral Graph Theory in Forensic Graphs](#5-spectral-graph-theory-in-forensic-graphs)
6. [Riemannian Geometry for Feature Manifolds](#6-riemannian-geometry-for-feature-manifolds)
7. [Random Matrix Theory for Noise Characterization](#7-random-matrix-theory-for-noise-characterization)
8. [Measure-Theoretic Probability Extensions](#8-measure-theoretic-probability-extensions)
9. [Computational Complexity Bounds](#9-computational-complexity-bounds)

---

## 1. Purpose & Scope

Document `44_Mathematical_Foundations` establishes the core notation, linear algebra, probability theory, and Bayesian framework underlying GDI. This document **extends** that foundation with advanced mathematical formalisms introduced by v3.0's new conceptual layers:

- **Document Physics** (Doc 51) requires energy minimization on graphs and stress tensor analysis.
- **Forensic Reasoning** (Doc 53) requires formal hypothesis algebra and Bayesian model selection.
- **Multi-Scale Analysis** (Doc 55) requires wavelet and pyramid theory.
- **Explainable Evidence Graph** (Doc 58) requires causal graph theory and counterfactual analysis.
- **Trust Computation** (Doc 59) requires calibration theory and effective sample size estimation.

This document provides the precise mathematical definitions, theorems, and proofs needed to ground these systems in rigorous mathematics. No approximation is introduced silently. Every bound is stated with its assumptions.

**Notation Conventions**: All notation is consistent with `44_Mathematical_Foundations`. New symbols are added below and do not conflict with existing symbols.

---

## 2. Information-Theoretic Extensions

### 2.1 Forensic Mutual Information

**Definition 61.1** — The *Forensic Mutual Information (FMI)* between evidence feature $X$ and ground truth class $Y$ is:

$$\text{FMI}(X; Y) = \sum_{x, y} P(x, y) \log_2 \frac{P(x, y)}{P(x)P(y)}$$

FMI is used to rank features by their discriminative value independent of the specific forensic model.

**Theorem 61.1** — *Data Processing Inequality*: For any deterministic function $f$, $\text{FMI}(f(X); Y) \leq \text{FMI}(X; Y)$.

This is the mathematical justification for the principle that feature engineering can never increase information; at best it preserves it.

### 2.2 Channel Capacity of Forensic Signals

Each forensic extraction module can be modeled as a **noisy channel** with capacity:

$$C_{\text{module}} = \max_{P(X)} \text{FMI}(X; Y)$$

Where the maximum is taken over all input distributions $P(X)$. The channel capacity bounds the maximum information any forensic conclusion can extract from the physical document signal.

**Practical Application**: Modules with $C_{\text{module}} < 0.1$ bits contribute negligible discriminative information and are candidates for deprecation.

### 2.3 Evidence Combination and Information Addition

For **conditionally independent** evidence sources $X_1, \ldots, X_n$ (given $Y$):

$$\text{FMI}(X_1, \ldots, X_n; Y) = \sum_{i=1}^{n} \text{FMI}(X_i; Y)$$

This is the mathematical justification for the log-LR addition rule in the Fusion Engine (Document 18). **Independence is required**. When sources are correlated, the actual combined information is less than the sum:

$$\text{FMI}(X_1, X_2; Y) = \text{FMI}(X_1; Y) + \text{FMI}(X_2 | X_1; Y)$$

Where $\text{FMI}(X_2 | X_1; Y) \leq \text{FMI}(X_2; Y)$.

This motivates the **evidence independence analysis** that the Fusion Engine performs before combining signals.

### 2.4 Minimum Description Length (MDL) for Model Selection

When selecting among competing forensic hypotheses, GDI uses the **Minimum Description Length** principle as a complement to Bayesian model selection:

$$H^* = \underset{H_k}{\arg\min} \left\{ L(H_k) + L(\mathcal{D} | H_k) \right\}$$

Where $L(\cdot)$ is description length in bits. This selects the hypothesis that provides the most compact explanation of the observed evidence — preferring simpler explanations (Occam's Razor in information-theoretic form).

---

## 3. Topological Data Analysis

### 3.1 Persistent Homology for Document Structure

Topological Data Analysis (TDA) provides a framework for analyzing the *shape* of document feature spaces independent of specific metrics.

**Definition 61.2** — Given a point cloud $\mathcal{X} = \{x_1, \ldots, x_n\} \subset \mathbb{R}^d$ of document features, the **Vietoris-Rips complex** $\mathcal{VR}(\mathcal{X}, \epsilon)$ at scale $\epsilon$ is the simplicial complex containing all subsets $\sigma \subset \mathcal{X}$ with $\text{diam}(\sigma) \leq \epsilon$.

**Definition 61.3** — The **persistence diagram** $\mathcal{PD}(k)$ for homological dimension $k$ is the multiset of pairs $(b_i, d_i)$ where $b_i$ is the "birth" scale and $d_i$ is the "death" scale of the $i$-th $k$-dimensional topological feature (connected component for $k=0$, loop for $k=1$, void for $k=2$).

**Forensic Application**: A document's layout connectivity structure has a characteristic persistence diagram. Forgeries created by copy-paste operations introduce spurious topological features (extra connected components, unexpected loops) that appear in $\mathcal{PD}(0)$ and $\mathcal{PD}(1)$ but not in the original template's diagram.

**Bottleneck Distance**: Two persistence diagrams $\mathcal{PD}_1, \mathcal{PD}_2$ are compared via:

$$d_B(\mathcal{PD}_1, \mathcal{PD}_2) = \inf_{\gamma} \sup_{x \in \mathcal{PD}_1} \|x - \gamma(x)\|_{\infty}$$

Where $\gamma$ ranges over bijections between the two diagrams (including mapping to the diagonal). Small bottleneck distance means topologically similar structures.

### 3.2 Euler Characteristic as Forensic Invariant

**Theorem 61.2** — The Euler characteristic $\chi$ of a planar document layout graph satisfies:

$$\chi = V - E + F = 2 - 2g$$

Where $V$ is vertices, $E$ is edges, $F$ is faces, and $g$ is the genus. For planar documents ($g = 0$), $\chi = 2$.

A tampered document that introduces non-planar connections (e.g., text regions overlapping image regions in a non-physically realizable way) will have $\chi \neq 2$. This is a **topological forgery invariant** detectable without any machine learning.

---

## 4. Optimal Transport for Document Comparison

### 4.1 Wasserstein Distance for Feature Distributions

When comparing the statistical distribution of a document's features against a template distribution, standard $L_2$ distance is sensitive to outliers and misaligned distributions. **Optimal Transport** provides a more geometrically meaningful comparison.

**Definition 61.4** — The *p-Wasserstein distance* between probability measures $\mu$ and $\nu$ on $\mathbb{R}^d$ is:

$$W_p(\mu, \nu) = \left(\inf_{\gamma \in \Gamma(\mu, \nu)} \int_{\mathbb{R}^d \times \mathbb{R}^d} \|x - y\|^p \, d\gamma(x, y)\right)^{1/p}$$

Where $\Gamma(\mu, \nu)$ is the set of all joint distributions ("transport plans") with marginals $\mu$ and $\nu$.

**Forensic Application**: Let $\mu_{\text{doc}}$ be the empirical distribution of kerning values extracted from the query document, and $\mu_{\text{template}}$ be the distribution from the reference template. Then:

$$\text{KerningDivergence} = W_2(\mu_{\text{doc}}, \mu_{\text{template}})$$

$W_2$ is preferred over KL divergence because it is well-defined even when the distributions have disjoint support (i.e., when the document uses completely different kerning values than the template).

### 4.2 Sliced Wasserstein for High-Dimensional Features

Computing $W_2$ exactly is $\mathcal{O}(n^3)$ in the number of samples. For high-dimensional feature spaces, the **Sliced Wasserstein Distance** approximates $W_2$ efficiently:

$$\text{SW}_p(\mu, \nu) = \int_{\mathbb{S}^{d-1}} W_p(\theta_{\#}^{\mu}, \theta_{\#}^{\nu}) \, d\theta$$

Where $\theta_{\#}^{\mu}$ is the one-dimensional projection of $\mu$ along direction $\theta \in \mathbb{S}^{d-1}$, and the integral is approximated by Monte Carlo sampling over $K$ random directions. Complexity: $\mathcal{O}(Kn\log n)$.

### 4.3 Earth Mover's Distance for Spatial Layout Comparison

The $W_1$ (Earth Mover's) distance has a natural forensic interpretation: it is the minimum "cost" of transforming one document's spatial layout into another's, where cost = mass × distance.

$$W_1(\mu_{\text{doc}}, \mu_{\text{template}}) = \min_{\text{transport plan}} \sum_{i,j} T_{ij} \cdot \|x_i - y_j\|$$

Large EMD indicates significant spatial rearrangement — a strong signal for layout tampering when combined with other evidence.

---

## 5. Spectral Graph Theory in Forensic Graphs

### 5.1 Graph Laplacian for Layout Analysis

**Definition 61.5** — For a document layout graph $G = (V, E, w)$ with weighted adjacency matrix $A$, the **normalized graph Laplacian** is:

$$\mathcal{L} = I - D^{-1/2} A D^{-1/2}$$

Where $D = \text{diag}(A\mathbf{1})$ is the degree matrix.

**Properties**:
- $\mathcal{L}$ is positive semi-definite with eigenvalues $0 = \lambda_0 \leq \lambda_1 \leq \ldots \leq \lambda_{|V|}$.
- $\lambda_1$ (Fiedler value) measures the **algebraic connectivity** — low $\lambda_1$ means the graph is close to disconnected (sparse layout).
- The Fiedler vector $\mathbf{v}_1$ provides a natural 1D embedding of graph nodes, revealing community structure.

**Forensic Application**: A document's structural graph has a characteristic Laplacian spectrum. Copy-paste forgeries alter the spectrum by introducing new isolated components (reducing $\lambda_1$) or artificial bridges (increasing $\lambda_1$ unnaturally).

### 5.2 Spectral Distance Between Graphs

**Definition 61.6** — The *Spectral Distance* between two graphs $G_1$ and $G_2$ with eigenvalue sequences $\Lambda_1, \Lambda_2$ is:

$$d_{\text{spec}}(G_1, G_2) = \|\Lambda_1 - \Lambda_2\|_2 = \sqrt{\sum_{k=1}^{\min(|V_1|, |V_2|)} (\lambda_k^{(1)} - \lambda_k^{(2)})^2}$$

This is computed between a query document's graph and the reference template's graph. $d_{\text{spec}}$ is invariant to vertex labeling permutations, making it suitable for comparing documents with similar structure but different content.

### 5.3 Random Walk Forensic Signatures

The probability that a length-$t$ random walk starting at vertex $u$ reaches vertex $v$ is:

$$P^t(u,v) = (I - \mathcal{L})^t_{uv}$$

This **heat kernel** $K_t = e^{-t\mathcal{L}}$ characterizes how information "diffuses" through the document graph over time $t$. The trace $\text{tr}(K_t)$ is a graph invariant used as a compact forensic signature.

---

## 6. Riemannian Geometry for Feature Manifolds

### 6.1 Manifold Hypothesis in Document Forensics

The high-dimensional feature vectors extracted from genuine documents do not fill the full $\mathbb{R}^d$ feature space uniformly. They cluster on a **lower-dimensional manifold** $\mathcal{M} \subset \mathbb{R}^d$ corresponding to the physical constraints of genuine document production.

**Claim**: The genuine document manifold $\mathcal{M}_{\text{genuine}}$ has intrinsic dimension $d_{\text{intrinsic}} \ll d_{\text{ambient}}$, reflecting that legitimate document production has far fewer degrees of freedom than the space of all possible pixel arrangements.

### 6.2 Riemannian Metric on Feature Space

**Definition 61.7** — A *Riemannian metric* on $\mathcal{M}$ is a smoothly varying inner product $g_p: T_p\mathcal{M} \times T_p\mathcal{M} \to \mathbb{R}$ on each tangent space $T_p\mathcal{M}$.

The **geodesic distance** $d_{\mathcal{M}}(x, y)$ between two points on the manifold is the length of the shortest path connecting them *within the manifold* — not the straight-line (Euclidean) distance through ambient space.

$$d_{\mathcal{M}}(x, y) = \inf_{\gamma: [0,1] \to \mathcal{M}, \gamma(0)=x, \gamma(1)=y} \int_0^1 \sqrt{g_{\gamma(t)}(\dot\gamma(t), \dot\gamma(t))} \, dt$$

**Forensic Application**: Forged documents may have feature vectors that lie off the genuine manifold. The **manifold deviation distance**:

$$\delta_{\mathcal{M}}(x) = \inf_{y \in \mathcal{M}} d_{\text{Euclidean}}(x, y)$$

measures how far a query document's features deviate from the genuine manifold. Large $\delta_{\mathcal{M}}$ is a strong forgery indicator.

### 6.3 Fisher Information Metric

For parametric models, the **Fisher Information Metric** defines a natural Riemannian metric on the parameter space:

$$g_{ij}(\theta) = \mathbb{E}\left[\frac{\partial \log P(x|\theta)}{\partial \theta_i} \frac{\partial \log P(x|\theta)}{\partial \theta_j}\right]$$

This metric defines the **Cramér-Rao lower bound** on estimation variance and is used in GDI to characterize the fundamental limits of forensic detection: no estimator can achieve lower variance than the inverse Fisher information.

---

## 7. Random Matrix Theory for Noise Characterization

### 7.1 Marchenko-Pastur Law for Background Noise

When analyzing correlation matrices of document features extracted from genuine documents, the eigenvalue distribution of the **sample covariance matrix** $\hat{\Sigma} = \frac{1}{n} X^T X$ follows the **Marchenko-Pastur distribution** when the features are i.i.d.:

$$\rho_{\text{MP}}(\lambda) = \frac{\sqrt{(\lambda_+ - \lambda)(\lambda - \lambda_-)}}{2\pi \sigma^2 \lambda / n} \cdot \mathbb{1}_{[\lambda_-, \lambda_+]}(\lambda)$$

Where $\lambda_{\pm} = \sigma^2 (1 \pm \sqrt{d/n})^2$ are the theoretical bulk eigenvalue bounds.

**Forensic Application**: In a genuine document, the correlation between extracted features should exhibit a random matrix spectrum consistent with $\rho_{\text{MP}}$. Eigenvalues *above* $\lambda_+$ represent genuine structural correlations. Eigenvalues *far below* $\lambda_-$ indicate anomalous anti-correlations that may indicate artificial constraint imposition (a common artifact in synthetic or forged documents).

### 7.2 Spiked Covariance Model

When forensic structure is present, the covariance matrix follows a **spiked model**:

$$\Sigma = \sigma^2 I + \sum_{k=1}^{r} (\theta_k - \sigma^2) u_k u_k^T$$

Where $r$ is the number of true structural components ("spikes") and $\theta_k > \lambda_+$ are the spiked eigenvalues. The number of detectable spikes $r$ bounds the number of independent forensic dimensions that can be resolved from a document.

---

## 8. Measure-Theoretic Probability Extensions

### 8.1 Formal Probability Space

**Definition 61.8** — The GDI forensic probability space is the triple $(\Omega, \mathcal{F}, P)$ where:

- $\Omega = \mathcal{D} \times \{0, 1\}$ is the sample space of (document, label) pairs
- $\mathcal{F}$ is the $\sigma$-algebra generated by all measurable document properties
- $P$ is the probability measure defined by the prior over document populations

### 8.2 Radon-Nikodym Theorem and Likelihood Ratios

The **Radon-Nikodym theorem** provides the measure-theoretic justification for the likelihood ratio framework:

**Theorem 61.3** — If $P_{H_1} \ll P_{H_0}$ (i.e., the forged distribution is absolutely continuous with respect to the genuine distribution), then there exists a unique measurable function $\frac{dP_{H_1}}{dP_{H_0}}$ — the **Radon-Nikodym derivative** — such that:

$$P_{H_1}(A) = \int_A \frac{dP_{H_1}}{dP_{H_0}} \, dP_{H_0} \quad \forall A \in \mathcal{F}$$

The function $\Lambda(x) = \frac{dP_{H_1}}{dP_{H_0}}(x)$ is precisely the **likelihood ratio** $\text{LR}(x)$ used throughout GDI.

**Implication**: The LR framework is valid precisely when $P_{H_1} \ll P_{H_0}$ — when the forged distribution does not assign probability to events that have zero probability under genuine. In forensic practice, this assumption can fail at extreme manipulation levels, which is why the `OUTSIDE_MODEL_RANGE` fallback exists in the Decision Engine.

### 8.3 De Finetti's Theorem and Exchangeability

When GDI processes a **batch** of documents alleged to originate from the same source, it exploits **exchangeability**: the joint distribution of the batch is invariant to permutation.

**De Finetti's Theorem** (informal): An exchangeable sequence of random variables behaves as if it were i.i.d. given some latent parameter $\theta$ representing the "true source."

This justifies the hierarchical Bayesian model used when analyzing multiple documents from a single case: the documents share a latent source parameter, enabling information sharing across documents within the case.

---

## 9. Computational Complexity Bounds

### 9.1 Complexity Table for v3.0 Mathematical Operations

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Persistent homology (Vietoris-Rips) | $\mathcal{O}(n^3)$ worst case | Use approximations for $n > 10^4$ |
| Wasserstein-2 distance (exact) | $\mathcal{O}(n^3)$ | Use Sliced Wasserstein for $d > 10$ |
| Sliced Wasserstein ($K$ projections) | $\mathcal{O}(Kn\log n)$ | $K=100$ typical |
| Graph Laplacian eigendecomposition | $\mathcal{O}(|V|^3)$ | Use Lanczos for sparse graphs |
| Spectral distance computation | $\mathcal{O}(|V|^2)$ after eigendecomp | |
| Manifold deviation distance | $\mathcal{O}(n \cdot d_{\text{ambient}})$ | After manifold fit (offline) |
| Marchenko-Pastur bulk test | $\mathcal{O}(d^2 n)$ | $d$ = feature dim, $n$ = samples |
| Topological Euler characteristic | $\mathcal{O}(|V| + |E|)$ | Linear in graph size |
| Fisher Information metric | $\mathcal{O}(d^2)$ per point | Jacobian computation |
| Heat kernel trace $\text{tr}(K_t)$ | $\mathcal{O}(|V| k)$ | $k$ Lanczos iterations |

### 9.2 Approximation Hierarchy

When exact computation is intractable for a given document size, the following approximation hierarchy applies:

```
Exact Computation
    │ (feasible for |V| ≤ 1,000)
    ▼
Randomized Approximation (±5% error bound)
    │ (feasible for |V| ≤ 10,000)
    ▼
Heuristic / Streaming Approximation (±15% error bound, flagged)
    │ (feasible for |V| ≤ 100,000)
    ▼
Feature Reduction + Exact on Reduced Space (loss-of-fidelity logged)
```

Every approximation step is logged in the case record with the approximation method, expected error bound, and the estimated impact on verdict confidence.

### 9.3 Complexity Constraints on Real-Time Processing

For the real-time API path ($\leq$ 60 second SLA), the following maximum problem sizes are enforced:

| Feature | Max Size for Real-Time | Overflow Action |
|---------|----------------------|-----------------|
| Document layout graph $|V|$ | 5,000 nodes | Coarsen graph before spectral analysis |
| Feature vector dimension $d$ | 2,048 | PCA reduction to 512 |
| Feature sample count $n$ | 10,000 | Stratified subsample |
| TDA complex scale parameter | 3 levels | Truncate at level 3 |

Larger documents are automatically routed to the **async high-fidelity queue** (90-minute SLA) where exact algorithms are applied.

---

*Document 61 — End of Specification*
*GDI Platform Version 3.0.0 — INTERNAL ENGINEERING CONFIDENTIAL*
