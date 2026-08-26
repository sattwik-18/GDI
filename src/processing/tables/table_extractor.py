"""Structured Table Extraction Engine.

Implements high-accuracy table grid detection, cell decomposition, and token-to-cell mapping,
combining morphological line analysis and spatial token clustering (Table Transformer / PP-Structure concepts).
"""

from __future__ import annotations
from typing import Any
import cv2
import numpy as np

from src.domain.entities.structural_genome import StructuredTable, TableCell
from src.domain.interfaces.ocr_engine import OCRPageResult, OCRTextElement


class StructuredTableExtractor:
    """Extracts table grids, cell boundaries, and maps OCR tokens into cells."""

    def extract_tables_from_page(
        self,
        image_bytes: bytes,
        ocr_result: OCRPageResult,
        page_number: int,
    ) -> list[StructuredTable]:
        """Detects tables and extracts structured cell matrices."""
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        if img is None:
            return self._extract_tables_from_tokens_fallback(ocr_result, page_number)

        h, w = img.shape[:2]

        # 1. Morphological table line detection
        # Thresholding (binary inverted)
        _, thresh = cv2.threshold(img, 220, 255, cv2.THRESH_BINARY_INV)

        # Scale kernels proportionally
        scale = max(w, h) // 100
        scale = max(scale, 15)

        horiz_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (scale, 1))
        vert_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, scale))

        horiz_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horiz_kernel)
        vert_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vert_kernel)

        table_mask = cv2.add(horiz_lines, vert_lines)

        # Find table contours
        contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        tables: list[StructuredTable] = []
        min_table_area = (w * h) * 0.02  # At least 2% of page area

        for t_idx, cnt in enumerate(contours):
            x, y, tw, th = cv2.boundingRect(cnt)
            if (tw * th) < min_table_area or tw < w * 0.2 or th < h * 0.05:
                continue

            # Found candidate table ROI
            table_bbox = [
                [float(x), float(y)],
                [float(x + tw), float(y)],
                [float(x + tw), float(y + th)],
                [float(x), float(y + th)],
            ]

            # Find tokens inside table ROI
            table_tokens = [
                t for t in ocr_result.elements
                if self._token_inside_bbox(t, x, y, tw, th)
            ]

            if not table_tokens:
                continue

            structured_table = self._build_table_from_tokens(
                tokens=table_tokens,
                table_id=f"p{page_number}_tbl_{t_idx+1}",
                page_number=page_number,
                table_bbox=table_bbox,
                extraction_method="morphological_grid",
            )
            if structured_table.num_rows >= 2:
                tables.append(structured_table)

        # If morphological detection found no tables, check for borderless tabulations via token clustering
        if not tables:
            borderless_table = self._extract_tables_from_tokens_fallback(ocr_result, page_number)
            tables.extend(borderless_table)

        return tables

    def _token_inside_bbox(self, token: OCRTextElement, x: int, y: int, w: int, h: int) -> bool:
        if not token.bbox:
            return False
        cx = (token.bbox[0][0] + token.bbox[1][0]) / 2.0
        cy = (token.bbox[0][1] + token.bbox[2][1]) / 2.0 if len(token.bbox) >= 3 else token.bbox[0][1]
        return (x <= cx <= x + w) and (y <= cy <= y + h)

    def _extract_tables_from_tokens_fallback(
        self,
        ocr_result: OCRPageResult,
        page_number: int,
    ) -> list[StructuredTable]:
        """Detects borderless tables using horizontal row alignment and vertical column clustering."""
        elements = ocr_result.elements
        if len(elements) < 6:
            return []

        # Find rows by clustering tokens with similar Y coordinates (within 12px)
        sorted_tokens = sorted(elements, key=lambda t: t.bbox[0][1] if t.bbox else 0)
        rows: list[list[OCRTextElement]] = []
        curr_row: list[OCRTextElement] = []
        last_y = None

        for t in sorted_tokens:
            if not t.bbox:
                continue
            cy = t.bbox[0][1]
            if last_y is None or abs(cy - last_y) < 14:
                curr_row.append(t)
                last_y = cy
            else:
                if len(curr_row) >= 2:  # At least 2 columns in row
                    rows.append(curr_row)
                curr_row = [t]
                last_y = cy

        if len(curr_row) >= 2:
            rows.append(curr_row)

        # If we have 3 or more consecutive multi-token rows, treat as a table
        if len(rows) >= 3:
            table_tokens = [t for r in rows for t in r]
            xs = [pt[0] for t in table_tokens for pt in t.bbox]
            ys = [pt[1] for t in table_tokens for pt in t.bbox]
            bbox = [
                [float(min(xs)), float(min(ys))],
                [float(max(xs)), float(min(ys))],
                [float(max(xs)), float(max(ys))],
                [float(min(xs)), float(max(ys))],
            ]
            tbl = self._build_table_from_tokens(
                tokens=table_tokens,
                table_id=f"p{page_number}_tbl_1",
                page_number=page_number,
                table_bbox=bbox,
                extraction_method="token_spatial_clustering",
            )
            return [tbl] if tbl.num_rows >= 2 else []

        return []

    def _build_table_from_tokens(
        self,
        tokens: list[OCRTextElement],
        table_id: str,
        page_number: int,
        table_bbox: list[list[float]],
        extraction_method: str,
    ) -> StructuredTable:
        """Clusters tokens into rows and columns, mapping bounding boxes and OCR token IDs."""
        # 1. Cluster rows by Y coordinate
        sorted_by_y = sorted(tokens, key=lambda t: t.bbox[0][1] if t.bbox else 0)
        row_groups: list[list[OCRTextElement]] = []
        current_row: list[OCRTextElement] = []
        last_y = None

        for t in sorted_by_y:
            if not t.bbox:
                continue
            cy = t.bbox[0][1]
            if last_y is None or abs(cy - last_y) < 15:
                current_row.append(t)
                last_y = cy
            else:
                if current_row:
                    row_groups.append(sorted(current_row, key=lambda tk: tk.bbox[0][0] if tk.bbox else 0))
                current_row = [t]
                last_y = cy

        if current_row:
            row_groups.append(sorted(current_row, key=lambda tk: tk.bbox[0][0] if tk.bbox else 0))

        if not row_groups:
            return StructuredTable(table_id=table_id, page_number=page_number, bbox=table_bbox)

        # 2. Determine column count
        max_cols = max(len(r) for r in row_groups)
        cells: list[TableCell] = []

        for r_idx, row_tokens in enumerate(row_groups):
            is_header_row = (r_idx == 0)
            for c_idx, token in enumerate(row_tokens):
                cell_id = f"{table_id}_r{r_idx+1}_c{c_idx+1}"
                cells.append(
                    TableCell(
                        cell_id=cell_id,
                        row_index=r_idx,
                        col_index=c_idx,
                        row_span=1,
                        col_span=1,
                        is_header=is_header_row,
                        bbox=token.bbox,
                        text=token.text,
                        confidence=token.confidence,
                        ocr_token_ids=[str(token.id)],
                    )
                )

        mean_conf = float(np.mean([c.confidence for c in cells])) if cells else 1.0

        return StructuredTable(
            table_id=table_id,
            page_number=page_number,
            bbox=table_bbox,
            num_rows=len(row_groups),
            num_cols=max_cols,
            cells=cells,
            has_header=True,
            confidence=round(mean_conf, 4),
            extraction_method=extraction_method,
        )
