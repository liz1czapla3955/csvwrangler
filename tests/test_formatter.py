"""Tests for csvwrangler.formatter."""
import pytest
from csvwrangler.formatter import _format_value, format_rows


def _rows(*dicts):
    return list(dicts)


# _format_value tests

def test_format_value_date_valid():
    result = _format_value("2024-01-15", "date", "%Y-%m-%d->%d/%m/%Y")
    assert result == "15/01/2024"


def test_format_value_date_invalid_passthrough():
    result = _format_value("not-a-date", "date", "%Y-%m-%d->%d/%m/%Y")
    assert result == "not-a-date"


def test_format_value_date_bad_arg_passthrough():
    result = _format_value("2024-01-15", "date", "no-arrow")
    assert result == "2024-01-15"


def test_format_value_number_float():
    assert _format_value("3.14159", "number", ".2f") == "3.14"


def test_format_value_number_invalid_passthrough():
    assert _format_value("abc", "number", ".2f") == "abc"


def test_format_value_zeropad():
    assert _format_value("42", "zeropad", "6") == "000042"


def test_format_value_zeropad_already_wide():
    assert _format_value("1234567", "zeropad", "4") == "1234567"


def test_format_value_upper():
    assert _format_value("hello world", "upper", "") == "HELLO WORLD"


def test_format_value_lower():
    assert _format_value("HELLO", "lower", "") == "hello"


def test_format_value_title():
    assert _format_value("hello world", "title", "") == "Hello World"


def test_format_value_unknown_type_passthrough():
    assert _format_value("foo", "unknown", "") == "foo"


# format_rows tests

def test_format_rows_applies_to_column():
    rows = [{"name": "alice", "age": "30"}, {"name": "bob", "age": "25"}]
    result = list(format_rows(rows, "name", "upper"))
    assert result[0]["name"] == "ALICE"
    assert result[1]["name"] == "BOB"
    assert result[0]["age"] == "30"


def test_format_rows_missing_column_unchanged():
    rows = [{"name": "alice"}]
    result = list(format_rows(rows, "missing", "upper"))
    assert result[0] == {"name": "alice"}


def test_format_rows_empty_input():
    assert list(format_rows([], "col", "upper")) == []


def test_format_rows_number_formatting():
    rows = [{"price": "9.9"}, {"price": "100"}]
    result = list(format_rows(rows, "price", "number", ".2f"))
    assert result[0]["price"] == "9.90"
    assert result[1]["price"] == "100.00"


def test_format_rows_date_reformatting():
    rows = [{"dob": "1990-06-15"}]
    result = list(format_rows(rows, "dob", "date", "%Y-%m-%d->%d/%m/%Y"))
    assert result[0]["dob"] == "15/06/1990"
