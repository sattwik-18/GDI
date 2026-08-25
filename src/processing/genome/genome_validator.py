"""GenomeValidator: validates DocumentGenome against the canonical Pydantic schema."""

from src.domain.entities.genome import DocumentGenome
from src.domain.exceptions import GenomeValidationError
from src.schemas.genome_schema import DocumentGenomeSchema, GenomeSealSchema, PageGenomeSchema
from src.schemas.genome_schema import PageMetadataSchema, PageQualityMetricsSchema, ProcessingManifestSchema
import uuid
from datetime import datetime


class GenomeValidator:
    """Validates a DocumentGenome entity against the canonical Pydantic schema."""

    def validate(self, genome: DocumentGenome) -> None:
        """Raises GenomeValidationError if the genome does not satisfy the schema."""
        try:
            # Build minimal Pydantic model for validation
            pages_schemas = []
            for p in genome.pages:
                meta = p.get("metadata", {})
                quality = p.get("quality_metrics")
                pages_schemas.append(
                    PageGenomeSchema(
                        page_number=p["page_number"],
                        metadata=PageMetadataSchema(
                            page_id=uuid.UUID(meta.get("page_id", str(uuid.uuid4()))),
                            width_px=meta.get("width_px", 1),
                            height_px=meta.get("height_px", 1),
                            dpi=meta.get("dpi", 300),
                            orientation_deg=meta.get("orientation_deg", 0),
                            skew_angle_deg=meta.get("skew_angle_deg", 0.0),
                        ),
                        quality_metrics=PageQualityMetricsSchema(**quality) if quality else None,
                        ocr_element_count=p.get("ocr_element_count", 0),
                        layout_region_count=p.get("layout_region_count", 0),
                    )
                )

            manifest_data = genome.processing_manifest or {}
            manifest_schema = ProcessingManifestSchema(
                manifest_id=uuid.UUID(str(manifest_data.get("manifest_id", uuid.uuid4()))),
                job_id=genome.job_id,
                total_duration_ms=manifest_data.get("total_duration_ms", 0.0),
                step_count=manifest_data.get("step_count", 0),
                steps=manifest_data.get("steps", []),
                created_at=manifest_data.get("created_at", genome.created_at),
            )

            DocumentGenomeSchema(
                genome_id=genome.id,
                job_id=genome.job_id,
                document_id=genome.document_id,
                schema_version=genome.schema_version,
                pipeline_version=genome.pipeline_version,
                feature_version=genome.feature_version,
                processing_version=genome.processing_version,
                document_hash_sha256=genome.document_hash_sha256,
                document_hash_sha3_256=genome.document_hash_sha3_256,
                extraction_timestamp=genome.extraction_timestamp,
                processing_duration_ms=genome.processing_duration_ms,
                page_count=genome.page_count,
                pages=pages_schemas,
                feature_vector=genome.feature_vector,
                genome_seal=GenomeSealSchema(
                    feature_count=genome.genome_seal.feature_count,
                    sha256_of_features=genome.genome_seal.sha256_of_features,
                    sealed_at=genome.genome_seal.sealed_at,
                    seal_type=genome.genome_seal.seal_type,
                ),
                processing_manifest=manifest_schema,
            )
        except Exception as exc:
            raise GenomeValidationError(
                message=f"Genome schema validation failed: {str(exc)}",
                details={"error": str(exc)},
            ) from exc
