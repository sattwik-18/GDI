"""Metadata extraction for files, PDFs, and images."""

import io
from typing import Any
from PIL import Image
import fitz  # PyMuPDF


class MetadataExtractor:
    """Extracts document and image metadata headers."""

    def extract_pdf_metadata(self, content: bytes) -> dict[str, Any]:
        """Extracts PDF document metadata using PyMuPDF."""
        doc = fitz.open(stream=content, filetype="pdf")
        meta = doc.metadata or {}
        page_count = doc.page_count
        first_page = doc[0] if page_count > 0 else None
        width = first_page.rect.width if first_page else 0
        height = first_page.rect.height if first_page else 0

        pdf_ver = "1.4"
        if isinstance(meta, dict) and meta.get("format"):
            fmt = meta.get("format", "")
            if "PDF" in fmt:
                pdf_ver = fmt.replace("PDF", "").strip() or "1.4"

        metadata = {
            "format": "PDF",
            "page_count": page_count,
            "pdf_version": pdf_ver,
            "title": meta.get("title", ""),
            "author": meta.get("author", ""),
            "subject": meta.get("subject", ""),
            "keywords": meta.get("keywords", ""),
            "creator": meta.get("creator", ""),
            "producer": meta.get("producer", ""),
            "creation_date": meta.get("creationDate", ""),
            "modification_date": meta.get("modDate", ""),
            "first_page_width_pt": float(width),
            "first_page_height_pt": float(height),
            "is_encrypted": doc.is_encrypted,
        }
        doc.close()
        return metadata

    def extract_image_metadata(self, content: bytes) -> dict[str, Any]:
        """Extracts image format, DPI, color mode, and EXIF metadata."""
        img = Image.open(io.BytesIO(content))
        dpi_val = img.info.get("dpi", (300, 300))
        dpi = int(dpi_val[0]) if isinstance(dpi_val, tuple) else int(dpi_val)

        exif_data = {}
        if hasattr(img, "_getexif") and img._getexif():
            try:
                raw_exif = img._getexif()
                if raw_exif:
                    for k, v in raw_exif.items():
                        if isinstance(v, (int, float, str)):
                            exif_data[str(k)] = v
            except Exception:
                pass

        return {
            "format": img.format or "IMAGE",
            "page_count": getattr(img, "n_frames", 1),
            "width_px": img.width,
            "height_px": img.height,
            "color_mode": img.mode,
            "dpi": dpi if dpi > 0 else 300,
            "exif": exif_data,
        }
