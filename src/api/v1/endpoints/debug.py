"""Development pipeline inspection endpoint (DEBUG_PIPELINE=true mode)."""

import dataclasses

from typing import Any
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.dependencies import get_db
from src.application.context.processing_context import ProcessingContext
from src.application.registry.pipeline_registry import get_default_pipeline_registry
from src.config.settings import get_settings
from src.domain.error_catalog import ERR_VALIDATION_SIZE_EXCEEDED
from src.domain.exceptions import ValidationError

router = APIRouter(tags=["debug"])
settings = get_settings()


@router.post(
    "/genome/debug",
    summary="Inspect intermediate pipeline artifacts (Development Only)",
    description=(
        "Executes the processing pipeline and returns intermediate debug artifacts "
        "(OCR text & boxes, page dimensions, feature group breakdowns, step timings). "
        "Requires DEBUG_PIPELINE=true and non-production environment."
    ),
)
async def debug_pipeline_inspection(
    file: UploadFile = File(..., description="Document file to inspect"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Development-only inspection endpoint exposing intermediate pipeline context state."""
    # Enforce development-only security restriction
    if not settings.processing.debug_pipeline or settings.api.environment.lower() == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Pipeline debug inspection is disabled. Set DEBUG_PIPELINE=true in non-production environment.",
        )

    file_bytes = await file.read()
    filename = file.filename or "uploaded_document"

    if len(file_bytes) > settings.security.max_file_size_bytes:
        raise ValidationError(
            f"File size {len(file_bytes)} bytes exceeds limit {settings.security.max_file_size_bytes} bytes.",
            entry=ERR_VALIDATION_SIZE_EXCEEDED,
        )

    context = ProcessingContext.create(
        uploaded_file_bytes=file_bytes,
        original_filename=filename,
        mime_type=file.content_type or "application/octet-stream",
        working_directory=settings.processing.temp_dir,
    )

    registry = get_default_pipeline_registry(db)
    orchestrator = registry.build_orchestrator()
    context = await orchestrator.run(context)

    # Serialize intermediate inspection data
    debug_output: dict[str, Any] = {
        "request_id": str(context.request_id),
        "job_id": str(context.job_id),
        "original_filename": context.original_filename,
        "file_size_bytes": len(context.uploaded_file_bytes),
        "metadata": {
            "mime_type": context.document.mime_type if context.document else None,
            "page_count": context.document.page_count if context.document else 0,
            "hash_sha256": context.document.hashes.sha256 if context.document else None,
        },
        "rendered_pages": [
            {
                "page_number": p.page_number,
                "width_px": p.width_px,
                "height_px": p.height_px,
                "dpi": p.dpi,
            }
            for p in context.rendered_pages
        ],
        "normalized_pages": [
            {
                "page_number": p.page_number,
                "skew_angle_deg": round(p.skew_angle_deg, 2),
                "color_space": p.color_space,
            }
            for p in context.normalized_pages
        ],
        "page_quality_reports": [
            {
                "page_id": str(q.page_id),
                "blur_score": q.blur_score,
                "sharpness_score": q.sharpness_score,
                "contrast_score": q.contrast_score,
                "noise_score": q.noise_score,
                "metrics": q.metrics,
            }
            for q in context.page_quality_reports
        ],
        "ocr_results": [
            {
                "page_number": o.page_number,
                "element_count": len(o.elements),
                "total_words": o.total_words,
                "mean_confidence": round(o.mean_confidence, 4),
                "elements": [
                    {
                        "id": e.id,
                        "text": e.text,
                        "confidence": round(e.confidence * (100.0 if e.confidence <= 1.0 else 1.0), 1),
                        "bbox": e.bbox,
                        "page_number": e.page_number,
                    }
                    for e in o.elements
                ],
            }
            for o in context.ocr_results
        ],
        "layout_results": [
            {
                "page_number": l.page_number,
                "region_count": len(l.regions),
                "reading_order_len": len(l.reading_order),
            }
            for l in context.layout_results
        ],
        "feature_groups": [
            {
                "name": g.name,
                "version": g.version,
                "feature_count": g.feature_count,
                "extraction_time_ms": g.extraction_time_ms,
                "features": g.features,
            }
            for g in context.extracted_feature_groups
        ],
        "processing_manifest": dataclasses.asdict(context.processing_manifest) if context.processing_manifest else None,
        "warnings": [w.message for w in context.warnings],
        "errors": [e.message for e in context.errors],
    }

    return debug_output
