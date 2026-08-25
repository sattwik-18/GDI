"""GenerateGenome use case: orchestrates the complete genome extraction pipeline using PipelineRegistry."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.context.processing_context import ProcessingContext
from src.application.pipeline.base import PipelineOrchestrator
from src.application.registry.pipeline_registry import PipelineRegistry, get_default_pipeline_registry
from src.config.settings import get_settings
from src.domain.entities.genome import DocumentGenome

settings = get_settings()


class GenerateGenomeUseCase:
    """Orchestrates the 17-step Genome Extraction pipeline assembled from PipelineRegistry."""

    def __init__(self, session: AsyncSession, registry: PipelineRegistry | None = None) -> None:
        self._session = session
        self._registry = registry or get_default_pipeline_registry(session)

    def _build_pipeline(self) -> PipelineOrchestrator:
        return self._registry.build_orchestrator()

    async def execute(
        self,
        file_bytes: bytes,
        filename: str,
        mime_type: str,
    ) -> DocumentGenome:
        """Runs the full genome extraction pipeline and returns the canonical genome."""
        context = ProcessingContext.create(
            uploaded_file_bytes=file_bytes,
            original_filename=filename,
            mime_type=mime_type,
            working_directory=settings.processing.temp_dir,
        )

        orchestrator = self._build_pipeline()
        context = await orchestrator.run(context)

        if context.genome is None:
            raise RuntimeError("Pipeline completed but genome was not produced.")

        return context.genome
