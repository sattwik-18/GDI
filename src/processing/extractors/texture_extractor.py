"""Texture Feature Extractor (LBP, GLCM, Haralick, Local Variance)."""

import time
import cv2
import numpy as np
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern

from src.application.context.processing_context import ProcessingContext
from src.domain.entities.feature_group import FeatureGroup
from src.domain.interfaces.feature_extractor import FeatureExtractor


class TextureExtractor(FeatureExtractor):
    """Extracts texture descriptors (LBP, GLCM contrast/energy/homogeneity, local variance)."""

    @property
    def name(self) -> str:
        return "TextureExtractor"

    @property
    def version(self) -> str:
        return "1.0.0"

    def extract(self, context: ProcessingContext) -> FeatureGroup:
        start_t = time.perf_counter()
        features: dict[str, float] = {}

        for n_page in context.normalized_pages:
            prefix = f"p{n_page.page_number}_tex_"
            nparr = np.frombuffer(n_page.image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                continue

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Downsample large images for fast deterministic texture computation
            h, w = gray.shape
            if h > 1024 or w > 1024:
                scale = 1024.0 / max(h, w)
                gray = cv2.resize(gray, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

            # 1. Local Binary Patterns (LBP)
            lbp = local_binary_pattern(gray, P=8, R=1, method="uniform")
            lbp_hist, _ = np.histogram(lbp.ravel(), bins=10, range=(0, 10), density=True)
            for b_idx, val in enumerate(lbp_hist):
                features[f"{prefix}lbp_bin_{b_idx}"] = round(float(val), 6)

            # 2. GLCM (Gray-Level Co-occurrence Matrix)
            # Quantize to 16 levels for speed
            gray_q = (gray // 16).astype(np.uint8)
            glcm = graycomatrix(gray_q, distances=[1, 3], angles=[0, np.pi / 4], levels=16, symmetric=True, normed=True)

            features[f"{prefix}glcm_contrast"] = round(float(graycoprops(glcm, "contrast").mean()), 4)
            features[f"{prefix}glcm_dissimilarity"] = round(float(graycoprops(glcm, "dissimilarity").mean()), 4)
            features[f"{prefix}glcm_homogeneity"] = round(float(graycoprops(glcm, "homogeneity").mean()), 4)
            features[f"{prefix}glcm_energy"] = round(float(graycoprops(glcm, "energy").mean()), 4)
            features[f"{prefix}glcm_correlation"] = round(float(graycoprops(glcm, "correlation").mean()), 4)
            features[f"{prefix}glcm_ASM"] = round(float(graycoprops(glcm, "ASM").mean()), 4)

            # 3. Local Variance & Entropy
            local_var = float(np.var(gray))
            features[f"{prefix}local_variance"] = round(local_var, 4)

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        return FeatureGroup.create(
            name=self.name,
            version=self.version,
            extraction_time_ms=round(elapsed_ms, 2),
            features=features,
        )
