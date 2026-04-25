"""Tests for stack_files() using reader/writer objects."""
import csv
import io
import pytest
from csvwrangler.stacker import stack_files


class ListWriter:
    def __init__(self, fieldnames):
        self.fieldnames = fieldnames
        self.rows = []
        self.header_written = False

    def writeheader(self):
        self.header_written = True

    def writerows(self, rows):
        self.rows.extend(rows)


def _make_reader(rows, fieldnames=None):
    if not rows:
        buf = io.StringIO()
        fnames = fieldnames or []
        w = csv.DictWriter(buf, fieldnames=fnames)
        w.writeheader()
        buf.seek(0)
        return csv.DictReader(buf)
    fnames = fieldnames or list(rows[0].keys())
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fnames)
    w.writeheader()
    w.writerows(rows)
    buf.seek(0)
    return csv.DictReader(buf)


def test_stack_files_basic():
    r1 = _make_reader([{"a": "1", "b": "2"}])
    r2 = _make_reader([{"a": "3", "b": "4"}])
    writer = ListWriter(["a", "b"])
    stack_files([r1, r2], writer)
    assert writer.header_written
    assert len(writer.rows) == 2
    assert writer.rows[0]["a"] == "1"
    assert writer.rows[1]["a"] == "3"


def test_stack_files_empty_produces_no_output():
    r1 = _make_reader([], fieldnames=["a"])
    r2 = _make_reader([], fieldnames=["a"])
    writer = ListWriter(["a"])
    stack_files([r1, r2], writer)
    assert not writer.header_written
    assert writer.rows == []


def test_stack_files_fill_missing_column():
    r1 = _make_reader([{"name": "Alice", "age": "30"}])
    r2 = _make_reader([{"name": "Bob", "city": "NYC"}])
    writer = ListWriter([])
    stack_files([r1, r2], writer, fill_value="-")
    assert len(writer.rows) == 2
    assert writer.rows[0]["city"] == "-"
    assert writer.rows[1]["age"] == "-"
