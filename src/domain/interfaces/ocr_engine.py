"""Abstract OCR Engine interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class OCRTextElement:
    """Extracted text bounding box and text result."""

    id: str
    text: str
    confidence: float
    bbox: list[list[float]]  # [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    page_number: int


@dataclass
class OCRPageResult:
    """OCR extraction output for a single page."""

    page_number: int
    elements: list[OCRTextElement]
    mean_confidence: float
    total_words: int
    raw_output: dict[str, Any]
    width_px: int = 0
    height_px: int = 0


class OCREngine(ABC):
    """Abstract OCR engine interface."""

    @abstractmethod
    async def extract_page(self, image_bytes: bytes, page_number: int) -> OCRPageResult:
        """Runs OCR on an image and returns structured text elements."""
        pass
