"""ValidationStep pipeline step."""

from src.application.context.processing_context import ProcessingContext
from src.application.pipeline.base import PipelineStep
from src.security.file_validator import FileSecurityValidator


class ValidationStep(PipelineStep):
    """Pipeline step 1: File security, magic bytes, extension, size, and page validation."""

    def __init__(self) -> None:
        self._validator = FileSecurityValidator()

    @property
    def name(self) -> str:
        return "ValidationStep"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        canonical_ext = self._validator.validate(
            content=context.uploaded_file_bytes,
            filename=context.original_filename,
            mime_type=context.mime_type,
        )
        # Store canonical extension in context
        context.mime_type = f"image/{canonical_ext}" if canonical_ext != "pdf" else "application/pdf"
        return context
