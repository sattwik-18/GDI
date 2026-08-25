"""Build metadata provider reading environment variables set during build/deploy."""

import os
import platform
from dataclasses import dataclass

from src.config.settings import get_settings


@dataclass(frozen=True)
class BuildInfo:
    """Build and version metadata."""

    app_version: str
    git_commit: str
    build_date: str
    python_version: str
    schema_version: str
    feature_version: str
    pipeline_version: str


def get_build_info() -> BuildInfo:
    """Returns BuildInfo populated from config and environment variables."""
    settings = get_settings()
    return BuildInfo(
        app_version=settings.processing.pipeline_version,
        git_commit=os.getenv("GIT_COMMIT", "dev-local"),
        build_date=os.getenv("BUILD_DATE", "2026-07-22T00:00:00Z"),
        python_version=platform.python_version(),
        schema_version=settings.processing.schema_version,
        feature_version=settings.processing.feature_version,
        pipeline_version=settings.processing.pipeline_version,
    )
