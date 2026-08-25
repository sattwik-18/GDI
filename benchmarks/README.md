# GDI Prototype 1 — Benchmark Framework

## Purpose

The benchmark framework measures per-stage latency, memory usage, CPU consumption, and feature extraction throughput across document types.

## Running Benchmarks

```bash
# Run standalone benchmark suite
python benchmarks/run_benchmarks.py
```

## Generated Artifacts

- `benchmarks/results/latest_benchmark.json` — Machine-readable structured benchmark metrics
- `benchmarks/results/latest_benchmark.md` — Human-readable Markdown dashboard

## Measured Metrics

| Metric | Target / Description |
|---|---|
| PDF Rendering | Latency per page at 300 DPI |
| Image Normalization | Deskewing & color transform latency |
| OCR Execution | Text detection & recognition latency |
| Feature Extraction | Latency per extractor (geometry, texture, frequency, statistical) |
| Peak Memory (RSS) | Maximum resident set size memory allocated |
