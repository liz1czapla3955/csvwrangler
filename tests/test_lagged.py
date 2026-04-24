"""Tests for csvwrangler.lagged."""

import pytest
from csvwrangler.lagged import lag_rows


def _rows():
    return [
        {"id": "1", "val": "10"},
        {"id": "2", "val": "20"},
        {"id": "3", "val": "30"},
        {"id": "4", "val": "40"},
    ]


def test_lag_default_one_period():
    result = list(lag_rows(_rows(), column="val"))
    assert result[0]["val_lag1"] == ""
    assert result[1]["val_lag1"] == "10"
    assert result[2]["val_lag1"] == "20"
    assert result[3]["val_lag1"] == "30"


def test_lag_two_periods():
    result = list(lag_rows(_rows(), column="val", n=2))
    assert result[0]["val_lag2"] == ""
    assert result[1]["val_lag2"] == ""
    assert result[2]["val_lag2"] == "10"
    assert result[3]["val_lag2"] == "20"


def test_lead_one_period():
    result = list(lag_rows(_rows(), column="val", lead=True))
    assert result[0]["val_lead1"] == "20"
    assert result[1]["val_lead1"] == "30"
    assert result[2]["val_lead1"] == "40"
    assert result[3]["val_lead1"] == ""


def test_lead_via_negative_n():
    result = list(lag_rows(_rows(), column="val", n=-1))
    assert result[0]["val_lead1"] == "20"
    assert result[3]["val_lead1"] == ""


def test_custom_output_column():
    result = list(lag_rows(_rows(), column="val", output_column="prev_val"))
    assert "prev_val" in result[0]
    assert result[1]["prev_val"] == "10"


def test_custom_fill_value():
    result = list(lag_rows(_rows(), column="val", fill="N/A"))
    assert result[0]["val_lag1"] == "N/A"


def test_original_columns_preserved():
    result = list(lag_rows(_rows(), column="val"))
    for row in result:
        assert "id" in row
        assert "val" in row


def test_empty_input():
    result = list(lag_rows([], column="val"))
    assert result == []


def test_single_row_lag():
    rows = [{"x": "5"}]
    result = list(lag_rows(rows, column="x"))
    assert result[0]["x_lag1"] == ""


def test_single_row_lead():
    rows = [{"x": "5"}]
    result = list(lag_rows(rows, column="x", lead=True))
    assert result[0]["x_lead1"] == ""


def test_lag_zero_periods():
    result = list(lag_rows(_rows(), column="val", n=0))
    # lag by 0 means same row
    assert result[0]["val_lag0"] == "10"
    assert result[3]["val_lag0"] == "40"
