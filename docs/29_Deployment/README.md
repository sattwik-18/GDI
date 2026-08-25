# Document 29 — Deployment
## GDI: Kubernetes, CI/CD, and Release Management

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [03_System_Architecture], [21_Backend_Architecture], [28_Infrastructure], [31_Testing]

---

## Table of Contents

1. [Continuous Integration & Deployment Philosophy](#1-continuous-integration--deployment-philosophy)
2. [GitOps Architecture (ArgoCD)](#2-gitops-architecture-argocd)
3. [Release Progression & Deployment Strategies](#3-release-progression--deployment-strategies)
4. [Helm Chart Structure](#4-helm-chart-structure)
5. [Database Migration Strategy](#5-database-migration-strategy)
6. [Rollback Procedures](#6-rollback-procedures)

---

## 1. Continuous Integration & Deployment Philosophy

Deployment at GDI follows **GitOps principles** (ArgoCD). The desired state of the production environment is declaratively stored in version-controlled Git repositories (`gdi-deploy-k8s`).

No developer or DevOps engineer has direct `kubectl write` access to production clusters.

---

## 2. GitOps Architecture (ArgoCD)

```
[Developer] ──▶ Push to Git ──▶ GitHub Actions (Build, Test, Scan)
                                      │
                                      ▼
                             Publish OCI Image to ECR
                                      │
                                      ▼
                             Update Git Manifest (gdi-deploy-k8s)
                                      │
                                      ▼
                             [ ArgoCD Controller ] ──▶ Sync to EKS Cluster
```

---

## 3. Release Progression & Deployment Strategies

### 3.1 Canary Deployments (Istio + Flagger)
For core microservices (`job-orchestrator`, `intelligence-svc`):
1. Flagger deploys a canary pod revision (10% traffic weight).
2. Prometheus metrics are monitored over a 10-minute evaluation window:
   - Success Rate $\ge 99.9\%$
   - P95 Latency $\le 200\text{ms}$
3. If criteria met, traffic scales incrementally: 10% $\to$ 25% $\to$ 50% $\to$ 100%.

### 3.2 Blue/Green Deployments
Used for breaking database migration releases or forensic engine algorithm upgrades.

---

## 4. Helm Chart Structure

All microservices are packaged using a unified Helm umbrella chart (`gdi-platform`):

```
gdi-platform/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── _helpers.tpl
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── hpa.yaml
│   └── virtualservice.yaml
└── charts/
    ├── ingest-svc/
    ├── job-orchestrator/
    └── engine-typography/
```

---

## 5. Database Migration Strategy

Database schema migrations are executed using **golang-migrate** pre-deployment jobs:
- Migrations must be strictly **additive and backward-compatible**.
- `PreSync` ArgoCD hooks execute schema migration jobs before deploying the new microservice pods.

---

## 6. Rollback Procedures

- **Automated Metric Rollback**: Flagger automatically aborts canary rollouts if error rates exceed 0.1% or latency spikes occur.
- **Manual Git Rollback**: Reverting the Git commit in `gdi-deploy-k8s` triggers ArgoCD to sync the cluster back to the previous deployment revision within 60 seconds.

---

*Previous: [28_Infrastructure](../28_Infrastructure/README.md)*
*Next: [30_Observability](../30_Observability/README.md)*
*Return to: [Master Index](../README.md)*
