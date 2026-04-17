import csv
import io
import os
import tempfile
import argparse
import pytest

from csvwrangler.cli_replace import run_replace


def _write_csv(path, rows, fieldnames):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _make_args(**kwargs):
    defaults = {"regex": False, "ignore_case": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_run_replace_basic(tmp_path):
    inp = str(tmp_path / "in.csv")
    out = str(tmp_path / "out.csv")
    _write_csv(inp, [{"a": "hello world"}, {"a": "world"}], ["a"])
    args = _make_args(input=inp, output=out, column="a", pattern="world", replacement="earth")
    run_replace(args)
    rows = _read_csv(out)
    assert rows[0]["a"] == "hello earth"
    assert rows[1]["a"] == "earth"


def test_run_replace_regex(tmp_path):
    inp = str(tmp_path / "in.csv")
    out = str(tmp_path / "out.csv")
    _write_csv(inp, [{"val": "abc123"}, {"val": "xyz"}], ["val"])
    args = _make_args(input=inp, output=out, column="val", pattern=r"\d+", replacement="NUM", regex=True)
    run_replace(args)
    rows = _read_csv(out)
    assert rows[0]["val"] == "abcNUM"
    assert rows[1]["val"] == "xyz"


def test_run_replace_bad_column_exits(tmp_path):
    inp = str(tmp_path / "in.csv")
    out = str(tmp_path / "out.csv")
    _write_csv(inp, [{"a": "hello"}], ["a"])
    args = _make_args(input=inp, output=out, column="missing", pattern="x", replacement.raises(SystemExit):
        run_replace(args)
