"""Integration tests for the reshape CLI subcommand."""

from __future__ import annotations

import argparse
import csv
import os
import tempfile

import pytest

from csvwrangler.cli_reshape import run_reshape


def _write_csv(path: str, rows: list[dict], fieldnames: list[str]) -> None:
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _read_csv(path: str) -> list[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = dict(
        mode="melt",
        id_vars=["id"],
        value_vars=None,
        var_name="variable",
        value_name="value",
        var_col="variable",
        value_col="value",
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_run_reshape_melt(tmp_path):
    inp = str(tmp_path / "wide.csv")
    out = str(tmp_path / "long.csv")
    _write_csv(inp, [{"id": "1", "a": "10", "b": "20"}], ["id", "a", "b"])
    args = _make_args(input=inp, output=out, mode="melt", id_vars=["id"], value_vars=["a", "b"])
    run_reshape(args)
    rows = _read_csv(out)
    assert len(rows) == 2
    assert {r["variable"] for r in rows} == {"a", "b"}


def test_run_reshape_unmelt(tmp_path):
    inp = str(tmp_path / "long.csv")
    out = str(tmp_path / "wide.csv")
    _write_csv(
        inp,
        [{"id": "1", "variable": "a", "value": "10"}, {"id": "1", "variable": "b", "value": "20"}],
        ["id", "variable", "value"],
    )
    args = _make_args(input=inp, output=out, mode="unmelt", id_vars=["id"], value_vars=None)
    run_reshape(args)
    rows = _read_csv(out)
    assert len(rows) == 1
    assert rows[0]["a"] == "10"
    assert rows[0]["b"] == "20"


def test_run_reshape_bad_value_var_exits(tmp_path):
    inp = str(tmp_path / "wide.csv")
    out = str(tmp_path / "long.csv")
    _write_csv(inp, [{"id": "1", "a": "10"}], ["id", "a"])
    args = _make_args(input=inp, output=out, mode="melt", id_vars=["id"], value_vars=["nonexistent"])
    with pytest.raises(SystemExit) as exc_info:
        run_reshape(args)
    assert exc_info.value.code == 1
