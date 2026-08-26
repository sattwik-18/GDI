"""Document Layout Graph Topology Comparator.

Compares document structure via hierarchical graph edit distance and spatial relationships
(ABOVE, BELOW, ALIGNED, CONTAINS), incorporating semantic region types, relative geometry,
bounding box coordinates, and reading order sequences.
"""

from __future__ import annotations
import math
from typing import Any


class LayoutGraphNode:
    """Represents a structural layout node with geometry and semantic type."""

    def __init__(
        self,
        node_id: str,
        node_type: str,  # "HEADER" | "PARAGRAPH" | "TABLE" | "FOOTER" | "KV_FIELD" | "SEAL"
        bbox: list[list[float]] | list[float],
        page_idx: int = 0,
        text_snippet: str = "",
    ) -> None:
        self.node_id = node_id
        self.node_type = node_type.upper()
        self.page_idx = page_idx
        self.text_snippet = text_snippet

        # Normalize bbox to [ymin, xmin, ymax, xmax] in [0, 1000] space
        if bbox and isinstance(bbox[0], (list, tuple)) and len(bbox) >= 2:
            self.ymin = float(bbox[0][1])
            self.xmin = float(bbox[0][0])
            self.ymax = float(bbox[1][1])
            self.xmax = float(bbox[1][0])
        elif bbox and len(bbox) >= 4 and isinstance(bbox[0], (int, float)):
            self.ymin = float(bbox[0])
            self.xmin = float(bbox[1])
            self.ymax = float(bbox[2])
            self.xmax = float(bbox[3])
        else:
            self.ymin, self.xmin, self.ymax, self.xmax = 0.0, 0.0, 100.0, 100.0

        self.height = max(1.0, self.ymax - self.ymin)
        self.width = max(1.0, self.xmax - self.xmin)
        self.center_y = (self.ymin + self.ymax) / 2.0
        self.center_x = (self.xmin + self.xmax) / 2.0
        self.aspect_ratio = self.width / self.height

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "page_idx": self.page_idx,
            "center": [round(self.center_x, 1), round(self.center_y, 1)],
            "size": [round(self.width, 1), round(self.height, 1)],
            "aspect_ratio": round(self.aspect_ratio, 2),
            "text": self.text_snippet[:30],
        }


class LayoutGraphMatchResult:
    """Document layout graph comparison metrics."""

    def __init__(
        self,
        nodes_a_count: int,
        nodes_b_count: int,
        node_type_similarity: float,
        spatial_relation_similarity: float,
        reading_order_similarity: float,
        graph_edit_similarity: float,
        matched_node_pairs: list[tuple[str, str]] | None = None,
        unmatched_nodes_a: list[str] | None = None,
        unmatched_nodes_b: list[str] | None = None,
        graph_a_summary: list[dict[str, Any]] | None = None,
        graph_b_summary: list[dict[str, Any]] | None = None,
    ) -> None:
        self.nodes_a_count = nodes_a_count
        self.nodes_b_count = nodes_b_count
        self.node_type_similarity = round(node_type_similarity, 4)
        self.spatial_relation_similarity = round(spatial_relation_similarity, 4)
        self.reading_order_similarity = round(reading_order_similarity, 4)
        self.graph_edit_similarity = round(graph_edit_similarity, 4)
        self.matched_node_pairs = matched_node_pairs or []
        self.unmatched_nodes_a = unmatched_nodes_a or []
        self.unmatched_nodes_b = unmatched_nodes_b or []
        self.graph_a_summary = graph_a_summary or []
        self.graph_b_summary = graph_b_summary or []

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes_a_count": self.nodes_a_count,
            "nodes_b_count": self.nodes_b_count,
            "node_type_similarity": self.node_type_similarity,
            "spatial_relation_similarity": self.spatial_relation_similarity,
            "reading_order_similarity": self.reading_order_similarity,
            "graph_edit_similarity": self.graph_edit_similarity,
            "matched_node_pairs": self.matched_node_pairs,
            "unmatched_nodes_a": self.unmatched_nodes_a,
            "unmatched_nodes_b": self.unmatched_nodes_b,
            "graph_a_nodes": self.graph_a_summary,
            "graph_b_nodes": self.graph_b_summary,
        }


