"""Image normalization engine using OpenCV (skew, color, border normalization)."""

import cv2
import numpy as np

from src.application.context.processing_context import NormalizedPageData, RenderedPageData
from src.config.settings import get_settings

settings = get_settings()


class ImageNormalizer:
    """Normalizes rendered images (deskewing, perspective correction, color space)."""

    def __init__(self) -> None:
        self._vision_config = settings.vision

    def normalize(self, page_data: RenderedPageData) -> NormalizedPageData:
        """Normalizes a single rendered page."""
        # Convert bytes to cv2 Mat
        nparr = np.frombuffer(page_data.image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return NormalizedPageData(
                page_number=page_data.page_number,
                image_bytes=page_data.image_bytes,
                skew_angle_deg=0.0,
                color_space="sRGB",
            )

        skew_angle = 0.0
        if self._vision_config.enable_deskew:
            img, skew_angle = self._deskew(img)

        # Encode back to PNG
        _, buf = cv2.imencode(".png", img)
        norm_bytes = buf.tobytes()

        return NormalizedPageData(
            page_number=page_data.page_number,
            image_bytes=norm_bytes,
            skew_angle_deg=round(float(skew_angle), 2),
            color_space="sRGB",
        )

    def _deskew(self, img: np.ndarray) -> tuple[np.ndarray, float]:
        """Detects skew angle using Hough Transform and rotates image if skew > 0.5 deg."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(
            gray,
            self._vision_config.canny_lower_threshold,
            self._vision_config.canny_upper_threshold,
            apertureSize=3,
        )
        lines = cv2.HoughLinesP(
            edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10
        )

        if lines is None or len(lines) == 0:
            return img, 0.0

        angles = []
        for line in lines:
            pts = np.asarray(line).ravel()
            if len(pts) < 4:
                continue
            x1, y1, x2, y2 = pts[0], pts[1], pts[2], pts[3]
            angle = float(np.arctan2(float(y2 - y1), float(x2 - x1)) * 180.0 / np.pi)
            if -45 < angle < 45:
                angles.append(angle)

        if not angles:
            return img, 0.0

        median_angle = float(np.median(angles))
        if abs(median_angle) < 0.5:
            return img, median_angle

        h, w = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        rotated = cv2.warpAffine(
            img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )
        return rotated, median_angle
