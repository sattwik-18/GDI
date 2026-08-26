"""Canonical ProcessingContext state carrier."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid

from src.domain.entities.document import Document
from src.domain.entities.evidence_graph import DocumentEvidenceGraph
from src.domain.entities.feature_group import FeatureGroup
from src.domain.entities.genome import DocumentGenome
from src.domain.entities.manifest import ManifestStepRecord, ProcessingManifest
from src.domain.entities.page import Page
from src.domain.entities.processing_job import ProcessingJob
from src.domain.entities.quality_report import QualityReport
from src.domain.entities.semantic_genome import SemanticGenome
from src.domain.entities.structural_genome import StructuralElement, StructuralGenome, StructuredTable
from src.domain.entities.template_genome import TemplateGenome
from src.domain.entities.visual_genome import VisualGenome
from src.domain.interfaces.ocr_engine import OCRPageResult


@dataclass
class ProcessingWarning:
    """Processing warning entry."""

    step_name: str
    message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ProcessingErrorDetail:
    """Processing error entry."""

    step_name: str
    message: str
    exception_type: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RenderedPageData:
    """Page rendering result."""

    page_number: int
    image_bytes: bytes
    width_px: int
    height_px: int
    dpi: int
    format: str = "PNG"


@dataclass
class NormalizedPageData:
    """Page normalization result."""

    page_number: int
    image_bytes: bytes
    skew_angle_deg: float = 0.0
    color_space: str = "sRGB"


@dataclass
class LayoutPageResult:
    """Layout analysis output for a page."""

    page_number: int
    regions: list[dict[str, Any]] = field(default_factory=list)
    reading_order: list[str] = field(default_factory=list)


@dataclass
class ProcessingContext:
    """Canonical single-source-of-truth state object during document processing pipeline."""

    request_id: uuid.UUID
    job_id: uuid.UUID
    uploaded_file_bytes: bytes
    original_filename: str
    mime_type: str
    working_directory: str

    document: Document | None = None
    job: ProcessingJob | None = None
    pages: list[Page] = field(default_factory=list)
    rendered_pages: list[RenderedPageData] = field(default_factory=list)
    normalized_pages: list[NormalizedPageData] = field(default_factory=list)
    page_quality_reports: list[QualityReport] = field(default_factory=list)
    ocr_results: list[OCRPageResult] = field(default_factory=list)
    layout_results: list[LayoutPageResult] = field(default_factory=list)
    extracted_feature_groups: list[FeatureGroup] = field(default_factory=list)
    
    # Intelligent Multi-Layer Genome Properties
    structural_elements: list[StructuralElement] = field(default_factory=list)
    extracted_tables: list[StructuredTable] = field(default_factory=list)
    structural_genome: StructuralGenome | None = None
    semantic_genome: SemanticGenome | None = None
    visual_genome: VisualGenome | None = None
    template_genome: TemplateGenome | None = None
    evidence_graph: DocumentEvidenceGraph | None = None

    genome: DocumentGenome | None = None
    serialized_genome_json: str | None = None
    processing_manifest: ProcessingManifest | None = None

    step_records: list[ManifestStepRecord] = field(default_factory=list)
    warnings: list[ProcessingWarning] = field(default_factory=list)
    errors: list[ProcessingErrorDetail] = field(default_factory=list)
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finish_time: datetime | None = None

    @classmethod
    def create(
        cls,
        uploaded_file_bytes: bytes,
        original_filename: str,
        mime_type: str,
        working_directory: str,
    ) -> "ProcessingContext":
        req_id = uuid.uuid4()
        job_id = uuid.uuid4()
        return cls(
            request_id=req_id,
            job_id=job_id,
            uploaded_file_bytes=uploaded_file_bytes,
            original_filename=original_filename,
            mime_type=mime_type,
            working_directory=working_directory,
        )

    def add_warning(self, step_name: str, message: str) -> None:
        self.warnings.append(ProcessingWarning(step_name=step_name, message=message))

    def add_error(self, step_name: str, message: str, exception: Exception) -> None:
        self.errors.append(
            ProcessingErrorDetail(
                step_name=step_name,
                message=message,
                exception_type=type(exception).__name__,
            )
        )
