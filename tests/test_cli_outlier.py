import csv
import os
import argparse
import pytest
from csvwrangler.cli_outlier import run_outlier


def _write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _make_args(**kwargs):
    defaults = {"threshold": 3.0, "mark": False, "mark_column": "is_outlier"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_run_outlier_filters(tmp_path):
    src = str(tmp_path / "in.csv")
    dst = str(tmp_path / "out.csv")
    rows = [
        {"id": "1", "v": "10"}, {"id": "2", "v": "11"},
        {"id": "3", "v": "12"}, {"id": "4", "v": "13"},
        {"id": "5", "v": "200"},
    ]
    _write_csv(src, rows, ["id", "v"])
    args = _make_args(input=src, output=dst, column="v", threshold=2.0)
    run_outlier(args)
    result = _read_csv(dst)
    ids = [r["id"] for r in result]
    assert "5" not in ids


def test_run_outlier_mark(tmp_path):
    src = str(tmp_path / "in.csv")
    dst = str(tmp_path / "out.csv")
    rows = [
        {"id": "1", "v": "10"}, {"id": "2", "v": "11"},
        {"id": "3", "v": "12"}, {"id": "4", "v": "13"},
        {"id": "5", "v": "200"},
    ]
    _write_csv(src, rows, ["id", "v"])
    args = _make_args(input=src, output=dst, column="v", threshold=2.0, mark=True)
    run_outlier(args)
    result = _read_csv(dst)
    assert len(result) == 5
    assert result[-1]["is_outlier"] == "1"


def test_run_outlier_bad_column_exits(tmp_path):
    src = str(tmp_path / "in.csv")
    dst = str(tmp_path / "out.csv")
    _write_csv(src, [{"a": "1"}], ["a"])
    args = _make_args(input=src, output=dst, column="missing")
    with pytest.raises(SystemExit):
        run_outlier(args)


def test_run_outlier_missing_file_exits(tmp_path):
    args = _make_args(input="no_such.csv", output=str(tmp_path / "out.csv"), column="v")
    with pytest.raises(SystemExit):
        run_outlier(args)
