"""Comprehensive component health check endpoint."""

import os
from datetime import datetime, timezone
import time

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.dependencies import get_db
from src.config.settings import get_settings
from src.schemas.responses import BuildInfoSchema, ComponentHealth, HealthResponse
from src.utils.build_info import get_build_info

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Comprehensive health check",
    description="Probes API, Database, Storage, OCR Engine, and Filesystem components independently.",
)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    components: dict[str, ComponentHealth] = {}
    overall_status = "healthy"

    # 1. API probe
    api_details: dict = {}
    try:
        import psutil
        process = psutil.Process()
        api_details["memory_mb"] = round(process.memory_info().rss / (1024 * 1024), 1)
        api_details["cpu_percent"] = round(psutil.cpu_percent(interval=None), 1)
    except Exception:
        pass

    components["api"] = ComponentHealth(status="healthy", latency_ms=0.1, details=api_details)

    # 2. Database probe
    db_start = time.perf_counter()
    try:
        await db.execute(text("SELECT 1"))
        db_ms = (time.perf_counter() - db_start) * 1000.0
        components["database"] = ComponentHealth(status="healthy", latency_ms=round(db_ms, 2))
    except Exception as e:
        db_ms = (time.perf_counter() - db_start) * 1000.0
        components["database"] = ComponentHealth(
            status="degraded", latency_ms=round(db_ms, 2), details={"error": str(e), "note": "Local storage persistence fallback active"}
        )
        if overall_status == "healthy":
            overall_status = "degraded"

    # 3. Storage & Filesystem probe
    storage_start = time.perf_counter()
    try:
        temp_dir = settings.processing.temp_dir
        os.makedirs(temp_dir, exist_ok=True)
        test_file = os.path.join(temp_dir, ".health_check.tmp")
        with open(test_file, "w") as f:
            f.write("health_ok")
        if os.path.exists(test_file):
            os.remove(test_file)
        st_ms = (time.perf_counter() - storage_start) * 1000.0
        components["storage"] = ComponentHealth(
            status="healthy", latency_ms=round(st_ms, 2), details={"path": settings.processing.storage_root}
        )
        components["filesystem"] = ComponentHealth(
            status="healthy", latency_ms=round(st_ms, 2), details={"temp_dir_writable": True}
        )
    except Exception as e:
        st_ms = (time.perf_counter() - storage_start) * 1000.0
        components["storage"] = ComponentHealth(
            status="unhealthy", latency_ms=round(st_ms, 2), details={"error": str(e)}
        )
        components["filesystem"] = ComponentHealth(
            status="unhealthy", latency_ms=round(st_ms, 2), details={"temp_dir_writable": False}
        )
        overall_status = "unhealthy"

    # 4. OCR Engine probe
    ocr_start = time.perf_counter()
    provider = settings.ocr.engine_provider
    dev_fallback = settings.ocr.dev_ocr_fallback
    ocr_ms = (time.perf_counter() - ocr_start) * 1000.0

    if provider == "paddleocr" and not dev_fallback:
        try:
            import paddleocr  # noqa: F401
            components["ocr_engine"] = ComponentHealth(
                status="healthy",
                latency_ms=round(ocr_ms, 2),
                details={"engine": "paddleocr", "mode": "production_deterministic"},
            )
        except Exception:
            components["ocr_engine"] = ComponentHealth(
                status="unhealthy",
                latency_ms=round(ocr_ms, 2),
                details={"engine": "paddleocr", "mode": "production", "error": "PaddleOCR package missing"},
            )
            overall_status = "degraded"
    else:
        components["ocr_engine"] = ComponentHealth(
            status="degraded" if dev_fallback else "healthy",
            latency_ms=round(ocr_ms, 2),
            details={
                "engine": provider,
                "dev_fallback_active": dev_fallback,
                "note": "Dev fallback active — determinism not guaranteed across environments",
            },
        )

    # Build Info
    b_info = get_build_info()
    build_schema = BuildInfoSchema(
        app_version=b_info.app_version,
        git_commit=b_info.git_commit,
        build_date=b_info.build_date,
        python_version=b_info.python_version,
        schema_version=b_info.schema_version,
        feature_version=b_info.feature_version,
        pipeline_version=b_info.pipeline_version,
    )

    return HealthResponse(
        status=overall_status,
        version=settings.processing.pipeline_version,
        environment=settings.api.environment,
        timestamp=datetime.now(timezone.utc).isoformat(),
        components=components,
        build_info=build_schema,
    )
