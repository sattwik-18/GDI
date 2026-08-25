"""OCR configuration settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OCRSettings(BaseSettings):
    """OCR engine settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    use_gpu: bool = Field(default=False, validation_alias="OCR_USE_GPU")
    lang: str = Field(default="en", validation_alias="OCR_LANG")
    confidence_threshold: float = Field(default=0.5, validation_alias="OCR_CONFIDENCE_THRESHOLD")
    engine_provider: str = Field(default="paddleocr", validation_alias="OCR_ENGINE_PROVIDER")  # paddleocr or pytesseract
    tesseract_cmd: str | None = Field(default=None, validation_alias="TESSERACT_CMD")
    dev_ocr_fallback: bool = Field(default=False, validation_alias="DEV_OCR_FALLBACK")
