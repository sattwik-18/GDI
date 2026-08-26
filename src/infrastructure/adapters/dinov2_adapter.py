"""Real DINOv2 Visual Embedding Adapter.

Loads and executes the Meta DINOv2 Vision Transformer (ViT-S/14) model for
deep visual layout and appearance representation.
"""

from __future__ import annotations
import time
from typing import Any
import cv2
import numpy as np
import torch

from src.domain.entities.visual_genome import VisualGenome
from src.utils.logging import get_logger

logger = get_logger(__name__)


class DINOv2Adapter:
    """Production adapter for real DINOv2 ViT embedding inference."""

    def __init__(self, model_name: str = "dinov2_vits14", device: str | None = None) -> None:
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self._model: Any = None
        self._is_loaded = False
        self.embedding_dimension = 384

    def _load_model(self) -> bool:
        """Loads real DINOv2 model weights from torch hub or local torch cache."""
        if self._is_loaded and self._model is not None:
            return True

        try:
            logger.info("loading_dinov2_model", model=self.model_name, device=self.device)
            # Load from PyTorch hub
            self._model = torch.hub.load("facebookresearch/dinov2", self.model_name, pretrained=True)
            self._model.to(self.device)
            self._model.eval()
            self._is_loaded = True
            logger.info("dinov2_loaded_successfully", model=self.model_name)
            return True
        except Exception as e:
            logger.warning("dinov2_hub_load_failed", error=str(e))
            self._is_loaded = False
            self._model = None
            return False

    def extract_embedding(self, image_bytes: bytes) -> VisualGenome:
        """Runs real DINOv2 model inference on a document image."""
        start_t = time.perf_counter()
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img_bgr is None:
            return self._create_empty_genome()

        p_hash = self._compute_dhash(img_bgr)
        color_palette = self._compute_color_palette(img_bgr)

        # 1. Try real DINOv2 ViT forward pass
        if self._load_model() and self._model is not None:
            try:
                # Preprocess: BGR -> RGB -> resize to 224x224 -> normalize ImageNet stats
                img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                resized = cv2.resize(img_rgb, (224, 224), interpolation=cv2.INTER_CUBIC)
                tensor = torch.from_numpy(resized).permute(2, 0, 1).float() / 255.0

                mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
                std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
                tensor = (tensor - mean) / std
                batch = tensor.unsqueeze(0).to(self.device)

                with torch.no_grad():
                    embedding_tensor = self._model(batch)
                    # L2 normalize embedding
                    norm = torch.norm(embedding_tensor, p=2, dim=1, keepdim=True)
                    embedding_tensor = embedding_tensor / (norm + 1e-6)
                    embedding_list = embedding_tensor.squeeze(0).cpu().numpy().tolist()

                elapsed_ms = (time.perf_counter() - start_t) * 1000.0
                logger.info("dinov2_inference_complete", duration_ms=round(elapsed_ms, 2), dim=len(embedding_list))

                return VisualGenome(
                    visual_embedding=[round(float(v), 6) for v in embedding_list],
                    embedding_dimension=len(embedding_list),
                    embedding_model=f"facebookresearch/{self.model_name}_real",
                    perceptual_hash=p_hash,
                    color_palette=color_palette,
                    visual_signature_version="2.0.0",
                )
            except Exception as e:
                logger.error("dinov2_forward_pass_failed", error=str(e))

        # 2. Explicitly labeled GDI Custom Spatial-Spectral Fallback
        return self._fallback_custom_fingerprint(img_bgr, p_hash, color_palette)

    def _fallback_custom_fingerprint(
        self, img_bgr: np.ndarray, p_hash: str, color_palette: list[dict]
    ) -> VisualGenome:
        """GDI Custom Spatial-Spectral Fingerprint (Explicitly labeled fallback)."""
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        grid = cv2.resize(gray, (128, 128), interpolation=cv2.INTER_AREA).astype(np.float64) / 255.0

        # Spatial grid pooling
        h, w = grid.shape
        gh, gw = h // 8, w // 8
        spatial_pooled = []
        for i in range(8):
            for j in range(8):
                cell = grid[i * gh : (i + 1) * gh, j * gw : (j + 1) * gw]
                spatial_pooled.extend([float(np.mean(cell)), float(np.std(cell))])

        dct = cv2.dct(grid)
        dct_coeffs = dct[:16, :16].flatten()

        combined = np.concatenate([spatial_pooled, dct_coeffs])[: self.embedding_dimension]
        norm = np.linalg.norm(combined)
        if norm > 1e-6:
            combined = combined / norm

        return VisualGenome(
            visual_embedding=[round(float(v), 6) for v in combined],
            embedding_dimension=len(combined),
            embedding_model="gdi_custom_spatial_spectral_fallback",
            perceptual_hash=p_hash,
            color_palette=color_palette,
            visual_signature_version="1.0.0",
        )

    def _compute_dhash(self, img_bgr: np.ndarray) -> str:
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (9, 8), interpolation=cv2.INTER_AREA)
        diff = resized[:, 1:] > resized[:, :-1]
        decimal_val = 0
        hex_str = []
        for idx, val in enumerate(diff.flatten()):
            if val:
                decimal_val += 1 << (idx % 8)
            if (idx % 8) == 7:
                hex_str.append(f"{decimal_val:02x}")
                decimal_val = 0
        return "".join(hex_str)

    def _compute_color_palette(self, img_bgr: np.ndarray) -> list[dict]:
        small = cv2.resize(img_bgr, (64, 64), interpolation=cv2.INTER_AREA)
        pixels = small.reshape(-1, 3)
        mean_bgr = np.mean(pixels, axis=0)
        return [{"bgr": [int(mean_bgr[0]), int(mean_bgr[1]), int(mean_bgr[2])], "percentage": 100.0}]

    def _create_empty_genome(self) -> VisualGenome:
        return VisualGenome(
            visual_embedding=[0.0] * self.embedding_dimension,
            embedding_dimension=self.embedding_dimension,
            embedding_model="empty",
            perceptual_hash="0" * 32,
        )
