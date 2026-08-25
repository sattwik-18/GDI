"""Security tests for file upload endpoints."""

import io
import pytest
from httpx import AsyncClient
from PIL import Image


async def make_png_bytes(w: int = 100, h: int = 100) -> bytes:
    img = Image.new("RGB", (w, h))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class TestFileSecurityEndpoint:

    @pytest.mark.asyncio
    async def test_empty_file_returns_422(self, async_client: AsyncClient) -> None:
        response = await async_client.post(
            "/api/v1/genome",
            files={"file": ("empty.png", b"", "image/png")},
        )
        assert response.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_exe_extension_rejected(self, async_client: AsyncClient) -> None:
        response = await async_client.post(
            "/api/v1/genome",
            files={"file": ("malware.exe", b"\x4d\x5a\x90\x00", "application/octet-stream")},
        )
        assert response.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_magic_byte_mismatch_rejected(self, async_client: AsyncClient) -> None:
        # JPEG magic bytes declared as PNG
        fake_bytes = b"\xff\xd8\xff\xe0" + b"\x00" * 200
        response = await async_client.post(
            "/api/v1/genome",
            files={"file": ("fake.png", fake_bytes, "image/png")},
        )
        assert response.status_code in (400, 422)
