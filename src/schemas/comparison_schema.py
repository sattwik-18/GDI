"""Pydantic schemas for the Document & Media Comparison endpoint with Provenance & Ledger."""

from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field

from src.domain.entities.comparison import (
    CalculationTrace,
    ComparisonDimensions,
    ComparisonMode,
    ComparisonStatus,
    EvidenceLedgerEntry,
    InputDescriptor,
    LocalizedDifference,
    ModelExecutionProvenance,
)


class ComparisonRequest(BaseModel):
    """Payload for comparing two document genomes."""

    genome_a_id: str | None = None
    genome_b_id: str | None = None
    genome_a: dict[str, Any] | None = None
    genome_b: dict[str, Any] | None = None
    allow_specialized_face_matching: bool = False


class ComparisonResponse(BaseModel):
    """Structured response for multi-evidence modality-aware comparison."""

    status: ComparisonStatus
    mode: ComparisonMode | None = None
    decision: str
    decision_confidence: float
    reason: str
    similarity: float | None = None
    confidence: float
    dimensions: ComparisonDimensions
    differences: list[LocalizedDifference] = Field(default_factory=list)
    positive_evidence: list[str] = Field(default_factory=list)
    negative_evidence: list[str] = Field(default_factory=list)
    evidence_vector: dict[str, float | None] = Field(default_factory=dict)
    evidence_ledger: list[EvidenceLedgerEntry] = Field(default_factory=list)
    calculation_trace: CalculationTrace | None = None
    model_provenances: list[ModelExecutionProvenance] = Field(default_factory=list)
    field_alignment_status: str = "NOT_APPLICABLE"
    verdict: str
    input_a: InputDescriptor | None = None
    input_b: InputDescriptor | None = None
    explanation: str
    available_action: str | None = None
    calibration_version: str = "3.0.0"
