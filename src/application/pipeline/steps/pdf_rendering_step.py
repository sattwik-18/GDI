"""PDFRenderingStep pipeline step."""

from src.application.context.processing_context import ProcessingContext
from src.application.pipeline.base import PipelineStep
from src.domain.entities.page import Page
from src.processing.vision.pdf_renderer import PDFRenderer


class PDFRenderingStep(PipelineStep):
    """Pipeline step 3: Render PDF pages to 300 DPI images (or load input images)."""

    def __init__(self) -> None:
        self._renderer = PDFRenderer()

    @property
    def name(self) -> str:
        return "PDFRenderingStep"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        rendered_pages = self._renderer.render(
            content=context.uploaded_file_bytes,
            mime_type=context.mime_type,
        )
        context.rendered_pages = rendered_pages

        # Create Page domain entities
        pages: list[Page] = []
        if context.document:
            for p_data in rendered_pages:
                page_entity = Page.create(
                    document_id=context.document.id,
                    page_number=p_data.page_number,
                    width_px=p_data.width_px,
                    height_px=p_data.height_px,
                    dpi=p_data.dpi,
                )
                pages.append(page_entity)
        context.pages = pages

        return context
