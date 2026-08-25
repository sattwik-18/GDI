"""Unit tests for ErrorCatalog."""

import pytest
from src.domain.error_catalog import all_error_codes, get_error_entry, ErrorCategory


class TestErrorCatalog:

    def test_catalog_has_entries(self) -> None:
        codes = all_error_codes()
        assert len(codes) >= 15

    def test_every_entry_has_required_fields(self) -> None:
        for code in all_error_codes():
            entry = get_error_entry(code)
            assert entry is not None
            assert entry.code == code
            assert isinstance(entry.category, ErrorCategory)
            assert 400 <= entry.http_status <= 599
            assert len(entry.description) > 0
            assert len(entry.recommended_action) > 0

    def test_nonexistent_code_returns_none(self) -> None:
        assert get_error_entry("NONEXISTENT_CODE") is None
