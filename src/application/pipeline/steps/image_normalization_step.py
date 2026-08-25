"""ImageNormalizationStep pipeline step."""

from src.application.context.processing_context import ProcessingContext
from src.application.pipeline.base import PipelineStep
from src.processing.vision.image_normalizer import ImageNormalizer


class ImageNormalizationStep(PipelineStep):
    """Pipeline step 4: Deskew, homography correction, and sRGB color normalization."""

    def __init__(self) -> None:
        self._normalizer = ImageNormalizer()

    @property
    def name(self) -> str:
        return "ImageNormalizationStep"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        normalized_pages = []
        for r_page in context.rendered_pages:
            norm_page = self._normalizer.normalize(r_page)
            normalized_pages.append(norm_page)

        context.normalized_pages = normalized_pages
        return context
