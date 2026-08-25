# GDI Error Catalog Documentation

This directory contains reference documentation for every error code in the **GDI Platform Error Catalog**.

Every error entry guarantees standard fields:
- **Code:** Unique error string (e.g. `ERR_VAL_SIZE_EXCEEDED`)
- **Category:** High-level error domain (`VALIDATION`, `SECURITY`, `PROCESSING`, `OCR`, `GENOME`, `STORAGE`, `DATABASE`, `CONFIGURATION`)
- **HTTP Status:** Standard RFC HTTP status code
- **Description:** Clear explanation of cause
- **Recommended Action:** Remediation steps for client or administrator

---

## Complete Error Reference Table

| Code | Category | HTTP Status | Description | Recommended Action |
|---|---|---|---|---|
| `ERR_VAL_FILE_EMPTY` | `VALIDATION` | 422 | Uploaded file is empty (0 bytes). | Verify the file was correctly attached before submitting. |
| `ERR_VAL_EXTENSION_DENIED` | `VALIDATION` | 400 | File extension is not in the permitted list. | Upload one of: PDF, PNG, JPEG, TIFF, BMP, WebP. |
| `ERR_VAL_MAGIC_BYTES_MISMATCH` | `SECURITY` | 400 | File magic bytes do not match the declared file type. | Ensure the file is not renamed or corrupted. |
| `ERR_VAL_SIZE_EXCEEDED` | `SECURITY` | 413 | Uploaded file exceeds the configured maximum file size. | Compress the document or split it into smaller files. |
| `ERR_VAL_PAGE_LIMIT_EXCEEDED` | `VALIDATION` | 422 | Document page count exceeds the configured maximum. | Split the document and submit pages in smaller batches. |
| `ERR_VAL_DIMENSION_EXCEEDED` | `VALIDATION` | 422 | Image dimensions exceed configured maximum pixel dimensions. | Downscale the image before uploading. |
| `ERR_VAL_PDF_ENCRYPTED` | `VALIDATION` | 422 | PDF is encrypted or password-protected. | Remove password protection before uploading. |
| `ERR_VAL_PDF_MALFORMED` | `VALIDATION` | 422 | PDF file is malformed or corrupted. | Re-export or regenerate the PDF from source document. |
| `ERR_OCR_ENGINE_UNAVAILABLE` | `OCR` | 503 | Configured OCR engine is uninitialized or missing. | Install PaddleOCR or set `DEV_OCR_FALLBACK=true` in dev mode. |
| `ERR_OCR_EXECUTION_FAILED` | `OCR` | 500 | OCR engine raised error during extraction. | Inspect OCR logs and verify image readability. |
| `ERR_PROC_STEP_FAILED` | `PROCESSING` | 500 | Pipeline step raised unrecoverable error. | Inspect server logs for step_name and exception. |
| `ERR_PROC_GENOME_ASSEMBLY_FAILED` | `PROCESSING` | 500 | Genome assembly failed due to missing context data. | Ensure upstream pipeline steps completed successfully. |
| `ERR_GENOME_VALIDATION_FAILED` | `GENOME` | 422 | Assembled genome failed Pydantic schema validation. | Inspect feature extractor outputs and schema fields. |
| `ERR_GENOME_NOT_FOUND` | `GENOME` | 404 | No genome found for given genome_id. | Verify genome_id and processing completion. |
| `ERR_STORE_WRITE_FAILED` | `STORAGE` | 500 | File system write operation failed. | Verify storage root permissions. |
| `ERR_STORE_READ_FAILED` | `STORAGE` | 500 | File system read operation failed. | Verify file existence on disk. |
| `ERR_DB_CONSTRAINT_VIOLATION` | `DATABASE` | 409 | Database operation violated uniqueness constraint. | Avoid duplicate submission of identical documents. |
| `ERR_CFG_INVALID` | `CONFIGURATION` | 500 | Service configuration is invalid or missing fields. | Review .env against .env.example. |
