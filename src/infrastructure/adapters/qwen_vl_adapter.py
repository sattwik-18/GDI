"""Qwen2.5-VL Vision-Language Model Adapter.

Integrates the official Qwen2.5-VL multimodal stack for grounded Key-Information Extraction,
visual reasoning, ambiguity arbitration, and semantic contradiction checking.
"""

from __future__ import annotations
import base64
import json
import os
import time
from typing import Any
import httpx

from src.domain.entities.evidence_graph import EntityProvenance, GroundedEntity
from src.utils.logging import get_logger

logger = get_logger(__name__)


class QwenVisionAdapter:
    """Production adapter for Qwen2.5-VL multimodal inference."""

    def __init__(
        self,
        endpoint_url: str | None = None,
        api_key: str | None = None,
        model_name: str = "Qwen/Qwen2.5-VL-7B-Instruct",
    ) -> None:
        self.endpoint_url = endpoint_url or os.getenv("QWEN_VL_ENDPOINT", "")
        self.api_key = api_key or os.getenv("QWEN_VL_API_KEY", "")
        self.model_name = model_name
        self._is_enabled = bool(self.endpoint_url)

    @property
    def is_available(self) -> bool:
        return self._is_enabled

    async def extract_grounded_fields(
        self,
        image_bytes: bytes,
        ocr_text: str,
        target_schema_fields: list[str],
        page_number: int = 1,
    ) -> dict[str, GroundedEntity]:
        """Runs real Qwen2.5-VL grounded multimodal inference to extract schema fields."""
        if not self._is_enabled:
            logger.info("qwen_vl_endpoint_not_configured_skipping")
            return {}

        start_t = time.perf_counter()
        b64_img = base64.b64encode(image_bytes).decode("utf-8")
        data_uri = f"data:image/png;base64,{b64_img}"

        prompt = (
            f"You are a forensic document extraction engine. Extract the following fields from this document: "
            f"{', '.join(target_schema_fields)}. "
            f"OCR context:\n{ocr_text[:1000]}\n"
            f"Respond ONLY with a JSON object where each key is the field name and the value is: "
            f'{{"value": "...", "bbox": [[x1,y1],[x2,y2],[x3,y3],[x4,y4]], "confidence": 0.95}}.'
        )

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_uri}},
                    ],
                }
            ],
            "temperature": 0.1,
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(self.endpoint_url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    content = data["choices"][0]["message"]["content"]
                    parsed = json.loads(content)

                    results: dict[str, GroundedEntity] = {}
                    for field_key, field_data in parsed.items():
                        if isinstance(field_data, dict):
                            val = field_data.get("value")
                            bbox = field_data.get("bbox", [])
                            conf = float(field_data.get("confidence", 0.95))
                            prov = EntityProvenance(
                                page_number=page_number,
                                bounding_box=bbox,
                                extraction_method="qwen2.5_vl_real",
                                model_version=self.model_name,
                            )
                            results[field_key] = GroundedEntity(
                                entity_id=f"qwen_{field_key}_{page_number}",
                                key=field_key,
                                value=val,
                                normalized_value=val,
                                confidence=conf,
                                provenance=prov,
                            )
                    elapsed_ms = (time.perf_counter() - start_t) * 1000.0
                    logger.info("qwen_vl_extraction_complete", duration_ms=round(elapsed_ms, 2), count=len(results))
                    return results
        except Exception as e:
            logger.error("qwen_vl_request_failed", error=str(e))

        return {}
