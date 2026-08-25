# GDI Prototype 1 — Known Limitations & Scope Gaps

## Technical Limitations

1. **OCR Determinism across OS Platforms**
   - Tesseract output varies across Operating System versions and binary builds.
   - For 100% byte-identical reproducibility across environments, **PaddleOCR on Docker/Linux** must be used.

2. **Single-Node Execution**
   - Prototype 1 runs as a single-node application. Distributed worker queues (Celery/Kafka) are reserved for Prototype 2+.

3. **Storage Provider**
   - Only `LocalStorageProvider` is implemented. S3/Blob storage is supported via the `StorageProvider` interface, but concrete cloud providers are not implemented in Prototype 1.

4. **Cryptographic Sealing**
   - Uses `SHA256_SOFT` feature vector hashing. Production ECDSA P-384 hardware security module (HSM) sealing is planned for future versions.

5. **Rate Limiting**
   - API rate limiting middleware is not included in Prototype 1.
