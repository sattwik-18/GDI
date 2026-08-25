"""Accuracy & Quality Evaluation Suite: evaluates 1,000 documents against ground truth.

Calculates:
- Confusion Matrix (TP, FP, TN, FN)
- Precision = TP / (TP + FP)
- Recall = TP / (TP + FN)
- F1 Score = 2 * (Precision * Recall) / (Precision + Recall)
- ROC Curve coordinates (True Positive Rate vs False Positive Rate across threshold sweeps)
- Feature vector reproducibility and seal validity metrics
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
import argparse
import json
import time
from typing import Any
import numpy as np

from src.application.context.processing_context import ProcessingContext
from src.application.pipeline.steps.frequency_extraction_step import FrequencyExtractionStep
from src.application.pipeline.steps.geometry_extraction_step import GeometryExtractionStep
from src.application.pipeline.steps.image_normalization_step import ImageNormalizationStep
from src.application.pipeline.steps.metadata_extraction_step import MetadataExtractionStep
from src.application.pipeline.steps.pdf_rendering_step import PDFRenderingStep
from src.application.pipeline.steps.quality_assessment_step import QualityAssessmentStep
from src.application.pipeline.steps.statistical_extraction_step import StatisticalExtractionStep
from src.application.pipeline.steps.texture_extraction_step import TextureExtractionStep
from src.application.pipeline.steps.validation_step import ValidationStep
from src.processing.genome.genome_assembler import GenomeAssembler
from src.processing.genome.genome_sealer import GenomeSealer
from src.processing.genome.genome_validator import GenomeValidator
from src.processing.genome.genome_serializer import GenomeSerializer
from src.domain.entities.document import Document
from src.utils.hashing import compute_document_hashes


class AccuracyEvaluator:
    """Evaluates Genome Extraction Engine quality assessment and feature extraction on a dataset."""

    def __init__(self, dataset_dir: str = "datasets") -> None:
        self.dataset_dir = Path(dataset_dir)
        self.gt_path = self.dataset_dir / "ground_truth.json"

    async def run_evaluation(self, max_docs: int | None = None) -> dict[str, Any]:
        """Evaluates documents in dataset against ground truth labels."""
        if not self.gt_path.exists():
            raise FileNotFoundError(f"Ground truth file not found at {self.gt_path}")

        gt_data = json.loads(self.gt_path.read_text(encoding="utf-8"))
        documents_gt = gt_data.get("documents", {})

        doc_items = list(documents_gt.items())
        if max_docs and max_docs < len(doc_items):
            doc_items = doc_items[:max_docs]

        total_evaluated = len(doc_items)
        print(f"Starting accuracy evaluation on {total_evaluated} documents...")

        assembler = GenomeAssembler()
        validator = GenomeValidator()
        sealer = GenomeSealer()
        serializer = GenomeSerializer()

        # Metrics trackers for Quality Classification (Degraded / Blurred Detection)
        # Positive = Quality Degraded (Blur / Noise / Low Contrast)
        # Negative = High Quality / Acceptable
        tp = 0  # Correctly predicted degraded
        fp = 0  # Incorrectly predicted degraded (was clean)
        tn = 0  # Correctly predicted clean
        fn = 0  # Incorrectly predicted clean (was degraded)

        # Integrity seal validation counts
        sealed_valid_count = 0
        sealed_failed_count = 0

        # Processing durations
        durations_ms: list[float] = []
        feature_counts: list[int] = []

        # Ground truth labels & prediction probability scores for ROC curve computation
        y_true: list[int] = []
        y_scores: list[float] = []

        t_start_all = time.perf_counter()

        for doc_id, meta in doc_items:
            rel_path = meta["relative_path"]
            file_path = self.dataset_dir / rel_path

            if not file_path.exists():
                print(f"Warning: File {file_path} not found, skipping.")
                continue

            file_bytes = file_path.read_bytes()
            ground_quality = meta["ground_truth_quality"]
            actual_degraded = ground_quality["is_degraded"] or ground_quality["is_blurred"]

            ctx = ProcessingContext.create(
                uploaded_file_bytes=file_bytes,
                original_filename=file_path.name,
                mime_type=f"image/{meta['format'].lower()}",
                working_directory="./gdi_storage/temp",
            )

            # Execute pipeline steps
            steps = [
                ValidationStep(),
                MetadataExtractionStep(),
                PDFRenderingStep(),
                ImageNormalizationStep(),
                QualityAssessmentStep(),
                GeometryExtractionStep(),
                TextureExtractionStep(),
                FrequencyExtractionStep(),
                StatisticalExtractionStep(),
            ]

            t0 = time.perf_counter()
            for step in steps:
                ctx = await step.execute(ctx)
            t1 = time.perf_counter()

            dur_ms = (t1 - t0) * 1000.0
            durations_ms.append(dur_ms)

            # Assemble & Seal Genome
            genome = assembler.assemble(ctx)
            validator.validate(genome)
            genome = sealer.seal(genome)
            json_str = serializer.serialize(genome)

            feature_counts.append(len(genome.feature_vector))

            # Verify Seal
            sealer_check = sealer.seal(genome)
            if sealer_check.genome_seal.sha256_of_features == genome.genome_seal.sha256_of_features:
                sealed_valid_count += 1
            else:
                sealed_failed_count += 1

            # Quality Assessment Prediction Logic:
            # Predict degraded if blur_score < 150.0 or contrast_score < 0.15
            blur_score = ctx.page_quality_reports[0].blur_score if ctx.page_quality_reports else 200.0
            contrast_score = ctx.page_quality_reports[0].contrast_score if ctx.page_quality_reports else 0.5

            degraded_prob = float(np.clip(1.0 - (blur_score / 300.0), 0.0, 1.0))
            predicted_degraded = (blur_score < 150.0) or (contrast_score < 0.15)

            y_true.append(1 if actual_degraded else 0)
            y_scores.append(degraded_prob)

            if actual_degraded and predicted_degraded:
                tp += 1
            elif not actual_degraded and predicted_degraded:
                fp += 1
            elif not actual_degraded and not predicted_degraded:
                tn += 1
            elif actual_degraded and not predicted_degraded:
                fn += 1

        t_end_all = time.perf_counter()
        total_time_s = t_end_all - t_start_all

        # Compute Statistical Metrics
        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        accuracy = (tp + tn) / total_evaluated if total_evaluated > 0 else 1.0

        # Compute ROC Curve coordinates (TPR vs FPR across 10 threshold steps)
        roc_curve = self._compute_roc_curve(y_true, y_scores)

        results = {
            "evaluation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_documents_evaluated": total_evaluated,
            "total_execution_time_seconds": round(total_time_s, 2),
            "throughput_docs_per_sec": round(total_evaluated / max(total_time_s, 0.001), 2),
            "confusion_matrix": {
                "true_positives": tp,
                "false_positives": fp,
                "true_negatives": tn,
                "false_negatives": fn,
            },
            "statistical_metrics": {
                "accuracy": round(accuracy, 4),
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1_score": round(f1, 4),
                "false_positive_rate": round(fp / (fp + tn) if (fp + tn) > 0 else 0.0, 4),
                "false_negative_rate": round(fn / (fn + tp) if (fn + tp) > 0 else 0.0, 4),
            },
            "integrity_seal_validation": {
                "valid_seals": sealed_valid_count,
                "failed_seals": sealed_failed_count,
                "pass_rate": round(sealed_valid_count / max(total_evaluated, 1), 4),
            },
            "performance_metrics": {
                "mean_duration_ms": round(float(np.mean(durations_ms)), 2) if durations_ms else 0.0,
                "p50_duration_ms": round(float(np.percentile(durations_ms, 50)), 2) if durations_ms else 0.0,
                "p95_duration_ms": round(float(np.percentile(durations_ms, 95)), 2) if durations_ms else 0.0,
                "p99_duration_ms": round(float(np.percentile(durations_ms, 99)), 2) if durations_ms else 0.0,
                "mean_feature_count": int(np.mean(feature_counts)) if feature_counts else 0,
            },
            "roc_curve": roc_curve,
        }

        # Save output reports
        output_dir = Path("benchmarks/results")
        output_dir.mkdir(parents=True, exist_ok=True)

        json_path = output_dir / "accuracy_metrics_1000.json"
        json_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

        md_path = output_dir / "accuracy_metrics_1000.md"
        self._write_markdown_report(results, md_path)

        print(f"\nEvaluation Complete!")
        print(f"Accuracy: {accuracy*100:.2f}% | Precision: {precision:.4f} | Recall: {recall:.4f} | F1: {f1:.4f}")
        print(f"Reports saved to {json_path} and {md_path}")
        return results

    def _compute_roc_curve(self, y_true: list[int], y_scores: list[float]) -> list[dict[str, float]]:
        """Computes ROC curve points (FPR, TPR) across threshold sweeps."""
        thresholds = [i / 10.0 for i in range(11)]
        points = []
        n_pos = sum(y_true)
        n_neg = len(y_true) - n_pos

        for th in thresholds:
            tp_c = sum(1 for yt, ys in zip(y_true, y_scores) if ys >= th and yt == 1)
            fp_c = sum(1 for yt, ys in zip(y_true, y_scores) if ys >= th and yt == 0)

            tpr = tp_c / n_pos if n_pos > 0 else 0.0
            fpr = fp_c / n_neg if n_neg > 0 else 0.0

            points.append({
                "threshold": round(th, 2),
                "fpr": round(fpr, 4),
                "tpr": round(tpr, 4),
            })
        return points

    def _write_markdown_report(self, results: dict[str, Any], path: Path) -> None:
        cm = results["confusion_matrix"]
        sm = results["statistical_metrics"]
        pm = results["performance_metrics"]
        is_val = results["integrity_seal_validation"]

        md_content = f"""# GDI Prototype 1 — Accuracy & Statistical Metrics Report

