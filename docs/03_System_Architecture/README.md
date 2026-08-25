# Document 03 — System Architecture
## GDI: Overall System Design and Component Topology

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [02_Core_Principles], [04_Data_Flow], [21_Backend_Architecture], [28_Infrastructure], [29_Deployment]

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Architectural Layers](#2-architectural-layers)
3. [Component Topology](#3-component-topology)
4. [Service Registry](#4-service-registry)
5. [Communication Patterns](#5-communication-patterns)
6. [Data Stores Overview](#6-data-stores-overview)
7. [Security Perimeter](#7-security-perimeter)
8. [Deployment Topology](#8-deployment-topology)
9. [Technology Stack](#9-technology-stack)
10. [Architectural Decision Records](#10-architectural-decision-records)
11. [Capacity Model](#11-capacity-model)
12. [Failure Domain Analysis](#12-failure-domain-analysis)

---

## 1. Architecture Overview

GDI is a cloud-native, microservices-based platform organized around a central forensic processing pipeline. The architecture follows a layered design with a strict data flow: document ingestion → forensic reconstruction → genome extraction → genome comparison → evidence fusion → verdict → report generation.

### 1.1 Top-Level System Boundaries

```
┌─────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL ZONE                               │
│  Customer Web App   Customer API Client   Human Reviewer UI         │
└──────────────┬───────────────────┬──────────────────────────────────┘
               │                   │                    │
               ▼                   ▼                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                              │
│  TLS Termination │ Auth/Authz │ Rate Limiting │ DDoS Protection     │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                              │
│    Document Ingestion Service │ Job Orchestrator │ Template Manager  │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ (Kafka)
┌──────────────────────────▼──────────────────────────────────────────┐
│                  FORENSIC PROCESSING LAYER                          │
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │
│  │ Document        │  │ Genome          │  │ AI Inference        │ │
│  │ Reconstruction  │  │ Extraction      │  │ Engine              │ │
│  │ Engine          │  │ Orchestrator    │  │ (Multi-Model)       │ │
│  └────────┬────────┘  └────────┬────────┘  └──────────┬──────────┘ │
│           │                    │                        │            │
│  ┌────────▼──────────────────────────────────────────────────────┐  │
│  │              FORENSIC ENGINE FARM (12–20 engines)             │  │
│  │  Layout │ Typography │ Rendering │ Texture │ Frequency │ ...   │  │
│  └────────────────────────────────────────────────────────────── ┘  │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│                    INTELLIGENCE LAYER                               │
│  Similarity Engine │ Fusion Engine │ Decision Engine                │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│                     OUTPUT LAYER                                    │
│  Report Generator │ Heatmap Generator │ Evidence Packager           │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│                    DATA PERSISTENCE LAYER                           │
│  PostgreSQL │ Redis │ Kafka │ MinIO/S3 │ Qdrant │ Elasticsearch     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Architectural Layers

### 2.1 API Gateway Layer

**Purpose**: Single ingress point for all external traffic. Handles TLS termination, authentication, authorization, rate limiting, and request routing.

**Why Separate Layer**: Centralizing these cross-cutting concerns at the gateway prevents duplication across services and provides a single point for security policy enforcement.

**Technology**: Kong Gateway (self-hosted) for enterprise/government; AWS API Gateway for SaaS. Kong is selected for:
- Plugin ecosystem (rate limiting, JWT verification, request/response transformation)
- On-premise deployment support (required for government tier)
- Declarative configuration (managed as code)
- OpenID Connect integration for SSO

**Alternatives Considered**:
- *Nginx Plus*: Less feature-complete for API management; no native declarative config for auth plugins
- *Envoy standalone*: Lower-level, requires more configuration; better suited as sidecar proxy in service mesh
- *AWS API Gateway*: Cloud-only, not suitable for on-premise government deployment

---

### 2.2 Orchestration Layer

**Purpose**: Manages job lifecycle from receipt through completion. Maintains job state, coordinates engine execution, handles failures, and routes results.

**Components**:
- **Document Ingestion Service**: Receives documents, computes hash, stores binary, queues job
- **Job Orchestrator**: Manages job state machine; coordinates parallel engine execution; handles timeouts and retries
- **Template Manager**: CRUD operations for templates; manages genome enrollment workflow

**Technology**: Go services for high-throughput ingestion and orchestration. Go is selected for:
- High concurrency with low memory overhead (goroutines)
- Excellent gRPC and Kafka client libraries
- Strong type system reduces runtime errors in state machine logic
- Deterministic garbage collection pause behavior
- Compiled binary deployment simplicity

---

### 2.3 Forensic Processing Layer

**Purpose**: Transforms raw document binary into a complete forensic genome through parallel execution of all forensic engines.

**Components**:
- **Document Reconstruction Engine**: Normalizes, renders, and decomposes document into multiple analysis modalities
- **Genome Extraction Orchestrator**: Fans out extraction tasks to all forensic engines; collects results; assembles genome record
- **Forensic Engine Farm**: All individual forensic engines (Layout, Typography, Rendering, Texture, Frequency, Noise, Metadata, Object Graph, Micro-DNA, AI)
- **AI Inference Engine**: GPU-accelerated deep learning inference for AI-based forensic features

**Technology**: Python services for forensic engines (access to scipy, OpenCV, scikit-image, PyTorch, pillow). Go for the orchestration tier. FastAPI for engine HTTP interfaces (when gRPC is not used directly).

---

### 2.4 Intelligence Layer

**Purpose**: Takes engine outputs and produces the final forensic verdict through structured, interpretable evidence aggregation.

**Components**:
- **Similarity Engine**: Computes per-feature and per-engine similarity scores relative to the natural variation model
- **Fusion Engine**: Aggregates engine scores using Bayesian fusion and computes evidence weights
- **Decision Engine**: Applies verdict thresholds, computes confidence, routes to human review if needed

**Technology**: Python (scipy, numpy, pymc) for statistical computation. All intelligence layer components are purely computational (no I/O); they receive structured data and produce structured data.

---

### 2.5 Output Layer

**Purpose**: Transforms the verdict and evidence into human-readable and machine-readable forensic artifacts.

**Components**:
- **Forensic Report Generator**: Produces PDF and JSON forensic reports
- **Heatmap Generator**: Produces spatial anomaly visualizations
- **Evidence Packager**: Assembles and cryptographically seals the complete evidence package

**Technology**: Python (reportlab for PDF, matplotlib/seaborn for heatmaps). Cryptographic sealing uses platform-managed signing keys via HSM interface.

---

### 2.6 Data Persistence Layer

**Purpose**: Stores all forensic artifacts, job records, genome vectors, and operational data.

| Store | Technology | Purpose |
|-------|------------|---------|
| Primary Relational DB | PostgreSQL 16 | Job records, template metadata, user/tenant data, audit logs |
| Cache | Redis Cluster | Job status, session data, rate limit counters, feature cache |
| Message Queue | Apache Kafka | Job events, engine task distribution, result aggregation |
| Object Storage | MinIO (on-prem) / S3 (SaaS) | Document binaries, genome records, forensic reports |
| Vector Database | Qdrant | Genome vectors for similarity search |
| Search/Index | Elasticsearch | Full-text search on report content, template metadata |
| Time-Series | Prometheus (TSDB) | Operational metrics |

---

## 3. Component Topology

### 3.1 Detailed Service Map

```
┌────────────────────────────────────────────────────────────────────┐
│                        INGRESS SERVICES                            │
├───────────────────┬────────────────────┬───────────────────────────┤
│  api-gateway      │  auth-service      │  rate-limiter             │
│  (Kong)           │  (Keycloak)        │  (Redis-backed)           │
└───────────────────┴────────────────────┴───────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────────────┐
│                     ORCHESTRATION SERVICES                         │
├──────────────────┬─────────────────────┬──────────────────────────┤
│  ingest-svc      │  job-orchestrator   │  template-svc             │
│  (Go)            │  (Go)               │  (Go)                     │
└──────────────────┴─────────────────────┴──────────────────────────┘
                              │ Kafka
┌─────────────────────────────▼──────────────────────────────────────┐
│                   FORENSIC PROCESSING SERVICES                     │
├──────────────────┬──────────────────────────────────────────────── ┤
│ reconstruct-svc  │ genome-orchestrator-svc                         │
│ (Python/Go)      │ (Go)                                            │
├──────────────────┴──────────────────────────────────────────────── ┤
│                     FORENSIC ENGINE PODS                           │
│  layout-engine   │ typography-engine │ rendering-engine            │
│  (Python)        │ (Python)          │ (Python)                    │
│  texture-engine  │ frequency-engine  │ noise-engine                │
│  (Python)        │ (Python)          │ (Python)                    │
│  metadata-engine │ objgraph-engine   │ microdna-engine             │
│  (Python)        │ (Python)          │ (Python/C++)                │
│  ai-engine-svc   │ (Python/CUDA)     │                             │
└─────────────────────────────────────────────────────────────────── ┘
                              │
┌─────────────────────────────▼──────────────────────────────────────┐
│                     INTELLIGENCE SERVICES                          │
├──────────────────┬─────────────────────┬──────────────────────────┤
│  similarity-svc  │  fusion-svc         │  decision-svc             │
│  (Python)        │  (Python)           │  (Python)                 │
└──────────────────┴─────────────────────┴──────────────────────────┘
                              │
┌─────────────────────────────▼──────────────────────────────────────┐
│                        OUTPUT SERVICES                             │
├──────────────────┬─────────────────────┬──────────────────────────┤
│  report-svc      │  heatmap-svc        │  evidence-packager-svc   │
│  (Python)        │  (Python)           │  (Python)                 │
└──────────────────┴─────────────────────┴──────────────────────────┘
```

---

## 4. Service Registry

| Service Name | Language | CPU | RAM | GPU | Replicas (normal) | Replicas (peak) |
|--------------|----------|-----|-----|-----|-------------------|-----------------|
| api-gateway | Kong | 4 vCPU | 8 GB | None | 3 | 10 |
| auth-service | Keycloak/Java | 4 vCPU | 16 GB | None | 2 | 4 |
| ingest-svc | Go | 2 vCPU | 4 GB | None | 3 | 20 |
| job-orchestrator | Go | 4 vCPU | 8 GB | None | 2 | 8 |
| template-svc | Go | 2 vCPU | 4 GB | None | 2 | 4 |
| reconstruct-svc | Python | 8 vCPU | 32 GB | None | 4 | 16 |
| genome-orchestrator | Go | 4 vCPU | 8 GB | None | 2 | 8 |
| layout-engine | Python | 8 vCPU | 16 GB | None | 4 | 20 |
| typography-engine | Python | 8 vCPU | 16 GB | None | 4 | 20 |
| rendering-engine | Python | 8 vCPU | 16 GB | None | 4 | 20 |
| texture-engine | Python | 8 vCPU | 16 GB | None | 2 | 10 |
| frequency-engine | Python | 8 vCPU | 16 GB | None | 2 | 10 |
| noise-engine | Python | 8 vCPU | 16 GB | None | 2 | 10 |
| metadata-engine | Python | 4 vCPU | 8 GB | None | 2 | 8 |
| objgraph-engine | Python | 8 vCPU | 16 GB | None | 2 | 8 |
| microdna-engine | Python/C++ | 8 vCPU | 32 GB | None | 4 | 16 |
| ai-engine-svc | Python/CUDA | 8 vCPU | 64 GB | 1× A100 | 4 | 16 |
| similarity-svc | Python | 4 vCPU | 16 GB | None | 2 | 8 |
| fusion-svc | Python | 4 vCPU | 8 GB | None | 2 | 8 |
| decision-svc | Python | 4 vCPU | 8 GB | None | 2 | 8 |
| report-svc | Python | 4 vCPU | 8 GB | None | 2 | 8 |
| heatmap-svc | Python | 8 vCPU | 16 GB | Optional | 2 | 8 |
| evidence-packager | Python | 4 vCPU | 8 GB | None | 2 | 6 |
| review-ui-svc | Node.js | 4 vCPU | 8 GB | None | 2 | 4 |
| admin-svc | Go | 2 vCPU | 4 GB | None | 2 | 4 |
| notification-svc | Go | 2 vCPU | 4 GB | None | 2 | 6 |
| audit-svc | Go | 4 vCPU | 8 GB | None | 2 | 4 |

---

## 5. Communication Patterns

### 5.1 Synchronous (gRPC)

Used for:
- API Gateway → Ingest Service (document submission)
- Job Orchestrator → Genome Orchestrator (job kick-off)
- Genome Orchestrator → Individual Engines (task dispatch, when low-latency response needed)
- Intelligence layer internal communication (similarity → fusion → decision)
- Admin service → all management operations

**Why gRPC over REST for internal calls**:
- Protocol Buffers provide type-safe, versioned, compact serialization
- HTTP/2 multiplexing reduces connection overhead for high-volume inter-service calls
- Generated client stubs reduce boilerplate and eliminate serialization errors
- Bi-directional streaming capability is used by the genome orchestrator to stream partial results from engines

---

### 5.2 Asynchronous (Kafka)

Used for:
- Ingest Service → Job Orchestrator (document arrival events)
- Job Orchestrator → Forensic Engine Farm (task distribution, fan-out)
- Forensic Engines → Genome Orchestrator (result fan-in)
- Decision Engine → Report Generator, Heatmap Generator, Evidence Packager (parallel output generation)
- Audit logging (all services → audit topic)
- Notification delivery

**Why Kafka over alternatives**:
- *vs. RabbitMQ*: Kafka's log-based architecture provides better durability (messages can be replayed), better throughput, and built-in partitioning for parallelism
- *vs. SQS/SNS*: Cloud-only; not suitable for on-premise government deployment; less control over partitioning and consumer groups
- *vs. NATS*: NATS JetStream is a valid alternative; Kafka chosen for better operational maturity, broader ecosystem integration (Kafka Connect for CDC), and team familiarity

**Topic Design**:
- `gdi.jobs.submitted`: New job events from ingestion
- `gdi.jobs.{job_id}.engine.{engine_name}`: Per-job engine task topics
- `gdi.jobs.{job_id}.results`: Engine result collection
- `gdi.jobs.completed`: Completed job events (drives report generation)
- `gdi.audit.*`: Audit log events (append-only, long retention)
- `gdi.alerts.*`: Operational alert events

---

### 5.3 Service Mesh

All services communicate through an Istio service mesh providing:
- mTLS for all inter-service communication (zero-trust enforcement)
- Traffic management (circuit breakers, retry policies, timeouts)
- Distributed tracing propagation (via Jaeger/Tempo)
- Metrics collection at the network layer

---

## 6. Data Stores Overview

### 6.1 PostgreSQL (Primary Relational Database)

**Role**: System of record for all structured metadata: jobs, templates, users, tenants, audit logs, configuration.

**Database Schemas** (logical; all within a single PostgreSQL cluster with schema-level isolation per tenant):
- `core`: Platform-wide entities (tenants, users, roles)
- `jobs`: Job lifecycle records
- `templates`: Template and genome enrollment records
- `audit`: Immutable audit log (append-only, row-level deletion prohibited)
- `config`: System configuration

**High Availability**: Patroni-managed primary/replica cluster with automatic failover. Read replicas for analytics and audit queries.

---

### 6.2 Redis Cluster

**Role**: Ephemeral high-speed cache and coordination store.

**Uses**:
- Job status cache (avoid PostgreSQL polling)
- Session tokens (short-lived)
- Rate limiting counters (sliding window algorithm)
- Feature vector cache (avoid recomputing expensive features for recently seen documents)
- Distributed locks (for singleton orchestrator operations)

**Configuration**: Redis Cluster mode with 6 nodes (3 masters, 3 replicas). Persistence configured as RDB + AOF.

---

### 6.3 Apache Kafka

**Role**: Event streaming backbone for asynchronous job processing and audit logging.

**Configuration**: 3-node Kafka cluster with KRaft (no ZooKeeper). Replication factor 3 for all forensic topics. Minimum in-sync replicas: 2.

**Retention**: Job topics: 7 days. Audit topics: 7 years (compliance requirement).

---

### 6.4 MinIO / Amazon S3

**Role**: Object storage for all binary artifacts: document binaries, genome records (serialized), forensic reports (PDF, JSON), heatmaps, evidence packages.

**Immutability**: All buckets configured with Object Lock (WORM) for forensic artifact buckets.

**Encryption**: Server-side encryption (SSE-KMS) with HSM-backed keys.

---

### 6.5 Qdrant (Vector Database)

**Role**: Storage and similarity search for genome vectors. Each genome is stored as a high-dimensional vector enabling approximate nearest neighbor (ANN) search for population-level analysis.

**Why Qdrant**:
- Purpose-built for vector similarity search with high performance on high-dimensional vectors
- Supports payload filters (enabling search within a tenant's corpus)
- HNSW indexing with configurable precision/speed tradeoff
- REST and gRPC APIs
- Horizontal scaling (distributed mode)
- Apache 2.0 license (permissive commercial use)

**Alternatives**:
- *Pinecone*: Cloud-only; not suitable for on-premise; vendor lock-in
- *Weaviate*: Broader feature set but more operational complexity; Qdrant is more focused
- *FAISS*: Library, not a service; requires additional infrastructure to operationalize; no persistence or horizontal scaling
- *pgvector*: In-process with PostgreSQL; suitable for smaller scale but performance degrades at 10M+ vectors

---

### 6.6 Elasticsearch

**Role**: Full-text search and log aggregation. Template metadata search, forensic report search, and structured log querying.

**Why Elasticsearch**:
- Best-in-class full-text search with forensic domain-specific analyzers (configurable)
- Native integration with Kibana for operational log exploration
- Aggregation capabilities for analytics queries

---

## 7. Security Perimeter

### 7.1 Network Zones

```
Internet ──▶ WAF/DDoS ──▶ [DMZ]
                              ├── API Gateway (public-facing)
                              └── Load Balancer
                                        │
                                    [Service Zone] (private)
                                        ├── All application services
                                        └── Service Mesh (Istio mTLS)
                                                  │
                                           [Data Zone] (private, isolated)
                                                  ├── PostgreSQL
                                                  ├── Redis
                                                  ├── Kafka
                                                  ├── Qdrant
                                                  └── MinIO/S3 Endpoint
                                                            │
                                                    [HSM Zone] (physical isolation)
                                                            └── HSM Appliance
```

**Zone Separation**:
- DMZ to Service Zone: Firewall rules allowing only API Gateway traffic inbound
- Service Zone to Data Zone: Firewall rules allowing only specific service IPs on defined ports
- Data Zone to HSM Zone: Physical network isolation; HSM PKCS#11 client access only

---

## 8. Deployment Topology

### 8.1 SaaS Multi-Tenant Deployment

**Cloud Provider**: AWS (primary), GCP (secondary for DR), Azure (tertiary for specific government requirements).

**Regions**: US-East-1 (primary), EU-West-1 (EU data residency), APAC (planned Phase 2).

**Kubernetes**: Amazon EKS with managed node groups. GPU nodes use EC2 P4d (A100) or P5 (H100) instances.

**Tenant Isolation**: Logical isolation via Kubernetes namespaces and network policies. Shared compute infrastructure with dedicated namespace-level resource quotas.

### 8.2 On-Premise / Government Deployment

**Kubernetes**: k3s or OpenShift (depending on customer environment) on customer-managed bare metal or private cloud.

**GPU**: Customer-provisioned NVIDIA A100 or H100 cards or GPU appliances.

**Object Storage**: MinIO cluster on-premise (S3-compatible).

**Network**: Fully air-gapped option available: no outbound internet connections required after initial installation.

---

## 9. Technology Stack

| Layer | Component | Technology | Version | License |
|-------|-----------|------------|---------|---------|
| Orchestration | Container | Kubernetes | 1.30+ | Apache 2.0 |
| Orchestration | Mesh | Istio | 1.21+ | Apache 2.0 |
| Gateway | API Gateway | Kong Gateway | 3.7+ | Apache 2.0 |
| Auth | Identity Provider | Keycloak | 24+ | Apache 2.0 |
| Messaging | Event Stream | Apache Kafka | 3.8+ | Apache 2.0 |
| Cache | In-Memory | Redis | 7.2+ | BSD |
| Database | Relational | PostgreSQL | 16+ | PostgreSQL License |
| Database | Vector | Qdrant | 1.10+ | Apache 2.0 |
| Storage | Object | MinIO / S3 | Latest | AGPL / Commercial |
| Search | Full-Text | Elasticsearch | 8.14+ | Elastic License 2.0 |
| AI Framework | Deep Learning | PyTorch | 2.3+ | BSD |
| AI Framework | Serving | TorchServe | 0.10+ | Apache 2.0 |
| Image Processing | CV | OpenCV | 4.10+ | Apache 2.0 |
| Image Processing | Scientific | scikit-image | 0.23+ | BSD |
| PDF | Processing | PyMuPDF | 1.24+ | AGPL / Commercial |
| Service | Backend | Go | 1.22+ | BSD |
| Service | AI/ML | Python | 3.12+ | PSF |
| API | Framework | FastAPI | 0.111+ | MIT |
| RPC | Protocol | gRPC / protobuf | v3 | Apache 2.0 |
| Observability | Metrics | Prometheus | 2.52+ | Apache 2.0 |
| Observability | Tracing | Tempo / Jaeger | Latest | Apache 2.0 |
| Observability | Logging | Loki | 3.0+ | AGPL |
| Observability | Dashboard | Grafana | 11+ | AGPL |
| Security | Vulnerability | Trivy | Latest | Apache 2.0 |
| CI/CD | Pipeline | GitHub Actions / ArgoCD | Latest | MIT/Apache |
| HSM | Cryptography | AWS CloudHSM / Thales Luna | N/A | Commercial |

---

## 10. Architectural Decision Records

### ADR-001: Microservices vs. Monolith

**Decision**: Microservices architecture.

**Context**: Forensic engines have very different resource profiles (CPU-bound, GPU-bound, memory-bound). Individual engine upgrades must not require full system redeployment. Different deployment targets (SaaS, on-premise) require different subsets of components.

**Rejected Alternative**: Monolith. While operationally simpler initially, a monolith would prohibit independent engine scaling, make GPU allocation inefficient, and prevent the modular engine upgrade capability required by [Axiom 10].

**Trade-off Accepted**: Increased operational complexity managed through Kubernetes, Helm charts, and ArgoCD.

---

### ADR-002: Python for AI/ML, Go for Orchestration

**Decision**: Python for all forensic engine and intelligence layer services. Go for all orchestration, ingestion, and gateway-adjacent services.

**Context**: Python has an unmatched ecosystem for scientific computing and AI (PyTorch, scipy, OpenCV, scikit-image). Go has superior concurrency primitives, lower memory overhead, and more predictable garbage collection for high-throughput orchestration tasks.

**Rejected Alternatives**:
- *All Python*: Python's GIL and higher memory overhead make it suboptimal for the high-concurrency orchestration tier
- *All Go*: Go's ML/CV ecosystem is immature; implementing forensic algorithms in Go would require writing from scratch what Python libraries provide

---

### ADR-003: Kafka over RabbitMQ

**Decision**: Apache Kafka for all event streaming.

**Context**: Kafka's log-based architecture enables message replay (critical for job recovery), supports multiple independent consumer groups (enabling the fan-in/fan-out engine pattern), and has significantly higher throughput (millions of messages/second vs. hundreds of thousands for RabbitMQ). Audit topics require 7-year retention, which Kafka handles natively.

---

### ADR-004: Qdrant over pgvector

**Decision**: Qdrant as the dedicated vector database.

**Context**: Genome vectors are high-dimensional (836–3,168 dimensions). pgvector's HNSW index shows significant performance degradation at dimensions above 512 and at vector corpus sizes above 1 million. Qdrant's native HNSW implementation maintains query latency under 50ms (P99) up to 100M+ vectors.

---

## 11. Capacity Model

### 11.1 Per-Analysis Job Resource Budget

| Stage | CPU (cores·s) | GPU (A100·s) | Memory (GB·s) | Storage (MB) |
|-------|--------------|-------------|----------------|-------------|
| Ingestion | 0.5 | 0 | 0.5 | 5–500 (doc size) |
| Reconstruction | 15 | 0 | 20 | 50 |
| Layout Engine | 20 | 0 | 8 | 5 |
| Typography Engine | 25 | 0 | 8 | 5 |
| Rendering Engine | 15 | 0 | 8 | 5 |
| Texture Engine | 10 | 0 | 8 | 5 |
| Frequency Engine | 10 | 0 | 8 | 5 |
| Noise Engine | 15 | 0 | 8 | 5 |
| Metadata Engine | 5 | 0 | 4 | 2 |
| Object Graph Engine | 20 | 0 | 16 | 10 |
| Micro-DNA Engine | 30 | 0 | 32 | 10 |
| AI Engine (inference) | 10 | 8 | 64 | 20 |
| Similarity + Fusion + Decision | 5 | 0 | 4 | 1 |
| Report + Heatmap + Evidence | 10 | 0 | 8 | 20 |
| **Total (standard tier)** | **190** | **8** | **193** | **~156** |

### 11.2 Infrastructure Sizing for 10,000 docs/day

Assuming 16-hour operating day with 2× peak factor:
- Effective rate: ~1,250 docs/hour standard; ~2,500 peak
- CPU: ~65 concurrent jobs at peak → ~520 CPU cores required
- GPU A100 (8 s/job): ~5,500 A100-seconds/hour → ~2.5 A100 GPUs average, ~5 peak
- With utilization efficiency (70% GPU, 60% CPU): ~8 A100s, ~870 CPU cores provisioned

Actual cluster sizing in [28_Infrastructure] accounts for redundancy, headroom, and multi-zone distribution.

---

## 12. Failure Domain Analysis

### 12.1 Critical Path Failure Modes

| Failure | Impact | Detection | Recovery |
|---------|--------|-----------|----------|
| API Gateway node failure | Partial (traffic rerouted) | Load balancer health check (5s) | Auto-replace pod (<60s) |
| Job Orchestrator failure | Jobs suspended (not lost) | Liveness probe (10s) | Pod restart; job resumes from Kafka offset |
| Single forensic engine failure | Genome incomplete; verdict indeterminate | Engine health check (30s) | Pod restart; job re-enqueued |
| All replicas of one engine fail | Genome incomplete; job → human review | Alert + engine circuit breaker | Scale new pods; replay from Kafka |
| PostgreSQL primary failure | Write operations suspended | Patroni auto-failover (<30s) | Read replica promoted; writes resume |
| Kafka broker failure | Message buffering at producer | ISR monitoring | Kafka rebalances consumers (<60s) |
| Qdrant node failure | Vector search degraded | Qdrant health endpoint | Qdrant self-heals via replica promotion |
| GPU node failure | AI analysis queued | Node health monitoring | Spare GPU node activated (<5 min) |
| Region failure | Full outage in region | Cross-region health checks | Route 53 failover to secondary region |

### 12.2 Failure Containment

- **Engine failures** are isolated: one engine failing does not affect others (independent pods)
- **Tenant failures** are isolated: a tenant workload spike cannot affect other tenants (namespace quotas)
- **Data corruption** is detected via checksums at every storage and retrieval operation; corrupted artifacts trigger immediate alert and job suspension

---

*Previous: [02_Core_Principles](../02_Core_Principles/README.md)*
*Next: [04_Data_Flow](../04_Data_Flow/README.md)*
*Return to: [Master Index](../README.md)*
