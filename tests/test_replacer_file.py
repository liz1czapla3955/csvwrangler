import csv
import io
from csvwrangler.replacer import replace_file


class ListWriter:
    def __init__(self, fieldnames):
        self.fieldnames = fieldnames
        self.rows = []
        self.header_written = False

    def writeheader(self):
        self.header_written = True

    def writerow(self, row):
        self.rows.append(row)


def _make_reader(rows, fieldnames):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)
    buf.seek(0)
    return csv.DictReader(buf)


def test_replace_file_basic():
    rows = [{"x": "foo bar"}, {"x": "bar baz"}]
    reader = _make_reader(rows, ["x"])
    writer = ListWriter(["x"])
    replace_file(reader, writer, column="x", pattern="bar", replacement="qux")
    assert writer.header_written
    assert writer.rows[0]["x"] == "foo qux"
    assert writer.rows[1]["x"] == "qux baz"


def test_replace_file_regex():
    rows = [{"v": "price: 100"}, {"v": "price: 200"}]
    reader = _make_reader(rows, ["v"])
    writer = ListWriter(["v"])
    replace_file(reader, writer, column="v", pattern=r"\d+", replacement="X", use_regex=True)
    assert writer.rows[0]["v"] == "price: X"
    assert writer.rows[1]["v"] == "price: X"


def test_replace_file_empty():
    reader = _make_reader([], ["col"])
    writer = ListWriter(["col"])
    replace_file(reader, writer, column="col", pattern="a", replacement="b")
    assert writer.header_written
    assert writer.rows == []
