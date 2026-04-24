"""Unit tests for csvwrangler.chunker."""

import pytest
from csvwrangler.chunker import chunk_rows


def _rows(n):
    return [{"id": str(i), "val": str(i * 10)} for i in range(1, n + 1)]


def test_chunk_rows_even_split():
    result = list(chunk_rows(_rows(6), 2))
    assert len(result) == 3
    assert result[0] == [{"id": "1", "val": "10"}, {"id": "2", "val": "20"}]
    assert result[2] == [{"id": "5", "val": "50"}, {"id": "6", "val": "60"}]


def test_chunk_rows_uneven_split():
    result = list(chunk_rows(_rows(5), 2))
    assert len(result) == 3
    assert len(result[-1]) == 1
    assert result[-1][0]["id"] == "5"


def test_chunk_rows_size_larger_than_input():
    result = list(chunk_rows(_rows(3), 10))
    assert len(result) == 1
    assert len(result[0]) == 3


def test_chunk_rows_size_one():
    result = list(chunk_rows(_rows(4), 1))
    assert len(result) == 4
    for i, chunk in enumerate(result):
        assert len(chunk) == 1
        assert chunk[0]["id"] == str(i + 1)


def test_chunk_rows_empty_input():
    result = list(chunk_rows([], 3))
    assert result == []


def test_chunk_rows_invalid_size_raises():
    with pytest.raises(ValueError, match="chunk size must be >= 1"):
        list(chunk_rows(_rows(5), 0))


def test_chunk_rows_negative_size_raises():
    with pytest.raises(ValueError):
        list(chunk_rows(_rows(5), -2))


def test_chunk_rows_preserves_all_rows():
    data = _rows(10)
    chunks = list(chunk_rows(data, 3))
    flat = [row for chunk in chunks for row in chunk]
    assert flat == data


def test_chunk_rows_exact_multiple():
    result = list(chunk_rows(_rows(9), 3))
    assert len(result) == 3
    assert all(len(c) == 3 for c in result)
