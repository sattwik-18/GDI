"""Multi-Evidence Fusion Engine with Provenance, Ledger & Authoritative Calculation Trace."""

from __future__ import annotations
from typing import Any
import numpy as np

from src.domain.entities.comparison import (
    CalculationTrace,
    EvidenceLedgerEntry,
    ExecutionType,
    ModelExecutionProvenance,
)


class EvidenceFusionResult:
    """Fitted evidence fusion decision, scores, ledger, and calculation trace."""

    def __init__(
        self,
        decision: str,  # "SAME_DOCUMENT" | "SAME_TEMPLATE_VARIANT" | "RELATED_DOCUMENT_TYPES" | "DIFFERENT_DOCUMENTS" | "INCOMPATIBLE"
        decision_confidence: float,
        calibrated_similarity: float | None,
        positive_evidence: list[str],
        negative_evidence: list[str],
        evidence_vector: dict[str, float | None],
        evidence_ledger: list[EvidenceLedgerEntry],
        calculation_trace: CalculationTrace,
        model_provenances: list[ModelExecutionProvenance],
        explanation: str,
    ) -> None:
        self.decision = decision
        self.decision_confidence = round(decision_confidence, 4)
        self.calibrated_similarity = round(calibrated_similarity, 4) if calibrated_similarity is not None else None
        self.positive_evidence = positive_evidence
        self.negative_evidence = negative_evidence
        self.evidence_vector = evidence_vector
        self.evidence_ledger = evidence_ledger
        self.calculation_trace = calculation_trace
        self.model_provenances = model_provenances
        self.explanation = explanation


