"""Model Inference Arbitrator and Consistency Layer.

Resolves disagreements between OCR, Layout, Table Detectors, KIE, and VLM models,
generating explicit consensus evidence and flagging forensic tampering/drift signals.
"""

from __future__ import annotations
from typing import Any
import numpy as np

from src.domain.entities.evidence_graph import DocumentEvidenceGraph, EvidenceNode, GroundedEntity
from src.domain.entities.structural_genome import StructuralElement, StructuredTable
from src.domain.entities.template_genome import AnomalySignal
from src.utils.logging import get_logger

logger = get_logger(__name__)


class InferenceArbitrator:
    """Arbitrates multi-model predictions and validates cross-engine consistency."""

    def arbitrate_tables(
        self,
        pps_tables: list[StructuredTable],
        tatr_tables: list[StructuredTable],
        fallback_tables: list[StructuredTable],
    ) -> list[StructuredTable]:
        """Arbitrates between PP-Structure, Table Transformer, and Morphological tables."""
        if tatr_tables and any(t.extraction_method == "table_transformer_real" for t in tatr_tables):
            return tatr_tables
        if pps_tables:
            return pps_tables
        return fallback_tables

    def arbitrate_entities(
        self,
        deterministic_entities: dict[str, GroundedEntity],
        vlm_entities: dict[str, GroundedEntity],
    ) -> tuple[dict[str, GroundedEntity], list[AnomalySignal]]:
        """Resolves field extraction candidates and flags semantic contradictions."""
        final_entities = dict(deterministic_entities)
        anomaly_signals: list[AnomalySignal] = []

        for key, vlm_ent in vlm_entities.items():
            if key not in final_entities:
                final_entities[key] = vlm_ent
                continue

            det_ent = final_entities[key]
            # If values disagree between deterministic extraction and VLM
            if str(det_ent.normalized_value).strip().lower() != str(vlm_ent.normalized_value).strip().lower():
                anomaly_signals.append(
                    AnomalySignal(
                        signal_id=f"discrepancy_{key}",
                        category="SEMANTIC_CONTRADICTION",
                        severity="HIGH",
                        description=(
                            f"Disagreement for field '{key}': deterministic extraction found "
                            f"'{det_ent.value}' whereas VLM extracted '{vlm_ent.value}'."
                        ),
                        details={
                            "field_key": key,
                            "deterministic_val": str(det_ent.value),
                            "vlm_val": str(vlm_ent.value),
                            "det_method": det_ent.provenance.extraction_method if det_ent.provenance else "",
                            "vlm_method": vlm_ent.provenance.extraction_method if vlm_ent.provenance else "",
                        },
                    )
                )
                # Escalate to higher confidence
                if vlm_ent.confidence > det_ent.confidence:
                    final_entities[key] = vlm_ent

        return final_entities, anomaly_signals

    def compute_bbox_iou(self, bbox_a: list[list[float]], bbox_b: list[list[float]]) -> float:
        """Computes 2D axis-aligned Intersection over Union (IoU) of two 4-point polygons."""
        if len(bbox_a) < 4 or len(bbox_b) < 4:
            return 0.0

        ax1, ay1 = bbox_a[0][0], bbox_a[0][1]
        ax2, ay2 = bbox_a[2][0], bbox_a[2][1]

        bx1, by1 = bbox_b[0][0], bbox_b[0][1]
        bx2, by2 = bbox_b[2][0], bbox_b[2][1]

        # Intersection box
        ix1 = max(ax1, bx1)
        iy1 = max(ay1, by1)
        ix2 = min(ax2, bx2)
        iy2 = min(ay2, by2)

        iw = max(0.0, ix2 - ix1)
        ih = max(0.0, iy2 - iy1)
        intersection_area = iw * ih

        area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
        area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
        union_area = area_a + area_b - intersection_area

        if union_area <= 1e-6:
            return 0.0

        return round(float(intersection_area / union_area), 4)
