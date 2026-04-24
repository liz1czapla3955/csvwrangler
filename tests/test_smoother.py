"""Tests for csvwrangler.smoother."""

import pytest
from csvwrangler.smoother import smooth_rows, smooth_file
import csv
import io


def _rows(*dicts):
    return list(dicts)


# ---------------------------------------------------------------------------
# smooth_rows
# ---------------------------------------------------------------------------

def test_smooth_rows_single_value():
    rows = _rows({"x": "10"})
    result = smooth_rows(rows, "x", alpha=0.5)
    assert result[0]["x_ema"] == "10"


def test_smooth_rows_two_values_alpha_one():
    """With alpha=1, EMA equals the current value."""
    rows = _rows({"x": "5"}, {"x": "15"})
    result = smooth_rows(rows, "x", alpha=1.0)
    assert result[0]["x_ema"] == "5"
    assert result[1]["x_ema"] == "15"


def test_smooth_rows_ema_calculation():
    """EMA(t) = alpha*v + (1-alpha)*EMA(t-1)."""
    rows = _rows({"v": "10"}, {"v": "20"}, {"v": "30"})
    result = smooth_rows(rows, "v", alpha=0.5)
    ema0 = 10.0
    ema1 = 0.5 * 20 + 0.5 * ema0  # 15
    ema2 = 0.5 * 30 + 0.5 * ema1  # 22.5
    assert float(result[0]["v_ema"]) == pytest.approx(ema0)
    assert float(result[1]["v_ema"]) == pytest.approx(ema1)
    assert float(result[2]["v_ema"]) == pytest.approx(ema2)


def test_smooth_rows_non_numeric_passthrough():
    rows = _rows({"x": "hello"}, {"x": "10"})
    result = smooth_rows(rows, "x", alpha=0.5)
    assert result[0]["x_ema"] == "hello"
    # EMA resets on next numeric value
    assert float(result[1]["x_ema"]) == pytest.approx(10.0)


def test_smooth_rows_custom_output_column():
    rows = _rows({"price": "100"}, {"price": "200"})
    result = smooth_rows(rows, "price", alpha=0.3, output_column="price_smooth")
    assert "price_smooth" in result[0]
    assert "price_ema" not in result[0]


def test_smooth_rows_preserves_other_columns():
    rows = _rows({"id": "1", "val": "5"}, {"id": "2", "val": "10"})
    result = smooth_rows(rows, "val", alpha=0.5)
    assert result[0]["id"] == "1"
    assert result[1]["id"] == "2"


def test_smooth_rows_invalid_alpha_raises():
    with pytest.raises(ValueError, match="alpha must be in"):
        smooth_rows([], "x", alpha=0.0)


def test_smooth_rows_alpha_gt_one_raises():
    with pytest.raises(ValueError):
        smooth_rows([], "x", alpha=1.5)


def test_smooth_rows_missing_column_passthrough():
    rows = _rows({"a": "1"}, {"a": "2"})
    result = smooth_rows(rows, "b", alpha=0.5)
    # missing column returns empty string passthrough
    assert result[0]["b_ema"] == ""
    assert result[1]["b_ema"] == ""


# ---------------------------------------------------------------------------
# smooth_file
# ---------------------------------------------------------------------------

class ListWriter:
    def __init__(self):
        self.fieldnames = None
        self.rows = []

    def writeheader(self):
        self.rows.append(self.fieldnames)

    def writerow(self, row):
        self.rows.append(row)


def _make_reader(data: str) -> csv.DictReader:
    return csv.DictReader(io.StringIO(data))


def test_smooth_file_basic():
    data = "val\n10\n20\n30\n"
    reader = _make_reader(data)
    writer = ListWriter()
    smooth_file(reader, writer, column="val", alpha=1.0)
    assert writer.fieldnames == ["val", "val_ema"]
    assert writer.rows[1]["val_ema"] == "10"
    assert writer.rows[2]["val_ema"] == "20"
    assert writer.rows[3]["val_ema"] == "30"


def test_smooth_file_empty_input():
    reader = _make_reader("val\n")
    writer = ListWriter()
    smooth_file(reader, writer, column="val", alpha=0.5)
    # No rows written — writeheader never called
    assert writer.rows == []
