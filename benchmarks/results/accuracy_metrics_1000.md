# GDI Prototype 1 — Accuracy & Statistical Metrics Report

**Total Documents Evaluated:** 1000  
**Evaluation Duration:** 261.26s  
**Throughput:** 3.83 docs/sec  

---

## 1. Confusion Matrix

| | Predicted Degraded (Positive) | Predicted Clean (Negative) |
|---|---|---|
| **Actual Degraded (Positive)** | **True Positive (TP):** 115 | **False Negative (FN):** 20 |
| **Actual Clean (Negative)** | **False Positive (FP):** 0 | **True Negative (TN):** 865 |

---

## 2. Classification Accuracy Metrics

| Metric | Score | Formula / Notes |
|---|---|---|
| **Accuracy** | **98.00%** | $(TP + TN) / 	ext{Total}$ |
| **Precision** | **1.0000** | $TP / (TP + FP)$ |
| **Recall (Sensitivity)** | **0.8519** | $TP / (TP + FN)$ |
| **F1 Score** | **0.9200** | $2 	imes (	ext{Precision} 	imes 	ext{Recall}) / (	ext{Precision} + 	ext{Recall})$ |
| **False Positive Rate (FPR)** | **0.0000** | $FP / (FP + TN)$ |
| **False Negative Rate (FNR)** | **0.1481** | $FN / (FN + TP)$ |

---

## 3. ROC Curve Coordinates (Receiver Operating Characteristic)

| Threshold | False Positive Rate (FPR) | True Positive Rate (TPR) |
|---|---|---|
| 0.00 | 1.0000 | 1.0000 |
| 0.10 | 0.0000 | 0.7037 |
| 0.20 | 0.0000 | 0.7037 |
| 0.30 | 0.0000 | 0.7037 |
| 0.40 | 0.0000 | 0.7037 |
| 0.50 | 0.0000 | 0.7037 |
| 0.60 | 0.0000 | 0.7037 |
| 0.70 | 0.0000 | 0.7037 |
| 0.80 | 0.0000 | 0.7037 |
| 0.90 | 0.0000 | 0.7037 |
| 1.00 | 0.0000 | 0.0000 |

---

## 4. Genome Integrity & Cryptographic Seal Validation

- **Valid Integrity Seals:** 1000 / 1000
- **Failed Integrity Seals:** 0
- **Pass Rate:** **100.00%**

---

## 5. Performance Latency Profile

- **Mean Processing Time:** 256.50 ms
- **Median ($p_{50}$):** 252.55 ms
- **95th Percentile ($p_{95}$):** 274.12 ms
- **99th Percentile ($p_{99}$):** 430.95 ms
- **Mean Feature Count per Genome:** 94 features
