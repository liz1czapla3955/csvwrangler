"""Tests for csvwrangler.flattener."""

import csv
import os
import tempfile
import pytest

from csvwrangler.flattener import fill_down_rows, flatten_file


# ---------------------------------------------------------------------------
# fill_down_rows
# ---------------------------------------------------------------------------

def test_fill_down_all_columns():
    rows = [
        {"region": "North", "city": "Oslo"},
        {"region": "", "city": "Bergen"},
        {"region": "", "city": "Tromsø"},
        {"region": "South", "city": "Stavanger"},
    ]
    result = fill_down_rows(rows)
    assert result[1]["region"] == "North"
    assert result[2]["region"] == "North"
    assert result[3]["region"] == "South"


def test_fill_down_specific_columns():
    rows = [
        {"a": "1", "b": "x"},
        {"a": "", "b": ""},
        {"a": "2", "b": ""},
    ]
    result = fill_down_rows(rows, columns=["a"])
    assert result[1]["a"] == "1"
    assert result[1]["b"] == ""  # b not filled
    assert result[2]["a"] == "2"


def test_fill_down_empty_input():
    assert fill_down_rows([]) == []


def test_fill_down_no_empty_cells():
    rows = [
        {"x": "a", "y": "1"},
        {"x": "b", "y": "2"},
    ]
    result = fill_down_rows(rows)
    assert result == rows


def test_fill_down_leading_empty_stays_empty():
    """Cells before any non-empty value remain empty."""
    rows = [
        {"cat": "", "val": "10"},
        {"cat": "A", "val": "20"},
        {"cat": "", "val": "30"},
    ]
    result = fill_down_rows(rows, columns=["cat"])
    assert result[0]["cat"] == ""
    assert result[1]["cat"] == "A"
    assert result[2]["cat"] == "A"


def test_fill_down_whitespace_treated_as_empty():
    rows = [
        {"col": "value"},
        {"col": "   "},
    ]
    result = fill_down_rows(rows)
    assert result[1]["col"] == "value"


# ---------------------------------------------------------------------------
# flatten_file
# ---------------------------------------------------------------------------

def _write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_flatten_file_roundtrip():
    rows = [
        {"group": "A", "value": "1"},
        {"group": "", "value": "2"},
        {"group": "B", "value": "3"},
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        inp = os.path.join(tmpdir, "in.csv")
        out = os.path.join(tmpdir, "out.csv")
        _write_csv(inp, rows, ["group", "value"])
        flatten_file(inp, out)
        with open(out, newline="", encoding="utf-8") as fh:
            result = list(csv.DictReader(fh))
    assert result[1]["group"] == "A"
    assert result[2]["group"] == "B"


def test_flatten_file_bad_column_raises():
    rows = [{"a": "1"}, {"a": ""}]
    with tempfile.TemporaryDirectory() as tmpdir:
        inp = os.path.join(tmpdir, "in.csv")
        out = os.path.join(tmpdir, "out.csv")
        _write_csv(inp, rows, ["a"])
        with pytest.raises(ValueError, match="Columns not found"):
            flatten_file(inp, out, columns=["nonexistent"])
