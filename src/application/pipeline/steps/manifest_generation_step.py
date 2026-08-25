"""ManifestGenerationStep: finalizes the execution log manifest in the genome."""

from datetime import timezone
import uuid

from src.application.context.processing_context import ProcessingContext
from src.application.pipeline.base import PipelineStep
from src.domain.exceptions import ProcessingError


class ManifestGenerationStep(PipelineStep):
    """Pipeline step 17 (final): Attach completed manifest to genome and finalize context."""

    @property
    def name(self) -> str:
        return "ManifestGenerationStep"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        if context.genome is None:
            raise ProcessingError("Cannot generate manifest: genome not assembled.", step_name=self.name)

        steps_data = [
            {
                "step_name": r.step_name,
                "version": r.version,
                "start_timestamp": r.start_timestamp,
                "finish_timestamp": r.finish_timestamp,
                "duration_ms": r.duration_ms,
                "status": r.status,
                "parameters": r.parameters,
                "warnings": r.warnings,
                "exception": r.exception,
            }
            for r in context.step_records
        ]

        manifest_dict = {
            "manifest_id": str(uuid.uuid4()),
            "job_id": str(context.job_id),
            "total_duration_ms": context.processing_manifest.total_duration_ms if context.processing_manifest else 0.0,
            "step_count": len(steps_data),
            "steps": steps_data,
            "created_at": context.start_time.isoformat(),
            "warnings": [{"step": w.step_name, "message": w.message} for w in context.warnings],
        }
        context.genome.processing_manifest = manifest_dict

        return context
