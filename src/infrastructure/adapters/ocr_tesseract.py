"""Tesseract OCR Adapter — designated for development and testing environments.

NOTE: Output determinism across operating systems and Tesseract versions is NOT guaranteed.
Use PaddleOCR for production deterministic execution.
"""

import io
import pytesseract
from PIL import Image
import numpy as np

from src.config.settings import get_settings
from src.domain.exceptions import OCRError
from src.domain.interfaces.ocr_engine import OCREngine, OCRPageResult, OCRTextElement
from src.utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class TesseractOCRAdapter(OCREngine):
    """Tesseract OCR engine adapter for development and non-Linux test environments."""

    def __init__(self) -> None:
        self._ocr_config = settings.ocr
        if self._ocr_config.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self._ocr_config.tesseract_cmd

    async def extract_page(self, image_bytes: bytes, page_number: int) -> OCRPageResult:
        """Extracts OCR text elements from an image using Tesseract."""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

            elements: list[OCRTextElement] = []
            confidences: list[float] = []

            n_boxes = len(data["text"])
            elem_idx = 1
            for i in range(n_boxes):
                text = data["text"][i].strip()
                conf = float(data["conf"][i])
                if text and conf > 0:
                    score = conf / 100.0
                    if score >= self._ocr_config.confidence_threshold:
                        confidences.append(score)
                        x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                        bbox = [[float(x), float(y)], [float(x + w), float(y)], [float(x + w), float(y + h)], [float(x), float(y + h)]]
                        elements.append(
                            OCRTextElement(
                                id=f"p{page_number}_txt_{elem_idx}",
                                text=text,
                                confidence=round(score, 4),
                                bbox=bbox,
                                page_number=page_number,
                            )
                        )
                        elem_idx += 1

            mean_conf = float(np.mean(confidences)) if confidences else 0.0
            total_words = sum(len(el.text.split()) for el in elements)

            return OCRPageResult(
                page_number=page_number,
                elements=elements,
                mean_confidence=round(mean_conf, 4),
                total_words=total_words,
                raw_output={"engine": "pytesseract", "element_count": len(elements), "width_px": img.width, "height_px": img.height},
                width_px=img.width,
                height_px=img.height,
            )
        except Exception as e:
            logger.error("tesseract_ocr_execution_failed", error=str(e))
            if settings.ocr.dev_ocr_fallback:
                logger.warning("tesseract_ocr_dev_fallback_active", error=str(e))
                img_w = getattr(img, "width", 0) if "img" in locals() else 0
                img_h = getattr(img, "height", 0) if "img" in locals() else 0
                return OCRPageResult(
                    page_number=page_number,
                    elements=[],
                    mean_confidence=0.0,
                    total_words=0,
                    raw_output={"engine": "dev_empty_fallback", "error": str(e), "element_count": 0},
                    width_px=img_w,
                    height_px=img_h,
                )
            raise OCRError(f"Tesseract OCR execution failed: {str(e)}", details={"error": str(e)}) from e
