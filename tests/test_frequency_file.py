"""Tests for frequency_file() — the reader/writer integration layer."""
import csv
import io
from csvwrangler.differ2 import frequency_file


class ListWriter:
    """Minimal csv.DictWriter-compatible sink that collects rows."""

    def __init__(self):
        self.fieldnames = []
        self.rows = []

    def writeheader(self):
        pass

    def writerow(self, row):
        self.rows.append(dict(row))


def _make_reader(rows, fieldnames=None):
    fieldnames = fieldnames or list(rows[0].keys())
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)
    buf.seek(0)
    return csv.DictReader(buf)


def test_frequency_file_basic():
    rows = [
        {"animal": "cat"},
        {"animal": "dog"},
        {"animal": "cat"},
        {"animal": "bird"},
    ]
    reader = _make_reader(rows)
    writer = ListWriter()
    frequency_file(reader, writer, column="animal", sort_by="count", ascending=False)
    by_animal = {r["animal"]: int(r["frequency"]) for r in writer.rows}
    assert by_animal == {"cat": 2, "dog": 1, "bird": 1}


def test_frequency_file_custom_output_column():
    rows = [{"x": "a"}, {"x": "b"}, {"x": "a"}]
    reader = _make_reader(rows)
    writer = ListWriter()
    frequency_file(reader, writer, column="x", output_column="cnt")
    assert all("cnt" in r for r in writer.rows)


def test_frequency_file_empty_input():
    reader = _make_reader([{"col": "val"}])
    # consume the one row so reader is exhausted
    list(reader)
    reader = _make_reader([])
    writer = ListWriter()
    # empty input — no rows written, no crash
    frequency_file(reader, writer, column="col")
    assert writer.rows == []


def test_frequency_file_sets_fieldnames():
    rows = [{"lang": "python"}, {"lang": "go"}, {"lang": "python"}]
    reader = _make_reader(rows)
    writer = ListWriter()
    frequency_file(reader, writer, column="lang")
    assert writer.fieldnames == ["lang", "frequency"]
