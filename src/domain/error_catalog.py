"""Centralized error catalog for all GDI domain errors.

Every error has: code, category, http_status, description, recommended_action.
This catalog is the single source of truth for all structured error reporting.
"""

from enum import Enum
from dataclasses import dataclass


class ErrorCategory(str, Enum):
    """High-level error category groupings."""

    VALIDATION = "VALIDATION"
    SECURITY = "SECURITY"
    PROCESSING = "PROCESSING"
    OCR = "OCR"
    GENOME = "GENOME"
    STORAGE = "STORAGE"
    DATABASE = "DATABASE"
    CONFIGURATION = "CONFIGURATION"
    INFRASTRUCTURE = "INFRASTRUCTURE"


@dataclass(frozen=True)
class ErrorEntry:
    """Structured catalog entry for a single error code."""

    code: str
    category: ErrorCategory
    http_status: int
    description: str
    recommended_action: str


# ─── Validation Errors (ERR_VAL_*) ────────────────────────────────────────────
ERR_VALIDATION_FILE_EMPTY = ErrorEntry(
    code="ERR_VAL_FILE_EMPTY",
    category=ErrorCategory.VALIDATION,
    http_status=422,
    description="Uploaded file is empty (0 bytes).",
    recommended_action="Verify the file was correctly attached before submitting.",
)

ERR_VALIDATION_EXTENSION_DENIED = ErrorEntry(
    code="ERR_VAL_EXTENSION_DENIED",
    category=ErrorCategory.VALIDATION,
    http_status=400,
    description="File extension is not in the permitted list.",
    recommended_action="Upload one of: PDF, PNG, JPEG, TIFF, BMP, WebP.",
)

ERR_VALIDATION_MAGIC_BYTES_MISMATCH = ErrorEntry(
    code="ERR_VAL_MAGIC_BYTES_MISMATCH",
    category=ErrorCategory.SECURITY,
    http_status=400,
    description="File magic bytes do not match the declared file type.",
    recommended_action="Ensure the file is not renamed or corrupted.",
)

ERR_VALIDATION_SIZE_EXCEEDED = ErrorEntry(
    code="ERR_VAL_SIZE_EXCEEDED",
    category=ErrorCategory.SECURITY,
    http_status=413,
    description="Uploaded file exceeds the configured maximum file size.",
    recommended_action="Compress the document or split it into smaller files.",
)

ERR_VALIDATION_PAGE_LIMIT_EXCEEDED = ErrorEntry(
    code="ERR_VAL_PAGE_LIMIT_EXCEEDED",
    category=ErrorCategory.VALIDATION,
    http_status=422,
    description="Document page count exceeds the configured maximum.",
    recommended_action="Split the document and submit pages in smaller batches.",
)

ERR_VALIDATION_DIMENSION_EXCEEDED = ErrorEntry(
    code="ERR_VAL_DIMENSION_EXCEEDED",
    category=ErrorCategory.VALIDATION,
    http_status=422,
    description="Image dimensions exceed the configured maximum pixel dimensions.",
    recommended_action="Downscale the image before uploading.",
)

ERR_VALIDATION_PDF_ENCRYPTED = ErrorEntry(
    code="ERR_VAL_PDF_ENCRYPTED",
    category=ErrorCategory.VALIDATION,
    http_status=422,
    description="PDF is encrypted or password-protected.",
    recommended_action="Remove the password protection before uploading.",
)

ERR_VALIDATION_PDF_MALFORMED = ErrorEntry(
    code="ERR_VAL_PDF_MALFORMED",
    category=ErrorCategory.VALIDATION,
    http_status=422,
    description="PDF file is malformed or corrupted and cannot be parsed.",
    recommended_action="Re-export or regenerate the PDF from the source document.",
)

# ─── OCR Errors (ERR_OCR_*) ───────────────────────────────────────────────────
ERR_OCR_ENGINE_UNAVAILABLE = ErrorEntry(
    code="ERR_OCR_ENGINE_UNAVAILABLE",
    category=ErrorCategory.OCR,
    http_status=503,
    description=(
        "The configured OCR engine is not available or failed to initialize. "
        "For PaddleOCR: ensure paddlepaddle and paddleocr are installed. "
        "For Tesseract: ensure the tesseract binary is on PATH."
    ),
    recommended_action=(
        "Install the required OCR engine, or set DEV_OCR_FALLBACK=true to "
        "use Tesseract in development mode (genome determinism not guaranteed)."
    ),
)

ERR_OCR_EXECUTION_FAILED = ErrorEntry(
    code="ERR_OCR_EXECUTION_FAILED",
    category=ErrorCategory.OCR,
    http_status=500,
    description="OCR engine raised an error during text extraction.",
    recommended_action="Check OCR engine logs and verify the image is readable.",
)

