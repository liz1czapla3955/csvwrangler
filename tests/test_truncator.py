"""Tests for csvwrangler.truncator."""

import csv
import os
import tempfile

import pytest

from csvwrangler.truncator import truncate_rows, truncate_file


ROWS = [
    {"name": "Alice", "bio": "A software engineer", "city": "New York"},
    {"name": "Bob", "bio": "Data scientist and researcher", "city": "LA"},
    {"name": "Charlie", "bio": "Short", "city": "Chicago"},
]


def test_truncate_rows_all_columns():
    result = truncate_rows(ROWS, max_length=6)
    assert result[0]["name"] == "Alice"
    assert result[0]["bio"] == "A so..."
    assert result[1]["bio"] == "Data ..."
    assert result[2]["bio"] == "Short"


def test_truncate_rows_specific_columns():
    result = truncate_rows(ROWS, max_length=8, columns=["bio"])
    assert result[0]["name"] == "Alice"  # untouched
    assert result[0]["bio"] == "A soft..."
    assert result[1]["city"] == "LA"  # untouched


def test_truncate_rows_custom_placeholder():
    result = truncate_rows(ROWS, max_length=7, placeholder="--")
    assert result[0]["bio"] == "A soft--"


def test_truncate_rows_no_truncation_needed():
    result = truncate_rows(ROWS, max_length=100)
    assert result[0]["bio"] == "A software engineer"
    assert result[1]["bio"] == "Data scientist and researcher"


def test_truncate_rows_exact_length():
    result = truncate_rows(ROWS, max_length=5)
    assert result[0]["name"] == "Alice"  # exactly 5, not truncated
    assert result[2]["name"] == "Ch..."


def test_truncate_rows_empty_input():
    assert truncate_rows([], max_length=10) == []


def test_truncate_rows_placeholder_too_long():
    with pytest.raises(ValueError, match="max_length"):
        truncate_rows(ROWS, max_length=2, placeholder="...")


def test_truncate_rows_preserves_all_keys():
    result = truncate_rows(ROWS, max_length=10)
    for row, original in zip(result, ROWS):
        assert set(row.keys()) == set(original.keys())


def test_truncate_rows_does_not_mutate_input():
    """Ensure truncate_rows returns new dicts and does not modify the originals."""
    import copy
    original = copy.deepcopy(ROWS)
    truncate_rows(ROWS, max_length=6)
    assert ROWS == original


def test_truncate_file(tmp_path):
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.csv"

    with open(input_file, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["name", "bio", "city"])
        writer.writeheader()
        writer.writerows(ROWS)

    truncate_file(str(input_file), str(output_file), max_length=8)

    with open(output_file, newline="") as fh:
        reader = csv.DictReader(fh)
        result = list(reader)

    assert len(result) == 3
    assert result[0]["bio"] == "A soft..."
    assert result[2]["bio"] == "Short"


def test_truncate_file_columns_subset(tmp_path):
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.csv"

    with open(input_file, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["name", "bio", "city"])
        writer.writeheader()
        writer.writerows(ROWS)

    truncate_file(str(input_file), str(output_file), max_length=5, columns=["bio"])

    with open(output_file, newline="") as fh:
        reader = csv.DictReader(fh)
        result = list(reader)
