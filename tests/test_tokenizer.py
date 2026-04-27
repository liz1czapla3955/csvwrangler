"""Tests for csvwrangler.tokenizer"""

import pytest
from csvwrangler.tokenizer import tokenize_rows


def _rows():
    return [
        {"id": "1", "tags": "python csv data"},
        {"id": "2", "tags": "csv json"},
        {"id": "3", "tags": "python"},
        {"id": "4", "tags": ""},
    ]


# ── split mode ────────────────────────────────────────────────────────────────

def test_split_default_sep():
    result = list(tokenize_rows(_rows(), column="tags"))
    assert result[0]["tags"] == "python|csv|data"
    assert result[1]["tags"] == "csv|json"


def test_split_custom_output_sep():
    result = list(tokenize_rows(_rows(), column="tags", output_sep=","))
    assert result[0]["tags"] == "python,csv,data"


def test_split_custom_input_sep():
    rows = [{"id": "1", "tags": "a,b,c"}]
    result = list(tokenize_rows(rows, column="tags", sep=","))
    assert result[0]["tags"] == "a|b|c"


def test_split_empty_value_produces_empty_string():
    result = list(tokenize_rows(_rows(), column="tags"))
    assert result[3]["tags"] == ""


def test_split_lowercase():
    rows = [{"id": "1", "tags": "Python CSV"}]
    result = list(tokenize_rows(rows, column="tags", lowercase=True))
    assert result[0]["tags"] == "python|csv"


def test_split_preserves_other_columns():
    result = list(tokenize_rows(_rows(), column="tags"))
    assert result[0]["id"] == "1"


# ── indicator mode ────────────────────────────────────────────────────────────

def test_indicator_adds_columns():
    result = list(tokenize_rows(_rows(), column="tags", mode="indicator"))
    assert "python" in result[0]
    assert "csv" in result[0]
    assert "data" in result[0]
    assert "json" in result[0]


def test_indicator_values_correct():
    result = list(tokenize_rows(_rows(), column="tags", mode="indicator"))
    assert result[0]["python"] == "1"
    assert result[0]["json"] == "0"
    assert result[1]["csv"] == "1"
    assert result[1]["data"] == "0"


def test_indicator_empty_row_all_zeros():
    result = list(tokenize_rows(_rows(), column="tags", mode="indicator"))
    assert result[3]["python"] == "0"
    assert result[3]["csv"] == "0"


def test_indicator_prefix():
    result = list(tokenize_rows(_rows(), column="tags", mode="indicator", prefix="tag_"))
    assert "tag_python" in result[0]
    assert "tag_csv" in result[0]


def test_indicator_lowercase():
    rows = [{"id": "1", "tags": "Python"}, {"id": "2", "tags": "python"}]
    result = list(tokenize_rows(rows, column="tags", mode="indicator", lowercase=True))
    assert result[0]["python"] == "1"
    assert result[1]["python"] == "1"


# ── edge cases ────────────────────────────────────────────────────────────────

def test_empty_input_yields_nothing():
    result = list(tokenize_rows([], column="tags"))
    assert result == []


def test_invalid_mode_raises():
    with pytest.raises(ValueError, match="Unknown mode"):
        list(tokenize_rows(_rows(), column="tags", mode="explode"))
