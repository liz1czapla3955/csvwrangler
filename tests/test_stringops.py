"""Tests for csvwrangler.stringops."""

import pytest
from csvwrangler.stringops import _apply_op, stringops_rows


def test_apply_op_upper():
    assert _apply_op("hello", "upper") == "HELLO"


def test_apply_op_lower():
    assert _apply_op("HELLO", "lower") == "hello"


def test_apply_op_strip():
    assert _apply_op("  hi  ", "strip") == "hi"


def test_apply_op_lstrip():
    assert _apply_op("  hi  ", "lstrip") == "hi  "


def test_apply_op_rstrip():
    assert _apply_op("  hi  ", "rstrip") == "  hi"


def test_apply_op_title():
    assert _apply_op("hello world", "title") == "Hello World"


def test_apply_op_replace():
    assert _apply_op("foo bar", "replace", "foo:baz") == "baz bar"


def test_apply_op_replace_bad_arg():
    with pytest.raises(ValueError, match="replace arg"):
        _apply_op("foo", "replace", "nodivider")


def test_apply_op_prefix():
    assert _apply_op("world", "prefix", "hello_") == "hello_world"


def test_apply_op_suffix():
    assert _apply_op("hello", "suffix", "_world") == "hello_world"


def test_apply_op_zfill():
    assert _apply_op("42", "zfill", "5") == "00042"


def test_apply_op_zfill_bad_arg():
    with pytest.raises(ValueError, match="zfill arg"):
        _apply_op("42", "zfill", "abc")


def test_apply_op_unknown():
    with pytest.raises(ValueError, match="Unknown string op"):
        _apply_op("x", "explode")


def _rows(*dicts):
    return list(dicts)


def test_stringops_rows_upper():
    rows = [{"name": "alice", "age": "30"}, {"name": "bob", "age": "25"}]
    result = list(stringops_rows(rows, "name", "upper"))
    assert result[0]["name"] == "ALICE"
    assert result[1]["name"] == "BOB"
    assert result[0]["age"] == "30"


def test_stringops_rows_missing_column():
    rows = [{"name": "alice"}]
    result = list(stringops_rows(rows, "missing", "upper"))
    assert result[0] == {"name": "alice"}


def test_stringops_rows_replace():
    rows = [{"city": "New York"}, {"city": "New Jersey"}]
    result = list(stringops_rows(rows, "city", "replace", "New:Old"))
    assert result[0]["city"] == "Old York"
    assert result[1]["city"] == "Old Jersey"


def test_stringops_rows_zfill():
    rows = [{"id": "7"}, {"id": "42"}]
    result = list(stringops_rows(rows, "id", "zfill", "4"))
    assert result[0]["id"] == "0007"
    assert result[1]["id"] == "0042"
