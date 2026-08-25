"""GenomeValidationStep pipeline step."""

from src.application.context.processing_context import ProcessingContext
from src.application.pipeline.base import PipelineStep
from src.domain.exceptions import ProcessingError
from src.processing.genome.genome_validator import GenomeValidator


class GenomeValidationStep(PipelineStep):
    """Pipeline step 13: Validate assembled genome against canonical Pydantic schema."""

    def __init__(self) -> None:
        self._validator = GenomeValidator()

    @property
    def name(self) -> str:
        return "GenomeValidationStep"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        if context.genome is None:
            raise ProcessingError("Cannot validate genome: genome was not assembled.", step_name=self.name)
        self._validator.validate(context.genome)
        return context
