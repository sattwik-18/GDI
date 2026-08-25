"""Regression test for config fingerprint stability."""

import pytest
from src.utils.config_fingerprint import compute_config_fingerprint
from src.config.settings import Settings


class TestConfigFingerprintStability:

    def test_fingerprint_stable_across_10_calls(self) -> None:
        cfg = Settings()
        hashes = [compute_config_fingerprint(cfg) for _ in range(10)]
        assert len(set(hashes)) == 1, f"Config fingerprint was non-deterministic: {set(hashes)}"
