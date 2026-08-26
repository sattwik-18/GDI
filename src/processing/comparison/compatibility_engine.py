"""Comparison Compatibility Engine & Hard Compatibility Gate.

Enforces strict two-stage comparison routing:
Stage 1: Independent Modality & Document-Likeness Analysis
Stage 2: Hard Compatibility Gate BEFORE any dimensional scoring
"""

from __future__ import annotations
from src.domain.entities.comparison import (
    ComparisonMode,
    ComparisonStatus,
    InputDescriptor,
)


class ComparisonCompatibilityEngine:
    """Evaluates cross-input compatibility and routes to the appropriate comparison mode."""

    def evaluate_compatibility(
        self,
        input_a: InputDescriptor,
        input_b: InputDescriptor,
        allow_specialized_face_matching: bool = False,
    ) -> tuple[ComparisonStatus, ComparisonMode | None, str, str | None]:
        """Determines compatibility status, mode, reason, and available action."""
        mod_a = input_a.modality
        mod_b = input_b.modality

        # 1. Hard Gate: Document vs Photograph
        if (mod_a == "DOCUMENT" and mod_b == "PHOTOGRAPH") or (mod_a == "PHOTOGRAPH" and mod_b == "DOCUMENT"):
            return (
                ComparisonStatus.INCOMPATIBLE,
                None,
                "DOCUMENT_VS_PHOTOGRAPH: Cannot compute document similarity between a structured document and a photograph.",
                "Upload a document or another photograph to perform a valid comparison.",
            )

        # 2. Hard Gate: ID Document vs Photograph
        if (mod_a == "ID_DOCUMENT" and mod_b == "PHOTOGRAPH") or (mod_a == "PHOTOGRAPH" and mod_b == "ID_DOCUMENT"):
            if allow_specialized_face_matching:
                return (
                    ComparisonStatus.SPECIALIZED_COMPARISON,
                    ComparisonMode.FACE_IDENTITY,
                    "SPECIALIZED_FACE_DOCUMENT_COMPARISON: Face verification between identity document and photograph.",
                    None,
                )
            return (
                ComparisonStatus.INCOMPATIBLE,
                None,
                "DOCUMENT_VS_PHOTOGRAPH: Identity document vs human photograph requires specialized face verification mode.",
                "Enable specialized face verification mode for ID vs Portrait comparison.",
            )

        # 3. Photograph vs Photograph
        if mod_a == "PHOTOGRAPH" and mod_b == "PHOTOGRAPH":
            return (
                ComparisonStatus.COMPATIBLE,
                ComparisonMode.GENERIC_IMAGE,
                "IMAGE_IMAGE_COMPARISON: Visual and perceptual image similarity mode.",
                None,
            )

        # 4. Document vs Document
        if mod_a in ["DOCUMENT", "ID_DOCUMENT"] and mod_b in ["DOCUMENT", "ID_DOCUMENT"]:
            if input_a.document_type and input_b.document_type and input_a.document_type == input_b.document_type:
                return (
                    ComparisonStatus.COMPATIBLE,
                    ComparisonMode.SAME_TEMPLATE_OR_FAMILY,
                    f"SAME_DOCUMENT_TYPE: Both inputs are {input_a.document_type.upper()} documents.",
                    None,
                )
            return (
                ComparisonStatus.RELATED_BUT_DIFFERENT_DOCUMENT_TYPES,
                ComparisonMode.DOCUMENT_DOCUMENT,
                f"RELATED_BUT_DIFFERENT_DOCUMENT_TYPES: Comparing {str(input_a.document_type or 'document').upper()} with {str(input_b.document_type or 'document').upper()}.",
                None,
            )

        # 5. Unknown / Low Confidence
        return (
            ComparisonStatus.UNKNOWN,
            None,
            "INSUFFICIENT_EVIDENCE: Sparse structural evidence available to verify compatibility.",
            None,
        )
