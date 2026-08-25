"""SQLAlchemy implementation of GenomeRepository."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.genome import DocumentGenome, GenomeSeal
from src.domain.interfaces.repositories import GenomeRepository
from src.infrastructure.database.models import GenomeModel


class SQLAlchemyGenomeRepository(GenomeRepository):
    """SQLAlchemy async implementation for DocumentGenome repository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, genome: DocumentGenome) -> None:
        model = GenomeModel(
            id=genome.id,
            job_id=genome.job_id,
            document_id=genome.document_id,
            schema_version=genome.schema_version,
            pipeline_version=genome.pipeline_version,
            feature_version=genome.feature_version,
            canonical_json=genome.pages,  # Store page array/canonical structure
            feature_vector=genome.feature_vector,
            seal_hash=genome.genome_seal.sha256_of_features,
            created_at=genome.created_at,
        )
        self._session.add(model)
        await self._session.flush()

    async def get_by_id(self, genome_id: uuid.UUID) -> DocumentGenome | None:
        stmt = select(GenomeModel).where(GenomeModel.id == genome_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def get_by_job_id(self, job_id: uuid.UUID) -> DocumentGenome | None:
        stmt = select(GenomeModel).where(GenomeModel.job_id == job_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def get_by_document_id(self, document_id: uuid.UUID) -> DocumentGenome | None:
        stmt = select(GenomeModel).where(GenomeModel.document_id == document_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    def _to_entity(self, model: GenomeModel) -> DocumentGenome:
        return DocumentGenome(
            id=model.id,
            job_id=model.job_id,
            document_id=model.document_id,
            schema_version=model.schema_version,
            pipeline_version=model.pipeline_version,
            feature_version=model.feature_version,
            processing_version="1.0.0",
            document_hash_sha256="",
            document_hash_sha3_256="",
            extraction_timestamp=model.created_at,
            processing_duration_ms=0.0,
            page_count=len(model.canonical_json) if isinstance(model.canonical_json, list) else 1,
            pages=model.canonical_json if isinstance(model.canonical_json, list) else [],
            feature_vector=list(model.feature_vector) if model.feature_vector else [],
            genome_seal=GenomeSeal(
                feature_count=len(model.feature_vector) if model.feature_vector else 0,
                sha256_of_features=model.seal_hash,
                sealed_at=model.created_at,
            ),
            processing_manifest={},
            created_at=model.created_at,
        )
