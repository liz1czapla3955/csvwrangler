import pytest
from csvwrangler.roller import rolling_rows


def _rows(data):
    keys = data[0]
    return [dict(zip(keys, row)) for row in data[1:]]


SAMPLE = _rows([
    ["id", "val"],
    ["1", "10"],
    ["2", "20"],
    ["3", "30"],
    ["4", "40"],
    ["5", "50"],
])


def test_rolling_mean_window2():
    result = list(rolling_rows(SAMPLE, "val", 2, "mean"))
    assert result[0]["val_rolling_mean"] == "10"
    assert result[1]["val_rolling_mean"] == "15"
    assert result[2]["val_rolling_mean"] == "25"


def test_rolling_sum_window3():
    result = list(rolling_rows(SAMPLE, "val", 3, "sum"))
    assert result[0]["val_rolling_sum"] == "10"
    assert result[1]["val_rolling_sum"] == "30"
    assert result[2]["val_rolling_sum"] == "60"
    assert result[3]["val_rolling_sum"] == "90"


def test_rolling_min():
    result = list(rolling_rows(SAMPLE, "val", 3, "min"))
    assert result[2]["val_rolling_min"] == "10"
    assert result[4]["val_rolling_min"] == "30"


def test_rolling_max():
    result = list(rolling_rows(SAMPLE, "val", 3, "max"))
    assert result[2]["val_rolling_max"] == "30"
    assert result[4]["val_rolling_max"] == "50"


def test_rolling_custom_output_column():
    result = list(rolling_rows(SAMPLE, "val", 2, "mean", output_column="avg"))
    assert "avg" in result[0]
    assert "val_rolling_mean" not in result[0]


def test_rolling_non_numeric_passthrough():
    rows = [{"id": "1", "val": "abc"}, {"id": "2", "val": "20"}]
    result = list(rolling_rows(rows, "val", 2, "mean"))
    assert result[0]["val_rolling_mean"] == ""
    assert result[1]["val_rolling_mean"] == "20"


def test_rolling_invalid_window():
    with pytest.raises(ValueError, match="window"):
        list(rolling_rows(SAMPLE, "val", 0))


def test_rolling_invalid_agg():
    with pytest.raises(ValueError, match="agg"):
        list(rolling_rows(SAMPLE, "val", 2, "median"))


def test_rolling_window_larger_than_data():
    result = list(rolling_rows(SAMPLE, "val", 10, "sum"))
    assert result[-1]["val_rolling_sum"] == "150"


def test_rolling_preserves_other_columns():
    result = list(rolling_rows(SAMPLE, "val", 2, "mean"))
    assert result[0]["id"] == "1"
