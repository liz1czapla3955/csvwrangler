"""Tests for csvwrangler.uniquifier."""

import pytest
from csvwrangler.uniquifier import uniquify_rows, uniquify_file
import csv
import io


def _rows(*dicts):
    return list(dicts)


SAMPLE = [
    {"id": "1", "city": "London"},
    {"id": "2", "city": "Paris"},
    {"id": "3", "city": "London"},
    {"id": "4", "city": "Berlin"},
]


def test_uniquify_keeps_unique_values():
    result = list(uniquify_rows(SAMPLE, column="city"))
    cities = [r["city"] for r in result]
    assert cities == ["Paris", "Berlin"]


def test_uniquify_invert_keeps_duplicates():
    result = list(uniquify_rows(SAMPLE, column="city", invert=True))
    cities = [r["city"] for r in result]
    assert cities == ["London", "London"]


def test_uniquify_all_unique():
    rows = [
        {"id": "1", "val": "a"},
        {"id": "2", "val": "b"},
        {"id": "3", "val": "c"},
    ]
    result = list(uniquify_rows(rows, column="val"))
    assert len(result) == 3


def test_uniquify_all_duplicates():
    rows = [
        {"id": "1", "val": "x"},
        {"id": "2", "val": "x"},
    ]
    result = list(uniquify_rows(rows, column="val"))
    assert result == []


def test_uniquify_empty_input():
    result = list(uniquify_rows([], column="city"))
    assert result == []


def test_uniquify_missing_column_raises():
    rows = [{"id": "1", "city": "Rome"}]
    with pytest.raises(KeyError, match="country"):
        list(uniquify_rows(rows, column="country"))


def test_uniquify_preserves_row_content():
    result = list(uniquify_rows(SAMPLE, column="city"))
    assert result[0] == {"id": "2", "city": "Paris"}
    assert result[1] == {"id": "4", "city": "Berlin"}


def test_uniquify_file_writes_header_and_rows():
    src = "id,city\n1,London\n2,Paris\n3,London\n4,Berlin\n"
    reader = csv.DictReader(io.StringIO(src))
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=["id", "city"])
    uniquify_file(reader, writer, column="city")
    out.seek(0)
    lines = out.read().splitlines()
    assert lines[0] == "id,city"
    assert len(lines) == 3  # header + Paris + Berlin


def test_uniquify_file_invert():
    src = "id,city\n1,London\n2,Paris\n3,London\n"
    reader = csv.DictReader(io.StringIO(src))
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=["id", "city"])
    uniquify_file(reader, writer, column="city", invert=True)
    out.seek(0)
    result = list(csv.DictReader(out))
    assert all(r["city"] == "London" for r in result)
    assert len(result) == 2
