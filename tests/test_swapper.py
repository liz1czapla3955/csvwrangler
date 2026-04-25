"""Unit tests for csvwrangler.swapper."""

import pytest

from csvwrangler.swapper import swap_rows


def _rows(*dicts):
    return list(dicts)


def test_swap_basic():
    rows = _rows(
        {"a": "1", "b": "2", "c": "x"},
        {"a": "3", "b": "4", "c": "y"},
    )
    result = list(swap_rows(iter(rows), "a", "b"))
    assert result[0]["a"] == "2"
    assert result[0]["b"] == "1"
    assert result[0]["c"] == "x"
    assert result[1]["a"] == "4"
    assert result[1]["b"] == "3"


def test_swap_preserves_other_columns():
    rows = _rows({"x": "hello", "y": "world", "z": "!"})
    result = list(swap_rows(iter(rows), "x", "y"))
    assert result[0]["z"] == "!"


def test_swap_missing_col_a_passthrough():
    rows = _rows({"b": "2", "c": "3"})
    result = list(swap_rows(iter(rows), "a", "b"))
    assert result[0] == {"b": "2", "c": "3"}


def test_swap_missing_col_b_passthrough():
    rows = _rows({"a": "1", "c": "3"})
    result = list(swap_rows(iter(rows), "a", "b"))
    assert result[0] == {"a": "1", "c": "3"}


def test_swap_both_columns_missing_passthrough():
    rows = _rows({"c": "only"})
    result = list(swap_rows(iter(rows), "a", "b"))
    assert result[0] == {"c": "only"}


def test_swap_empty_values():
    rows = _rows({"a": "", "b": "hello"})
    result = list(swap_rows(iter(rows), "a", "b"))
    assert result[0]["a"] == "hello"
    assert result[0]["b"] == ""


def test_swap_same_column_is_noop():
    rows = _rows({"a": "val", "b": "other"})
    result = list(swap_rows(iter(rows), "a", "a"))
    assert result[0]["a"] == "val"


def test_swap_empty_input():
    result = list(swap_rows(iter([]), "a", "b"))
    assert result == []


def test_swap_does_not_mutate_original():
    original = {"a": "1", "b": "2"}
    rows = [original]
    list(swap_rows(iter(rows), "a", "b"))
    assert original["a"] == "1"
    assert original["b"] == "2"
