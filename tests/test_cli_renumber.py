"""Integration tests for the renumber CLI sub-command."""

import argparse
import csv
import io
import os
import tempfile

import pytest

from csvwrangler.cli_renumber import run_renumber


def _write_csv(path: str, rows: list[dict], fieldnames: list[str]) -> None:
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _read_csv(path: str) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = dict(input="-", output="-", column="id", start=1, step=1, overwrite=True)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_run_renumber_adds_id_column(tmp_path):
    src = str(tmp_path / "in.csv")
    dst = str(tmp_path / "out.csv")
    _write_csv(src, [{"name": "Alice"}, {"name": "Bob"}], ["name"])
    args = _make_args(input=src, output=dst)
    run_renumber(args)
    rows = _read_csv(dst)
    assert rows[0]["id"] == "1"
    assert rows[1]["id"] == "2"


def test_run_renumber_custom_start_and_step(tmp_path):
    src = str(tmp_path / "in.csv")
    dst = str(tmp_path / "out.csv")
    _write_csv(src, [{"v": "a"}, {"v": "b"}, {"v": "c"}], ["v"])
    args = _make_args(input=src, output=dst, start=10, step=10)
    run_renumber(args)
    rows = _read_csv(dst)
    assert [r["id"] for r in rows] == ["10", "20", "30"]


def test_run_renumber_no_overwrite(tmp_path):
    src = str(tmp_path / "in.csv")
    dst = str(tmp_path / "out.csv")
    _write_csv(
        src,
        [{"id": "existing", "v": "a"}, {"id": "", "v": "b"}],
        ["id", "v"],
    )
    args = _make_args(input=src, output=dst, overwrite=False)
    run_renumber(args)
    rows = _read_csv(dst)
    assert rows[0]["id"] == "existing"
    assert rows[1]["id"] == "2"
