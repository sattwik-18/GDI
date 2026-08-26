"""GenomeAssembler: combines FeatureGroups and context data into a DocumentGenome entity."""

from datetime import datetime, timezone
import uuid

from src.application.context.processing_context import ProcessingContext
from src.config.settings import get_settings
from src.domain.entities.feature_group import FeatureGroup
from src.domain.entities.genome import DocumentGenome, GenomeSeal
from src.utils.config_fingerprint import compute_config_fingerprint


class GenomeAssembler:
    """Assembles a DocumentGenome entity from extracted FeatureGroups in the ProcessingContext."""

    def assemble(self, context: ProcessingContext) -> DocumentGenome:
        """Constructs a DocumentGenome from all feature groups in the context."""
        settings = get_settings()
        config_fp = compute_config_fingerprint(settings)

        # Flatten all feature values into a single deterministic ordered vector
        sorted_groups = sorted(context.extracted_feature_groups, key=lambda fg: fg.name)
        feature_vector: list[float] = []
        for fg in sorted_groups:
            for key in sorted(fg.features.keys()):
                val = fg.features[key]
                if isinstance(val, (int, float)):
                    feature_vector.append(float(val))

        # Build per-page genome structures
        pages: list[dict] = []
        for idx, page_entity in enumerate(context.pages):
            n_page = context.normalized_pages[idx] if idx < len(context.normalized_pages) else None
            q_report = context.page_quality_reports[idx] if idx < len(context.page_quality_reports) else None
            ocr_res = context.ocr_results[idx] if idx < len(context.ocr_results) else None
            l_res = context.layout_results[idx] if idx < len(context.layout_results) else None

            page_fgs = [
                {
                    "id": str(fg.id),
                    "name": fg.name,
                    "version": fg.version,
                    "feature_count": fg.feature_count,
                    "extraction_time_ms": fg.extraction_time_ms,
                    "features": {
                        k: v for k, v in fg.features.items()
                        if k.startswith(f"p{page_entity.page_number}_")
                    },
                }
                for fg in sorted_groups
            ]

            pages.append({
                "page_number": page_entity.page_number,
                "metadata": {
                    "page_id": str(page_entity.id),
                    "width_px": page_entity.width_px,
                    "height_px": page_entity.height_px,
                    "dpi": page_entity.dpi,
                    "orientation_deg": page_entity.orientation_deg,
                    "skew_angle_deg": n_page.skew_angle_deg if n_page else 0.0,
                },
                "feature_groups": page_fgs,
                "quality_metrics": {
                    "blur_score": q_report.blur_score,
                    "sharpness_score": q_report.sharpness_score,
                    "noise_score": q_report.noise_score,
                    "contrast_score": q_report.contrast_score,
                    "metrics": q_report.metrics,
                } if q_report else None,
                "ocr_element_count": len(ocr_res.elements) if ocr_res else 0,
                "ocr_elements": [
                    {
                        "id": str(e.id),
                        "text": e.text,
                        "confidence": round(e.confidence * (100.0 if e.confidence <= 1.0 else 1.0), 1),
                        "bbox": e.bbox,
                        "page_number": e.page_number,
                        "img_width": getattr(ocr_res, "width_px", page_entity.width_px or 1000),
                        "img_height": getattr(ocr_res, "height_px", page_entity.height_px or 1414),
                    }
                    for e in ocr_res.elements
                ] if ocr_res else [],
                "layout_region_count": len(l_res.regions) if l_res else 0,
            })

        duration_ms = (
            (context.finish_time - context.start_time).total_seconds() * 1000.0
            if context.finish_time else 0.0
        )

        doc_hash_sha256 = context.document.hashes.sha256 if context.document else ""
        doc_hash_sha3 = context.document.hashes.sha3_256 if context.document else ""

        placeholder_seal = GenomeSeal(
            feature_count=len(feature_vector),
            sha256_of_features="0" * 64,
        )

        # 1. Serialize Structural Genome
        structural_dict = None
        if context.structural_genome:
            structural_dict = {
                "total_regions": context.structural_genome.total_regions,
                "total_tables": context.structural_genome.total_tables,
                "reading_order": context.structural_genome.reading_order,
                "elements": [
                    {
                        "element_id": el.element_id,
                        "element_type": el.element_type,
                        "page_number": el.page_number,
                        "bbox": el.bbox,
                        "reading_order_index": el.reading_order_index,
                        "text": el.text,
                        "confidence": el.confidence,
                        "ocr_token_ids": el.ocr_token_ids,
                    }
                    for el in context.structural_genome.elements
                ],
                "tables": [
                    {
                        "table_id": tbl.table_id,
                        "page_number": tbl.page_number,
                        "bbox": tbl.bbox,
                        "num_rows": tbl.num_rows,
                        "num_cols": tbl.num_cols,
                        "has_header": tbl.has_header,
                        "confidence": tbl.confidence,
                        "extraction_method": tbl.extraction_method,
                        "matrix": tbl.to_matrix(),
                        "cells": [
                            {
                                "cell_id": c.cell_id,
                                "row_index": c.row_index,
                                "col_index": c.col_index,
                                "row_span": c.row_span,
                                "col_span": c.col_span,
                                "is_header": c.is_header,
                                "text": c.text,
                                "confidence": c.confidence,
                                "bbox": c.bbox,
                            }
                            for c in tbl.cells
                        ],
                    }
                    for tbl in context.extracted_tables
                ],
            }

        # 2. Serialize Semantic Genome
        semantic_dict = None
        if context.semantic_genome:
            semantic_dict = {
                "taxonomy": {
                    "primary_type": context.semantic_genome.taxonomy.primary_type,
                    "subtype": context.semantic_genome.taxonomy.subtype,
                    "confidence": context.semantic_genome.taxonomy.confidence,
                    "alternative_types": context.semantic_genome.taxonomy.alternative_types,
                },
                "entities": {
                    k: {
                        "key": ent.key,
                        "value": ent.value,
                        "normalized_value": ent.normalized_value,
                        "data_type": ent.data_type,
                        "confidence": ent.confidence,
                        "validation_status": ent.validation_status,
                        "validation_message": ent.validation_message,
                        "provenance": {
                            "page_number": ent.provenance.page_number,
                            "bbox": ent.provenance.bounding_box,
                            "source_ocr_token_ids": ent.provenance.source_ocr_token_ids,
                            "extraction_method": ent.provenance.extraction_method,
                        } if ent.provenance else None,
                    }
                    for k, ent in context.semantic_genome.entities.items()
                },
                "relationships": [
                    {
                        "relationship_type": r.relationship_type,
                        "source_entity_keys": r.source_entity_keys,
                        "target_entity_key": r.target_entity_key,
                        "is_valid": r.is_valid,
                        "details": r.details,
                    }
                    for r in context.semantic_genome.relationships
                ],
                "has_validation_errors": context.semantic_genome.has_validation_errors,
            }

        # 3. Serialize Visual Genome
        visual_dict = None
        if context.visual_genome:
            visual_dict = {
                "embedding_dimension": context.visual_genome.embedding_dimension,
                "embedding_model": context.visual_genome.embedding_model,
                "perceptual_hash": context.visual_genome.perceptual_hash,
                "color_palette": context.visual_genome.color_palette,
                "visual_embedding": context.visual_genome.visual_embedding,
            }

        # 4. Serialize Template Genome
        template_dict = None
        if context.template_genome:
            template_dict = {
                "match_result": {
                    "is_matched": context.template_genome.match_result.is_matched,
                    "template_id": context.template_genome.match_result.template_id,
                    "template_name": context.template_genome.match_result.template_name,
                    "issuer_name": context.template_genome.match_result.issuer_name,
                    "version": context.template_genome.match_result.version,
                    "overall_similarity": context.template_genome.match_result.overall_similarity,
                    "structural_similarity": context.template_genome.match_result.structural_similarity,
                    "visual_similarity": context.template_genome.match_result.visual_similarity,
                },
                "structural_drift_score": context.template_genome.structural_drift_score,
                "visual_drift_score": context.template_genome.visual_drift_score,
                "is_anomaly": context.template_genome.is_anomaly,
                "anomaly_signals": [
                    {
                        "signal_id": s.signal_id,
                        "category": s.category,
                        "severity": s.severity,
                        "description": s.description,
                        "confidence": s.confidence,
                    }
                    for s in context.template_genome.anomaly_signals
                ],
            }

        # 5. Serialize Evidence Graph
        evidence_graph_dict = None
        if context.evidence_graph:
            evidence_graph_dict = {
                "graph_id": str(context.evidence_graph.graph_id),
                "nodes": [
                    {
                        "node_id": n.node_id,
                        "node_type": n.node_type,
                        "page_number": n.page_number,
                        "bbox": n.bbox,
                        "text": n.text,
                        "confidence": n.confidence,
                        "metadata": n.metadata,
                    }
                    for n in context.evidence_graph.nodes
                ],
                "edges": [
                    {
                        "source_node_id": e.source_node_id,
                        "target_node_id": e.target_node_id,
                        "relationship": e.relationship,
                        "weight": e.weight,
                    }
                    for e in context.evidence_graph.edges
                ],
            }

        return DocumentGenome(
            id=uuid.uuid4(),
            job_id=context.job_id,
            document_id=context.document.id if context.document else uuid.uuid4(),
            schema_version=settings.processing.schema_version,
            pipeline_version=settings.processing.pipeline_version,
            feature_version=settings.processing.feature_version,
            processing_version=settings.processing.processing_version,
            config_fingerprint=config_fp,
            document_hash_sha256=doc_hash_sha256,
            document_hash_sha3_256=doc_hash_sha3,
            extraction_timestamp=context.start_time,
            processing_duration_ms=round(duration_ms, 2),
            page_count=len(pages),
            pages=pages,
            feature_vector=feature_vector,
            genome_seal=placeholder_seal,
            processing_manifest={},
            structural_genome=structural_dict,
            semantic_genome=semantic_dict,
            visual_genome=visual_dict,
            template_genome=template_dict,
            evidence_graph=evidence_graph_dict,
        )
