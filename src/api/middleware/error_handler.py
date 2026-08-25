"""Centralized exception handler middleware for FastAPI."""

from datetime import datetime, timezone

from fastapi import Request, status
from fastapi.responses import JSONResponse
import uuid

from src.domain.exceptions import (
    GDIException,
    GenomeValidationError,
    ProcessingError,
    ResourceNotFoundError,
    SecurityError,
    ValidationError,
)


async def gdi_exception_handler(request: Request, exc: GDIException) -> JSONResponse:
    """Maps GDI domain exceptions to structured HTTP error responses."""
    status_code_map: dict[type, int] = {
        ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
        SecurityError: status.HTTP_400_BAD_REQUEST,
        ResourceNotFoundError: status.HTTP_404_NOT_FOUND,
        GenomeValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
        ProcessingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    http_status = status_code_map.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)

    return JSONResponse(
        status_code=http_status,
        content={
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status_code": http_status,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catches unexpected errors; never exposes stack traces to clients."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status_code": 500,
            "error": {
                "code": "ERR_INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again.",
                "details": {},
            },
        },
    )
