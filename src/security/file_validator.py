"""Security file validator verifying magic bytes, MIME types, extensions, and size limits."""

import io
from PIL import Image
import fitz  # PyMuPDF

from src.config.settings import get_settings
from src.domain.exceptions import SecurityError, ValidationError

settings = get_settings()

# Magic bytes signatures
MAGIC_BYTES_MAP = {
    "pdf": [b"%PDF"],
    "png": [b"\x89PNG\r\n\x1a\n"],
    "jpg": [b"\xff\xd8\xff"],
    "jpeg": [b"\xff\xd8\xff"],
    "tiff": [b"II*\x00", b"MM\x00*"],
    "tif": [b"II*\x00", b"MM\x00*"],
    "bmp": [b"BM"],
    "webp": [b"RIFF"],
}


class FileSecurityValidator:
    """Validates document safety, integrity, magic bytes, and dimensions."""

    def __init__(self) -> None:
        self._sec_config = settings.security

    def validate(self, content: bytes, filename: str, mime_type: str) -> str:
        """Validates uploaded file against security and formatting constraints. Returns canonical extension."""
        if not content:
            raise ValidationError("Uploaded file is empty (0 bytes).")

        size_bytes = len(content)
        if size_bytes > self._sec_config.max_file_size_bytes:
            raise SecurityError(
                f"File size ({size_bytes} bytes) exceeds maximum limit of {self._sec_config.max_file_size_bytes} bytes."
            )

        # Extension check
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        if ext not in self._sec_config.allowed_extensions:
            raise SecurityError(f"File extension '.{ext}' is not allowed.")

        # Magic bytes check
        self._verify_magic_bytes(content, ext)

        # Detailed structure check
        if ext == "pdf":
            self._validate_pdf_structure(content)
        else:
            self._validate_image_structure(content)

        return ext

    def _verify_magic_bytes(self, content: bytes, ext: str) -> None:
        valid_signatures = MAGIC_BYTES_MAP.get(ext, [])
        if not valid_signatures:
            raise SecurityError(f"Unsupported extension for magic byte check: {ext}")

        header = content[:16]
        matched = False
        for sig in valid_signatures:
            if ext == "webp":
                if header.startswith(b"RIFF") and b"WEBP" in header:
                    matched = True
                    break
            elif header.startswith(sig):
                matched = True
                break

        if not matched:
            raise SecurityError(f"Magic bytes check failed for declared file type .{ext}")

    def _validate_pdf_structure(self, content: bytes) -> None:
        try:
            doc = fitz.open(stream=content, filetype="pdf")
            if doc.is_encrypted:
                raise ValidationError("Encrypted or password-protected PDFs are not supported.")
            page_count = doc.page_count
            if page_count == 0:
                raise ValidationError("PDF has zero pages.")
            if page_count > self._sec_config.max_page_count:
                raise SecurityError(
                    f"PDF page count ({page_count}) exceeds max limit of {self._sec_config.max_page_count}."
                )
            doc.close()
        except fitz.FileDataError as e:
            raise ValidationError(f"Malformed or corrupted PDF file: {str(e)}") from e
        except Exception as e:
            if isinstance(e, (ValidationError, SecurityError)):
                raise
            raise ValidationError(f"Failed to parse PDF document structure: {str(e)}") from e

    def _validate_image_structure(self, content: bytes) -> None:
        try:
            img = Image.open(io.BytesIO(content))
            img.verify()  # Verify file integrity
            # Re-open for size check because verify() closes file pointers
            img2 = Image.open(io.BytesIO(content))
            width, height = img2.size
            if (
                width > self._sec_config.max_image_dimension_px
                or height > self._sec_config.max_image_dimension_px
            ):
                raise SecurityError(
                    f"Image dimensions ({width}x{height}) exceed maximum allowed dimension of {self._sec_config.max_image_dimension_px}px."
                )
        except Exception as e:
            if isinstance(e, SecurityError):
                raise
            raise ValidationError(f"Invalid or corrupted image file: {str(e)}") from e
