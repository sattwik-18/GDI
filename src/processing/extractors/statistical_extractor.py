"""Statistical Image Feature Extractor (histogram stats, mean, std, skewness, kurtosis)."""

import time
import cv2
import numpy as np
from scipy import stats

from src.application.context.processing_context import ProcessingContext
from src.domain.entities.feature_group import FeatureGroup
from src.domain.interfaces.feature_extractor import FeatureExtractor


class StatisticalExtractor(FeatureExtractor):
    """Extracts pixel intensity distribution statistics and histogram descriptors."""

    @property
    def name(self) -> str:
        return "StatisticalExtractor"

    @property
    def version(self) -> str:
        return "1.0.0"

    def extract(self, context: ProcessingContext) -> FeatureGroup:
        start_t = time.perf_counter()
        features: dict[str, float] = {}

        for n_page in context.normalized_pages:
            prefix = f"p{n_page.page_number}_stat_"
            nparr = np.frombuffer(n_page.image_bytes, np.uint8)
            img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            img_gray = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

            if img_gray is None:
                continue

            gray_f = img_gray.astype(np.float64)

            # 1. Grayscale intensity statistics
            features[f"{prefix}mean"] = round(float(np.mean(gray_f)), 4)
            features[f"{prefix}median"] = round(float(np.median(gray_f)), 4)
            features[f"{prefix}std"] = round(float(np.std(gray_f)), 4)
            features[f"{prefix}variance"] = round(float(np.var(gray_f)), 4)
            features[f"{prefix}skewness"] = round(float(stats.skew(gray_f.ravel())), 4)
            features[f"{prefix}kurtosis"] = round(float(stats.kurtosis(gray_f.ravel())), 4)
            features[f"{prefix}p5"] = round(float(np.percentile(gray_f, 5)), 4)
            features[f"{prefix}p25"] = round(float(np.percentile(gray_f, 25)), 4)
            features[f"{prefix}p75"] = round(float(np.percentile(gray_f, 75)), 4)
            features[f"{prefix}p95"] = round(float(np.percentile(gray_f, 95)), 4)

            # 2. Normalized histogram (16 bins, deterministic)
            hist, _ = np.histogram(img_gray.ravel(), bins=16, range=(0, 256), density=True)
            for b_idx, val in enumerate(hist):
                features[f"{prefix}hist_bin_{b_idx}"] = round(float(val), 6)

            # 3. Per-channel (BGR) mean and std
            if img_bgr is not None:
                for ch_idx, ch_name in enumerate(["blue", "green", "red"]):
                    ch = img_bgr[:, :, ch_idx].astype(np.float64)
                    features[f"{prefix}ch_{ch_name}_mean"] = round(float(np.mean(ch)), 4)
                    features[f"{prefix}ch_{ch_name}_std"] = round(float(np.std(ch)), 4)

            # 4. Entropy (Shannon)
            hist_norm = hist + 1e-10
            entropy = float(-np.sum(hist_norm * np.log2(hist_norm)))
            features[f"{prefix}shannon_entropy"] = round(entropy, 4)

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        return FeatureGroup.create(
            name=self.name,
            version=self.version,
            extraction_time_ms=round(elapsed_ms, 2),
            features=features,
        )
