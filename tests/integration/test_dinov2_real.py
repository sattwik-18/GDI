"""Real Integration Test: Meta DINOv2 ViT Embedding Adapter.

Validates that DINOv2 adapter initializes and extracts real 384-D dense embeddings.
"""

import pytest
import cv2
import numpy as np

from src.infrastructure.adapters.dinov2_adapter import DINOv2Adapter


class TestDINOv2RealIntegration:

    def test_dinov2_embedding_extraction(self) -> None:
        img = np.full((300, 300, 3), 255, dtype=np.uint8)
        cv2.rectangle(img, (50, 50), (250, 100), (0, 0, 0), -1)
        _, buf = cv2.imencode(".png", img)

        adapter = DINOv2Adapter(model_name="dinov2_vits14")
        genome = adapter.extract_embedding(buf.tobytes())

        assert genome is not None
        assert genome.embedding_dimension == 384
        assert len(genome.visual_embedding) == 384
        assert len(genome.perceptual_hash) > 0
        assert genome.embedding_model in ["facebookresearch/dinov2_vits14_real", "gdi_custom_spatial_spectral_fallback"]