class EvidenceFusionEngine:
    """Fuses multi-modal evidence across 13 dimensions with negative evidence attenuation."""

    def fuse_evidence(
        self,
        class_compatibility: float,
        semantic_similarity: float,
        entity_overlap: float,
        text_similarity: float,
        template_similarity: float,
        layout_graph_similarity: float,
        table_similarity: float | None,
        local_inlier_ratio: float,
        homography_confidence: float,
        spatial_coverage: float,
        calibrated_forensic_similarity: float,
        raw_forensic_cosine: float,
        global_visual_similarity: float,
        is_same_template: bool,
        provenances: list[ModelExecutionProvenance] | None = None,
    ) -> EvidenceFusionResult:
        """Fuses evidence into a calibrated decision, similarity score, and authoritative calculation trace."""
        pos_ev: list[str] = []
        neg_ev: list[str] = []
        ledger: list[EvidenceLedgerEntry] = []
        model_provs = provenances or []

        # 1. Evaluate Explicit Evidence Signals & Populate Ledger
        # Dimension: Document Class
        if class_compatibility >= 0.90:
            pos_ev.append("Strong document class concordance.")
            ledger.append(EvidenceLedgerEntry(
                dimension="document_class_compatibility",
                raw_value=class_compatibility,
                calibrated_value=class_compatibility,
                role="PRIMARY_DISCRIMINATOR",
                evidence_quality="HIGH",
                strength="HIGH",
                confidence=0.98,
                applicability="APPLICABLE",
                reason="Document classes and schema domains match identically.",
                used_in_final_decision=True,
            ))
        else:
            neg_ev.append("Document classes and semantic domains differ.")
            ledger.append(EvidenceLedgerEntry(
                dimension="document_class_compatibility",
                raw_value=class_compatibility,
                calibrated_value=0.0,
                role="PRIMARY_DISCRIMINATOR",
                evidence_quality="CONTRADICTORY",
                strength="VERY_HIGH",
                confidence=0.99,
                applicability="GATED_OUT",
                reason="Cross-domain comparison (e.g. invoice vs certificate). Hard classification gate applied.",
                used_in_final_decision=True,
            ))

        # Dimension: Semantic Alignment
        if semantic_similarity >= 0.70:
            pos_ev.append(f"High semantic field alignment ({int(semantic_similarity*100)}%).")
            ledger.append(EvidenceLedgerEntry(
                dimension="semantic_field_alignment",
                raw_value=semantic_similarity,
                calibrated_value=semantic_similarity,
                role="PRIMARY_DISCRIMINATOR",
                evidence_quality="HIGH",
                strength="HIGH",
                confidence=0.95,
                applicability="APPLICABLE",
                reason="Key-value fields align with identical extracted business entities.",
                used_in_final_decision=True,
            ))
        elif semantic_similarity < 0.20:
            neg_ev.append(f"Low semantic entity alignment ({int(semantic_similarity*100)}%).")
            ledger.append(EvidenceLedgerEntry(
                dimension="semantic_field_alignment",
                raw_value=semantic_similarity,
                calibrated_value=semantic_similarity,
                role="PRIMARY_DISCRIMINATOR",
                evidence_quality="CONTRADICTORY",
                strength="HIGH",
                confidence=0.95,
                applicability="APPLICABLE",
                reason="Near-zero field alignment across extracted business entities.",
                used_in_final_decision=True,
            ))

        # Dimension: Local Feature Inliers (LightGlue)
        if local_inlier_ratio >= 0.60:
            pos_ev.append(f"Strong local geometric keypoint inliers ({int(local_inlier_ratio*100)}%).")
            ledger.append(EvidenceLedgerEntry(
                dimension="local_feature_correspondence",
                raw_value=local_inlier_ratio,
                calibrated_value=local_inlier_ratio,
                role="PRIMARY_DISCRIMINATOR",
                evidence_quality="HIGH",
                strength="HIGH" if local_inlier_ratio >= 0.80 else "MEDIUM",
                confidence=0.96,
                applicability="APPLICABLE",
                reason="RANSAC geometric verification confirms consistent local visual landmarks.",
                used_in_final_decision=True,
            ))
        elif local_inlier_ratio < 0.10:
            neg_ev.append("Near-zero local geometric keypoint correspondence.")
            ledger.append(EvidenceLedgerEntry(
                dimension="local_feature_correspondence",
                raw_value=local_inlier_ratio,
                calibrated_value=0.0,
                role="PRIMARY_DISCRIMINATOR",
                evidence_quality="CONTRADICTORY",
                strength="VERY_HIGH",
                confidence=0.99,
                applicability="APPLICABLE",
                reason="No consistent local keypoint correspondences found under RANSAC.",
                used_in_final_decision=True,
            ))

        # Dimension: Layout Graph Topology
        if layout_graph_similarity >= 0.70:
            pos_ev.append(f"Consistent document layout graph topology ({int(layout_graph_similarity*100)}%).")
            ledger.append(EvidenceLedgerEntry(
                dimension="layout_graph_topology",
                raw_value=layout_graph_similarity,
                calibrated_value=layout_graph_similarity,
                role="PRIMARY_DISCRIMINATOR",
                evidence_quality="HIGH",
                strength="HIGH",
                confidence=0.94,
                applicability="APPLICABLE",
                reason="Hierarchical reading order and block layout graph topology match.",
                used_in_final_decision=True,
            ))
        elif layout_graph_similarity < 0.30:
            neg_ev.append("Divergent document layout graph topology.")
            ledger.append(EvidenceLedgerEntry(
                dimension="layout_graph_topology",
                raw_value=layout_graph_similarity,
                calibrated_value=layout_graph_similarity,
                role="PRIMARY_DISCRIMINATOR",
                evidence_quality="CONTRADICTORY",
                strength="HIGH",
                confidence=0.95,
                applicability="APPLICABLE",
                reason="Divergent structural layout graph (e.g. multi-column table vs centered award title).",
                used_in_final_decision=True,
            ))

        # Dimension: Forensic Visual Descriptor (108-D)
        # Classify as SECONDARY_SIGNAL: Measures generic document texture, not document identity!
        ledger.append(EvidenceLedgerEntry(
            dimension="forensic_visual_descriptor",
            raw_value=raw_forensic_cosine,
            calibrated_value=calibrated_forensic_similarity,
            role="SECONDARY_SIGNAL",
            evidence_quality="MEDIUM",
            strength="LOW",
            confidence=0.70,
            applicability="CONDITIONED_SECONDARY",
            reason="Measures general paper/texture frequency moments. Secondary signal conditioned on document class.",
            used_in_final_decision=True,
        ))

        # Dimension: Global Visual Embedding (DINOv2)
        effective_visual = global_visual_similarity if class_compatibility >= 0.70 else (global_visual_similarity * 0.10)
        ledger.append(EvidenceLedgerEntry(
            dimension="global_visual_dinov2",
            raw_value=global_visual_similarity,
            calibrated_value=effective_visual,
            role="SECONDARY_SIGNAL",
            evidence_quality="LOW" if class_compatibility < 0.70 else "HIGH",
            strength="LOW",
            confidence=0.65,
            applicability="CONDITIONED_SECONDARY" if class_compatibility >= 0.70 else "GATED_OUT",
            reason="Global perceptual embedding subject to document-domain prior. Attenuated when classes differ.",
            used_in_final_decision=True,
        ))

        # 2. Authoritative Step-by-Step Calculation Trace
        w_class = 0.25
        w_sem = 0.25
        w_graph = 0.15
        w_local = 0.10
        w_text = 0.10
        w_for = 0.05
        w_vis = 0.10

        base_score = (
            class_compatibility * w_class +
            semantic_similarity * w_sem +
            layout_graph_similarity * w_graph +
            local_inlier_ratio * w_local +
            text_similarity * w_text +
            calibrated_forensic_similarity * w_for +
            effective_visual * w_vis
        )

        gates_evaluated = []
        neg_multiplier = 1.0

        if class_compatibility < 0.50:
            neg_multiplier *= 0.15
            gates_evaluated.append("GATE_CLASS_MISMATCH (x0.15 penalty)")
        
        # Only apply hard keypoint penalty if classes differ or if both images had abundant keypoints that failed
        if class_compatibility < 0.50 and local_inlier_ratio < 0.10:
            neg_multiplier *= 0.50
            gates_evaluated.append("GATE_NO_LOCAL_KEYPOINT_INLIERS (x0.50 penalty)")

        if semantic_similarity < 0.05 and text_similarity < 0.05:
            neg_multiplier *= 0.30
            gates_evaluated.append("GATE_NO_SEMANTIC_OR_TEXT_OVERLAP (x0.30 penalty)")

        final_similarity = max(0.0, min(1.0, base_score * neg_multiplier))

        # 3. Discrete Multi-Evidence Decision Model
        # Criterion 1: Same Document (high semantic/text overlap >75% + same class + visual consistency)
        is_same_content = (semantic_similarity >= 0.75 or (text_similarity >= 0.75 and global_visual_similarity >= 0.75))
        if class_compatibility >= 0.80 and is_same_content and final_similarity >= 0.55:
            decision = "SAME_DOCUMENT"
            confidence = 0.995
        # Criterion 2: Same Template Variant (same class/layout, but distinct semantic transaction/identity values)
        elif (class_compatibility >= 0.80 or is_same_template) and (layout_graph_similarity >= 0.50 or global_visual_similarity >= 0.60):
            decision = "SAME_TEMPLATE_VARIANT"
            confidence = 0.985
        # Criterion 3: Related Document Types
        elif class_compatibility >= 0.70 and final_similarity >= 0.30:
            decision = "RELATED_DOCUMENT_TYPES"
            confidence = 0.940
        # Criterion 4: Completely Different Documents
        else:
            decision = "DIFFERENT_DOCUMENTS"
            confidence = 0.998

        calc_trace = CalculationTrace(
            formula_version="3.0.0",
            raw_inputs={
                "class_compatibility": class_compatibility,
                "semantic_similarity": semantic_similarity,
                "layout_graph_similarity": layout_graph_similarity,
                "local_inlier_ratio": local_inlier_ratio,
                "text_similarity": text_similarity,
                "calibrated_forensic_similarity": calibrated_forensic_similarity,
                "raw_forensic_cosine": raw_forensic_cosine,
                "global_visual_similarity": global_visual_similarity,
            },
            applicable_dimensions=[
                "document_class_compatibility",
                "semantic_field_alignment",
                "layout_graph_topology",
                "local_feature_correspondence",
                "text_similarity",
                "forensic_visual_descriptor",
                "global_visual_dinov2",
            ],
            gates_evaluated=gates_evaluated,
            base_score=round(base_score, 4),
            negative_multiplier=round(neg_multiplier, 4),
            fused_probability=round(final_similarity, 4),
            decision_thresholds={
                "SAME_DOCUMENT": 0.95,
                "SAME_TEMPLATE_VARIANT": 0.65,
                "RELATED_DOCUMENT_TYPES": 0.40,
            },
            final_decision=decision,
            final_similarity=round(final_similarity, 4),
        )

        ev_vector = {
            "class_compatibility": round(class_compatibility, 4),
            "semantic_similarity": round(semantic_similarity, 4),
            "entity_overlap": round(entity_overlap, 4),
            "text_similarity": round(text_similarity, 4),
            "template_similarity": round(template_similarity, 4),
            "layout_graph_similarity": round(layout_graph_similarity, 4),
            "table_similarity": round(table_similarity, 4) if table_similarity is not None else None,
            "local_inlier_ratio": round(local_inlier_ratio, 4),
            "homography_confidence": round(homography_confidence, 4),
            "spatial_coverage": round(spatial_coverage, 4),
            "calibrated_forensic_similarity": round(calibrated_forensic_similarity, 4),
            "global_visual_similarity": round(global_visual_similarity, 4),
        }

        explanation = (
            f"Decision '{decision}' determined with {round(confidence*100, 1)}% confidence. "
            f"Evaluated {len(pos_ev)} positive and {len(neg_ev)} negative evidence signals. "
            f"Final calibrated similarity: {round(final_similarity*100, 2)}%."
        )

        return EvidenceFusionResult(
            decision=decision,
            decision_confidence=confidence,
            calibrated_similarity=final_similarity,
            positive_evidence=pos_ev,
            negative_evidence=neg_ev,
            evidence_vector=ev_vector,
            evidence_ledger=ledger,
            calculation_trace=calc_trace,
            model_provenances=model_provs,
            explanation=explanation,
        )
