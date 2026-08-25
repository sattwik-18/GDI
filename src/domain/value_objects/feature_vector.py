"""Feature vector value object."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class FeatureVector:
    """Normalized feature vector representation."""

    values: tuple[float, ...]

    @property
    def dimension(self) -> int:
        return len(self.values)

    @property
    def l2_norm(self) -> float:
        return math.sqrt(sum(x * x for x in self.values))

    def normalize_l2(self) -> "FeatureVector":
        norm = self.l2_norm
        if norm == 0.0:
            return self
        return FeatureVector(values=tuple(x / norm for x in self.values))
