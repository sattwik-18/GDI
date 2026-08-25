"""Pytest fixtures shared across the test suite."""

import io
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport

from src.main import app


@pytest.fixture
def sample_png_bytes() -> bytes:
    """Generates a small valid PNG image for testing."""
    from PIL import Image
    img = Image.new("RGB", (100, 100), color=(128, 64, 32))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """Generates a minimal single-page PDF for testing."""
    import fitz
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((72, 72), "GDI Test Document — Prototype 1")
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
