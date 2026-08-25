"""GenomeSealingStep pipeline step."""

from src.application.context.processing_context import ProcessingContext
from src.application.pipeline.base import PipelineStep
from src.domain.exceptions import ProcessingError
from src.processing.genome.genome_sealer import GenomeSealer


class GenomeSealingStep(PipelineStep):
    """Pipeline step 14: Generate SHA-256 soft integrity seal on the feature vector."""

    def __init__(self) -> None:
        self._sealer = GenomeSealer()

    @property
    def name(self) -> str:
        return "GenomeSealingStep"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        if context.genome is None:
            raise ProcessingError("Cannot seal genome: genome was not assembled.", step_name=self.name)
        context.genome = self._sealer.seal(context.genome)
        return context
