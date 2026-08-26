"""TableExtractionStep pipeline step with Table Transformer and Arbitrator."""

from src.application.context.processing_context import ProcessingContext
from src.application.pipeline.base import PipelineStep
from src.infrastructure.adapters.table_transformer_adapter import TableTransformerAdapter
from src.processing.arbitration.inference_arbitrator import InferenceArbitrator


class TableExtractionStep(PipelineStep):
    """Pipeline step: extracts structured table matrices, cells, and tokens using Table Transformer."""

    def __init__(self) -> None:
        self._tatr_adapter = TableTransformerAdapter()
        self._arbitrator = InferenceArbitrator()

    @property
    def name(self) -> str:
        return "TableExtractionStep"

    @property
    def version(self) -> str:
        return "2.0.0"

    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        all_tables = list(context.extracted_tables)  # from PP-Structure if any

        for idx, n_page in enumerate(context.normalized_pages):
            ocr_res = context.ocr_results[idx] if idx < len(context.ocr_results) else None
            if not ocr_res:
                continue

            # Confidence Routing: Only execute Table Transformer if PP-Structure detected a table
            # candidate or if OCR tokens exhibit tabular spatial alignment (>= 3 columns)
            has_table_candidate = (
                any(el.element_type == "TABLE" for el in context.structural_elements if el.page_number == n_page.page_number)
                or any(t.page_number == n_page.page_number for t in context.extracted_tables)
            )

            if not has_table_candidate and not self._has_tabular_token_alignment(ocr_res):
                continue

            # Run Table Transformer when table candidate exists
            tatr_tables = self._tatr_adapter.extract_tables(
                image_bytes=n_page.image_bytes,
                ocr_result=ocr_res,
                page_number=n_page.page_number,
            )

            # Arbitrate between existing PP-Structure tables and Table Transformer
            if tatr_tables:
                all_tables = self._arbitrator.arbitrate_tables(
                    pps_tables=context.extracted_tables,
                    tatr_tables=tatr_tables,
                    fallback_tables=[],
                )

        context.extracted_tables = all_tables
        if context.structural_genome:
            context.structural_genome.tables = all_tables
            context.structural_genome.total_tables = len(all_tables)

        return context

    def _has_tabular_token_alignment(self, ocr_res) -> bool:
        """Lightweight spatial heuristic checking for 3+ horizontally aligned column clusters."""
        if not ocr_res or len(ocr_res.elements) < 6:
            return False
        # Check for multiple distinct X-coordinates in roughly the same Y-band
        y_buckets: dict[int, list[float]] = {}
        for elem in ocr_res.elements:
            if elem.bbox:
                mid_y = int((elem.bbox[0][1] + elem.bbox[2][1]) / 2 // 30)
                mid_x = (elem.bbox[0][0] + elem.bbox[1][0]) / 2
                y_buckets.setdefault(mid_y, []).append(mid_x)
        return any(len(xs) >= 3 for xs in y_buckets.values())
