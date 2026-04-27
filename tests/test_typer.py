"""Tests for csvwrangler.typer."""
import pytest
from csvwrangler.typer import _coerce, retype_rows


# ---------------------------------------------------------------------------
# _coerce
# ---------------------------------------------------------------------------

def test_coerce_int_whole():
    assert _coerce("42", "int") == "42"


def test_coerce_int_float_string():
    assert _coerce("3.7", "int") == "3"


def test_coerce_int_invalid_passthrough():
    assert _coerce("abc", "int") == "abc"


def test_coerce_float_valid():
    assert _coerce("1.5", "float") == "1.5"


def test_coerce_float_integer_string():
    assert _coerce("7", "float") == "7.0"


def test_coerce_float_invalid_passthrough():
    assert _coerce("nope", "float") == "nope"


def test_coerce_bool_true_variants():
    for v in ("true", "True", "TRUE", "yes", "1", "on"):
        assert _coerce(v, "bool") == "true", f"expected true for {v!r}"


def test_coerce_bool_false_variants():
    for v in ("false", "False", "FALSE", "no", "0", "off"):
        assert _coerce(v, "bool") == "false", f"expected false for {v!r}"


def test_coerce_bool_unknown_passthrough():
    assert _coerce("maybe", "bool") == "maybe"


def test_coerce_str_strips_whitespace():
    assert _coerce("  hello  ", "str") == "hello"


def test_coerce_unknown_dtype_passthrough():
    assert _coerce("hello", "date") == "hello"


# ---------------------------------------------------------------------------
# retype_rows
# ---------------------------------------------------------------------------

def _rows():
    return [
        {"id": "1", "score": "9.5", "active": "yes", "name": "  Alice  "},
        {"id": "2", "score": "bad", "active": "0",   "name": "Bob"},
        {"id": "3.9", "score": "3.0", "active": "True", "name": "Carol"},
    ]


def test_retype_rows_int_column():
    result = list(retype_rows(_rows(), {"id": "int"}))
    assert result[0]["id"] == "1"
    assert result[2]["id"] == "3"  # 3.9 -> int 3


def test_retype_rows_float_column():
    result = list(retype_rows(_rows(), {"score": "float"}))
    assert result[0]["score"] == "9.5"
    assert result[1]["score"] == "bad"  # invalid passthrough


def test_retype_rows_bool_column():
    result = list(retype_rows(_rows(), {"active": "bool"}))
    assert result[0]["active"] == "true"
    assert result[1]["active"] == "false"
    assert result[2]["active"] == "true"


def test_retype_rows_str_column_strips():
    result = list(retype_rows(_rows(), {"name": "str"}))
    assert result[0]["name"] == "Alice"


def test_retype_rows_unknown_column_ignored():
    result = list(retype_rows(_rows(), {"nonexistent": "int"}))
    assert result[0]["id"] == "1"  # unchanged


def test_retype_rows_multiple_columns():
    result = list(retype_rows(_rows(), {"id": "int", "active": "bool"}))
    assert result[0]["id"] == "1"
    assert result[0]["active"] == "true"
    assert result[0]["score"] == "9.5"  # untouched


def test_retype_rows_empty_input():
    result = list(retype_rows([], {"id": "int"}))
    assert result == []
