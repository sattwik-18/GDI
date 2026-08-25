"""Unit tests for FileSecurityValidator."""

import io
import pytest
from PIL import Image

from src.domain.exceptions import SecurityError, ValidationError
from src.security.file_validator import FileSecurityValidator


@pytest.fixture
def validator() -> FileSecurityValidator:
    return FileSecurityValidator()


def make_png_bytes(width: int = 100, height: int = 100) -> bytes:
    img = Image.new("RGB", (width, height), color=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class TestFileSecurityValidator:

    def test_valid_png_accepted(self, validator: FileSecurityValidator) -> None:
        content = make_png_bytes()
        ext = validator.validate(content, "test.png", "image/png")
        assert ext == "png"

    def test_empty_file_raises_validation_error(self, validator: FileSecurityValidator) -> None:
        with pytest.raises(ValidationError, match="empty"):
            validator.validate(b"", "test.png", "image/png")

    def test_invalid_extension_raises_security_error(self, validator: FileSecurityValidator) -> None:
        content = make_png_bytes()
        with pytest.raises(SecurityError, match="extension"):
            validator.validate(content, "test.exe", "application/octet-stream")

    def test_wrong_magic_bytes_raises_security_error(self, validator: FileSecurityValidator) -> None:
        fake_content = b"\xff\xd8\xff" + b"\x00" * 100  # JPEG magic bytes but declared PNG
        with pytest.raises(SecurityError, match="Magic bytes"):
            validator.validate(fake_content, "test.png", "image/png")

    def test_oversized_file_raises_security_error(self, validator: FileSecurityValidator, monkeypatch) -> None:
        import src.security.file_validator as fv_module
        monkeypatch.setattr(fv_module.settings.security, "max_file_size_bytes", 10)
        content = make_png_bytes()
        with pytest.raises(SecurityError, match="size"):
            validator.validate(content, "test.png", "image/png")
