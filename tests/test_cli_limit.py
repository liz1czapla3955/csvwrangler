import csv
import os
import tempfile
import types
import pytest

from csvwrangler.cli_limit import run_limit


def _write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _make_args(**kwargs):
    defaults = {"limit": 3, "offset": 0}
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


def test_run_limit_basic(tmp_path):
    inp = str(tmp_path / "in.csv")
    out = str(tmp_path / "out.csv")
    rows = [{"id": str(i)} for i in range(1, 6)]
    _write_csv(inp, rows, ["id"])
    args = _make_args(input=inp, output=out, limit=3, offset=0)
    run_limit(args)
    result = _read_csv(out)
    assert len(result) == 3
    assert result[0]["id"] == "1"


def test_run_limit_with_offset(tmp_path):
    inp = str(tmp_path / "in.csv")
    out = str(tmp_path / "out.csv")
    rows = [{"id": str(i)} for i in range(1, 6)]
    _write_csv(inp, rows, ["id"])
    args = _make_args(input=inp, output=out, limit=2, offset=2)
    run_limit(args)
    result = _read_csv(out)
    assert len(result) == 2
    assert result[0]["id"] == "3"


def test_run_limit_negative_exits(tmp_path):
    inp = str(tmp_path / "in.csv")
    out = str(tmp_path / "out.csv")
    _write_csv(inp, [{"id": "1"}], ["id"])
    args = _make_args(input=inp, output=out, limit=-1, offset=0)
    with pytest.raises(SystemExit):
        run_limit(args)


def test_run_limit_negative_offset_exits(tmp_path):
    inp = str(tmp_path / "in.csv")
    out = str(tmp_path / "out.csv")
    _write_csv(inp, [{"id": "1"}], ["id"])
    args = _make_args(input=inp, output=out, limit=2, offset=-3)
    with pytest.raises(SystemExit):
        run_limit(args)