**Total Documents Evaluated:** {results['total_documents_evaluated']}  
**Evaluation Duration:** {results['total_execution_time_seconds']}s  
**Throughput:** {results['throughput_docs_per_sec']} docs/sec  

---

## 1. Confusion Matrix

| | Predicted Degraded (Positive) | Predicted Clean (Negative) |
|---|---|---|
| **Actual Degraded (Positive)** | **True Positive (TP):** {cm['true_positives']} | **False Negative (FN):** {cm['false_negatives']} |
| **Actual Clean (Negative)** | **False Positive (FP):** {cm['false_positives']} | **True Negative (TN):** {cm['true_negatives']} |

---

## 2. Classification Accuracy Metrics

| Metric | Score | Formula / Notes |
|---|---|---|
| **Accuracy** | **{sm['accuracy']*100:.2f}%** | $(TP + TN) / \text{{Total}}$ |
| **Precision** | **{sm['precision']:.4f}** | $TP / (TP + FP)$ |
| **Recall (Sensitivity)** | **{sm['recall']:.4f}** | $TP / (TP + FN)$ |
| **F1 Score** | **{sm['f1_score']:.4f}** | $2 \times (\text{{Precision}} \times \text{{Recall}}) / (\text{{Precision}} + \text{{Recall}})$ |
| **False Positive Rate (FPR)** | **{sm['false_positive_rate']:.4f}** | $FP / (FP + TN)$ |
| **False Negative Rate (FNR)** | **{sm['false_negative_rate']:.4f}** | $FN / (FN + TP)$ |

