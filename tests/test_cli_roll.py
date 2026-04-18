import csv
import os
import tempfile
import types
import pytest

from csvwrangler.cli_roll import run_roll


def _write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _make_args(**kwargs):
    defaults = dict(column="val", window=2, agg="mean", output_column=None)
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


def test_run_roll_mean(tmp_path):
    src = str(tmp_path / "in.csv")
    dst = str(tmp_path / "out.csv")
    _write_csv(src, [{"id": "1", "val": "10"}, {"id": "2", "val": "20"}, {"id": "3", "val": "30"}])
    args = _make_args(input=src, output=dst)
    run_roll(args)
    rows = _read_csv(dst)
    assert rows[1]["val_rolling_mean"] == "15"
    assert rows[2]["val_rolling_mean"] == "25"


def test_run_roll_sum(tmp_path):
    src = str(tmp_path / "in.csv")
    dst = str(tmp_path / "out.csv")
    _write_csv(src, [{"id": str(i), "val": str(i * 10)} for i in range(1, 5)])
    args = _make_args(input=src, output=dst, agg="sum", window=2)
    run_roll(args)
    rows = _read_csv(dst)
    assert rows[1]["val_rolling_sum"] == "30"


def test_run_roll_bad_window_exits(tmp_path):
    src = str(tmp_path / "in.csv")
    dst = str(tmp_path / "out.csv")
    _write_csv(src, [{"val": "1"}])
    args = _make_args(input=src, output=dst, window=0)
    with pytest.raises(SystemExit):
        run_roll(args)


def test_run_roll_bad_column_exits(tmp_path):
    src = str(tmp_path / "in.csv")
    dst = str(tmp_path / "out.csv")
    _write_csv(src, [{"val": "1"}])
    args = _make_args(input=src, output=dst, column="missing")
    with pytest.raises(SystemExit):
        run_roll(args)
