# Document 21 — Backend Architecture
## GDI: Microservices, APIs, and Service Mesh

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [03_System_Architecture], [04_Data_Flow], [22_API_Design], [26_Security], [29_Deployment]

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Microservices Breakdown](#2-microservices-breakdown)
3. [Service Mesh & Networking (Istio)](#3-service-mesh--networking-istio)
4. [Asynchronous Event Architecture (Kafka)](#4-asynchronous-event-architecture-kafka)
5. [Distributed Caching Strategy (Redis)](#5-distributed-caching-strategy-redis)
6. [Resilience Patterns & Circuit Breakers](#6-resilience-patterns--circuit-breakers)

---

## 1. Architecture Overview

GDI's backend is implemented as a cloud-native microservices architecture orchestrated via Kubernetes and Istio. High-throughput ingestion, orchestration, and gateway services are implemented in **Go 1.22+**, while scientific computing, engine extraction, and AI models are implemented in **Python 3.12+**.

---

## 2. Microservices Breakdown

| Service Name | Language | Core Responsibilities | State Management | Communication |
|--------------|----------|-----------------------|------------------|---------------|
| `ingest-svc` | Go | Document upload, size validation, SHA3-256 hashing | Stateless | HTTP/REST, Kafka Producer |
| `job-orchestrator` | Go | Job lifecycle state machine, timeout tracking | Redis / PostgreSQL | Kafka Consumer/Producer, gRPC |
| `reconstruct-svc` | Python/Go | Format normalization, multi-modality rendering | Ephemeral Scratch | gRPC, MinIO I/O |
| `genome-orchestrator` | Go | Fan-out dispatch, engine result collection | Redis Counter | Kafka, gRPC |
| `engine-farm-*` | Python | Feature extraction per dimension (12+ services) | Stateless | Kafka Consumer/Producer |
| `intelligence-svc` | Python | Similarity, Fusion, and Decision computation | Stateless | gRPC |
| `report-svc` | Python | PDF/JSON generation, heatmap compositing | Ephemeral Scratch | gRPC, MinIO I/O |

---

## 3. Service Mesh & Networking (Istio)

All inter-service communication is governed by an **Istio Service Mesh**:
- **mTLS Strict Mode**: All pod-to-pod communication is encrypted using mutual TLS with short-lived SPIFFE/SPIRE certificates.
- **Traffic Routing**: Canary releases and blue-green engine deployments managed via Istio `VirtualService` and `DestinationRule` manifests.
- **Ingress Gateway**: Kong Gateway manages external traffic, delegating internal service mesh routing to Istio Ingress.

---

## 4. Asynchronous Event Architecture (Kafka)

Kafka acts as the primary event bus for decoupling asynchronous processing stages:

```
[ingest-svc] ──(gdi.jobs.submitted)──▶ [job-orchestrator]
                                              │
                     ┌────────────────────────┘
                     ▼
        (gdi.jobs.<id>.tasks)
                     │
      ┌──────────────┼──────────────┐
      ▼              ▼              ▼
[engine-layout] [engine-typo] [engine-ai]
      │              │              │
      └──────────────┼──────────────┘
                     ▼
        (gdi.jobs.<id>.results) ──▶ [genome-orchestrator]
```

- **Partitioning Strategy**: Partitioned by `job_id` to guarantee ordering per document.
- **Durability**: `acks=all`, `min.insync.replicas=2`, replication factor 3.

---

## 5. Distributed Caching Strategy (Redis)

A Redis Cluster (6 nodes) handles ephemeral high-speed state:
- **Rate Limiter**: Sliding window counters per tenant (`rate:{tenant_id}:{minute}`).
- **Engine Counter**: Dynamic fan-in completion tracking (`genome:{job_id}:pending`).
- **Feature Cache**: Pre-computed embeddings for recently analyzed templates (`cache:template:{id}`).

---

## 6. Resilience Patterns & Circuit Breakers

- **Timeout Boundaries**: Hard gRPC timeout of $10\text{s}$ per engine request; overall job timeout of $120\text{s}$ (Standard Tier).
- **Retries & Backoff**: Exponential backoff with jitter ($base=100\text{ms}, max=3\text{s}$, max 3 retries).
- **Circuit Breakers**: Istio `OutlierDetection` ejects unhealthy engine pods from the load balancing pool if they return 5xx errors $>50\%$ of requests over a 10s window.

---

*Previous: [20_Forensic_Report_Generator](../20_Forensic_Report_Generator/README.md)*
*Next: [22_API_Design](../22_API_Design/README.md)*
*Return to: [Master Index](../README.md)*
