# Document 27 — Cryptography
## GDI: Cryptographic Design, Key Management, and Provenance

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [01_Product_Requirements §11], [05_Genome_Extraction_Engine §8], [20_Forensic_Report_Generator], [26_Security]

---

## Table of Contents

1. [Cryptographic Principles](#1-cryptographic-principles)
2. [Supported Algorithms & Standards](#2-supported-algorithms--standards)
3. [Key Management Architecture (HSM)](#3-key-management-architecture-hsm)
4. [Envelope Encryption Model](#4-envelope-encryption-model)
5. [Cryptographic Chain of Custody](#5-cryptographic-chain-of-custody)
6. [FIPS 140-3 Compliance](#6-fips-140-3-compliance)

---

## 1. Cryptographic Principles

GDI relies on cryptography to guarantee **integrity, authenticity, non-repudiation, and confidentiality**. No forensic verdict or report is emitted without a verifiable cryptographic signature linked to an HSM root of trust.

---

## 2. Supported Algorithms & Standards

| Purpose | Algorithm / Primitive | Key Length / Parameters | Standard |
|---------|-----------------------|-------------------------|----------|
| **Hashing** | SHA3-256 / SHA3-512 | 256-bit / 512-bit | NIST FIPS 202 |
| **Digital Signatures** | ECDSA | Curve P-384 / SHA-384 | NIST FIPS 186-5 |
| **Symmetric Encryption** | AES-GCM | 256-bit (12-byte IV, 16-byte Tag) | NIST SP 800-38D |
| **Key Derivation** | HKDF-SHA512 | 512-bit output | RFC 5869 |
| **TLS Key Exchange** | ECDHE | Curve P-384 / X25519 | RFC 8446 (TLS 1.3) |

---

## 3. Key Management Architecture (HSM)

Key operations are managed via hardware isolation:
- **SaaS Deployment**: AWS CloudHSM (FIPS 140-3 Level 3 validated).
- **Government Deployment**: Thales Luna PCIe HSM / Network HSM (FIPS 140-3 Level 3).

```
┌────────────────────────────────────────────────────────┐
│                   HSM (Hardware Boundary)              │
│  [ Master Root Key (KMR) ]                             │
│        │                                               │
│        └──▶ [ Tenant Key Encryption Key (KEK_Tenant) ] │
└──────────────────────────┬─────────────────────────────┘
                           │ Encrypts DEK
                           ▼
┌────────────────────────────────────────────────────────┐
│                 Application Memory (RAM)               │
│  [ Data Encryption Key (DEK) ] ──▶ Encrypts Document   │
└────────────────────────────────────────────────────────┘
```

---

## 4. Envelope Encryption Model

1. **Object Upload**: Ingestion service requests a new Data Encryption Key (`DEK`) from KMS/HSM for `job_id`.
2. **Encryption**: Document binary is encrypted locally using `AES-256-GCM` with the plaintext `DEK`.
3. **Storage**: The plaintext `DEK` is wiped from memory; the encrypted `DEK` (wrapped by `KEK_Tenant`) is stored alongside the encrypted binary payload in Object Storage.

---

## 5. Cryptographic Chain of Custody

The chain of custody is a cryptographically linked hash chain:

$$H_0 = \text{SHA3-256}(\text{Raw\_Document\_Binary})$$
$$H_1 = \text{SHA3-256}(H_0 \,\|\, \text{Reconstruction\_Manifest})$$
$$H_2 = \text{SHA3-512}(H_1 \,\|\, \text{Serialized\_Genome\_Proto})$$
$$H_3 = \text{SHA3-512}(H_2 \,\|\, \text{Fusion\_Verdict\_Record})$$

$$\text{Final\_Signature} = \text{ECDSA\_Sign}_{K_{HSM}}(H_3)$$

Any alteration to raw binary, intermediate modalities, or final scores breaks the verification chain $H_0 \to H_3$.

---

## 6. FIPS 140-3 Compliance

For government-tier deployments:
- All cryptographic libraries use **Bouncy Castle FIPS Java API** or **OpenSSL FIPS Provider 3.0**.
- Non-FIPS algorithms (e.g., MD5, SHA-1, RSA-1024) are programmatically disabled via FIPS mode flags.

---

*Previous: [26_Security](../26_Security/README.md)*
*Next: [28_Infrastructure](../28_Infrastructure/README.md)*
*Return to: [Master Index](../README.md)*
