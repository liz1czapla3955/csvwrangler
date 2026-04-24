"""Integration tests for the correlate CLI subcommand."""

from __future__ import annotations

import argparse
import csv
import io
import sys
import pytest

from csvwrangler.cli_correlate import run_correlate


def _write_csv(tmp_path, name, rows, fieldnames):
    p = tmp_path / name
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    return str(p)


def _read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _make_args(**kwargs):
    defaults = dict(input="-", output="-", columns="a,b", decimals=4)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_run_correlate_success(tmp_path):
    rows = [{"a": str(i), "b": str(i * 3)} for i in range(1, 6)]
    src = _write_csv(tmp_path, "in.csv", rows, ["a", "b"])
    out = str(tmp_path / "out.csv")
    args = _make_args(input=src, output=out, columns="a,b")
    run_correlate(args)
    result = _read_csv(out)
    assert len(result) == 2
    cols = {r["column"] for r in result}
    assert cols == {"a", "b"}


def test_run_correlate_diagonal_one(tmp_path):
    rows = [{"x": str(i), "y": str(i + 1)} for i in range(1, 6)]
    src = _write_csv(tmp_path, "in.csv", rows, ["x", "y"])
    out = str(tmp_path / "out.csv")
    args = _make_args(input=src, output=out, columns="x,y")
    run_correlate(args)
    result = {r["column"]: r for r in _read_csv(out)}
    assert float(result["x"]["x"]) == pytest.approx(1.0, abs=1e-4)
    assert float(result["y"]["y"]) == pytest.approx(1.0, abs=1e-4)


def test_run_correlate_bad_columns_exits(tmp_path):
    rows = [{"a": "1"}]
    src = _write_csv(tmp_path, "in.csv", rows, ["a"])
    args = _make_args(input=src, columns="")
    with pytest.raises(SystemExit):
        run_correlate(args)
