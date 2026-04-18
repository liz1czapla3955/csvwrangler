import pytest
from csvwrangler.roller import rolling_file


class ListWriter:
    def __init__(self):
        self.header = None
        self.rows = []

    def writeheader(self):
        pass

    def writerow(self, row):
        self.rows.append(row)


def _make_reader(rows):
    return iter(rows)


def test_rolling_file_mean():
    rows = [{"x": "1", "v": str(i * 5)} for i in range(1, 6)]
    writer = ListWriter()
    rolling_file(_make_reader(rows), writer, column="v", window=2, agg="mean")
    assert writer.rows[0]["v_rolling_mean"] == "5"
    assert writer.rows[1]["v_rolling_mean"] == "7.5"


def test_rolling_file_empty():
    writer = ListWriter()
    rolling_file(_make_reader([]), writer, column="v", window=2)
    assert writer.rows == []


def test_rolling_file_custom_output_column():
    rows = [{"v": "10"}, {"v": "20"}]
    writer = ListWriter()
    rolling_file(_make_reader(rows), writer, column="v", window=2, output_column="smooth")
    assert "smooth" in writer.rows[0]


def test_rolling_file_max():
    rows = [{"v": str(i)} for i in [3, 1, 4, 1, 5]]
    writer = ListWriter()
    rolling_file(_make_reader(rows), writer, column="v", window=3, agg="max")
    assert writer.rows[2]["v_rolling_max"] == "4"
    assert writer.rows[4]["v_rolling_max"] == "5"