# ─── Processing Errors (ERR_PROC_*) ───────────────────────────────────────────
ERR_PROCESSING_STEP_FAILED = ErrorEntry(
    code="ERR_PROC_STEP_FAILED",
    category=ErrorCategory.PROCESSING,
    http_status=500,
    description="A pipeline processing step raised an unrecoverable error.",
    recommended_action="Check server logs for the specific step_name and exception.",
)

ERR_PROCESSING_GENOME_ASSEMBLY_FAILED = ErrorEntry(
    code="ERR_PROC_GENOME_ASSEMBLY_FAILED",
    category=ErrorCategory.PROCESSING,
    http_status=500,
    description="Genome assembly could not complete due to missing or invalid context data.",
    recommended_action="Ensure all upstream pipeline steps completed successfully.",
)

# ─── Genome Errors (ERR_GENOME_*) ─────────────────────────────────────────────
ERR_GENOME_VALIDATION_FAILED = ErrorEntry(
    code="ERR_GENOME_VALIDATION_FAILED",
    category=ErrorCategory.GENOME,
    http_status=422,
    description="Assembled genome failed Pydantic schema validation.",
    recommended_action="Check feature extractor outputs and genome assembler logic.",
)

ERR_GENOME_NOT_FOUND = ErrorEntry(
    code="ERR_GENOME_NOT_FOUND",
    category=ErrorCategory.GENOME,
    http_status=404,
    description="No genome was found for the given genome_id.",
    recommended_action="Verify the genome_id and ensure the document was successfully processed.",
)

# ─── Storage Errors (ERR_STORE_*) ─────────────────────────────────────────────
ERR_STORAGE_WRITE_FAILED = ErrorEntry(
    code="ERR_STORE_WRITE_FAILED",
    category=ErrorCategory.STORAGE,
    http_status=500,
    description="File system write operation failed.",
    recommended_action="Verify the storage directory exists and has write permissions.",
)

ERR_STORAGE_READ_FAILED = ErrorEntry(
    code="ERR_STORE_READ_FAILED",
    category=ErrorCategory.STORAGE,
    http_status=500,
    description="File system read operation failed.",
    recommended_action="Verify the file exists at the expected path.",
)

# ─── Database Errors (ERR_DB_*) ───────────────────────────────────────────────
ERR_DB_CONSTRAINT_VIOLATION = ErrorEntry(
    code="ERR_DB_CONSTRAINT_VIOLATION",
    category=ErrorCategory.DATABASE,
    http_status=409,
    description="Database operation violated a uniqueness or foreign key constraint.",
    recommended_action="Check for duplicate submission of the same document.",
)

# ─── Configuration Errors (ERR_CFG_*) ─────────────────────────────────────────
ERR_CONFIG_INVALID = ErrorEntry(
    code="ERR_CFG_INVALID",
    category=ErrorCategory.CONFIGURATION,
    http_status=500,
    description="Service configuration is invalid or missing required values.",
    recommended_action="Review .env file against .env.example and correct missing fields.",
)


# ─── Lookup Utility ───────────────────────────────────────────────────────────
_ALL_ENTRIES: dict[str, ErrorEntry] = {
    entry.code: entry
    for entry in [
        ERR_VALIDATION_FILE_EMPTY,
        ERR_VALIDATION_EXTENSION_DENIED,
        ERR_VALIDATION_MAGIC_BYTES_MISMATCH,
        ERR_VALIDATION_SIZE_EXCEEDED,
        ERR_VALIDATION_PAGE_LIMIT_EXCEEDED,
        ERR_VALIDATION_DIMENSION_EXCEEDED,
        ERR_VALIDATION_PDF_ENCRYPTED,
        ERR_VALIDATION_PDF_MALFORMED,
        ERR_OCR_ENGINE_UNAVAILABLE,
        ERR_OCR_EXECUTION_FAILED,
        ERR_PROCESSING_STEP_FAILED,
        ERR_PROCESSING_GENOME_ASSEMBLY_FAILED,
        ERR_GENOME_VALIDATION_FAILED,
        ERR_GENOME_NOT_FOUND,
        ERR_STORAGE_WRITE_FAILED,
        ERR_STORAGE_READ_FAILED,
        ERR_DB_CONSTRAINT_VIOLATION,
        ERR_CONFIG_INVALID,
    ]
}


def get_error_entry(code: str) -> ErrorEntry | None:
    """Look up an ErrorEntry by its error code string."""
    return _ALL_ENTRIES.get(code)


def all_error_codes() -> list[str]:
    """Returns all registered error codes."""
    return sorted(_ALL_ENTRIES.keys())
