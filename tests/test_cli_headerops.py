"""Integration tests for cli_headerops.run_headerops."""
import csv
import os
import types
import pytest
from csvwrangler.cli_headerops import run_headerops


def _write_csv(path, rows):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _make_args(**kwargs):
    defaults = dict(op="drop", columns=None, insert_name=None,
                    insert_value="", insert_position=-1)
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


def test_run_headerops_drop(tmp_path):
    inp = tmp_path / "in.csv"
    out = tmp_path / "out.csv"
    _write_csv(inp, [{"a": "1", "b": "2", "c": "3"}])
    args = _make_args(input=str(inp), output=str(out), op="drop", columns=["b"])
    run_headerops(args)
    result = _read_csv(out)
    assert "b" not in result[0]
    assert result[0]["a"] == "1"


def test_run_headerops_reorder(tmp_path):
    inp = tmp_path / "in.csv"
    out = tmp_path / "out.csv"
    _write_csv(inp, [{"a": "1", "b": "2", "c": "3"}])
    args = _make_args(input=str(inp), output=str(out), op="reorder", columns=["c", "a", "b"])
    run_headerops(args)
    result = _read_csv(out)
    assert list(result[0].keys()) == ["c", "a", "b"]


def test_run_headerops_insert(tmp_path):
    inp = tmp_path / "in.csv"
    out = tmp_path / "out.csv"
    _write_csv(inp, [{"a": "1", "b": "2"}])
    args = _make_args(input=str(inp), output=str(out), op="insert",
                      insert_name="flag", insert_value="yes", insert_position=0)
    run_headerops(args)
    result = _read_csv(out)
    assert result[0]["flag"] == "yes"
    assert list(result[0].keys())[0] == "flag"


def test_run_headerops_bad_file_exits(tmp_path):
    out = tmp_path / "out.csv"
    args = _make_args(input="nonexistent.csv", output=str(out), op="drop", columns=["x"])
    with pytest.raises(SystemExit):
        run_headerops(args)
