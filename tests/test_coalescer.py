"""Tests for csvwrangler.coalescer."""

import csv
import io
import pytest

from csvwrangler.coalescer import coalesce_rows, coalesce_file


def _rows(*dicts):
    return list(dicts)


def test_coalesce_fills_empty_from_first_source():
    rows = _rows({"a": "", "b": "hello", "c": "world"})
    result = list(coalesce_rows(rows, target="a", sources=["b", "c"]))
    assert result[0]["a"] == "hello"


def test_coalesce_fills_from_second_source_when_first_empty():
    rows = _rows({"a": "", "b": "", "c": "world"})
    result = list(coalesce_rows(rows, target="a", sources=["b", "c"]))
    assert result[0]["a"] == "world"


def test_coalesce_does_not_overwrite_non_empty_target():
    rows = _rows({"a": "keep", "b": "other", "c": "another"})
    result = list(coalesce_rows(rows, target="a", sources=["b", "c"]))
    assert result[0]["a"] == "keep"


def test_coalesce_leaves_empty_when_all_sources_empty():
    rows = _rows({"a": "", "b": "", "c": ""})
    result = list(coalesce_rows(rows, target="a", sources=["b", "c"]))
    assert result[0]["a"] == ""


def test_coalesce_custom_empty_values():
    rows = _rows({"a": "N/A", "b": "fallback", "c": "other"})
    result = list(coalesce_rows(rows, target="a", sources=["b"], empty_values=("N/A", "")))
    assert result[0]["a"] == "fallback"


def test_coalesce_multiple_rows():
    rows = [
        {"a": "", "b": "x"},
        {"a": "y", "b": "z"},
        {"a": "", "b": ""},
    ]
    result = list(coalesce_rows(rows, target="a", sources=["b"]))
    assert result[0]["a"] == "x"
    assert result[1]["a"] == "y"
    assert result[2]["a"] == ""


def test_coalesce_does_not_mutate_original_row():
    original = {"a": "", "b": "fill"}
    rows = [original]
    result = list(coalesce_rows(rows, target="a", sources=["b"]))
    assert result[0]["a"] == "fill"
    assert original["a"] == ""  # original unchanged


def test_coalesce_missing_source_column_treated_as_empty():
    rows = _rows({"a": "", "b": "value"})
    result = list(coalesce_rows(rows, target="a", sources=["nonexistent", "b"]))
    assert result[0]["a"] == "value"


def test_coalesce_file_writes_header_and_rows():
    csv_input = "a,b,c\n,hello,world\nkeep,x,y\n"
    reader = csv.DictReader(io.StringIO(csv_input))
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=["a", "b", "c"])
    coalesce_file(reader, writer, target="a", sources=["b", "c"])
    out.seek(0)
    result = list(csv.DictReader(out))
    assert result[0]["a"] == "hello"
    assert result[1]["a"] == "keep"
