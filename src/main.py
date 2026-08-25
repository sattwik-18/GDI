"""GDI Genome Extraction Engine — FastAPI application entry point."""

import os
os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.api.middleware.error_handler import gdi_exception_handler, generic_exception_handler
from src.api.v1.router import api_v1_router
from src.config.settings import get_settings
from src.domain.exceptions import GDIException
from src.utils.logging import configure_logging, get_logger

settings = get_settings()
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler — startup and shutdown."""
    logger.info(
        "gdi_genome_engine_starting",
        pipeline_version=settings.processing.pipeline_version,
        environment=settings.api.environment,
    )
    yield
    logger.info("gdi_genome_engine_shutting_down")


app = FastAPI(
    title=settings.api.app_name,
    description=(
        "GDI Prototype 1 — Genome Extraction Engine\n\n"
        "Deterministic document ingestion and genome generation for the GDI Platform. "
        "Supports PDF, PNG, JPEG, TIFF, BMP, and WebP formats."
    ),
    version=settings.processing.pipeline_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(GDIException, gdi_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, generic_exception_handler)  # type: ignore[arg-type]

# Routes
app.include_router(api_v1_router, prefix=settings.api.api_prefix)
