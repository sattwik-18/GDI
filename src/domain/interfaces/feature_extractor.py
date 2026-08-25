"""Abstract FeatureExtractor interface."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.application.context.processing_context import ProcessingContext
    from src.domain.entities.feature_group import FeatureGroup


class FeatureExtractor(ABC):
    """Common interface for all deterministic feature extractors."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the feature extractor group."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Version of the feature extractor logic."""
        pass

    @abstractmethod
    def extract(self, context: "ProcessingContext") -> "FeatureGroup":
        """Extracts features from the processing context into a FeatureGroup."""
        pass
