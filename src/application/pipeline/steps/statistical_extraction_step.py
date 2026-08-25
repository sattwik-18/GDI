"""StatisticalExtractionStep — runs edge, OCR, and statistical extractors in sequence."""

from src.application.context.processing_context import ProcessingContext
from src.application.pipeline.base import PipelineStep
from src.processing.extractors.edge_extractor import EdgeExtractor
from src.processing.extractors.ocr_extractor import OCRFeatureExtractor
from src.processing.extractors.statistical_extractor import StatisticalExtractor


class StatisticalExtractionStep(PipelineStep):
    """Pipeline step 11: Runs edge, OCR stats, and statistical extractors."""

    def __init__(self) -> None:
        self._edge_extractor = EdgeExtractor()
        self._ocr_extractor = OCRFeatureExtractor()
        self._stat_extractor = StatisticalExtractor()

    @property
    def name(self) -> str:
        return "StatisticalExtractionStep"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        context.extracted_feature_groups.append(self._edge_extractor.extract(context))
        context.extracted_feature_groups.append(self._ocr_extractor.extract(context))
        context.extracted_feature_groups.append(self._stat_extractor.extract(context))
        return context
