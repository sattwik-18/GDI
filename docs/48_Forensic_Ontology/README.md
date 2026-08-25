# Document 48 — Forensic Ontology
## GDI: Formal Forensic Domain Ontology and Knowledge Graph

**Version:** 2.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Authors:** Principal Architect, Chief Research Engineer, Technical Documentation Lead
**Cross-References:** [00_Project_Vision], [38_Genome_Hierarchy], [40_Reverse_Engineering], [42_Evidence_Model]

---

## Table of Contents

1. [Purpose and Scope](#1-purpose-and-scope)
2. [Ontology Core Architecture (OWL / RDF Specification)](#2-ontology-core-architecture-owl--rdf-specification)
3. [Top-Level Classes and Relationships](#3-top-level-classes-and-relationships)
4. [Forensic Artifact Concepts](#4-forensic-artifact-concepts)
5. [Forgery & Anomaly Concepts](#5-forgery--anomaly-concepts)
6. [Hardware & Software Provenance Concepts](#6-hardware--software-provenance-concepts)
7. [RDF / TURTLE Serialization Example](#7-rdf--turtle-serialization-example)

---

## 1. Purpose and Scope

The **GDI Forensic Ontology** establishes a formal, machine-readable vocabulary and knowledge graph schema for digital and physical document forensics. 

It standardizes forensic concepts across all 10 chromosomes, enabling semantic reasoning, automated evidence classification, and inter-agency evidence exchange using W3C Semantic Web standards (OWL 2, RDF, SHACL).

---

## 2. Ontology Core Architecture (OWL / RDF Specification)

- **IRI Base**: `https://gdi.forensics.ai/ontology/v2/`
- **Prefixes**: `gdi:`, `owl:`, `rdf:`, `rdfs:`, `xsd:`

---

## 3. Top-Level Classes and Relationships

```
                        ┌────────────────────────┐
                        │      gdi:Entity        │
                        └───────────┬────────────┘
                                    │
       ┌────────────────────────────┼────────────────────────────┐
       ▼                            ▼                            ▼
┌──────────────┐             ┌──────────────┐             ┌──────────────┐
│ gdi:Document │             │ gdi:Genome   │             │ gdi:Evidence │
└──────┬───────┘             └──────┬───────┘             └──────┬───────┘
       │                            │                            │
       ▼                            ▼                            ▼
┌──────────────┐             ┌──────────────┐             ┌──────────────┐
│ gdi:Physical │             │ gdi:Chrom    │             │ gdi:Anomaly  │
│ gdi:Digital  │             │ gdi:Gene     │             │ gdi:Verdict  │
└──────────────┘             └──────────────┘             └──────────────┘
```

---

## 4. Forensic Artifact Concepts

- `gdi:Document`: Master entity.
- `gdi:PhysicalDocument`: Tangible document subject to scanning/printing.
- `gdi:DigitalNativeDocument`: Document authored and exported digitally without physical print/scan cycle.
- `gdi:Modality`: Rendered analysis representation (`rgb_300dpi`, `lab_300dpi`, `pdf_vector`).

---

## 5. Forgery & Anomaly Concepts

- `gdi:Forgery`: Superclass for all malicious alterations.
  - `gdi:CharacterSubstitution`: Swapping text glyphs.
  - `gdi:PasteOver`: Physical or digital covering of content.
  - `gdi:GenerativeInpainting`: Synthesizing content via diffusion models.
  - `gdi:ReTypesetting`: Complete re-creation of document layout.

---

## 6. Hardware & Software Provenance Concepts

- `gdi:Provenance`: History of creation.
  - `gdi:AuthoringSoftware`: MS Word, InDesign, LaTeX.
  - `gdi:PDFProducer`: Adobe PDF Library, Quartz, Cairo.
  - `gdi:PrintDevice`: Laser, Inkjet, Thermal.
  - `gdi:AcquisitionDevice`: Flatbed Scanner, Mobile Camera.

---

## 7. RDF / TURTLE Serialization Example

```turtle
@prefix gdi: <https://gdi.forensics.ai/ontology/v2/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

gdi:Evidence_10928 a gdi:Evidence ;
    gdi:extractedFromChromosome gdi:Chr_02_Typography ;
    gdi:hasTrait "typo.kerning.pair_AV" ;
    gdi:hasLikelihoodRatio "0.021"^^xsd:double ;
    gdi:indicatesAnomaly gdi:CharacterSubstitution ;
    gdi:hasEvidenceLevel gdi:Level_3_Statistical .
```

---

*Previous: [47_AI_Expert_Architecture](../47_AI_Expert_Architecture/README.md)*
*Next: [49_Data_Model_Specification](../49_Data_Model_Specification/README.md)*
*Return to: [Master Index](../README.md)*
