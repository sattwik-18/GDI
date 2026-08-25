"""Unit tests for GeometryExtractor."""

import io
import pytest
import uuid
from PIL import Image

from src.application.context.processing_context import ProcessingContext, RenderedPageData, NormalizedPageData
from src.domain.entities.page import Page
from src.domain.interfaces.ocr_engine import OCRPageResult
from src.processing.extractors.geometry_extractor import GeometryExtractor


def make_processing_context_with_page() -> ProcessingContext:
    content = io.BytesIO()
    Image.new("RGB", (200, 300)).save(content, format="PNG")
    ctx = ProcessingContext.create(
        uploaded_file_bytes=content.getvalue(),
        original_filename="test.png",
        mime_type="image/png",
        working_directory="./tmp_test",
    )
    doc_id = uuid.uuid4()
    ctx.pages = [
        Page(
            id=uuid.uuid4(),
            document_id=doc_id,
            page_number=1,
            width_px=200,
            height_px=300,
            dpi=300,
        )
    ]
    ctx.ocr_results = [
        OCRPageResult(page_number=1, elements=[], mean_confidence=0.0, total_words=0, raw_output={})
    ]
    return ctx


class TestGeometryExtractor:

    def test_returns_feature_group(self) -> None:
        extractor = GeometryExtractor()
        ctx = make_processing_context_with_page()
        fg = extractor.extract(ctx)
        assert fg.name == "GeometryExtractor"
        assert fg.feature_count > 0

    def test_aspect_ratio_correct(self) -> None:
        extractor = GeometryExtractor()
        ctx = make_processing_context_with_page()
        fg = extractor.extract(ctx)
        aspect = fg.features.get("p1_geom_aspect_ratio")
        assert aspect is not None
        assert abs(aspect - (200.0 / 300.0)) < 0.01

    def test_deterministic_output(self) -> None:
        extractor = GeometryExtractor()
        ctx = make_processing_context_with_page()
        fg1 = extractor.extract(ctx)
        fg2 = extractor.extract(ctx)
        assert fg1.features == fg2.features
