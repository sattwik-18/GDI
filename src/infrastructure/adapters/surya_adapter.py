"""Surya OCR and Layout Engine Adapter.

Adapter integrating Surya for reading order validation and secondary layout detection.
"""

from __future__ import annotations
from typing import Any
from src.domain.entities.structural_genome import StructuralElement, StructuralGenome
from src.utils.logging import get_logger

logger = get_logger(__name__)


class SuryaAdapter:
    """Benchmark and secondary layout validator adapter for Surya."""

    def __init__(self) -> None:
        self._is_available = False
        self._check_availability()

    def _check_availability(self) -> None:
        try:
            import surya
            self._is_available = True
            logger.info("surya_package_available")
        except ImportError:
            self._is_available = False

    @property
    def is_available(self) -> bool:
        return self._is_available

    def run_layout_detection(self, pil_images: list[Any]) -> list[dict[str, Any]]:
        """Runs Surya layout detection model if installed."""
        if not self._is_available:
            return []

        try:
            from surya.layout import batch_layout_detection
            from surya.model.layout.model import load_model, load_processor
            model = load_model()
            processor = load_processor()
            results = batch_layout_detection(pil_images, model, processor)
            return results
        except Exception as e:
            logger.error("surya_layout_failed", error=str(e))
            return []
