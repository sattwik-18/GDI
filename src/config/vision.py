"""Computer vision settings."""

from pydantic import Field
from pydantic_settings import BaseSettings


class VisionSettings(BaseSettings):
    """Computer vision parameters."""

    enable_deskew: bool = Field(default=True, validation_alias="VISION_ENABLE_DESKEW")
    enable_homography: bool = Field(default=True, validation_alias="VISION_ENABLE_HOMOGRAPHY")
    enable_color_normalization: bool = Field(default=True, validation_alias="VISION_ENABLE_COLOR_NORM")
    canny_lower_threshold: int = Field(default=50, validation_alias="CANNY_LOWER_THRESHOLD")
    canny_upper_threshold: int = Field(default=150, validation_alias="CANNY_UPPER_THRESHOLD")

    class Config:
        extra = "ignore"
