"""Tests for csvwrangler.zipper."""
import pytest
from csvwrangler.zipper import zip_rows


ROWS_A = [
    {"id": "1", "name": "Alice"},
    {"id": "2", "name": "Bob"},
    {"id": "3", "name": "Carol"},
]

ROWS_B = [
    {"id": "1", "score": "90"},
    {"id": "2", "score": "85"},
    {"id": "3", "score": "78"},
]


def test_zip_position_basic():
    result = zip_rows(ROWS_A, ROWS_B, how="position")
    assert len(result) == 3
    assert result[0]["name"] == "Alice"
    assert result[0]["score"] == "90"


def test_zip_position_conflict_renamed():
    a = [{"id": "1", "val": "a"}]
    b = [{"id": "2", "val": "b"}]
    result = zip_rows(a, b, how="position")
    assert result[0]["val"] == "a"
    assert result[0]["val_b"] == "b"


def test_zip_position_truncates_to_shorter():
    a = ROWS_A[:2]
    result = zip_rows(a, ROWS_B, how="position")
    assert len(result) == 2


def test_zip_key_inner():
    result = zip_rows(ROWS_A, ROWS_B, how="key", key="id")
    assert len(result) == 3
    assert result[1]["name"] == "Bob"
    assert result[1]["score"] == "85"


def test_zip_key_filters_unmatched():
    a = ROWS_A  # ids 1,2,3
    b = [{"id": "1", "score": "90"}, {"id": "4", "score": "55"}]
    result = zip_rows(a, b, how="key", key="id")
    assert len(result) == 1
    assert result[0]["id"] == "1"


def test_zip_left_keeps_all_a():
    a = ROWS_A
    b = [{"id": "1", "score": "90"}]
    result = zip_rows(a, b, how="left", key="id")
    assert len(result) == 3
    assert result[0]["score"] == "90"
    assert result[1]["score"] == ""
    assert result[2]["score"] == ""


def test_zip_left_requires_key():
    with pytest.raises(ValueError, match="key"):
        zip_rows(ROWS_A, ROWS_B, how="left", key=None)


def test_zip_key_requires_key():
    with pytest.raises(ValueError, match="key"):
        zip_rows(ROWS_A, ROWS_B, how="key", key=None)


def test_zip_invalid_how():
    with pytest.raises(ValueError, match="Unknown how"):
        zip_rows(ROWS_A, ROWS_B, how="outer")


def test_zip_empty_inputs():
    result = zip_rows([], [], how="position")
    assert result == []
