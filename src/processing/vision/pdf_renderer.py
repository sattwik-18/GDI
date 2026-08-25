"""PDF rendering engine using PyMuPDF."""

import io
from PIL import Image
import fitz  # PyMuPDF

from src.application.context.processing_context import RenderedPageData
from src.config.settings import get_settings

settings = get_settings()


class PDFRenderer:
    """Renders PDF pages or loads input images into RenderedPageData objects at configured DPI."""

    def __init__(self, dpi: int | None = None) -> None:
        self._dpi = dpi or settings.processing.rendering_dpi

    def render(self, content: bytes, mime_type: str) -> list[RenderedPageData]:
        """Renders input document bytes into a list of 300 DPI RenderedPageData objects."""
        if "pdf" in mime_type.lower():
            return self._render_pdf(content)
        return self._render_image(content)

    def _render_pdf(self, content: bytes) -> list[RenderedPageData]:
        doc = fitz.open(stream=content, filetype="pdf")
        rendered_pages: list[RenderedPageData] = []

        zoom = self._dpi / 72.0  # 72 pt/inch baseline
        mat = fitz.Matrix(zoom, zoom)

        for page_idx in range(doc.page_count):
            page = doc[page_idx]
            pix = page.get_pixmap(matrix=mat, alpha=False)
            image_bytes = pix.tobytes("png")

            rendered_pages.append(
                RenderedPageData(
                    page_number=page_idx + 1,
                    image_bytes=image_bytes,
                    width_px=pix.width,
                    height_px=pix.height,
                    dpi=self._dpi,
                    format="PNG",
                )
            )

        doc.close()
        return rendered_pages

    def _render_image(self, content: bytes) -> list[RenderedPageData]:
        img = Image.open(io.BytesIO(content))
        if img.mode != "RGB":
            img = img.convert("RGB")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        png_bytes = buffer.getvalue()

        return [
            RenderedPageData(
                page_number=1,
                image_bytes=png_bytes,
                width_px=img.width,
                height_px=img.height,
                dpi=self._dpi,
                format="PNG",
            )
        ]
