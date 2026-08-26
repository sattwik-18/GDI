"""Modality-Aware Document Comparison API Endpoint."""

from __future__ import annotations
import json
import os
import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.dependencies import get_db
from src.config.settings import get_settings
from src.infrastructure.repositories.genome_repository import SQLAlchemyGenomeRepository
from src.processing.comparison.comparison_engine import ComparisonEngine
from src.schemas.comparison_schema import ComparisonRequest, ComparisonResponse
from src.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/genome/compare", tags=["comparison"])


async def _load_genome(genome_id: str, db: AsyncSession) -> dict[str, Any]:
    """Loads genome by UUID from PostgreSQL or local file storage fallback."""
    settings = get_settings()

    # 1. Try PostgreSQL repository first
    try:
        repo = SQLAlchemyGenomeRepository(db)
        genome = await repo.get_by_id(uuid.UUID(genome_id))
        if genome is not None:
            from src.api.v1.endpoints.genome import _genome_to_response
            return _genome_to_response(genome).model_dump()
    except Exception as e:
        logger.warning("db_load_failed_for_comparison", genome_id=genome_id, error=str(e))

    # 2. Try local disk storage
    local_path = os.path.join(settings.processing.storage_root, "genomes", f"{genome_id}.json")
    if os.path.exists(local_path):
        try:
            with open(local_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("local_genome_load_failed", path=local_path, error=str(e))

    raise HTTPException(status_code=404, detail=f"Genome with ID '{genome_id}' not found.")


@router.post(
    "",
    response_model=ComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare Two Document Genomes (Multi-Evidence)",
    description=(
        "Executes multi-stage, multi-evidence modality-aware comparison between two inputs. "
        "Produces an explicit decision, calibrated similarity, LightGlue local feature correspondences, "
        "layout graph topology, and deterministic evidence graph provenance."
    ),
)
async def compare_genomes(
    request: ComparisonRequest,
    db: AsyncSession = Depends(get_db),
) -> ComparisonResponse:
    # 1. Resolve Genome A
    genome_a = request.genome_a
    if not genome_a and request.genome_a_id:
        genome_a = await _load_genome(request.genome_a_id, db)

    # 2. Resolve Genome B
    genome_b = request.genome_b
    if not genome_b and request.genome_b_id:
        genome_b = await _load_genome(request.genome_b_id, db)

    if not genome_a or not genome_b:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either (genome_a, genome_b) objects or (genome_a_id, genome_b_id).",
        )

    # 3. Execute Comparison Engine
    engine = ComparisonEngine()
    result = engine.compare_documents(
        genome_a=genome_a,
        genome_b=genome_b,
        allow_specialized_face_matching=request.allow_specialized_face_matching,
    )

    return ComparisonResponse(
        status=result.status,
        mode=result.mode,
        decision=result.decision,
        decision_confidence=result.decision_confidence,
        reason=result.reason,
        similarity=result.similarity,
        confidence=result.confidence,
        dimensions=result.dimensions,
        differences=result.differences,
        positive_evidence=result.positive_evidence,
        negative_evidence=result.negative_evidence,
        evidence_vector=result.evidence_vector,
        evidence_ledger=result.evidence_ledger,
        calculation_trace=result.calculation_trace,
        model_provenances=result.model_provenances,
        field_alignment_status=result.field_alignment_status,
        verdict=result.verdict,
        input_a=result.input_a,
        input_b=result.input_b,
        explanation=result.explanation,
        available_action=result.available_action,
        calibration_version=result.calibration_version,
    )
