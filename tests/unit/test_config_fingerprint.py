"""Unit tests for config fingerprinting."""

import pytest
from src.utils.config_fingerprint import compute_config_fingerprint
from src.config.settings import Settings


class TestConfigFingerprint:

    def test_fingerprint_returns_64_char_sha256(self) -> None:
        fp = compute_config_fingerprint()
        assert isinstance(fp, str)
        assert len(fp) == 64

    def test_fingerprint_changes_on_config_mutation(self) -> None:
        s1 = Settings()
        fp1 = compute_config_fingerprint(s1)

        s2 = Settings()
        s2.ocr.confidence_threshold = 0.99
        fp2 = compute_config_fingerprint(s2)

        assert fp1 != fp2

    def test_fingerprint_identical_for_identical_config(self) -> None:
        s1 = Settings()
        s2 = Settings()
        assert compute_config_fingerprint(s1) == compute_config_fingerprint(s2)
