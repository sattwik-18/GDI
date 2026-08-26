"""Document-Likeness and Photographic Scene Analyzer.

Independently evaluates whether an input is a genuine structured document or a natural photograph,
preventing background OCR artifacts (e.g. cafe signs, t-shirts, posters) from classifying a photo as a document.
"""

from __future__ import annotations
from typing import Any
import numpy as np


class DocumentLikelihoodResult:
    """Document vs Photo likelihood evaluation metrics."""

    def __init__(
        self,
        document_likelihood: float,
        photo_likelihood: float,
        modality: str,  # "DOCUMENT" | "PHOTOGRAPH" | "ID_DOCUMENT" | "UNKNOWN"
        document_class: str,
        confidence: float,
        rationale: str,
        indicators: dict[str, Any],
    ) -> None:
        self.document_likelihood = round(document_likelihood, 4)
        self.photo_likelihood = round(photo_likelihood, 4)
        self.modality = modality
        self.document_class = document_class
        self.confidence = round(confidence, 4)
        self.rationale = rationale
        self.indicators = indicators

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_likelihood": self.document_likelihood,
            "photo_likelihood": self.photo_likelihood,
            "modality": self.modality,
            "document_class": self.document_class,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "indicators": self.indicators,
        }


class DocumentLikelihoodAnalyzer:
    """Analyzes visual, layout, and textual properties to determine document-likeness."""

    def analyze(self, genome_data: dict[str, Any] | Any) -> DocumentLikelihoodResult:
        """Computes document_likelihood vs photo_likelihood independently."""
        def _get(obj: Any, key: str, default: Any = None) -> Any:
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        pages = _get(genome_data, "pages", []) or []
        semantic_genome = _get(genome_data, "semantic_genome")
        structural_genome = _get(genome_data, "structural_genome")
        feature_vec = _get(genome_data, "feature_vector", []) or []

        # 1. Evaluate OCR Text Structure & Key-Value Regularity
        ocr_tokens: list[dict[str, Any]] = []
        structured_kv_hits = 0
        doc_patterns = {
            "total", "amount", "invoice", "date", "subtotal", "tax", "bill", "due",
            "account", "balance", "qty", "rate", "price", "certify", "certificate",
            "completion", "completed", "awarded", "degree", "diploma", "agreement",
            "contract", "signature", "signed", "statement", "report", "policy"
        }

        for p in pages:
            ocr_elements = _get(p, "ocr_elements", []) or []
            for el in ocr_elements:
                ocr_tokens.append(el)
                txt = str(_get(el, "text", "")).lower()
                if any(kw in txt for kw in doc_patterns):
                    structured_kv_hits += 1

        total_words = len(ocr_tokens)
        page_count = max(1, len(pages))
        words_per_page = total_words / page_count

        # 2. Evaluate Structural Document Layout Blocks
        structural_elements = _get(structural_genome, "elements", []) or []
        tables = _get(structural_genome, "tables", []) or []
        num_layout_blocks = len(structural_elements)
        has_tables = len(tables) > 0

        # Check semantic taxonomy
        taxonomy = _get(semantic_genome, "taxonomy")
        primary_type = str(_get(taxonomy, "primary_type", "UNKNOWN")).upper() if taxonomy else "UNKNOWN"

        # 3. Multi-Evidence Scoring
        doc_score = 0.0
        photo_score = 0.0

        # Evidence A: Structured key-value / document header terms
        if structured_kv_hits >= 2:
            doc_score += 0.50
        elif structured_kv_hits == 1:
            doc_score += 0.35
        else:
            photo_score += 0.15

        # Evidence B: Text density and layout blocks
        if words_per_page >= 10 and num_layout_blocks >= 2:
            doc_score += 0.35
        elif words_per_page >= 3 or num_layout_blocks >= 1:
            doc_score += 0.25
        else:
            photo_score += 0.25

        # Evidence C: Document Type & Tabular structures
        known_doc_types = {"INVOICE", "RECEIPT", "TAX_DOCUMENT", "CONTRACT", "CERTIFICATE", "REPORT", "LETTER", "STATEMENT", "AGREEMENT", "ACADEMIC_TITLE"}
        if has_tables or primary_type in known_doc_types:
            doc_score += 0.45
        else:
            photo_score += 0.10

        # Evidence D: Natural scene / photograph indicators (0 words, 0 layout blocks, no tables, UNKNOWN taxonomy)
        if total_words <= 3 and num_layout_blocks == 0 and not has_tables and primary_type == "UNKNOWN" and structured_kv_hits == 0:
            photo_score += 0.60

        # Normalize probabilities
        total = doc_score + photo_score + 1e-6
        doc_likelihood = min(1.0, max(0.0, doc_score / total))
        photo_likelihood = min(1.0, max(0.0, photo_score / total))

        # 4. Final Classification
        if photo_likelihood > 0.65 and doc_likelihood < 0.35:
            modality = "PHOTOGRAPH"
            doc_class = "photograph"
            confidence = max(photo_likelihood, 0.90)
            rationale = "Natural photograph or non-document scene (low text density, lack of structured key-value alignment)."
        elif primary_type == "IDENTITY_DOCUMENT" or (words_per_page < 30 and primary_type in ["ID", "PASSPORT", "LICENSE"]):
            modality = "ID_DOCUMENT"
            doc_class = "identity_document"
            confidence = 0.95
            rationale = "Identity card / document detected."
        else:
            modality = "DOCUMENT"
            doc_class = primary_type.lower() if primary_type != "UNKNOWN" else "document"
            confidence = max(doc_likelihood, 0.90)
            rationale = f"Structured document ({doc_class.upper()}) with tabular/key-value layout."

        indicators = {
            "words_per_page": round(words_per_page, 2),
            "structured_kv_hits": structured_kv_hits,
            "layout_blocks": num_layout_blocks,
            "has_tables": has_tables,
            "primary_taxonomy": primary_type,
        }

        return DocumentLikelihoodResult(
            document_likelihood=doc_likelihood,
            photo_likelihood=photo_likelihood,
            modality=modality,
            document_class=doc_class,
            confidence=confidence,
            rationale=rationale,
            indicators=indicators,
        )
