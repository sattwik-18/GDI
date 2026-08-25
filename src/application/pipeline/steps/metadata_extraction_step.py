"""MetadataExtractionStep pipeline step."""

from src.application.context.processing_context import ProcessingContext
from src.application.pipeline.base import PipelineStep
from src.domain.entities.document import Document
from src.processing.ingestion.metadata_extractor import MetadataExtractor
from src.utils.hashing import compute_document_hashes


class MetadataExtractionStep(PipelineStep):
    """Pipeline step 2: Extract document file hashes, PDF/Image metadata, and create Document entity."""

    def __init__(self) -> None:
        self._extractor = MetadataExtractor()

    @property
    def name(self) -> str:
        return "MetadataExtractionStep"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        hashes = compute_document_hashes(context.uploaded_file_bytes)

        if "pdf" in context.mime_type:
            meta = self._extractor.extract_pdf_metadata(context.uploaded_file_bytes)
        else:
            meta = self._extractor.extract_image_metadata(context.uploaded_file_bytes)

        page_count = meta.get("page_count", 1)

        document = Document.create(
            hashes=hashes,
            mime_type=context.mime_type,
            size_bytes=len(context.uploaded_file_bytes),
            file_path="",  # Populated during storage persistence
            original_filename=context.original_filename,
            page_count=page_count,
        )

        context.document = document
        return context
