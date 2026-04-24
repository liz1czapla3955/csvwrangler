"""Tests for correlate_file using in-memory reader/writer helpers."""

from __future__ import annotations

import csv
import io
import pytest

from csvwrangler.correlator import correlate_file


class ListWriter:
    def __init__(self):
        self.fieldnames = None
        self.rows = []

    def writeheader(self):
        pass

    def writerow(self, row):
        self.rows.append(dict(row))


def _make_reader(rows, fieldnames):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)
    buf.seek(0)
    return csv.DictReader(buf)


def test_correlate_file_produces_matrix():
    rows = [{"a": str(i), "b": str(i * 2)} for i in range(1, 6)]
    reader = _make_reader(rows, ["a", "b"])
    writer = ListWriter()
    correlate_file(reader, writer, columns=["a", "b"])
    assert len(writer.rows) == 2
    assert writer.fieldnames == ["column", "a", "b"]


def test_correlate_file_perfect_correlation():
    rows = [{"p": str(i), "q": str(i)} for i in range(1, 5)]
    reader = _make_reader(rows, ["p", "q"])
    writer = ListWriter()
    correlate_file(reader, writer, columns=["p", "q"], decimals=4)
    result = {r["column"]: r for r in writer.rows}
    assert float(result["p"]["q"]) == pytest.approx(1.0, abs=1e-4)


def test_correlate_file_three_columns():
    rows = [
        {"a": "1", "b": "2", "c": "3"},
        {"a": "4", "b": "5", "c": "6"},
        {"a": "7", "b": "8", "c": "9"},
    ]
    reader = _make_reader(rows, ["a", "b", "c"])
    writer = ListWriter()
    correlate_file(reader, writer, columns=["a", "b", "c"])
    assert len(writer.rows) == 3
    assert writer.fieldnames == ["column", "a", "b", "c"]
