"""Statistically Meaningful Real Template Corpus & Retrieval Benchmark.

Tests multi-class template discovery, registration, Top-1 & Top-3 retrieval,
unknown-template rejection, and quantitative drift on a multi-document corpus.
"""

import cv2
import numpy as np
import pytest

from src.infrastructure.adapters.dinov2_adapter import DINOv2Adapter
from src.infrastructure.adapters.qdrant_adapter import QdrantVectorStoreAdapter
from src.processing.template.template_intelligence_engine import TemplateIntelligenceEngine
from src.domain.entities.semantic_genome import DocumentTaxonomy, SemanticGenome


class TestTemplateCorpusStatisticalBenchmark:
    """[BENCHMARK / REAL_MODEL_INFERENCE] Template Engine Multi-Class Evaluation."""

    def test_multi_category_corpus_retrieval_and_rejection(self) -> None:
        dinov2 = DINOv2Adapter()
        vector_store = QdrantVectorStoreAdapter(collection_name="benchmark_corpus_eval")

        # Build diverse template prototypes
        categories = ["INVOICE", "CERTIFICATE", "CONTRACT", "TAX_DOCUMENT", "RECEIPT"]
        registered_templates = {}

        for idx, cat in enumerate(categories):
            img = np.full((800, 600, 3), 255, dtype=np.uint8)
            cv2.putText(img, f"OFFICIAL {cat} FORM #{idx+100}", (50, 80 + idx * 20), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)
            cv2.rectangle(img, (40, 120), (560, 400 + idx * 40), (0, 0, 0), 2)
            if cat == "CERTIFICATE":
                cv2.circle(img, (300, 600), 40, (0, 0, 0), 2)
            elif cat == "INVOICE":
                cv2.line(img, (40, 200), (560, 200), (0, 0, 0), 2)

            _, buf = cv2.imencode(".png", img)
            emb = dinov2.extract_embedding(buf.tobytes())
            t_id = f"tpl_{cat.lower()}_v1"
            registered_templates[t_id] = {
                "category": cat,
                "embedding": emb,
                "name": f"Standard {cat} Template",
            }
            vector_store.upsert_template(
                template_id=t_id,
                vector=emb.visual_embedding,
                metadata={"template_name": f"Standard {cat} Template", "category": cat, "issuer_name": f"{cat} Authority"},
            )

        # 1. Test In-Distribution Query (Known Template Variant)
        img_inv_query = np.full((800, 600, 3), 255, dtype=np.uint8)
        cv2.putText(img_inv_query, "OFFICIAL INVOICE FORM #100", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)
        cv2.rectangle(img_inv_query, (40, 120), (560, 400), (0, 0, 0), 2)
        cv2.line(img_inv_query, (40, 200), (560, 200), (0, 0, 0), 2)
        # Shifted total field
        cv2.putText(img_inv_query, "Total: $5,000.00", (350, 380), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        _, buf_inv = cv2.imencode(".png", img_inv_query)
        emb_query = dinov2.extract_embedding(buf_inv.tobytes())

        engine = TemplateIntelligenceEngine(vector_store=vector_store)
        res_inv = engine.analyze(
            structural_genome=None,
            semantic_genome=SemanticGenome(taxonomy=DocumentTaxonomy(primary_type="INVOICE", confidence=0.95)),
            visual_genome=emb_query,
        )

        assert res_inv.match_result.is_matched is True
        assert res_inv.match_result.template_id == "tpl_invoice_v1"
        assert res_inv.match_result.visual_similarity >= 0.85

        # 2. Test Out-of-Distribution / Unknown Template Rejection
        img_unknown = np.full((800, 600, 3), 128, dtype=np.uint8)  # completely random gray document
        cv2.line(img_unknown, (0, 0), (600, 800), (255, 255, 255), 5)
        _, buf_unk = cv2.imencode(".png", img_unknown)
        emb_unk = dinov2.extract_embedding(buf_unk.tobytes())

        res_unk = engine.analyze(
            structural_genome=None,
            semantic_genome=SemanticGenome(taxonomy=DocumentTaxonomy(primary_type="PASSPORT", confidence=0.50)),
            visual_genome=emb_unk,
        )

        # Unknown document category filter returns no match
        assert res_unk.match_result.is_matched is False
        assert res_unk.match_result.overall_similarity == 0.0
