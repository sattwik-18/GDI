# Document 20 — Forensic Report Generator
## GDI: Structured Forensic Report Generation and Evidence Packaging

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [01_Product_Requirements §6], [04_Data_Flow §7], [19_Decision_Engine], [27_Cryptography]

---

## Table of Contents

1. [Purpose and Requirements](#1-purpose-and-requirements)
2. [Report Artifact Types](#2-report-artifact-types)
3. [JSON Machine-Readable Report Schema](#3-json-machine-readable-report-schema)
4. [PDF Legal Forensic Report Layout](#4-pdf-legal-forensic-report-layout)
5. [Evidence Packaging and WORM Storage](#5-evidence-packaging-and-worm-storage)
6. [Cryptographic Signature and Chain of Custody](#6-cryptographic-signature-and-chain-of-custody)

---

## 1. Purpose and Requirements

The Forensic Report Generator transforms raw internal analysis artifacts into legally defensible, standardized reports. 

Per **REQ-RPT-001** and **REQ-RPT-002**, reports must be produced in both machine-readable (JSON) and human-readable (PDF/A-3) formats, bound with complete cryptographic chain-of-custody documentation.

---

## 2. Report Artifact Types

1. **`forensic_report.json`**: Machine-readable schema for downstream automated API ingestion.
2. **`forensic_report.pdf`**: PDF/A-3 compliant document designed for legal proceedings, regulatory submission, and human review.
3. **`evidence_package.zip`**: WORM-locked container containing raw binary, heatmaps, per-engine outputs, JSON/PDF reports, and HSM signature block.

---

## 3. JSON Machine-Readable Report Schema (v1.0)

```json
{
  "$schema": "https://gdi.forensics.ai/schemas/v1/report.json",
  "report_id": "rpt-98f2b3a1-c4d5-4e6f-8a1b-2c3d4e5f6a7b",
  "job_id": "job-12a3b4c5-d6e7-8f9a-0b1c-2d3e4f5a6b7c",
  "tenant_id": "t-enterprise-01",
  "timestamp_utc": "2026-07-21T18:45:00.123456Z",
  "pipeline_version": "1.0.0",
  "document_metadata": {
    "filename": "submitted_contract.pdf",
    "sha3_256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "file_size_bytes": 2458920,
    "page_count": 1
  },
  "verdict": {
    "category": "FRAUDULENT_HIGH_CONFIDENCE",
    "authenticity_score": 0.082,
    "calibrated_probability": 0.079,
    "anomaly_score": 0.914,
    "confidence_score": 0.895,
    "uncertainty_interval_95": [0.051, 0.112],
    "human_review_required": false
  },
  "score_decomposition": {
    "engine_scores": {
      "layout": {"similarity": 0.94, "anomaly": 0.05, "confidence": 0.95},
      "typography": {"similarity": 0.31, "anomaly": 0.88, "confidence": 0.92},
      "rendering": {"similarity": 0.45, "anomaly": 0.72, "confidence": 0.88},
      "micro_dna": {"similarity": 0.12, "anomaly": 0.95, "confidence": 0.90}
    },
    "top_contributing_features": [
      {
        "feature_id": "microdna.edge.subpixel_jitter_std",
        "measured_value": 0.42,
        "expected_value": 0.08,
        "z_score": 4.25,
        "impact_weight": 0.28
      }
    ]
  },
  "chain_of_custody": {
    "hsm_key_id": "arn:aws:kms:us-east-1:123456789012:key/gdi-forensic-signing-key",
    "signature_algorithm": "ECDSA_P384_SHA384",
    "signature_base64": "MGUCMQC..."
  }
}
```

---

## 4. PDF Legal Forensic Report Layout

The PDF report adheres to Federal Rules of Evidence Rule 702 (USA) and ENFSI Guidelines (EU) for expert witness evidence:

- **Header / Banner**: GDI Seal, Security Classification, Unique Report ID.
- **Section 1: Executive Summary**: Verdict badge, primary score metrics, clear binary recommendation.
- **Section 2: Document Chain of Custody**: Cryptographic hashes, ingestion timestamp, platform version.
- **Section 3: Key Forensic Findings**: Annotated high-resolution document image with spatial anomaly heatmap overlay.
- **Section 4: Engine-by-Engine Evidence Breakdown**: Table of 10 engine scores and top feature anomalies.
- **Section 5: Reconstructed Creation Pipeline**: Inferred software, printer, and editing history.
- **Section 6: Statement of Methodology & Limitations**: Formal scientific limitations and 95% confidence intervals.
- **Footer**: Digital Signature verification mark.

---

## 5. Evidence Packaging and WORM Storage

The `evidence_package.zip` is structured canonically:

```
evidence_package.zip
├── manifest.json
├── original_document.pdf
├── reconstructed/
│   ├── page_1_300dpi.png
│   └── pdf_objects.xml
├── heatmaps/
│   ├── master_anomaly_heatmap.png
│   └── typography_heatmap.png
├── reports/
│   ├── forensic_report.json
│   └── forensic_report.pdf
└── security/
    ├── chain_of_custody.log
    └── signature_block.sig
```

The ZIP is written directly to an S3/MinIO bucket configured with **WORM (Write-Once-Read-Many) Object Lock** in Compliance mode.

---

## 6. Cryptographic Signature and Chain of Custody

1. Compute $H = \text{SHA3-512}(\text{evidence\_package.zip})$.
2. Submit $H$ to HSM via PKCS#11 interface.
3. HSM signs $H$ using an ECDSA P-384 private key.
4. Output signature block and public certificate chain are attached to the job record in PostgreSQL and stored alongside the ZIP artifact.

---

*Previous: [19_Decision_Engine](../19_Decision_Engine/README.md)*
*Next: [21_Backend_Architecture](../21_Backend_Architecture/README.md)*
*Return to: [Master Index](../README.md)*
