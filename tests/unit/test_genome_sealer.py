"""Unit tests for GenomeSealer."""

import pytest
import uuid
from datetime import datetime, timezone

from src.domain.entities.genome import DocumentGenome, GenomeSeal
from src.processing.genome.genome_sealer import GenomeSealer


@pytest.fixture
def sample_genome() -> DocumentGenome:
    return DocumentGenome(
        id=uuid.uuid4(),
        job_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        schema_version="1.0.0",
        pipeline_version="1.0.0",
        feature_version="1.0.0",
        processing_version="1.0.0",
        config_fingerprint="test_fingerprint_hash",
        document_hash_sha256="a" * 64,
        document_hash_sha3_256="b" * 64,
        extraction_timestamp=datetime.now(timezone.utc),
        processing_duration_ms=120.0,
        page_count=1,
        pages=[],
        feature_vector=[0.1, 0.2, 0.3, 0.4, 0.5],
        genome_seal=GenomeSeal(feature_count=0, sha256_of_features="0" * 64),
        processing_manifest={},
    )


class TestGenomeSealer:

    def test_seal_populates_sha256(self, sample_genome: DocumentGenome) -> None:
        sealer = GenomeSealer()
        sealed_genome = sealer.seal(sample_genome)

        assert sealed_genome.genome_seal.seal_type == "SHA256_SOFT"
        assert len(sealed_genome.genome_seal.sha256_of_features) == 64
        assert sealed_genome.genome_seal.feature_count == 5

    def test_seal_is_deterministic(self, sample_genome: DocumentGenome) -> None:
        sealer = GenomeSealer()
        g1 = sealer.seal(sample_genome)
        hash1 = g1.genome_seal.sha256_of_features

        g2 = sealer.seal(sample_genome)
        hash2 = g2.genome_seal.sha256_of_features

        assert hash1 == hash2
