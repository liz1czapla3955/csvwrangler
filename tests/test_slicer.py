import pytest
from csvwrangler.slicer import slice_rows


ROWS = [
    {"id": "1", "val": "a"},
    {"id": "2", "val": "b"},
    {"id": "3", "val": "c"},
    {"id": "4", "val": "d"},
    {"id": "5", "val": "e"},
]


def test_slice_default_returns_all():
    assert slice_rows(ROWS) == ROWS


def test_slice_start_only():
    result = slice_rows(ROWS, start=2)
    assert [r["id"] for r in result] == ["3", "4", "5"]


def test_slice_stop_only():
    result = slice_rows(ROWS, stop=3)
    assert [r["id"] for r in result] == ["1", "2", "3"]


def test_slice_start_and_stop():
    result = slice_rows(ROWS, start=1, stop=4)
    assert [r["id"] for r in result] == ["2", "3", "4"]


def test_slice_step_two():
    result = slice_rows(ROWS, step=2)
    assert [r["id"] for r in result] == ["1", "3", "5"]


def test_slice_negative_step_reverses():
    result = slice_rows(ROWS, step=-1)
    assert [r["id"] for r in result] == ["5", "4", "3", "2", "1"]


def test_slice_empty_input():
    assert slice_rows([]) == []


def test_slice_out_of_range_stop():
    result = slice_rows(ROWS, start=3, stop=100)
    assert [r["id"] for r in result] == ["4", "5"]


def test_slice_start_equals_stop_returns_empty():
    result = slice_rows(ROWS, start=2, stop=2)
    assert result == []


def test_slice_zero_step_raises():
    with pytest.raises(ValueError, match="step cannot be zero"):
        slice_rows(ROWS, step=0)


def test_slice_negative_start():
    result = slice_rows(ROWS, start=-2)
    assert [r["id"] for r in result] == ["4", "5"]
