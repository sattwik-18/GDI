"""Centralized Model Registry for GDI.

Tracks all real AI models, adapters, fallbacks, licenses, hardware requirements,
and deployment statuses across the entire GDI platform.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class IntegrationStatus(str, Enum):
    REAL_INTEGRATION = "REAL_INTEGRATION"
    PARTIAL_INTEGRATION = "PARTIAL_INTEGRATION"
    CUSTOM = "CUSTOM"
    FALLBACK = "FALLBACK"
    BENCHMARK_ONLY = "BENCHMARK_ONLY"
    MISSING = "MISSING"


@dataclass
class ModelMetadata:
    """Metadata specification for every registered model."""

    model_id: str
    model_name: str
    repository_url: str
    version_or_commit: str
    checkpoint_name: str
    license_type: str
    capabilities: list[str]
    device_requirements: str  # "CPU", "CUDA_GPU", "CPU_OR_GPU"
    memory_budget_mb: int
    status: IntegrationStatus
    is_enabled: bool = True
    description: str = ""


class ModelRegistry:
    """Central registry of all models and analytical engines."""

    def __init__(self) -> None:
        self._models: dict[str, ModelMetadata] = {}
        self._register_all_known_models()

    def _register_all_known_models(self) -> None:
        # 1. PP-OCRv4 (PaddleOCR)
        self.register(
            ModelMetadata(
                model_id="paddle_ocr_v4",
                model_name="PaddleOCR PP-OCRv4",
                repository_url="https://github.com/PaddlePaddle/PaddleOCR",
                version_or_commit="2.7.3 / PP-OCRv4",
                checkpoint_name="en_PP-OCRv4_rec / en_PP-OCRv4_det",
                license_type="Apache 2.0",
                capabilities=["text_detection", "text_recognition", "direction_classification"],
                device_requirements="CPU_OR_GPU",
                memory_budget_mb=350,
                status=IntegrationStatus.REAL_INTEGRATION,
                is_enabled=True,
                description="Production OCR engine for raster document images.",
            )
        )

        # 2. PP-StructureV3 (PaddleOCR)
        self.register(
            ModelMetadata(
                model_id="pp_structure_v3",
                model_name="PP-StructureV3 Document Analyzer",
                repository_url="https://github.com/PaddlePaddle/PaddleOCR",
                version_or_commit="2.7.3 / PP-StructureV3",
                checkpoint_name="picodet_lcnet_x1_0_fgd_layout / slanet_mobile",
                license_type="Apache 2.0",
                capabilities=["layout_detection", "table_structure", "reading_order", "document_parsing"],
                device_requirements="CPU_OR_GPU",
                memory_budget_mb=450,
                status=IntegrationStatus.REAL_INTEGRATION,
                is_enabled=True,
                description="Production structural layout and table structure recognition engine.",
            )
        )

        # 3. Microsoft Table Transformer
        self.register(
            ModelMetadata(
                model_id="table_transformer",
                model_name="Microsoft Table Transformer (TATR)",
                repository_url="https://github.com/microsoft/table-transformer",
                version_or_commit="v1.0.0",
                checkpoint_name="microsoft/table-transformer-structure-recognition",
                license_type="MIT",
                capabilities=["table_detection", "cell_recognition", "row_column_decomposition"],
                device_requirements="CPU_OR_GPU",
                memory_budget_mb=650,
                status=IntegrationStatus.PARTIAL_INTEGRATION,
                is_enabled=True,
                description="Specialized DETR-based neural table decomposition adapter.",
            )
        )

        # 4. Meta DINOv2
        self.register(
            ModelMetadata(
                model_id="dinov2_vits14",
                model_name="Meta DINOv2 ViT-S/14",
                repository_url="https://github.com/facebookresearch/dinov2",
                version_or_commit="v1.0.0",
                checkpoint_name="dinov2_vits14",
                license_type="Apache 2.0",
                capabilities=["visual_embedding", "layout_similarity", "visual_clustering"],
                device_requirements="CPU_OR_GPU",
                memory_budget_mb=400,
                status=IntegrationStatus.REAL_INTEGRATION,
                is_enabled=True,
                description="Dense self-supervised Vision Transformer for visual document fingerprinting.",
            )
        )

        # 5. Qwen2.5-VL
        self.register(
            ModelMetadata(
                model_id="qwen2.5_vl",
                model_name="Qwen2.5-VL Vision-Language Model",
                repository_url="https://github.com/QwenLM/Qwen2.5-VL",
                version_or_commit="2.5-VL-7B / 2.5-VL-3B",
                checkpoint_name="Qwen/Qwen2.5-VL-7B-Instruct",
                license_type="Apache 2.0",
                capabilities=["grounded_kie", "visual_reasoning", "document_classification", "ambiguity_arbitration"],
                device_requirements="CUDA_GPU",
                memory_budget_mb=8000,
                status=IntegrationStatus.PARTIAL_INTEGRATION,
                is_enabled=True,
                description="Multimodal VLM escalation layer for high-ambiguity field extraction and grounding.",
            )
        )

        # 6. Qdrant Vector Engine
        self.register(
            ModelMetadata(
                model_id="qdrant_vector_store",
                model_name="Qdrant Vector Database Engine",
                repository_url="https://github.com/qdrant/qdrant",
                version_or_commit="1.11.0",
                checkpoint_name="qdrant/qdrant:latest",
                license_type="Apache 2.0",
                capabilities=["vector_retrieval", "template_clustering", "payload_filtering", "similarity_search"],
                device_requirements="CPU_OR_GPU",
                memory_budget_mb=256,
                status=IntegrationStatus.REAL_INTEGRATION,
                is_enabled=True,
                description="Production-grade vector database provider for multi-modal template matching.",
            )
        )

        # 7. Docling
        self.register(
            ModelMetadata(
                model_id="docling_engine",
                model_name="IBM Docling Document Parser",
                repository_url="https://github.com/docling-project/docling",
                version_or_commit="v2.0.0",
                checkpoint_name="docling-core",
                license_type="MIT",
                capabilities=["document_hierarchy", "provenance_tracking", "complex_pdf_parsing"],
                device_requirements="CPU_OR_GPU",
                memory_budget_mb=600,
                status=IntegrationStatus.BENCHMARK_ONLY,
                is_enabled=False,
                description="Evaluated benchmark candidate for universal PDF parsing.",
            )
        )

        # 8. Surya OCR / Layout
        self.register(
            ModelMetadata(
                model_id="surya_layout_engine",
                model_name="Surya OCR & Layout",
                repository_url="https://github.com/suryatmodulus/surya-ocr",
                version_or_commit="0.4.0",
                checkpoint_name="surya-layout-rec",
                license_type="GPL 3.0",
                capabilities=["reading_order", "layout_analysis", "table_recognition"],
                device_requirements="CPU_OR_GPU",
                memory_budget_mb=700,
                status=IntegrationStatus.BENCHMARK_ONLY,
                is_enabled=False,
                description="Secondary layout validator and disagreement detector candidate.",
            )
        )

        # 9. MinerU
        self.register(
            ModelMetadata(
                model_id="mineru_pdf_engine",
                model_name="OpenDataLab MinerU",
                repository_url="https://github.com/opendatalab/MinerU",
                version_or_commit="v0.8.0",
                checkpoint_name="magic-pdf",
                license_type="Apache 2.0",
                capabilities=["complex_pdf_extraction", "formula_recovery", "academic_paper_parsing"],
                device_requirements="CUDA_GPU",
                memory_budget_mb=2000,
                status=IntegrationStatus.BENCHMARK_ONLY,
                is_enabled=False,
                description="Complex PDF specialist benchmark candidate.",
            )
        )

        # 10. GDI 108-D Forensic Engine (Custom GDI Core)
        self.register(
            ModelMetadata(
                model_id="gdi_forensic_108d",
                model_name="GDI 108-D Mathematical Forensic Feature Engine",
                repository_url="local://gdi/src/processing/extractors",
                version_or_commit="1.0.0",
                checkpoint_name="deterministic_math_v1",
                license_type="Proprietary / GDI",
                capabilities=["geometry_moments", "lbp_glcm_texture", "fft_dct_wavelet_frequency", "statistical_entropy"],
                device_requirements="CPU",
                memory_budget_mb=120,
                status=IntegrationStatus.CUSTOM,
                is_enabled=True,
                description="Core deterministic 108-D mathematical feature extraction engine.",
            )
        )

    def register(self, metadata: ModelMetadata) -> None:
        self._models[metadata.model_id] = metadata

    def get_model(self, model_id: str) -> ModelMetadata | None:
        return self._models.get(model_id)

    def list_models(self) -> list[ModelMetadata]:
        return list(self._models.values())


# Singleton instance
_model_registry = ModelRegistry()


def get_model_registry() -> ModelRegistry:
    return _model_registry
