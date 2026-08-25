# Document 04 — Data Flow
## GDI: End-to-End Data Movement and Lifecycle

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [03_System_Architecture], [05_Genome_Extraction_Engine], [21_Backend_Architecture], [23_Database_Architecture], [25_Object_Storage], [27_Cryptography]

---

## Table of Contents

1. [Data Flow Overview](#1-data-flow-overview)
2. [Document Ingestion Flow](#2-document-ingestion-flow)
3. [Template Enrollment Flow](#3-template-enrollment-flow)
4. [Forensic Analysis Flow (Standard Tier)](#4-forensic-analysis-flow-standard-tier)
5. [Genome Extraction Fan-Out Flow](#5-genome-extraction-fan-out-flow)
6. [Intelligence Pipeline Flow](#6-intelligence-pipeline-flow)
7. [Report Generation Flow](#7-report-generation-flow)
8. [Human Review Flow](#8-human-review-flow)
9. [Audit Data Flow](#9-audit-data-flow)
10. [Data Lifecycle and Retention](#10-data-lifecycle-and-retention)
11. [Data Classification Taxonomy](#11-data-classification-taxonomy)
12. [Error Flow and Dead Letter Handling](#12-error-flow-and-dead-letter-handling)
13. [Cross-Tenant Data Isolation](#13-cross-tenant-data-isolation)
14. [Data Flow Diagrams (Detailed)](#14-data-flow-diagrams-detailed)

---

## 1. Data Flow Overview

GDI processes two primary document flows: **Template Enrollment** (establishing a reference genome) and **Verification Analysis** (comparing a submitted document against a template genome).

Both flows share the document ingestion, forensic processing, and genome extraction sub-flows. They diverge at the comparison and verdict stages.

### 1.1 Primary Data Artifact Types

| Artifact | Description | Format | Mutability |
|----------|-------------|--------|------------|
| Document Binary | Raw submitted document | As submitted (PDF, TIFF, etc.) | Immutable after ingestion |
| Document Rendering | Normalized raster representation | PNG (16-bit TIFF for high-res) | Immutable after generation |
| Document Modalities | Vector, color channel, grayscale decompositions | Various | Immutable after generation |
| Genome Record | Structured forensic feature set | Protocol Buffer / JSON | Immutable after sealing |
| Genome Vector | Dense float32 embedding for ANN search | Float32 array | Immutable after sealing |
| Engine Result | Per-engine analysis output | Protocol Buffer / JSON | Immutable after generation |
| Fusion Result | Aggregated engine scores | Protocol Buffer / JSON | Immutable after generation |
| Verdict Record | Final decision engine output | Protocol Buffer / JSON | Immutable after generation |
| Heatmap | Spatial anomaly visualization | PNG | Immutable after generation |
| Forensic Report (JSON) | Machine-readable report | JSON (schema versioned) | Immutable after generation |
| Forensic Report (PDF) | Human-readable report | PDF/A-3 | Immutable after generation |
| Evidence Package | Complete sealed forensic evidence | ZIP + signature | Immutable after sealing |
| Audit Record | Immutable event log entry | JSON (append-only) | Immutable, never deleted |

---

## 2. Document Ingestion Flow

### 2.1 Step-by-Step Ingestion

**Trigger**: Client submits document via REST API POST `/v1/jobs`

```
Step 1: API Gateway
  ─ TLS termination (TLS 1.3)
  ─ JWT token validation (signature check, expiry, scope: 'write:jobs')
  ─ Rate limit check (sliding window, per tenant)
  ─ DDoS protection (connection rate limits)
  ─ Request routing to ingest-svc

Step 2: Ingest Service (ingest-svc)
  ─ Parse multipart request
  ─ Validate Content-Type header
  ─ Enforce file size limit (per tier)
  ─ Stream document binary to temporary buffer (in-memory or /dev/shm)
  ─ Compute SHA3-256 hash of raw binary (pre-normalization)
  ─ Generate job ID (UUID v4, cryptographically random)
  ─ Generate ingestion timestamp (UTC, nanosecond precision)
  ─ Write document binary to Object Storage (bucket: gdi-documents-raw)
    * Object key: {tenant_id}/{date}/{job_id}/original.{ext}
    * Object metadata: job_id, sha3_256, ingested_at, content_type, size_bytes, tenant_id
    * SSE-KMS encryption enabled
    * Object Lock: GOVERNANCE mode, retention 7 years
  ─ Write initial job record to PostgreSQL:
    * Table: jobs.job_records
    * Fields: job_id, tenant_id, status='INGESTED', sha3_256, ingested_at,
              template_id, analysis_tier, context_metadata (JSONB),
              pipeline_version
  ─ Produce job.submitted event to Kafka topic: gdi.jobs.submitted
    * Payload: {job_id, tenant_id, document_object_key, sha3_256,
                template_id, analysis_tier, pipeline_version}
  ─ Write ingestion audit record to PostgreSQL:
    * Table: audit.events
    * Fields: event_id, event_type='JOB_INGESTED', job_id, tenant_id,
              actor_id (from JWT), timestamp, sha3_256
  ─ Return HTTP 202 Accepted with {job_id, status_url, estimated_completion}

Step 3: Malware Scanning (async, parallel to step 2)
  ─ Malware scan service reads document from Object Storage
  ─ ClamAV scan executed in sandboxed environment
  ─ If clean: produce job.scan_passed event → pipeline continues
  ─ If malware detected:
    * Update job status → 'REJECTED_MALWARE'
    * Move object to quarantine bucket (access restricted)
    * Emit security alert to SIEM
    * Notify submitter via webhook (code: MALWARE_DETECTED, no details)
    * Log security event with full context (internal only)
```

### 2.2 Ingestion Data Guarantees

- Document binary stored before job record created (storage failure → retry upload; no orphan job record)
- Job record created before Kafka event produced (Kafka failure → retry event publication; idempotent with job_id as deduplication key)
- All ingestion steps are logged to audit before the HTTP response is returned

---

## 3. Template Enrollment Flow

### 3.1 Step-by-Step Template Enrollment

**Trigger**: Authorized user submits template via REST API POST `/v1/templates`

```
Step 1: API Gateway
  ─ JWT validation with scope 'write:templates' (elevated role required)
  ─ Rate limit check (template uploads are less frequent; separate limit)

Step 2: Template Service (template-svc)
  ─ Parse multipart request
  ─ Validate template metadata fields
  ─ Compute SHA3-256 hash of document binary
  ─ Generate template_id (UUID v4)
  ─ Store document binary in Object Storage
    * Bucket: gdi-templates (separate bucket, higher redundancy)
    * Object key: {tenant_id}/templates/{template_id}/v{version}/original.{ext}
    * Object Lock: COMPLIANCE mode, retention indefinite
  ─ Write template record to PostgreSQL (status='ENROLLING')
  ─ Produce template.enrollment.started event to Kafka
  ─ Return HTTP 202 with {template_id, enrollment_status_url}

Step 3: Genome Extraction (identical to analysis flow, §4, Steps 3–7)
  ─ Full genome extraction pipeline runs on template document
  ─ Genome stored in Object Storage and Qdrant

Step 4: Template Genome Sealing
  ─ Genome record assembled and cryptographically signed:
    * Payload: {template_id, genome_values, pipeline_version, sha3_256, timestamp}
    * Signature: ECDSA P-384 using HSM-backed private key
    * Signature stored alongside genome record
  ─ Template record updated in PostgreSQL (status='ACTIVE')
  ─ Produce template.enrollment.completed event

Step 5: Natural Variation Model Initialization
  ─ Single-sample variation model initialized (σ_F = 0 for all features)
  ─ Template enrollment metadata recorded:
    * sample_count=1, variation_model_confidence='LOW'
  ─ System requests additional authentic samples via notification
```

---

## 4. Forensic Analysis Flow (Standard Tier)

This describes the end-to-end flow for a submitted verification job:

```
[Kafka: gdi.jobs.submitted]
         │
         ▼
Job Orchestrator (job-orchestrator)
  ─ Consume job.submitted event
  ─ Read job record from PostgreSQL
  ─ Load template genome record from Object Storage
  ─ Update job status → 'RECONSTRUCTION'
  ─ Dispatch reconstruction task to reconstruct-svc (gRPC)

         │
         ▼
Document Reconstruction Engine (reconstruct-svc)
  ─ Read document binary from Object Storage
  ─ Validate format
  ─ Normalize document:
    * Detect and correct skew (Hough transform, deskewing)
    * Detect and correct perspective distortion (homography estimation)
    * Normalize color space (sRGB linearization)
    * Remove border artifacts
  ─ Render document at analysis DPI:
    * Standard tier: 300 DPI
    * Enhanced tier: 400 DPI
    * Deep tier: 600 DPI
  ─ Generate analysis modalities:
    * Rendered RGB raster (main analysis image)
    * Grayscale luminance channel
    * CIE-Lab color representation
    * For PDF: vector object graph (pdf2xml + custom parser)
  ─ Store all modalities in Object Storage
    * Object key: {tenant_id}/{date}/{job_id}/reconstructed/{modality}.{ext}
  ─ Return reconstruction_manifest (list of modality object keys) to Job Orchestrator

         │
         ▼
Job Orchestrator
  ─ Receive reconstruction_manifest
  ─ Update job status → 'EXTRACTING'
  ─ Dispatch genome extraction tasks to all active engines via Kafka
    * One message per engine per modality required by that engine
    * Kafka topic: gdi.jobs.{job_id}.tasks

         │ (Fan-out via Kafka)
         ▼
[All Forensic Engines run in parallel - see §5]

         │ (Fan-in via Kafka)
         ▼
Genome Orchestrator
  ─ Collect engine results from Kafka: gdi.jobs.{job_id}.results
  ─ Wait for all engines (with configurable timeout per engine)
  ─ Handle missing results:
    * Timed-out engines: marked as 'FAILED' in genome record
    * Failed engines: marked with error context
  ─ Assemble genome record:
    * All feature values
    * Per-feature confidence values
    * Per-engine status (SUCCESS/FAILED/TIMEOUT)
    * Pipeline version
    * Analysis timestamp
  ─ Compute genome vector (concatenate and normalize feature vectors)
  ─ Store genome record in Object Storage (Protocol Buffer format)
  ─ Store genome vector in Qdrant
    * Collection: tenant_{tenant_id}_genomes
    * Payload: {job_id, document_type, template_id, analysis_tier, timestamp}
  ─ Produce genome.assembled event → Intelligence Layer
```

---

## 5. Genome Extraction Fan-Out Flow

Each forensic engine follows this identical data flow pattern:

```
Kafka Consumer (engine-specific group)
  ─ Consume task from: gdi.jobs.{job_id}.tasks
    * Filter: engine_name == '{this_engine}'
  ─ Read required modalities from Object Storage
  ─ Run extraction algorithm (see individual engine documents)
  ─ Produce engine result to: gdi.jobs.{job_id}.results
    * Payload: {
        engine_name: string,
        job_id: UUID,
        status: SUCCESS|FAILED|PARTIAL,
        features: {feature_name: {value, confidence, metadata}},
        anomaly_regions: [{bbox, feature_name, deviation, confidence}],
        spatial_anomaly_map: object_key (optional),
        processing_time_ms: int,
        error: string (if failed)
      }
  ─ Store any spatial artifacts (intermediate maps) in Object Storage
  ─ Emit engine.completed audit event
```

**Fan-In Coordination**:
- The Genome Orchestrator uses a Redis counter per job (key: `genome:{job_id}:pending_engines`)
- Each engine completion decrements the counter
- When counter reaches 0 (or timeout fires), genome assembly begins
- Redis key has TTL of 2× the maximum expected engine processing time

---

## 6. Intelligence Pipeline Flow

```
[Kafka: gdi.jobs.genome.assembled]
         │
         ▼
Similarity Service (similarity-svc)
  ─ Read genome record (submitted document) from Object Storage
  ─ Read template genome record from Object Storage
    * Template genome includes natural variation model (μ_F, σ_F per feature)
  ─ For each feature F in genome:
    * Compute Z-score: Z_F = |value_F(submitted) - μ_F(template)| / σ_F(template)
    * Compute normalized similarity: S_F = exp(-Z_F² / 2) [Gaussian similarity]
    * Compute weighted similarity: WS_F = S_F × weight_F
  ─ Compute per-engine similarity:
    * SE_engine = mean(WS_F for all F in engine)
  ─ Compute overall similarity:
    * S_overall = weighted mean of SE_engine scores (weights from fusion config)
  ─ Compute anomaly features:
    * For each engine: AE_engine = features where Z_F > anomaly_threshold
    * Rank anomalies by Z-score (top-K reported)
  ─ Produce similarity result to: gdi.jobs.{job_id}.similarity

         │
         ▼
Fusion Service (fusion-svc)
  ─ Read all engine results from Object Storage
  ─ Read similarity result
  ─ Compute evidence weights using Bayesian reliability model:
    * Weight_engine = confidence_engine × reliability_prior_engine × (1 - failure_flag_engine)
    * Reliability priors from engine performance data in PostgreSQL
  ─ Compute engine divergence score:
    * D = variance(SE_engine values) / mean(SE_engine values)
    * High divergence → lower confidence, potentially higher anomaly signal
  ─ Apply evidence hierarchy weighting:
    * L1 evidence (cryptographic): weight multiplier 3.0
    * L2 evidence (structural): weight multiplier 2.0
    * L3 evidence (statistical): weight multiplier 1.5
    * L4 evidence (AI-inferred): weight multiplier 1.0
    * L5 evidence (heuristic): weight multiplier 0.5
  ─ Compute fused scores:
    * Authenticity_raw = Bayesian fusion of weighted engine authenticity signals
    * Anomaly_fused = weighted combination of per-engine anomaly scores
    * Confidence_raw = f(engine_agreement, sample_count, engine_success_rate)
  ─ Produce fusion result to: gdi.jobs.{job_id}.fusion

         │
         ▼
Decision Service (decision-svc)
  ─ Read fusion result
  ─ Apply calibration model:
    * Platt scaling (sigmoid calibration) applied to raw authenticity score
    * Calibration model trained on verified ground-truth corpus
  ─ Apply tenant-specific threshold configuration:
    * Read thresholds from Redis cache (fallback: PostgreSQL)
  ─ Compute confidence interval (95% credible interval via bootstrapping)
  ─ Assign verdict category:
    * AUTHENTIC_HIGH_CONFIDENCE: score > high_threshold AND confidence > confidence_threshold
    * LIKELY_AUTHENTIC: score > auto_pass_threshold
    * INDETERMINATE: score in human_review_band
    * LIKELY_FRAUDULENT: score < auto_reject_threshold
    * FRAUDULENT_HIGH_CONFIDENCE: score < low_threshold AND confidence > confidence_threshold
  ─ Determine routing:
    * If verdict in {INDETERMINATE}: route to human review queue
    * Else: auto-verdict
  ─ Write verdict record to PostgreSQL (jobs.verdict_records)
  ─ Update job status → 'VERDICT_ISSUED'
  ─ Produce verdict.issued event to: gdi.jobs.{job_id}.verdict

         │
         ▼
[Output Layer — see §7]
```

---

## 7. Report Generation Flow

```
[Kafka: gdi.jobs.verdict.issued]
         │
         ├──────────────────────────────────────────────┐
         ▼                                              ▼
Heatmap Generator (heatmap-svc)                Report Generator (report-svc)
  ─ Read spatial anomaly maps from                ─ Read all job artifacts:
    all engines                                     * Genome record
  ─ Composite into combined heatmap                 * Engine results
  ─ Apply colormap (cool-to-warm)                   * Similarity result
  ─ Generate per-engine heatmaps                    * Fusion result
  ─ Store PNGs in Object Storage                    * Verdict record
  ─ Produce heatmaps.generated event               * Heatmap object keys
                                                  ─ Generate explainability report:
                                                    * Run SHAP analysis on fusion inputs
                                                    * Rank top-20 contributing features
                                                  ─ Generate JSON report
                                                    (schema: gdi-forensic-report-v1.0)
                                                  ─ Generate PDF report
                                                    (template: forensic-report-v1.0.html)
                                                  ─ Store both in Object Storage
                                                  ─ Produce reports.generated event

         ├──────────────────────────────────────────────┘
         ▼
Evidence Packager (evidence-packager-svc)
  ─ Wait for: heatmaps.generated AND reports.generated
  ─ Assemble evidence package:
    * Original document binary
    * All reconstructed modalities
    * All engine results
    * Genome record
    * Heatmaps (all variants)
    * JSON forensic report
    * PDF forensic report
    * Audit log for this job (extracted from PostgreSQL)
  ─ Create ZIP archive with canonical directory structure
  ─ Compute SHA3-512 hash of ZIP archive
  ─ Sign the hash with HSM-backed ECDSA P-384 key
    * Produce: {archive_hash, signature, public_key_cert, timestamp}
  ─ Store ZIP archive in Object Storage (WORM bucket)
  ─ Store signature block in Object Storage
  ─ Update job status → 'COMPLETED'
  ─ Write completion audit record
  ─ Trigger webhook notification (if configured)
  ─ Produce job.completed event
```

---

## 8. Human Review Flow

```
[Decision Service: route_to_review = true]
         │
         ▼
Job Orchestrator
  ─ Update job status → 'PENDING_REVIEW'
  ─ Create review case record in PostgreSQL:
    * case_id, job_id, assigned_to (if auto-assignment configured),
      created_at, priority (from anomaly score), deadline (SLA-based)
  ─ Produce review.case.created event
  ─ Send notification to reviewer(s) via notification-svc

         │
         ▼
Human Reviewer (via review-ui-svc)
  ─ Access review case via authenticated web interface
  ─ Interface presents:
    * Document image (submitted)
    * Template image (reference)
    * Side-by-side comparison viewer
    * Anomaly heatmaps with opacity control
    * Per-engine scores table
    * Explainability feature list
    * Full forensic chain of custody
    * Pre-filled automated verdict (NOT binding)
  ─ Reviewer performs analysis
  ─ Reviewer submits verdict:
    * Decision: AUTHENTIC | FRAUDULENT | INDETERMINATE | NEEDS_EXPERT
    * Confidence: LOW | MEDIUM | HIGH
    * Evidence annotations: {region, annotation, feature_type}
    * Notes: free text
    * If escalating: NEEDS_EXPERT → assign to senior reviewer

         │
         ▼
Review Service
  ─ Record reviewer verdict in PostgreSQL:
    * Table: jobs.reviewer_verdicts (SEPARATE from automated verdict)
    * Fields: review_id, job_id, reviewer_id, decision, confidence,
              annotations (JSONB), notes, timestamp
  ─ Update job status → 'REVIEW_COMPLETED'
  ─ Generate reviewer-annotated report addendum (PDF)
  ─ Append addendum to evidence package (with new signature over combined package)
  ─ Write reviewer audit record
  ─ Trigger webhook notification with final verdict
```

---

## 9. Audit Data Flow

All services emit structured audit events to a dedicated Kafka topic:

```
Service → [Kafka: gdi.audit.*] → Audit Service → PostgreSQL (audit.events)
                                              └──→ Elasticsearch (for search)
                                              └──→ SIEM integration (Splunk/QRadar)
```

**Audit Event Schema**:
```json
{
  "event_id": "uuid-v4",
  "event_type": "string (enum)",
  "timestamp": "RFC3339 nanosecond",
  "service_name": "string",
  "service_version": "string",
  "actor_type": "USER|SERVICE|SYSTEM",
  "actor_id": "string (user_id or service_name)",
  "actor_ip": "string (for user actions)",
  "tenant_id": "string",
  "resource_type": "JOB|TEMPLATE|USER|CONFIG|...",
  "resource_id": "string",
  "action": "string",
  "outcome": "SUCCESS|FAILURE|PARTIAL",
  "context": {...},
  "correlation_id": "string (distributed trace ID)"
}
```

**Audit Table Properties** (PostgreSQL):
- `audit.events` is an append-only table (INSERT only; no UPDATE, DELETE via row-level triggers + policy)
- Partitioned by month (automatic partition creation)
- Row-level security prevents cross-tenant access
- Separate PostgreSQL role for audit writes (write-only, no delete)
- Automated export to object storage for long-term retention (7 years)

---

## 10. Data Lifecycle and Retention

| Artifact | Default Retention | Government Tier | Deletion Method |
|----------|-------------------|-----------------|-----------------|
| Document Binary (raw) | 90 days (configurable) | 7 years | Secure delete (DoD 5220.22-M) |
| Document Rendering/Modalities | 30 days | 7 years | Secure delete |
| Genome Record | Indefinite (while template active) | Indefinite | Requires multi-party auth |
| Engine Results | 30 days | 7 years | Secure delete |
| Forensic Reports | 7 years | 10 years | Secure delete |
| Evidence Package | 7 years | 10 years | Secure delete |
| Heatmaps | 30 days | 7 years | Secure delete |
| Job Records (PostgreSQL) | Indefinite | Indefinite | Anonymize + archive |
| Audit Records | 7 years | 10 years | Never deleted; archived |
| Template Genomes | Indefinite | Indefinite | Requires multi-party auth |

**Retention Policy Enforcement**:
- Object Storage lifecycle rules enforce automatic deletion at retention expiry
- Retention policy configuration is per-tenant and requires Tenant Administrator authorization
- Any retention policy shortening requires security officer counter-signature
- Retention policy changes are logged as audit events

---

## 11. Data Classification Taxonomy

| Class | Description | Examples | Controls |
|-------|-------------|----------|----------|
| C1: SECRET | Most sensitive; externally regulated | Document content with PII, identity documents | Encrypted at rest (AES-256-GCM), encrypted in transit (TLS 1.3), access logged, minimum access |
| C2: CONFIDENTIAL | Sensitive business data | Forensic reports, genome records, verdicts | Encrypted at rest, encrypted in transit, RBAC enforced |
| C3: INTERNAL | Internal operational data | Job metadata, audit logs, configuration | Encrypted in transit, RBAC enforced |
| C4: PUBLIC | No sensitivity | API documentation, public health endpoints | No special controls |

---

## 12. Error Flow and Dead Letter Handling

### 12.1 Kafka Dead Letter Queue

Any message that fails processing after 3 retry attempts is routed to a dead letter topic:
- `gdi.dlq.{original_topic}` 

Dead letter topics are:
- Monitored with alerting (any DLQ message triggers P2 alert)
- Manually inspectable by on-call engineers
- Replayable after root cause resolution

### 12.2 Job Error State Machine

```
INGESTED → SCANNING → RECONSTRUCTION → EXTRACTING → INTELLIGENCE → VERDICT_ISSUED → COMPLETED
               │              │              │              │              │
         REJECTED_MALWARE   ERROR          ERROR          ERROR         PENDING_REVIEW
                              │              │              │
                              └──────────────┴──────────────┘
                                         FAILED
                                    (→ human review)
```

Failed jobs:
- Status updated to 'FAILED' in PostgreSQL
- Failure context (engine name, error message, stack trace) stored in job record
- Job automatically routed to human review queue with FAILURE context
- Submitter notified of failure and routing
- Retry is possible (creates a new job with parent_job_id reference)

---

## 13. Cross-Tenant Data Isolation

### 13.1 Storage Isolation

- **Object Storage**: All objects prefixed with `{tenant_id}/`; bucket policies deny cross-tenant access; separate KMS keys per tenant
- **PostgreSQL**: Row-level security (RLS) policies enforce tenant isolation; connection pool separated by tenant tier
- **Redis**: Key namespace prefixed with `{tenant_id}:` for all tenant data; separate Redis logical databases for high-value tenants
- **Qdrant**: Separate collection per tenant (`tenant_{tenant_id}_genomes`); no cross-tenant query possible

### 13.2 Network Isolation

- Kubernetes namespace-level NetworkPolicy prevents cross-tenant pod communication
- Service accounts are tenant-scoped for API service calls
- Kafka ACLs restrict consumer groups to tenant-prefixed topics

### 13.3 Compute Isolation (Government/Enterprise Tier)

Premium tiers run on dedicated node pools with `nodeSelector` and `tolerations` preventing shared-tenant workloads on the same physical nodes.

---

## 14. Data Flow Diagrams (Detailed)

### 14.1 Complete Job Data Flow (Summary)

```
CLIENT
  │ POST /v1/jobs (multipart, JWT)
  ▼
API GATEWAY (TLS, Auth, Rate Limit)
  │ gRPC
  ▼
INGEST-SVC
  │ Write binary ──────────────────────────────▶ OBJECT STORAGE (gdi-documents-raw)
  │ Write job record ──────────────────────────▶ POSTGRESQL (jobs.job_records)
  │ Produce event ─────────────────────────────▶ KAFKA (gdi.jobs.submitted)
  │ 202 Accepted {job_id}
  ▼
CLIENT

KAFKA (gdi.jobs.submitted)
  │
  ▼
JOB-ORCHESTRATOR
  │ gRPC dispatch
  ▼
RECONSTRUCT-SVC
  │ Read binary ───────────────────────────────▶ OBJECT STORAGE
  │ Write modalities ──────────────────────────▶ OBJECT STORAGE
  │ Return manifest
  ▼
JOB-ORCHESTRATOR
  │ Produce N tasks ───────────────────────────▶ KAFKA (gdi.jobs.{id}.tasks)
  │
  │ (Fan-out)
  │
  ├──▶ LAYOUT-ENGINE
  ├──▶ TYPOGRAPHY-ENGINE
  ├──▶ RENDERING-ENGINE
  ├──▶ TEXTURE-ENGINE
  ├──▶ FREQUENCY-ENGINE
  ├──▶ NOISE-ENGINE
  ├──▶ METADATA-ENGINE
  ├──▶ OBJGRAPH-ENGINE
  ├──▶ MICRODNA-ENGINE
  └──▶ AI-ENGINE-SVC
        (All read from OBJECT STORAGE, write results to KAFKA)
  │
  │ (Fan-in)
  │
  ▼
GENOME-ORCHESTRATOR
  │ Assemble genome
  │ Write genome ──────────────────────────────▶ OBJECT STORAGE
  │ Write vector ──────────────────────────────▶ QDRANT
  │ Produce genome.assembled
  ▼
KAFKA (gdi.jobs.genome.assembled)
  │
  ▼
SIMILARITY-SVC ──▶ FUSION-SVC ──▶ DECISION-SVC
                                      │
                          ┌───────────┴───────────┐
                          ▼                       ▼
                   HEATMAP-SVC           REPORT-SVC
                          │                       │
                          └───────────┬───────────┘
                                      ▼
                           EVIDENCE-PACKAGER-SVC
                                      │
                                      ▼
                               OBJECT STORAGE (WORM)
                               POSTGRESQL (job complete)
                               KAFKA (job.completed)
                               WEBHOOK (client notification)
```

---

*Previous: [03_System_Architecture](../03_System_Architecture/README.md)*
*Next: [05_Genome_Extraction_Engine](../05_Genome_Extraction_Engine/README.md)*
*Return to: [Master Index](../README.md)*
