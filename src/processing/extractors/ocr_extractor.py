"""OCR Feature Extractor (character counts, word counts, confidence statistics)."""

import time
import numpy as np

from src.application.context.processing_context import ProcessingContext
from src.domain.entities.feature_group import FeatureGroup
from src.domain.interfaces.feature_extractor import FeatureExtractor


class OCRFeatureExtractor(FeatureExtractor):
    """Extracts features derived from OCR results: character/word/line counts, confidence stats."""

    @property
    def name(self) -> str:
        return "OCRFeatureExtractor"

    @property
    def version(self) -> str:
        return "1.0.0"

    def extract(self, context: ProcessingContext) -> FeatureGroup:
        start_t = time.perf_counter()
        features: dict[str, float] = {}

        for ocr_res in context.ocr_results:
            prefix = f"p{ocr_res.page_number}_ocr_"
            elements = ocr_res.elements

            confidences = [el.confidence for el in elements]
            char_counts = [len(el.text) for el in elements]
            word_counts = [len(el.text.split()) for el in elements]

            total_chars = sum(char_counts)
            total_words = sum(word_counts)
            total_elements = len(elements)

            # Count unique lines by grouping by approximate Y coordinate
            if elements:
                y_coords = sorted({round(el.bbox[0][1]) for el in elements if el.bbox})
                y_bins = []
                last_y: float | None = None
                for y in y_coords:
                    if last_y is None or (y - last_y) > 15:
                        y_bins.append(y)
                        last_y = float(y)
                line_count = len(y_bins)
            else:
                line_count = 0

            features[f"{prefix}element_count"] = float(total_elements)
            features[f"{prefix}char_count"] = float(total_chars)
            features[f"{prefix}word_count"] = float(total_words)
            features[f"{prefix}line_count"] = float(line_count)
            features[f"{prefix}avg_words_per_element"] = round(total_words / max(total_elements, 1), 4)
            features[f"{prefix}avg_chars_per_word"] = round(total_chars / max(total_words, 1), 4)

            if confidences:
                features[f"{prefix}mean_confidence"] = round(float(np.mean(confidences)), 4)
                features[f"{prefix}min_confidence"] = round(float(np.min(confidences)), 4)
                features[f"{prefix}max_confidence"] = round(float(np.max(confidences)), 4)
                features[f"{prefix}std_confidence"] = round(float(np.std(confidences)), 4)
                features[f"{prefix}p10_confidence"] = round(float(np.percentile(confidences, 10)), 4)
                features[f"{prefix}p90_confidence"] = round(float(np.percentile(confidences, 90)), 4)
                features[f"{prefix}high_confidence_ratio"] = round(
                    float(sum(c >= 0.9 for c in confidences)) / len(confidences), 4
                )
            else:
                for metric in ["mean", "min", "max", "std", "p10", "p90"]:
                    features[f"{prefix}{metric}_confidence"] = 0.0
                features[f"{prefix}high_confidence_ratio"] = 0.0

            features[f"{prefix}text_density"] = round(
                total_chars / (context.pages[ocr_res.page_number - 1].width_px * context.pages[ocr_res.page_number - 1].height_px + 1e-10)
                if context.pages
                else 0.0,
                8,
            )

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        return FeatureGroup.create(
            name=self.name,
            version=self.version,
            extraction_time_ms=round(elapsed_ms, 2),
            features=features,
        )
