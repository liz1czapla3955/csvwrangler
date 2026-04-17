"""Tests for csvwrangler.clipper."""

import pytest
from csvwrangler.clipper import _clip_value, clip_rows


def _rows():
    return [
        {"name": "a", "score": "5", "value": "100"},
        {"name": "b", "score": "-3", "value": "50"},
        {"name": "c", "score": "12", "value": "0"},
        {"name": "d", "score": "7", "value": "75"},
    ]


def test_clip_value_below_low():
    assert _clip_value("2", 5.0, 10.0) == "5"


def test_clip_value_above_high():
    assert _clip_value("15", 5.0, 10.0) == "10"


def test_clip_value_within_range():
    assert _clip_value("7", 5.0, 10.0) == "7"


def test_clip_value_non_numeric_passthrough():
    assert _clip_value("abc", 0.0, 10.0) == "abc"


def test_clip_value_float_string():
    assert _clip_value("3.5", 4.0, 8.0) == "4.0"


def test_clip_value_only_low():
    assert _clip_value("-10", -5.0, None) == "-5"


def test_clip_value_only_high():
    assert _clip_value("999", None, 100.0) == "100"


def test_clip_rows_low_and_high():
    result = list(clip_rows(_rows(), columns=["score"], low=0.0, high=10.0))
    scores = [r["score"] for r in result]
    assert scores == ["5", "0", "10", "7"]


def test_clip_rows_only_low():
    result = list(clip_rows(_rows(), columns=["score"], low=0.0))
    scores = [r["score"] for r in result]
    assert scores == ["5", "0", "12", "7"]


def test_clip_rows_only_high():
    result = list(clip_rows(_rows(), columns=["value"], high=60.0))
    values = [r["value"] for r in result]
    assert values == ["60", "50", "0", "60"]


def test_clip_rows_multiple_columns():
    result = list(clip_rows(_rows(), columns=["score", "value"], low=0.0, high=60.0))
    assert result[0]["score"] == "5"
    assert result[0]["value"] == "60"
    assert result[1]["score"] == "0"


def test_clip_rows_unknown_column_ignored():
    result = list(clip_rows(_rows(), columns=["nonexistent"], low=0.0, high=10.0))
    assert result[0] == {"name": "a", "score": "5", "value": "100"}


def test_clip_rows_no_bounds_raises():
    with pytest.raises(ValueError, match="At least one"):
        list(clip_rows(_rows(), columns=["score"]))


def test_clip_rows_preserves_other_columns():
    result = list(clip_rows(_rows(), columns=["score"], low=0.0, high=10.0))
    assert [r["name"] for r in result] == ["a", "b", "c", "d"]
    assert [r["value"] for r in result] == ["100", "50", "0", "75"]
