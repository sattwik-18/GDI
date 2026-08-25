"""FeatureRegistry: dynamic registration and discovery of FeatureExtractors."""

from src.domain.interfaces.feature_extractor import FeatureExtractor
from src.processing.extractors.edge_extractor import EdgeExtractor
from src.processing.extractors.frequency_extractor import FrequencyExtractor
from src.processing.extractors.geometry_extractor import GeometryExtractor
from src.processing.extractors.ocr_extractor import OCRFeatureExtractor
from src.processing.extractors.statistical_extractor import StatisticalExtractor
from src.processing.extractors.texture_extractor import TextureExtractor


class FeatureRegistry:
    """Registry managing registered FeatureExtractor implementations."""

    def __init__(self) -> None:
        self._extractors: dict[str, FeatureExtractor] = {}

    def register(self, extractor: FeatureExtractor) -> None:
        """Registers a feature extractor."""
        if extractor.name in self._extractors:
            raise ValueError(f"FeatureExtractor '{extractor.name}' is already registered.")
        self._extractors[extractor.name] = extractor

    def get(self, name: str) -> FeatureExtractor | None:
        """Gets a feature extractor by name."""
        return self._extractors.get(name)

    def get_all(self) -> list[FeatureExtractor]:
        """Returns all registered extractors in registration order."""
        return list(self._extractors.values())

    def clear(self) -> None:
        """Clears all registered extractors (useful for unit testing)."""
        self._extractors.clear()


def get_default_feature_registry() -> FeatureRegistry:
    """Factory creating a FeatureRegistry pre-loaded with all Prototype 1 extractors in deterministic order."""
    registry = FeatureRegistry()
    registry.register(GeometryExtractor())
    registry.register(TextureExtractor())
    registry.register(FrequencyExtractor())
    registry.register(EdgeExtractor())
    registry.register(OCRFeatureExtractor())
    registry.register(StatisticalExtractor())
    return registry
