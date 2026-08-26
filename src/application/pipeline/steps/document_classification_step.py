"""DocumentClassificationStep pipeline step."""

from src.application.context.processing_context import ProcessingContext
from src.application.pipeline.base import PipelineStep
from src.domain.entities.semantic_genome import SemanticGenome
from src.processing.semantic.document_classifier import DocumentClassifier


class DocumentClassificationStep(PipelineStep):
    """Pipeline step: classifies document category taxonomy."""

    def __init__(self) -> None:
        self._classifier = DocumentClassifier()

    @property
    def name(self) -> str:
        return "DocumentClassificationStep"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        taxonomy = self._classifier.classify_document(context.ocr_results)

        if context.semantic_genome is None:
            context.semantic_genome = SemanticGenome(taxonomy=taxonomy)
        else:
            context.semantic_genome.taxonomy = taxonomy

        return context
