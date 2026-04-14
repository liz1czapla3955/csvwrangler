"""Tests for csvwrangler.deduplicator module."""

import csv
import os
import tempfile

import pytest

from csvwrangler.deduplicator import (
    _row_hash,
    deduplicate_file,
    deduplicate_rows,
)


SAMPLE_ROWS = [
    {"id": "1", "name": "Alice", "city": "NYC"},
    {"id": "2", "name": "Bob", "city": "LA"},
    {"id": "1", "name": "Alice", "city": "NYC"},  # exact duplicate of row 0
    {"id": "3", "name": "Charlie", "city": "NYC"},
    {"id": "2", "name": "Bob", "city": "SF"},    # same id/name, different city
]


def test_row_hash_all_fields():
    row = {"a": "1", "b": "2"}
    h1 = _row_hash(row)
    h2 = _row_hash({"a": "1", "b": "2"})
    assert h1 == h2


def test_row_hash_key_fields():
    row1 = {"id": "1", "name": "Alice", "city": "NYC"}
    row2 = {"id": "1", "name": "Alice", "city": "LA"}
    assert _row_hash(row1, ["id", "name"]) == _row_hash(row2, ["id", "name"])
    assert _row_hash(row1) != _row_hash(row2)


def test_deduplicate_rows_all_fields_keep_first():
    result = deduplicate_rows(SAMPLE_ROWS)
    assert len(result) == 4  # row index 2 is a duplicate of row 0
    assert result[0] == {"id": "1", "name": "Alice", "city": "NYC"}


def test_deduplicate_rows_all_fields_keep_last():
    result = deduplicate_rows(SAMPLE_ROWS, keep="last")
    assert len(result) == 4


def test_deduplicate_rows_key_fields():
    result = deduplicate_rows(SAMPLE_ROWS, key_fields=["id", "name"], keep="first")
    assert len(result) == 3  # ids 1, 2, 3


def test_deduplicate_rows_key_fields_keep_last():
    result = deduplicate_rows(SAMPLE_ROWS, key_fields=["id", "name"], keep="last")
    bob = next(r for r in result if r["name"] == "Bob")
    assert bob["city"] == "SF"  # last occurrence wins


def test_deduplicate_rows_invalid_keep():
    with pytest.raises(ValueError, match="keep must be"):
        deduplicate_rows(SAMPLE_ROWS, keep="none")


def test_deduplicate_rows_empty():
    assert deduplicate_rows([]) == []


def _write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_deduplicate_file():
    fieldnames = ["id", "name", "city"]
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "input.csv")
        output_path = os.path.join(tmpdir, "output.csv")
        _write_csv(input_path, SAMPLE_ROWS, fieldnames)

        original, deduped = deduplicate_file(input_path, output_path)

        assert original == 5
        assert deduped == 4

        with open(output_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            result_rows = list(reader)
        assert len(result_rows) == 4
        assert result_rows[0]["name"] == "Alice"
