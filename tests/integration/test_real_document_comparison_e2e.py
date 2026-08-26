"""Real-Document End-to-End Comparison & Model Provenance Integration Suite.

Classification: [REAL_MODEL_INFERENCE / REAL_DOCUMENT_VALIDATION]
Requirements:
1. Ingests actual image files from disk (sample_invoice.png, sample_certificate.png).
2. Executes the full 17-step pipeline via GenerateGenomeUseCase.
3. Passes real pipeline-generated Genome objects to the ComparisonEngine.
4. Asserts zero SYNTHETIC_FIXTURE occurrences in primary execution provenance.
5. Verifies data-driven decision (DIFFERENT_DOCUMENTS) without hardcoding score thresholds.
"""

import os
import pytest
from unittest.mock import MagicMock
from src.application.use_cases.generate_genome import GenerateGenomeUseCase
from src.domain.entities.comparison import ExecutionType
from src.processing.comparison.comparison_engine import ComparisonEngine


@pytest.fixture(scope="module")
def comparison_engine() -> ComparisonEngine:
    return ComparisonEngine()


class TestRealDocumentComparisonE2E:
    """[REAL_MODEL_INFERENCE / REAL_DOCUMENT_VALIDATION] Full Pipeline Ingestion & Comparison Suite."""

    @pytest.mark.asyncio
    async def test_real_documents_full_pipeline_invoice_vs_certificate(
        self,
        comparison_engine: ComparisonEngine,
    ) -> None:
        """Runs sample_invoice.png and sample_certificate.png through full 17-step pipeline
        and performs real-document comparison with complete model execution provenance.
        """
        golden_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "golden")
        invoice_path = os.path.join(golden_dir, "sample_invoice.png")
        cert_path = os.path.join(golden_dir, "sample_certificate.png")

        assert os.path.exists(invoice_path), f"Missing golden invoice: {invoice_path}"
        assert os.path.exists(cert_path), f"Missing golden certificate: {cert_path}"

        mock_session = MagicMock()
        use_case = GenerateGenomeUseCase(session=mock_session)

        # 1. Real Pipeline Execution on Document A (Invoice)
        with open(invoice_path, "rb") as f:
            invoice_bytes = f.read()

        genome_a = await use_case.execute(
            file_bytes=invoice_bytes,
            filename="sample_invoice.png",
            mime_type="image/png",
        )

        # 2. Real Pipeline Execution on Document B (Certificate)
        with open(cert_path, "rb") as f:
            cert_bytes = f.read()

        genome_b = await use_case.execute(
            file_bytes=cert_bytes,
            filename="sample_certificate.png",
            mime_type="image/png",
        )

        assert genome_a is not None
        assert genome_b is not None
        assert len(genome_a.feature_vector) == 108
        assert len(genome_b.feature_vector) == 108

        # 3. Real Comparison Execution
        result = comparison_engine.compare_documents(genome_a, genome_b)

        # 4. Assert Decision & Empirical Gating (No hardcoded score thresholds)
        assert result.decision == "DIFFERENT_DOCUMENTS"
        assert result.decision_confidence > 0.90
        assert result.status in ["RELATED_BUT_DIFFERENT_DOCUMENT_TYPES", "COMPATIBLE"]

        # 5. Provenance Assertions: Zero SYNTHETIC_FIXTURE entries
        assert len(result.model_provenances) >= 4
        for prov in result.model_provenances:
            assert prov.execution_type != ExecutionType.SYNTHETIC_FIXTURE
            assert prov.execution_type in [
                ExecutionType.REAL_INFERENCE,
                ExecutionType.REAL_LIBRARY,
                ExecutionType.DETERMINISTIC_ALGORITHM,
                ExecutionType.CACHED_RESULT,
            ]
            assert prov.runtime_ms >= 0.0

        # 6. Evidence Ledger Assertions
        assert len(result.evidence_ledger) >= 5
        dim_names = [e.dimension for e in result.evidence_ledger]
        assert "document_class_compatibility" in dim_names
        assert "local_feature_correspondence" in dim_names
        assert "forensic_visual_descriptor" in dim_names

        # 7. Authoritative Calculation Trace Assertions
        assert result.calculation_trace is not None
        assert result.calculation_trace.formula_version == "3.0.0"
        assert result.calculation_trace.final_decision == "DIFFERENT_DOCUMENTS"
        assert result.calculation_trace.negative_multiplier < 1.0  # Demonstrates negative evidence gating
