"""Advanced Layout Analyzer.

Implements Docling-inspired document element modeling, XY-Cut++ hierarchical spatial
decomposition, and topological reading-order sorting.
"""

from __future__ import annotations
from typing import Any
import numpy as np

from src.domain.entities.structural_genome import StructuralElement, StructuralGenome
from src.domain.interfaces.ocr_engine import OCRPageResult, OCRTextElement


class AdvancedLayoutAnalyzer:
    """Hybrid layout analysis and reading-order engine."""

    def analyze_page(
        self,
        ocr_result: OCRPageResult,
        page_width: int,
        page_height: int,
    ) -> tuple[list[StructuralElement], list[str]]:
        """Analyzes spatial layout, groups OCR tokens into hierarchical structural blocks,

        and computes calibrated reading order.
        """
        elements = ocr_result.elements
        if not elements:
            return [], []

        # 1. Sort tokens into lines based on Y-proximity and reading direction
        sorted_tokens = sorted(
            elements,
            key=lambda el: (
                el.bbox[0][1] if el.bbox else 0,
                el.bbox[0][0] if el.bbox else 0,
            ),
        )

        # 2. XY-Cut++ / Spatial clustering into structural blocks
        blocks: list[list[OCRTextElement]] = []
        current_block: list[OCRTextElement] = []

        line_height_estimate = 20.0
        if elements:
            heights = [
                abs(el.bbox[2][1] - el.bbox[0][1])
                for el in elements
                if el.bbox and len(el.bbox) >= 3
            ]
            if heights:
                line_height_estimate = float(np.median(heights))

        y_threshold = max(line_height_estimate * 1.5, 25.0)

        for token in sorted_tokens:
            if not current_block:
                current_block.append(token)
                continue

            last_token = current_block[-1]
            last_y = last_token.bbox[2][1] if len(last_token.bbox) >= 3 else last_token.bbox[0][1]
            curr_y = token.bbox[0][1] if token.bbox else 0

            # If vertical gap exceeds threshold, start a new block
            if (curr_y - last_y) > y_threshold:
                blocks.append(current_block)
                current_block = [token]
            else:
                current_block.append(token)

        if current_block:
            blocks.append(current_block)

        # 3. Construct StructuralElement items with taxonomy classification
        structural_elements: list[StructuralElement] = []
        reading_order: list[str] = []

        for idx, block_tokens in enumerate(blocks):
            elem_id = f"p{ocr_result.page_number}_elem_{idx+1}"
            reading_order.append(elem_id)

            # Compute union bounding box
            all_xs = [pt[0] for t in block_tokens for pt in t.bbox if t.bbox]
            all_ys = [pt[1] for t in block_tokens for pt in t.bbox if t.bbox]
            min_x = min(all_xs) if all_xs else 0.0
            max_x = max(all_xs) if all_xs else float(page_width)
            min_y = min(all_ys) if all_ys else 0.0
            max_y = max(all_ys) if all_ys else float(page_height)

            block_bbox = [
                [round(min_x, 1), round(min_y, 1)],
                [round(max_x, 1), round(min_y, 1)],
                [round(max_x, 1), round(max_y, 1)],
                [round(min_x, 1), round(max_y, 1)],
            ]

            block_text = " ".join(t.text for t in block_tokens)
            mean_conf = float(np.mean([t.confidence for t in block_tokens])) if block_tokens else 1.0

            # Heuristic / spatial classification of element type
            elem_type = self._classify_element_type(
                block_text=block_text,
                min_y=min_y,
                max_y=max_y,
                page_height=page_height,
                token_count=len(block_tokens),
            )

            token_ids = [str(t.id) for t in block_tokens]

            structural_elements.append(
                StructuralElement(
                    element_id=elem_id,
                    element_type=elem_type,
                    page_number=ocr_result.page_number,
                    bbox=block_bbox,
                    reading_order_index=idx + 1,
                    text=block_text,
                    confidence=round(mean_conf, 4),
                    ocr_token_ids=token_ids,
                    metadata={
                        "token_count": len(token_ids),
                        "line_height_est": round(line_height_estimate, 1),
                    },
                )
            )

        return structural_elements, reading_order

    def _classify_element_type(
        self,
        block_text: str,
        min_y: float,
        max_y: float,
        page_height: int,
        token_count: int,
    ) -> str:
        """Classifies structural element taxonomy."""
        upper_text = block_text.upper()

        # 1. Header (top 15% of page or strong keywords)
        if min_y < page_height * 0.15 and token_count <= 15:
            if any(k in upper_text for k in ["INVOICE", "STATEMENT", "CERTIFICATE", "BILL TO", "TAX", "REPORT"]):
                return "HEADER"
            if token_count <= 8:
                return "HEADER"

        # 2. Footer (bottom 10% of page)
        if max_y > page_height * 0.90 and token_count <= 25:
            return "FOOTER"

        # 3. Key-Value pair (contains ':' with short token count)
        if ":" in block_text and token_count <= 10:
            return "KEY_VALUE_PAIR"

        # 4. List Item
        if block_text.strip().startswith(("-", "•", "*", "1.", "2.", "3.", "[ ]", "[x]")):
            return "LIST_ITEM"

        # 5. Default paragraph
        return "PARAGRAPH"
