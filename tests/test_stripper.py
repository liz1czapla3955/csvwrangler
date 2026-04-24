"""Tests for csvwrangler.stripper."""

import pytest
from csvwrangler.stripper import strip_rows


def _rows(*dicts):
    return list(dicts)


ROW_A = {"id": "1", "name": "Alice"}
ROW_B = {"id": "2", "name": "Bob"}
ROW_C = {"id": "3", "name": "Carol"}
ROW_BLANK = {"id": "", "name": ""}
ROW_COMMENT = {"id": "# comment", "name": ""}


def test_strip_blank_rows_removed():
    result = strip_rows([ROW_A, ROW_BLANK, ROW_B])
    assert result == [ROW_A, ROW_B]


def test_strip_blank_rows_all_blank():
    result = strip_rows([ROW_BLANK, ROW_BLANK])
    assert result == []


def test_no_strip_blank_keeps_blank_rows():
    result = strip_rows([ROW_A, ROW_BLANK, ROW_B], strip_blank=False)
    assert len(result) == 3
    assert ROW_BLANK in result


def test_strip_comment_rows():
    result = strip_rows([ROW_COMMENT, ROW_A, ROW_B], comment_prefix="#")
    assert ROW_COMMENT not in result
    assert ROW_A in result


def test_strip_comment_prefix_no_match_kept():
    result = strip_rows([ROW_A, ROW_B], comment_prefix="#")
    assert result == [ROW_A, ROW_B]


def test_strip_comment_prefix_none_does_nothing():
    rows = [ROW_COMMENT, ROW_A]
    result = strip_rows(rows, strip_blank=False, comment_prefix=None)
    assert ROW_COMMENT in result


def test_strip_head_removes_first_n():
    result = strip_rows([ROW_A, ROW_B, ROW_C], strip_blank=False, head=1)
    assert result == [ROW_B, ROW_C]


def test_strip_head_more_than_rows():
    result = strip_rows([ROW_A, ROW_B], strip_blank=False, head=5)
    assert result == []


def test_strip_tail_removes_last_n():
    result = strip_rows([ROW_A, ROW_B, ROW_C], strip_blank=False, tail=1)
    assert result == [ROW_A, ROW_B]


def test_strip_tail_more_than_rows():
    result = strip_rows([ROW_A, ROW_B], strip_blank=False, tail=10)
    assert result == []


def test_strip_head_and_tail_combined():
    result = strip_rows([ROW_A, ROW_B, ROW_C], strip_blank=False, head=1, tail=1)
    assert result == [ROW_B]


def test_strip_empty_input():
    assert strip_rows([]) == []


def test_strip_blank_and_comment_combined():
    rows = [ROW_COMMENT, ROW_BLANK, ROW_A, ROW_B]
    result = strip_rows(rows, strip_blank=True, comment_prefix="#")
    assert result == [ROW_A, ROW_B]


def test_strip_whitespace_only_values_treated_as_blank():
    row_ws = {"id": "  ", "name": "\t"}
    result = strip_rows([row_ws, ROW_A])
    assert result == [ROW_A]
