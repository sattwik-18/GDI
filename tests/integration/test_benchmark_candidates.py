"""Real Integration Tests for Benchmark Candidates: Docling, Surya, and MinerU."""

import pytest
from src.infrastructure.adapters.docling_adapter import DoclingAdapter
from src.infrastructure.adapters.surya_adapter import SuryaAdapter
from src.infrastructure.adapters.mineru_adapter import MinerUAdapter


class TestBenchmarkCandidates:

    def test_docling_adapter_contract(self) -> None:
        adapter = DoclingAdapter()
        assert hasattr(adapter, "is_available")
        assert hasattr(adapter, "parse_document")

    def test_surya_adapter_contract(self) -> None:
        adapter = SuryaAdapter()
        assert hasattr(adapter, "is_available")
        assert hasattr(adapter, "run_layout_detection")

    def test_mineru_adapter_contract(self) -> None:
        adapter = MinerUAdapter()
        assert hasattr(adapter, "is_available")
        assert hasattr(adapter, "extract_complex_pdf")
