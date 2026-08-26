"""Qwen2.5-VL Multimodal Vision Adapter Verification.

Classification: [ADAPTER_CONTRACT / REAL_EXTERNAL_SERVICE]
Validates the Qwen2.5-VL interface contract and executes real remote inference when
a supported endpoint is configured via QWEN_VL_ENDPOINT.
"""

import os
import pytest
from src.infrastructure.adapters.qwen_vl_adapter import QwenVisionAdapter


class TestQwenVLRealContract:
    """[ADAPTER_CONTRACT / REAL_EXTERNAL_SERVICE] Qwen2.5-VL Integration Suite."""

    def test_qwen_adapter_interface_contract(self) -> None:
        """[ADAPTER_CONTRACT] Verifies initialization, default model ID, and availability probing."""
        adapter = QwenVisionAdapter()
        assert adapter.model_name == "Qwen/Qwen2.5-VL-7B-Instruct"
        # When unconfigured, reports available=False cleanly
        if not os.getenv("QWEN_VL_ENDPOINT"):
            assert adapter.is_available is False

    @pytest.mark.asyncio
    async def test_qwen_real_inference_execution_when_configured(self) -> None:
        """[REAL_EXTERNAL_SERVICE] Executes real Qwen2.5-VL inference if endpoint is configured."""
        endpoint = os.getenv("QWEN_VL_ENDPOINT")
        if not endpoint:
            pytest.skip("QWEN_VL_ENDPOINT not configured in environment: REAL_ADAPTER_IMPLEMENTED_BUT_ENVIRONMENT_NOT_CAPABLE_OF_INFERENCE")

        adapter = QwenVisionAdapter(endpoint_url=endpoint)
        results = await adapter.extract_grounded_fields(
            image_bytes=b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82",
            ocr_text="INVOICE #: 9812 Total: $400.00",
            target_schema_fields=["invoice_number", "total_amount"],
            page_number=1,
        )
        assert isinstance(results, dict)
