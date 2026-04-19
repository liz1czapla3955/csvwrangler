"""Tests for csvwrangler.deduper (column-level consecutive deduplication)."""
import csv
import io
import pytest
from csvwrangler.deduper import dedup_column_rows, dedup_column_file


def _rows(*dicts):
    return list(dicts)


def test_dedup_column_rows_blanks_repeat():
    rows = [
        {"a": "x", "b": "1"},
        {"a": "x", "b": "2"},
        {"a": "y", "b": "2"},
    ]
    result = list(dedup_column_rows(rows, ["a"]))
    assert result[0]["a"] == "x"
    assert result[1]["a"] == ""
    assert result[2]["a"] == "y"


def test_dedup_column_rows_preserves_other_columns():
    rows = [
        {"a": "x", "b": "1"},
        {"a": "x", "b": "2"},
    ]
    result = list(dedup_column_rows(rows, ["a"]))
    assert result[0]["b"] == "1"
    assert result[1]["b"] == "2"


def test_dedup_column_rows_multiple_columns():
    rows = [
        {"a": "x", "b": "1"},
        {"a": "x", "b": "1"},
        {"a": "x", "b": "2"},
    ]
    result = list(dedup_column_rows(rows, ["a", "b"]))
    assert result[1]["a"] == ""
    assert result[1]["b"] == ""
    assert result[2]["a"] == ""
    assert result[2]["b"] == "2"


def test_dedup_column_rows_non_consecutive_not_blanked():
    rows = [
        {"a": "x"},
        {"a": "y"},
        {"a": "x"},
    ]
    result = list(dedup_column_rows(rows, ["a"]))
    assert result[0]["a"] == "x"
    assert result[1]["a"] == "y"
    assert result[2]["a"] == "x"


def test_dedup_column_rows_empty_input():
    result = list(dedup_column_rows([], ["a"]))
    assert result == []


def test_dedup_column_rows_missing_column_ignored():
    rows = [{"a": "x"}, {"a": "x"}]
    result = list(dedup_column_rows(rows, ["b"]))
    assert result[0].get("b", "") == ""
    assert result[1].get("b", "") == ""


def test_dedup_column_file_writes_correctly():
    src = "a,b\nx,1\nx,2\ny,3\n"
    reader = csv.DictReader(io.StringIO(src))
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=["a", "b"])
    dedup_column_file(reader, writer, ["a"])
    out.seek(0)
    result = list(csv.DictReader(out))
    assert result[0]["a"] == "x"
    assert result[1]["a"] == ""
    assert result[2]["a"] == "y"
