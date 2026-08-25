"""Document layout analyzer (region detection, block classification, reading order)."""

from typing import Any
from src.application.context.processing_context import LayoutPageResult
from src.domain.interfaces.ocr_engine import OCRPageResult


class LayoutAnalyzer:
    """Analyzes spatial layout, groups OCR elements into logical blocks, and establishes reading order."""

    def analyze_page(self, ocr_result: OCRPageResult) -> LayoutPageResult:
        """Generates layout regions and reading order from OCR bounding boxes."""
        elements = ocr_result.elements
        if not elements:
            return LayoutPageResult(
                page_number=ocr_result.page_number,
                regions=[],
                reading_order=[],
            )

        # Sort elements by Y coordinate (top to bottom), then X coordinate (left to right)
        sorted_elements = sorted(
            elements,
            key=lambda el: (
                el.bbox[0][1] if el.bbox else 0,
                el.bbox[0][0] if el.bbox else 0,
            ),
        )

        regions: list[dict[str, Any]] = []
        reading_order: list[str] = []

        for idx, el in enumerate(sorted_elements):
            reading_order.append(el.id)

            # Classify block type based on position and properties
            is_header = el.bbox[0][1] < 150 if el.bbox else False
            region_type = "HEADER" if is_header else "PARAGRAPH"

            regions.append(
                {
                    "region_id": f"p{ocr_result.page_number}_reg_{idx+1}",
                    "region_type": region_type,
                    "element_id": el.id,
                    "bbox": el.bbox,
                    "text_snippet": el.text[:50],
                }
            )

        return LayoutPageResult(
            page_number=ocr_result.page_number,
            regions=regions,
            reading_order=reading_order,
        )
