# Document 49 — Data Model Specification
## GDI: Master Database Schemas, Protobuf Specifications, and Storage Contracts

**Version:** 2.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Authors:** Principal Architect, Chief Research Engineer, Technical Documentation Lead
**Cross-References:** [23_Database_Architecture], [24_Vector_Database], [25_Object_Storage], [38_Genome_Hierarchy], [39_Digital_Twin]

---

## Table of Contents

1. [Data Modeling Architecture](#1-data-modeling-architecture)
2. [PostgreSQL 16 Enterprise DDL Schemas](#2-postgresql-16-enterprise-ddl-schemas)
3. [Protobuf v3 Master Contract Definitions](#3-protobuf-v3-master-contract-definitions)
4. [Qdrant Vector DB Collection Schemas](#4-qdrant-vector-db-collection-schemas)
5. [Object Storage WORM Bucket Contracts](#5-object-storage-worm-bucket-contracts)

---

## 1. Data Modeling Architecture

GDI Version 2.0 enforces a polyglot persistence model with schema-level validation:
- **PostgreSQL 16**: Transactional records, Digital Twins, Audit Logs.
- **Protocol Buffers v3**: Binary serialization for Hierarchical Genomes, Engine Tasks, and Evidence Objects.
- **Qdrant**: Dense vector embeddings and ANN indexes.
- **S3 / MinIO**: Immutable WORM evidence packages and rendering modalities.

---

## 2. PostgreSQL 16 Enterprise DDL Schemas

```sql
CREATE SCHEMA IF NOT EXISTS digitaltwins;
CREATE SCHEMA IF NOT EXISTS evidence;

-- Digital Twins Master Table
CREATE TABLE digitaltwins.models (
    twin_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL,
    tenant_id UUID NOT NULL REFERENCES core.tenants(tenant_id),
    version BIGINT NOT NULL DEFAULT 1,
    sample_count BIGINT NOT NULL DEFAULT 1,
    status VARCHAR(50) NOT NULL CHECK (status IN ('UNINITIALIZED', 'PROVISIONAL', 'ACTIVE', 'DEPRECATED')),
    model_payload JSONB NOT NULL,
    hsm_signature BYTEA NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT uq_tenant_template_version UNIQUE (tenant_id, template_id, version)
);

-- Evidence Objects Log Table
CREATE TABLE evidence.evidence_records (
    evidence_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES jobs.job_records(job_id),
    tenant_id UUID NOT NULL,
    engine_id VARCHAR(100) NOT NULL,
    chromosome_id VARCHAR(100) NOT NULL,
    llr_score DOUBLE PRECISION NOT NULL,
    evidence_level VARCHAR(50) NOT NULL,
    reliability_score DOUBLE PRECISION NOT NULL,
    bounding_box JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
) PARTITION BY RANGE (created_at);
```

---

## 3. Protobuf v3 Master Contract Definitions

Excerpt from `proto/gdi/v2/master_contracts.proto`:

```protobuf
syntax = "proto3";
package gdi.v2.contracts;

import "google/protobuf/timestamp.proto";

message EngineTaskRequest {
  string task_id = 1;
  string job_id = 2;
  string tenant_id = 3;
  string engine_name = 4;
  string modality_object_key = 5;
  string digital_twin_id = 6;
  google.protobuf.Timestamp deadline = 7;
}

message EngineTaskResponse {
  string task_id = 1;
  string job_id = 2;
  string engine_name = 3;
  string status = 4; // SUCCESS, FAILED, TIMEOUT
  repeated string generated_evidence_ids = 5;
  int64 processing_time_ms = 6;
}
```

---

## 4. Qdrant Vector DB Collection Schemas

- **Collection Name**: `tenant_{tenant_id}_v2_genomes`
- **Vector Parameters**:
  - `size`: 1024 (DINOv2 global embedding) + 368 (key structural features) = 1392 dimensions.
  - `distance`: Cosine.
- **HNSW Parameters**: `m=16`, `ef_construct=128`.

---

## 5. Object Storage WORM Bucket Contracts

All objects are written using canonical key formats:
- `gdi-digital-twins/{tenant_id}/twin_{twin_id}_v{version}.pb`
- `gdi-genomes/{tenant_id}/{date}/{job_id}/genome_hierarchical.pb`
- `gdi-evidence-packages/{tenant_id}/{date}/{job_id}/evidence_package_v2.zip`

---

*Previous: [48_Forensic_Ontology](../48_Forensic_Ontology/README.md)*
*Next: [50_Engineering_Decision_Records](../50_Engineering_Decision_Records/README.md)*
*Return to: [Master Index](../README.md)*
