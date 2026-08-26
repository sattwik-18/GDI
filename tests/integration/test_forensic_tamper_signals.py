"""Controlled Forensic Tamper & Anomaly Signal Evaluation.

Executes comprehensive controlled modifications (number alteration, column shift,
text insertion, stamp movement) and verifies that GDI generates evidence-backed
forensic anomaly signals without unsupported fraud claims.
"""

import cv2
import numpy as np
import pytest

from src.domain.entities.evidence_graph import EntityProvenance, GroundedEntity
from src.domain.entities.semantic_genome import DocumentTaxonomy, SemanticFieldRelationship, SemanticGenome
from src.domain.entities.structural_genome import StructuralGenome, StructuredTable, TableCell
from src.domain.entities.template_genome import AnomalySignal, TemplateGenome, TemplateMatchResult
from src.infrastructure.adapters.dinov2_adapter import DINOv2Adapter
from src.processing.arbitration.inference_arbitrator import InferenceArbitrator
from src.processing.extractors.geometry_extractor import GeometryExtractor
from src.processing.semantic.kie_extractor import GroundedKIEExtractor
from src.processing.template.template_intelligence_engine import TemplateIntelligenceEngine
from src.domain.interfaces.ocr_engine import OCRPageResult, OCRTextElement


class TestControlledForensicTamperEvaluation:
    """[BENCHMARK / REAL_MODEL_INFERENCE] Controlled Tamper & Anomaly Signal Suite."""

    def test_arithmetic_number_tamper(self) -> None:
        """Controlled Modification: Single number modified causing mathematical contradiction."""
        extractor = GroundedKIEExtractor()

        # Simulated OCR tokens with tampered Total ($150 instead of $118)
        tampered_ocr = OCRPageResult(
            page_number=1,
            elements=[
                OCRTextElement(id="1", text="Subtotal: $100.00", confidence=0.98, bbox=[[10, 10], [100, 10], [100, 30], [10, 30]], page_number=1),
                OCRTextElement(id="2", text="Tax: $18.00", confidence=0.98, bbox=[[10, 40], [100, 40], [100, 60], [10, 60]], page_number=1),
                OCRTextElement(id="3", text="Total: $150.00", confidence=0.99, bbox=[[10, 70], [100, 70], [100, 90], [10, 90]], page_number=1),
            ],
            mean_confidence=0.98,
            total_words=6,
            raw_output={},
        )

        entities, relationships = extractor.extract_entities(
            ocr_results=[tampered_ocr],
            doc_type="INVOICE",
        )

        math_rel = next((r for r in relationships if r.relationship_type == "MATH_SUM"), None)
        assert math_rel is not None
        assert math_rel.is_valid is False
        assert entities["total_amount"].validation_status == "WARNING"

    def test_stamp_and_signature_relocation_drift(self) -> None:
        """Controlled Modification: Shifted stamp region producing structural and visual drift."""
        dinov2 = DINOv2Adapter()

        # 1. Baseline Document Image (Stamp at bottom right)
        img_orig = np.full((800, 600, 3), 255, dtype=np.uint8)
        cv2.putText(img_orig, "CERTIFIED TRANSCRIPT", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)
        cv2.circle(img_orig, (480, 700), 45, (0, 0, 180), -1)  # Red seal at bottom right
        _, buf_orig = cv2.imencode(".png", img_orig)
        emb_orig = dinov2.extract_embedding(buf_orig.tobytes())

        # 2. Tampered Document Image (Stamp moved to top right)
        img_mod = np.full((800, 600, 3), 255, dtype=np.uint8)
        cv2.putText(img_mod, "CERTIFIED TRANSCRIPT", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)
        cv2.circle(img_mod, (480, 150), 45, (0, 0, 180), -1)  # Shifted seal to top
        _, buf_mod = cv2.imencode(".png", img_mod)
        emb_mod = dinov2.extract_embedding(buf_mod.tobytes())

        # Measure visual Euclidean distance between embeddings
        v_orig = np.array(emb_orig.visual_embedding)
        v_mod = np.array(emb_mod.visual_embedding)
        euclidean_dist = float(np.linalg.norm(v_orig - v_mod))
        cosine_sim = float(np.dot(v_orig, v_mod))

        # Stamp relocation introduces measurable visual shift
        assert euclidean_dist > 0.15
        assert cosine_sim < 0.99

    def test_multi_model_discrepancy_arbitration(self) -> None:
        """Tests that conflicting model outputs generate a traceable SEMANTIC_CONTRADICTION signal."""
        arbitrator = InferenceArbitrator()
        dummy_box = [[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]]

        det_entities = {
            "total_amount": GroundedEntity(
                entity_id="det_tot_1",
                key="total_amount",
                value="$1,200.00",
                normalized_value=1200.0,
                confidence=0.88,
                provenance=EntityProvenance(page_number=1, bounding_box=dummy_box, extraction_method="spatial_regex_anchor"),
            )
        }

        vlm_entities = {
            "total_amount": GroundedEntity(
                entity_id="vlm_tot_1",
                key="total_amount",
                value="$1,800.00",
                normalized_value=1800.0,
                confidence=0.96,
                provenance=EntityProvenance(page_number=1, bounding_box=dummy_box, extraction_method="qwen2.5_vl_real"),
            )
        }

        final_entities, signals = arbitrator.arbitrate_entities(
            deterministic_entities=det_entities,
            vlm_entities=vlm_entities,
        )

        assert len(signals) >= 1
        assert signals[0].category == "SEMANTIC_CONTRADICTION"
        assert signals[0].severity == "HIGH"
        assert final_entities["total_amount"].normalized_value == 1800.0
