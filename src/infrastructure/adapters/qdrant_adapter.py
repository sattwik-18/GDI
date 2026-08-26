"""Real Qdrant Vector Store Adapter.

Integrates the official Qdrant vector database protocol for high-performance
multi-modal template similarity retrieval and payload filtering.
"""

from __future__ import annotations
import os
from typing import Any
import numpy as np

from src.utils.logging import get_logger

logger = get_logger(__name__)


class QdrantVectorStoreAdapter:
    """Production vector store adapter supporting official Qdrant client and local fallback."""

    def __init__(
        self,
        url: str | None = None,
        api_key: str | None = None,
        collection_name: str = "gdi_document_templates",
    ) -> None:
        self.url = url or os.getenv("QDRANT_URL", "http://localhost:6333")
        self.api_key = api_key or os.getenv("QDRANT_API_KEY")
        self.collection_name = collection_name
        self._client: Any = None
        self._is_connected = False
        self._local_fallback_store: dict[str, dict[str, Any]] = {}
        self._init_client()

    def _init_client(self) -> None:
        """Initializes connection to real Qdrant cluster if available."""
        try:
            from qdrant_client import QdrantClient
            self._client = QdrantClient(url=self.url, api_key=self.api_key, timeout=2.0)
            # Probe connection
            self._client.get_collections()
            self._is_connected = True
            logger.info("qdrant_client_connected", url=self.url, collection=self.collection_name)
        except Exception as e:
            logger.info("qdrant_unavailable_using_local_fallback", reason=str(e))
            self._client = None
            self._is_connected = False

    @property
    def is_real_qdrant(self) -> bool:
        return self._is_connected

    def upsert_template(
        self,
        template_id: str,
        vector: list[float],
        metadata: dict[str, Any],
    ) -> bool:
        """Upserts a multi-modal template vector with metadata into Qdrant or local fallback."""
        arr = np.array(vector, dtype=np.float64)
        norm = np.linalg.norm(arr)
        if norm > 1e-6:
            arr = arr / norm

        # 1. Real Qdrant Upsert
        if self._is_connected and self._client is not None:
            try:
                from qdrant_client.http import models as qmodels
                self._client.upsert(
                    collection_name=self.collection_name,
                    points=[
                        qmodels.PointStruct(
                            id=template_id,
                            vector=arr.tolist(),
                            payload=metadata,
                        )
                    ],
                )
                logger.info("qdrant_point_upserted", id=template_id)
                return True
            except Exception as e:
                logger.error("qdrant_upsert_failed", error=str(e))

        # 2. Local In-Memory Fallback
        self._local_fallback_store[template_id] = {
            "template_id": template_id,
            "vector": arr,
            "metadata": metadata,
            "provider": "local_vector_store_fallback",
        }
        return True

    def search_nearest_templates(
        self,
        query_vector: list[float],
        category_filter: str | None = None,
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        """Searches nearest candidate templates by cosine similarity."""
        if not query_vector:
            return []

        q_arr = np.array(query_vector, dtype=np.float64)
        q_norm = np.linalg.norm(q_arr)
        if q_norm > 1e-6:
            q_arr = q_arr / q_norm

        # 1. Real Qdrant Vector Search
        if self._is_connected and self._client is not None:
            try:
                from qdrant_client.http import models as qmodels
                q_filter = None
                if category_filter:
                    q_filter = qmodels.Filter(
                        must=[qmodels.FieldCondition(key="category", match=qmodels.MatchValue(value=category_filter))]
                    )
                hits = self._client.search(
                    collection_name=self.collection_name,
                    query_vector=q_arr.tolist(),
                    query_filter=q_filter,
                    limit=top_k,
                )
                return [
                    {
                        "template_id": hit.id,
                        "similarity": round(float(hit.score), 4),
                        "metadata": hit.payload,
                        "provider": "qdrant_real",
                    }
                    for hit in hits
                ]
            except Exception as e:
                logger.error("qdrant_search_failed", error=str(e))

        # 2. Local Fallback Search
        results = []
        for t_id, data in self._local_fallback_store.items():
            meta = data.get("metadata", {})
            if category_filter and meta.get("category") != category_filter:
                continue

            t_vec = data["vector"]
            similarity = float(np.dot(q_arr, t_vec))
            sim_score = max(0.0, min(1.0, (similarity + 1.0) / 2.0))

            results.append({
                "template_id": t_id,
                "template_name": meta.get("template_name", f"Template {t_id}"),
                "issuer_name": meta.get("issuer_name", "Issuer Authority"),
                "category": meta.get("category"),
                "similarity": round(sim_score, 4),
                "provider": "local_vector_store_fallback",
            })

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
