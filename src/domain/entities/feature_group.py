"""FeatureGroup domain entity with deterministic UUID generation and JSON float sanitization."""

from dataclasses import dataclass, field
import math
from typing import Any
import uuid


@dataclass
class FeatureGroup:
    """Standardized collection of features from an extractor."""

    id: uuid.UUID
    name: str
    version: str
    feature_count: int
    extraction_time_ms: float
    features: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        name: str,
        version: str,
        extraction_time_ms: float,
        features: dict[str, Any],
    ) -> "FeatureGroup":
        # Sanitize any NaN or Inf floating point values to 0.0 for deterministic JSON compliance
        sanitized_features: dict[str, Any] = {}
        for k, v in features.items():
            if isinstance(v, float):
                if math.isnan(v) or math.isinf(v):
                    sanitized_features[k] = 0.0
                else:
                    sanitized_features[k] = v
            else:
                sanitized_features[k] = v

        # Generate deterministic UUID5 derived from name + version namespace
        namespace = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
        deterministic_id = uuid.uuid5(namespace, f"{name}:{version}")
        return cls(
            id=deterministic_id,
            name=name,
            version=version,
            feature_count=len(sanitized_features),
            extraction_time_ms=extraction_time_ms,
            features=sanitized_features,
        )
