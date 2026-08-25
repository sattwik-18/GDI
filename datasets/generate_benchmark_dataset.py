"""Benchmark Dataset Generator: creates 1,000 synthetic and variation documents with ground-truth labels."""

import argparse
import io
import json
import os
import random
from pathlib import Path
from typing import Any
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


# Supported categories
CATEGORIES = [
    "certificates",
    "degrees",
    "transcripts",
    "invoices",
    "forms",
    "synthetic_clean",
    "synthetic_perturbed",
]

# Random seed for exact dataset reproducibility
RANDOM_SEED = 42


class BenchmarkDatasetGenerator:
    """Generates synthetic documents and variations with ground-truth metadata."""

    def __init__(self, output_dir: str = "datasets") -> None:
        self.output_dir = Path(output_dir)
        random.seed(RANDOM_SEED)
        np.random.seed(RANDOM_SEED)

    def generate(self, total_count: int = 1000) -> dict[str, Any]:
        """Generates total_count documents across categories and creates ground_truth.json."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        for cat in CATEGORIES:
            (self.output_dir / cat).mkdir(parents=True, exist_ok=True)

        ground_truth: dict[str, Any] = {
            "dataset_version": "1.0.0",
            "total_documents": total_count,
            "seed": RANDOM_SEED,
            "documents": {},
        }

        # Category distribution
        counts = {
            "certificates": int(total_count * 0.15),
            "degrees": int(total_count * 0.15),
            "transcripts": int(total_count * 0.15),
            "invoices": int(total_count * 0.15),
            "forms": int(total_count * 0.15),
            "synthetic_clean": int(total_count * 0.15),
            "synthetic_perturbed": total_count - (int(total_count * 0.15) * 6),
        }

        global_idx = 1
        for cat, count in counts.items():
            print(f"Generating {count} documents for category '{cat}'...")
            for idx in range(1, count + 1):
                doc_id = f"doc_{global_idx:04d}"
                rel_path, meta = self._generate_document(cat, doc_id, global_idx)
                ground_truth["documents"][doc_id] = meta
                global_idx += 1

        gt_path = self.output_dir / "ground_truth.json"
        gt_path.write_text(json.dumps(ground_truth, indent=2), encoding="utf-8")
        print(f"Generated {total_count} documents. Ground truth saved to {gt_path}")
        return ground_truth

    def _generate_document(self, category: str, doc_id: str, index: int) -> tuple[str, dict[str, Any]]:
        width, height = 850, 1100  # Standard letter proportions
        img = Image.new("RGB", (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        # Draw generic document layout elements
        # Header banner
        header_color = (
            random.randint(20, 80),
            random.randint(50, 120),
            random.randint(100, 200),
        )
        draw.rectangle([40, 40, width - 40, 120], fill=header_color)
        draw.text((60, 65), f"OFFICIAL DOCUMENT: {category.upper()} #{index:04d}", fill=(255, 255, 255))

        # Body text lines (simulated document content)
        y_pos = 160
        text_snippets = []
        for line_idx in range(15):
            line_text = f"Section {line_idx+1}: Verification record item {index:04d}-{line_idx+1:02d} for GDI platform benchmark evaluation."
            draw.text((60, y_pos), line_text, fill=(30, 30, 30))
            text_snippets.append(line_text)
            y_pos += 45

        # Footer block
        draw.rectangle([40, height - 80, width - 40, height - 40], fill=(240, 240, 240))
        draw.text((60, height - 65), f"ID: {doc_id} | Security Hash Placeholder", fill=(100, 100, 100))

        # Ground truth initial metadata
        is_degraded = False
        is_blurred = False
        is_noisy = False
        is_skewed = False
        skew_angle = 0.0
        is_tampered = False
        format_ext = "png"

        # Apply Category-specific perturbations
        if category == "synthetic_perturbed":
            perturb_type = index % 5
            if perturb_type == 0:  # Blur
                img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(2.5, 4.5)))
                is_degraded = True
                is_blurred = True
            elif perturb_type == 1:  # Skew
                skew_angle = float(random.choice([-5, -3, 3, 5, 8]))
                img = img.rotate(skew_angle, expand=False, fillcolor=(255, 255, 255))
                is_skewed = True
            elif perturb_type == 2:  # Noise
                arr = np.array(img)
                noise = np.random.normal(0, 25, arr.shape).astype(np.int16)
                noisy_arr = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)
                img = Image.fromarray(noisy_arr)
                is_degraded = True
                is_noisy = True
            elif perturb_type == 3:  # Low contrast
                arr = np.array(img).astype(np.float32)
                arr = arr * 0.4 + 100.0  # Compress dynamic range
                img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
                is_degraded = True
            elif perturb_type == 4:  # Tampered content flag
                is_tampered = True
        elif category in ("invoices", "forms") and index % 4 == 0:
            # Subtle degradation on 25% of real-world categories
            img = img.filter(ImageFilter.GaussianBlur(radius=1.5))
            is_degraded = True

        # Select file format
        formats = ["png", "jpg", "webp"]
        format_ext = formats[index % len(formats)]
        filename = f"{doc_id}.{format_ext}"
        rel_path = str(Path(category) / filename)
        full_path = self.output_dir / rel_path

        # Save file
        if format_ext == "jpg":
            img.save(full_path, format="JPEG", quality=85)
        elif format_ext == "webp":
            img.save(full_path, format="WEBP", quality=85)
        else:
            img.save(full_path, format="PNG")

        metadata = {
            "doc_id": doc_id,
            "category": category,
            "relative_path": rel_path,
            "format": format_ext.upper(),
            "width_px": width,
            "height_px": height,
            "page_count": 1,
            "ground_truth_quality": {
                "is_acceptable": not (is_blurred and not is_degraded),
                "is_degraded": is_degraded,
                "is_blurred": is_blurred,
                "is_noisy": is_noisy,
                "is_skewed": is_skewed,
                "skew_angle_deg": skew_angle,
                "is_tampered": is_tampered,
            },
            "ground_truth_text": text_snippets,
        }

        return rel_path, metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate GDI Benchmark Dataset")
    parser.add_argument("--count", type=int, default=1000, help="Total document count to generate")
    parser.add_argument("--output-dir", type=str, default="datasets", help="Output directory")
    args = parser.parse_args()

    gen = BenchmarkDatasetGenerator(output_dir=args.output_dir)
    gen.generate(total_count=args.count)


if __name__ == "__main__":
    main()
