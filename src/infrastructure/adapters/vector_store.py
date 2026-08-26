"""Vector Store and Template Retrieval Adapter.

Provides cosine vector similarity indexing, nearest-template matching, and clustering.
Supports both local in-memory cosine indexing and Qdrant/PostgreSQL vector stores.
"""

from __future__ import annotations
from typing import Any
import numpy as np


class VectorStoreAdapter:
    """Local high-speed cosine vector store for template genomes and document embeddings."""

    def __init__(self) -> None:
        # template_id -> {"vector": np.ndarray, "metadata": dict}
        self._store: dict[str, dict[str, Any]] = {}
        self._init_default_templates()

    def _init_default_templates(self) -> None:
        """Initializes standard baseline forensic template prototypes."""
        # Standard synthetic prototypes for Invoice, Certificate, Degree, Tax
        categories = ["INVOICE", "CERTIFICATE", "DEGREE", "TAX_DOCUMENT", "BANK_STATEMENT"]
        for cat in categories:
            # Seed deterministic pseudo-prototypes
            vec = np.zeros(384, dtype=np.float64)
            seed_val = sum(ord(c) for c in cat)
            np.random.seed(seed_val)
            raw = np.random.randn(384)
            vec = raw / np.linalg.norm(raw)
            self._store[f"tpl_{cat.lower()}_v1"] = {
                "template_id": f"tpl_{cat.lower()}_v1",
                "template_name": f"Standard {cat.replace('_', ' ').title()} Template",
                "issuer_name": "Standard Document Authority",
                "category": cat,
                "version": "1.0.0",
                "vector": vec,
                "created_at": "2026-01-01T00:00:00Z",
            }

    def register_template(
        self,
        template_id: str,
        template_name: str,
        issuer_name: str,
        category: str,
        vector: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Registers a new template vector into the store."""
        arr = np.array(vector, dtype=np.float64)
        norm = np.linalg.norm(arr)
        if norm > 1e-6:
            arr = arr / norm
        self._store[template_id] = {
            "template_id": template_id,
            "template_name": template_name,
            "issuer_name": issuer_name,
            "category": category,
            "version": metadata.get("version", "1.0.0") if metadata else "1.0.0",
            "vector": arr,
            "metadata": metadata or {},
        }

    def search_nearest_template(
        self,
        query_vector: list[float],
        category_filter: str | None = None,
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        """Finds top-k nearest matching templates using cosine similarity."""
        if not self._store or not query_vector:
            return []

        q_arr = np.array(query_vector, dtype=np.float64)
        q_norm = np.linalg.norm(q_arr)
        if q_norm > 1e-6:
            q_arr = q_arr / q_norm

        results = []
        for t_id, data in self._store.items():
            if category_filter and data.get("category") != category_filter:
                continue

            t_vec = data["vector"]
            similarity = float(np.dot(q_arr, t_vec))
            # Bound between 0.0 and 1.0
            sim_score = max(0.0, min(1.0, (similarity + 1.0) / 2.0))

            results.append({
                "template_id": data["template_id"],
                "template_name": data["template_name"],
                "issuer_name": data["issuer_name"],
                "version": data["version"],
                "category": data.get("category"),
                "similarity": round(sim_score, 4),
            })

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
