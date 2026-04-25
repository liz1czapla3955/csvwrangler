"""Integration tests for csvwrangler.cli_stack.run_stack."""
import argparse
import csv
import io
import os
import sys
import tempfile
import pytest

from csvwrangler.cli_stack import run_stack


def _write_csv(path: str, rows, fieldnames=None) -> None:
    if not rows:
        return
    fnames = fieldnames or list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fnames)
        w.writeheader()
        w.writerows(rows)


def _read_csv(path: str):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _make_args(**kwargs):
    defaults = dict(inputs=[], output="-", fill="", strict=False, func=run_stack)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_run_stack_basic(tmp_path, capsys):
    f1 = str(tmp_path / "a.csv")
    f2 = str(tmp_path / "b.csv")
    _write_csv(f1, [{"name": "Alice", "age": "30"}])
    _write_csv(f2, [{"name": "Bob", "age": "25"}])
    args = _make_args(inputs=[f1, f2])
    run_stack(args)
    captured = capsys.readouterr()
    reader = csv.DictReader(io.StringIO(captured.out))
    rows = list(reader)
    assert len(rows) == 2
    assert rows[0]["name"] == "Alice"
    assert rows[1]["name"] == "Bob"


def test_run_stack_to_output_file(tmp_path):
    f1 = str(tmp_path / "a.csv")
    f2 = str(tmp_path / "b.csv")
    out = str(tmp_path / "out.csv")
    _write_csv(f1, [{"x": "1"}])
    _write_csv(f2, [{"x": "2"}])
    args = _make_args(inputs=[f1, f2], output=out)
    run_stack(args)
    rows = _read_csv(out)
    assert [r["x"] for r in rows] == ["1", "2"]


def test_run_stack_fill_missing(tmp_path, capsys):
    f1 = str(tmp_path / "a.csv")
    f2 = str(tmp_path / "b.csv")
    _write_csv(f1, [{"name": "Alice", "age": "30"}])
    _write_csv(f2, [{"name": "Bob", "city": "NYC"}])
    args = _make_args(inputs=[f1, f2], fill="?")
    run_stack(args)
    captured = capsys.readouterr()
    reader = csv.DictReader(io.StringIO(captured.out))
    rows = list(reader)
    assert rows[0]["city"] == "?"
    assert rows[1]["age"] == "?"


def test_run_stack_strict_exits_on_mismatch(tmp_path):
    f1 = str(tmp_path / "a.csv")
    f2 = str(tmp_path / "b.csv")
    _write_csv(f1, [{"name": "Alice"}])
    _write_csv(f2, [{"city": "NYC"}])
    args = _make_args(inputs=[f1, f2], strict=True)
    with pytest.raises(SystemExit):
        run_stack(args)
