"""Tests for csvwrangler.comparer."""
import pytest
from csvwrangler.comparer import _compare, compare_rows


def _rows():
    return [
        {"a": "10", "b": "20"},
        {"a": "20", "b": "20"},
        {"a": "30", "b": "20"},
    ]


def test_compare_eq_true():
    assert _compare("5", "5", "eq") is True


def test_compare_eq_false():
    assert _compare("5", "6", "eq") is False


def test_compare_ne():
    assert _compare("5", "6", "ne") is True


def test_compare_lt():
    assert _compare("3", "5", "lt") is True


def test_compare_le_equal():
    assert _compare("5", "5", "le") is True


def test_compare_gt():
    assert _compare("7", "5", "gt") is True


def test_compare_ge_equal():
    assert _compare("5", "5", "ge") is True


def test_compare_string_eq():
    assert _compare("hello", "hello", "eq") is True


def test_compare_string_ne():
    assert _compare("hello", "world", "ne") is True


def test_compare_invalid_op():
    with pytest.raises(ValueError):
        _compare("1", "2", "xx")


def test_compare_rows_lt():
    result = list(compare_rows(iter(_rows()), "a", "b", "lt"))
    assert result[0]["match"] == "true"
    assert result[1]["match"] == "false"
    assert result[2]["match"] == "false"


def test_compare_rows_eq():
    result = list(compare_rows(iter(_rows()), "a", "b", "eq"))
    assert result[1]["match"] == "true"
    assert result[0]["match"] == "false"


def test_compare_rows_custom_output_col():
    result = list(compare_rows(iter(_rows()), "a", "b", "gt", output_col="is_greater"))
    assert "is_greater" in result[0]


def test_compare_rows_custom_values():
    result = list(compare_rows(iter(_rows()), "a", "b", "eq", true_val="yes", false_val="no"))
    assert result[1]["match"] == "yes"
    assert result[0]["match"] == "no"


def test_compare_rows_missing_col_defaults_false():
    rows = [{"a": "5"}]
    result = list(compare_rows(iter(rows), "a", "b", "eq"))
    assert result[0]["match"] == "false"


def test_compare_rows_preserves_other_fields():
    rows = [{"a": "1", "b": "2", "c": "x"}]
    result = list(compare_rows(iter(rows), "a", "b", "lt"))
    assert result[0]["c"] == "x"
