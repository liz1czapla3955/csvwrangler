import pytest
from csvwrangler.crossjoiner import crossjoin_rows


def _rows(data):
    """Helper: list of dicts from list-of-lists (first row = headers)."""
    headers = data[0]
    return [dict(zip(headers, row)) for row in data[1:]]


def test_crossjoin_basic():
    left = _rows([["id"], ["1"], ["2"]])
    right = _rows([["color"], ["red"], ["blue"]])
    result = crossjoin_rows(left, right)
    assert len(result) == 4
    ids = [r["id"] for r in result]
    colors = [r["color"] for r in result]
    assert ids == ["1", "1", "2", "2"]
    assert colors == ["red", "blue", "red", "blue"]


def test_crossjoin_empty_left():
    result = crossjoin_rows([], _rows([["x"], ["1"]]))
    assert result == []


def test_crossjoin_empty_right():
    result = crossjoin_rows(_rows([["x"], ["1"]]), [])
    assert result == []


def test_crossjoin_column_conflict_prefixed():
    left = _rows([["id", "name"], ["1", "Alice"]])
    right = _rows([["id", "city"], ["99", "Paris"]])
    result = crossjoin_rows(left, right, left_prefix="l_", right_prefix="r_")
    assert len(result) == 1
    row = result[0]
    assert "l_id" in row
    assert "r_id" in row
    assert "name" in row
    assert "city" in row
    assert row["l_id"] == "1"
    assert row["r_id"] == "99"


def test_crossjoin_no_conflict_no_prefix():
    left = _rows([["a"], ["x"]])
    right = _rows([["b"], ["y"]])
    result = crossjoin_rows(left, right)
    assert result == [{"a": "x", "b": "y"}]


def test_crossjoin_single_row_each():
    left = _rows([["x"], ["1"]])
    right = _rows([["y"], ["2"]])
    result = crossjoin_rows(left, right)
    assert len(result) == 1
    assert result[0] == {"x": "1", "y": "2"}


def test_crossjoin_three_by_three():
    left = _rows([["n"], ["1"], ["2"], ["3"]])
    right = _rows([["m"], ["a"], ["b"], ["c"]])
    result = crossjoin_rows(left, right)
    assert len(result) == 9
