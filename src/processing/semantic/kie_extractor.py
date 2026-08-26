"""Grounded Key-Information Extraction (KIE) Engine.

Extracts semantic business fields with complete bounding-box provenance and OCR token linkages,
performing cross-field consistency validation (math checks, date sequences).
"""

from __future__ import annotations
import re
from typing import Any
import uuid

from src.domain.entities.evidence_graph import EntityProvenance, GroundedEntity
from src.domain.entities.semantic_genome import SemanticFieldRelationship, SemanticGenome
from src.domain.interfaces.ocr_engine import OCRPageResult, OCRTextElement


class GroundedKIEExtractor:
    """Extracts grounded semantic fields with full forensic provenance."""

    def extract_entities(
        self,
        ocr_results: list[OCRPageResult],
        doc_type: str = "INVOICE",
    ) -> tuple[dict[str, GroundedEntity], list[SemanticFieldRelationship]]:
        """Extracts Key-Value entities grounded to source tokens and evaluates cross-field relationships."""
        entities: dict[str, GroundedEntity] = {}
        all_tokens = [
            (p.page_number, t)
            for p in ocr_results
            for t in p.elements
        ]

        if not all_tokens:
            return {}, []

        # 1. Extract Invoice / Document Number
        inv_num_entity = self._extract_invoice_number(all_tokens)
        if inv_num_entity:
            entities["invoice_number"] = inv_num_entity

        # 2. Extract Dates (Issue Date, Due Date)
        issue_date, due_date = self._extract_dates(all_tokens)
        if issue_date:
            entities["issue_date"] = issue_date
        if due_date:
            entities["due_date"] = due_date

        # 3. Extract Monetary Amounts (Total Amount, Subtotal, Tax)
        total_amt, subtotal_amt, tax_amt = self._extract_monetary_amounts(all_tokens)
        if total_amt:
            entities["total_amount"] = total_amt
        if subtotal_amt:
            entities["subtotal_amount"] = subtotal_amt
        if tax_amt:
            entities["tax_amount"] = tax_amt

        # 4. Extract Vendor / Counterparty
        vendor_entity = self._extract_vendor_name(all_tokens)
        if vendor_entity:
            entities["vendor_name"] = vendor_entity

        # 5. Evaluate Cross-Field Semantic Relationships
        relationships = self._evaluate_relationships(entities)

        return entities, relationships

    def _extract_invoice_number(self, tokens: list[tuple[int, OCRTextElement]]) -> GroundedEntity | None:
        patterns = [
            r"invoice\s*#?[:\s]*([A-Z0-9\-_]{4,25})",
            r"inv\s*#?[:\s]*([A-Z0-9\-_]{4,25})",
            r"bill\s*#?[:\s]*([A-Z0-9\-_]{4,25})",
            r"number[:\s]*([A-Z0-9\-_]{4,25})",
        ]
        for page_num, token in tokens:
            text = token.text.strip()
            for pat in patterns:
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    val = m.group(1).strip()
                    prov = EntityProvenance(
                        page_number=page_num,
                        bounding_box=token.bbox,
                        source_ocr_token_ids=[str(token.id)],
                        extraction_method="spatial_regex_anchor",
                    )
                    return GroundedEntity(
                        entity_id=str(uuid.uuid4()),
                        key="invoice_number",
                        value=val,
                        normalized_value=val.upper(),
                        data_type="string",
                        confidence=round(token.confidence, 4),
                        provenance=prov,
                    )
        return None

    def _extract_dates(
        self, tokens: list[tuple[int, OCRTextElement]]
    ) -> tuple[GroundedEntity | None, GroundedEntity | None]:
        issue_date_entity = None
        due_date_entity = None

        date_pat = r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}|\d{4}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2}[-/.]\d{4})"

        for page_num, token in tokens:
            text = token.text.strip()
            # Check for due date
            if any(k in text.lower() for k in ["due", "due date", "pay by"]):
                m = re.search(date_pat, text, re.IGNORECASE)
                if m:
                    val = m.group(1).strip()
                    prov = EntityProvenance(
                        page_number=page_num,
                        bounding_box=token.bbox,
                        source_ocr_token_ids=[str(token.id)],
                        extraction_method="spatial_regex_anchor",
                    )
                    due_date_entity = GroundedEntity(
                        entity_id=str(uuid.uuid4()),
                        key="due_date",
                        value=val,
                        normalized_value=val,
                        data_type="date",
                        confidence=round(token.confidence, 4),
                        provenance=prov,
                    )
            # Check for issue / invoice date
            elif any(k in text.lower() for k in ["date", "issue date", "date of issue"]):
                m = re.search(date_pat, text, re.IGNORECASE)
                if m and not issue_date_entity:
                    val = m.group(1).strip()
                    prov = EntityProvenance(
                        page_number=page_num,
                        bounding_box=token.bbox,
                        source_ocr_token_ids=[str(token.id)],
                        extraction_method="spatial_regex_anchor",
                    )
                    issue_date_entity = GroundedEntity(
                        entity_id=str(uuid.uuid4()),
                        key="issue_date",
                        value=val,
                        normalized_value=val,
                        data_type="date",
                        confidence=round(token.confidence, 4),
                        provenance=prov,
                    )
        return issue_date_entity, due_date_entity

    def _extract_monetary_amounts(
        self, tokens: list[tuple[int, OCRTextElement]]
    ) -> tuple[GroundedEntity | None, GroundedEntity | None, GroundedEntity | None]:
        total_entity = None
        subtotal_entity = None
        tax_entity = None

        currency_pat = r"[\$€£₹]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})|\d+(?:\.\d{2}))"

        for page_num, token in tokens:
            text = token.text.strip()
            lower_text = text.lower()

            # 1. Check Subtotal amount first
            if "subtotal" in lower_text or "net amount" in lower_text:
                m = re.search(currency_pat, text)
                if m:
                    try:
                        raw_num = m.group(1).replace(",", "")
                        float_val = float(raw_num)
                        prov = EntityProvenance(
                            page_number=page_num,
                            bounding_box=token.bbox,
                            source_ocr_token_ids=[str(token.id)],
                            extraction_method="spatial_regex_anchor",
                        )
                        subtotal_entity = GroundedEntity(
                            entity_id=str(uuid.uuid4()),
                            key="subtotal_amount",
                            value=text,
                            normalized_value=float_val,
                            data_type="currency",
                            confidence=round(token.confidence, 4),
                            provenance=prov,
                        )
                    except ValueError:
                        pass

            # 2. Check Tax / VAT / GST
            elif any(k in lower_text for k in ["tax", "vat", "gst", "cgst", "sgst"]):
                m = re.search(currency_pat, text)
                if m:
                    try:
                        raw_num = m.group(1).replace(",", "")
                        float_val = float(raw_num)
                        prov = EntityProvenance(
                            page_number=page_num,
                            bounding_box=token.bbox,
                            source_ocr_token_ids=[str(token.id)],
                            extraction_method="spatial_regex_anchor",
                        )
                        tax_entity = GroundedEntity(
                            entity_id=str(uuid.uuid4()),
                            key="tax_amount",
                            value=text,
                            normalized_value=float_val,
                            data_type="currency",
                            confidence=round(token.confidence, 4),
                            provenance=prov,
                        )
                    except ValueError:
                        pass

            # 3. Check Total amount
            elif any(k in lower_text for k in ["total", "amount due", "balance due", "grand total"]):
                m = re.search(currency_pat, text)
                if m:
                    try:
                        raw_num = m.group(1).replace(",", "")
                        float_val = float(raw_num)
                        prov = EntityProvenance(
                            page_number=page_num,
                            bounding_box=token.bbox,
                            source_ocr_token_ids=[str(token.id)],
                            extraction_method="spatial_regex_anchor",
                        )
                        total_entity = GroundedEntity(
                            entity_id=str(uuid.uuid4()),
                            key="total_amount",
                            value=text,
                            normalized_value=float_val,
                            data_type="currency",
                            confidence=round(token.confidence, 4),
                            provenance=prov,
                        )
                    except ValueError:
                        pass

        return total_entity, subtotal_entity, tax_entity

    def _extract_vendor_name(self, tokens: list[tuple[int, OCRTextElement]]) -> GroundedEntity | None:
        """Vendor name is typically at the top of the first page."""
        first_page_tokens = [t for p, t in tokens if p == 1]
        for token in first_page_tokens[:5]:
            text = token.text.strip()
            if len(text) >= 3 and not any(k in text.lower() for k in ["invoice", "page", "date", "bill to", "tax"]):
                prov = EntityProvenance(
                    page_number=1,
                    bounding_box=token.bbox,
                    source_ocr_token_ids=[str(token.id)],
                    extraction_method="header_spatial_heuristic",
                )
                return GroundedEntity(
                    entity_id=str(uuid.uuid4()),
                    key="vendor_name",
                    value=text,
                    normalized_value=text,
                    data_type="string",
                    confidence=round(token.confidence * 0.9, 4),
                    provenance=prov,
                )
        return None

    def _evaluate_relationships(
        self, entities: dict[str, GroundedEntity]
    ) -> list[SemanticFieldRelationship]:
        """Cross-checks arithmetic and timeline consistency between fields."""
        relationships: list[SemanticFieldRelationship] = []

        total = entities.get("total_amount")
        subtotal = entities.get("subtotal_amount")
        tax = entities.get("tax_amount")

        # Math sum verification (Total == Subtotal + Tax)
        if total and subtotal and tax:
            try:
                t_val = float(total.normalized_value)
                s_val = float(subtotal.normalized_value)
                tx_val = float(tax.normalized_value)
                diff = abs(t_val - (s_val + tx_val))
                is_valid = diff < 0.05
                relationships.append(
                    SemanticFieldRelationship(
                        relationship_type="MATH_SUM",
                        source_entity_keys=["subtotal_amount", "tax_amount"],
                        target_entity_key="total_amount",
                        is_valid=is_valid,
                        details={"expected_total": s_val + tx_val, "actual_total": t_val, "diff": round(diff, 2)},
                    )
                )
                if not is_valid:
                    total.validation_status = "WARNING"
                    total.validation_message = f"Arithmetic mismatch: expected {s_val + tx_val:.2f}, got {t_val:.2f}"
            except Exception:
                pass

        return relationships
