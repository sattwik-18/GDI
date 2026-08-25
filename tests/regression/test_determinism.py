"""Determinism regression tests — same document must produce identical genome seal 10 runs."""

import io
import pytest
import uuid
from datetime import datetime, timezone

from PIL import Image

from src.processing.genome.genome_assembler import GenomeAssembler
from src.processing.genome.genome_sealer import GenomeSealer
from src.processing.genome.genome_serializer import GenomeSerializer
from src.application.context.processing_context import ProcessingContext, NormalizedPageData
from src.domain.entities.page import Page
from src.domain.entities.document import Document
from src.domain.interfaces.ocr_engine import OCRPageResult
from src.processing.extractors.geometry_extractor import GeometryExtractor
from src.processing.extractors.statistical_extractor import StatisticalExtractor
from src.utils.hashing import compute_document_hashes

FIXED_ID = uuid.UUID("12345678-1234-5678-1234-567812345678")
FIXED_JOB_ID = uuid.UUID("87654321-4321-8765-4321-876543218765")
FIXED_TIME = datetime(2026, 7, 22, 12, 0, 0, tzinfo=timezone.utc)


def build_test_context() -> ProcessingContext:
    """Builds a minimal repeatable processing context with deterministic IDs and timestamps."""
    img = Image.new("RGB", (100, 100), color=(42, 85, 127))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    ctx = ProcessingContext(
        request_id=FIXED_ID,
        job_id=FIXED_JOB_ID,
        uploaded_file_bytes=img_bytes,
        original_filename="regression_test.png",
        mime_type="image/png",
        working_directory="./tmp_test",
        start_time=FIXED_TIME,
    )

    page = Page(
        id=FIXED_ID,
        document_id=FIXED_ID,
        page_number=1,
        width_px=100,
        height_px=100,
        dpi=300,
        created_at=FIXED_TIME,
    )
    ctx.pages = [page]

    norm_page = NormalizedPageData(
        page_number=1,
        image_bytes=img_bytes,
        skew_angle_deg=0.0,
        color_space="sRGB",
    )
    ctx.normalized_pages = [norm_page]
    ctx.ocr_results = [
        OCRPageResult(page_number=1, elements=[], mean_confidence=0.0, total_words=0, raw_output={})
    ]
    ctx.layout_results = []

    hashes = compute_document_hashes(img_bytes)
    ctx.document = Document(
        id=FIXED_ID,
        hashes=hashes,
        mime_type="image/png",
        size_bytes=len(img_bytes),
        file_path="./test.png",
        original_filename="regression_test.png",
        created_at=FIXED_TIME,
    )

    return ctx


class TestDeterminism:

    def test_seal_hash_identical_across_10_runs(self) -> None:
        """AXIOM 1 — Reproducibility: Same input must produce identical seal_hash."""
        assembler = GenomeAssembler()
        sealer = GenomeSealer()
        serializer = GenomeSerializer()

        geo_extractor = GeometryExtractor()
        stat_extractor = StatisticalExtractor()

        seal_hashes: list[str] = []
        serialized_jsons: list[str] = []

        for _ in range(10):
            ctx = build_test_context()
            geo_fg = geo_extractor.extract(ctx)
            stat_fg = stat_extractor.extract(ctx)
            # Normalize extraction_time_ms to zero for strict JSON equality test
            geo_fg.extraction_time_ms = 0.0
            stat_fg.extraction_time_ms = 0.0

            ctx.extracted_feature_groups = [geo_fg, stat_fg]

            genome = assembler.assemble(ctx)
            genome.id = FIXED_ID
            genome.created_at = FIXED_TIME
            genome.extraction_timestamp = FIXED_TIME
            genome.processing_duration_ms = 100.0

            genome = sealer.seal(genome)
            genome.genome_seal.sealed_at = FIXED_TIME

            json_str = serializer.serialize(genome)

            seal_hashes.append(genome.genome_seal.sha256_of_features)
            serialized_jsons.append(json_str)

        assert len(set(seal_hashes)) == 1, (
            f"Non-deterministic seal hashes across 10 runs: {set(seal_hashes)}"
        )
        assert len(set(serialized_jsons)) == 1, (
            "Non-deterministic JSON serialization across 10 runs"
        )
