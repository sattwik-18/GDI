# Document 30 — Observability
## GDI: Monitoring, Logging, Tracing, and Alerting

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [01_Product_Requirements §16], [03_System_Architecture], [21_Backend_Architecture]

---

## Table of Contents

1. [Observability Philosophy](#1-observability-philosophy)
2. [Metrics Architecture (Prometheus)](#2-metrics-architecture-prometheus)
3. [Distributed Tracing (OpenTelemetry / Tempo)](#3-distributed-tracing-opentelemetry--tempo)
4. [Structured Centralized Logging (Loki)](#4-structured-centralized-logging-loki)
5. [SLO / SLA Monitoring & Dashboards](#5-slo--sla-monitoring--dashboards)
6. [Alerting Rules & Incident Escalation](#6-alerting-rules--incident-escalation)

---

## 1. Observability Philosophy

GDI implements full-stack observability across the **Four Golden Signals**: Latency, Traffic, Errors, and Saturation. Observability data is strictly correlated using OpenTelemetry trace propagation context across every microservice call.

---

## 2. Metrics Architecture (Prometheus)

All services expose a `/metrics` endpoint formatted for Prometheus scraping.

### 2.1 Key Custom Metrics Exposed

| Metric Name | Type | Description | Labels |
|-------------|------|-------------|--------|
| `gdi_jobs_ingested_total` | Counter | Total submitted documents | `tenant_id`, `tier` |
| `gdi_job_duration_seconds` | Histogram | End-to-end processing latency | `tier`, `verdict_category` |
| `gdi_engine_duration_seconds` | Histogram | Per-engine extraction latency | `engine_name`, `status` |
| `gdi_engine_divergence_index` | Gauge | Measure of engine disagreement | `job_id` |
| `gdi_gpu_utilization_ratio` | Gauge | GPU compute utilization | `gpu_id`, `model_name` |

---

## 3. Distributed Tracing (OpenTelemetry / Tempo)

- Every request is assigned a 128-bit W3C `traceparent` ID at the API Gateway.
- Context is propagated across HTTP/gRPC headers and Kafka record headers.
- Traces are exported via OpenTelemetry Collector to **Grafana Tempo**.

---

## 4. Structured Centralized Logging (Loki)

All microservices write JSON-formatted logs to `stdout`:

```json
{
  "timestamp": "2026-07-21T18:55:00.123456Z",
  "level": "ERROR",
  "service": "typography-engine",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "job_id": "job-12a3b4c5-d6e7-8f9a-0b1c-2d3e4f5a6b7c",
  "tenant_id": "t-enterprise-01",
  "message": "Font metrics mismatch detected on character 'e'",
  "error_code": "ERR_TYPO_009",
  "duration_ms": 142
}
```

Logs are collected by Promtail and indexed in **Grafana Loki**.

---

## 5. SLO / SLA Monitoring & Dashboards

- **SLA**: $99.95\%$ Uptime annually.
- **SLO 1**: $95\%$ of Standard Tier verification jobs complete in $\le 120\text{s}$.
- **SLO 2**: P99 API Gateway response time $\le 500\text{ms}$.

---

## 6. Alerting Rules & Incident Escalation

Alertmanager routes alerts based on severity:
- **P0 Critical** (Immediate Page via PagerDuty): Uptime $<99.9\%$, Job failure rate $>1\%$, Database failover.
- **P1 High** (Slack notification): P95 processing time $>150\text{s}$, GPU utilization $>90\%$ for 15m.

---

*Previous: [29_Deployment](../29_Deployment/README.md)*
*Next: [31_Testing](../31_Testing/README.md)*
*Return to: [Master Index](../README.md)*
