"""SQLAlchemy ORM Database Models with UUID primary keys and version tracking."""

from datetime import datetime, timezone
import uuid

from sqlalchemy import BIGINT, BOOLEAN, FLOAT, INT, TEXT, VARCHAR, ForeignKey, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.connection import Base


class SchemaVersionModel(Base):
    """Schema version metadata table."""

    __tablename__ = "schema_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version: Mapped[str] = mapped_column(VARCHAR(50), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    release_date: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )
    is_compatible: Mapped[bool] = mapped_column(BOOLEAN, default=True, nullable=False)


class FeatureVersionModel(Base):
    """Feature version metadata table."""

    __tablename__ = "feature_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    extractor_name: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    feature_count: Mapped[int] = mapped_column(INT, nullable=False)
    release_date: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )


class ProcessingVersionModel(Base):
    """Processing engine version metadata table."""

    __tablename__ = "processing_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version: Mapped[str] = mapped_column(VARCHAR(50), nullable=False, unique=True)
    release_date: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )
    description: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    is_compatible: Mapped[bool] = mapped_column(BOOLEAN, default=True, nullable=False)
    migration_notes: Mapped[str | None] = mapped_column(TEXT, nullable=True)


class DocumentModel(Base):
    """Uploaded documents database table."""

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sha256: Mapped[str] = mapped_column(VARCHAR(64), nullable=False, index=True)
    sha3_256: Mapped[str] = mapped_column(VARCHAR(64), nullable=False, index=True)
    mime_type: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BIGINT, nullable=False)
    file_path: Mapped[str] = mapped_column(VARCHAR(512), nullable=False)
    original_filename: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    page_count: Mapped[int] = mapped_column(INT, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    pages: Mapped[list["PageModel"]] = relationship("PageModel", back_populates="document", cascade="all, delete-orphan")
    jobs: Mapped[list["ProcessingJobModel"]] = relationship("ProcessingJobModel", back_populates="document")


class PageModel(Base):
    """Document pages database table."""

    __tablename__ = "pages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_number: Mapped[int] = mapped_column(INT, nullable=False)
    width_px: Mapped[int] = mapped_column(INT, nullable=False)
    height_px: Mapped[int] = mapped_column(INT, nullable=False)
    dpi: Mapped[int] = mapped_column(INT, nullable=False)
    orientation_deg: Mapped[int] = mapped_column(INT, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    document: Mapped["DocumentModel"] = relationship("DocumentModel", back_populates="pages")
    quality_report: Mapped["QualityReportModel"] = relationship("QualityReportModel", back_populates="page", uselist=False)


class ProcessingJobModel(Base):
    """Processing job lifecycle table."""

    __tablename__ = "processing_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    status: Mapped[str] = mapped_column(VARCHAR(50), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    error_details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    document: Mapped["DocumentModel"] = relationship("DocumentModel", back_populates="jobs")
    genome: Mapped["GenomeModel"] = relationship("GenomeModel", back_populates="job", uselist=False)
    metadata_manifest: Mapped["ProcessingMetadataModel"] = relationship("ProcessingMetadataModel", back_populates="job", uselist=False)


class GenomeModel(Base):
    """Canonical document genome storage table."""

    __tablename__ = "genomes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("processing_jobs.id"), nullable=False, unique=True)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
    schema_version: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    pipeline_version: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    feature_version: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    canonical_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    feature_vector: Mapped[list[float]] = mapped_column(ARRAY(FLOAT), nullable=False)
    seal_hash: Mapped[str] = mapped_column(VARCHAR(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    job: Mapped["ProcessingJobModel"] = relationship("ProcessingJobModel", back_populates="genome")


class ProcessingMetadataModel(Base):
    """Processing execution manifest metadata table."""

    __tablename__ = "processing_metadata"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("processing_jobs.id"), nullable=False, unique=True)
    manifest_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    job: Mapped["ProcessingJobModel"] = relationship("ProcessingJobModel", back_populates="metadata_manifest")


class QualityReportModel(Base):
    """Page quality report database table."""

    __tablename__ = "quality_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    page_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pages.id", ondelete="CASCADE"), nullable=False, unique=True)
    blur_score: Mapped[float] = mapped_column(FLOAT, nullable=False)
    sharpness_score: Mapped[float] = mapped_column(FLOAT, nullable=False)
    noise_score: Mapped[float] = mapped_column(FLOAT, nullable=False)
    contrast_score: Mapped[float] = mapped_column(FLOAT, nullable=False)
    report_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    page: Mapped["PageModel"] = relationship("PageModel", back_populates="quality_report")
