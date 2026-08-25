# Document 28 — Infrastructure
## GDI: Cloud Infrastructure and Resource Topology

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [03_System_Architecture], [11_Capacity_Model], [29_Deployment], [33_Scaling]

---

## Table of Contents

1. [Infrastructure Provisioning Philosophy](#1-infrastructure-provisioning-philosophy)
2. [Multi-Cloud & Air-Gapped Topology](#2-multi-cloud--air-gapped-topology)
3. [Kubernetes Cluster Architecture (EKS / Bare-Metal)](#3-kubernetes-cluster-architecture-eks--bare-metal)
4. [GPU Node Topology & Heterogeneous Compute](#4-gpu-node-topology--heterogeneous-compute)
5. [Network Topology & Edge Integration](#5-network-topology--edge-integration)
6. [Terraform / OpenTofu Infrastructure Specs](#6-terraform--opentofu-infrastructure-specs)

---

## 1. Infrastructure Provisioning Philosophy

GDI infrastructure is managed strictly as code (**Infrastructure as Code / IaC**) using **Terraform / OpenTofu**. No manual modifications to cloud resources or bare-metal setups are permitted in production.

---

## 2. Multi-Cloud & Air-Gapped Topology

- **Primary Cloud (SaaS)**: AWS (us-east-1 primary, eu-west-1 secondary for EU GDPR).
- **Secondary Cloud (DR)**: GCP (us-central1).
- **On-Premise / Air-Gapped (Government)**: Bare-metal clusters running Red Hat OpenShift / k3s with air-gapped container registries.

---

## 3. Kubernetes Cluster Architecture (EKS / Bare-Metal)

Node pools are strictly segregated by workload characteristic:

| Node Pool Name | Instance Type / Hardware | Min/Max Nodes | Taints & Tolerations | Purpose |
|----------------|--------------------------|---------------|----------------------|---------|
| `system-pool` | `m6i.2xlarge` (8 vCPU, 32GB) | 3 / 10 | None | Ingress, Auth, Monitoring, Core API |
| `stateless-pool` | `c6i.4xlarge` (16 vCPU, 32GB) | 5 / 50 | `workload=general:NoSchedule` | Job Orchestrators, Ingestion, API Gateway |
| `cpu-engine-pool` | `c6i.8xlarge` (32 vCPU, 64GB) | 10 / 100 | `workload=cpu-engine:NoSchedule` | Layout, Typography, Texture, Noise Engines |
| `gpu-engine-pool` | `g5.12xlarge` (4× NVIDIA A10G) | 2 / 20 | `workload=gpu-engine:NoSchedule`, `nvidia.com/gpu` | Deep Learning AI Inference Engines |

---

## 4. GPU Node Topology & Heterogeneous Compute

- **GPU Interconnect**: NVLink (where available on P4d/P5 instances) to enable fast multi-GPU model loading.
- **NVIDIA GPU Operator**: Deployed on EKS to automate CUDA driver management, NVIDIA Container Toolkit, and GPU feature discovery.
- **MIG (Multi-Instance GPU)**: Enabled on A100 80GB GPUs to slice single physical GPUs into smaller instances for lightweight vision models.

---

## 5. Network Topology & Edge Integration

```
AWS Route 53 (DNS / Anycast)
       │
Cloudflare Magic Transit (DDoS Protection & WAF)
       │
AWS Network Load Balancer (NLB)
       │
Istio Ingress Gateway (EKS cluster)
```

---

## 6. Terraform / OpenTofu Infrastructure Specs

Key module organization:
- `modules/vpc`: Subnets (Public, Private, Isolated Data, HSM), NAT Gateways, VPC Flow Logs.
- `modules/eks`: Cluster control plane, Node groups, OIDC provider.
- `modules/rds`: PostgreSQL Patroni / AWS Aurora multi-AZ.
- `modules/kms`: KMS Keys and HSM key aliases.

---

*Previous: [27_Cryptography](../27_Cryptography/README.md)*
*Next: [29_Deployment](../29_Deployment/README.md)*
*Return to: [Master Index](../README.md)*
