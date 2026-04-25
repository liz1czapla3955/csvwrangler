"""Integration tests for the swap CLI sub-command."""

import argparse
import csv
import io
import os
import tempfile

import pytest

from csvwrangler.cli_swap import run_swap


def _write_csv(path: str, rows: list[dict], fieldnames: list[str]) -> None:
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _read_csv(path: str) -> list[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def _make_args(**kwargs):
    defaults = dict(input="-", col_a="a", col_b="b", output=None)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_run_swap_basic(tmp_path, capsys):
    p = tmp_path / "data.csv"
    _write_csv(
        str(p),
        [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}],
        ["a", "b"],
    )
    args = _make_args(input=str(p))
    run_swap(args)
    captured = capsys.readouterr()
    reader = csv.DictReader(io.StringIO(captured.out))
    rows = list(reader)
    assert rows[0]["a"] == "2"
    assert rows[0]["b"] == "1"
    assert rows[1]["a"] == "4"
    assert rows[1]["b"] == "3"


def test_run_swap_to_output_file(tmp_path):
    inp = tmp_path / "in.csv"
    out = tmp_path / "out.csv"
    _write_csv(str(inp), [{"x": "hello", "y": "world"}], ["x", "y"])
    args = _make_args(input=str(inp), col_a="x", col_b="y", output=str(out))
    run_swap(args)
    rows = _read_csv(str(out))
    assert rows[0]["x"] == "world"
    assert rows[0]["y"] == "hello"


def test_run_swap_bad_column_exits(tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(str(p), [{"a": "1", "b": "2"}], ["a", "b"])
    args = _make_args(input=str(p), col_a="a", col_b="nonexistent")
    with pytest.raises(SystemExit) as exc:
        run_swap(args)
    assert exc.value.code == 1
