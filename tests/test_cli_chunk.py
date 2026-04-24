"""Integration tests for the 'chunk' CLI sub-command."""

import csv
import io
import sys
import types
import pytest

from csvwrangler.cli_chunk import run_chunk


def _write_csv(tmp_path, name, rows, fieldnames=None):
    p = tmp_path / name
    fieldnames = fieldnames or list(rows[0].keys())
    with open(p, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    return str(p)


def _read_csv(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def _make_args(**kwargs):
    defaults = {"input": "-", "size": 2, "index": 0, "output": "-"}
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


def test_run_chunk_first_chunk(tmp_path, capsys):
    rows = [{"id": str(i)} for i in range(1, 7)]
    src = _write_csv(tmp_path, "data.csv", rows)
    out = tmp_path / "out.csv"
    run_chunk(_make_args(input=src, size=2, index=0, output=str(out)))
    result = _read_csv(str(out))
    assert [r["id"] for r in result] == ["1", "2"]


def test_run_chunk_second_chunk(tmp_path):
    rows = [{"id": str(i)} for i in range(1, 7)]
    src = _write_csv(tmp_path, "data.csv", rows)
    out = tmp_path / "out.csv"
    run_chunk(_make_args(input=src, size=2, index=1, output=str(out)))
    result = _read_csv(str(out))
    assert [r["id"] for r in result] == ["3", "4"]


def test_run_chunk_last_partial(tmp_path):
    rows = [{"id": str(i)} for i in range(1, 6)]
    src = _write_csv(tmp_path, "data.csv", rows)
    out = tmp_path / "out.csv"
    run_chunk(_make_args(input=src, size=2, index=2, output=str(out)))
    result = _read_csv(str(out))
    assert [r["id"] for r in result] == ["5"]


def test_run_chunk_index_out_of_range_exits(tmp_path):
    rows = [{"id": str(i)} for i in range(1, 4)]
    src = _write_csv(tmp_path, "data.csv", rows)
    with pytest.raises(SystemExit):
        run_chunk(_make_args(input=src, size=2, index=5, output="-"))


def test_run_chunk_bad_size_exits(tmp_path):
    rows = [{"id": "1"}]
    src = _write_csv(tmp_path, "data.csv", rows)
    with pytest.raises(SystemExit):
        run_chunk(_make_args(input=src, size=0, index=0, output="-"))
