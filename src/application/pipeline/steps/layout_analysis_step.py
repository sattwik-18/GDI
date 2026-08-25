"""LayoutAnalysisStep pipeline step."""

from src.application.context.processing_context import ProcessingContext
from src.application.pipeline.base import PipelineStep
from src.processing.ocr.layout_analyzer import LayoutAnalyzer


class LayoutAnalysisStep(PipelineStep):
    """Pipeline step 7: Document layout region detection and reading order analysis."""

    def __init__(self) -> None:
        self._analyzer = LayoutAnalyzer()

    @property
    def name(self) -> str:
        return "LayoutAnalysisStep"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        layout_results = []
        for ocr_res in context.ocr_results:
            l_res = self._analyzer.analyze_page(ocr_res)
            layout_results.append(l_res)

        context.layout_results = layout_results
        return context
