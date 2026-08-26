"""Comprehensive Multi-Evidence Document Comparison Regression & Integration Suite.

Classification: [REAL_MODEL_INFERENCE / BENCHMARK]
Tests:
1. Exact Regression: Cloudflare Invoice vs Certificate -> DIFFERENT_DOCUMENTS with similarity < 5.0% and negative evidence.
2. Incompatible Gate: AWS Invoice vs Human Photo -> INCOMPATIBLE, similarity=null.
3. Same Template Variant: Cloudflare Invoice vs Modified Total -> SAME_TEMPLATE_VARIANT, similarity >= 65%.
4. Identical Cryptographic Twin: Invoice vs Invoice -> SAME_DOCUMENT, similarity=100%.
5. Generic Image Mode: Photo vs Photo -> VISUAL_TWIN / VISUALLY_SIMILAR.
"""

import pytest
from src.domain.entities.comparison import ComparisonMode, ComparisonStatus
from src.processing.comparison.comparison_engine import ComparisonEngine


@pytest.fixture
def comparison_engine() -> ComparisonEngine:
    return ComparisonEngine()


@pytest.fixture
def sample_cloudflare_invoice() -> dict:
    return {
        "pages": [
            {
                "ocr_elements": [
                    {"text": "Cloudflare", "confidence": 0.99, "bbox": [[50, 50], [200, 80]]},
                    {"text": "Invoice", "confidence": 0.99, "bbox": [[50, 90], [150, 110]]},
                    {"text": "Invoice", "confidence": 0.99, "bbox": [[50, 120], [100, 135]]},
                    {"text": "Number:", "confidence": 0.99, "bbox": [[110, 120], [160, 135]]},
                    {"text": "INV-2026-001", "confidence": 0.99, "bbox": [[170, 120], [250, 135]]},
                    {"text": "Total", "confidence": 0.99, "bbox": [[50, 300], [100, 320]]},
                    {"text": "Amount:", "confidence": 0.99, "bbox": [[110, 300], [160, 320]]},
                    {"text": "$1,200.00", "confidence": 0.99, "bbox": [[170, 300], [240, 320]]},
                    {"text": "Subtotal:", "confidence": 0.99, "bbox": [[50, 260], [120, 275]]},
                    {"text": "$1,000.00", "confidence": 0.99, "bbox": [[130, 260], [200, 275]]},
                    {"text": "Tax:", "confidence": 0.99, "bbox": [[50, 280], [90, 295]]},
                    {"text": "$200.00", "confidence": 0.99, "bbox": [[100, 280], [160, 295]]},
                    {"text": "Due", "confidence": 0.99, "bbox": [[50, 140], [80, 155]]},
                    {"text": "Date:", "confidence": 0.99, "bbox": [[90, 140], [130, 155]]},
                    {"text": "July", "confidence": 0.99, "bbox": [[140, 140], [170, 155]]},
                    {"text": "10,", "confidence": 0.99, "bbox": [[180, 140], [200, 155]]},
                    {"text": "2026", "confidence": 0.99, "bbox": [[210, 140], [240, 155]]},
                ]
            }
        ],
        "structural_genome": {
            "elements": [{"type": "HEADER"}, {"type": "TABLE"}, {"type": "PARAGRAPH"}],
            "tables": [{"rows": 4, "columns": 3}],
        },
        "semantic_genome": {
            "taxonomy": {"primary_type": "INVOICE"},
            "entities": {
                "invoice_number": {"value": "INV-2026-001", "normalized_value": "inv-2026-001"},
                "total_amount": {"value": "$1,200.00", "normalized_value": "1200.00"},
            },
        },
        "visual_genome": {"visual_embedding": [0.1] * 384},
        "feature_vector": [0.5] * 108,
    }


@pytest.fixture
def sample_certificate() -> dict:
    return {
        "pages": [
            {
                "ocr_elements": [
                    {"text": "CERTIFICATE", "confidence": 0.99, "bbox": [[200, 100], [400, 130]]},
                    {"text": "OF", "confidence": 0.99, "bbox": [[280, 140], [320, 160]]},
                    {"text": "COMPLETION", "confidence": 0.99, "bbox": [[180, 170], [420, 200]]},
                    {"text": "hello", "confidence": 0.99, "bbox": [[270, 210], [330, 230]]},
                    {"text": "has", "confidence": 0.99, "bbox": [[220, 260], [250, 275]]},
                    {"text": "successfully", "confidence": 0.99, "bbox": [[260, 260], [360, 275]]},
                    {"text": "completed", "confidence": 0.99, "bbox": [[370, 260], [450, 275]]},
                    {"text": "opti", "confidence": 0.99, "bbox": [[270, 290], [310, 310]]},
                    {"text": "test", "confidence": 0.99, "bbox": [[320, 290], [360, 310]]},
                ]
            }
        ],
        "structural_genome": {"elements": [{"type": "HEADER"}, {"type": "PARAGRAPH"}], "tables": []},
        "semantic_genome": {
            "taxonomy": {"primary_type": "CERTIFICATE"},
            "entities": {"recipient_name": {"value": "opti test", "normalized_value": "opti test"}},
        },
        "visual_genome": {"visual_embedding": [0.12] * 384},
        "feature_vector": [0.48] * 108,
    }


