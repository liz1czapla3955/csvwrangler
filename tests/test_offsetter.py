"""Tests for csvwrangler.offsetter."""

import pytest
from csvwrangler.offsetter import _offset_value, offset_rows


# ---------------------------------------------------------------------------
# _offset_value
# ---------------------------------------------------------------------------

def test_offset_value_positive():
    assert _offset_value("10", 5, False) == "15"


def test_offset_value_negative():
    assert _offset_value("10", -3, False) == "7"


def test_offset_value_float_input():
    assert _offset_value("1.5", 0.5, False) == "2.0"


def test_offset_value_non_numeric_passthrough():
    assert _offset_value("N/A", 10, False) == "N/A"


def test_offset_value_empty_passthrough():
    assert _offset_value("", 10, False) == ""


def test_offset_value_percent():
    assert _offset_value("200", 10, True) == "220"


def test_offset_value_percent_negative():
    assert _offset_value("100", -50, True) == "50"


def test_offset_value_preserves_int_representation():
    result = _offset_value("7", 3, False)
    assert result == "10"
    assert "." not in result


def test_offset_value_float_result_when_input_has_decimal():
    result = _offset_value("7.0", 3, False)
    assert result == "10.0"


# ---------------------------------------------------------------------------
# offset_rows
# ---------------------------------------------------------------------------

def _rows():
    return [
        {"name": "alice", "score": "80", "bonus": "5"},
        {"name": "bob", "score": "90", "bonus": "10"},
        {"name": "carol", "score": "", "bonus": "N/A"},
    ]


def test_offset_rows_single_column():
    result = list(offset_rows(_rows(), ["score"], 10))
    assert result[0]["score"] == "90"
    assert result[1]["score"] == "100"
    assert result[2]["score"] == ""  # empty passthrough


def test_offset_rows_multiple_columns():
    result = list(offset_rows(_rows(), ["score", "bonus"], 5))
    assert result[0]["score"] == "85"
    assert result[0]["bonus"] == "10"
    assert result[1]["bonus"] == "15"


def test_offset_rows_percent():
    result = list(offset_rows(_rows(), ["score"], 10, percent=True))
    assert result[0]["score"] == "88.0"
    assert result[1]["score"] == "99.0"


def test_offset_rows_non_numeric_column_untouched():
    result = list(offset_rows(_rows(), ["bonus"], 1))
    assert result[2]["bonus"] == "N/A"


def test_offset_rows_unknown_column_ignored():
    result = list(offset_rows(_rows(), ["missing"], 5))
    assert result[0] == _rows()[0]


def test_offset_rows_preserves_other_columns():
    result = list(offset_rows(_rows(), ["score"], 0))
    assert result[0]["name"] == "alice"
    assert result[1]["name"] == "bob"


def test_offset_rows_zero_amount_no_change():
    original = _rows()
    result = list(offset_rows(original, ["score"], 0))
    assert result[0]["score"] == "80"
    assert result[1]["score"] == "90"
