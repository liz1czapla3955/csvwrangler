"""Integration tests for the interleave CLI sub-command."""

import csv
import io
import os
import sys
import types

import pytest

from csvwrangler.cli_interleave import run_interleave


def _write_csv(path, rows):
    headers, *body = rows
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(headers)
        w.writerows(body)


def _read_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _make_args(**kwargs):
    defaults = dict(fill=False, fill_value="", output="-")
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


def test_run_interleave_stdout(tmp_path, capsys):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    _write_csv(str(a), [["id", "v"], ["1", "x"], ["2", "y"]])
    _write_csv(str(b), [["id", "v"], ["3", "p"], ["4", "q"]])

    args = _make_args(file_a=str(a), file_b=str(b))
    run_interleave(args)

    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    ids = [r["id"] for r in rows]
    assert ids == ["1", "3", "2", "4"]


def test_run_interleave_output_file(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    out = tmp_path / "out.csv"
    _write_csv(str(a), [["id", "v"], ["1", "x"], ["2", "y"], ["3", "z"]])
    _write_csv(str(b), [["id", "v"], ["4", "p"], ["5", "q"], ["6", "r"]])

    args = _make_args(file_a=str(a), file_b=str(b), output=str(out))
    run_interleave(args)

    rows = _read_csv(str(out))
    assert len(rows) == 6
    assert rows[0]["id"] == "1"
    assert rows[1]["id"] == "4"


def test_run_interleave_fill(tmp_path, capsys):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    _write_csv(str(a), [["id", "v"], ["1", "x"]])
    _write_csv(str(b), [["id", "v"], ["2", "y"], ["3", "z"]])

    args = _make_args(file_a=str(a), file_b=str(b), fill=True, fill_value="")
    run_interleave(args)

    captured = capsys.readouterr().out
    rows = list(csv.DictReader(io.StringIO(captured)))
    assert len(rows) == 4


def test_run_interleave_bad_file_exits(tmp_path):
    args = _make_args(file_a="nonexistent_a.csv", file_b="nonexistent_b.csv")
    with pytest.raises(SystemExit) as exc_info:
        run_interleave(args)
    assert exc_info.value.code == 1
