"""VisualEmbeddingStep pipeline step with real DINOv2 adapter."""

from src.application.context.processing_context import ProcessingContext
from src.application.pipeline.base import PipelineStep
from src.infrastructure.adapters.dinov2_adapter import DINOv2Adapter


class VisualEmbeddingStep(PipelineStep):
    """Pipeline step: extracts dense visual layout embeddings via DINOv2 with custom fingerprint fallback."""

    def __init__(self) -> None:
        self._dinov2_adapter = DINOv2Adapter()

    @property
    def name(self) -> str:
        return "VisualEmbeddingStep"

    @property
    def version(self) -> str:
        return "2.0.0"

    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        if not context.normalized_pages:
            return context

        primary_page = context.normalized_pages[0]
        context.visual_genome = self._dinov2_adapter.extract_embedding(primary_page.image_bytes)

        return context
