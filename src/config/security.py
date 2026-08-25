"""Security configuration settings."""

from pydantic import Field
from pydantic_settings import BaseSettings


class SecuritySettings(BaseSettings):
    """Security validation limits and parameters."""

    max_file_size_bytes: int = Field(default=104_857_600, validation_alias="MAX_FILE_SIZE_BYTES")  # 100 MB
    max_page_count: int = Field(default=500, validation_alias="MAX_PAGE_COUNT")
    max_image_dimension_px: int = Field(default=15_000, validation_alias="MAX_IMAGE_DIMENSION_PX")
    allowed_extensions: set[str] = Field(
        default={"pdf", "png", "jpg", "jpeg", "tiff", "tif", "bmp", "webp"}
    )
    allowed_mime_types: set[str] = Field(
        default={
            "application/pdf",
            "image/png",
            "image/jpeg",
            "image/tiff",
            "image/bmp",
            "image/webp",
        }
    )

    class Config:
        extra = "ignore"
