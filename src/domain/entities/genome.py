"""DocumentGenome domain entity."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


@dataclass
class GenomeSeal:
    """Soft integrity seal for the genome."""

    feature_count: int
    sha256_of_features: str
    sealed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    seal_type: str = "SHA256_SOFT"


@dataclass
class DocumentGenome:
    """Canonical Document Genome domain entity."""

    id: uuid.UUID
    job_id: uuid.UUID
    document_id: uuid.UUID
    schema_version: str
    pipeline_version: str
    feature_version: str
    processing_version: str
    config_fingerprint: str
    document_hash_sha256: str
    document_hash_sha3_256: str
    extraction_timestamp: datetime
    processing_duration_ms: float
    page_count: int
    pages: list[dict[str, Any]]
    feature_vector: list[float]
    genome_seal: GenomeSeal
    processing_manifest: dict[str, Any]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
