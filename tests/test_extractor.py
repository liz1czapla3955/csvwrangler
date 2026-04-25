"""Tests for csvwrangler.extractor."""
import pytest
from csvwrangler.extractor import extract_rows


def _rows():
    return [
        {"id": "1", "name": "Alice", "email": "alice@example.com"},
        {"id": "2", "name": "Bob",   "email": "bob@work.org"},
        {"id": "3", "name": "Carol", "email": "carol@example.com"},
        {"id": "4", "name": "Dave",  "email": "dave@nowhere.net"},
    ]


def test_extract_basic_match():
    result = list(extract_rows(_rows(), ["email"], r"example\.com"))
    assert len(result) == 2
    assert result[0]["name"] == "Alice"
    assert result[1]["name"] == "Carol"


def test_extract_invert():
    result = list(extract_rows(_rows(), ["email"], r"example\.com", invert=True))
    assert len(result) == 2
    assert {r["name"] for r in result} == {"Bob", "Dave"}


def test_extract_multiple_columns():
    rows = [
        {"a": "hello", "b": "world"},
        {"a": "foo",   "b": "bar"},
        {"a": "baz",   "b": "hello"},
    ]
    result = list(extract_rows(rows, ["a", "b"], r"hello"))
    assert len(result) == 2
    assert result[0]["a"] == "hello"
    assert result[1]["b"] == "hello"


def test_extract_no_match_returns_empty():
    result = list(extract_rows(_rows(), ["name"], r"Zara"))
    assert result == []


def test_extract_all_match():
    result = list(extract_rows(_rows(), ["id"], r"\d"))
    assert len(result) == 4


def test_extract_output_column_full_match():
    rows = [{"val": "price: 42 dollars"}, {"val": "no number here"}]
    result = list(extract_rows(rows, ["val"], r"\d+", output_column="extracted"))
    assert len(result) == 1
    assert result[0]["extracted"] == "42"


def test_extract_output_column_capture_group():
    rows = [
        {"email": "alice@example.com"},
        {"email": "bob@work.org"},
    ]
    result = list(extract_rows(rows, ["email"], r"@([\w.]+)", output_column="domain"))
    assert len(result) == 2
    assert result[0]["domain"] == "example.com"
    assert result[1]["domain"] == "work.org"


def test_extract_invert_with_output_column():
    rows = [
        {"val": "abc123"},
        {"val": "nope"},
    ]
    result = list(extract_rows(rows, ["val"], r"\d+", invert=True, output_column="captured"))
    assert len(result) == 1
    assert result[0]["val"] == "nope"
    # invert=True means no match, so captured should be empty
    assert result[0]["captured"] == ""


def test_extract_missing_column_treated_as_empty():
    rows = [{"a": "hello"}, {"a": "world"}]
    # column 'b' does not exist — should not raise, just not match on it
    result = list(extract_rows(rows, ["b"], r"hello"))
    assert result == []


def test_extract_preserves_row_content():
    result = list(extract_rows(_rows(), ["name"], r"^Alice$"))
    assert len(result) == 1
    assert result[0] == {"id": "1", "name": "Alice", "email": "alice@example.com"}
