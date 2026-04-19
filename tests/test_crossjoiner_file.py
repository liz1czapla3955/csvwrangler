import csv
import io
from csvwrangler.crossjoiner import crossjoin_files


class ListWriter:
    def __init__(self, fieldnames):
        self.fieldnames = fieldnames
        self.rows = []
        self._header_written = False

    def writeheader(self):
        self._header_written = True

    def writerow(self, row):
        self.rows.append(row)


def _make_reader(rows):
    if not rows:
        return iter([])
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
    buf.seek(0)
    return csv.DictReader(buf)


def test_crossjoin_files_basic():
    left = [{"a": "1"}, {"a": "2"}]
    right = [{"b": "x"}]
    writer = ListWriter(["a", "b"])
    crossjoin_files(_make_reader(left), _make_reader(right), writer)
    assert len(writer.rows) == 2
    assert writer.rows[0] == {"a": "1", "b": "x"}
    assert writer.rows[1] == {"a": "2", "b": "x"}


def test_crossjoin_files_empty_left():
    writer = ListWriter([])
    crossjoin_files(_make_reader([]), _make_reader([{"b": "1"}]), writer)
    assert writer.rows == []


def test_crossjoin_files_conflict_prefix():
    left = [{"id": "L"}]
    right = [{"id": "R", "val": "v"}]
    writer = ListWriter([])
    crossjoin_files(_make_reader(left), _make_reader(right), writer, "l_", "r_")
    assert len(writer.rows) == 1
    row = writer.rows[0]
    assert row["l_id"] == "L"
    assert row["r_id"] == "R"
    assert row["val"] == "v"
