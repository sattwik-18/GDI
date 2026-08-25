#!/usr/bin/env python3
"""GDI Genome Extraction Engine — CI Smoke Test Script.

Validates end-to-end processing pipeline execution:
1. Health check probe.
2. File upload & Genome generation.
3. Canonical Document Genome schema & seal validation.
4. Returns exit code 0 on success, non-zero on failure.
"""

import asyncio
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.config.settings import get_settings


async def run_smoke_test() -> int:
    """Executes end-to-end smoke test against FastAPI ASGI application."""
    print("==================================================")
    print("--- GDI ENGINE CI SMOKE TEST STARTING ---")
    print("==================================================")
    
    settings = get_settings()
    settings.ocr.dev_ocr_fallback = False

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Health check probe
        print("[1/3] Probing GET /api/v1/health...")
        res_health = await client.get("/api/v1/health")
        if res_health.status_code != 200:
            print(f"[FAIL] Health check failed with status code {res_health.status_code}: {res_health.text}")
            return 1
        print(f"[OK] Health check PASSED (status={res_health.status_code})")

        # 2. Prepare test document image
        print("[2/3] Preparing test document image...")
        img = Image.new("RGB", (600, 800), color=(255, 255, 255))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        file_bytes = buf.getvalue()

        # 3. Post to /api/v1/genome
        print("[3/3] Uploading document to POST /api/v1/genome...")
        res_genome = await client.post(
            "/api/v1/genome",
            files={"file": ("smoke_test_doc.png", file_bytes, "image/png")},
        )

        if res_genome.status_code != 200:
            print(f"[FAIL] Genome generation failed (status={res_genome.status_code}): {res_genome.text}")
            return 1

        data = res_genome.json()

        # 4. Assertions
        assert "genome_id" in data and data["genome_id"], "Missing genome_id"
        assert "document_hash_sha256" in data, "Missing document_hash_sha256"
        assert len(data.get("feature_vector", [])) > 0, "Feature vector is empty"
        assert "genome_seal" in data, "Missing genome_seal"
        assert data["genome_seal"].get("sha256_of_features"), "Missing seal hash"
        assert "processing_manifest" in data, "Missing processing_manifest"
        assert data["processing_manifest"].get("step_count", 0) > 0, "Manifest step count is 0"

        print("==================================================")
        print("[OK] E2E SMOKE TEST PASSED SUCCESSFULLY!")
        print(f"   Genome ID           : {data.get('genome_id')}")
        print(f"   Feature Vector Len  : {len(data.get('feature_vector', []))}")
        print(f"   Seal Hash           : {data.get('genome_seal', {}).get('sha256_of_features')}")
        print(f"   Manifest Step Count : {data.get('processing_manifest', {}).get('step_count')}")
        print("==================================================")
        return 0


def main():
    try:
        exit_code = asyncio.run(run_smoke_test())
        sys.exit(exit_code)
    except Exception as e:
        print(f"[ERROR] Unhandled Exception in Smoke Test: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
