"""Tests for csvwrangler.splitter."""

import os
import csv
import pytest

from csvwrangler.splitter import split_rows, split_file


# ---------------------------------------------------------------------------
# split_rows
# ---------------------------------------------------------------------------

ROWS = [
    {"region": "north", "city": "Oslo",   "pop": "700000"},
    {"region": "south", "city": "Rome",   "pop": "2800000"},
    {"region": "north", "city": "Bergen", "pop": "280000"},
    {"region": "east",  "city": "Warsaw", "pop": "1800000"},
    {"region": "south", "city": "Naples", "pop": "960000"},
]


def test_split_rows_groups_correctly():
    groups = split_rows(ROWS, "region")
    assert set(groups.keys()) == {"north", "south", "east"}
    assert len(groups["north"]) == 2
    assert len(groups["south"]) == 2
    assert len(groups["east"]) == 1


def test_split_rows_preserves_row_content():
    groups = split_rows(ROWS, "region")
    north_cities = {r["city"] for r in groups["north"]}
    assert north_cities == {"Oslo", "Bergen"}


def test_split_rows_empty_input():
    assert split_rows([], "region") == {}


def test_split_rows_missing_column():
    with pytest.raises(KeyError, match="region"):
        split_rows([{"city": "Oslo"}], "region")


def test_split_rows_single_group():
    rows = [{"x": "a", "y": "1"}, {"x": "a", "y": "2"}]
    groups = split_rows(rows, "x")
    assert list(groups.keys()) == ["a"]
    assert len(groups["a"]) == 2


# ---------------------------------------------------------------------------
# split_file
# ---------------------------------------------------------------------------

def _write_csv(path: str, rows: list, fieldnames: list) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _read_csv(path: str) -> list:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_split_file_creates_correct_files(tmp_path):
    src = str(tmp_path / "input.csv")
    _write_csv(src, ROWS, ["region", "city", "pop"])
    written = split_file(src, column="region", output_dir=str(tmp_path / "out"))
    assert len(written) == 3
    names = {os.path.basename(p) for p in written}
    assert names == {"north.csv", "south.csv", "east.csv"}


def test_split_file_row_counts(tmp_path):
    src = str(tmp_path / "input.csv")
    _write_csv(src, ROWS, ["region", "city", "pop"])
    out_dir = str(tmp_path / "out")
    split_file(src, column="region", output_dir=out_dir)
    assert len(_read_csv(os.path.join(out_dir, "north.csv"))) == 2
    assert len(_read_csv(os.path.join(out_dir, "south.csv"))) == 2
    assert len(_read_csv(os.path.join(out_dir, "east.csv"))) == 1


def test_split_file_keep_column_true(tmp_path):
    src = str(tmp_path / "input.csv")
    _write_csv(src, ROWS, ["region", "city", "pop"])
    out_dir = str(tmp_path / "out")
    split_file(src, column="region", output_dir=out_dir, keep_column=True)
    rows = _read_csv(os.path.join(out_dir, "north.csv"))
    assert "region" in rows[0], "split column should be present when keep_column=True"


def test_split_file_keep_column_false(tmp_path):
    src = str(tmp_path / "input.csv")
    _write_csv(src, ROWS, ["region", "city", "pop"])
    out_dir = str(tmp_path / "out")
    split_file(src, column="region", output_dir=out_dir, keep_column=False)
    rows = _read_csv(os.path.join(out_dir, "north.csv"))
    assert "region" not in rows[0], "split column should be absent when keep_column=False"
