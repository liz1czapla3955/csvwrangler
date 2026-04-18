"""Tests for csvwrangler.filler."""
import pytest
from csvwrangler.filler import fill_rows, _mean


def _rows(*dicts):
    return list(dicts)


# --- _mean ---

def test_mean_basic():
    assert _mean(["1", "2", "3"]) == "2"


def test_mean_with_empty():
    assert _mean(["10", "", "20"]) == "15"


def test_mean_all_empty():
    assert _mean(["", ""]) == ""


def test_mean_float():
    result = _mean(["1", "2"])
    assert result == "1.5"


# --- fill_rows value ---

def test_fill_value_constant():
    rows = _rows({"a": "1", "b": ""}, {"a": "", "b": "2"})
    result = list(fill_rows(rows, columns=["a", "b"], method="value", fill_value="N/A"))
    assert result[0]["b"] == "N/A"
    assert result[1]["a"] == "N/A"


def test_fill_value_all_columns_default():
    rows = _rows({"x": "", "y": "hello"})
    result = list(fill_rows(rows, columns=[], method="value", fill_value="0"))
    assert result[0]["x"] == "0"
    assert result[0]["y"] == "hello"


def test_fill_value_specific_column_only():
    rows = _rows({"a": "", "b": ""})
    result = list(fill_rows(rows, columns=["a"], method="value", fill_value="X"))
    assert result[0]["a"] == "X"
    assert result[0]["b"] == ""  # untouched


# --- fill_rows mean ---

def test_fill_mean():
    rows = _rows(
        {"score": "10"},
        {"score": ""},
        {"score": "20"},
    )
    result = list(fill_rows(rows, columns=["score"], method="mean"))
    assert result[1]["score"] == "15"


# --- fill_rows ffill ---

def test_fill_ffill_basic():
    rows = _rows(
        {"val": "A"},
        {"val": ""},
        {"val": ""},
        {"val": "B"},
    )
    result = list(fill_rows(rows, columns=["val"], method="ffill"))
    assert result[1]["val"] == "A"
    assert result[2]["val"] == "A"
    assert result[3]["val"] == "B"


def test_fill_ffill_leading_empty_stays_empty():
    rows = _rows({"val": ""}, {"val": "X"})
    result = list(fill_rows(rows, columns=["val"], method="ffill"))
    assert result[0]["val"] == ""


# --- edge cases ---

def test_fill_empty_input():
    result = list(fill_rows([], columns=["a"], method="value", fill_value="0"))
    assert result == []
