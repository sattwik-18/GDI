"""Master settings configuration aggregating modular configs."""

from functools import lru_cache
from pydantic_settings import BaseSettings

from src.config.api import APISettings
from src.config.database import DatabaseSettings
from src.config.logging import LoggingSettings
from src.config.ocr import OCRSettings
from src.config.processing import ProcessingSettings
from src.config.security import SecuritySettings
from src.config.vision import VisionSettings


class Settings(BaseSettings):
    """Global configuration settings for GDI Genome Engine."""

    api: APISettings = APISettings()
    database: DatabaseSettings = DatabaseSettings()
    processing: ProcessingSettings = ProcessingSettings()
    ocr: OCRSettings = OCRSettings()
    vision: VisionSettings = VisionSettings()
    security: SecuritySettings = SecuritySettings()
    logging: LoggingSettings = LoggingSettings()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Returns cached singleton Settings instance."""
    return Settings()
