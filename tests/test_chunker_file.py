"""Tests for chunker.chunk_file using in-memory reader/writer stubs."""

from csvwrangler.chunker import chunk_file


class ListWriter:
    def __init__(self):
        self.header = None
        self.rows = []

    def writeheader(self):
        pass  # header set externally for these tests

    def writerow(self, row):
        self.rows.append(row)


def _make_reader(rows):
    """Return a list of dicts that acts as a DictReader stand-in."""
    return iter(rows)


def _rows(n):
    return [{"x": str(i)} for i in range(1, n + 1)]


def test_chunk_file_first_chunk():
    writer = ListWriter()
    chunk_file(_make_reader(_rows(6)), writer, size=2, chunk_index=0)
    assert [r["x"] for r in writer.rows] == ["1", "2"]


def test_chunk_file_middle_chunk():
    writer = ListWriter()
    chunk_file(_make_reader(_rows(6)), writer, size=2, chunk_index=1)
    assert [r["x"] for r in writer.rows] == ["3", "4"]


def test_chunk_file_last_partial_chunk():
    writer = ListWriter()
    chunk_file(_make_reader(_rows(5)), writer, size=2, chunk_index=2)
    assert [r["x"] for r in writer.rows] == ["5"]


def test_chunk_file_index_beyond_range_writes_nothing():
    writer = ListWriter()
    chunk_file(_make_reader(_rows(4)), writer, size=2, chunk_index=99)
    assert writer.rows == []


def test_chunk_file_empty_input_writes_nothing():
    writer = ListWriter()
    chunk_file(_make_reader([]), writer, size=3, chunk_index=0)
    assert writer.rows == []


def test_chunk_file_size_larger_than_data():
    writer = ListWriter()
    chunk_file(_make_reader(_rows(3)), writer, size=10, chunk_index=0)
    assert len(writer.rows) == 3
