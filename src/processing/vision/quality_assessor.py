"""Image quality assessment engine (blur, sharpness, noise, contrast)."""

import cv2
import numpy as np
import uuid

from src.domain.entities.quality_report import QualityReport


class QualityAssessor:
    """Computes objective image quality metrics."""

    def assess_page(self, page_id: uuid.UUID, image_bytes: bytes) -> QualityReport:
        """Calculates blur, sharpness, noise, and contrast for a page image."""
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return QualityReport.create(
                page_id=page_id,
                blur_score=0.0,
                sharpness_score=0.0,
                noise_score=0.0,
                contrast_score=0.0,
                metrics={"error": "Failed to decode image"},
            )

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 1. Blur score (Laplacian Variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        # 2. Sharpness score (Tenengrad gradient magnitude)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        grad_mag = np.sqrt(sobelx**2 + sobely**2)
        sharpness = float(np.mean(grad_mag))

        # 3. Noise score (Local variance in smooth regions)
        mean_intensity = float(np.mean(gray))
        std_intensity = float(np.std(gray))
        snr_db = 20.0 * np.log10(mean_intensity / (std_intensity + 1e-6)) if std_intensity > 0 else 0.0

        # 4. Contrast score (Dynamic range & RMS contrast)
        rms_contrast = std_intensity / 255.0
        min_val, max_val, _, _ = cv2.minMaxLoc(gray)
        dynamic_range = float(max_val - min_val)

        metrics = {
            "laplacian_variance": round(float(laplacian_var), 4),
            "tenengrad_sharpness": round(sharpness, 4),
            "snr_db": round(float(snr_db), 4),
            "rms_contrast": round(rms_contrast, 4),
            "dynamic_range": int(dynamic_range),
            "mean_intensity": round(mean_intensity, 2),
            "std_intensity": round(std_intensity, 2),
        }

        return QualityReport.create(
            page_id=page_id,
            blur_score=round(float(laplacian_var), 2),
            sharpness_score=round(sharpness, 2),
            noise_score=round(float(snr_db), 2),
            contrast_score=round(rms_contrast, 4),
            metrics=metrics,
        )
