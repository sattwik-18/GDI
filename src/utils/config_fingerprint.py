"""Config fingerprinting utility.

Generates a deterministic SHA-256 hash representing the exact processing environment:
OCR config, Vision config, feature versions, pipeline version, schema version,
OS platform, CPU architecture, Python version, and dependency versions.
Ensures exact reproducibility of processing environment parameters.
"""

import hashlib
import json
import platform
import sys
from typing import Any

from src.config.settings import Settings, get_settings
from src.utils.build_info import get_build_info


def get_environment_details() -> dict[str, Any]:
    """Retrieves runtime system and library version details."""
    details: dict[str, Any] = {
        "python_version": sys.version.split()[0],
        "os_platform": platform.system(),
        "os_release": platform.release(),
        "cpu_architecture": platform.machine(),
    }

    # Module versions
    try:
        import cv2
        details["opencv_version"] = getattr(cv2, "__version__", "unknown")
    except Exception:
        details["opencv_version"] = "unavailable"

    try:
        import numpy
        details["numpy_version"] = getattr(numpy, "__version__", "unknown")
    except Exception:
        details["numpy_version"] = "unavailable"

    try:
        import fitz
        details["pymupdf_version"] = getattr(fitz, "__version__", "unknown")
    except Exception:
        details["pymupdf_version"] = "unavailable"

    try:
        import paddle
        details["paddlepaddle_version"] = getattr(paddle, "__version__", "unknown")
    except Exception:
        details["paddlepaddle_version"] = "unavailable"

    try:
        import paddleocr
        details["paddleocr_version"] = getattr(paddleocr, "__version__", "unknown")
    except Exception:
        details["paddleocr_version"] = "unavailable"

    b_info = get_build_info()
    details["git_commit"] = b_info.git_commit
    details["build_date"] = b_info.build_date

    return details


def compute_config_fingerprint(settings: Settings | None = None) -> str:
    """Computes a SHA-256 fingerprint hex string of active configuration parameters and environment."""
    cfg = settings or get_settings()
    env = get_environment_details()

    config_dict: dict[str, Any] = {
        "pipeline_version": cfg.processing.pipeline_version,
        "schema_version": cfg.processing.schema_version,
        "feature_version": cfg.processing.feature_version,
        "rendering_dpi": cfg.processing.rendering_dpi,
        "environment": env,
        "ocr": {
            "engine_provider": cfg.ocr.engine_provider,
            "lang": cfg.ocr.lang,
            "confidence_threshold": cfg.ocr.confidence_threshold,
            "use_gpu": cfg.ocr.use_gpu,
        },
        "vision": {
            "enable_deskew": cfg.vision.enable_deskew,
            "enable_homography": cfg.vision.enable_homography,
            "enable_color_normalization": cfg.vision.enable_color_normalization,
            "canny_lower": cfg.vision.canny_lower_threshold,
            "canny_upper": cfg.vision.canny_upper_threshold,
        },
    }

    serialized = json.dumps(config_dict, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
