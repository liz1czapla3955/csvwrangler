"""Tests for swap_file() using in-memory reader/writer helpers."""

import csv
import io

from csvwrangler.swapper import swap_file


class ListWriter:
    def __init__(self, fieldnames):
        self.fieldnames = fieldnames
        self.rows = []
        self._header_written = False

    def writeheader(self):
        self._header_written = True

    def writerow(self, row):
        self.rows.append(dict(row))


def _make_reader(rows: list[dict], fieldnames: list[str]) -> csv.DictReader:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)
    buf.seek(0)
    return csv.DictReader(buf)


def test_swap_file_basic():
    reader = _make_reader(
        [{"name": "Alice", "score": "10", "rank": "1"}],
        ["name", "score", "rank"],
    )
    writer = ListWriter(["name", "score", "rank"])
    swap_file(reader, writer, "score", "rank")
    assert writer._header_written
    assert writer.rows[0]["score"] == "1"
    assert writer.rows[0]["rank"] == "10"
    assert writer.rows[0]["name"] == "Alice"


def test_swap_file_multiple_rows():
    reader = _make_reader(
        [{"p": "a", "q": "b"}, {"p": "c", "q": "d"}],
        ["p", "q"],
    )
    writer = ListWriter(["p", "q"])
    swap_file(reader, writer, "p", "q")
    assert writer.rows[0] == {"p": "b", "q": "a"}
    assert writer.rows[1] == {"p": "d", "q": "c"}


def test_swap_file_empty_input():
    reader = _make_reader([], ["a", "b"])
    writer = ListWriter(["a", "b"])
    swap_file(reader, writer, "a", "b")
    assert writer._header_written
    assert writer.rows == []
