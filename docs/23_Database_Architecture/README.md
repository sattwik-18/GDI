# Document 23 — Database Architecture
## GDI: Relational, Document, and Time-Series Databases

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [03_System_Architecture §6], [04_Data_Flow], [26_Security], [27_Cryptography]

---

## Table of Contents

1. [Database Architecture Overview](#1-database-architecture-overview)
2. [Relational Data Model (PostgreSQL 16)](#2-relational-data-model-postgresql-16)
3. [Immutable Audit Log Schema](#3-immutable-audit-log-schema)
4. [Indexing and Query Optimization](#4-indexing-and-query-optimization)
5. [High Availability and Replication](#5-high-availability-and-replication)
6. [Data Backup and Disaster Recovery](#6-data-backup-and-disaster-recovery)

---

## 1. Database Architecture Overview

GDI relies on **PostgreSQL 16** as its primary relational store for transactional entities, tenant management, template metadata, job lifecycles, and immutable audit logs. Relational integrity, row-level security (RLS), and schema partitioning are strictly enforced.

---

## 2. Relational Data Model (PostgreSQL 16)

### 2.1 Core Schema DDL (Excerpt)

```sql
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS jobs;
CREATE SCHEMA IF NOT EXISTS templates;
CREATE SCHEMA IF NOT EXISTS audit;

-- Tenants Table
CREATE TABLE core.tenants (
    tenant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    tier VARCHAR(50) NOT NULL CHECK (tier IN ('PROFESSIONAL', 'ENTERPRISE', 'GOVERNMENT')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    is_active BOOLEAN NOT NULL DEFAULT true
);

-- Jobs Table
CREATE TABLE jobs.job_records (
    job_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES core.tenants(tenant_id),
    template_id UUID NOT NULL,
    status VARCHAR(50) NOT NULL,
    sha3_256 BYTEA NOT NULL,
    analysis_tier VARCHAR(20) NOT NULL,
    pipeline_version VARCHAR(20) NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    context_metadata JSONB,
    CONSTRAINT fk_jobs_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants(tenant_id)
) PARTITION BY RANGE (ingested_at);

-- Row-Level Security (RLS) Policy
ALTER TABLE jobs.job_records ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_policy ON jobs.job_records
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);
```

---

## 3. Immutable Audit Log Schema

Per **REQ-SEC-005**, audit logs must be append-only and tamper-evident.

```sql
CREATE TABLE audit.events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    actor_id VARCHAR(255) NOT NULL,
    tenant_id UUID NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(255) NOT NULL,
    payload JSONB NOT NULL,
    prev_hash BYTEA,
    event_hash BYTEA NOT NULL
) PARTITION BY RANGE (timestamp);

-- Prohibit UPDATE and DELETE on audit log
CREATE RULE audit_no_update AS ON UPDATE TO audit.events DO INSTEAD NOTHING;
CREATE RULE audit_no_delete AS ON DELETE TO audit.events DO INSTEAD NOTHING;
```

---

## 4. Indexing and Query Optimization

- **B-Tree Indexes**: Applied to `job_id`, `tenant_id`, and `template_id` for $O(\log N)$ point lookups.
- **GIN Indexes**: Applied to `context_metadata` (JSONB) to allow fast querying over caller-provided metadata keys.
- **BRIN Indexes**: Applied to `ingested_at` and `timestamp` on partitioned tables to maintain minimal index overhead on time-series append workloads.

---

## 5. High Availability and Replication

- **Patroni Cluster**: Managed 3-node PostgreSQL cluster (1 Primary, 2 Synchronous Replicas) with automated DCS-based failover (using etcd).
- **Zero Data Loss Guarantee**: Synchronous replication (`synchronous_commit = on`) ensures transactions are committed to at least one standby before acknowledging success.

---

## 6. Data Backup and Disaster Recovery

- **WAL Archiving**: Continuous Write-Ahead Log (WAL) archiving to Object Storage via `pgBackRest`.
- **Point-in-Time Recovery (PITR)**: Enables rolling back database state to any specific nanosecond within a 30-day window.
- **RPO / RTO SLAs**: RPO $\le 0$ seconds (synchronous standby), RTO $\le 5$ minutes (Patroni failover).

---

*Previous: [22_API_Design](../22_API_Design/README.md)*
*Next: [24_Vector_Database](../24_Vector_Database/README.md)*
*Return to: [Master Index](../README.md)*
