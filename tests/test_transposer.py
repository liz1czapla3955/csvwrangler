"""Tests for csvwrangler.transposer."""

import csv
import os
import tempfile
import pytest

from csvwrangler.transposer import transpose_rows, transpose_file


ROWS = [
    {"name": "Alice", "age": "30", "city": "NYC"},
    {"name": "Bob",   "age": "25", "city": "LA"},
    {"name": "Carol", "age": "35", "city": "SF"},
]


def test_transpose_rows_no_index():
    result = transpose_rows(ROWS)
    assert len(result) == 3  # one row per original column
    assert result[0]["field"] == "name"
    assert result[0]["row_0"] == "Alice"
    assert result[0]["row_1"] == "Bob"
    assert result[0]["row_2"] == "Carol"


def test_transpose_rows_with_index_col():
    result = transpose_rows(ROWS, index_col="name")
    # 'name' is used as index, so only 'age' and 'city' become rows
    assert len(result) == 2
    fields = [r["field"] for r in result]
    assert fields == ["age", "city"]
    assert result[0]["Alice"] == "30"
    assert result[0]["Bob"] == "25"
    assert result[1]["Carol"] == "SF"


def test_transpose_rows_output_headers_no_index():
    result = transpose_rows(ROWS)
    keys = list(result[0].keys())
    assert keys[0] == "field"
    assert keys[1:] == ["row_0", "row_1", "row_2"]


def test_transpose_rows_output_headers_with_index():
    result = transpose_rows(ROWS, index_col="name")
    keys = list(result[0].keys())
    assert keys == ["field", "Alice", "Bob", "Carol"]


def test_transpose_rows_empty_input():
    result = transpose_rows([])
    assert result == []


def test_transpose_rows_invalid_index_col():
    with pytest.raises(ValueError, match="index_col 'missing'"):
        transpose_rows(ROWS, index_col="missing")


def test_transpose_rows_single_row():
    rows = [{"x": "1", "y": "2"}]
    result = transpose_rows(rows)
    assert len(result) == 2
    assert result[0] == {"field": "x", "row_0": "1"}
    assert result[1] == {"field": "y", "row_0": "2"}


def _write_csv(path, rows):
    if not rows:
        open(path, "w").close()
        return
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _read_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_transpose_file_no_index():
    with tempfile.TemporaryDirectory() as tmp:
        inp = os.path.join(tmp, "in.csv")
        out = os.path.join(tmp, "out.csv")
        _write_csv(inp, ROWS)
        transpose_file(inp, out)
        result = _read_csv(out)
        assert len(result) == 3
        assert result[1]["field"] == "age"
        assert result[1]["row_0"] == "30"


def test_transpose_file_with_index():
    with tempfile.TemporaryDirectory() as tmp:
        inp = os.path.join(tmp, "in.csv")
        out = os.path.join(tmp, "out.csv")
        _write_csv(inp, ROWS)
        transpose_file(inp, out, index_col="name")
        result = _read_csv(out)
        assert len(result) == 2
        assert result[0]["Alice"] == "30"
        assert result[1]["Bob"] == "LA"
