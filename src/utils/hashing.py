"""Cryptographic and hash utility functions."""

import hashlib
from src.domain.value_objects.document_hash import DocumentHash


def compute_document_hashes(content: bytes) -> DocumentHash:
    """Computes SHA-256 and SHA3-256 hashes of a byte payload."""
    sha256_hex = hashlib.sha256(content).hexdigest()
    sha3_256_hex = hashlib.sha3_256(content).hexdigest()
    return DocumentHash(sha256=sha256_hex, sha3_256=sha3_256_hex)


def compute_sha256(content: bytes) -> str:
    """Computes SHA-256 hex string."""
    return hashlib.sha256(content).hexdigest()
