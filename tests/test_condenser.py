"""Tests for csvwrangler.condenser."""

import pytest
from csvwrangler.condenser import condense_rows


def _rows(*dicts):
    return list(dicts)


def test_condense_basic():
    rows = _rows({"a": "1", "b": "2", "c": "x"})
    result = list(condense_rows(rows, columns=["a", "b"]))
    assert result[0]["summary"] == "a=1; b=2"


def test_condense_preserves_other_columns():
    rows = _rows({"a": "1", "b": "2", "c": "x"})
    result = list(condense_rows(rows, columns=["a", "b"]))
    assert result[0]["c"] == "x"


def test_condense_custom_output_column():
    rows = _rows({"x": "hello", "y": "world"})
    result = list(condense_rows(rows, columns=["x", "y"], output_column="merged"))
    assert "merged" in result[0]
    assert "summary" not in result[0]


def test_condense_custom_separator():
    rows = _rows({"a": "1", "b": "2"})
    result = list(condense_rows(rows, columns=["a", "b"], separator=" | "))
    assert result[0]["summary"] == "a=1 | b=2"


def test_condense_custom_template():
    rows = _rows({"a": "1", "b": "2"})
    result = list(condense_rows(rows, columns=["a", "b"], template="{col}:{val}"))
    assert result[0]["summary"] == "a:1; b:2"


def test_condense_skip_empty_true():
    rows = _rows({"a": "1", "b": "", "c": "3"})
    result = list(condense_rows(rows, columns=["a", "b", "c"], skip_empty=True))
    assert result[0]["summary"] == "a=1; c=3"


def test_condense_skip_empty_false():
    rows = _rows({"a": "1", "b": "", "c": "3"})
    result = list(condense_rows(rows, columns=["a", "b", "c"], skip_empty=False))
    assert result[0]["summary"] == "a=1; b=; c=3"


def test_condense_missing_column_treated_as_empty():
    rows = _rows({"a": "1"})
    result = list(condense_rows(rows, columns=["a", "z"], skip_empty=True))
    assert result[0]["summary"] == "a=1"


def test_condense_all_empty_skip():
    rows = _rows({"a": "", "b": ""})
    result = list(condense_rows(rows, columns=["a", "b"], skip_empty=True))
    assert result[0]["summary"] == ""


def test_condense_multiple_rows():
    rows = _rows(
        {"name": "Alice", "role": "admin"},
        {"name": "Bob", "role": ""},
    )
    result = list(condense_rows(rows, columns=["name", "role"], skip_empty=True))
    assert result[0]["summary"] == "name=Alice; role=admin"
    assert result[1]["summary"] == "name=Bob"


def test_condense_empty_input():
    result = list(condense_rows([], columns=["a", "b"]))
    assert result == []
