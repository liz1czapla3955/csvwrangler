"""Tests for csvwrangler.renumberer."""

import pytest
from csvwrangler.renumberer import renumber_rows


def _rows(*dicts):
    return list(dicts)


def test_renumber_adds_new_column():
    rows = _rows({"name": "Alice"}, {"name": "Bob"})
    result = list(renumber_rows(rows, column="id"))
    assert result[0]["id"] == "1"
    assert result[1]["id"] == "2"


def test_renumber_custom_start():
    rows = _rows({"x": "a"}, {"x": "b"}, {"x": "c"})
    result = list(renumber_rows(rows, column="n", start=10))
    assert [r["n"] for r in result] == ["10", "11", "12"]


def test_renumber_custom_step():
    rows = _rows({"x": "a"}, {"x": "b"}, {"x": "c"})
    result = list(renumber_rows(rows, column="n", start=0, step=5))
    assert [r["n"] for r in result] == ["0", "5", "10"]


def test_renumber_negative_step():
    rows = _rows({"x": "a"}, {"x": "b"}, {"x": "c"})
    result = list(renumber_rows(rows, column="n", start=100, step=-10))
    assert [r["n"] for r in result] == ["100", "90", "80"]


def test_renumber_overwrites_existing_column():
    rows = _rows({"id": "old", "v": "1"}, {"id": "also_old", "v": "2"})
    result = list(renumber_rows(rows, column="id", overwrite=True))
    assert result[0]["id"] == "1"
    assert result[1]["id"] == "2"


def test_renumber_no_overwrite_skips_non_empty():
    rows = _rows({"id": "keep", "v": "a"}, {"id": "", "v": "b"}, {"id": "also_keep", "v": "c"})
    result = list(renumber_rows(rows, column="id", start=1, overwrite=False))
    # counter still advances even when skipped
    assert result[0]["id"] == "keep"
    assert result[1]["id"] == "2"
    assert result[2]["id"] == "also_keep"


def test_renumber_empty_input():
    result = list(renumber_rows([], column="id"))
    assert result == []


def test_renumber_preserves_other_columns():
    rows = _rows({"a": "hello", "b": "world"})
    result = list(renumber_rows(rows, column="idx"))
    assert result[0]["a"] == "hello"
    assert result[0]["b"] == "world"
    assert result[0]["idx"] == "1"


def test_renumber_single_row():
    rows = _rows({"val": "x"})
    result = list(renumber_rows(rows, column="seq", start=42, step=7))
    assert result[0]["seq"] == "42"