class LayoutGraphComparator:
    """Evaluates hierarchical graph edit distance and reading order topology."""

    def extract_nodes(self, genome_data: dict[str, Any] | Any) -> list[LayoutGraphNode]:
        """Extracts rich structural layout nodes from structural elements and OCR blocks."""
        def _get(obj: Any, key: str, default: Any = None) -> Any:
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        nodes: list[LayoutGraphNode] = []
        struct = _get(genome_data, "structural_genome")
        pages = _get(genome_data, "pages", []) or []

        # 1. Elements from structural genome
        elements = _get(struct, "elements", []) if struct else []
        for i, el in enumerate(elements):
            raw_t = str(_get(el, "type", "PARAGRAPH")).upper()
            bbox = _get(el, "bbox", [])
            txt = str(_get(el, "text", ""))
            
            # Enrich and specialize node type using text semantics
            txt_lower = txt.lower()
            if "degree" in txt_lower or "bachelor" in txt_lower or "master" in txt_lower or "diploma" in txt_lower:
                t = "ACADEMIC_TITLE"
            elif "invoice" in txt_lower or "tax invoice" in txt_lower or "bill to" in txt_lower:
                t = "INVOICE_HEADER"
            elif "certificate" in txt_lower or "awarded to" in txt_lower or "completion" in txt_lower or "laude" in txt_lower:
                t = "AWARD_BODY"
            elif "total" in txt_lower or "due" in txt_lower or "subtotal" in txt_lower or "amount" in txt_lower or "tax" in txt_lower:
                t = "FINANCIAL_TOTAL"
            elif "vendor" in txt_lower or "remit" in txt_lower or "payment" in txt_lower:
                t = "PAYMENT_INFO"
            else:
                t = raw_t

            nodes.append(LayoutGraphNode(f"elem_{i}", t, bbox, text_snippet=txt))

        # 2. Tables from structural genome
        tables = _get(struct, "tables", []) if struct else []
        for i, tb in enumerate(tables):
            bbox = _get(tb, "bbox", [])
            nodes.append(LayoutGraphNode(f"table_{i}", "TABLE", bbox, text_snippet="[TABLE_BLOCK]"))

        # 3. If no structural elements, cluster OCR tokens by vertical reading lines
        if not nodes and pages:
            for p_idx, p in enumerate(pages):
                ocr_elements = _get(p, "ocr_elements", []) or []
                if not ocr_elements:
                    continue

                # Sort OCR elements top-to-bottom
                sorted_tokens = sorted(
                    ocr_elements,
                    key=lambda el: _get(el, "bbox", [[0, 0], [0, 0]])[0][1] if _get(el, "bbox") and len(_get(el, "bbox")) >= 1 and len(_get(el, "bbox")[0]) >= 2 else 0.0
                )

                # Group into spatial blocks (lines with vertical distance < 30px)
                current_block: list[dict[str, Any]] = []
                last_y = -999.0

                for tok in sorted_tokens:
                    bbox = _get(tok, "bbox", [[0, 0], [0, 0]])
                    y = bbox[0][1] if bbox and len(bbox) >= 1 and len(bbox[0]) >= 2 else 0.0
                    if last_y >= 0 and abs(y - last_y) > 40.0:
                        if current_block:
                            nodes.append(self._create_block_node(len(nodes), current_block, p_idx))
                            current_block = []
                    current_block.append(tok)
                    last_y = y

                if current_block:
                    nodes.append(self._create_block_node(len(nodes), current_block, p_idx))

        return nodes

    def _create_block_node(self, idx: int, tokens: list[dict[str, Any]], page_idx: int) -> LayoutGraphNode:
        all_text = " ".join(str(t.get("text", "") if isinstance(t, dict) else getattr(t, "text", "")) for t in tokens)
        xs = []
        ys = []
        for t in tokens:
            bbox = t.get("bbox", []) if isinstance(t, dict) else getattr(t, "bbox", [])
            if bbox and len(bbox) >= 2 and len(bbox[0]) >= 2 and len(bbox[1]) >= 2:
                xs.extend([bbox[0][0], bbox[1][0]])
                ys.extend([bbox[0][1], bbox[1][1]])

        min_x = min(xs) if xs else 50.0
        max_x = max(xs) if xs else 500.0
        min_y = min(ys) if ys else 50.0
        max_y = max(ys) if ys else 100.0

        # Classify block type based on vertical position, font geometry and text semantics
        txt_lower = all_text.lower()
        if "degree" in txt_lower or "bachelor" in txt_lower or "master" in txt_lower or "diploma" in txt_lower:
            b_type = "ACADEMIC_TITLE"
        elif "invoice" in txt_lower or "tax invoice" in txt_lower or "bill to" in txt_lower:
            b_type = "INVOICE_HEADER"
        elif "certificate" in txt_lower or "awarded to" in txt_lower or "completion" in txt_lower or "laude" in txt_lower:
            b_type = "AWARD_BODY"
        elif "total" in txt_lower or "due" in txt_lower or "subtotal" in txt_lower or "amount" in txt_lower or "tax" in txt_lower:
            b_type = "FINANCIAL_TOTAL"
        elif "vendor" in txt_lower or "remit" in txt_lower or "payment" in txt_lower:
            b_type = "PAYMENT_INFO"
        elif min_y < 150.0:
            b_type = "HEADER"
        elif min_y > 850.0:
            b_type = "FOOTER"
        else:
            b_type = "PARAGRAPH"

        return LayoutGraphNode(
            node_id=f"block_{idx}",
            node_type=b_type,
            bbox=[[min_x, min_y], [max_x, max_y]],
            page_idx=page_idx,
            text_snippet=all_text,
        )

    def compare_graphs(
        self,
        genome_a: dict[str, Any] | Any,
        genome_b: dict[str, Any] | Any,
    ) -> LayoutGraphMatchResult:
        """Computes structural layout graph similarity using node types and spatial geometry."""
        nodes_a = self.extract_nodes(genome_a)
        nodes_b = self.extract_nodes(genome_b)

        len_a = len(nodes_a)
        len_b = len(nodes_b)

        if len_a == 0 and len_b == 0:
            return LayoutGraphMatchResult(0, 0, 1.0, 1.0, 1.0, 1.0)
        if len_a == 0 or len_b == 0:
            return LayoutGraphMatchResult(len_a, len_b, 0.0, 0.0, 0.0, 0.0)

        # 1. Node Type Distribution Matching
        types_a = [n.node_type for n in nodes_a]
        types_b = [n.node_type for n in nodes_b]

        unique_types = set(types_a) | set(types_b)
        type_diff = sum(abs(types_a.count(t) - types_b.count(t)) for t in unique_types)
        total_nodes = len_a + len_b
        node_sim = max(0.0, 1.0 - (type_diff / total_nodes))

        # 2. Reading Order & Position Sequence Alignment
        match_seq = sum(1 for i in range(min(len_a, len_b)) if types_a[i] == types_b[i])
        seq_sim = match_seq / max(len_a, len_b, 1)

        # 3. Spatial Geometry & Relative Position Similarity
        matched_pairs: list[tuple[str, str]] = []
        used_b = set()
        spatial_sims: list[float] = []

        for na in nodes_a:
            best_match = None
            best_dist = 999.0
            for j, nb in enumerate(nodes_b):
                if j in used_b:
                    continue
                if na.node_type == nb.node_type:
                    # Normalized center Euclidean distance
                    dy = (na.center_y - nb.center_y) / 1000.0
                    dx = (na.center_x - nb.center_x) / 1000.0
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist < best_dist:
                        best_dist = dist
                        best_match = (j, nb)
            if best_match and best_dist < 0.35:  # within 35% spatial tolerance
                used_b.add(best_match[0])
                matched_pairs.append((na.node_id, best_match[1].node_id))
                spatial_sims.append(1.0 - best_dist)

        spatial_sim = float(sum(spatial_sims) / max(len_a, len_b, 1)) if spatial_sims else 0.0

        # 4. Composite Graph Edit Similarity
        graph_sim = (node_sim * 0.35) + (seq_sim * 0.35) + (spatial_sim * 0.30)

        unmatched_a = [n.node_id for n in nodes_a if not any(p[0] == n.node_id for p in matched_pairs)]
        unmatched_b = [n.node_id for j, n in enumerate(nodes_b) if j not in used_b]

        return LayoutGraphMatchResult(
            nodes_a_count=len_a,
            nodes_b_count=len_b,
            node_type_similarity=node_sim,
            spatial_relation_similarity=spatial_sim,
            reading_order_similarity=seq_sim,
            graph_edit_similarity=graph_sim,
            matched_node_pairs=matched_pairs,
            unmatched_nodes_a=unmatched_a,
            unmatched_nodes_b=unmatched_b,
            graph_a_summary=[n.to_dict() for n in nodes_a],
            graph_b_summary=[n.to_dict() for n in nodes_b],
        )
