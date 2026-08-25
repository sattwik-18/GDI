# Document 26 — Security
## GDI: Security Architecture, Threat Modeling, and Controls

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [01_Product_Requirements §11], [02_Core_Principles §6], [03_System_Architecture §7], [27_Cryptography]

---

## Table of Contents

1. [Security Architecture & Principles](#1-security-architecture--principles)
2. [STRIDE Threat Model](#2-stride-threat-model)
3. [Zero-Trust Network Controls](#3-zero-trust-network-controls)
4. [Identity and Access Management (IAM / RBAC)](#4-identity-and-access-management-iam--rbac)
5. [Malware Sandboxing & Input Sanitization](#5-malware-sandboxing--input-sanitization)
6. [Data Protection at Rest and in Transit](#6-data-protection-at-rest-and-in-transit)
7. [Security Incident Response Strategy](#7-security-incident-response-strategy)

---

## 1. Security Architecture & Principles

GDI is designed under the **Zero-Trust Architecture** model (NIST SP 800-207). No internal service, pod, or user network is implicitly trusted. Security controls are enforced at every boundary: API Gateway, Service Mesh, Microservice, Database, and Storage layers.

---

## 2. STRIDE Threat Model

| Threat Category | Specific System Risk | Architectural Mitigation |
|-----------------|----------------------|--------------------------|
| **Spoofing** | Unauthorized API client forging tenant identity | OAuth 2.0 / OIDC JWT validation at Gateway; mTLS SPIFFE identities per pod. |
| **Tampering** | Adversary modifying stored evidence or genome records | Cryptographic SHA3-512 hashes; WORM S3 Object Lock; HSM ECDSA signatures. |
| **Repudiation** | User denying submission of a forged document | Append-only immutable PostgreSQL audit log; cryptographic submission receipts. |
| **Information Disclosure** | Cross-tenant document or genome leak | PostgreSQL Row-Level Security (RLS); isolated Qdrant collections; per-tenant KMS keys. |
| **Denial of Service** | Complex PDF / image decompression bombs | Strict file size enforcement (100MB); CPU/Memory pod cgroup limits; hard timeouts. |
| **Elevation of Privilege** | Malicious PDF script escaping container | Non-root container execution; read-only root filesystems; Seccomp / AppArmor profiles. |

---

## 3. Zero-Trust Network Controls

1. **Network Policies**: Kubernetes `NetworkPolicy` objects restrict inter-namespace traffic. Pods in `engine-farm` cannot initiate outbound internet connections.
2. **mTLS Enforcement**: Istio sidecars enforce Strict mTLS using SPIFFE IDs:
   `spiffe://cluster.local/ns/gdi-services/sa/job-orchestrator-sa`

---

## 4. Identity and Access Management (IAM / RBAC)

Role-Based Access Control (RBAC) permissions matrix:

| Permission | Platform Admin | Tenant Admin | Template Mgr | Analyst | Reviewer | Auditor |
|------------|----------------|--------------|--------------|---------|----------|---------|
| `write:tenants` | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| `write:templates` | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| `write:jobs` | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ |
| `read:jobs` | ✓ | ✓ | ✓ | ✓ (Own) | ✓ | ✓ |
| `write:reviews` | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| `read:audit` | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ |

---

## 5. Malware Sandboxing & Input Sanitization

- **ClamAV Pre-Screening**: Every incoming byte stream is scanned prior to S3 persistence.
- **Document Rendering Isolation**: `reconstruct-svc` operates within ephemeral pods with unprivileged user accounts (`uid=10001`), no network capabilities (`cap_drop: ALL`), and read-only root filesystems.
- **PDF Active Content Stripping**: All JavaScript, Action scripts, and external URI launch hooks are neutralized during rendering.

---

## 6. Data Protection at Rest and in Transit

- **In Transit**: TLS 1.3 mandated across external and internal endpoints (Cipher Suites: `TLS_AES_256_GCM_SHA384`, `TLS_CHACHA20_POLY1305_SHA256`).
- **At Rest**: AES-256-GCM encryption across PostgreSQL, Redis, Kafka, Qdrant, and MinIO storage volumes.

---

## 7. Security Incident Response Strategy

1. **MTTD (Mean Time to Detect)**: $\le 15$ minutes via automated SIEM alerting (Splunk/QRadar).
2. **Automated Isolation**: Suspected compromised pods are automatically quarantined by Istio `AuthorizationPolicy` blocking all inbound/outbound traffic.
3. **Key Revocation**: Instant HSM key rotation protocol triggers re-encryption of current session keys.

---

*Previous: [25_Object_Storage](../25_Object_Storage/README.md)*
*Next: [27_Cryptography](../27_Cryptography/README.md)*
*Return to: [Master Index](../README.md)*
