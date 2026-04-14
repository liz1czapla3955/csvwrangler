"""Tests for csvwrangler.transformer module."""

import csv
import os
import tempfile
import pytest

from csvwrangler.transformer import (
    filter_rows,
    select_columns,
    rename_columns,
    transform_file,
)

SAMPLE_ROWS = [
    {"id": "1", "name": "Alice", "city": "NYC"},
    {"id": "2", "name": "Bob", "city": "LA"},
    {"id": "3", "name": "Charlie", "city": "NYC"},
]


def test_filter_rows_match():
    result = filter_rows(SAMPLE_ROWS, "city", "NYC")
    assert len(result) == 2
    assert all(r["city"] == "NYC" for r in result)


def test_filter_rows_negate():
    result = filter_rows(SAMPLE_ROWS, "city", "NYC", negate=True)
    assert len(result) == 1
    assert result[0]["name"] == "Bob"


def test_filter_rows_missing_column():
    with pytest.raises(KeyError, match="country"):
        filter_rows(SAMPLE_ROWS, "country", "US")


def test_filter_rows_no_match():
    result = filter_rows(SAMPLE_ROWS, "city", "Chicago")
    assert result == []


def test_select_columns():
    result = select_columns(SAMPLE_ROWS, ["id", "name"])
    assert result[0] == {"id": "1", "name": "Alice"}
    assert "city" not in result[0]


def test_select_columns_missing():
    with pytest.raises(KeyError):
        select_columns(SAMPLE_ROWS, ["id", "email"])


def test_select_columns_empty_rows():
    result = select_columns([], ["id"])
    assert result == []


def test_rename_columns():
    result = rename_columns(SAMPLE_ROWS, {"name": "full_name", "city": "location"})
    assert "full_name" in result[0]
    assert "location" in result[0]
    assert "name" not in result[0]
    assert "city" not in result[0]


def test_rename_columns_partial():
    result = rename_columns(SAMPLE_ROWS, {"id": "uid"})
    assert result[0]["uid"] == "1"
    assert "name" in result[0]


def _write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_transform_file_filter():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = os.path.join(tmpdir, "input.csv")
        dst = os.path.join(tmpdir, "output.csv")
        _write_csv(src, SAMPLE_ROWS, ["id", "name", "city"])
        count = transform_file(src, dst, filter_col="city", filter_val="NYC")
        assert count == 2
        with open(dst, newline="") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 2


def test_transform_file_select_and_rename():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = os.path.join(tmpdir, "input.csv")
        dst = os.path.join(tmpdir, "output.csv")
        _write_csv(src, SAMPLE_ROWS, ["id", "name", "city"])
        count = transform_file(
            src, dst,
            rename_map={"name": "full_name"},
            select_cols=["id", "full_name"],
        )
        assert count == 3
        with open(dst, newline="") as f:
            rows = list(csv.DictReader(f))
        assert "full_name" in rows[0]
        assert "city" not in rows[0]
