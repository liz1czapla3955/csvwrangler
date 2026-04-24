"""Tests for csvwrangler.correlator."""

from __future__ import annotations

import math
import pytest

from csvwrangler.correlator import _mean, _pearson, correlate_rows


def _rows(*dicts):
    return list(dicts)


# ---------------------------------------------------------------------------
# _mean
# ---------------------------------------------------------------------------

def test_mean_basic():
    assert _mean([1.0, 2.0, 3.0]) == 2.0


def test_mean_empty():
    assert _mean([]) == 0.0


# ---------------------------------------------------------------------------
# _pearson
# ---------------------------------------------------------------------------

def test_pearson_perfect_positive():
    r = _pearson([1, 2, 3, 4], [2, 4, 6, 8])
    assert r is not None
    assert abs(r - 1.0) < 1e-9


def test_pearson_perfect_negative():
    r = _pearson([1, 2, 3, 4], [8, 6, 4, 2])
    assert r is not None
    assert abs(r + 1.0) < 1e-9


def test_pearson_zero_variance_returns_none():
    assert _pearson([5, 5, 5], [1, 2, 3]) is None


def test_pearson_too_few_points_returns_none():
    assert _pearson([1.0], [2.0]) is None


# ---------------------------------------------------------------------------
# correlate_rows
# ---------------------------------------------------------------------------

def test_correlate_rows_shape():
    rows = [
        {"a": "1", "b": "2"},
        {"a": "2", "b": "4"},
        {"a": "3", "b": "6"},
    ]
    result = list(correlate_rows(rows, ["a", "b"]))
    assert len(result) == 2
    assert {r["column"] for r in result} == {"a", "b"}


def test_correlate_rows_diagonal_is_one():
    rows = [
        {"x": "1", "y": "3"},
        {"x": "2", "y": "1"},
        {"x": "3", "y": "4"},
    ]
    result = {r["column"]: r for r in correlate_rows(rows, ["x", "y"])}
    assert float(result["x"]["x"]) == pytest.approx(1.0)
    assert float(result["y"]["y"]) == pytest.approx(1.0)


def test_correlate_rows_symmetric():
    rows = [
        {"a": "10", "b": "20"},
        {"a": "20", "b": "15"},
        {"a": "30", "b": "25"},
    ]
    result = {r["column"]: r for r in correlate_rows(rows, ["a", "b"])}
    assert result["a"]["b"] == result["b"]["a"]


def test_correlate_rows_non_numeric_skipped():
    rows = [
        {"a": "1", "b": "two"},
        {"a": "2", "b": "4"},
        {"a": "3", "b": "6"},
    ]
    # Only rows where ALL columns are numeric are used
    result = {r["column"]: r for r in correlate_rows(rows, ["a", "b"])}
    # Should still produce output without crashing
    assert "a" in result and "b" in result


def test_correlate_rows_decimals():
    rows = [{"p": str(i), "q": str(i * 2)} for i in range(1, 6)]
    result = {r["column"]: r for r in correlate_rows(rows, ["p", "q"], decimals=2)}
    assert len(result["p"]["q"]) <= 7  # e.g. "1.00" or "-1.00"


def test_correlate_rows_empty_input():
    result = list(correlate_rows([], ["a", "b"]))
    assert len(result) == 2
    for r in result:
        assert r["a"] == "" or r["b"] == ""
