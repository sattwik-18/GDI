"""Initial GDI schema with all tables.

Revision ID: 001
Revises:
Create Date: 2026-07-22
"""

from typing import Sequence, Union
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # schema_versions
    op.create_table(
        "schema_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("version", sa.VARCHAR(50), nullable=False, unique=True),
        sa.Column("description", sa.VARCHAR(255), nullable=False),
        sa.Column("release_date", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("is_compatible", sa.BOOLEAN, nullable=False, server_default="true"),
    )

    # feature_versions
    op.create_table(
        "feature_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("version", sa.VARCHAR(50), nullable=False),
        sa.Column("extractor_name", sa.VARCHAR(100), nullable=False),
        sa.Column("feature_count", sa.INTEGER, nullable=False),
        sa.Column("release_date", sa.TIMESTAMP(timezone=True), nullable=False),
    )

    # documents
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("sha256", sa.VARCHAR(64), nullable=False),
        sa.Column("sha3_256", sa.VARCHAR(64), nullable=False),
        sa.Column("mime_type", sa.VARCHAR(100), nullable=False),
        sa.Column("size_bytes", sa.BIGINT, nullable=False),
        sa.Column("file_path", sa.VARCHAR(512), nullable=False),
        sa.Column("original_filename", sa.VARCHAR(255), nullable=False),
        sa.Column("page_count", sa.INTEGER, nullable=False, server_default="1"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )
    op.create_index("ix_documents_sha256", "documents", ["sha256"])
    op.create_index("ix_documents_sha3_256", "documents", ["sha3_256"])

    # pages
    op.create_table(
        "pages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("page_number", sa.INTEGER, nullable=False),
        sa.Column("width_px", sa.INTEGER, nullable=False),
        sa.Column("height_px", sa.INTEGER, nullable=False),
        sa.Column("dpi", sa.INTEGER, nullable=False),
        sa.Column("orientation_deg", sa.INTEGER, nullable=False, server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )

    # processing_jobs
    op.create_table(
        "processing_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("status", sa.VARCHAR(50), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("completed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("error_details", postgresql.JSONB, nullable=True),
    )
    op.create_index("ix_processing_jobs_status", "processing_jobs", ["status"])

    # genomes
    op.create_table(
        "genomes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("processing_jobs.id"), nullable=False, unique=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("schema_version", sa.VARCHAR(50), nullable=False),
        sa.Column("pipeline_version", sa.VARCHAR(50), nullable=False),
        sa.Column("feature_version", sa.VARCHAR(50), nullable=False),
        sa.Column("canonical_json", postgresql.JSONB, nullable=False),
        sa.Column("feature_vector", postgresql.ARRAY(sa.FLOAT), nullable=False),
        sa.Column("seal_hash", sa.VARCHAR(64), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )
    op.create_index("ix_genomes_document_id", "genomes", ["document_id"])

    # processing_metadata
    op.create_table(
        "processing_metadata",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("processing_jobs.id"), nullable=False, unique=True),
        sa.Column("manifest_json", postgresql.JSONB, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )

    # quality_reports
    op.create_table(
        "quality_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("page_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("pages.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("blur_score", sa.FLOAT, nullable=False),
        sa.Column("sharpness_score", sa.FLOAT, nullable=False),
        sa.Column("noise_score", sa.FLOAT, nullable=False),
        sa.Column("contrast_score", sa.FLOAT, nullable=False),
        sa.Column("report_json", postgresql.JSONB, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )

    # Insert initial schema version record
    op.execute(
        """
        INSERT INTO schema_versions (id, version, description, release_date, is_compatible)
        VALUES (gen_random_uuid(), '1.0.0', 'GDI Prototype 1 initial schema', NOW(), true)
        """
    )


def downgrade() -> None:
    op.drop_table("quality_reports")
    op.drop_table("processing_metadata")
    op.drop_table("genomes")
    op.drop_table("processing_jobs")
    op.drop_table("pages")
    op.drop_table("documents")
    op.drop_table("feature_versions")
    op.drop_table("schema_versions")
