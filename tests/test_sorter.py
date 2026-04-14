"""Tests for csvwrangler.sorter."""

import csv
import os
import tempfile

import pytest

from csvwrangler.sorter import sort_rows, sort_file


ROWS = [
    {"name": "Charlie", "age": "30", "score": "88.5"},
    {"name": "Alice", "age": "25", "score": "95.0"},
    {"name": "Bob", "age": "25", "score": "70.0"},
    {"name": "Diana", "age": "35", "score": "88.5"},
]


def test_sort_rows_single_key_ascending():
    result = sort_rows(ROWS, keys=["name"])
    assert [r["name"] for r in result] == ["Alice", "Bob", "Charlie", "Diana"]


def test_sort_rows_single_key_descending():
    result = sort_rows(ROWS, keys=["name"], reverse=True)
    assert [r["name"] for r in result] == ["Diana", "Charlie", "Bob", "Alice"]


def test_sort_rows_numeric():
    result = sort_rows(ROWS, keys=["score"], numeric=True)
    assert [r["score"] for r in result] == ["70.0", "88.5", "88.5", "95.0"]


def test_sort_rows_multi_key():
    result = sort_rows(ROWS, keys=["age", "name"])
    names = [r["name"] for r in result]
    # age 25 first (Alice before Bob), then 30, then 35
    assert names == ["Alice", "Bob", "Charlie", "Diana"]


def test_sort_rows_numeric_descending():
    result = sort_rows(ROWS, keys=["age"], numeric=True, reverse=True)
    assert result[0]["name"] == "Diana"
    assert result[-1]["name"] in {"Alice", "Bob"}


def test_sort_rows_empty():
    assert sort_rows([], keys=["name"]) == []


def test_sort_rows_missing_key():
    with pytest.raises(KeyError, match="nonexistent"):
        sort_rows(ROWS, keys=["nonexistent"])


def _write_csv(rows, fieldnames, delimiter=","):
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, newline="", encoding="utf-8"
    )
    writer = csv.DictWriter(tmp, fieldnames=fieldnames, delimiter=delimiter)
    writer.writeheader()
    writer.writerows(rows)
    tmp.close()
    return tmp.name


def test_sort_file_ascending():
    src = _write_csv(ROWS, ["name", "age", "score"])
    dst = src + ".out.csv"
    try:
        count = sort_file(src, dst, keys=["name"])
        assert count == 4
        with open(dst, newline="", encoding="utf-8") as fh:
            result = list(csv.DictReader(fh))
        assert [r["name"] for r in result] == ["Alice", "Bob", "Charlie", "Diana"]
    finally:
        os.unlink(src)
        if os.path.exists(dst):
            os.unlink(dst)


def test_sort_file_missing_key():
    src = _write_csv(ROWS, ["name", "age", "score"])
    dst = src + ".out.csv"
    try:
        with pytest.raises(KeyError):
            sort_file(src, dst, keys=["missing"])
    finally:
        os.unlink(src)
        if os.path.exists(dst):
            os.unlink(dst)
