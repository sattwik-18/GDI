"""Edge Feature Extractor (Canny, Sobel, Gradient statistics)."""

import time
import cv2
import numpy as np

from src.application.context.processing_context import ProcessingContext
from src.domain.entities.feature_group import FeatureGroup
from src.domain.interfaces.feature_extractor import FeatureExtractor
from src.config.settings import get_settings

settings = get_settings()


class EdgeExtractor(FeatureExtractor):
    """Extracts edge-based features: Canny edge density, Sobel magnitude stats, gradient distributions."""

    @property
    def name(self) -> str:
        return "EdgeExtractor"

    @property
    def version(self) -> str:
        return "1.0.0"

    def extract(self, context: ProcessingContext) -> FeatureGroup:
        start_t = time.perf_counter()
        features: dict[str, float] = {}
        v_cfg = settings.vision

        for n_page in context.normalized_pages:
            prefix = f"p{n_page.page_number}_edge_"
            nparr = np.frombuffer(n_page.image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

            if img is None:
                continue

            # 1. Canny edge detection
            edges = cv2.Canny(
                img,
                v_cfg.canny_lower_threshold,
                v_cfg.canny_upper_threshold,
            )
            total_px = edges.shape[0] * edges.shape[1]
            edge_px = int(np.count_nonzero(edges))
            features[f"{prefix}canny_edge_density"] = round(edge_px / total_px, 6)
            features[f"{prefix}canny_edge_count"] = float(edge_px)

            # 2. Sobel gradient magnitude
            sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)
            grad_mag = np.sqrt(sobelx**2 + sobely**2)
            features[f"{prefix}sobel_mean"] = round(float(np.mean(grad_mag)), 4)
            features[f"{prefix}sobel_std"] = round(float(np.std(grad_mag)), 4)
            features[f"{prefix}sobel_max"] = round(float(np.max(grad_mag)), 4)
            features[f"{prefix}sobel_p90"] = round(float(np.percentile(grad_mag, 90)), 4)

            # Gradient direction distribution (4 bins: 0-45, 45-90, 90-135, 135-180 deg)
            grad_dir = np.arctan2(np.abs(sobely), np.abs(sobelx)) * 180.0 / np.pi
            for b_idx, (lo, hi) in enumerate([(0, 45), (45, 90), (90, 135), (135, 180)]):
                bin_count = int(np.sum((grad_dir >= lo) & (grad_dir < hi)))
                features[f"{prefix}grad_dir_bin_{b_idx}"] = round(bin_count / (total_px + 1e-10), 6)

            # 3. Laplacian-of-Gaussian (LoG) sharpness
            log_result = cv2.Laplacian(img, cv2.CV_64F)
            features[f"{prefix}laplacian_variance"] = round(float(np.var(log_result)), 4)
            features[f"{prefix}laplacian_max"] = round(float(np.max(np.abs(log_result))), 4)

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        return FeatureGroup.create(
            name=self.name,
            version=self.version,
            extraction_time_ms=round(elapsed_ms, 2),
            features=features,
        )
