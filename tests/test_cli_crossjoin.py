import csv
import io
import os
import sys
import tempfile
import types
import pytest

from csvwrangler.cli_crossjoin import run_crossjoin


def _write_csv(path, rows):
    headers = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(rows)


def _read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _make_args(**kwargs):
    defaults = dict(left_prefix="left_", right_prefix="right_", output="-")
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


def test_run_crossjoin_stdout(tmp_path, capsys):
    lf = str(tmp_path / "left.csv")
    rf = str(tmp_path / "right.csv")
    _write_csv(lf, [{"id": "1"}, {"id": "2"}])
    _write_csv(rf, [{"color": "red"}, {"color": "blue"}])
    args = _make_args(left=lf, right=rf)
    run_crossjoin(args)
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    assert len(rows) == 4


def test_run_crossjoin_output_file(tmp_path):
    lf = str(tmp_path / "left.csv")
    rf = str(tmp_path / "right.csv")
    out = str(tmp_path / "out.csv")
    _write_csv(lf, [{"x": "a"}])
    _write_csv(rf, [{"y": "b"}, {"y": "c"}])
    args = _make_args(left=lf, right=rf, output=out)
    run_crossjoin(args)
    rows = _read_csv(out)
    assert len(rows) == 2
    assert rows[0] == {"x": "a", "y": "b"}


def test_run_crossjoin_missing_file_exits(tmp_path):
    args = _make_args(left="no.csv", right="no2.csv")
    with pytest.raises(SystemExit):
        run_crossjoin(args)
