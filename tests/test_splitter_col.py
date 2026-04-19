"""Tests for csvwrangler.splitter_col."""
import pytest
from csvwrangler.splitter_col import split_column_rows


def _rows(data):
    return list(data)


def test_split_column_default_names():
    rows = [{"tags": "a,b,c", "id": "1"}]
    result = _rows(split_column_rows(rows, "tags"))
    assert result == [{"id": "1", "tags_1": "a", "tags_2": "b", "tags_3": "c"}]


def test_split_column_custom_output_columns():
    rows = [{"name": "John Doe", "x": "y"}]
    result = _rows(split_column_rows(rows, "name", delimiter=" ", output_columns=["first", "last"]))
    assert result == [{"x": "y", "first": "John", "last": "Doe"}]


def test_split_column_fewer_parts_than_output_columns():
    rows = [{"val": "a"}]
    result = _rows(split_column_rows(rows, "val", output_columns=["c1", "c2", "c3"]))
    assert result[0]["c1"] == "a"
    assert result[0]["c2"] == ""
    assert result[0]["c3"] == ""


def test_split_column_removes_original():
    rows = [{"data": "x|y", "keep": "z"}]
    result = _rows(split_column_rows(rows, "data", delimiter="|"))
    assert "data" not in result[0]
    assert "keep" in result[0]


def test_split_column_max_split():
    rows = [{"v": "a:b:c:d"}]
    result = _rows(split_column_rows(rows, "v", delimiter=":", max_split=2))
    # split(':', 2) => ['a', 'b', 'c:d']
    assert result[0]["v_1"] == "a"
    assert result[0]["v_2"] == "b"
    assert result[0]["v_3"] == "c:d"


def test_split_column_empty_value():
    rows = [{"col": ""}]
    result = _rows(split_column_rows(rows, "col", output_columns=["a", "b"]))
    assert result[0]["a"] == ""
    assert result[0]["b"] == ""


def test_split_column_multiple_rows():
    rows = [
        {"tags": "x,y", "id": "1"},
        {"tags": "p,q,r", "id": "2"},
    ]
    results = _rows(split_column_rows(rows, "tags"))
    assert results[0] == {"id": "1", "tags_1": "x", "tags_2": "y"}
    assert results[1] == {"id": "2", "tags_1": "p", "tags_2": "q", "tags_3": "r"}


def test_split_column_missing_column_gives_empty_default():
    rows = [{"other": "val"}]
    result = _rows(split_column_rows(rows, "missing", output_columns=["a"]))
    assert result[0]["a"] == ""