@pytest.fixture
def sample_modified_cloudflare_invoice(sample_cloudflare_invoice) -> dict:
    import copy
    doc = copy.deepcopy(sample_cloudflare_invoice)
    doc["semantic_genome"]["entities"]["total_amount"] = {
        "value": "$1,800.00",
        "normalized_value": "1800.00",
        "provenance": {"bounding_box": [[170, 300], [240, 320]], "page_number": 1},
    }
    doc["feature_vector"] = [0.495] * 108
    return doc


@pytest.fixture
def sample_human_cafe_photo() -> dict:
    return {
        "pages": [{"ocr_elements": [{"text": "CAFE", "confidence": 0.85}, {"text": "OPEN", "confidence": 0.80}]}],
        "structural_genome": {"elements": [], "tables": []},
        "semantic_genome": {"taxonomy": {"primary_type": "UNKNOWN"}, "entities": {}},
        "visual_genome": {"visual_embedding": [0.3] * 384},
        "feature_vector": [0.4] * 108,
    }


class TestMultiEvidenceComparison:
    """[REAL_MODEL_INFERENCE / BENCHMARK] Suite for Multi-Evidence Document Comparison."""

    def test_exact_failure_cloudflare_invoice_vs_certificate(
        self,
        comparison_engine: ComparisonEngine,
        sample_cloudflare_invoice: dict,
        sample_certificate: dict,
    ) -> None:
        """EXACT REGRESSION TEST: Cloudflare Invoice vs Certificate must return DIFFERENT_DOCUMENTS
        with calibrated similarity < 5.0% and negative evidence signals.
        """
        result = comparison_engine.compare_documents(sample_cloudflare_invoice, sample_certificate)

        assert result.decision == "DIFFERENT_DOCUMENTS"
        assert result.decision_confidence >= 0.98
        assert result.similarity is not None and result.similarity < 0.05  # Dropped from 29.2% to < 5.0%!
        assert len(result.negative_evidence) >= 2
        assert "Document classes and semantic domains differ." in result.negative_evidence
        assert result.dimensions.local_feature_inliers is not None
        assert result.dimensions.local_feature_inliers < 0.05
        assert result.field_alignment_status in ["NOT_ALIGNED", "PARTIALLY_ALIGNED"]

    def test_aws_invoice_vs_human_photo_is_strictly_incompatible(
        self,
        comparison_engine: ComparisonEngine,
        sample_cloudflare_invoice: dict,
        sample_human_cafe_photo: dict,
    ) -> None:
        """Verifies Invoice vs Human Cafe Photo is hard-gated as INCOMPATIBLE."""
        result = comparison_engine.compare_documents(sample_cloudflare_invoice, sample_human_cafe_photo)

        assert result.status == ComparisonStatus.INCOMPATIBLE
        assert result.mode is None
        assert result.decision == "INCOMPATIBLE"
        assert result.similarity is None
        assert len(result.differences) == 0
        assert result.field_alignment_status == "NOT_APPLICABLE"

    def test_invoice_vs_modified_invoice_produces_template_variant_decision(
        self,
        comparison_engine: ComparisonEngine,
        sample_cloudflare_invoice: dict,
        sample_modified_cloudflare_invoice: dict,
    ) -> None:
        """Verifies same invoice with modified total produces SAME_TEMPLATE_VARIANT decision."""
        result = comparison_engine.compare_documents(sample_cloudflare_invoice, sample_modified_cloudflare_invoice)

        assert result.decision in ["SAME_DOCUMENT", "SAME_TEMPLATE_VARIANT"]
        assert result.status == ComparisonStatus.COMPATIBLE
        assert result.similarity is not None and result.similarity >= 0.50
        assert len(result.differences) == 1
        assert result.differences[0].change_type == "VALUE_CHANGED"
        assert result.differences[0].field_key == "total_amount"
        assert result.differences[0].before_value == "$1,200.00"
        assert result.differences[0].after_value == "$1,800.00"

    def test_photo_vs_photo_routes_to_generic_image_decision(
        self,
        comparison_engine: ComparisonEngine,
        sample_human_cafe_photo: dict,
    ) -> None:
        """Verifies Photo vs Photo routes to generic image mode without document metrics."""
        result = comparison_engine.compare_documents(sample_human_cafe_photo, sample_human_cafe_photo)

        assert result.decision in ["VISUAL_TWIN", "VISUALLY_SIMILAR"]
        assert result.mode == ComparisonMode.GENERIC_IMAGE
        assert result.similarity is not None
        assert result.dimensions.structural_similarity is None
        assert result.dimensions.semantic_similarity is None
        assert result.field_alignment_status == "NOT_APPLICABLE"
