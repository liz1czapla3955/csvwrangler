"""Tests for csvwrangler.rounder."""

import pytest
from csvwrangler.rounder import _round_value, round_rows


# ---------------------------------------------------------------------------
# _round_value
# ---------------------------------------------------------------------------

def test_round_value_two_decimals():
    assert _round_value("3.14159", 2) == "3.14"


def test_round_value_zero_decimals_returns_int_string():
    assert _round_value("3.7", 0) == "4"


def test_round_value_zero_decimals_negative():
    assert _round_value("-2.5", 0) == "-2"


def test_round_value_non_numeric_passthrough():
    assert _round_value("hello", 2) == "hello"


def test_round_value_empty_string_passthrough():
    assert _round_value("", 2) == ""


def test_round_value_already_integer_string():
    assert _round_value("5", 2) == "5.0"


def test_round_value_four_decimals():
    assert _round_value("1.23456789", 4) == "1.2346"


# ---------------------------------------------------------------------------
# round_rows
# ---------------------------------------------------------------------------

def _rows():
    return [
        {"name": "alice", "score": "9.8765", "ratio": "0.333333"},
        {"name": "bob",   "score": "7.1",    "ratio": "0.666667"},
        {"name": "carol", "score": "n/a",    "ratio": "1.0"},
    ]


def test_round_rows_single_column():
    result = list(round_rows(_rows(), columns=["score"], decimals=1))
    assert result[0]["score"] == "9.9"
    assert result[1]["score"] == "7.1"
    assert result[2]["score"] == "n/a"   # non-numeric passthrough


def test_round_rows_multiple_columns():
    result = list(round_rows(_rows(), columns=["score", "ratio"], decimals=2))
    assert result[0]["score"] == "9.88"
    assert result[0]["ratio"] == "0.33"
    assert result[1]["ratio"] == "0.67"


def test_round_rows_non_target_columns_unchanged():
    result = list(round_rows(_rows(), columns=["score"], decimals=2))
    assert result[0]["name"] == "alice"
    assert result[0]["ratio"] == "0.333333"  # untouched


def test_round_rows_zero_decimals():
    result = list(round_rows(_rows(), columns=["score"], decimals=0))
    assert result[0]["score"] == "10"
    assert result[1]["score"] == "7"


def test_round_rows_empty_input():
    result = list(round_rows([], columns=["score"], decimals=2))
    assert result == []


def test_round_rows_unknown_column_ignored():
    """Specifying a column that doesn't exist should not raise."""
    result = list(round_rows(_rows(), columns=["nonexistent"], decimals=2))
    assert result[0]["score"] == "9.8765"  # unchanged


def test_round_rows_default_decimals():
    rows = [{"val": "1.23456"}]
    result = list(round_rows(rows, columns=["val"]))
    assert result[0]["val"] == "1.23"
