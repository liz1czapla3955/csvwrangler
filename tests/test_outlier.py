import pytest
from csvwrangler.outlier import detect_outliers, _mean, _stddev


ROWS = [
    {"id": "1", "value": "10"},
    {"id": "2", "value": "12"},
    {"id": "3", "value": "11"},
    {"id": "4", "value": "13"},
    {"id": "5", "value": "100"},  # outlier
]


def test_mean_basic():
    assert _mean([1.0, 2.0, 3.0]) == pytest.approx(2.0)


def test_mean_empty():
    assert _mean([]) == 0.0


def test_stddev_basic():
    assert _stddev([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0], 5.0) == pytest.approx(2.0)


def test_stddev_single():
    assert _stddev([5.0], 5.0) == 0.0


def test_detect_outliers_filters_outlier():
    result = list(detect_outliers(ROWS, "value", threshold=2.0))
    ids = [r["id"] for r in result]
    assert "5" not in ids
    assert "1" in ids


def test_detect_outliers_keeps_all_below_threshold():
    result = list(detect_outliers(ROWS, "value", threshold=10.0))
    assert len(result) == 5


def test_detect_outliers_mark_mode():
    result = list(detect_outliers(ROWS, "value", threshold=2.0, mark=True))
    assert len(result) == 5
    marked = {r["id"]: r["is_outlier"] for r in result}
    assert marked["5"] == "1"
    assert marked["1"] == "0"


def test_detect_outliers_custom_mark_column():
    result = list(detect_outliers(ROWS, "value", threshold=2.0, mark=True, mark_column="outlier_flag"))
    assert "outlier_flag" in result[0]


def test_detect_outliers_non_numeric_skipped():
    rows = [{"id": "1", "value": "abc"}, {"id": "2", "value": "10"}]
    result = list(detect_outliers(rows, "value", threshold=1.0))
    assert len(result) == 2


def test_detect_outliers_missing_column_passthrough():
    rows = [{"id": "1", "x": "5"}, {"id": "2", "x": "6"}]
    result = list(detect_outliers(rows, "value"))
    assert len(result) == 2


def test_detect_outliers_empty_input():
    result = list(detect_outliers([], "value"))
    assert result == []
