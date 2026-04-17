import csv
import io
from csvwrangler.counter import count_file


def _make_reader(rows, fieldnames):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)
    buf.seek(0)
    return csv.DictReader(buf)


class ListWriter:
    def __init__(self, fieldnames):
        self.fieldnames = fieldnames
        self.rows = []

    def writeheader(self):
        pass

    def writerow(self, row):
        self.rows.append(dict(row))


def test_count_file_basic():
    rows = [{"color": "red"}, {"color": "blue"}, {"color": "red"}]
    reader = _make_reader(rows, ["color"])
    writer = ListWriter(["value", "count"])
    count_file(reader, writer, column="color")
    counts = {r["value"]: r["count"] for r in writer.rows}
    assert counts["red"] == 2
    assert counts["blue"] == 1


def test_count_file_sort_by_value_ascending():
    rows = [{"x": "b"}, {"x": "a"}, {"x": "b"}, {"x": "c"}]
    reader = _make_reader(rows, ["x"])
    writer = ListWriter(["value", "count"])
    count_file(reader, writer, column="x", sort_by="value", ascending=True)
    values = [r["value"] for r in writer.rows]
    assert values == sorted(values)


def test_count_file_empty():
    reader = _make_reader([], ["x"])
    writer = ListWriter(["value", "count"])
    count_file(reader, writer, column="x")
    assert writer.rows == []
