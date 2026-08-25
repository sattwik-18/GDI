"""Domain layer custom exceptions integrated with ErrorCatalog entries."""

from typing import Any
from src.domain.error_catalog import (
    ErrorEntry,
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
    ERR_GENOME_VALIDATION_FAILED,
    ERR_GENOME_NOT_FOUND,
    ERR_STORAGE_WRITE_FAILED,
    ERR_STORAGE_READ_FAILED,
    ERR_DB_CONSTRAINT_VIOLATION,
    ERR_CONFIG_INVALID,
)


class GDIException(Exception):
    """Base domain exception for GDI platform."""

    def __init__(
        self,
        message: str,
        entry: ErrorEntry | None = None,
        code: str = "ERR_INTERNAL",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.entry = entry
        self.code = entry.code if entry else code
        self.details = details or {}
        if entry:
            self.details.setdefault("recommended_action", entry.recommended_action)
            self.details.setdefault("category", entry.category.value)


class ValidationError(GDIException):
    """Document or input validation failure."""

    def __init__(self, message: str, entry: ErrorEntry | None = None, details: dict[str, Any] | None = None):
        super().__init__(message, entry=entry or ERR_VALIDATION_FILE_EMPTY, details=details)


class SecurityError(GDIException):
    """Security check failure."""

    def __init__(self, message: str, entry: ErrorEntry | None = None, details: dict[str, Any] | None = None):
        super().__init__(message, entry=entry or ERR_VALIDATION_MAGIC_BYTES_MISMATCH, details=details)


class ResourceNotFoundError(GDIException):
    """Requested domain entity not found."""

    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with ID '{resource_id}' was not found."
        super().__init__(
            message,
            entry=ERR_GENOME_NOT_FOUND,
            details={"resource_type": resource_type, "resource_id": resource_id},
        )


class ProcessingError(GDIException):
    """Error during pipeline step execution."""

    def __init__(self, message: str, step_name: str | None = None, entry: ErrorEntry | None = None, details: dict[str, Any] | None = None):
        merged_details = details or {}
        if step_name:
            merged_details["step_name"] = step_name
        super().__init__(message, entry=entry or ERR_PROCESSING_STEP_FAILED, details=merged_details)


class OCRError(GDIException):
    """Error during OCR text detection/recognition."""

    def __init__(self, message: str, entry: ErrorEntry | None = None, details: dict[str, Any] | None = None):
        super().__init__(message, entry=entry or ERR_OCR_EXECUTION_FAILED, details=details)


class OCREngineUnavailableError(OCRError):
    """OCR engine is unavailable or uninitialized."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, entry=ERR_OCR_ENGINE_UNAVAILABLE, details=details)


class GenomeValidationError(GDIException):
    """Genome schema or integrity seal validation failure."""

    def __init__(self, message: str, entry: ErrorEntry | None = None, details: dict[str, Any] | None = None):
        super().__init__(message, entry=entry or ERR_GENOME_VALIDATION_FAILED, details=details)
