"""Unit tests for PipelineRegistry."""

import pytest
from unittest.mock import MagicMock
from src.application.registry.pipeline_registry import PipelineRegistry, get_default_pipeline_registry
from src.config.settings import get_settings


class TestPipelineRegistry:

    def test_default_registry_has_steps(self, monkeypatch: pytest.MonkeyPatch) -> None:
        settings = get_settings()
        monkeypatch.setattr(settings.ocr, "dev_ocr_fallback", True)

        mock_session = MagicMock()
        reg = get_default_pipeline_registry(mock_session)
        steps = reg.build_ordered()
        assert len(steps) >= 17
        step_names = [s.name for s in steps]
        assert "TableExtractionStep" in step_names
        assert "DocumentClassificationStep" in step_names
        assert "SemanticKIEStep" in step_names
        assert "VisualEmbeddingStep" in step_names
        assert "TemplateIntelligenceStep" in step_names

    def test_steps_are_ordered_by_order_integer(self, monkeypatch: pytest.MonkeyPatch) -> None:
        settings = get_settings()
        monkeypatch.setattr(settings.ocr, "dev_ocr_fallback", True)

        mock_session = MagicMock()
        reg = get_default_pipeline_registry(mock_session)
        steps = reg.build_ordered()

        assert steps[0].name == "ValidationStep"
        assert steps[-1].name == "ManifestGenerationStep"
