"""Geometry Feature Extractor."""

import time
from src.application.context.processing_context import ProcessingContext
from src.domain.entities.feature_group import FeatureGroup
from src.domain.interfaces.feature_extractor import FeatureExtractor


class GeometryExtractor(FeatureExtractor):
    """Extracts geometric features (dimensions, aspect ratios, margins, bounding boxes)."""

    @property
    def name(self) -> str:
        return "GeometryExtractor"

    @property
    def version(self) -> str:
        return "1.0.0"

    def extract(self, context: ProcessingContext) -> FeatureGroup:
        start_t = time.perf_counter()
        features: dict[str, float] = {}

        for idx, page in enumerate(context.pages):
            prefix = f"p{page.page_number}_geom_"
            w, h = page.width_px, page.height_px
            aspect_ratio = float(w) / float(h) if h > 0 else 1.0

            features[f"{prefix}width_px"] = float(w)
            features[f"{prefix}height_px"] = float(h)
            features[f"{prefix}aspect_ratio"] = round(aspect_ratio, 4)
            features[f"{prefix}dpi"] = float(page.dpi)
            features[f"{prefix}orientation_deg"] = float(page.orientation_deg)

            # OCR Bounding box statistics
            ocr_res = context.ocr_results[idx] if idx < len(context.ocr_results) else None
            if ocr_res and ocr_res.elements:
                bbox_widths = [el.bbox[1][0] - el.bbox[0][0] for el in ocr_res.elements if len(el.bbox) >= 2]
                bbox_heights = [el.bbox[2][1] - el.bbox[0][1] for el in ocr_res.elements if len(el.bbox) >= 3]

                features[f"{prefix}bbox_count"] = float(len(ocr_res.elements))
                features[f"{prefix}mean_bbox_width"] = round(float(sum(bbox_widths) / len(bbox_widths)), 2) if bbox_widths else 0.0
                features[f"{prefix}mean_bbox_height"] = round(float(sum(bbox_heights) / len(bbox_heights)), 2) if bbox_heights else 0.0
            else:
                features[f"{prefix}bbox_count"] = 0.0
                features[f"{prefix}mean_bbox_width"] = 0.0
                features[f"{prefix}mean_bbox_height"] = 0.0

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        return FeatureGroup.create(
            name=self.name,
            version=self.version,
            extraction_time_ms=round(elapsed_ms, 2),
            features=features,
        )
