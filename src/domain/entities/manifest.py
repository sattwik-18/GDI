"""Processing Manifest domain entity with rich stage metrics."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


@dataclass
class ManifestStepRecord:
    """Detailed execution record for a single pipeline step."""

    step_name: str
    version: str
    start_timestamp: str
    finish_timestamp: str
    duration_ms: float
    status: str
    parameters: dict[str, Any] = field(default_factory=dict)
    configuration: dict[str, Any] = field(default_factory=dict)
    input_summary: dict[str, Any] = field(default_factory=dict)
    output_summary: dict[str, Any] = field(default_factory=dict)
    cpu_percent: float = 0.0
    memory_rss_mb: float = 0.0
    peak_memory_mb: float = 0.0
    retry_count: int = 0
    warnings: list[str] = field(default_factory=list)
    exception: str | None = None


@dataclass
class ProcessingManifest:
    """Execution log manifest of the entire document processing lifecycle."""

    id: uuid.UUID
    job_id: uuid.UUID
    total_duration_ms: float
    steps: list[ManifestStepRecord] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        job_id: uuid.UUID,
        total_duration_ms: float,
        steps: list[ManifestStepRecord],
    ) -> "ProcessingManifest":
        return cls(
            id=uuid.uuid4(),
            job_id=job_id,
            total_duration_ms=total_duration_ms,
            steps=steps,
        )
