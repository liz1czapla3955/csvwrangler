import csv
import io
import os
import tempfile
import argparse
import pytest

from csvwrangler.cli_bin import run_bin


def _write_csv(path, rows, fieldnames):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _make_args(**kwargs):
    defaults = {
        "column": "score",
        "edges": "0,10,20",
        "labels": None,
        "output_column": "bin",
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_run_bin_success():
    rows = [{"name": "a", "score": "5"}, {"name": "b", "score": "15"}]
    with tempfile.TemporaryDirectory() as d:
        inp = os.path.join(d, "in.csv")
        out = os.path.join(d, "out.csv")
        _write_csv(inp, rows, ["name", "score"])
        args = _make_args(input=inp, output=out)
        run_bin(args)
        result = _read_csv(out)
        assert result[0]["bin"] == "0-10"
        assert result[1]["bin"] == "10-20"


def test_run_bin_custom_labels():
    rows = [{"val": "25"}]
    with tempfile.TemporaryDirectory() as d:
        inp = os.path.join(d, "in.csv")
        out = os.path.join(d, "out.csv")
        _write_csv(inp, rows, ["val"])
        args = _make_args(input=inp, output=out, column="val", edges="0,20", labels="low,mid,high")
        run_bin(args)
        result = _read_csv(out)
        assert result[0]["bin"] == "high"


def test_run_bin_bad_edges_exits():
    with tempfile.TemporaryDirectory() as d:
        inp = os.path.join(d, "in.csv")
        out = os.path.join(d, "out.csv")
        _write_csv(inp, [{"score": "5"}], ["score"])
        args = _make_args(input=inp, output=out, edges="a,b,c")
        with pytest.raises(SystemExit):
            run_bin(args)
