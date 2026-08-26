"""Semantic Genome Domain Entities.

Encapsulates document classification taxonomy, grounded Key-Information Extraction (KIE)
entities with complete bounding-box provenance, and field relationships.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import uuid

from src.domain.entities.evidence_graph import GroundedEntity


@dataclass
class DocumentTaxonomy:
    """Document classification result with hierarchical category taxonomy."""

    primary_type: str = "GENERIC_DOCUMENT"  # "INVOICE", "RECEIPT", "CERTIFICATE", "DEGREE", "TAX_DOCUMENT", "CONTRACT", "ID_CARD", etc.
    subtype: str = "UNKNOWN"
    confidence: float = 1.0
    alternative_types: list[dict[str, Any]] = field(default_factory=list)  # [{"type": "RECEIPT", "confidence": 0.25}]
    taxonomy_version: str = "1.0.0"


@dataclass
class SemanticFieldRelationship:
    """Relationship between semantic entities (e.g., total = subtotal + tax)."""

    relationship_type: str  # "MATH_SUM", "DUE_AFTER_ISSUE", "ISSUER_OF", "RECIPIENT_OF"
    source_entity_keys: list[str]
    target_entity_key: str
    is_valid: bool = True
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class SemanticGenome:
    """Complete semantic intelligence genome layer."""

    genome_id: uuid.UUID = field(default_factory=uuid.uuid4)
    taxonomy: DocumentTaxonomy = field(default_factory=DocumentTaxonomy)
    entities: dict[str, GroundedEntity] = field(default_factory=dict)  # Key -> GroundedEntity
    relationships: list[SemanticFieldRelationship] = field(default_factory=list)
    extraction_summary: dict[str, Any] = field(default_factory=dict)
    has_validation_errors: bool = False
    validation_warnings: list[str] = field(default_factory=list)
