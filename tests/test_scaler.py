"""Tests for csvwrangler.scaler."""
import pytest
from csvwrangler.scaler import _mean, _stddev, scale_rows


def _rows():
    return [
        {"name": "a", "score": "10", "value": "100"},
        {"name": "b", "score": "20", "value": "200"},
        {"name": "c", "score": "30", "value": "300"},
    ]


def test_mean_basic():
    assert _mean([1.0, 2.0, 3.0]) == 2.0


def test_mean_empty():
    assert _mean([]) == 0.0


def test_stddev_basic():
    result = _stddev([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
    assert abs(result - 2.0) < 1e-9


def test_stddev_single():
    assert _stddev([5.0]) == 0.0


def test_scale_minmax_basic():
    result = scale_rows(_rows(), ["score"])
    scores = [float(r["score"]) for r in result]
    assert scores[0] == pytest.approx(0.0)
    assert scores[1] == pytest.approx(0.5)
    assert scores[2] == pytest.approx(1.0)


def test_scale_minmax_preserves_other_columns():
    result = scale_rows(_rows(), ["score"])
    assert [r["name"] for r in result] == ["a", "b", "c"]
    assert [r["value"] for r in result] == ["100", "200", "300"]


def test_scale_minmax_multiple_columns():
    result = scale_rows(_rows(), ["score", "value"])
    assert float(result[0]["score"]) == pytest.approx(0.0)
    assert float(result[2]["value"]) == pytest.approx(1.0)


def test_scale_zscore_basic():
    result = scale_rows(_rows(), ["score"], method="zscore")
    scores = [float(r["score"]) for r in result]
    assert scores[1] == pytest.approx(0.0)
    assert scores[0] < 0
    assert scores[2] > 0


def test_scale_zscore_mean_zero():
    result = scale_rows(_rows(), ["score"], method="zscore")
    scores = [float(r["score"]) for r in result]
    assert sum(scores) == pytest.approx(0.0, abs=1e-9)


def test_scale_invalid_method():
    with pytest.raises(ValueError, match="Unknown scaling method"):
        scale_rows(_rows(), ["score"], method="log")


def test_scale_non_numeric_passthrough():
    rows = [{"x": "abc"}, {"x": "10"}, {"x": "20"}]
    result = scale_rows(rows, ["x"], method="minmax")
    assert result[0]["x"] == "abc"


def test_scale_empty_input():
    assert scale_rows([], ["score"]) == []


def test_scale_constant_column_minmax():
    rows = [{"v": "5"}, {"v": "5"}, {"v": "5"}]
    result = scale_rows(rows, ["v"], method="minmax")
    assert all(r["v"] == "0.0" for r in result)


def test_scale_constant_column_zscore():
    rows = [{"v": "5"}, {"v": "5"}, {"v": "5"}]
    result = scale_rows(rows, ["v"], method="zscore")
    assert all(r["v"] == "0.0" for r in result)
