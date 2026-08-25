"""SQLAlchemy implementation of JobRepository."""

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.processing_job import ProcessingJob
from src.domain.interfaces.repositories import JobRepository
from src.infrastructure.database.models import ProcessingJobModel


class SQLAlchemyJobRepository(JobRepository):
    """SQLAlchemy async implementation for ProcessingJob repository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, job: ProcessingJob) -> None:
        stmt = select(ProcessingJobModel).where(ProcessingJobModel.id == job.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            model = ProcessingJobModel(
                id=job.id,
                document_id=job.document_id,
                status=job.status,
                created_at=job.created_at,
                completed_at=job.completed_at,
                error_details=job.error_details,
            )
            self._session.add(model)
        else:
            model.status = job.status
            model.completed_at = job.completed_at
            model.error_details = job.error_details

        await self._session.flush()

    async def get_by_id(self, job_id: uuid.UUID) -> ProcessingJob | None:
        stmt = select(ProcessingJobModel).where(ProcessingJobModel.id == job_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return ProcessingJob(
            id=model.id,
            document_id=model.document_id,
            status=model.status,
            error_details=model.error_details,
            created_at=model.created_at,
            completed_at=model.completed_at,
        )
