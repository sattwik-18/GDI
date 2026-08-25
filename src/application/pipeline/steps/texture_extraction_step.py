"""TextureExtractionStep pipeline step."""

from src.application.context.processing_context import ProcessingContext
from src.application.pipeline.base import PipelineStep
from src.processing.extractors.texture_extractor import TextureExtractor


class TextureExtractionStep(PipelineStep):
    """Pipeline step 9: Extract texture features (LBP, GLCM, local variance)."""

    def __init__(self) -> None:
        self._extractor = TextureExtractor()

    @property
    def name(self) -> str:
        return "TextureExtractionStep"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        feature_group = self._extractor.extract(context)
        context.extracted_feature_groups.append(feature_group)
        return context
