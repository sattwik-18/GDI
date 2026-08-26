"""Real Integration Test: Qdrant Vector Store Adapter.

Validates that Qdrant adapter correctly upserts multi-modal template vectors and executes
nearest-neighbor cosine similarity queries with payload filtering.
"""

import pytest
import numpy as np

from src.infrastructure.adapters.qdrant_adapter import QdrantVectorStoreAdapter


class TestQdrantRealIntegration:

    def test_qdrant_upsert_and_similarity_retrieval(self) -> None:
        adapter = QdrantVectorStoreAdapter(collection_name="test_gdi_templates")

        vec_a = [0.1] * 384
        adapter.upsert_template(
            template_id="tpl_invoice_acme_v1",
            vector=vec_a,
            metadata={"template_name": "ACME Standard Invoice", "issuer_name": "ACME Corp", "category": "INVOICE"},
        )

        vec_b = [0.8] * 384
        adapter.upsert_template(
            template_id="tpl_degree_oxford_v1",
            vector=vec_b,
            metadata={"template_name": "Oxford Degree", "issuer_name": "Oxford", "category": "DEGREE"},
        )

        # Query with vec_a
        results = adapter.search_nearest_templates(query_vector=vec_a, category_filter="INVOICE", top_k=1)
        assert len(results) >= 1
        assert results[0]["template_id"] == "tpl_invoice_acme_v1"
        assert results[0]["similarity"] >= 0.95
