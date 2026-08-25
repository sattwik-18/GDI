# Document 24 — Vector Database
## GDI: High-Dimensional Genome Vector Storage and Retrieval

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [05_Genome_Extraction_Engine], [17_Similarity_Engine], [21_Backend_Architecture]

---

## Table of Contents

1. [Purpose and Requirements](#1-purpose-and-requirements)
2. [Vector Database Selection (Qdrant)](#2-vector-database-selection-qdrant)
3. [Vector Schema and Payload Structure](#3-vector-schema-and-payload-structure)
4. [HNSW Index Configuration](#4-hnsw-index-configuration)
5. [Similarity Search and Filtering](#5-similarity-search-and-filtering)
6. [Scaling and Sharding Topology](#6-scaling-and-sharding-topology)

---

## 1. Purpose and Requirements

The Vector Database enables high-speed, population-level similarity search across millions of stored Document Genomes. While pairwise template comparison is performed in memory by the Similarity Engine, the Vector Database enables:
- **Global Fraud Ring Discovery**: Detecting if a submitted document's genome matches previously submitted fraudulent documents across a tenant's history.
- **Template Identification**: Auto-matching an unlabelled document against a library of 100,000+ template genomes.

---

## 2. Vector Database Selection (Qdrant)

GDI selected **Qdrant** (distributed mode) as its core vector engine based on:
- High performance on high-dimensional dense vectors ($1,391$ to $3,168$ dimensions).
- Native payload filtering (enforcing tenant isolation in vector search).
- Rust implementation providing deterministic memory utilization and zero garbage collection pauses.

---

## 3. Vector Schema and Payload Structure

Vectors are stored in collections partitioned by tenant: `tenant_{tenant_id}_genomes`.

```json
{
  "id": "job-12a3b4c5-d6e7-8f9a-0b1c-2d3e4f5a6b7c",
  "vector": [0.0124, -0.0841, 0.3125, "... 1391 dimensions ..."],
  "payload": {
    "tenant_id": "t-enterprise-01",
    "template_id": "tmpl-9988",
    "document_type": "PASSPORT_EU",
    "pipeline_version": "1.0.0",
    "verdict_category": "FRAUDULENT_HIGH_CONFIDENCE",
    "created_at_timestamp": 1784659200
  }
}
```

---

## 4. HNSW Index Configuration

Qdrant is configured with Hierarchical Navigable Small World (HNSW) graphs:
- **`m`**: 16 (number of edges per node)
- **`ef_construct`**: 128 (construction search depth)
- **Distance Metric**: `Cosine`
- **On-Disk Storage**: In-memory HNSW graph with payload stored on mmap SSD for RAM optimization.

---

## 5. Similarity Search and Filtering

Searching for similar document genomes within a tenant's historical corpus:

```json
{
  "vector": [ "... query_genome_vector ... " ],
  "filter": {
    "must": [
      { "key": "document_type", "match": { "value": "PASSPORT_EU" } },
      { "key": "verdict_category", "match": { "value": "FRAUDULENT_HIGH_CONFIDENCE" } }
    ]
  },
  "top": 10,
  "params": {
    "hnsw_ef": 64,
    "exact": false
  }
}
```

---

## 6. Scaling and Sharding Topology

- **Sharding**: 6 shards per collection, distributed across 3 Qdrant node replicas.
- **Capacity**: Tested up to **50 Million vectors** ($1,391$-d) maintaining **P99 search latency < 42ms**.

---

*Previous: [23_Database_Architecture](../23_Database_Architecture/README.md)*
*Next: [25_Object_Storage](../25_Object_Storage/README.md)*
*Return to: [Master Index](../README.md)*
