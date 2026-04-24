"""Integration tests for the frequency CLI sub-command."""
import csv
import io
import sys
import types
import pytest

from csvwrangler.cli_frequency import run_frequency


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
    defaults = {
        "input": "-",
        "output": "-",
        "column": "color",
        "output_column": "frequency",
        "sort_by": "count",
        "ascending": False,
    }
    defaults.update(kwargs)
    ns = types.SimpleNamespace(**defaults)
    ns.func = run_frequency
    return ns


def test_run_frequency_success(tmp_path):
    rows = [
        {"color": "red"}, {"color": "blue"}, {"color": "red"}, {"color": "green"},
    ]
    src = _write_csv(tmp_path, "in.csv", rows)
    dst = str(tmp_path / "out.csv")
    args = _make_args(input=src, output=dst, column="color")
    run_frequency(args)
    result = _read_csv(dst)
    by_color = {r["color"]: int(r["frequency"]) for r in result}
    assert by_color == {"red": 2, "blue": 1, "green": 1}


def test_run_frequency_sort_ascending(tmp_path):
    rows = [
        {"v": "a"}, {"v": "a"}, {"v": "b"}, {"v": "c"}, {"v": "c"}, {"v": "c"},
    ]
    src = _write_csv(tmp_path, "in.csv", rows)
    dst = str(tmp_path / "out.csv")
    args = _make_args(input=src, output=dst, column="v", sort_by="count", ascending=True)
    run_frequency(args)
    result = _read_csv(dst)
    counts = [int(r["frequency"]) for r in result]
    assert counts == sorted(counts)


def test_run_frequency_bad_column_exits(tmp_path):
    rows = [{"color": "red"}]
    src = _write_csv(tmp_path, "in.csv", rows)
    args = _make_args(input=src, column="nonexistent")
    with pytest.raises(SystemExit) as exc_info:
        run_frequency(args)
    assert exc_info.value.code == 1
