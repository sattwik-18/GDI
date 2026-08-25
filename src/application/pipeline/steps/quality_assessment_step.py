"""QualityAssessmentStep pipeline step."""

from src.application.context.processing_context import ProcessingContext
from src.application.pipeline.base import PipelineStep
from src.processing.vision.quality_assessor import QualityAssessor


class QualityAssessmentStep(PipelineStep):
    """Pipeline step 5: Assess image quality (blur, sharpness, noise, contrast)."""

    def __init__(self) -> None:
        self._assessor = QualityAssessor()

    @property
    def name(self) -> str:
        return "QualityAssessmentStep"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        quality_reports = []
        for idx, n_page in enumerate(context.normalized_pages):
            page_entity = context.pages[idx] if idx < len(context.pages) else None
            page_id = page_entity.id if page_entity else context.job_id

            report = self._assessor.assess_page(page_id=page_id, image_bytes=n_page.image_bytes)
            quality_reports.append(report)

        context.page_quality_reports = quality_reports
        return context
