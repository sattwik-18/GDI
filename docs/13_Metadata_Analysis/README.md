# Document 13 — Metadata Analysis Engine
## GDI: EXIF, XMP, PDF Metadata, and Provenance Forensics

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [05_Genome_Extraction_Engine], [06_Document_Reconstruction_Engine §2], [26_Security], [27_Cryptography]

---

## Table of Contents

1. [Purpose and Forensic Rationale](#1-purpose-and-forensic-rationale)
2. [Feature Groups and Definitions](#2-feature-groups-and-definitions)
3. [PDF Metadata Analysis](#3-pdf-metadata-analysis)
4. [EXIF Metadata Analysis](#4-exif-metadata-analysis)
5. [XMP Metadata Analysis](#5-xmp-metadata-analysis)
6. [Document Provenance Reconstruction](#6-document-provenance-reconstruction)
7. [Temporal Consistency Analysis](#7-temporal-consistency-analysis)
8. [Software Fingerprinting](#8-software-fingerprinting)
9. [Digital Signature Verification](#9-digital-signature-verification)
10. [Metadata Spoofing Detection](#10-metadata-spoofing-detection)
11. [Implementation](#11-implementation)

---

## 1. Purpose and Forensic Rationale

Document metadata is structured information embedded within the document file that describes its creation, modification history, authorship, and technical provenance. Metadata analysis serves two distinct forensic purposes:

**Direct evidence**: Metadata inconsistencies are direct evidence of manipulation. A PDF that claims to have been created in 2018 but contains metadata referencing PDF specifications introduced in 2022 is internally inconsistent — a clear sign of manipulation or forgery.

**Provenance reconstruction**: Consistent metadata enables the reconstruction of the document's creation pipeline, which can be compared against the claimed provenance.

**Limitations**: Metadata is easily stripped or spoofed. The Metadata Analysis Engine is therefore classified as Level 2 forensic evidence (structural), not Level 1 (cryptographic). Metadata findings are used in conjunction with lower-level physical and rendering forensics, not as standalone evidence.

---

## 2. Feature Groups and Definitions

| Group | Features (std) | Features (deep) | Significance |
|-------|----------------|-----------------|-------------|
| Creation Metadata | 15 | 25 | FS2 (Major) |
| Software Fingerprint | 12 | 15 | FS2 (Major) |
| Modification History | 10 | 15 | FS2 (Major) |
| Device Fingerprint | 8 | 15 | FS2 (Major) |
| **Total** | **45** | **70** | — |

---

## 3. PDF Metadata Analysis

### 3.1 PDF Information Dictionary

PDF documents contain a Document Information Dictionary with standardized fields:

| Field | Description | Forensic Use |
|-------|-------------|-------------|
| Title | Document title | Consistency with declared document type |
| Author | Author name | Organizational attribution |
| Subject | Document subject | Context verification |
| Keywords | Search keywords | Content consistency |
| Creator | Software that created the original source file | Production pipeline reconstruction |
| Producer | PDF producer software that generated the PDF | Technical provenance |
| CreationDate | Date the document was first created (PDF date format) | Temporal consistency |
| ModDate | Date of last modification | Modification history |
| Trapped | Whether the document has been trapped for printing | Production context |

### 3.2 PDF Version and Feature Consistency

PDF documents have a version number (1.0–2.0). GDI verifies:
- Features used in the PDF are supported by the declared version
- The Creator/Producer software's known capabilities are consistent with the declared version
- If the declared version is older than the actual features used: temporal/version inconsistency

**Example inconsistency**: A PDF declaring version 1.3 but using AES-256 encryption (introduced in PDF 1.7) is internally inconsistent.

### 3.3 PDF Feature Inventory

GDI extracts a complete feature inventory from every PDF:

| Feature ID | Description | Significance |
|------------|-------------|-------------|
| `meta.pdf.version` | Declared PDF version | FS2 |
| `meta.pdf.creator_software` | Creator field value | FS2 |
| `meta.pdf.producer_software` | Producer field value | FS2 |
| `meta.pdf.creation_date` | CreationDate timestamp | FS2 |
| `meta.pdf.modification_date` | ModDate timestamp | FS2 |
| `meta.pdf.pages` | Number of pages | FS3 |
| `meta.pdf.linearized` | Whether PDF is linearized | FS2 |
| `meta.pdf.encrypted` | Whether PDF is encrypted | FS2 |
| `meta.pdf.encryption_level` | Encryption algorithm and key length | FS2 |
| `meta.pdf.embedded_files` | Count of embedded file attachments | FS2 |
| `meta.pdf.javascript_present` | Whether JavaScript is present | FS1 |
| `meta.pdf.update_count` | Number of incremental updates | FS2 |
| `meta.pdf.font_count` | Number of embedded fonts | FS3 |
| `meta.pdf.color_profiles` | ICC color profiles embedded | FS2 |
| `meta.pdf.object_count` | Total PDF object count | FS3 |

### 3.4 Incremental Update Analysis

PDF allows incremental updates: new objects are appended to the file without rewriting existing objects, and a new cross-reference table points to both old and new objects. This is used for form filling, digital signatures, and annotations.

**Forensic significance**: The incremental update structure reveals the modification history:
- How many times the document was modified
- What types of objects were added or modified in each update
- Whether the modification pattern is consistent with claimed edits

**Suspicious pattern**: A PDF with a large number of incremental updates where entire page streams have been replaced — this pattern is consistent with content manipulation rather than simple annotation or form-filling.

---

## 4. EXIF Metadata Analysis

For JPEG, TIFF, and other raster format documents, EXIF (Exchangeable Image File Format) metadata is extracted.

### 4.1 Feature Definitions

| Feature ID | Description | Significance |
|------------|-------------|-------------|
| `meta.exif.make` | Camera/scanner manufacturer | FS2 |
| `meta.exif.model` | Camera/scanner model | FS2 |
| `meta.exif.software` | Processing software | FS2 |
| `meta.exif.datetime_original` | Original capture datetime | FS2 |
| `meta.exif.datetime_digitized` | Digitization datetime | FS2 |
| `meta.exif.datetime_modified` | Last modification datetime | FS2 |
| `meta.exif.resolution_x` | Horizontal resolution (DPI) | FS2 |
| `meta.exif.resolution_y` | Vertical resolution (DPI) | FS2 |
| `meta.exif.orientation` | Encoded orientation | FS2 |
| `meta.exif.color_space` | Color space tag | FS2 |
| `meta.exif.exposure_time` | Camera exposure time (for photos) | FS3 |
| `meta.exif.iso` | ISO sensitivity (for photos) | FS3 |
| `meta.exif.focal_length` | Camera focal length | FS3 |
| `meta.exif.gps_lat` | GPS latitude (if present) | FS2 |
| `meta.exif.gps_lon` | GPS longitude (if present) | FS2 |
| `meta.exif.thumbnail_present` | Whether EXIF thumbnail is present | FS2 |
| `meta.exif.thumbnail_hash` | SHA256 of EXIF thumbnail | FS1 |

### 4.2 EXIF Thumbnail Forensics

EXIF thumbnails are small preview images embedded within the EXIF data. In camera-produced images, the thumbnail should be a scaled version of the full image.

**Critical forensic signal**: If the EXIF thumbnail does not match the main image content, this indicates that the main image has been modified after the thumbnail was generated. For example:
- Thumbnail shows original, unmodified content
- Main image shows manipulated content
- The mismatch reveals that the thumbnail was not regenerated after manipulation

This is detected by comparing the content of the EXIF thumbnail against a downscaled version of the full-resolution image.

---

## 5. XMP Metadata Analysis

XMP (Extensible Metadata Platform) is Adobe's schema for embedding rich metadata in files. XMP is embedded in most documents produced by Adobe software (Acrobat, Photoshop, InDesign) and supports editing history.

### 5.1 XMP History Analysis

Adobe applications write the complete editing history into XMP:

```xml
<xmpMM:History>
  <rdf:Seq>
    <rdf:li rdf:parseType="Resource">
      <stEvt:action>created</stEvt:action>
      <stEvt:when>2022-03-15T10:23:45+05:30</stEvt:when>
      <stEvt:softwareAgent>Adobe InDesign 17.2</stEvt:softwareAgent>
    </rdf:li>
    <rdf:li rdf:parseType="Resource">
      <stEvt:action>converted</stEvt:action>
      <stEvt:when>2022-03-15T10:30:12+05:30</stEvt:when>
      <stEvt:softwareAgent>Adobe Acrobat DC 22.001</stEvt:softwareAgent>
    </rdf:li>
  </rdf:Seq>
</xmpMM:History>
```

GDI extracts and parses the complete XMP history, computing:
- Total edit operations
- Software agents involved
- Time intervals between operations (implausibly short intervals are suspicious)
- Consistency of software agent versions with their release dates

### 5.2 Feature Definitions

| Feature ID | Description | Significance |
|------------|-------------|-------------|
| `meta.xmp.history_depth` | Number of history entries | FS2 |
| `meta.xmp.software_agents` | List of software agents in history | FS2 |
| `meta.xmp.creation_software` | Software that created the document | FS2 |
| `meta.xmp.modification_count` | Count of recorded modifications | FS2 |
| `meta.xmp.document_id` | Original document ID (UUID) | FS2 |
| `meta.xmp.instance_id` | Current instance ID (changes on each save) | FS2 |
| `meta.xmp.derivation_source` | Source document reference (for derived docs) | FS2 |
| `meta.xmp.rights` | Copyright/rights information | FS3 |
| `meta.xmp.temporal_consistency_score` | Score for temporal consistency of XMP history | 0–1 | FS1 |

---

## 6. Document Provenance Reconstruction

### 6.1 Provenance Chain

From metadata analysis, GDI reconstructs a **Document Provenance Chain**:

```
Source Document → [creation by Software X] → [conversion by Software Y] → 
[modification by Software Z] → [export to PDF] → [scan by Scanner A] → 
[processed by Software B] → Submitted Document
```

Each step in this chain is associated with:
- Inferred software/device
- Inferred timestamp
- Evidence supporting this inference (metadata fields)
- Confidence level

### 6.2 Consistency Verification

The reconstructed provenance chain is verified for consistency:
1. **Temporal consistency**: Timestamps must be monotonically increasing; future timestamps are invalid
2. **Software version consistency**: Software versions must predate the document creation timestamp
3. **Format consistency**: Each step must produce a format consistent with the next step's input expectations
4. **Capability consistency**: Features in the document must be within the capabilities of the declared creating software version

---

## 7. Temporal Consistency Analysis

### 7.1 Timestamp Hierarchy

Documents often contain multiple timestamps from different sources:
- PDF creation date
- EXIF capture date
- XMP modification dates
- File system timestamps (not forensically reliable)
- Embedded content timestamps (e.g., date printed on the document)

GDI builds a timestamp hierarchy and verifies internal consistency.

### 7.2 Temporal Anomaly Detection

| Anomaly | Description | Significance |
|---------|-------------|-------------|
| Future timestamp | Timestamp is after analysis time | High — document cannot be from the future |
| Inconsistent order | Modification date < Creation date | High — timestamps manipulated |
| Software release date mismatch | Document created by software released after its creation timestamp | High |
| Temporal gap anomaly | Suspicious time gaps between related operations | Medium |
| Timezone inconsistency | Timestamps use different timezones inconsistently | Low |

---

## 8. Software Fingerprinting

### 8.1 Software Signature Database

GDI maintains a database of known software signatures, including:
- Typical metadata patterns for each application and version
- Known bugs and quirks in metadata writing
- Version-specific feature sets

Software fingerprinting identifies the producing software through:
1. Exact match of Creator/Producer fields to known software signatures
2. Pattern matching for software with known metadata formats
3. Inference from document features (format quirks specific to certain software)

The identified software is cross-referenced against its known release date to verify temporal consistency.

### 8.2 Feature Definitions

| Feature ID | Description | Significance |
|------------|-------------|-------------|
| `meta.software.identified_creator` | Identified creator software | FS2 |
| `meta.software.identified_creator_version` | Version of creator software | FS2 |
| `meta.software.creator_release_date` | Known release date of identified version | FS2 |
| `meta.software.identified_producer` | Identified PDF producer software | FS2 |
| `meta.software.version_temporal_inconsistency` | Whether software version postdates creation timestamp | boolean | FS1 |
| `meta.software.signature_confidence` | Confidence of software identification | 0–1 | FS2 |

---

## 9. Digital Signature Verification

For documents containing digital signatures (PDF signatures via PKCS#7/CMS, PAdES):

### 9.1 Signature Verification Steps

1. Extract signature object from PDF (AcroForm field, DocMDP certification)
2. Parse PKCS#7/CMS envelope
3. Verify certificate chain up to trusted root (using system trust store + tenant-configured roots)
4. Verify signature coverage: does the signature cover the entire document or only part of it?
5. Verify that the signed byte range matches the claimed byte range
6. Check for incremental updates after signing (would invalidate signature coverage)
7. Verify timestamp (if counter-signed by a trusted Timestamping Authority)
8. Verify OCSP/CRL revocation status of signing certificate

### 9.2 Feature Definitions

| Feature ID | Description | Significance |
|------------|-------------|-------------|
| `meta.signature.present` | Whether a digital signature is present | FS1 |
| `meta.signature.valid` | Whether signature cryptographically verifies | FS1 |
| `meta.signature.coverage` | Fraction of document covered by signature | FS1 |
| `meta.signature.post_sign_modifications` | Whether modifications occurred after signing | FS1 |
| `meta.signature.certificate_chain_valid` | Whether certificate chain is valid | FS1 |
| `meta.signature.timestamp_valid` | Whether timestamp counter-signature is valid | FS1 |
| `meta.signature.revocation_status` | Certificate revocation status | FS1 |
| `meta.signature.signer_identity` | DN of the signing certificate | FS2 |

**Note**: A valid digital signature is the only L1 (cryptographic) evidence available in document analysis. A document with a valid, unbroken, timestamp-verified signature from a trusted authority provides the highest level of authenticity assurance. However, if no signature is present, GDI falls back to L2–L5 evidence for authenticity determination.

---

## 10. Metadata Spoofing Detection

Metadata is trivially spoofable: any PDF editing tool allows modification of metadata fields. GDI therefore treats metadata as supporting evidence (L2), not primary evidence.

Metadata spoofing detection:
1. **Cross-consistency check**: Metadata claims are cross-referenced against physical characteristics. A document claiming to be from 2018 but showing rendering characteristics of a 2024 font renderer is inconsistent.
2. **Implausible values check**: Timestamps in the future, negative resolutions, non-existent software version numbers.
3. **Missing metadata check**: Legitimate documents from known producing software always have certain metadata fields. Completely empty metadata may indicate stripping (potential evidence concealment).
4. **Template metadata comparison**: The submitted document's metadata structure is compared against the template's. Significant differences in metadata fields present/absent are flagged.

---

## 11. Implementation

| Task | Library | Notes |
|------|---------|-------|
| PDF metadata extraction | PyMuPDF | Full info dict, annots, form fields |
| EXIF extraction | Pillow + exifread | Full EXIF including thumbnail |
| XMP extraction | python-xmp-toolkit | Full XMP DOM parsing |
| Digital signature verification | pyhanko (Py PDF handling) | PAdES/CAdES, TSA verification |
| Certificate chain verification | cryptography (pyca) | X.509 chain validation |
| Software signature database | Custom JSON database | Updated as new software versions release |
| Temporal analysis | dateutil | Timezone-aware datetime handling |

**Processing time**: P50 0.5s, P95 2s per document. Signature verification can add 1–3s (network OCSP/CRL check, cached for 1 hour).

---

*Previous: [12_Noise_Analysis](../12_Noise_Analysis/README.md)*
*Next: [14_Object_Relationship_Graph](../14_Object_Relationship_Graph/README.md)*
*Return to: [Master Index](../README.md)*
