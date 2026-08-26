"""Unit tests for the upgraded Forensic Document Intelligence & Template Engine."""

import pytest
import numpy as np

from src.domain.entities.structural_genome import StructuralElement, StructuredTable
from src.domain.interfaces.ocr_engine import OCRPageResult, OCRTextElement
from src.processing.layout.advanced_layout_analyzer import AdvancedLayoutAnalyzer
from src.processing.tables.table_extractor import StructuredTableExtractor
from src.processing.semantic.document_classifier import DocumentClassifier
from src.processing.semantic.kie_extractor import GroundedKIEExtractor
from src.processing.visual.dinov2_extractor import VisualEmbeddingExtractor
from src.processing.template.template_intelligence_engine import TemplateIntelligenceEngine


class TestForensicDocumentIntelligence:

    def test_advanced_layout_analyzer(self) -> None:
        analyzer = AdvancedLayoutAnalyzer()
        mock_elements = [
            OCRTextElement(id=1, text="ACME CORPORATION INVOICE", confidence=0.98, bbox=[[50, 40], [400, 40], [400, 70], [50, 70]], page_number=1),
            OCRTextElement(id=2, text="Invoice Number: INV-2026-001", confidence=0.95, bbox=[[50, 100], [300, 100], [300, 120], [50, 120]], page_number=1),
            OCRTextElement(id=3, text="Total Amount: $1,250.00", confidence=0.96, bbox=[[50, 500], [250, 500], [250, 525], [50, 525]], page_number=1),
        ]
        ocr_res = OCRPageResult(
            page_number=1,
            elements=mock_elements,
            mean_confidence=0.96,
            total_words=len(mock_elements),
            raw_output={},
        )
        elements, reading_order = analyzer.analyze_page(ocr_res, page_width=1000, page_height=1400)

        assert len(elements) >= 2
        assert len(reading_order) == len(elements)
        assert elements[0].element_type == "HEADER"

    def test_document_classifier(self) -> None:
        classifier = DocumentClassifier()
        mock_elements = [
            OCRTextElement(id=1, text="INVOICE", confidence=0.99, bbox=[[10, 10], [50, 10], [50, 30], [10, 30]], page_number=1),
            OCRTextElement(id=2, text="Bill To: John Doe", confidence=0.95, bbox=[[10, 50], [100, 50], [100, 70], [10, 70]], page_number=1),
            OCRTextElement(id=3, text="Total Amount Due: $500.00", confidence=0.97, bbox=[[10, 90], [150, 90], [150, 110], [10, 110]], page_number=1),
        ]
        ocr_res = OCRPageResult(
            page_number=1,
            elements=mock_elements,
            mean_confidence=0.96,
            total_words=len(mock_elements),
            raw_output={},
        )
        taxonomy = classifier.classify_document([ocr_res])

        assert taxonomy.primary_type == "INVOICE"
        assert taxonomy.confidence >= 0.70

    def test_grounded_kie_extractor_with_math_validation(self) -> None:
        extractor = GroundedKIEExtractor()
        mock_elements = [
            OCRTextElement(id=1, text="Acme Supply Ltd", confidence=0.99, bbox=[[50, 20], [200, 20], [200, 40], [50, 40]], page_number=1),
            OCRTextElement(id=2, text="Invoice # INV-99882", confidence=0.98, bbox=[[50, 60], [220, 60], [220, 80], [50, 80]], page_number=1),
            OCRTextElement(id=3, text="Date: Jan 15, 2026", confidence=0.95, bbox=[[50, 100], [200, 100], [200, 120], [50, 120]], page_number=1),
            OCRTextElement(id=4, text="Subtotal: $1000.00", confidence=0.96, bbox=[[50, 300], [200, 300], [200, 320], [50, 320]], page_number=1),
            OCRTextElement(id=5, text="Tax: $100.00", confidence=0.95, bbox=[[50, 330], [150, 330], [150, 350], [50, 350]], page_number=1),
            OCRTextElement(id=6, text="Total: $1100.00", confidence=0.99, bbox=[[50, 360], [180, 360], [180, 380], [50, 380]], page_number=1),
        ]
        ocr_res = OCRPageResult(
            page_number=1,
            elements=mock_elements,
            mean_confidence=0.96,
            total_words=len(mock_elements),
            raw_output={},
        )
        entities, relationships = extractor.extract_entities([ocr_res], doc_type="INVOICE")

        assert "invoice_number" in entities
        assert entities["invoice_number"].normalized_value == "INV-99882"
        assert entities["invoice_number"].provenance.page_number == 1
        assert entities["invoice_number"].provenance.source_ocr_token_ids == ["2"]

        assert "total_amount" in entities
        assert entities["total_amount"].normalized_value == 1100.0
        assert len(relationships) >= 1
        assert relationships[0].is_valid is True

    def test_visual_embedding_extractor(self) -> None:
        extractor = VisualEmbeddingExtractor(embedding_dimension=384)
        # Create a synthetic white page image with text bar
        import cv2
        img = np.full((300, 300, 3), 255, dtype=np.uint8)
        cv2.rectangle(img, (50, 50), (250, 100), (0, 0, 0), -1)
        _, buf = cv2.imencode(".png", img)

        visual_genome = extractor.extract_visual_genome(buf.tobytes())
        assert visual_genome.embedding_dimension == 384
        assert len(visual_genome.visual_embedding) == 384
        assert len(visual_genome.perceptual_hash) > 0

    def test_template_intelligence_engine(self) -> None:
        extractor = VisualEmbeddingExtractor(embedding_dimension=384)
        img = np.full((300, 300, 3), 255, dtype=np.uint8)
        import cv2
        _, buf = cv2.imencode(".png", img)
        v_genome = extractor.extract_visual_genome(buf.tobytes())

        engine = TemplateIntelligenceEngine()
        template_genome = engine.analyze(
            structural_genome=None,
            semantic_genome=None,
            visual_genome=v_genome,
        )

        assert template_genome is not None
        assert hasattr(template_genome, "structural_drift_score")
        assert hasattr(template_genome, "visual_drift_score")
        assert hasattr(template_genome, "is_anomaly")
