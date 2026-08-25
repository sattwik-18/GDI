# Document 25 — Object Storage
## GDI: Immutable Artifact and Evidence Storage

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [04_Data_Flow], [20_Forensic_Report_Generator], [26_Security], [27_Cryptography]

---

## Table of Contents

1. [Storage Architecture & Bucket Taxonomy](#1-storage-architecture--bucket-taxonomy)
2. [WORM Object Lock Compliance](#2-worm-object-lock-compliance)
3. [Server-Side Encryption (SSE-KMS)](#3-server-side-encryption-sse-kms)
4. [Lifecycle & Retention Policies](#4-lifecycle--retention-policies)
5. [MinIO and AWS S3 Feature Parity](#5-minio-and-aws-s3-feature-parity)

---

## 1. Storage Architecture & Bucket Taxonomy

GDI utilizes S3-compatible object storage (Amazon S3 for SaaS; MinIO enterprise cluster for on-premise/government). 

### 1.1 Bucket Hierarchy
- **`gdi-raw-documents`**: Stores original uploaded binaries.
- **`gdi-reconstructed-modalities`**: Stores rendered PNG/TIFF/XML modality maps.
- **`gdi-genomes`**: Stores serialized Protocol Buffer genome records.
- **`gdi-reports`**: Stores generated PDF and JSON reports.
- **`gdi-evidence-packages`**: Stores final WORM-locked forensic `.zip` packages.

---

## 2. WORM Object Lock Compliance

To comply with legal evidence chain-of-custody standards (**REQ-SEC-005**), `gdi-evidence-packages` enforces S3 **Object Lock in COMPLIANCE Mode**:
- **Mechanism**: Once written, an object version cannot be overwritten, modified, or deleted by any IAM user or root account until the retention duration expires (default: 7 years).
- **Enforcement**: Enforced at the S3 API level via `PutObjectRetention`.

---

## 3. Server-Side Encryption (SSE-KMS)

- All buckets mandate Server-Side Encryption with Customer Managed Keys (SSE-KMS).
- Keys are managed in AWS KMS or Thales Luna HSM.
- Envelope Encryption: A unique Data Encryption Key (DEK) encrypts each object; the DEK is encrypted with the tenant's Key Encryption Key (KEK).

---

## 4. Lifecycle & Retention Policies

```json
{
  "Rules": [
    {
      "ID": "PurgeTemporaryModalities",
      "Status": "Enabled",
      "Filter": { "Prefix": "reconstructed/" },
      "Expiration": { "Days": 30 }
    },
    {
      "ID": "ArchiveEvidencePackages",
      "Status": "Enabled",
      "Filter": { "Prefix": "evidence/" },
      "Transitions": [
        { "Days": 90, "StorageClass": "GLACIER_IR" },
        { "Days": 365, "StorageClass": "DEEP_ARCHIVE" }
      ]
    }
  ]
}
```

---

## 5. MinIO and AWS S3 Feature Parity

For air-gapped government installations:
- MinIO Enterprise is deployed across a 4-node cluster with Erasure Coding ($EC:4$).
- Supports native Object Lock, TLS 1.3, SSE-KMS via HashiCorp Vault / KMS integration, and identical S3 API calls.

---

*Previous: [24_Vector_Database](../24_Vector_Database/README.md)*
*Next: [26_Security](../26_Security/README.md)*
*Return to: [Master Index](../README.md)*
