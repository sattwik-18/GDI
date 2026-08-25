# Document 33 — Scaling
## GDI: Horizontal and Vertical Scaling Strategy

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [01_Product_Requirements §12], [03_System_Architecture], [28_Infrastructure]

---

## Table of Contents

1. [Scaling Philosophy](#1-scaling-philosophy)
2. [Horizontal Pod Autoscaling (HPA) Rules](#2-horizontal-pod-autoscaling-hpa-rules)
3. [KEDA Event-Driven Kafka Autoscaling](#3-keda-event-driven-kafka-autoscaling)
4. [Kubernetes Cluster Autoscaling (Karpenter)](#4-kubernetes-cluster-autoscaling-karpenter)
5. [Database and State Storage Scaling](#5-database-and-state-storage-scaling)
6. [Multi-Region Global Scaling](#6-multi-region-global-scaling)

---

## 1. Scaling Philosophy

GDI scales **elastically based on queue lag and compute demand**. The platform guarantees seamless horizontal scaling from baseline load up to **10× load within 15 minutes** (**REQ-SCL-001**).

---

## 2. Horizontal Pod Autoscaling (HPA) Rules

Stateless API and orchestration microservices scale using Kubernetes HPA based on CPU and Memory metrics:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ingest-svc-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ingest-svc
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## 3. KEDA Event-Driven Kafka Autoscaling

Forensic engine worker pods scale dynamically using **KEDA (Kubernetes Event-driven Autoscaling)** monitoring Kafka consumer queue lag.

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: typography-engine-scaler
spec:
  scaleTargetRef:
    name: engine-typography
  minReplicaCount: 2
  maxReplicaCount: 30
  triggers:
  - type: kafka
    metadata:
      bootstrapServers: kafka:9092
      consumerGroup: typography-engine-group
      topic: gdi.jobs.tasks.typography
      lagThreshold: "10"
```

---

## 4. Kubernetes Cluster Autoscaling (Karpenter)

- **Karpenter** manages AWS EC2 node provisioning directly, bypassing standard Cluster Autoscaler limitations.
- Automatically provisions appropriate node sizes (`c6i.8xlarge`, `g5.12xlarge`) within 60 seconds when pending pods are detected.

---

## 5. Database and State Storage Scaling

- **PostgreSQL**: Read scaling via Patroni read-replicas; Connection pooling via PgBouncer.
- **Qdrant**: Horizontally sharded collection topology across nodes.
- **Redis**: Cluster sharding over 6 master nodes with auto-slot rebalancing.

---

## 6. Multi-Region Global Scaling

Phase 2 scaling introduces active-active multi-region deployment across US-East-1 and EU-West-1 utilizing AWS Route 53 latency-based routing and cross-region Kafka mirroring (MirrorMaker 2).

---

*Previous: [32_Performance](../32_Performance/README.md)*
*Next: [34_AI_Model_Management](../34_AI_Model_Management/README.md)*
*Return to: [Master Index](../README.md)*
