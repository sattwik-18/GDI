# Document 05 — Genome Extraction Engine
## GDI: Forensic Characteristic Extraction Pipeline

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [04_Data_Flow], [06_Document_Reconstruction_Engine], [07_Layout_Analysis] through [15_Micro_DNA_Engine], [16_Multi_Model_AI], [17_Similarity_Engine], [34_AI_Model_Management]

---

## Table of Contents

1. [Engine Overview and Purpose](#1-engine-overview-and-purpose)
2. [Why Genome Extraction Exists](#2-why-genome-extraction-exists)
3. [Genome Architecture](#3-genome-architecture)
4. [Feature Space Definition](#4-feature-space-definition)
5. [Extraction Orchestration](#5-extraction-orchestration)
6. [Feature Confidence Modeling](#6-feature-confidence-modeling)
7. [Genome Serialization Format](#7-genome-serialization-format)
8. [Genome Sealing and Cryptographic Provenance](#8-genome-sealing-and-cryptographic-provenance)
9. [Natural Variation Integration](#9-natural-variation-integration)
10. [Pipeline Versioning](#10-pipeline-versioning)
11. [Genome Record Schema](#11-genome-record-schema)
12. [Performance Characteristics](#12-performance-characteristics)
13. [Failure Modes and Recovery](#13-failure-modes-and-recovery)
14. [Testing Strategy](#14-testing-strategy)
15. [Mathematical Foundation Summary](#15-mathematical-foundation-summary)

---

## 1. Engine Overview and Purpose

The Genome Extraction Engine (GEE) is the central coordination system for transforming a reconstructed document representation into a complete, structured, cryptographically sealed forensic genome.

The GEE does not perform extraction itself — it orchestrates the distributed execution of all individual forensic engines and assembles their outputs into a unified genome record.

**Inputs**:
- Reconstruction manifest (list of modality object keys from reconstruct-svc)
- Pipeline version specification
- Analysis tier (standard, enhanced, deep)

**Outputs**:
- Genome record (structured Protocol Buffer, stored in Object Storage)
- Genome vector (concatenated, normalized float32 array, stored in Qdrant)
- Per-engine status report
- Genome cryptographic seal

**Why the GEE exists as a separate service**:
The GEE separates the concern of "what features to extract" from "how to extract each feature." Individual engines define what they measure; the GEE defines the canonical genome structure and ensures completeness, consistency, and integrity across engine outputs. Without a central orchestrator, genome assembly would be distributed and error-prone.

---

## 2. Why Genome Extraction Exists

### 2.1 Alternative Approaches Considered

**Alternative 1: Direct Image Comparison**
Compare the submitted document image directly against the template image using pixel-level or perceptual hash comparison.

*Why rejected*: Direct image comparison cannot distinguish between:
- A faithful photocopy (authentic, different scan)
- A high-quality forgery with correctly reproduced layout
- A legitimate document from a different printer

It also cannot localize manipulations, provide forensic evidence, or account for natural variation.

**Alternative 2: Holistic AI Classifier**
Train a single deep learning model to classify documents as authentic or fraudulent.

*Why rejected*: A holistic classifier produces a black-box verdict without explainability. It is brittle to distribution shift (new document types, new printers). It cannot produce legally defensible evidence. It is vulnerable to adversarial examples. It fails to capture the multi-dimensional forensic richness required for government-grade verification.

**Alternative 3: Template Matching with Threshold**
Match the submitted document against stored template images using structural similarity indices (SSIM, PSNR).

*Why rejected*: SSIM and PSNR measure overall image quality, not forensic authenticity. A forged document with correct overall layout but subtle manipulation in one field would pass SSIM comparison with a high score. These metrics also don't decompose into forensically meaningful dimensions.

### 2.2 Why the Genome Approach

The genome approach provides:
1. **Decomposability**: Every component of the genome is independently meaningful and forensically interpretable
2. **Completeness**: The genome captures all forensically relevant dimensions
3. **Reproducibility**: The same document always produces the same genome (determinism)
4. **Comparability**: Genomes from different documents can be compared dimension by dimension
5. **Evolvability**: New forensic dimensions can be added to future genome versions without invalidating existing genomes

---

## 3. Genome Architecture

### 3.1 Genome Structure (Conceptual)

```
GENOME
├── HEADER
│   ├── genome_id: UUID
│   ├── job_id: UUID
│   ├── document_sha3_256: bytes[32]
│   ├── pipeline_version: "1.0.0"
│   ├── analysis_tier: STANDARD|ENHANCED|DEEP
│   ├── extraction_timestamp: datetime
│   └── engine_manifest: [{name, version, status}]
│
├── LAYER 1: LAYOUT GENOME
│   ├── Feature group: Margin measurements (12 features)
│   ├── Feature group: Column structure (8 features)
│   ├── Feature group: Line spacing (6 features)
│   ├── Feature group: Object bounding box statistics (20 features)
│   ├── Feature group: Whitespace distribution (15 features)
│   └── Feature group: Geometric alignment (12 features)
│
├── LAYER 2: TYPOGRAPHY GENOME
│   ├── Feature group: Font identification (30 features)
│   ├── Feature group: Glyph metrics (50 features)
│   ├── Feature group: Kerning statistics (40 features)
│   ├── Feature group: Baseline consistency (20 features)
│   ├── Feature group: Inter-word spacing (25 features)
│   └── Feature group: Rendering quality (25 features)
│
├── LAYER 3: RENDERING GENOME
│   ├── Feature group: Anti-aliasing profile (15 features)
│   ├── Feature group: Subpixel rendering (12 features)
│   ├── Feature group: Ink/toner spread (10 features)
│   ├── Feature group: Edge sharpness statistics (15 features)
│   └── Feature group: Rasterization artifacts (8 features)
│
├── LAYER 4: TEXTURE GENOME
│   ├── Feature group: Paper grain statistics (20 features)
│   ├── Feature group: Ink texture (15 features)
│   ├── Feature group: GLCM descriptors (13 features)
│   └── Feature group: LBP histograms (16 features)
│
├── LAYER 5: FREQUENCY GENOME
│   ├── Feature group: DCT coefficient statistics (20 features)
│   ├── Feature group: Wavelet energy bands (15 features)
│   └── Feature group: Periodogram features (10 features)
│
├── LAYER 6: NOISE GENOME
│   ├── Feature group: Sensor noise model (20 features)
│   ├── Feature group: JPEG artifact profile (15 features)
│   ├── Feature group: Compression history (10 features)
│   └── Feature group: CFA pattern (Bayer demosaicing artifacts) (8 features)
│
├── LAYER 7: METADATA GENOME
│   ├── Feature group: Creation metadata (15 features)
│   ├── Feature group: Software fingerprint (12 features)
│   ├── Feature group: Modification history (10 features)
│   └── Feature group: Device fingerprint (8 features)
│
├── LAYER 8: OBJECT RELATIONSHIP GENOME
│   ├── Feature group: Object graph topology (25 features)
│   ├── Feature group: Spatial relationship matrix (15 features)
│   └── Feature group: Object semantic consistency (12 features)
│
├── LAYER 9: MICRO-DNA GENOME
│   ├── Feature group: Sub-pixel edge profiles (40 features)
│   ├── Feature group: Micro-texture fingerprints (30 features)
│   ├── Feature group: Printing dot pattern statistics (20 features)
│   └── Feature group: Micro-detail preservation (15 features)
│
├── LAYER 10: AI SEMANTIC GENOME
│   ├── Feature group: Vision Foundation Model embeddings (512 dims)
│   ├── Feature group: Document structure AI features (128 dims)
│   └── Feature group: Semantic anomaly signatures (64 dims)
│
└── GENOME SEAL
    ├── feature_count: int
    ├── sha3_512_of_features: bytes[64]
    ├── ecdsa_p384_signature: bytes[96]
    ├── signing_key_id: string
    └── seal_timestamp: datetime
```

### 3.2 Genome Dimensions Summary

| Layer | Feature Groups | Feature Count (std) | Feature Count (deep) |
|-------|----------------|---------------------|----------------------|
| Layout | 6 | 73 | 120 |
| Typography | 6 | 190 | 300 |
| Rendering | 5 | 60 | 100 |
| Texture | 4 | 64 | 80 |
| Frequency | 3 | 45 | 60 |
| Noise | 4 | 53 | 90 |
| Metadata | 4 | 45 | 70 |
| Object Relationship | 3 | 52 | 100 |
| Micro-DNA | 4 | 105 | 200 |
| AI Semantic | 3 | 704 | 2048 |
| **Total** | **42** | **1,391** | **3,168** |

---

## 4. Feature Space Definition

### 4.1 Feature Taxonomy

Features are classified along two independent axes:

**Extraction Method**:
- **M1: Direct Measurement**: Directly measured from the document signal (e.g., margin width in points)
- **M2: Statistical Aggregate**: Statistical summary over a population of measurements (e.g., mean glyph height, std dev of kerning)
- **M3: Transform Coefficient**: Derived via mathematical transform (e.g., DCT coefficient at frequency k)
- **M4: AI-Derived**: Derived from a neural network's internal representation (e.g., ViT embedding)
- **M5: Graph Property**: Derived from graph structure analysis (e.g., object graph diameter)

**Forensic Significance Level**:
- **FS1: Critical**: Highly discriminative between authentic and manipulated documents; high weight in fusion
- **FS2: Major**: Moderately discriminative; standard weight in fusion
- **FS3: Supporting**: Low discriminative power alone; only used in ensemble
- **FS4: Contextual**: Provides context but not direct evidence of manipulation; no weight in authenticity fusion

### 4.2 Feature Vector Representation

The genome vector (used for Qdrant storage and ANN search) is produced by:

1. **Normalization**: Each feature F is normalized using its natural variation model:
   ```
   F_normalized = (F_value - μ_F) / σ_F
   ```
   For features without natural variation data (first document of a type), standardization is performed using feature-type population statistics from the pre-training corpus.

2. **Concatenation**: All normalized features are concatenated in a canonical order defined by the pipeline version spec.

3. **L2 normalization**: The concatenated vector is L2-normalized to unit length (enabling cosine similarity comparison in Qdrant).

4. **Dimensional reduction** (optional, Enhanced/Deep tiers): PCA or UMAP projection to a canonical embedding space of 1,024 dimensions for efficient ANN search while maintaining the full-dimensional genome for precise comparison.

---

## 5. Extraction Orchestration

### 5.1 Orchestration State Machine

```
GENOME_ORCHESTRATOR State Machine

State: DISPATCHING
  ─ Receive reconstruction manifest
  ─ Load pipeline version spec (defines active engines and their configurations)
  ─ For each active engine:
    * Create Redis counter entry: genome:{job_id}:pending = N (N = number of engines)
    * Dispatch task to Kafka
  ─ Set orchestration timeout timer in Redis (TTL = max_engine_time × 1.5)
  ─ Transition to: COLLECTING

State: COLLECTING
  ─ On each engine result arrival (Kafka consumer):
    * Validate result schema
    * Store result in Redis (key: genome:{job_id}:result:{engine_name})
    * Decrement pending counter: DECR genome:{job_id}:pending
    * If counter == 0: transition to ASSEMBLING
  ─ On timeout:
    * Identify engines that have not responded
    * Mark them as TIMEOUT
    * If minimum engine quorum met: transition to ASSEMBLING
    * Else: transition to FAILED

State: ASSEMBLING
  ─ Load all engine results from Redis
  ─ Validate each result against engine schema (protobuf validation)
  ─ For each engine with status TIMEOUT or FAILED:
    * Mark corresponding features as MISSING
    * Decrement genome completeness score
  ─ Build genome record (structured)
  ─ Compute genome vector
  ─ Transition to: SEALING

State: SEALING
  ─ Serialize genome record to Protocol Buffer
  ─ Compute SHA3-512 of serialized bytes
  ─ Request ECDSA P-384 signature from HSM via PKCS#11
  ─ Attach seal to genome record
  ─ Store sealed genome record in Object Storage
  ─ Store genome vector in Qdrant
  ─ Transition to: COMPLETED

State: FAILED
  ─ If quorum not met:
    * Store partial genome with failure context
    * Route job to human review with EXTRACTION_FAILURE context
    * Emit alert
```

### 5.2 Engine Quorum Requirements

| Analysis Tier | Minimum Engine Quorum | Required Engines (cannot fail) |
|--------------|----------------------|-------------------------------|
| Standard | 10 of 12 | metadata-engine, layout-engine |
| Enhanced | 14 of 16 | metadata-engine, layout-engine, typography-engine |
| Deep | 18 of 20 | metadata-engine, layout-engine, typography-engine, ai-engine |

Quorum failure (below minimum) routes the job to human review with PARTIAL_GENOME context, clearly indicating which engines failed and what forensic coverage is missing.

---

## 6. Feature Confidence Modeling

### 6.1 Per-Feature Confidence

Every extracted feature value is accompanied by a confidence score (0.0–1.0) representing the reliability of the measurement. Confidence is computed differently for each extraction method:

**M1 (Direct Measurement) Confidence**:
```
confidence = 1.0 - (measurement_noise / (signal_magnitude + ε))
```
Where `measurement_noise` is estimated from the local signal variance and `signal_magnitude` is the feature value magnitude.

**M2 (Statistical Aggregate) Confidence**:
```
confidence = 1.0 - (1.0 / √N) × cv
```
Where N is the number of sample measurements and cv is the coefficient of variation. More samples and lower variation → higher confidence.

**M3 (Transform Coefficient) Confidence**:
```
confidence = SNR_dB / (SNR_dB + SNR_threshold)
```
Based on the signal-to-noise ratio in the transform domain at the measured frequency.

**M4 (AI-Derived) Confidence**:
Uses the AI model's output uncertainty (MC Dropout for neural networks, or calibrated temperature scaling applied to logits).

**M5 (Graph Property) Confidence**:
```
confidence = 1.0 if graph_is_complete else 
             (edges_detected / expected_edges_for_document_type)
```

### 6.2 Genome-Level Confidence

The overall genome confidence is computed as a weighted harmonic mean of individual feature confidences, weighted by the forensic significance level (FS1–FS4):

```
Genome_Confidence = (Σ FS_weight_i) / (Σ FS_weight_i / confidence_i)
```

A genome with many low-confidence features produces a low genome confidence, which propagates to the final report's confidence interval.

---

## 7. Genome Serialization Format

### 7.1 Primary Format: Protocol Buffer

The canonical genome format is Protocol Buffer v3 (protobuf). Protocol Buffer is chosen over JSON or MessagePack because:
- **Deterministic serialization**: Proto3 with `deterministic=True` produces byte-identical serialization for identical data structures (critical for reproducible hashing)
- **Typed schema**: The schema is formally defined and versioned (proto schema evolution rules)
- **Compact**: ~5× smaller than equivalent JSON (important for genomes with 3,000+ float64 features)
- **Fast**: ~10× faster serialization/deserialization than JSON for numeric data

**Note**: JSON representation is also generated and stored as a human-readable companion to the binary proto, but the proto is the canonical authoritative format for hashing and signing.

### 7.2 Genome File Size Estimates

| Analysis Tier | Proto Size | JSON Size |
|--------------|-----------|----------|
| Standard | ~85 KB | ~400 KB |
| Enhanced | ~140 KB | ~650 KB |
| Deep | ~350 KB | ~1.6 MB |

---

## 8. Genome Sealing and Cryptographic Provenance

### 8.1 Sealing Process

The genome sealing process establishes cryptographic provenance:

```
1. Serialize genome_payload = proto.SerializeToString(genome_record)
   (deterministic=True)

2. Compute sha3_512_hash = SHA3-512(genome_payload)

3. Request HSM signature:
   signature = HSM.sign(
     data=sha3_512_hash,
     key_id=current_forensic_signing_key_id,
     algorithm=ECDSA_P384_SHA384
   )

4. Construct genome_seal = {
     sha3_512_hash: bytes[64],
     ecdsa_signature: bytes[96],
     signing_key_id: string,
     signing_cert_fingerprint: bytes[32],
     seal_timestamp: RFC3339_nanosecond,
     pipeline_version: string
   }

5. Attach genome_seal to genome_record.seal
6. Re-serialize (with seal)
7. Store final sealed genome
```

### 8.2 Signature Verification

Any party with the GDI forensic signing certificate's public key can verify a genome's authenticity:

```
1. Extract genome_seal from genome record
2. Re-serialize genome_payload (excluding the seal field)
3. Recompute sha3_512_hash
4. Verify: ECDSA_VERIFY(signature, sha3_512_hash, public_key)
5. Verify: seal_timestamp is within expected range
6. Verify: pipeline_version matches declared version
```

This verification can be performed offline, making genome verification independent of GDI system access.

---

## 9. Natural Variation Integration

### 9.1 Variation Model Storage

The natural variation model for a template is stored alongside the template genome:

```
template_variation_model = {
  template_id: UUID,
  pipeline_version: string,
  sample_count: int,
  features: {
    feature_name: {
      mu: float64,           // mean across authentic samples
      sigma: float64,        // standard deviation
      min: float64,          // minimum observed
      max: float64,          // maximum observed
      percentile_5: float64,
      percentile_95: float64,
      distribution_type: NORMAL|LOG_NORMAL|UNIFORM|EMPIRICAL
    }
  }
}
```

### 9.2 Variation Model Update Protocol

When a new authentic sample is added to a template:
1. Extract the genome of the authentic sample
2. For each feature: update running mean and variance using Welford's online algorithm
3. Update the variation model record in Object Storage (new version)
4. Update the template record in PostgreSQL (sample_count, variation_model_version)
5. Log the update as an audit event

**Welford's Online Algorithm** is used because:
- It is numerically stable for computing variance incrementally
- It requires O(1) memory (no need to store all sample values)
- It is suitable for streaming updates without reprocessing the entire sample set

---

## 10. Pipeline Versioning

### 10.1 Version Compatibility Matrix

Pipeline versions are compatible for genome comparison if:
- MAJOR versions are identical (breaking changes affect feature definitions)
- MINOR versions are compatible in an additive direction (newer MINOR can compare against older MINOR; new features are treated as missing in old genomes)
- PATCH versions are always compatible

**Formal compatibility rule**:
```
compatible(v1, v2) = (v1.MAJOR == v2.MAJOR) AND 
                     NOT (v1.MINOR > v2.MINOR AND 
                          v1 uses features deprecated between v2.MINOR and v1.MINOR)
```

### 10.2 Version Changelog Requirement

Every pipeline version change must document:
- Features added, modified, or removed
- Algorithm changes affecting feature values
- Compatibility classification (MAJOR/MINOR/PATCH)
- Migration path for existing genomes (if applicable)

---

## 11. Genome Record Schema

Full protobuf schema definition (excerpt — canonical definition in `proto/genome/v1/genome.proto`):

```protobuf
syntax = "proto3";
package gdi.genome.v1;

message GenomeRecord {
  GenomeHeader header = 1;
  LayoutGenome layout = 2;
  TypographyGenome typography = 3;
  RenderingGenome rendering = 4;
  TextureGenome texture = 5;
  FrequencyGenome frequency = 6;
  NoiseGenome noise = 7;
  MetadataGenome metadata = 8;
  ObjectRelationshipGenome object_graph = 9;
  MicroDNAGenome micro_dna = 10;
  AISemanticGenome ai_semantic = 11;
  GenomeSeal seal = 12;
}

message GenomeHeader {
  string genome_id = 1;
  string job_id = 2;
  bytes document_sha3_256 = 3;
  string pipeline_version = 4;
  AnalysisTier analysis_tier = 5;
  google.protobuf.Timestamp extraction_timestamp = 6;
  repeated EngineStatus engine_manifest = 7;
  float genome_confidence = 8;
  int32 feature_count = 9;
  bool is_template_genome = 10;
  string template_id = 11;  // populated if is_template_genome
}

message Feature {
  string feature_id = 1;
  double value = 2;
  float confidence = 3;
  string unit = 4;
  ExtractionMethod method = 5;
  ForensicSignificance significance = 6;
  map<string, string> metadata = 7;
}

message FeatureVector {
  repeated float values = 1;  // normalized float32 for vector operations
}

message AnomalyRegion {
  float x = 1;
  float y = 2;
  float width = 3;
  float height = 4;
  string feature_id = 5;
  float deviation_zscore = 6;
  float confidence = 7;
}

message GenomeSeal {
  bytes sha3_512_hash = 1;
  bytes ecdsa_p384_signature = 2;
  string signing_key_id = 3;
  bytes signing_cert_sha256 = 4;
  google.protobuf.Timestamp seal_timestamp = 5;
  string pipeline_version = 6;
}
```

---

## 12. Performance Characteristics

### 12.1 Extraction Throughput

| Stage | Wall Time (P50) | Wall Time (P95) | Bottleneck |
|-------|-----------------|-----------------|------------|
| Task dispatch (all engines) | 50 ms | 100 ms | Kafka producer |
| Layout Engine | 2.5 s | 6 s | CPU (convolution) |
| Typography Engine | 8 s | 18 s | CPU (glyph rendering) |
| Rendering Engine | 3 s | 8 s | CPU (subpixel analysis) |
| Texture Engine | 2 s | 5 s | CPU (GLCM computation) |
| Frequency Engine | 1.5 s | 4 s | CPU (FFT) |
| Noise Engine | 4 s | 10 s | CPU (noise estimation) |
| Metadata Engine | 0.5 s | 2 s | I/O (file parsing) |
| Object Graph Engine | 5 s | 15 s | CPU (graph construction) |
| Micro-DNA Engine | 15 s | 35 s | CPU (sub-pixel analysis) |
| AI Engine | 8 s | 20 s | GPU (inference) |
| Genome Assembly | 0.5 s | 1 s | I/O + crypto |
| **Total (parallel, standard)** | **~25 s** | **~55 s** | AI + Typography |

Note: All engines run in parallel. Total wall time is bounded by the slowest engine (Typography or Micro-DNA for standard tier), not the sum.

### 12.2 Memory Usage

| Engine | Peak RSS |
|--------|---------|
| Layout | 1.2 GB |
| Typography | 2.1 GB |
| Rendering | 1.5 GB |
| Texture | 1.0 GB |
| Frequency | 0.8 GB |
| Noise | 1.2 GB |
| Metadata | 0.3 GB |
| Object Graph | 2.0 GB |
| Micro-DNA | 3.5 GB |
| AI Engine | 12 GB (model loaded) |
| Genome Orchestrator | 0.5 GB |

---

## 13. Failure Modes and Recovery

| Failure Mode | Probability | Impact | Recovery |
|--------------|-------------|--------|---------|
| Engine pod crash during extraction | Low | Feature group missing | Pod restarts; genome marked partial; job continues if quorum met |
| Engine timeout (slow document) | Medium | Feature group missing | Timeout after 2× P95 processing time; marked TIMEOUT in genome |
| Object Storage write failure | Very Low | Genome not stored | Retry 3× with exponential backoff; job suspended on persistent failure |
| HSM signing failure | Very Low | Genome not sealed | Retry 3×; if persistent: genome stored unsigned with alert; human review required |
| Kafka consumer lag (engine overloaded) | Low | Job processing delayed | Auto-scaling triggers additional engine pods; no data loss |
| Genome orchestrator failure | Very Low | In-flight job state lost | Orchestrator is stateless (state in Redis + Kafka); new pod resumes from Kafka offset |
| Redis failure (counter tracking) | Very Low | In-flight job coordination lost | Redis replica promotion (<1s); counter reconstructed from Kafka if needed |

---

## 14. Testing Strategy

### 14.1 Unit Tests

Each forensic engine has a dedicated unit test suite verifying:
- Correct feature value for known test documents (regression tests)
- Correct confidence score computation
- Correct handling of edge cases (blank document, corrupted section, missing data)
- Determinism: same input → same output (100 repetitions)

### 14.2 Integration Tests

Genome Extraction integration tests:
- Full pipeline run on reference document corpus (50 authentic, 50 known forgeries per document type)
- Verify genome completeness (no missing features for successful extractions)
- Verify genome seal validity
- Verify genome vector dimensions and normalization
- Verify correct routing on engine failure scenarios

### 14.3 Performance Tests

- Throughput benchmark: 100 concurrent jobs; verify P95 wall time within SLA
- Memory leak detection: 1,000 sequential jobs; verify memory returns to baseline after each
- Engine failure injection: verify correct quorum behavior and routing

### 14.4 Adversarial Tests

- Gradual manipulation test: progressively manipulate one region of a known authentic document; verify anomaly score increases monotonically
- Multi-engine evasion test: craft documents that manipulate one forensic dimension; verify divergence detection
- Edge case corpus: blank pages, corrupted PDFs, encrypted PDFs, zero-byte documents, documents exceeding size limits

---

## 15. Mathematical Foundation Summary

### 15.1 Core Mathematical Structures

**Feature vector space**: ℝ^D where D = 1,391 (standard) or 3,168 (deep). Each dimension is a real-valued forensic measurement, normalized to zero mean and unit variance relative to the authentic population.

**Genome similarity**: Cosine similarity in normalized feature space:
```
cos(G₁, G₂) = (G₁ · G₂) / (|G₁| × |G₂|)
```
(Note: after L2 normalization, this equals the dot product)

**Feature confidence**: Modeled as a random variable C_F ~ Beta(α, β) where α and β are estimated from measurement precision characteristics. The point estimate is E[C_F] = α/(α+β).

**Genome confidence**: Weighted harmonic mean of individual feature confidences:
```
C_genome = (Σ w_i) / (Σ w_i / C_i)
```
where w_i is the forensic significance weight of feature i.

**Natural variation model**: Per-feature Gaussian N(μ_F, σ_F²) estimated by maximum likelihood from authentic sample population. Features with non-Gaussian distributions (e.g., count data) use appropriate distributions (Poisson, Log-Normal) as identified by goodness-of-fit testing.

**Z-score comparison**:
```
Z_F = |value_F(submitted) - μ_F| / σ_F
```

This Z-score is the primary input to the similarity engine (see [17_Similarity_Engine]).

---

*Previous: [04_Data_Flow](../04_Data_Flow/README.md)*
*Next: [06_Document_Reconstruction_Engine](../06_Document_Reconstruction_Engine/README.md)*
*Return to: [Master Index](../README.md)*
