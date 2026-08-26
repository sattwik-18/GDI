"""Evidence Graph and Provenance Domain Models.

Every semantic field, table cell, layout element, and anomaly contains a traceable
provenance link back to the exact source page, bounding box, OCR token IDs, model,
and extraction method.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


@dataclass
class EntityProvenance:
    """Complete provenance metadata for any extracted value or element."""

    page_number: int
    bounding_box: list[list[float]]  # 4-point polygon [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    source_ocr_token_ids: list[str] = field(default_factory=list)
    extraction_method: str = "deterministic_spatial_rule"  # "deterministic_spatial_rule", "table_extractor", "vlm_grounded", etc.
    model_version: str = "1.0.0"
    model_fingerprint: str = ""
    extracted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class GroundedEntity:
    """A semantic field grounded with value, confidence, and provenance."""

    entity_id: str
    key: str
    value: Any
    normalized_value: Any
    data_type: str = "string"  # "string", "currency", "date", "number", "boolean", "composite"
    confidence: float = 1.0  # Calibrated confidence 0.0 - 1.0
    is_ambiguous: bool = False
    provenance: EntityProvenance | None = None
    validation_status: str = "VALID"  # "VALID", "WARNING", "INVALID", "NEEDS_REVIEW"
    validation_message: str | None = None


@dataclass
class EvidenceNode:
    """A single node in the document evidence graph."""

    node_id: str
    node_type: str  # "OCR_TOKEN", "LAYOUT_REGION", "TABLE_CELL", "SEMANTIC_FIELD", "ANOMALY"
    page_number: int
    bbox: list[list[float]]
    text: str
    confidence: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidenceEdge:
    """Directed edge representing spatial, hierarchical, or semantic relationships."""

    source_node_id: str
    target_node_id: str
    relationship: str  # "CONTAINS", "READING_ORDER_NEXT", "KEY_FOR_VALUE", "ROW_SIBLING", "COL_SIBLING", "ALIGNED_WITH"
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentEvidenceGraph:
    """Complete document evidence graph linking all extracted tokens, regions, cells, and entities."""

    graph_id: uuid.UUID = field(default_factory=uuid.uuid4)
    nodes: list[EvidenceNode] = field(default_factory=list)
    edges: list[EvidenceEdge] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_node(self, node: EvidenceNode) -> None:
        self.nodes.append(node)

    def add_edge(self, edge: EvidenceEdge) -> None:
        self.edges.append(edge)
