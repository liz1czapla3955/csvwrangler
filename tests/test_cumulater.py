"""Tests for csvwrangler.cumulater."""

import pytest
from csvwrangler.cumulater import cumulate_rows


def _rows(*tuples):
    """Build list-of-dicts from (value,) or (value, extra) tuples."""
    return [{"val": str(t[0]), **({"x": t[1]} if len(t) > 1 else {})} for t in tuples]


# ---------------------------------------------------------------------------
# cumulative sum
# ---------------------------------------------------------------------------

def test_cumulate_sum_basic():
    rows = _rows((1,), (2,), (3,))
    result = list(cumulate_rows(rows, column="val", op="sum"))
    assert [r["cumulative_sum"] for r in result] == ["1", "3", "6"]


def test_cumulate_sum_float():
    rows = [{"val": "1.5"}, {"val": "2.5"}]
    result = list(cumulate_rows(rows, column="val", op="sum"))
    assert result[1]["cumulative_sum"] == "4.0"


def test_cumulate_sum_custom_output_column():
    rows = _rows((10,), (20,))
    result = list(cumulate_rows(rows, column="val", op="sum", output_column="running"))
    assert "running" in result[0]
    assert result[-1]["running"] == "30"


# ---------------------------------------------------------------------------
# cumulative min / max
# ---------------------------------------------------------------------------

def test_cumulate_min():
    rows = _rows((5,), (3,), (7,), (1,))
    result = list(cumulate_rows(rows, column="val", op="min"))
    assert [r["cumulative_min"] for r in result] == ["5", "3", "3", "1"]


def test_cumulate_max():
    rows = _rows((2,), (8,), (5,), (10,))
    result = list(cumulate_rows(rows, column="val", op="max"))
    assert [r["cumulative_max"] for r in result] == ["2", "8", "8", "10"]


# ---------------------------------------------------------------------------
# cumulative product
# ---------------------------------------------------------------------------

def test_cumulate_product():
    rows = _rows((1,), (2,), (3,), (4,))
    result = list(cumulate_rows(rows, column="val", op="product"))
    assert [r["cumulative_product"] for r in result] == ["1", "2", "6", "24"]


# ---------------------------------------------------------------------------
# non-numeric passthrough
# ---------------------------------------------------------------------------

def test_cumulate_non_numeric_passthrough():
    rows = [{"val": "abc"}, {"val": "2"}, {"val": ""}, {"val": "3"}]
    result = list(cumulate_rows(rows, column="val", op="sum"))
    assert result[0]["cumulative_sum"] == ""
    assert result[2]["cumulative_sum"] == ""
    assert result[1]["cumulative_sum"] == "2"
    assert result[3]["cumulative_sum"] == "5"


# ---------------------------------------------------------------------------
# missing column
# ---------------------------------------------------------------------------

def test_cumulate_missing_column_yields_empty():
    rows = [{"other": "1"}, {"other": "2"}]
    result = list(cumulate_rows(rows, column="val", op="sum"))
    assert all(r["cumulative_sum"] == "" for r in result)


# ---------------------------------------------------------------------------
# invalid op
# ---------------------------------------------------------------------------

def test_cumulate_invalid_op_raises():
    with pytest.raises(ValueError, match="Unsupported op"):
        list(cumulate_rows(_rows((1,)), column="val", op="mean"))


# ---------------------------------------------------------------------------
# original columns preserved
# ---------------------------------------------------------------------------

def test_cumulate_preserves_other_columns():
    rows = [{"val": "5", "name": "alice"}, {"val": "3", "name": "bob"}]
    result = list(cumulate_rows(rows, column="val", op="sum"))
    assert result[0]["name"] == "alice"
    assert result[1]["name"] == "bob"
