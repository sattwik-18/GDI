"""Visual Genome Domain Entities.

Encapsulates dense visual embeddings (DINOv2 / ViT), visual perceptual fingerprints,
and layout topology signatures.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import uuid


@dataclass
class VisualGenome:
    """Visual appearance and dense layout embedding genome layer."""

    genome_id: uuid.UUID = field(default_factory=uuid.uuid4)
    visual_embedding: list[float] = field(default_factory=list)  # e.g., 384-D / 768-D DINOv2 vector
    embedding_dimension: int = 0
    embedding_model: str = "dinov2_vits14_spatial"
    perceptual_hash: str = ""
    color_palette: list[dict[str, Any]] = field(default_factory=list)  # Top dominant colors & ratios
    visual_signature_version: str = "1.0.0"