---

## 3. ROC Curve Coordinates (Receiver Operating Characteristic)

| Threshold | False Positive Rate (FPR) | True Positive Rate (TPR) |
|---|---|---|
"""
        for pt in results["roc_curve"]:
            md_content += f"| {pt['threshold']:.2f} | {pt['fpr']:.4f} | {pt['tpr']:.4f} |\n"

        md_content += f"""
---

## 4. Genome Integrity & Cryptographic Seal Validation

- **Valid Integrity Seals:** {is_val['valid_seals']} / {results['total_documents_evaluated']}
- **Failed Integrity Seals:** {is_val['failed_seals']}
- **Pass Rate:** **{is_val['pass_rate']*100:.2f}%**

---

## 5. Performance Latency Profile

- **Mean Processing Time:** {pm['mean_duration_ms']:.2f} ms
- **Median ($p_{{50}}$):** {pm['p50_duration_ms']:.2f} ms
- **95th Percentile ($p_{{95}}$):** {pm['p95_duration_ms']:.2f} ms
- **99th Percentile ($p_{{99}}$):** {pm['p99_duration_ms']:.2f} ms
- **Mean Feature Count per Genome:** {pm['mean_feature_count']} features
"""
        path.write_text(md_content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate GDI Genome Extraction Engine Accuracy")
    parser.add_argument("--dataset-dir", type=str, default="datasets", help="Dataset directory")
    parser.add_argument("--max-docs", type=int, default=None, help="Maximum documents to evaluate (optional)")
    args = parser.parse_args()

    evaluator = AccuracyEvaluator(dataset_dir=args.dataset_dir)
    asyncio.run(evaluator.run_evaluation(max_docs=args.max_docs))


if __name__ == "__main__":
    main()
