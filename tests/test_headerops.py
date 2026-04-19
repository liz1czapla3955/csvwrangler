"""Tests for csvwrangler.headerops."""
import pytest
from csvwrangler.headerops import reorder_columns, drop_columns, insert_column

ROWS = [
    {"a": "1", "b": "2", "c": "3"},
    {"a": "4", "b": "5", "c": "6"},
]


def test_reorder_columns_basic():
    result = list(reorder_columns(ROWS, ["c", "a", "b"]))
    assert list(result[0].keys()) == ["c", "a", "b"]
    assert result[0]["c"] == "3"


def test_reorder_columns_partial_order():
    result = list(reorder_columns(ROWS, ["c", "a"]))
    assert list(result[0].keys()) == ["c", "a", "b"]


def test_reorder_columns_unknown_in_order_ignored():
    result = list(reorder_columns(ROWS, ["z", "b", "a"]))
    assert list(result[0].keys()) == ["b", "a", "c"]


def test_reorder_columns_empty_input():
    result = list(reorder_columns([], ["a", "b"]))
    assert result == []


def test_drop_columns_basic():
    result = list(drop_columns(ROWS, ["b"]))
    assert "b" not in result[0]
    assert result[0] == {"a": "1", "c": "3"}


def test_drop_columns_multiple():
    result = list(drop_columns(ROWS, ["a", "c"]))
    assert list(result[0].keys()) == ["b"]


def test_drop_columns_nonexistent_ignored():
    result = list(drop_columns(ROWS, ["z"]))
    assert result[0] == ROWS[0]


def test_drop_columns_all_columns():
    result = list(drop_columns(ROWS, ["a", "b", "c"]))
    assert result[0] == {}
    assert result[1] == {}


def test_insert_column_end():
    result = list(insert_column(ROWS, "d", "x"))
    assert list(result[0].keys())[-1] == "d"
    assert result[0]["d"] == "x"


def test_insert_column_position_zero():
    result = list(insert_column(ROWS, "d", "0", position=0))
    assert list(result[0].keys())[0] == "d"


def test_insert_column_middle():
    result = list(insert_column(ROWS, "d", "mid", position=1))
    assert list(result[0].keys())[1] == "d"


def test_insert_column_preserves_values():
    result = list(insert_column(ROWS, "d", "9"))
    assert result[1]["a"] == "4"
    assert result[1]["d"] == "9"
