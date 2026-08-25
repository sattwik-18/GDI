"""Frequency Feature Extractor (FFT, DCT, Wavelet statistics)."""

import time
import cv2
import numpy as np
import pywt

from src.application.context.processing_context import ProcessingContext
from src.domain.entities.feature_group import FeatureGroup
from src.domain.interfaces.feature_extractor import FeatureExtractor


class FrequencyExtractor(FeatureExtractor):
    """Extracts frequency domain features: FFT magnitude statistics, DCT energy, Wavelet band stats."""

    @property
    def name(self) -> str:
        return "FrequencyExtractor"

    @property
    def version(self) -> str:
        return "1.0.0"

    def extract(self, context: ProcessingContext) -> FeatureGroup:
        start_t = time.perf_counter()
        features: dict[str, float] = {}

        for n_page in context.normalized_pages:
            prefix = f"p{n_page.page_number}_freq_"
            nparr = np.frombuffer(n_page.image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

            if img is None:
                continue

            # Resize to 512x512 for deterministic computation
            h, w = img.shape
            if h != 512 or w != 512:
                img = cv2.resize(img, (512, 512), interpolation=cv2.INTER_AREA)

            img_f = img.astype(np.float64)

            # 1. FFT magnitude spectrum statistics
            fft2d = np.fft.fft2(img_f)
            fft_magnitude = np.abs(np.fft.fftshift(fft2d))
            features[f"{prefix}fft_mean"] = round(float(np.mean(fft_magnitude)), 4)
            features[f"{prefix}fft_std"] = round(float(np.std(fft_magnitude)), 4)
            features[f"{prefix}fft_max"] = round(float(np.max(fft_magnitude)), 4)
            features[f"{prefix}fft_energy"] = round(float(np.sum(fft_magnitude**2)), 4)

            # High-frequency ratio: energy in outer vs inner 25% radius
            cy, cx = img_f.shape[0] // 2, img_f.shape[1] // 2
            y_coords, x_coords = np.ogrid[-cy:cy, -cx:cx]
            dist_map = np.sqrt(x_coords**2 + y_coords**2)
            inner_radius = min(cy, cx) * 0.25
            inner_mask = dist_map < inner_radius
            outer_mask = ~inner_mask
            low_freq_energy = float(np.sum(fft_magnitude[inner_mask] ** 2))
            high_freq_energy = float(np.sum(fft_magnitude[outer_mask] ** 2))
            total_energy = low_freq_energy + high_freq_energy + 1e-10
            features[f"{prefix}fft_hf_ratio"] = round(high_freq_energy / total_energy, 4)

            # 2. DCT energy concentration (top-left 8x8 block fraction)
            dct_result = cv2.dct(img_f)
            dc_component = float(dct_result[0, 0])
            dct_8x8_energy = float(np.sum(dct_result[:8, :8] ** 2))
            dct_total_energy = float(np.sum(dct_result**2)) + 1e-10
            features[f"{prefix}dct_dc_component"] = round(dc_component, 4)
            features[f"{prefix}dct_energy_concentration"] = round(dct_8x8_energy / dct_total_energy, 4)
            features[f"{prefix}dct_mean"] = round(float(np.mean(np.abs(dct_result))), 4)
            features[f"{prefix}dct_std"] = round(float(np.std(dct_result)), 4)

            # 3. Wavelet statistics (Haar, 2 levels)
            coeffs = pywt.wavedec2(img_f, wavelet="haar", level=2)
            # LL (approximation) statistics
            ll_band = coeffs[0]
            features[f"{prefix}wavelet_ll_mean"] = round(float(np.mean(ll_band)), 4)
            features[f"{prefix}wavelet_ll_std"] = round(float(np.std(ll_band)), 4)
            features[f"{prefix}wavelet_ll_energy"] = round(float(np.sum(ll_band**2)), 4)

            # Detail bands at each level
            for level_idx, detail_tuple in enumerate(coeffs[1:], start=1):
                lh, hl, hh = detail_tuple
                for band_name, band in [("lh", lh), ("hl", hl), ("hh", hh)]:
                    features[f"{prefix}wavelet_l{level_idx}_{band_name}_std"] = round(float(np.std(band)), 4)
                    features[f"{prefix}wavelet_l{level_idx}_{band_name}_energy"] = round(float(np.sum(band**2)), 4)

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        return FeatureGroup.create(
            name=self.name,
            version=self.version,
            extraction_time_ms=round(elapsed_ms, 2),
            features=features,
        )
