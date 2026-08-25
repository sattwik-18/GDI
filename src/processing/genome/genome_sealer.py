"""GenomeSealer: generates SHA-256 soft integrity seal over the feature vector."""

import hashlib
import json
from datetime import datetime, timezone

from src.domain.entities.genome import DocumentGenome, GenomeSeal


class GenomeSealer:
    """Computes a SHA-256 integrity seal over the serialized feature vector.

    seal_type is explicitly 'SHA256_SOFT' to distinguish from the production
    ECDSA P-384 + HSM seal used in the full platform.
    """

    def seal(self, genome: DocumentGenome) -> DocumentGenome:
        """Returns a new genome with a valid SHA-256 soft seal applied."""
        # Deterministic serialization: round to 8 decimal places, sort by value order
        vector_bytes = json.dumps(
            [round(v, 8) for v in genome.feature_vector],
            separators=(",", ":"),
        ).encode("utf-8")

        seal_hash = hashlib.sha256(vector_bytes).hexdigest()

        genome.genome_seal = GenomeSeal(
            feature_count=len(genome.feature_vector),
            sha256_of_features=seal_hash,
            sealed_at=datetime.now(timezone.utc),
            seal_type="SHA256_SOFT",
        )
        return genome
