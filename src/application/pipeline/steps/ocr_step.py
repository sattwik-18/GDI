"""OCRStep pipeline step."""

import fitz
from src.application.context.processing_context import ProcessingContext
from src.application.pipeline.base import PipelineStep
from src.config.settings import get_settings
from src.domain.interfaces.ocr_engine import OCREngine, OCRPageResult, OCRTextElement
from src.infrastructure.adapters.ocr_paddle import PaddleOCRAdapter

settings = get_settings()


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
        is_pdf = (
            context.document is not None
            and (context.document.mime_type == "application/pdf" or context.original_filename.lower().endswith(".pdf"))
        )

        pdf_doc = None
        if is_pdf and context.uploaded_file_bytes:
            try:
                pdf_doc = fitz.open(stream=context.uploaded_file_bytes, filetype="pdf")
            except Exception:
                pdf_doc = None

        for n_page in context.normalized_pages:
            res = await self._engine.extract_page(
                image_bytes=n_page.image_bytes,
                page_number=n_page.page_number,
            )

            # If raster OCR found 0 elements and this is a digital PDF, extract native vector text & boxes
            if (not res.elements or len(res.elements) == 0) and pdf_doc is not None:
                p_idx = n_page.page_number - 1
                if 0 <= p_idx < len(pdf_doc):
                    pdf_page = pdf_doc[p_idx]
                    dpi = settings.processing.rendering_dpi or 300
                    scale = dpi / 72.0
                    blocks = pdf_page.get_text("blocks")
                    vector_elements = []

                    for idx, b in enumerate(blocks):
                        x0, y0, x1, y1, text, block_no, block_type = b
                        clean_text = text.strip()
                        if not clean_text or block_type != 0:
                            continue
                        px0 = round(x0 * scale, 1)
                        py0 = round(y0 * scale, 1)
                        px1 = round(x1 * scale, 1)
                        py1 = round(y1 * scale, 1)
                        bbox = [[px0, py0], [px1, py0], [px1, py1], [px0, py1]]
                        vector_elements.append(
                            OCRTextElement(
                                id=f"p{n_page.page_number}_txt_{idx+1}",
                                text=clean_text,
                                confidence=0.99,
                                bbox=bbox,
                                page_number=n_page.page_number,
                            )
                        )

                    if vector_elements:
                        total_words = sum(len(el.text.split()) for el in vector_elements)
                        res = OCRPageResult(
                            page_number=n_page.page_number,
                            elements=vector_elements,
                            mean_confidence=0.99,
                            total_words=total_words,
                            raw_output={"engine": "pymupdf_vector", "element_count": len(vector_elements)},
                            width_px=getattr(res, "width_px", int(pdf_page.rect.width * scale)),
                            height_px=getattr(res, "height_px", int(pdf_page.rect.height * scale)),
                        )

            ocr_results.append(res)

        context.ocr_results = ocr_results
        return context
