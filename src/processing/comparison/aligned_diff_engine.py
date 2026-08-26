"""Cross-Document Semantic Field Alignment and Localized Diff Engine.

Aligns semantic fields across document genomes and generates localized structural/textual
differences with precise bounding box coordinates and provenance.
"""

from __future__ import annotations
import uuid
from typing import Any

from src.domain.entities.comparison import LocalizedDifference


class AlignedDiffEngine:
    """Computes semantic field alignment and localized differences between compatible documents."""

    def compute_differences(
        self,
        genome_a: dict[str, Any] | Any,
        genome_b: dict[str, Any] | Any,
    ) -> list[LocalizedDifference]:
        """Aligns semantic fields and structural regions, generating structured differences."""
        def _get(obj: Any, key: str, default: Any = None) -> Any:
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        differences: list[LocalizedDifference] = []

        sem_a = _get(genome_a, "semantic_genome")
        sem_b = _get(genome_b, "semantic_genome")

        entities_a = _get(sem_a, "entities", {}) or {}
        entities_b = _get(sem_b, "entities", {}) or {}

        # 1. Cross-Document Semantic Field Alignment
        all_keys = set(entities_a.keys()) | set(entities_b.keys())
        for key in sorted(all_keys):
            ent_a = entities_a.get(key)
            ent_b = entities_b.get(key)

            if ent_a and ent_b:
                val_a = _get(ent_a, "value")
                val_b = _get(ent_b, "value")
                norm_a = str(_get(ent_a, "normalized_value", val_a)).strip().lower()
                norm_b = str(_get(ent_b, "normalized_value", val_b)).strip().lower()

                if norm_a != norm_b:
                    prov_b = _get(ent_b, "provenance")
                    bbox = _get(prov_b, "bounding_box", []) if prov_b else []
                    page_no = _get(prov_b, "page_number", 1) if prov_b else 1

                    differences.append(
                        LocalizedDifference(
                            diff_id=f"diff_{key}_{uuid.uuid4().hex[:6]}",
                            change_type="VALUE_CHANGED",
                            field_key=key,
                            page_number=page_no,
                            bounding_box=bbox,
                            before_value=val_a,
                            after_value=val_b,
                            confidence=0.98,
                            explanation=f"Field '{key}' value changed from '{val_a}' to '{val_b}'.",
                            evidence_references=[f"sem_{key}_a", f"sem_{key}_b"],
                        )
                    )
            elif ent_a and not ent_b:
                val_a = _get(ent_a, "value")
                differences.append(
                    LocalizedDifference(
                        diff_id=f"diff_{key}_removed_{uuid.uuid4().hex[:6]}",
                        change_type="FIELD_REMOVED",
                        field_key=key,
                        page_number=1,
                        before_value=val_a,
                        after_value=None,
                        confidence=0.95,
                        explanation=f"Field '{key}' ('{val_a}') present in Document A is missing in Document B.",
                    )
                )
            elif ent_b and not ent_a:
                val_b = _get(ent_b, "value")
                prov_b = _get(ent_b, "provenance")
                bbox = _get(prov_b, "bounding_box", []) if prov_b else []
                page_no = _get(prov_b, "page_number", 1) if prov_b else 1

                differences.append(
                    LocalizedDifference(
                        diff_id=f"diff_{key}_added_{uuid.uuid4().hex[:6]}",
                        change_type="FIELD_ADDED",
                        field_key=key,
                        page_number=page_no,
                        bounding_box=bbox,
                        before_value=None,
                        after_value=val_b,
                        confidence=0.95,
                        explanation=f"Field '{key}' ('{val_b}') newly introduced in Document B.",
                    )
                )

        return differences
