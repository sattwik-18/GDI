"""PipelineRegistry: configurable assembly of PipelineSteps."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.pipeline.base import PipelineOrchestrator, PipelineStep
from src.application.pipeline.steps.frequency_extraction_step import FrequencyExtractionStep
from src.application.pipeline.steps.genome_assembly_step import GenomeAssemblyStep
from src.application.pipeline.steps.genome_sealing_step import GenomeSealingStep
from src.application.pipeline.steps.genome_serialization_step import GenomeSerializationStep
from src.application.pipeline.steps.genome_validation_step import GenomeValidationStep
from src.application.pipeline.steps.geometry_extraction_step import GeometryExtractionStep
from src.application.pipeline.steps.image_normalization_step import ImageNormalizationStep
from src.application.pipeline.steps.layout_analysis_step import LayoutAnalysisStep
from src.application.pipeline.steps.manifest_generation_step import ManifestGenerationStep
from src.application.pipeline.steps.metadata_extraction_step import MetadataExtractionStep
from src.application.pipeline.steps.ocr_step import OCRStep
from src.application.pipeline.steps.pdf_rendering_step import PDFRenderingStep
from src.application.pipeline.steps.persistence_step import PersistenceStep
from src.application.pipeline.steps.quality_assessment_step import QualityAssessmentStep
from src.application.pipeline.steps.statistical_extraction_step import StatisticalExtractionStep
from src.application.pipeline.steps.texture_extraction_step import TextureExtractionStep
from src.application.pipeline.steps.validation_step import ValidationStep


class PipelineRegistry:
    """Registry managing registered PipelineSteps and building PipelineOrchestrators."""

    def __init__(self) -> None:
        self._steps: list[tuple[int, PipelineStep]] = []

    def register(self, step: PipelineStep, order: int) -> None:
        """Registers a pipeline step with an explicit execution order integer."""
        self._steps.append((order, step))
        # Keep sorted by order integer
        self._steps.sort(key=lambda item: item[0])

    def build_ordered(self) -> list[PipelineStep]:
        """Returns ordered list of PipelineStep instances."""
        return [step for _, step in self._steps]

    def build_orchestrator(self) -> PipelineOrchestrator:
        """Creates a PipelineOrchestrator with all registered steps."""
        return PipelineOrchestrator(steps=self.build_ordered())


def get_default_pipeline_registry(session: AsyncSession) -> PipelineRegistry:
    """Factory building pre-registered 17-step pipeline in canonical order."""
    registry = PipelineRegistry()
    registry.register(ValidationStep(), order=10)
    registry.register(MetadataExtractionStep(), order=20)
    registry.register(PDFRenderingStep(), order=30)
    registry.register(ImageNormalizationStep(), order=40)
    registry.register(QualityAssessmentStep(), order=50)
    registry.register(OCRStep(), order=60)
    registry.register(LayoutAnalysisStep(), order=70)
    registry.register(GeometryExtractionStep(), order=80)
    registry.register(TextureExtractionStep(), order=90)
    registry.register(FrequencyExtractionStep(), order=100)
    registry.register(StatisticalExtractionStep(), order=110)
    registry.register(GenomeAssemblyStep(), order=120)
    registry.register(GenomeValidationStep(), order=130)
    registry.register(GenomeSealingStep(), order=140)
    registry.register(GenomeSerializationStep(), order=150)
    registry.register(PersistenceStep(session), order=160)
    registry.register(ManifestGenerationStep(), order=170)
    return registry
