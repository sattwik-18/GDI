"""Unit tests for FeatureRegistry."""

import pytest
from src.application.registry.feature_registry import FeatureRegistry, get_default_feature_registry
from src.processing.extractors.geometry_extractor import GeometryExtractor


class TestFeatureRegistry:

    def test_default_registry_has_6_extractors(self) -> None:
        reg = get_default_feature_registry()
        extractors = reg.get_all()
        assert len(extractors) == 6

    def test_duplicate_registration_raises_value_error(self) -> None:
        reg = FeatureRegistry()
        ext = GeometryExtractor()
        reg.register(ext)
        with pytest.raises(ValueError, match="already registered"):
            reg.register(ext)

    def test_clear_empties_registry(self) -> None:
        reg = get_default_feature_registry()
        assert len(reg.get_all()) == 6
        reg.clear()
        assert len(reg.get_all()) == 0
