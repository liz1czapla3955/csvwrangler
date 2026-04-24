"""Tests for csvwrangler.clamper."""

from __future__ import annotations

import pytest

from csvwrangler.clamper import _percentile, clamp_rows


# ---------------------------------------------------------------------------
# _percentile
# ---------------------------------------------------------------------------

def test_percentile_min():
    assert _percentile([1, 2, 3, 4, 5], 0) == 1.0


def test_percentile_max():
    assert _percentile([1, 2, 3, 4, 5], 100) == 5.0


def test_percentile_median():
    assert _percentile([1, 2, 3, 4, 5], 50) == 3.0


def test_percentile_empty_raises():
    with pytest.raises(ValueError):
        _percentile([], 50)


def test_percentile_single_value():
    assert _percentile([7], 25) == 7.0


# ---------------------------------------------------------------------------
# clamp_rows — absolute bounds
# ---------------------------------------------------------------------------

def _rows():
    return [
        {"id": "1", "val": "5"},
        {"id": "2", "val": "15"},
        {"id": "3", "val": "25"},
        {"id": "4", "val": "abc"},
        {"id": "5", "val": ""},
    ]


def test_clamp_low_only():
    result = clamp_rows(_rows(), column="val", low=10)
    vals = [r["val"] for r in result]
    assert vals == ["10", "15", "25", "abc", ""]


def test_clamp_high_only():
    result = clamp_rows(_rows(), column="val", high=20)
    vals = [r["val"] for r in result]
    assert vals == ["5", "15", "20", "abc", ""]


def test_clamp_both_bounds():
    result = clamp_rows(_rows(), column="val", low=10, high=20)
    vals = [r["val"] for r in result]
    assert vals == ["10", "15", "20", "abc", ""]


def test_clamp_non_numeric_passthrough():
    result = clamp_rows(_rows(), column="val", low=0, high=100)
    assert result[3]["val"] == "abc"
    assert result[4]["val"] == ""


def test_clamp_output_column():
    result = clamp_rows(_rows(), column="val", low=10, high=20, output_column="clamped")
    assert result[0]["val"] == "5"        # original unchanged
    assert result[0]["clamped"] == "10"   # new column added
    assert result[2]["clamped"] == "20"


def test_clamp_empty_input():
    assert clamp_rows([], column="val", low=0, high=10) == []


# ---------------------------------------------------------------------------
# clamp_rows — percentile bounds
# ---------------------------------------------------------------------------

def _pct_rows():
    return [{"v": str(i)} for i in range(1, 11)]  # 1..10


def test_clamp_low_pct():
    # 10th percentile of 1..10 ≈ 1.9  → values below are raised
    result = clamp_rows(_pct_rows(), column="v", low_pct=10)
    assert float(result[0]["v"]) >= 1.9


def test_clamp_high_pct():
    # 90th percentile of 1..10 ≈ 9.1  → values above are lowered
    result = clamp_rows(_pct_rows(), column="v", high_pct=90)
    assert float(result[-1]["v"]) <= 9.1


def test_clamp_pct_overrides_absolute():
    # Even if absolute bounds are passed, pct should override
    result = clamp_rows(_pct_rows(), column="v", low=0, low_pct=50)
    # 50th pct of 1..10 = 5.5, so first few values should be raised
    assert float(result[0]["v"]) >= 5.5
