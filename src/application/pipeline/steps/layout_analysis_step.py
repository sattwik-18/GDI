"""LayoutAnalysisStep pipeline step with real PP-StructureV3 integration."""

from src.application.context.processing_context import LayoutPageResult, ProcessingContext
from src.application.pipeline.base import PipelineStep
from src.domain.entities.structural_genome import StructuralGenome
from src.infrastructure.adapters.pp_structure_adapter import PPStructureAdapter


class LayoutAnalysisStep(PipelineStep):
    """Pipeline step: Document layout region detection, reading order recovery, and table parsing."""

    def __init__(self) -> None:
        self._pps_adapter = PPStructureAdapter(table=True, layout=True)

    @property
    def name(self) -> str:
        return "LayoutAnalysisStep"

    @property
    def version(self) -> str:
        return "2.0.0"

    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        layout_results = []
        all_structural_elements = []
        all_tables = []
        all_reading_order = []

        for idx, ocr_res in enumerate(context.ocr_results):
            page_meta = context.pages[idx] if idx < len(context.pages) else None
            pw = page_meta.width_px if page_meta else 2550
            ph = page_meta.height_px if page_meta else 3300

            n_page = context.normalized_pages[idx] if idx < len(context.normalized_pages) else None
            img_bytes = n_page.image_bytes if n_page else b""

            elements, pps_tables, reading_order = self._pps_adapter.analyze_page(
                image_bytes=img_bytes,
                ocr_result=ocr_res,
                page_number=ocr_res.page_number,
                page_width=pw,
                page_height=ph,
            )

            all_structural_elements.extend(elements)
            all_tables.extend(pps_tables)
            all_reading_order.extend(reading_order)

            regions = [
                {
                    "region_id": el.element_id,
                    "region_type": el.element_type,
                    "element_id": el.element_id,
                    "bbox": el.bbox,
                    "text_snippet": el.text[:50],
                    "confidence": el.confidence,
                    "method": el.metadata.get("extraction_method", "pp_structure"),
                }
                for el in elements
            ]
            layout_results.append(
                LayoutPageResult(
                    page_number=ocr_res.page_number,
                    regions=regions,
                    reading_order=reading_order,
                )
            )

        context.layout_results = layout_results
        context.structural_elements = all_structural_elements
        if all_tables:
            context.extracted_tables.extend(all_tables)

        context.structural_genome = StructuralGenome(
            elements=all_structural_elements,
            tables=context.extracted_tables,
            reading_order=all_reading_order,
            total_regions=len(all_structural_elements),
            total_tables=len(context.extracted_tables),
        )
        return context
