"""GenomeAssemblyStep pipeline step."""

from src.application.context.processing_context import ProcessingContext
from src.application.pipeline.base import PipelineStep
from src.processing.genome.genome_assembler import GenomeAssembler


class GenomeAssemblyStep(PipelineStep):
    """Pipeline step 12: Assemble DocumentGenome from all extracted FeatureGroups."""

    def __init__(self) -> None:
        self._assembler = GenomeAssembler()

    @property
    def name(self) -> str:
        return "GenomeAssemblyStep"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        context.genome = self._assembler.assemble(context)
        return context
