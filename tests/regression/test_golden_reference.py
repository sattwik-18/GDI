"""Golden Reference Regression Tests.

Validates that Document Genome extraction produces deterministic canonical outputs matching
established Golden Reference datasets in `tests/golden/`.
Ignores dynamic run fields (UUIDs, timestamps, processing durations).
"""

import json
import os
import pytest
from httpx import AsyncClient, ASGITransport

from src.main import app

GOLDEN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tests", "golden")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sample_name",
    [
        "sample_certificate",
        "sample_invoice",
        "sample_degree",
    ],
)
async def test_golden_reference_match(sample_name: str):
    png_path = os.path.join(GOLDEN_DIR, f"{sample_name}.png")
    json_path = os.path.join(GOLDEN_DIR, f"{sample_name}.json")

    assert os.path.exists(png_path), f"Golden reference image missing: {png_path}"
    assert os.path.exists(json_path), f"Golden reference json missing: {json_path}"

    with open(json_path, "r", encoding="utf-8") as f:
        expected_genome = json.load(f)

    with open(png_path, "rb") as f:
        img_bytes = f.read()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post(
            "/api/v1/genome",
            files={"file": (f"{sample_name}.png", img_bytes, "image/png")},
        )
        assert res.status_code == 200, f"Extraction failed: {res.text}"
        actual_genome = res.json()

    # Compare static deterministic content
    assert actual_genome["schema_version"] == expected_genome["schema_version"]
    assert actual_genome["pipeline_version"] == expected_genome["pipeline_version"]
    assert actual_genome["feature_version"] == expected_genome["feature_version"]
    assert len(actual_genome["feature_vector"]) == len(expected_genome["feature_vector"])
    assert actual_genome["feature_vector"] == expected_genome["feature_vector"]
    assert actual_genome["genome_seal"]["sha256_of_features"] == expected_genome["genome_seal"]["sha256_of_features"]
    assert actual_genome["processing_manifest"]["step_count"] == expected_genome["processing_manifest"]["step_count"]
