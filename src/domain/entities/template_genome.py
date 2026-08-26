"""Template Intelligence and Evolution Domain Entities.

Encapsulates multi-modal template matching, structural/visual drift scoring,
cross-engine disagreement detection, and template evolution lineage.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


@dataclass
class AnomalySignal:
    """A detected anomaly or cross-engine discrepancy in the document."""

    signal_id: str
    category: str  # "STRUCTURAL_DRIFT", "VISUAL_DRIFT", "FORENSIC_TAMPER", "OCR_DISAGREEMENT", "LAYOUT_SHIFT"
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    description: str
    page_number: int = 1
    bbox: list[list[float]] = field(default_factory=list)
    confidence: float = 1.0
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class TemplateMatchResult:
    """Result of querying the template registry for nearest matching template."""

    is_matched: bool = False
    template_id: str | None = None
    template_name: str | None = None
    issuer_name: str | None = None
    version: str = "1.0.0"
    overall_similarity: float = 0.0  # Combined multi-modal similarity 0.0 - 1.0
    structural_similarity: float = 0.0
    visual_similarity: float = 0.0
    text_similarity: float = 0.0
    forensic_similarity: float = 0.0


@dataclass
class TemplateGenome:
    """Complete template intelligence and drift analysis genome layer."""

    genome_id: uuid.UUID = field(default_factory=uuid.uuid4)
    match_result: TemplateMatchResult = field(default_factory=TemplateMatchResult)
    structural_drift_score: float = 0.0  # 0.0 (identical) to 1.0 (completely altered)
    visual_drift_score: float = 0.0
    is_anomaly: bool = False
    anomaly_signals: list[AnomalySignal] = field(default_factory=list)
    template_evolution_parent: str | None = None
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
