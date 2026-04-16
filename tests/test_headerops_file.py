"""Tests for headerops_file integration."""
import csv
import io
from csvwrangler.headerops import headerops_file


def _make_reader(rows):
    fieldnames = list(rows[0].keys())
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)
    buf.seek(0)
    return csv.DictReader(buf)


class ListWriter:
    def __init__(self):
        self.rows = []
    def writerow(self, row):
        self.rows.append(dict(row))


def test_headerops_file_drop():
    reader = _make_reader([{"x": "1", "y": "2"}, {"x": "3", "y": "4"}])
    writer = ListWriter()
    headerops_file(reader, writer, "drop", columns=["y"])
    assert all("y" not in r for r in writer.rows)
    assert writer.rows[0]["x"] == "1"


def test_headerops_file_reorder():
    reader = _make_reader([{"a": "1", "b": "2", "c": "3"}])
    writer = ListWriter()
    headerops_file(reader, writer, "reorder", columns=["c", "b", "a"])
    assert list(writer.rows[0].keys()) == ["c", "b", "a"]


def test_headerops_file_insert():
    reader = _make_reader([{"a": "1"}])
    writer = ListWriter()
    headerops_file(reader, writer, "insert", insert_name="b", insert_value="v", insert_position=0)
    assert writer.rows[0]["b"] == "v"
    assert list(writer.rows[0].keys())[0] == "b"


def test_headerops_file_invalid_op():
    import pytest
    reader = _make_reader([{"a": "1"}])
    writer = ListWriter()
    with pytest.raises(ValueError, match="Unknown headerops"):
        headerops_file(reader, writer, "explode")
