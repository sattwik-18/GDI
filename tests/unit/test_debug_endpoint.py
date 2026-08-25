"""Unit tests for developer pipeline inspection debug endpoint."""

import pytest
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.config.settings import get_settings


@pytest.mark.asyncio
async def test_debug_endpoint_security_restriction():
    settings = get_settings()
    settings.processing.debug_pipeline = False

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with open("tests/golden/sample_certificate.png", "rb") as f:
            img_bytes = f.read()

        res = await client.post("/api/v1/genome/debug", files={"file": ("doc.png", img_bytes, "image/png")})
        assert res.status_code == 403
        assert "Pipeline debug inspection is disabled" in res.json()["detail"]


@pytest.mark.asyncio
async def test_debug_endpoint_successful_inspection():
    settings = get_settings()
    settings.processing.debug_pipeline = True

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with open("tests/golden/sample_certificate.png", "rb") as f:
            img_bytes = f.read()

        res = await client.post("/api/v1/genome/debug", files={"file": ("doc.png", img_bytes, "image/png")})
        assert res.status_code == 200
        data = res.json()

        assert "request_id" in data
        assert "job_id" in data
        assert "rendered_pages" in data
        assert "normalized_pages" in data
        assert "ocr_results" in data
        assert "feature_groups" in data
        assert "processing_manifest" in data
