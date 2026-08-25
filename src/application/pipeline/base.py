"""PipelineStep abstract base class and PipelineOrchestrator."""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
import time
import psutil

from src.application.context.processing_context import ProcessingContext
from src.domain.entities.manifest import ManifestStepRecord, ProcessingManifest
from src.utils.logging import bind_correlation_context, clear_correlation_context, get_logger

logger = get_logger(__name__)


class PipelineStep(ABC):
    """Abstract base class for a single document processing pipeline step."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique step name identifier."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Step implementation version."""
        pass

    @abstractmethod
    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        """Executes step logic, updating context in-place."""
        pass


class PipelineOrchestrator:
    """Executes an ordered list of PipelineSteps sequentially over a ProcessingContext."""

    def __init__(self, steps: list[PipelineStep]) -> None:
        self._steps = steps

    async def run(self, context: ProcessingContext) -> ProcessingContext:
        """Runs all pipeline steps in sequence, building the execution manifest."""
        bind_correlation_context(
            request_id=str(context.request_id),
            job_id=str(context.job_id),
        )

        logger.info(
            "pipeline_started",
            job_id=str(context.job_id),
            step_count=len(self._steps),
        )

        overall_start = time.perf_counter()
        proc = psutil.Process()

        for step in self._steps:
            step_name = step.name
            step_version = step.version
            start_iso = datetime.now(timezone.utc).isoformat()
            step_start = time.perf_counter()

            bind_correlation_context(pipeline_stage=step_name)

            # Pre-step resource measurement
            try:
                cpu_before = proc.cpu_percent(interval=None)
                mem_before = proc.memory_info().rss / (1024 * 1024)
            except Exception:
                cpu_before = 0.0
                mem_before = 0.0

            logger.info("step_execution_started", job_id=str(context.job_id), step=step_name)

            status = "SUCCESS"
            exception_msg = None

            # Generate input summary based on step
            input_summary = {
                "uploaded_size_bytes": len(context.uploaded_file_bytes),
                "rendered_page_count": len(context.rendered_pages),
                "feature_group_count": len(context.extracted_feature_groups),
            }

            try:
                context = await step.execute(context)
            except Exception as e:
                status = "FAILED"
                exception_msg = f"{type(e).__name__}: {str(e)}"
                context.add_error(step_name, str(e), e)
                logger.error(
                    "step_execution_failed",
                    job_id=str(context.job_id),
                    step=step_name,
                    error=str(e),
                )
                raise

            finally:
                duration_ms = (time.perf_counter() - step_start) * 1000.0
                finish_iso = datetime.now(timezone.utc).isoformat()

                # Post-step resource measurement
                try:
                    cpu_after = proc.cpu_percent(interval=None)
                    mem_after = proc.memory_info().rss / (1024 * 1024)
                except Exception:
                    cpu_after = 0.0
                    mem_after = 0.0

                output_summary = {
                    "rendered_pages": len(context.rendered_pages),
                    "normalized_pages": len(context.normalized_pages),
                    "feature_groups": len(context.extracted_feature_groups),
                    "has_genome": context.genome is not None,
                }

                step_warnings = [
                    w.message for w in context.warnings if w.step_name == step_name
                ]

                record = ManifestStepRecord(
                    step_name=step_name,
                    version=step_version,
                    start_timestamp=start_iso,
                    finish_timestamp=finish_iso,
                    duration_ms=round(duration_ms, 2),
                    status=status,
                    parameters={},
                    configuration={},
                    input_summary=input_summary,
                    output_summary=output_summary,
                    cpu_percent=round(max(cpu_before, cpu_after), 1),
                    memory_rss_mb=round(mem_after, 2),
                    peak_memory_mb=round(max(mem_before, mem_after), 2),
                    retry_count=0,
                    warnings=step_warnings,
                    exception=exception_msg,
                )
                context.step_records.append(record)

                logger.info(
                    "step_execution_finished",
                    job_id=str(context.job_id),
                    step=step_name,
                    duration_ms=round(duration_ms, 2),
                    status=status,
                    memory_rss_mb=round(mem_after, 2),
                )

        total_duration_ms = (time.perf_counter() - overall_start) * 1000.0
        context.finish_time = datetime.now(timezone.utc)
        context.processing_manifest = ProcessingManifest.create(
            job_id=context.job_id,
            total_duration_ms=round(total_duration_ms, 2),
            steps=context.step_records,
        )

        logger.info(
            "pipeline_completed",
            job_id=str(context.job_id),
            total_duration_ms=round(total_duration_ms, 2),
        )

        clear_correlation_context()
        return context
