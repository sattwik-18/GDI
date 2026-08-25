"""Structured JSON logging configuration using structlog."""

import logging
import sys
from typing import Any
import structlog

from src.config.settings import get_settings


def configure_logging() -> None:
    """Configures global structlog logging system."""
    settings = get_settings()
    log_level = getattr(logging, settings.logging.log_level.upper(), logging.INFO)

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.logging.log_format == "text":
        renderer: structlog.types.Processor = structlog.dev.ConsoleRenderer()
    else:
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Gets a structured logger instance for the given module name."""
    return structlog.get_logger(name)  # type: ignore[no-any-return]


def bind_correlation_context(
    request_id: str | None = None,
    job_id: str | None = None,
    pipeline_stage: str | None = None,
    **kwargs: Any,
) -> None:
    """Binds correlation context parameters to structlog contextvars for downstream logging."""
    context: dict[str, Any] = {}
    if request_id:
        context["request_id"] = request_id
    if job_id:
        context["job_id"] = job_id
        context["correlation_id"] = job_id
    if pipeline_stage:
        context["pipeline_stage"] = pipeline_stage
    context.update(kwargs)
    structlog.contextvars.bind_contextvars(**context)


def clear_correlation_context() -> None:
    """Clears bound structlog contextvars."""
    structlog.contextvars.clear_contextvars()
