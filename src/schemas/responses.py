"""Standardized API response and error schemas."""

from datetime import datetime, timezone
from typing import Any
import uuid

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """RFC 7807-inspired error response."""

    request_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status_code: int
    error: ErrorDetail


class UploadResponse(BaseModel):
    """Response returned when a document is uploaded."""

    job_id: str
    document_id: str
    status: str = "INGESTED"
    sha256: str
    original_filename: str
    size_bytes: int
    created_at: str


class GenomeSealResponse(BaseModel):
    feature_count: int
    sha256_of_features: str
    sealed_at: str
    seal_type: str


class GenomeResponse(BaseModel):
    """Response returned when genome extraction completes."""

    genome_id: str
    job_id: str
    document_id: str
    schema_version: str
    pipeline_version: str
    feature_version: str
    processing_version: str
    config_fingerprint: str = ""
    document_hash_sha256: str
    document_hash_sha3_256: str
    extraction_timestamp: str
    processing_duration_ms: float
    page_count: int
    feature_vector: list[float]
    genome_seal: GenomeSealResponse
    pages: list[dict[str, Any]]
    processing_manifest: dict[str, Any]


class ComponentHealth(BaseModel):
    status: str  # healthy, degraded, unhealthy
    latency_ms: float = 0.0
    details: dict[str, Any] = Field(default_factory=dict)


class BuildInfoSchema(BaseModel):
    app_version: str
    git_commit: str
    build_date: str
    python_version: str
    schema_version: str
    feature_version: str
    pipeline_version: str


class HealthResponse(BaseModel):
    """Comprehensive component health check response."""

    status: str
    version: str
    environment: str
    timestamp: str
    components: dict[str, ComponentHealth] = Field(default_factory=dict)
    build_info: BuildInfoSchema | None = None
