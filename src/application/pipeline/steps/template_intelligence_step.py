"""TemplateIntelligenceStep pipeline step."""

from src.application.context.processing_context import ProcessingContext
from src.application.pipeline.base import PipelineStep
from src.processing.template.template_intelligence_engine import TemplateIntelligenceEngine


class TemplateIntelligenceStep(PipelineStep):
    """Pipeline step: evaluates template matching, drift scoring, and forensic anomaly reporting."""

    def __init__(self) -> None:
        self._engine = TemplateIntelligenceEngine()

    @property
    def name(self) -> str:
        return "TemplateIntelligenceStep"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        context.template_genome = self._engine.analyze(
            structural_genome=context.structural_genome,
            semantic_genome=context.semantic_genome,
            visual_genome=context.visual_genome,
        )
        return context
