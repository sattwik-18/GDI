"""Docling Document Parser Adapter.

Adapter evaluating IBM Docling package for universal document parsing and
hierarchical DoclingDocument representation mapping into GDI StructuralGenome.
"""

from __future__ import annotations
from typing import Any
from src.domain.entities.structural_genome import StructuralGenome, StructuralElement
from src.utils.logging import get_logger

logger = get_logger(__name__)


class DoclingAdapter:
    """Benchmark and integration adapter for IBM Docling parser."""

    def __init__(self) -> None:
        self._is_available = False
        self._converter: Any = None
        self._check_availability()

    def _check_availability(self) -> None:
        try:
            from docling.document_converter import DocumentConverter
            self._converter = DocumentConverter()
            self._is_available = True
            logger.info("docling_package_available")
        except ImportError:
            self._is_available = False
            self._converter = None

    @property
    def is_available(self) -> bool:
        return self._is_available

    def parse_document(self, file_path_or_bytes: str | bytes) -> StructuralGenome | None:
        """Parses document using real Docling converter and maps into GDI StructuralGenome."""
        if not self._is_available or self._converter is None:
            logger.info("docling_not_available_skipping")
            return None

        try:
            conv_res = self._converter.convert(file_path_or_bytes)
            doc = conv_res.document
            elements: list[StructuralElement] = []
            reading_order: list[str] = []

            for idx, item in enumerate(doc.texts):
                elem_id = f"docling_{idx+1}"
                reading_order.append(elem_id)
                elements.append(
                    StructuralElement(
                        element_id=elem_id,
                        element_type=getattr(item, "label", "PARAGRAPH"),
                        page_number=getattr(item, "page_no", 1),
                        bbox=getattr(item, "bbox", []),
                        reading_order_index=idx + 1,
                        text=getattr(item, "text", ""),
                        confidence=1.0,
                        metadata={"model": "docling_real"},
                    )
                )

            return StructuralGenome(
                elements=elements,
                reading_order=reading_order,
                total_regions=len(elements),
            )
        except Exception as e:
            logger.error("docling_parse_failed", error=str(e))
            return None
