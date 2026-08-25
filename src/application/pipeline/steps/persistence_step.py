"""PersistenceStep: persists Document, Job, and Genome records to storage and database (with graceful fallback)."""

import os
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.context.processing_context import ProcessingContext
from src.application.pipeline.base import PipelineStep
from src.domain.entities.processing_job import ProcessingJob
from src.domain.exceptions import ProcessingError
from src.infrastructure.repositories.document_repository import SQLAlchemyDocumentRepository
from src.infrastructure.repositories.genome_repository import SQLAlchemyGenomeRepository
from src.infrastructure.repositories.job_repository import SQLAlchemyJobRepository
from src.infrastructure.storage.local_storage import LocalStorageProvider
from src.config.settings import get_settings
from src.utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class PersistenceStep(PipelineStep):
    """Pipeline step 16: Persist document, job, and genome to local file storage and PostgreSQL database."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._storage = LocalStorageProvider(base_directory=settings.processing.storage_root)
        self._doc_repo = SQLAlchemyDocumentRepository(session)
        self._job_repo = SQLAlchemyJobRepository(session)
        self._genome_repo = SQLAlchemyGenomeRepository(session)

    @property
    def name(self) -> str:
        return "PersistenceStep"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        if context.document is None:
            raise ProcessingError("Cannot persist: document entity not populated.", step_name=self.name)
        if context.genome is None:
            raise ProcessingError("Cannot persist: genome entity not populated.", step_name=self.name)

        # 1. Store original file to local storage (always mandatory)
        ext = context.original_filename.split(".")[-1].lower() if "." in context.original_filename else "bin"
        file_dest = os.path.join("uploads", str(context.document.id), f"original.{ext}")
        stored_path = await self._storage.save_file(context.uploaded_file_bytes, file_dest)
        context.document.file_path = stored_path

        # 2. Store serialized genome JSON to local storage (always mandatory)
        if context.serialized_genome_json:
            genome_dest = os.path.join("genomes", f"{context.genome.id}.json")
            await self._storage.save_file(context.serialized_genome_json.encode("utf-8"), genome_dest)

        # 2. Persist to PostgreSQL database (graceful fallback if DB is unconfigured/unreachable)
        try:
            await self._doc_repo.save(context.document)

            job = ProcessingJob.create(document_id=context.document.id)
            job.id = context.job_id
            job.mark_completed()
            context.job = job
            await self._job_repo.save(job)

            context.genome.job_id = context.job_id
            context.genome.document_id = context.document.id
            await self._genome_repo.save(context.genome)
            logger.info("database_persistence_successful", job_id=str(context.job_id))
        except Exception as e:
            try:
                await self._session.rollback()
            except Exception:
                pass

            if not settings.database.database_optional:
                logger.error("database_persistence_failed_production", job_id=str(context.job_id), error=str(e))
                raise ProcessingError(
                    f"Database persistence failed and DATABASE_OPTIONAL=false ({type(e).__name__}: {str(e)})",
                    step_name=self.name,
                ) from e

            logger.warning("database_persistence_bypassed", job_id=str(context.job_id), error=str(e))
            context.add_warning(
                self.name,
                f"Database persistence bypassed ({type(e).__name__}: {str(e)})"
            )

        return context
