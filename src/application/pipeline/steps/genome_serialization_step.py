"""GenomeSerializationStep pipeline step."""

from src.application.context.processing_context import ProcessingContext
from src.application.pipeline.base import PipelineStep
from src.domain.exceptions import ProcessingError
from src.processing.genome.genome_serializer import GenomeSerializer


class GenomeSerializationStep(PipelineStep):
    """Pipeline step 15: Serialize genome to canonical deterministic JSON string."""

    def __init__(self) -> None:
        self._serializer = GenomeSerializer()

    @property
    def name(self) -> str:
        return "GenomeSerializationStep"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        if context.genome is None:
            raise ProcessingError("Cannot serialize genome: genome was not assembled.", step_name=self.name)
        context.serialized_genome_json = self._serializer.serialize(context.genome)
        return context
