"""GenomeSerializer: deterministic canonical JSON serialization of a DocumentGenome."""

import json
from datetime import datetime
from typing import Any
import uuid

from src.domain.entities.genome import DocumentGenome


class GenomeSerializer:
    """Deterministic JSON serialization of DocumentGenome.

    Sort keys is True to guarantee identical byte output for identical inputs,
    satisfying Axiom 1: Reproducibility Over Efficiency.
    """

    def serialize(self, genome: DocumentGenome) -> str:
        """Converts DocumentGenome to a canonical, deterministic JSON string."""
        payload = self._genome_to_dict(genome)
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=self._default_encoder)

    def _genome_to_dict(self, genome: DocumentGenome) -> dict[str, Any]:
        return {
            "genome_id": str(genome.id),
            "job_id": str(genome.job_id),
            "document_id": str(genome.document_id),
            "schema_version": genome.schema_version,
            "pipeline_version": genome.pipeline_version,
            "feature_version": genome.feature_version,
            "processing_version": genome.processing_version,
            "document_hash_sha256": genome.document_hash_sha256,
            "document_hash_sha3_256": genome.document_hash_sha3_256,
            "extraction_timestamp": genome.extraction_timestamp.isoformat(),
            "processing_duration_ms": genome.processing_duration_ms,
            "page_count": genome.page_count,
            "pages": genome.pages,  # Already dict-serializable
            "feature_vector": [round(v, 8) for v in genome.feature_vector],
            "genome_seal": {
                "feature_count": genome.genome_seal.feature_count,
                "sha256_of_features": genome.genome_seal.sha256_of_features,
                "sealed_at": genome.genome_seal.sealed_at.isoformat(),
                "seal_type": genome.genome_seal.seal_type,
            },
            "processing_manifest": genome.processing_manifest,
            "created_at": genome.created_at.isoformat(),
        }

    def _default_encoder(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, uuid.UUID):
            return str(obj)
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
