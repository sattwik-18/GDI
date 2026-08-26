"""SemanticKIEStep pipeline step with Grounded KIE, Qwen2.5-VL escalation, and Arbitration."""

from src.application.context.processing_context import ProcessingContext
from src.application.pipeline.base import PipelineStep
from src.domain.entities.evidence_graph import DocumentEvidenceGraph, EvidenceNode
from src.domain.entities.semantic_genome import SemanticGenome
from src.infrastructure.adapters.qwen_vl_adapter import QwenVisionAdapter
from src.processing.arbitration.inference_arbitrator import InferenceArbitrator
from src.processing.semantic.kie_extractor import GroundedKIEExtractor


class SemanticKIEStep(PipelineStep):
    """Pipeline step: extracts grounded Key-Information entities, escalates to Qwen-VL, and arbitrates."""

    def __init__(self) -> None:
        self._kie_extractor = GroundedKIEExtractor()
        self._qwen_adapter = QwenVisionAdapter()
        self._arbitrator = InferenceArbitrator()

    @property
    def name(self) -> str:
        return "SemanticKIEStep"

    @property
    def version(self) -> str:
        return "2.0.0"

    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        doc_type = (
            context.semantic_genome.taxonomy.primary_type
            if context.semantic_genome
            else "INVOICE"
        )

        # 1. Deterministic fast-path extraction
        entities, relationships = self._kie_extractor.extract_entities(
            ocr_results=context.ocr_results,
            doc_type=doc_type,
        )

        # 2. Qwen2.5-VL Escalation if available and fields are missing/ambiguous
        vlm_entities = {}
        target_fields = ["invoice_number", "issue_date", "total_amount", "vendor_name"]
        missing_fields = [f for f in target_fields if f not in entities]

        if missing_fields and self._qwen_adapter.is_available and context.normalized_pages:
            primary_img = context.normalized_pages[0].image_bytes
            ocr_txt = " ".join(t.text for p in context.ocr_results for t in p.elements)
            vlm_entities = await self._qwen_adapter.extract_grounded_fields(
                image_bytes=primary_img,
                ocr_text=ocr_txt,
                target_schema_fields=missing_fields,
                page_number=1,
            )

        # 3. Model Arbitration
        final_entities, anomaly_signals = self._arbitrator.arbitrate_entities(
            deterministic_entities=entities,
            vlm_entities=vlm_entities,
        )

        has_validation_errors = any(
            not r.is_valid for r in relationships
        ) or any(
            e.validation_status in ["WARNING", "INVALID"] for e in final_entities.values()
        )

        if context.semantic_genome is None:
            context.semantic_genome = SemanticGenome(
                entities=final_entities,
                relationships=relationships,
                has_validation_errors=has_validation_errors,
            )
        else:
            context.semantic_genome.entities = final_entities
            context.semantic_genome.relationships = relationships
            context.semantic_genome.has_validation_errors = has_validation_errors

        # 4. Build Canonical Evidence Graph
        evidence_graph = DocumentEvidenceGraph()
        for key, entity in final_entities.items():
            if entity.provenance:
                evidence_graph.add_node(
                    EvidenceNode(
                        node_id=entity.entity_id,
                        node_type="SEMANTIC_FIELD",
                        page_number=entity.provenance.page_number,
                        bbox=entity.provenance.bounding_box,
                        text=str(entity.value),
                        confidence=entity.confidence,
                        metadata={
                            "field_key": key,
                            "data_type": entity.data_type,
                            "source_tokens": entity.provenance.source_ocr_token_ids,
                            "extraction_method": entity.provenance.extraction_method,
                            "model_version": entity.provenance.model_version,
                        },
                    )
                )

        context.evidence_graph = evidence_graph
        return context
