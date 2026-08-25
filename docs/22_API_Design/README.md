# Document 22 — API Design
## GDI: REST, gRPC, and Async API Specifications

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [01_Product_Requirements §4], [21_Backend_Architecture], [26_Security]

---

## Table of Contents

1. [Overview and API Philosophy](#1-overview-and-api-philosophy)
2. [Authentication and Headers](#2-authentication-and-headers)
3. [REST Endpoints Specification](#3-rest-endpoints-specification)
4. [gRPC Protobuf Service Contracts](#4-grpc-protobuf-service-contracts)
5. [Async Webhook Delivery](#5-async-webhook-delivery)
6. [Error Handling and Status Codes](#6-error-handling-and-status-codes)

---

## 1. Overview and API Philosophy

GDI exposes three external/internal API surfaces:
1. **Public REST API (OpenAPI 3.1)**: Synchronous and asynchronous HTTP interface for client integrations.
2. **Internal gRPC API**: High-performance binary interfaces between microservices.
3. **Webhook Notifications**: Real-time event delivery for asynchronous verification completion.

---

## 2. Authentication and Headers

All API calls must include:
- `Authorization: Bearer <JWT_TOKEN>`
- `X-GDI-Tenant-ID: <TENANT_UUID>`
- `X-Correlation-ID: <TRACE_UUID>` (Optional; auto-generated if omitted)

---

## 3. REST Endpoints Specification

### 3.1 Document Verification Submission
`POST /v1/jobs`

**Request (Multipart Form-Data)**:
- `file`: Document binary (PDF, TIFF, PNG, etc.)
- `template_id`: UUID of reference template
- `analysis_tier`: `STANDARD` | `ENHANCED` | `DEEP` (Default: `STANDARD`)
- `context_metadata`: JSON string (Up to 50 key-value pairs)

**Response (HTTP 202 Accepted)**:
```json
{
  "job_id": "job-12a3b4c5-d6e7-8f9a-0b1c-2d3e4f5a6b7c",
  "status": "INGESTED",
  "sha3_256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "created_at": "2026-07-21T18:50:00Z",
  "estimated_completion_seconds": 45,
  "links": {
    "status": "/v1/jobs/job-12a3b4c5-d6e7-8f9a-0b1c-2d3e4f5a6b7c",
    "report": "/v1/jobs/job-12a3b4c5-d6e7-8f9a-0b1c-2d3e4f5a6b7c/report"
  }
}
```

### 3.2 Get Job Status & Verdict
`GET /v1/jobs/{job_id}`

**Response (HTTP 200 OK)**:
```json
{
  "job_id": "job-12a3b4c5-d6e7-8f9a-0b1c-2d3e4f5a6b7c",
  "status": "COMPLETED",
  "verdict": {
    "category": "AUTHENTIC_HIGH_CONFIDENCE",
    "authenticity_score": 0.942,
    "confidence_score": 0.910
  },
  "completed_at": "2026-07-21T18:50:42Z"
}
```

---

## 4. gRPC Protobuf Service Contracts

Excerpt from internal protobuf definition (`proto/gdi/v1/orchestrator.proto`):

```protobuf
syntax = "proto3";
package gdi.v1;

service JobOrchestrator {
  rpc SubmitJob (SubmitJobRequest) returns (SubmitJobResponse);
  rpc StreamEngineResults (stream EngineResult) returns (JobStatusResponse);
}

message SubmitJobRequest {
  string job_id = 1;
  string tenant_id = 2;
  string template_id = 3;
  string raw_document_object_key = 4;
  string analysis_tier = 5;
}

message SubmitJobResponse {
  bool accepted = 1;
  string status = 2;
}
```

---

## 5. Async Webhook Delivery

When a job reaches a terminal status (`COMPLETED`, `PENDING_REVIEW`, `FAILED`), GDI dispatches an HTTP POST payload to the tenant's registered webhook URL.

**Security**: Payload is signed via HMAC-SHA256 using the tenant's webhook secret, delivered in header `X-GDI-Signature`.

---

## 6. Error Handling and Status Codes

Errors follow standard RFC 7807 Problem Details format:

```json
{
  "type": "https://gdi.forensics.ai/errors/FILE_SIZE_EXCEEDED",
  "title": "Payload Too Large",
  "status": 413,
  "detail": "Submitted document size (124 MB) exceeds tenant limit of 100 MB.",
  "instance": "/v1/jobs",
  "error_code": "ERR_SUB_004"
}
```

---

*Previous: [21_Backend_Architecture](../21_Backend_Architecture/README.md)*
*Next: [23_Database_Architecture](../23_Database_Architecture/README.md)*
*Return to: [Master Index](../README.md)*
