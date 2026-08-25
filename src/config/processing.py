"""Processing pipeline configuration settings."""

from pydantic import Field
from pydantic_settings import BaseSettings


class ProcessingSettings(BaseSettings):
    """Processing pipeline configuration."""

    rendering_dpi: int = Field(default=300, validation_alias="RENDERING_DPI")
    analysis_tier: str = Field(default="STANDARD", validation_alias="ANALYSIS_TIER")
    pipeline_version: str = Field(default="1.0.0", validation_alias="PIPELINE_VERSION")
    schema_version: str = Field(default="1.0.0", validation_alias="SCHEMA_VERSION")
    feature_version: str = Field(default="1.0.0", validation_alias="FEATURE_VERSION")
    processing_version: str = Field(default="1.0.0", validation_alias="PROCESSING_VERSION")
    storage_root: str = Field(default="./gdi_storage", validation_alias="STORAGE_ROOT")
    temp_dir: str = Field(default="./gdi_storage/temp", validation_alias="TEMP_DIR")
    step_timeout_seconds: float = Field(default=60.0, validation_alias="STEP_TIMEOUT_SECONDS")
    debug_pipeline: bool = Field(default=False, validation_alias="DEBUG_PIPELINE")

    class Config:
        extra = "ignore"
