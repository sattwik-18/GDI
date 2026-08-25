"""GeometryExtractionStep pipeline step."""

from src.application.context.processing_context import ProcessingContext
from src.application.pipeline.base import PipelineStep
from src.processing.extractors.geometry_extractor import GeometryExtractor


class GeometryExtractionStep(PipelineStep):
    """Pipeline step 8: Extract geometry features (dimensions, aspect ratio, bbox stats)."""

    def __init__(self) -> None:
        self._extractor = GeometryExtractor()

    @property
    def name(self) -> str:
        return "GeometryExtractionStep"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        feature_group = self._extractor.extract(context)
        context.extracted_feature_groups.append(feature_group)
        return context
