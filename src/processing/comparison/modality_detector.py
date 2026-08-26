"""Modality and Document-Type Analyzer.

Analyzes document genomes and visual evidence to determine media type,
document category, text/layout density, and structural characteristics.
"""

from __future__ import annotations
from typing import Any

from src.domain.entities.comparison import (
    DocumentClass,
    InputModalityAnalysis,
    MediaType,
    StructuralProfile,
)


class ModalityDetector:
    """Classifies input media type and structural profile from document genomes."""

    def analyze(self, genome_data: dict[str, Any] | Any) -> InputModalityAnalysis:
        """Determines media_type, document_class, and structural profile."""
        # Normalize dict vs object access
        def _get(obj: Any, key: str, default: Any = None) -> Any:
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        pages = _get(genome_data, "pages", []) or []
        semantic_genome = _get(genome_data, "semantic_genome")
        structural_genome = _get(genome_data, "structural_genome")

        # 1. Calculate Text Density
        total_ocr_words = 0
        for p in pages:
            ocr_elems = _get(p, "ocr_elements", []) or []
            total_ocr_words += len(ocr_elems)

        page_count = max(1, len(pages))
        words_per_page = total_ocr_words / page_count

        # 2. Structural & Layout Density
        structural_elements = _get(structural_genome, "elements", []) or []
        tables = _get(structural_genome, "tables", []) or []
        layout_density = len(structural_elements)
        has_tables = len(tables) > 0

        # Check semantic taxonomy
        taxonomy = _get(semantic_genome, "taxonomy")
        primary_type = str(_get(taxonomy, "primary_type", "UNKNOWN")).upper() if taxonomy else "UNKNOWN"

        # 3. Detect Photography vs Document
        # A document has high text density (>= 15 words) or recognized document taxonomy/tables.
        # A photograph has low text density (< 8 words), zero structural layout blocks, or is natural scenery/face.
        is_photograph = words_per_page < 8 and layout_density <= 2 and not has_tables and primary_type in ["UNKNOWN", "OTHER"]

        if is_photograph:
            media_type = MediaType.PHOTOGRAPH
            doc_class = DocumentClass.PHOTOGRAPH
            rationale = "Natural photograph or non-document image detected (very low text density, no structured document layout)."
        elif primary_type == "INVOICE":
            media_type = MediaType.INVOICE
            doc_class = DocumentClass.INVOICE
            rationale = "Document identified as Invoice with structured monetary and tabular regions."
        elif primary_type == "RECEIPT":
            media_type = MediaType.RECEIPT
            doc_class = DocumentClass.RECEIPT
            rationale = "Document identified as Receipt."
        elif primary_type == "CERTIFICATE" or primary_type == "DEGREE":
            media_type = MediaType.CERTIFICATE
            doc_class = DocumentClass.CERTIFICATE
            rationale = "Document identified as Certificate/Diploma."
        elif primary_type == "CONTRACT":
            media_type = MediaType.CONTRACT
            doc_class = DocumentClass.CONTRACT
            rationale = "Document identified as Legal Contract."
        elif primary_type == "TAX_DOCUMENT":
            media_type = MediaType.FORM
            doc_class = DocumentClass.TAX_DOCUMENT
            rationale = "Document identified as Tax Form/Document."
        elif words_per_page >= 15 or layout_density >= 3:
            media_type = MediaType.DOCUMENT_IMAGE
            doc_class = DocumentClass.FINANCIAL_DOCUMENT if has_tables else DocumentClass.OTHER
            rationale = "Document image with structured typography and layout blocks."
        else:
            media_type = MediaType.UNKNOWN
            doc_class = DocumentClass.UNKNOWN
            rationale = "Ambiguous media type with sparse text."

        profile = StructuralProfile(
            page_count=page_count,
            text_density=round(words_per_page, 2),
            layout_density=layout_density,
            table_presence=has_tables,
            form_presence=primary_type in ["TAX_DOCUMENT", "FORM"],
            face_presence=False,
            signature_presence=False,
            stamp_presence=primary_type in ["CERTIFICATE", "DEGREE"],
        )

        return InputModalityAnalysis(
            media_type=media_type,
            document_class=doc_class,
            structural_profile=profile,
            confidence=0.96 if not is_photograph else 0.92,
            rationale=rationale,
        )
