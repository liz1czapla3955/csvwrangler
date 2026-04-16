"""Tests for csvwrangler.caster."""
import pytest
from csvwrangler.caster import _cast_value, cast_rows, cast_file


def test_cast_value_int():
    assert _cast_value("42", "int") == "42"
    assert _cast_value("3.9", "int") == "3"


def test_cast_value_float():
    assert _cast_value("3", "float") == "3.0"
    assert _cast_value("1.5", "float") == "1.5"


def test_cast_value_bool_true():
    for v in ("1", "true", "yes", "True", "YES"):
        assert _cast_value(v, "bool") == "true"


def test_cast_value_bool_false():
    for v in ("0", "false", "no", "False"):
        assert _cast_value(v, "bool") == "false"


def test_cast_value_bool_invalid():
    with pytest.raises(ValueError):
        _cast_value("maybe", "bool")


def test_cast_value_str():
    assert _cast_value("hello", "str") == "hello"


def test_cast_value_unsupported_type():
    with pytest.raises(ValueError, match="Unsupported type"):
        _cast_value("x", "datetime")


def test_cast_rows_basic():
    rows = [{"age": "25", "score": "9.5", "name": "Alice"}]
    result = list(cast_rows(rows, {"age": "int", "score": "float"}))
    assert result[0]["age"] == "25"
    assert result[0]["score"] == "9.5"
    assert result[0]["name"] == "Alice"


def test_cast_rows_missing_column_skipped():
    rows = [{"a": "1"}]
    result = list(cast_rows(rows, {"b": "int"}))
    assert result[0] == {"a": "1"}


def test_cast_rows_errors_raise():
    rows = [{"x": "abc"}]
    with pytest.raises((ValueError, TypeError)):
        list(cast_rows(rows, {"x": "int"}, errors="raise"))


def test_cast_rows_errors_ignore():
    rows = [{"x": "abc"}]
    result = list(cast_rows(rows, {"x": "int"}, errors="ignore"))
    assert result[0]["x"] == "abc"


def test_cast_file_roundtrip():
    csv_text = "name,age,score\nAlice,25,9.5\nBob,30,8.0\n"
    result = cast_file(csv_text, {"age": "int", "score": "float"})
    lines = result.strip().splitlines()
    assert lines[0] == "name,age,score"
    assert "Alice" in lines[1]
    assert "25" in lines[1]


def test_cast_file_bool_column():
    csv_text = "name,active\nAlice,true\nBob,false\n"
    result = cast_file(csv_text, {"active": "bool"})
    assert "true" in result
    assert "false" in result
