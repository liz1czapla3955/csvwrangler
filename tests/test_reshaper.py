"""Tests for csvwrangler.reshaper."""

from __future__ import annotations

import pytest

from csvwrangler.reshaper import melt_rows, unmelt_rows


WIDE_ROWS = [
    {"id": "1", "name": "Alice", "math": "90", "english": "85"},
    {"id": "2", "name": "Bob", "math": "78", "english": "92"},
]

LONG_ROWS = [
    {"id": "1", "name": "Alice", "subject": "math", "score": "90"},
    {"id": "1", "name": "Alice", "subject": "english", "score": "85"},
    {"id": "2", "name": "Bob", "subject": "math", "score": "78"},
    {"id": "2", "name": "Bob", "subject": "english", "score": "92"},
]


def test_melt_rows_basic():
    result = list(melt_rows(WIDE_ROWS, ["id", "name"], ["math", "english"], "subject", "score"))
    assert result == LONG_ROWS


def test_melt_rows_default_column_names():
    result = list(melt_rows(WIDE_ROWS, ["id"], ["math"]))
    assert result[0]["variable"] == "math"
    assert result[0]["value"] == "90"


def test_melt_rows_single_value_var():
    result = list(melt_rows(WIDE_ROWS, ["id", "name"], ["math"], "subject", "score"))
    assert len(result) == 2
    assert all(r["subject"] == "math" for r in result)


def test_melt_rows_missing_value_var_raises():
    with pytest.raises(KeyError, match="nonexistent"):
        list(melt_rows(WIDE_ROWS, ["id"], ["nonexistent"]))


def test_melt_rows_missing_id_var_ignored():
    # id_vars not present in row are silently skipped
    result = list(melt_rows(WIDE_ROWS, ["id", "missing"], ["math"], "subject", "score"))
    assert "missing" not in result[0]
    assert result[0]["id"] == "1"


def test_melt_rows_empty_input():
    result = list(melt_rows([], ["id"], ["math"]))
    assert result == []


def test_unmelt_rows_basic():
    result = unmelt_rows(LONG_ROWS, ["id", "name"], "subject", "score")
    assert len(result) == 2
    alice = next(r for r in result if r["id"] == "1")
    assert alice["math"] == "90"
    assert alice["english"] == "85"
    assert alice["name"] == "Alice"


def test_unmelt_rows_preserves_all_entities():
    result = unmelt_rows(LONG_ROWS, ["id", "name"], "subject", "score")
    ids = {r["id"] for r in result}
    assert ids == {"1", "2"}


def test_unmelt_rows_empty_input():
    result = unmelt_rows([], ["id"], "variable", "value")
    assert result == []


def test_unmelt_rows_single_row():
    rows = [{"id": "1", "variable": "x", "value": "42"}]
    result = unmelt_rows(rows, ["id"], "variable", "value")
    assert result == [{"id": "1", "x": "42"}]


def test_melt_then_unmelt_roundtrip():
    melted = list(melt_rows(WIDE_ROWS, ["id", "name"], ["math", "english"], "subject", "score"))
    restored = unmelt_rows(melted, ["id", "name"], "subject", "score")
    restored_sorted = sorted(restored, key=lambda r: r["id"])
    assert restored_sorted[0]["math"] == "90"
    assert restored_sorted[1]["english"] == "92"
