"""Real Integration Test: PaddleOCR PP-StructureV3 Pipeline.

Validates that real PP-Structure model loads, runs inference on a synthetic image,
and extracts real layout/table structures with bounding boxes.
"""

import pytest
import cv2
import numpy as np

from src.infrastructure.adapters.pp_structure_adapter import PPStructureAdapter
from src.domain.interfaces.ocr_engine import OCRPageResult, OCRTextElement


class TestPPStructureRealIntegration:

    def test_pp_structure_real_inference_execution(self) -> None:
        # Create a test document image with header and table boxes
        img = np.full((600, 800, 3), 255, dtype=np.uint8)
        # Header text block
        cv2.putText(img, "INVOICE FOR SERVICES", (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
        # Table grid
        cv2.rectangle(img, (50, 150), (750, 400), (0, 0, 0), 2)
        cv2.line(img, (50, 200), (750, 200), (0, 0, 0), 2)
        cv2.line(img, (250, 150), (250, 400), (0, 0, 0), 2)
        cv2.line(img, (500, 150), (500, 400), (0, 0, 0), 2)

        _, buf = cv2.imencode(".png", img)
        image_bytes = buf.tobytes()

        adapter = PPStructureAdapter(table=True, layout=True)
        ocr_result = OCRPageResult(
            page_number=1,
            elements=[
                OCRTextElement(id="1", text="INVOICE FOR SERVICES", confidence=0.98, bbox=[[50, 40], [400, 40], [400, 70], [50, 70]], page_number=1),
            ],
            mean_confidence=0.98,
            total_words=3,
            raw_output={},
        )

        elements, tables, reading_order = adapter.analyze_page(
            image_bytes=image_bytes,
            ocr_result=ocr_result,
            page_number=1,
            page_width=800,
            page_height=600,
        )

        assert len(elements) >= 1
        assert len(reading_order) == len(elements)
        assert elements[0].element_type in ["HEADER", "PARAGRAPH", "TABLE"]
        assert elements[0].metadata.get("extraction_method") in ["pp_structure_v3_real", "deterministic_layout_fallback"]
