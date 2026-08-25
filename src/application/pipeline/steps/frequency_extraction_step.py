"""FrequencyExtractionStep pipeline step."""

from src.application.context.processing_context import ProcessingContext
from src.application.pipeline.base import PipelineStep
from src.processing.extractors.frequency_extractor import FrequencyExtractor


class FrequencyExtractionStep(PipelineStep):
    """Pipeline step 10: Extract frequency features (FFT, DCT, Wavelet)."""

    def __init__(self) -> None:
        self._extractor = FrequencyExtractor()

    @property
    def name(self) -> str:
        return "FrequencyExtractionStep"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        feature_group = self._extractor.extract(context)
        context.extracted_feature_groups.append(feature_group)
        return context
