# Document 38 — Genome Hierarchy
## GDI: Hierarchical Biological Genome Architecture

**Version:** 2.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Authors:** Principal Architect, Chief Research Engineer, Technical Documentation Lead
**Cross-References:** [05_Genome_Extraction_Engine], [39_Digital_Twin], [44_Mathematical_Foundations], [45_Genome_Taxonomy]

---

## Table of Contents

1. [Executive Rationale](#1-executive-rationale)
2. [Biological Metaphor and Architectural Hierarchy](#2-biological-metaphor-and-architectural-hierarchy)
3. [Formal Layer Specifications](#3-formal-layer-specifications)
    - [3.1 Document Genome (Organism Level)](#31-document-genome-organism-level)
    - [3.2 Chromosomes (Subsystem Level)](#32-chromosomes-subsystem-level)
    - [3.3 Genes (Functional Feature Group Level)](#33-genes-functional-feature-group-level)
    - [3.4 Traits (Phenotypic Characteristic Level)](#34-traits-phenotypic-characteristic-level)
    - [3.5 Measurements (Raw Sensor/Metric Level)](#35-measurements-raw-sensormetric-level)
    - [3.6 Feature Vectors (Mathematical Embedding Level)](#36-feature-vectors-mathematical-embedding-level)
    - [3.7 Evidence Objects (Forensic Signal Level)](#37-evidence-objects-forensic-signal-level)
    - [3.8 Confidence Objects (Epistemic/Aleatoric Quality Level)](#38-confidence-objects-epistemicaleatoric-quality-level)
    - [3.9 Version Metadata (Provenance and Evolution Level)](#39-version-metadata-provenance-and-evolution-level)
4. [Extraction Pipeline Lifecycle](#4-extraction-pipeline-lifecycle)
5. [Storage and Binary Protocol Serialization](#5-storage-and-binary-protocol-serialization)
6. [Hierarchical Similarity & Distance Computation](#6-hierarchical-similarity--distance-computation)
7. [Epistemic and Aleatoric Uncertainty Propagation](#7-epistemic-and-aleatoric-uncertainty-propagation)
8. [Failure Modes and Recovery Strategies](#8-failure-modes-and-recovery-strategies)
9. [Verification and Testing Methodology](#9-verification-and-testing-methodology)

---

## 1. Executive Rationale

In Version 1.0 of the GDI Platform, the Document Genome was modeled as a flat, concatenated vector space $\mathbb{R}^D$ ($D \in [1391, 3168]$). While computationally efficient for vector database indexing (Qdrant HNSW), flat vectors introduce fundamental architectural limitations:

1. **Loss of Structural Context**: Feature interactions across distinct physical domains (e.g., how paper grain interacts with ink spread vs. how font kerning relates to line spacing) are flattened into uniform vector dimensions.
2. **Brittle Evidence Aggregation**: Global vector distances (Euclidean, Cosine) blur localized anomalies. A severe localized forgery (e.g., single altered digit) can be mathematically drowned out by high similarity across the remaining 3,000 dimensions.
3. **Limited Explainability**: Attributing a flat distance scalar to specific forensic anomalies requires complex post-hoc attributions (SHAP/LIME), which suffer from instability and approximation error.

Version 2.0 transitions the Document Genome from a flat vector to a **Hierarchical Biological Model**. The genome is structured as a 9-layer directed tree $\mathcal{T}_{\text{genome}}$, directly mirroring biological genetics. Each layer abstracts and transforms physical and statistical characteristics into formal, versioned, and cryptographically signed objects.

---

## 2. Biological Metaphor and Architectural Hierarchy

```
┌────────────────────────────────────────────────────────────────────────┐
│                        LAYER 1: DOCUMENT GENOME                        │
│                   (Complete Forensic Organism Representation)          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                         LAYER 2: CHROMOSOMES                           │
│     (10 Structural Sub-Genomes: Layout, Typography, Rendering...)      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                            LAYER 3: GENES                              │
│       (Functional Feature Groups: Font Glyph, Kerning, GLCM...)        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                            LAYER 4: TRAITS                             │
│       (Phenotypic Characteristics: Stroke Width, Sub-pixel Jitter)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                         LAYER 5: MEASUREMENTS                          │
│          (Raw Measured Values, Units, Modality Manifests)              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                       LAYER 6: FEATURE VECTORS                         │
│         (Normalized Continuous & Discrete Vector Embeddings)          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                       LAYER 7: EVIDENCE OBJECTS                        │
│        (Likelihood Ratios, Evidence Multipliers, Anomaly Maps)         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                      LAYER 8: CONFIDENCE OBJECTS                       │
│    (Epistemic/Aleatoric Covariance, Measurement Precision Bounds)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                      LAYER 9: VERSION METADATA                         │
│     (Pipeline Version, Cryptographic Seals, Schema Hashes, HSM cert)   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Formal Layer Specifications

### 3.1 Document Genome (Organism Level)
- **Purpose**: Top-level container representing the complete forensic identity of a document instance.
- **Inputs**: Raw document payload, tenant configuration, target pipeline version.
- **Outputs**: Fully populated, cryptographically signed biological genome tree $\mathcal{T}_{\text{genome}}$.
- **Structure**: Contains root metadata, pointer to 10 Chromosome objects, and the root cryptographic seal.

### 3.2 Chromosomes (Subsystem Level)
- **Purpose**: Represents major independent physical or logical forensic dimensions.
- **Taxonomy**:
  1. `Chr_01_Layout`: Spatial layout, grid structures, margin properties.
  2. `Chr_02_Typography`: Font glyphs, kerning, baselines, ligatures, hinting.
  3. `Chr_03_Rendering`: Anti-aliasing profiles, subpixel ordering, edge sharpness.
  4. `Chr_04_Texture`: Paper grain, GLCM descriptors, LBP histograms.
  5. `Chr_05_Frequency`: 2D DCT, wavelet subband energy, periodogram spectral density.
  6. `Chr_06_Noise`: Sensor noise, PRNU fingerprints, JPEG artifacts, CFA demosaicing.
  7. `Chr_07_Metadata`: PDF structure, EXIF tags, XMP history, digital signatures.
  8. `Chr_08_ObjectGraph`: Topological relation graphs, spatial matrices, scene structures.
  9. `Chr_09_MicroDNA`: Sub-pixel Zernike edge profiles, halftone dot patterns (LPI/angle).
  10. `Chr_10_AISemantic`: Latent embeddings from Vision Foundation Models and Experts.

### 3.3 Genes (Functional Feature Group Level)
- **Purpose**: A cohesive functional unit within a chromosome measuring a specific physical phenomenon (e.g., `Gene_Typo_Kerning` within `Chr_02_Typography`).
- **Attributes**: Gene ID, Active/Deprecated Status, Required Modality, Extraction Engine Identifier.

### 3.4 Traits (Phenotypic Characteristic Level)
- **Purpose**: An individual observable characteristic exhibiting a specific forensic property (e.g., `Trait_Kerning_Pair_AV_Deviation`).
- **Attributes**: Trait ID, Human-readable description, Forensic Significance Level (FS1–FS4).

### 3.5 Measurements (Raw Sensor/Metric Level)
- **Purpose**: Raw, un-normalized measurement value extracted directly from document signals.
- **Data Structure**:
  ```protobuf
  message Measurement {
    string measurement_id = 1;
    double raw_value = 2;
    string unit = 3;  // e.g., "points", "pixels", "dB", "LPI"
    double SNR = 4;
    int64 sample_size = 5;
    google.protobuf.Timestamp measured_at = 6;
  }
  ```

### 3.6 Feature Vectors (Mathematical Embedding Level)
- **Purpose**: Continuous and discrete normalized representations derived from measurements, standardized against population parameters $\mathcal{M}_{\text{var}}(\mu, \sigma)$.
- **Mathematical Form**:
  $$v_i = \frac{m_i - \mu_i}{\sigma_i + \epsilon}$$

### 3.7 Evidence Objects (Forensic Signal Level)
- **Purpose**: Converts normalized feature vectors into formal forensic evidence parameters.
- **Attributes**: Log-Likelihood Ratio ($\text{LLR}$), Anomaly Intensity ($A \in [0, 1]$), Bounding Box Region ($[x_1, y_1, x_2, y_2]$).

### 3.8 Confidence Objects (Epistemic/Aleatoric Quality Level)
- **Purpose**: Quantifies measurement certainty and data quality.
- **Attributes**:
  - `aleatoric_variance`: Irreducible physical noise variance $\sigma_{\text{alea}}^2$.
  - `epistemic_variance`: Model/sample uncertainty variance $\sigma_{\text{epis}}^2$.
  - `measurement_precision`: Sensor resolution ratio.

### 3.9 Version Metadata (Provenance and Evolution Level)
- **Purpose**: Ensures complete cryptographic chain of custody and forward/backward compatibility.
- **Attributes**: Pipeline version, Schema Git commit, HSM signature block, SHA3-512 payload hash.

---

## 4. Extraction Pipeline Lifecycle

```
Raw Document Binary ──▶ Format Deconstruction ──▶ Modality Rendering ──▶ Chromosome Extraction (Parallel)
                                                                               │
Genome Root Assembly ◄── Evidence Fusion ◄── Confidence/Uncertainty Fitting ◄──┘
         │
         ▼
HSM Cryptographic Sealing ──▶ Immutable Storage (WORM / MinIO) + Qdrant Indexing
```

---

## 5. Storage and Binary Protocol Serialization

The Hierarchical Genome is serialized using Protocol Buffer v3 schemas (`proto/gdi/v2/genome_hierarchy.proto`) and persisted in WORM object storage.

```protobuf
syntax = "proto3";
package gdi.v2;

message HierarchicalGenome {
  VersionMetadata version_metadata = 1;
  string genome_id = 2;
  string tenant_id = 3;
  string document_hash_sha3 = 4;
  
  repeated Chromosome chromosomes = 5;
  RootCryptographicSeal seal = 6;
}

message Chromosome {
  string chromosome_id = 1;
  string name = 2;
  double chromosome_confidence = 3;
  repeated Gene genes = 4;
}

message Gene {
  string gene_id = 1;
  string name = 2;
  repeated Trait traits = 3;
}

message Trait {
  string trait_id = 1;
  Measurement measurement = 2;
  FeatureVector feature_vector = 3;
  EvidenceObject evidence = 4;
  ConfidenceObject confidence = 5;
}
```

---

## 6. Hierarchical Similarity & Distance Computation

Instead of computing distance over a flat vector, GDI v2 uses a **Hierarchical Tree Distance Metric**:

$$D_{\text{genome}}(G_A, G_B) = \sum_{k=1}^{10} w_{\text{chr}, k} \cdot D_{\text{chromosome}}\left( \text{Chr}_k^A, \text{Chr}_k^B \right)$$

where the chromosome distance $D_{\text{chromosome}}$ is the weighted aggregation of gene-level distances:

$$D_{\text{chromosome}}(\text{Chr}^A, \text{Chr}^B) = \sum_{g \in \text{Genes}} w_g \cdot d_{\text{trait}}\left( \text{Trait}_g^A, \text{Trait}_g^B \right)$$

---

## 7. Epistemic and Aleatoric Uncertainty Propagation

Uncertainty is propagated upward from Layer 5 (Measurements) to Layer 1 (Document Genome) using law of total variance:

$$\sigma_{\text{total}}^2 = \sigma_{\text{aleatoric}}^2 + \sigma_{\text{epistemic}}^2$$

For a parent node $P$ with child nodes $C_1, \dots, C_M$:

$$\sigma_{\text{epistemic}, P}^2 = \sum_{j=1}^M w_j^2 \cdot \sigma_{\text{epistemic}, C_j}^2 + 2 \sum_{i < j} w_i w_j \cdot \text{Cov}\left( C_i, C_j \right)$$

This prevents naive score averaging and preserves true physical uncertainty boundaries.

---

## 8. Failure Modes and Recovery Strategies

| Failure Mode | Impacted Layer | Root Cause | Recovery Strategy |
|--------------|----------------|------------|-------------------|
| Partial Chromosome Extraction Timeout | Layer 2 (Chromosomes) | Heavy GPU load or complex page | Mark Chromosome status as `DEGRADED`; re-weight remaining Chromosomes in tree distance |
| Missing Measurement Modality | Layer 5 (Measurements) | Low resolution input (<300 DPI) | Set `epistemic_variance = 1.0`; bypass sub-pixel trait computation |
| Protobuf Version Mismatch | Layer 9 (Version Metadata) | Older client loading v2.0 genome | Invoke Protobuf schema transformer fallback |

---

## 9. Verification and Testing Methodology

- **Hierarchy Invariant Test**: Assert that tree traversal from root to leaf visits exactly 9 distinct layers.
- **Determinism Test**: Re-running extraction on identical binaries must yield identical SHA3-512 tree node hashes across all 9 layers.
- **Uncertainty Propagation Verification**: Synthetic noise injection at Layer 5 must monotonically increase `epistemic_variance` at Layer 1.

---

*Previous: [37_Master_Context](../37_Master_Context/README.md)*
*Next: [39_Digital_Twin](../39_Digital_Twin/README.md)*
*Return to: [Master Index](../README.md)*
