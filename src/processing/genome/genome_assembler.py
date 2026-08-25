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
        )
