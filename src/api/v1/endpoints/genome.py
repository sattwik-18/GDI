"""Document upload and genome generation endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.dependencies import get_db
from src.application.use_cases.generate_genome import GenerateGenomeUseCase
from src.schemas.responses import GenomeResponse, GenomeSealResponse

router = APIRouter(prefix="/genome", tags=["genome"])


def _genome_to_response(genome) -> GenomeResponse:
    return GenomeResponse(
        genome_id=str(genome.id),
        job_id=str(genome.job_id),
        document_id=str(genome.document_id),
        schema_version=genome.schema_version,
        pipeline_version=genome.pipeline_version,
        feature_version=genome.feature_version,
        processing_version=genome.processing_version,
        document_hash_sha256=genome.document_hash_sha256,
        document_hash_sha3_256=genome.document_hash_sha3_256,
        extraction_timestamp=genome.extraction_timestamp.isoformat(),
        processing_duration_ms=genome.processing_duration_ms,
        page_count=genome.page_count,
        feature_vector=genome.feature_vector,
        genome_seal=GenomeSealResponse(
            feature_count=genome.genome_seal.feature_count,
            sha256_of_features=genome.genome_seal.sha256_of_features,
            sealed_at=genome.genome_seal.sealed_at.isoformat(),
            seal_type=genome.genome_seal.seal_type,
        ),
        pages=genome.pages,
        processing_manifest=genome.processing_manifest,
    )


@router.post(
    "",
    response_model=GenomeResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Document Genome",
    description=(
        "Upload a document (PDF, PNG, JPEG, TIFF, BMP, WebP) to run the full "
        "Genome Extraction Engine pipeline and receive a canonical Document Genome."
    ),
)
async def generate_genome(
    file: UploadFile = File(..., description="Document to process"),
    db: AsyncSession = Depends(get_db),
) -> GenomeResponse:
    file_bytes = await file.read()
    mime_type = file.content_type or "application/octet-stream"
    filename = file.filename or "upload.bin"

    use_case = GenerateGenomeUseCase(session=db)
    genome = await use_case.execute(
        file_bytes=file_bytes,
        filename=filename,
        mime_type=mime_type,
    )
    return _genome_to_response(genome)


@router.get(
    "/{genome_id}",
    response_model=GenomeResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve stored genome by ID",
    description="Returns a previously generated Document Genome by its UUID.",
)
async def get_genome(
    genome_id: str,
    db: AsyncSession = Depends(get_db),
) -> GenomeResponse:
    import json
    import os
    import uuid as _uuid
    from src.config.settings import get_settings
    from src.domain.exceptions import ResourceNotFoundError
    from src.infrastructure.repositories.genome_repository import SQLAlchemyGenomeRepository
    from src.utils.logging import get_logger

    logger = get_logger(__name__)
    settings = get_settings()

    # 1. Try PostgreSQL repository first
    try:
        repo = SQLAlchemyGenomeRepository(db)
        genome = await repo.get_by_id(_uuid.UUID(genome_id))
        if genome is not None:
            return _genome_to_response(genome)
    except Exception as e:
        logger.warning(
            "database_query_bypassed_for_get_genome",
            genome_id=genome_id,
            error=str(e),
        )

    # 2. Fallback to local file storage
    local_genome_path = os.path.join(settings.processing.storage_root, "genomes", f"{genome_id}.json")
    if os.path.exists(local_genome_path):
        try:
            with open(local_genome_path, "r", encoding="utf-8") as f:
                genome_data = json.load(f)
            return GenomeResponse.model_validate(genome_data)
        except Exception as e:
            logger.error(
                "local_genome_json_parse_failed",
                genome_id=genome_id,
                file_path=local_genome_path,
                error=str(e),
            )

    # 3. Not found in DB or disk storage
    raise ResourceNotFoundError("Genome", genome_id)
