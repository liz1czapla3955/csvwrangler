import pytest
from csvwrangler.profiler import profile_rows


def _rows(*dicts):
    return list(dicts)


def test_profile_empty_input():
    assert profile_rows([]) == []


def test_profile_column_names():
    rows = _rows({"a": "1", "b": "2"}, {"a": "3", "b": ""})
    result = profile_rows(rows)
    assert [r["column"] for r in result] == ["a", "b"]


def test_profile_count():
    rows = _rows({"x": "a"}, {"x": "b"}, {"x": "c"})
    result = profile_rows(rows)
    assert result[0]["count"] == 3


def test_profile_empty_count():
    rows = _rows({"x": "a"}, {"x": ""}, {"x": ""})
    result = profile_rows(rows)
    assert result[0]["empty"] == 2
    assert result[0]["filled"] == 1


def test_profile_fill_rate():
    rows = _rows({"x": "a"}, {"x": "b"}, {"x": ""}, {"x": ""})
    result = profile_rows(rows)
    assert result[0]["fill_rate"] == "50.00%"


def test_profile_unique():
    rows = _rows({"x": "a"}, {"x": "b"}, {"x": "a"}, {"x": "c"})
    result = profile_rows(rows)
    assert result[0]["unique"] == 3


def test_profile_min_max_len():
    rows = _rows({"x": "hi"}, {"x": "hello"}, {"x": "yo"})
    result = profile_rows(rows)
    assert result[0]["min_len"] == 2
    assert result[0]["max_len"] == 5


def test_profile_all_empty_len():
    rows = _rows({"x": ""}, {"x": ""})
    result = profile_rows(rows)
    assert result[0]["min_len"] == 0
    assert result[0]["max_len"] == 0


def test_profile_multiple_columns():
    rows = _rows({"a": "1", "b": "hello"}, {"a": "22", "b": ""})
    result = profile_rows(rows)
    a = next(r for r in result if r["column"] == "a")
    b = next(r for r in result if r["column"] == "b")
    assert a["unique"] == 2
    assert b["empty"] == 1
