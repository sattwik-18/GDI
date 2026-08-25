"""API configuration settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class APISettings(BaseSettings):
    """FastAPI application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="GDI Genome Extraction Engine", validation_alias="APP_NAME")
    api_prefix: str = Field(default="/api/v1", validation_alias="API_PREFIX")
    environment: str = Field(default="development", validation_alias="ENVIRONMENT")
    debug: bool = Field(default=False, validation_alias="DEBUG")
    host: str = Field(default="0.0.0.0", validation_alias="HOST")
    port: int = Field(default=8000, validation_alias="PORT")
    cors_origins: list[str] = Field(default=["*"], validation_alias="CORS_ORIGINS")
