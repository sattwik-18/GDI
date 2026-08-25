"""OCRStep pipeline step."""

from src.application.context.processing_context import ProcessingContext
from src.application.pipeline.base import PipelineStep
from src.domain.interfaces.ocr_engine import OCREngine
from src.infrastructure.adapters.ocr_paddle import PaddleOCRAdapter


class OCRStep(PipelineStep):
    """Pipeline step 6: OCR text detection and recognition."""

    def __init__(self, ocr_engine: OCREngine | None = None) -> None:
        self._engine = ocr_engine or PaddleOCRAdapter()

    @property
    def name(self) -> str:
        return "OCRStep"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        ocr_results = []
        for n_page in context.normalized_pages:
            res = await self._engine.extract_page(
                image_bytes=n_page.image_bytes,
                page_number=n_page.page_number,
            )
            ocr_results.append(res)

        context.ocr_results = ocr_results
        return context
