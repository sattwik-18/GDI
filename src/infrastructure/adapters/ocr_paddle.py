"""PaddleOCR Adapter — Primary deterministic OCR engine.

In production mode, PaddleOCR is mandatory. Silent engine fallback is disabled to enforce
Axiom 1 (Reproducibility). If PaddleOCR is uninitialized, pipeline startup fails fast
with OCREngineUnavailableError unless DEV_OCR_FALLBACK=true.
"""

import io
import cv2
import numpy as np

from src.config.settings import get_settings
from src.domain.exceptions import OCREngineUnavailableError, OCRError
from src.domain.interfaces.ocr_engine import OCREngine, OCRPageResult, OCRTextElement
from src.infrastructure.adapters.ocr_tesseract import TesseractOCRAdapter
from src.utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class PaddleOCRAdapter(OCREngine):
    """PaddleOCR engine adapter with fail-fast production determinism guarantees."""

    def __init__(self) -> None:
        self._ocr_config = settings.ocr
        self._paddle_engine = None
        self._dev_fallback_adapter: TesseractOCRAdapter | None = None
        self._init_engine()

    def _init_engine(self) -> None:
        if self._ocr_config.engine_provider.lower() == "pytesseract":
            if not self._ocr_config.dev_ocr_fallback:
                raise OCREngineUnavailableError(
                    "OCR engine set to pytesseract, but DEV_OCR_FALLBACK is False. "
                    "Pytesseract is non-deterministic and not allowed for production genomes."
                )
            logger.warning("ocr_engine_initialized_dev_mode", provider="pytesseract")
            self._dev_fallback_adapter = TesseractOCRAdapter()
            return

        try:
            import os
            os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
            if not hasattr(np, "sctypes"):
                np.sctypes = {
                    "int": [np.int8, np.int16, np.int32, np.int64],
                    "uint": [np.uint8, np.uint16, np.uint32, np.uint64],
                    "float": [np.float16, np.float32, np.float64],
                    "complex": [np.complex64, np.complex128],
                    "others": [bool, object, bytes, str, np.void],
                }

            from paddleocr import PaddleOCR

            self._paddle_engine = PaddleOCR(
                use_angle_cls=True,
                lang=self._ocr_config.lang,
                use_gpu=self._ocr_config.use_gpu,
                show_log=False,
            )
            logger.info("ocr_engine_initialized", provider="paddleocr")
        except Exception as e:
            if self._ocr_config.dev_ocr_fallback:
                logger.warning(
                    "paddleocr_init_failed_using_dev_fallback",
                    error=str(e),
                )
                self._dev_fallback_adapter = TesseractOCRAdapter()
            else:
                raise OCREngineUnavailableError(
                    f"PaddleOCR failed to initialize: {str(e)}. "
                    "Production determinism requires PaddleOCR. "
                    "Set DEV_OCR_FALLBACK=true for local dev fallback.",
                    details={"error": str(e)},
                ) from e

    async def extract_page(self, image_bytes: bytes, page_number: int) -> OCRPageResult:
        """Extracts OCR text elements from an image using PaddleOCR (or dev fallback)."""
        if self._dev_fallback_adapter is not None:
            return await self._dev_fallback_adapter.extract_page(image_bytes, page_number)

        if self._paddle_engine is None:
            raise OCREngineUnavailableError("PaddleOCR engine is uninitialized.")

        try:
            return self._run_paddle_ocr(image_bytes, page_number)
        except Exception as e:
            if self._ocr_config.dev_ocr_fallback:
                logger.warning("paddleocr_execution_failed_using_dev_fallback", error=str(e))
                fallback = TesseractOCRAdapter()
                return await fallback.extract_page(image_bytes, page_number)
            raise OCRError(f"PaddleOCR execution failed on page {page_number}: {str(e)}", details={"error": str(e)}) from e

    def _run_paddle_ocr(self, image_bytes: bytes, page_number: int) -> OCRPageResult:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return OCRPageResult(
                page_number=page_number,
                elements=[],
                mean_confidence=0.0,
                total_words=0,
                raw_output={"error": "Failed to decode image"},
            )

        img_h, img_w = img.shape[:2]

        results = self._paddle_engine.ocr(img, cls=True)

        elements: list[OCRTextElement] = []
        confidences: list[float] = []

        if results and results[0]:
            for idx, res in enumerate(results[0]):
                box = res[0]  # [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
                text_info = res[1]  # (text, score)
                text = text_info[0]
                score = float(text_info[1])

                if score >= self._ocr_config.confidence_threshold:
                    confidences.append(score)
                    elements.append(
                        OCRTextElement(
                            id=f"p{page_number}_txt_{idx+1}",
                            text=text,
                            confidence=round(score, 4),
                            bbox=box,
                            page_number=page_number,
                        )
                    )

        mean_conf = float(np.mean(confidences)) if confidences else 0.0
        total_words = sum(len(el.text.split()) for el in elements)

        return OCRPageResult(
            page_number=page_number,
            elements=elements,
            mean_confidence=round(mean_conf, 4),
            total_words=total_words,
            raw_output={"engine": "paddleocr", "element_count": len(elements), "width_px": img_w, "height_px": img_h},
            width_px=img_w,
            height_px=img_h,
        )
