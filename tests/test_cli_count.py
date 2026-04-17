import csv
import io
import os
import tempfile
import argparse
import pytest

from csvwrangler.cli_count import run_count


def _write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _make_args(**kwargs):
    defaults = {"input": "", "output": "", "column": "dept", "sort_by": "count", "ascending": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


ROWS = [
    {"name": "Alice", "dept": "Eng"},
    {"name": "Bob",   "dept": "HR"},
    {"name": "Carol", "dept": "Eng"},
]


def test_run_count_success():
    with tempfile.TemporaryDirectory() as d:
        inp = os.path.join(d, "in.csv")
        out = os.path.join(d, "out.csv")
        _write_csv(inp, ROWS, ["name", "dept"])
        args = _make_args(input=inp, output=out)
        run_count(args)
        result = _read_csv(out)
        counts = {r["value"]: int(r["count"]) for r in result}
        assert counts["Eng"] == 2
        assert counts["HR"] == 1


def test_run_count_bad_column_exits():
    with tempfile.TemporaryDirectory() as d:
        inp = os.path.join(d, "in.csv")
        out = os.path.join(d, "out.csv")
        _write_csv(inp, ROWS, ["name", "dept"])
        args = _make_args(input=inp, output=out, column="missing")
        with pytest.raises(SystemExit):
            run_count(args)


def test_run_count_missing_file_exits():
    args = _make_args(input="/nonexistent/file.csv", output="/tmp/out.csv")
    with pytest.raises(SystemExit):
        run_count(args)
