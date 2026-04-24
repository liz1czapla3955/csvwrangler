"""Tests for csvwrangler.winsorizer."""

import pytest
from csvwrangler.winsorizer import _percentile, winsorize_rows


def _rows():
    return [
        {"id": "1", "score": "1"},
        {"id": "2", "score": "10"},
        {"id": "3", "score": "20"},
        {"id": "4", "score": "30"},
        {"id": "5", "score": "100"},
    ]


# --- _percentile ---

def test_percentile_min():
    assert _percentile([1.0, 2.0, 3.0, 4.0, 5.0], 0) == 1.0


def test_percentile_max():
    assert _percentile([1.0, 2.0, 3.0, 4.0, 5.0], 100) == 5.0


def test_percentile_median():
    result = _percentile([1.0, 2.0, 3.0, 4.0, 5.0], 50)
    assert result == 3.0


def test_percentile_single_value():
    assert _percentile([42.0], 25) == 42.0


def test_percentile_empty():
    assert _percentile([], 50) == 0.0


# --- winsorize_rows ---

def test_winsorize_empty_input():
    assert winsorize_rows([], ["score"]) == []


def test_winsorize_clamps_lower_outlier():
    rows = _rows()
    result = winsorize_rows(rows, ["score"], lower_pct=20, upper_pct=80)
    scores = [float(r["score"]) for r in result]
    low_bound = _percentile([1, 10, 20, 30, 100], 20)
    assert scores[0] == pytest.approx(low_bound)


def test_winsorize_clamps_upper_outlier():
    rows = _rows()
    result = winsorize_rows(rows, ["score"], lower_pct=20, upper_pct=80)
    scores = [float(r["score"]) for r in result]
    hi_bound = _percentile([1, 10, 20, 30, 100], 80)
    assert scores[-1] == pytest.approx(hi_bound)


def test_winsorize_middle_values_unchanged():
    rows = _rows()
    result = winsorize_rows(rows, ["score"], lower_pct=5, upper_pct=95)
    # The middle value (20) should be unchanged
    assert float(result[2]["score"]) == 20.0


def test_winsorize_non_numeric_passthrough():
    rows = [
        {"id": "a", "score": "n/a"},
        {"id": "b", "score": "50"},
        {"id": "c", "score": "100"},
    ]
    result = winsorize_rows(rows, ["score"], lower_pct=10, upper_pct=90)
    # Non-numeric value should remain unchanged
    assert result[0]["score"] == "n/a"


def test_winsorize_preserves_other_columns():
    rows = _rows()
    result = winsorize_rows(rows, ["score"], lower_pct=20, upper_pct=80)
    ids = [r["id"] for r in result]
    assert ids == ["1", "2", "3", "4", "5"]


def test_winsorize_column_not_in_rows_is_ignored():
    rows = [{"id": "1", "val": "10"}, {"id": "2", "val": "20"}]
    # Should not raise even if column doesn't exist
    result = winsorize_rows(rows, ["nonexistent"], lower_pct=5, upper_pct=95)
    assert result == rows


def test_winsorize_multiple_columns():
    rows = [
        {"a": "1", "b": "100"},
        {"a": "50", "b": "50"},
        {"a": "100", "b": "1"},
    ]
    result = winsorize_rows(rows, ["a", "b"], lower_pct=10, upper_pct=90)
    a_vals = [float(r["a"]) for r in result]
    b_vals = [float(r["b"]) for r in result]
    assert a_vals[0] <= a_vals[1] <= a_vals[2]
    assert b_vals[2] <= b_vals[1] <= b_vals[0]
