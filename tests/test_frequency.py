"""Unit tests for csvwrangler.differ2 (frequency analysis)."""
import pytest
from csvwrangler.differ2 import frequency_rows


def _rows():
    return [
        {"color": "red", "size": "S"},
        {"color": "blue", "size": "M"},
        {"color": "red", "size": "L"},
        {"color": "green", "size": "S"},
        {"color": "red", "size": "S"},
        {"color": "blue", "size": "S"},
    ]


def test_frequency_rows_counts_correctly():
    result = frequency_rows(_rows(), column="color", sort_by="value", ascending=True)
    by_color = {r["color"]: int(r["frequency"]) for r in result}
    assert by_color == {"red": 3, "blue": 2, "green": 1}


def test_frequency_rows_sort_by_count_descending():
    result = frequency_rows(_rows(), column="color", sort_by="count", ascending=False)
    counts = [int(r["frequency"]) for r in result]
    assert counts == sorted(counts, reverse=True)


def test_frequency_rows_sort_by_count_ascending():
    result = frequency_rows(_rows(), column="color", sort_by="count", ascending=True)
    counts = [int(r["frequency"]) for r in result]
    assert counts == sorted(counts)


def test_frequency_rows_sort_by_value_ascending():
    result = frequency_rows(_rows(), column="color", sort_by="value", ascending=True)
    values = [r["color"] for r in result]
    assert values == sorted(values)


def test_frequency_rows_sort_by_value_descending():
    result = frequency_rows(_rows(), column="color", sort_by="value", ascending=False)
    values = [r["color"] for r in result]
    assert values == sorted(values, reverse=True)


def test_frequency_rows_custom_output_column():
    result = frequency_rows(_rows(), column="color", output_column="cnt")
    assert all("cnt" in r for r in result)
    assert all("frequency" not in r for r in result)


def test_frequency_rows_missing_column_raises():
    with pytest.raises(KeyError, match="missing"):
        frequency_rows(_rows(), column="missing")


def test_frequency_rows_invalid_sort_by_raises():
    with pytest.raises(ValueError, match="sort_by"):
        frequency_rows(_rows(), column="color", sort_by="bad")


def test_frequency_rows_empty_input():
    result = frequency_rows([], column="color")
    assert result == []


def test_frequency_rows_single_value():
    rows = [{"x": "a"}, {"x": "a"}, {"x": "a"}]
    result = frequency_rows(rows, column="x")
    assert len(result) == 1
    assert int(result[0]["frequency"]) == 3
