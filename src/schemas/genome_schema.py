"""Canonical Document Genome Pydantic schemas for validation and serialization."""

from __future__ import annotations

from datetime import datetime
from typing import Any
import uuid

from pydantic import BaseModel, Field, model_validator


class FeatureGroupSchema(BaseModel):
    """Schema for a single extracted feature group."""

    id: uuid.UUID
    name: str
    version: str
    feature_count: int = Field(ge=0)
    extraction_time_ms: float = Field(ge=0.0)
    features: dict[str, float | int | str] = Field(default_factory=dict)


class PageQualityMetricsSchema(BaseModel):
    """Quality metrics for a rendered page."""

    blur_score: float
    sharpness_score: float
    noise_score: float
    contrast_score: float
    metrics: dict[str, Any] = Field(default_factory=dict)


class PageMetadataSchema(BaseModel):
    """Dimensional metadata for a page."""

    page_id: uuid.UUID
    width_px: int = Field(ge=1)
    height_px: int = Field(ge=1)
    dpi: int = Field(ge=72)
    orientation_deg: int = Field(ge=0, le=360)
    skew_angle_deg: float = 0.0


class PageGenomeSchema(BaseModel):
    """Per-page genome layer containing all feature groups for that page."""

    page_number: int = Field(ge=1)
    metadata: PageMetadataSchema
    feature_groups: list[FeatureGroupSchema] = Field(default_factory=list)
    quality_metrics: PageQualityMetricsSchema | None = None
    ocr_element_count: int = 0
    layout_region_count: int = 0


class ManifestStepSchema(BaseModel):
    """Per-step execution record in the processing manifest."""

    step_name: str
    version: str
    start_timestamp: str
    finish_timestamp: str
    duration_ms: float
    status: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    configuration: dict[str, Any] = Field(default_factory=dict)
    input_summary: dict[str, Any] = Field(default_factory=dict)
    output_summary: dict[str, Any] = Field(default_factory=dict)
    cpu_percent: float = 0.0
    memory_rss_mb: float = 0.0
    peak_memory_mb: float = 0.0
    retry_count: int = 0
    warnings: list[str] = Field(default_factory=list)
    exception: str | None = None


class ProcessingManifestSchema(BaseModel):
    """Full execution log for the processing pipeline."""

    manifest_id: uuid.UUID
    job_id: uuid.UUID
    total_duration_ms: float
    step_count: int
    steps: list[ManifestStepSchema] = Field(default_factory=list)
    created_at: datetime


class GenomeSealSchema(BaseModel):
    """Integrity seal for the genome."""

    feature_count: int = Field(ge=0)
    sha256_of_features: str = Field(min_length=64, max_length=64)
    sealed_at: datetime
    seal_type: str = "SHA256_SOFT"


class DocumentGenomeSchema(BaseModel):
    """Canonical Document Genome schema — the primary output of Prototype 1."""

    genome_id: uuid.UUID
    job_id: uuid.UUID
    document_id: uuid.UUID
    schema_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    pipeline_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    feature_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    processing_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    config_fingerprint: str = Field(default="", min_length=0, max_length=64)
    document_hash_sha256: str = Field(min_length=64, max_length=64)
    document_hash_sha3_256: str = Field(min_length=64, max_length=64)
    extraction_timestamp: datetime
    processing_duration_ms: float = Field(ge=0.0)
    page_count: int = Field(ge=1)
    pages: list[PageGenomeSchema]
    feature_vector: list[float]
    genome_seal: GenomeSealSchema
    processing_manifest: ProcessingManifestSchema
    structural_genome: dict[str, Any] | None = None
    semantic_genome: dict[str, Any] | None = None
    visual_genome: dict[str, Any] | None = None
    template_genome: dict[str, Any] | None = None
    evidence_graph: dict[str, Any] | None = None

    @model_validator(mode="after")
    def validate_page_count_consistency(self) -> DocumentGenomeSchema:
        if len(self.pages) != self.page_count:
            raise ValueError(
                f"page_count ({self.page_count}) does not match actual pages list length ({len(self.pages)})"
            )
        return self

    @model_validator(mode="after")
    def validate_seal_feature_count(self) -> DocumentGenomeSchema:
        if self.genome_seal.feature_count != len(self.feature_vector):
            raise ValueError(
                f"Seal feature_count ({self.genome_seal.feature_count}) does not match "
                f"feature_vector length ({len(self.feature_vector)})"
            )
        return self
