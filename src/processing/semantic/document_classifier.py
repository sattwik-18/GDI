"""Document Classification and Taxonomy Engine.

Classifies incoming documents into canonical forensic taxonomy categories
using structural signatures, OCR text tokens, and layout geometry.
"""

from __future__ import annotations
import re
from typing import Any
from src.domain.entities.semantic_genome import DocumentTaxonomy
from src.domain.interfaces.ocr_engine import OCRPageResult


class DocumentClassifier:
    """Classifies document types and calculates category confidence scores."""

    TAXONOMY_KEYWORDS = {
        "INVOICE": [
            r"\binvoice\b", r"\bbill to\b", r"\bamount due\b", r"\binvoice date\b",
            r"\binvoice number\b", r"\binvoice no\b", r"\btotal amount\b", r"\bdue date\b",
            r"\bbalance due\b", r"\bvat\b", r"\bgst\b", r"\bsubtotal\b", r"\bitem description\b"
        ],
        "RECEIPT": [
            r"\breceipt\b", r"\bcashier\b", r"\bpos\b", r"\bmerchant\b", r"\bchange due\b",
            r"\btendered\b", r"\bterminal\b", r"\bstore #\b"
        ],
        "CERTIFICATE": [
            r"\bcertificate\b", r"\bhereby certify\b", r"\bcertified that\b", r"\bawarded to\b",
            r"\bcompletion\b", r"\bexcellence\b", r"\bin witness whereof\b", r"\bconferred upon\b"
        ],
        "DEGREE": [
            r"\buniversity\b", r"\bdegree\b", r"\bbachelor of\b", r"\bmaster of\b",
            r"\bdoctor of\b", r"\bfaculty of\b", r"\bacademic senate\b", r"\bchancellor\b"
        ],
        "TAX_DOCUMENT": [
            r"\bform 1040\b", r"\bw-2\b", r"\b1099\b", r"\binternal revenue\b", r"\btax return\b",
            r"\bwithholding\b", r"\btax year\b", r"\bsocial security number\b"
        ],
        "CONTRACT": [
            r"\bagreement\b", r"\bcontract\b", r"\bparty of the first part\b", r"\bterms and conditions\b",
            r"\bindemnification\b", r"\bgoverning law\b", r"\bnon-disclosure\b"
        ],
        "BANK_STATEMENT": [
            r"\bbank statement\b", r"\baccount summary\b", r"\bopening balance\b",
            r"\bclosing balance\b", r"\btransactions\b", r"\bdeposit\b", r"\bwithdrawal\b"
        ],
    }

    def classify_document(
        self,
        ocr_results: list[OCRPageResult],
    ) -> DocumentTaxonomy:
        """Classifies document taxonomy based on multi-page text and structural tokens."""
        combined_text = " ".join(
            el.text.lower()
            for page in ocr_results
            for el in page.elements
        )

        if not combined_text.strip():
            return DocumentTaxonomy(
                primary_type="GENERIC_DOCUMENT",
                subtype="EMPTY_OR_UNRECOGNIZED",
                confidence=0.5,
                alternative_types=[],
            )

        scores: dict[str, int] = {}
        for category, patterns in self.TAXONOMY_KEYWORDS.items():
            match_count = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, combined_text, re.IGNORECASE))
                match_count += matches
            scores[category] = match_count

        sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        top_cat, top_score = sorted_scores[0]

        if top_score == 0:
            return DocumentTaxonomy(
                primary_type="GENERIC_DOCUMENT",
                subtype="UNCLASSIFIED",
                confidence=0.6,
                alternative_types=[],
            )

        total_score = sum(scores.values()) + 1e-5
        confidence = min(0.99, max(0.70, 0.70 + 0.05 * min(5, top_score)))

        alternatives = [
            {"type": cat, "confidence": round(sc / total_score, 3)}
            for cat, sc in sorted_scores[1:4]
            if sc > 0
        ]

        return DocumentTaxonomy(
            primary_type=top_cat,
            subtype=f"{top_cat.lower()}_standard",
            confidence=round(confidence, 4),
            alternative_types=alternatives,
            taxonomy_version="1.0.0",
        )
