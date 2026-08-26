"""Structural Genome Domain Entities.

Encapsulates Docling-inspired hierarchical document representations,
element taxonomy, reading order graphs, and structured table/cell decompositions.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import uuid


@dataclass
class TableCell:
    """A single cell within a structured table."""

    cell_id: str
    row_index: int
    col_index: int
    row_span: int = 1
    col_span: int = 1
    is_header: bool = False
    bbox: list[list[float]] = field(default_factory=list)  # Polygon coordinates
    text: str = ""
    confidence: float = 1.0
    ocr_token_ids: list[str] = field(default_factory=list)


@dataclass
class StructuredTable:
    """Full structured table representation with grid matrix and cell relationships."""

    table_id: str
    page_number: int
    bbox: list[list[float]] = field(default_factory=list)
    num_rows: int = 0
    num_cols: int = 0
    cells: list[TableCell] = field(default_factory=list)
    has_header: bool = True
    confidence: float = 1.0
    extraction_method: str = "morphological_grid"  # "morphological_grid", "table_transformer", "pp_structure"

    def to_matrix(self) -> list[list[str]]:
        """Converts cells into a 2D string matrix."""
        if self.num_rows == 0 or self.num_cols == 0:
            return []
        grid = [["" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        for cell in self.cells:
            if 0 <= cell.row_index < self.num_rows and 0 <= cell.col_index < self.num_cols:
                grid[cell.row_index][cell.col_index] = cell.text
        return grid


@dataclass
class StructuralElement:
    """A typed structural region within the document hierarchy."""

    element_id: str
    element_type: str  # "HEADER", "PARAGRAPH", "TABLE", "FIGURE", "KEY_VALUE_PAIR", "FOOTER", "SEAL", "SIGNATURE", "LIST_ITEM"
    page_number: int
    bbox: list[list[float]] = field(default_factory=list)
    reading_order_index: int = 0
    text: str = ""
    confidence: float = 1.0
    parent_element_id: str | None = None
    child_element_ids: list[str] = field(default_factory=list)
    ocr_token_ids: list[str] = field(default_factory=list)
    table_data: StructuredTable | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StructuralGenome:
    """Complete structural genome layer for a document."""

    genome_id: uuid.UUID = field(default_factory=uuid.uuid4)
    elements: list[StructuralElement] = field(default_factory=list)
    tables: list[StructuredTable] = field(default_factory=list)
    reading_order: list[str] = field(default_factory=list)  # Ordered element IDs
    total_regions: int = 0
    total_tables: int = 0
    column_count_estimate: int = 1
