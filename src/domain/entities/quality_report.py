"""QualityReport domain entity."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


@dataclass
class QualityReport:
    """Page quality assessment report domain entity."""

    id: uuid.UUID
    page_id: uuid.UUID
    blur_score: float
    sharpness_score: float
    noise_score: float
    contrast_score: float
    metrics: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        page_id: uuid.UUID,
        blur_score: float,
        sharpness_score: float,
        noise_score: float,
        contrast_score: float,
        metrics: dict[str, Any],
    ) -> "QualityReport":
        return cls(
            id=uuid.uuid4(),
            page_id=page_id,
            blur_score=blur_score,
            sharpness_score=sharpness_score,
            noise_score=noise_score,
            contrast_score=contrast_score,
            metrics=metrics,
        )
