"""MinerU Complex PDF Parser Adapter.

Adapter evaluating OpenDataLab MinerU (magic-pdf) for specialized complex PDF structure extraction.
"""

from __future__ import annotations
from typing import Any
from src.utils.logging import get_logger

logger = get_logger(__name__)


class MinerUAdapter:
    """Benchmark adapter for OpenDataLab MinerU (magic-pdf)."""

    def __init__(self) -> None:
        self._is_available = False
        self._check_availability()

    def _check_availability(self) -> None:
        try:
            import magic_pdf
            self._is_available = True
            logger.info("mineru_package_available")
        except ImportError:
            self._is_available = False

    @property
    def is_available(self) -> bool:
        return self._is_available

    def extract_complex_pdf(self, pdf_bytes: bytes) -> dict[str, Any] | None:
        """Parses complex PDF using magic-pdf if installed."""
        if not self._is_available:
            return None

        try:
            from magic_pdf.pipe.UNIPipe import UNIPipe
            pipe = UNIPipe(pdf_bytes, jso_useful_key={"_pdf_type": "", "model_list": []})
            pipe.pipe_classify()
            pipe.pipe_analyze()
            pipe.pipe_parse()
            return pipe.to_dict()
        except Exception as e:
            logger.error("mineru_parse_failed", error=str(e))
            return None
