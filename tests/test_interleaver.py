"""Unit tests for csvwrangler.interleaver."""

import pytest

from csvwrangler.interleaver import interleave_rows


def _rows(data):
    """Build list-of-dicts from a list-of-lists where first list is headers."""
    headers, *body = data
    return [dict(zip(headers, row)) for row in body]


ROWS_A = _rows([["id", "val"], ["1", "a"], ["2", "b"], ["3", "c"]])
ROWS_B = _rows([["id", "val"], ["4", "d"], ["5", "e"], ["6", "f"]])


def test_interleave_basic_alternates():
    result = interleave_rows(ROWS_A, ROWS_B)
    ids = [r["id"] for r in result]
    assert ids == ["1", "4", "2", "5", "3", "6"]


def test_interleave_basic_length():
    result = interleave_rows(ROWS_A, ROWS_B)
    assert len(result) == 6


def test_interleave_no_fill_truncates_to_shorter():
    short = _rows([["id", "val"], ["4", "d"]])
    result = interleave_rows(ROWS_A, short)
    assert len(result) == 2
    assert result[0]["id"] == "1"
    assert result[1]["id"] == "4"


def test_interleave_fill_extends_shorter_a():
    short_a = _rows([["id", "val"], ["1", "a"]])
    result = interleave_rows(short_a, ROWS_B, fill=True)
    ids = [r["id"] for r in result]
    # short_a has 1 row, ROWS_B has 3 → 6 total with fill
    assert len(result) == 6
    # Second pair: fill row from A, then "5" from B
    assert ids[2] == ""  # fill row for A
    assert ids[3] == "5"


def test_interleave_fill_extends_shorter_b():
    short_b = _rows([["id", "val"], ["4", "d"]])
    result = interleave_rows(ROWS_A, short_b, fill=True)
    assert len(result) == 6
    ids = [r["id"] for r in result]
    assert ids[3] == ""  # fill row for B after first pair


def test_interleave_fill_value_applied():
    short_a = _rows([["id", "val"], ["1", "a"]])
    result = interleave_rows(short_a, ROWS_B, fill=True, fill_value="N/A")
    fill_rows = [r for r in result if r["id"] == "N/A"]
    assert len(fill_rows) == 2  # two missing A rows filled


def test_interleave_both_empty():
    result = interleave_rows([], [])
    assert result == []


def test_interleave_a_empty_no_fill():
    result = interleave_rows([], ROWS_B)
    assert result == []


def test_interleave_b_empty_no_fill():
    result = interleave_rows(ROWS_A, [])
    assert result == []


def test_interleave_a_empty_fill():
    result = interleave_rows([], ROWS_B, fill=True)
    # fill pads A side; result should contain B rows interleaved with fill rows
    assert len(result) == 6
    b_ids = [r["id"] for r in result[1::2]]
    assert b_ids == ["4", "5", "6"]


def test_interleave_preserves_field_values():
    result = interleave_rows(ROWS_A, ROWS_B)
    assert result[0] == {"id": "1", "val": "a"}
    assert result[1] == {"id": "4", "val": "d"}
