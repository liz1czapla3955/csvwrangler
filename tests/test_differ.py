"""Tests for csvwrangler.differ."""

import csv
import io
import os
import tempfile

import pytest

from csvwrangler.differ import diff_rows, diff_files


ROWS_A = [
    {"id": "1", "name": "Alice", "score": "90"},
    {"id": "2", "name": "Bob",   "score": "80"},
    {"id": "3", "name": "Carol", "score": "70"},
]

ROWS_B = [
    {"id": "1", "name": "Alice", "score": "95"},  # changed
    {"id": "2", "name": "Bob",   "score": "80"},  # unchanged
    {"id": "4", "name": "Dave",  "score": "60"},  # added
    # id=3 removed
]


def _by_id(rows, id_val):
    return next((r for r in rows if r["id"] == id_val), None)


def test_diff_rows_changed():
    result = diff_rows(ROWS_A, ROWS_B, key_fields=["id"])
    row = _by_id(result, "1")
    assert row is not None
    assert row["_diff"] == "changed"
    assert row["score"] == "95"


def test_diff_rows_unchanged():
    result = diff_rows(ROWS_A, ROWS_B, key_fields=["id"])
    row = _by_id(result, "2")
    assert row is not None
    assert row["_diff"] == "unchanged"


def test_diff_rows_removed():
    result = diff_rows(ROWS_A, ROWS_B, key_fields=["id"])
    row = _by_id(result, "3")
    assert row is not None
    assert row["_diff"] == "removed"


def test_diff_rows_added():
    result = diff_rows(ROWS_A, ROWS_B, key_fields=["id"])
    row = _by_id(result, "4")
    assert row is not None
    assert row["_diff"] == "added"


def test_diff_rows_all_statuses_present():
    result = diff_rows(ROWS_A, ROWS_B, key_fields=["id"])
    statuses = {r["_diff"] for r in result}
    assert statuses == {"changed", "unchanged", "removed", "added"}


def test_diff_rows_empty_inputs():
    result = diff_rows([], [], key_fields=["id"])
    assert result == []


def test_diff_rows_composite_key():
    a = [{"dept": "eng", "level": "senior", "count": "5"}]
    b = [{"dept": "eng", "level": "senior", "count": "7"}]
    result = diff_rows(a, b, key_fields=["dept", "level"])
    assert len(result) == 1
    assert result[0]["_diff"] == "changed"


def _write_temp_csv(rows: list[dict]) -> str:
    f = tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, newline="", encoding="utf-8"
    )
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    f.close()
    return f.name


def test_diff_files_excludes_unchanged_by_default():
    path_a = _write_temp_csv(ROWS_A)
    path_b = _write_temp_csv(ROWS_B)
    try:
        out = io.StringIO()
        diff_files(path_a, path_b, key_fields=["id"], output=out)
        out.seek(0)
        rows = list(csv.DictReader(out))
        statuses = {r["_diff"] for r in rows}
        assert "unchanged" not in statuses
        assert "changed" in statuses or "added" in statuses or "removed" in statuses
    finally:
        os.unlink(path_a)
        os.unlink(path_b)


def test_diff_files_include_unchanged():
    path_a = _write_temp_csv(ROWS_A)
    path_b = _write_temp_csv(ROWS_B)
    try:
        out = io.StringIO()
        diff_files(path_a, path_b, key_fields=["id"], output=out, include_unchanged=True)
        out.seek(0)
        rows = list(csv.DictReader(out))
        statuses = {r["_diff"] for r in rows}
        assert "unchanged" in statuses
    finally:
        os.unlink(path_a)
        os.unlink(path_b)
