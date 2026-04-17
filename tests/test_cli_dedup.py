import csv
import io
import os
import sys
import tempfile
import types
import pytest

from csvwrangler.cli_dedup import run_dedup


def _write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _make_args(**kwargs):
    args = types.SimpleNamespace(
        keys=None,
        keep="first",
        **kwargs,
    )
    return args


def test_run_dedup_removes_duplicates(tmp_path):
    inp = str(tmp_path / "in.csv")
    out = str(tmp_path / "out.csv")
    rows = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
        {"id": "1", "name": "Alice"},
    ]
    _write_csv(inp, rows, ["id", "name"])
    args = _make_args(input=inp, output=out)
    run_dedup(args)
    result = _read_csv(out)
    assert len(result) == 2
    assert result[0]["id"] == "1"
    assert result[1]["id"] == "2"


def test_run_dedup_keep_last(tmp_path):
    inp = str(tmp_path / "in.csv")
    out = str(tmp_path / "out.csv")
    rows = [
        {"id": "1", "val": "first"},
        {"id": "1", "val": "last"},
    ]
    _write_csv(inp, rows, ["id", "val"])
    args = _make_args(input=inp, output=out, keys=["id"], keep="last")
    run_dedup(args)
    result = _read_csv(out)
    assert len(result) == 1
    assert result[0]["val"] == "last"


def test_run_dedup_bad_key_exits(tmp_path):
    inp = str(tmp_path / "in.csv")
    out = str(tmp_path / "out.csv")
    rows = [{"id": "1", "name": "Alice"}]
    _write_csv(inp, rows, ["id", "name"])
    args = _make_args(input=inp, output=out, keys=["nonexistent"])
    with pytest.raises(SystemExit):
        run_dedup(args)


def test_run_dedup_missing_input_exits(tmp_path):
    args = _make_args(input=str(tmp_path / "nope.csv"), output=str(tmp_path / "out.csv"))
    with pytest.raises(SystemExit):
        run_dedup(args)
