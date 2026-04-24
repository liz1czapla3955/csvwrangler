"""Integration tests for the strip CLI subcommand."""

import argparse
import csv
import io
import os
import tempfile

import pytest

from csvwrangler.cli_strip import run_strip


def _write_csv(path: str, rows: list, fieldnames: list) -> None:
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _read_csv(path: str) -> list:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "input": "-",
        "output": "-",
        "no_strip_blank": False,
        "comment_prefix": None,
        "head": 0,
        "tail": 0,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_run_strip_removes_blank_rows(tmp_path):
    src = str(tmp_path / "in.csv")
    dst = str(tmp_path / "out.csv")
    _write_csv(
        src,
        [
            {"id": "1", "name": "Alice"},
            {"id": "", "name": ""},
            {"id": "2", "name": "Bob"},
        ],
        ["id", "name"],
    )
    args = _make_args(input=src, output=dst)
    run_strip(args)
    result = _read_csv(dst)
    assert len(result) == 2
    assert result[0]["name"] == "Alice"
    assert result[1]["name"] == "Bob"


def test_run_strip_comment_prefix(tmp_path):
    src = str(tmp_path / "in.csv")
    dst = str(tmp_path / "out.csv")
    _write_csv(
        src,
        [
            {"id": "# skip me", "name": ""},
            {"id": "1", "name": "Alice"},
        ],
        ["id", "name"],
    )
    args = _make_args(input=src, output=dst, comment_prefix="#", strip_blank=False)
    run_strip(args)
    result = _read_csv(dst)
    assert len(result) == 1
    assert result[0]["name"] == "Alice"


def test_run_strip_head_and_tail(tmp_path):
    src = str(tmp_path / "in.csv")
    dst = str(tmp_path / "out.csv")
    rows = [{"id": str(i), "name": f"Row{i}"} for i in range(5)]
    _write_csv(src, rows, ["id", "name"])
    args = _make_args(input=src, output=dst, no_strip_blank=True, head=1, tail=1)
    run_strip(args)
    result = _read_csv(dst)
    assert len(result) == 3
    assert result[0]["id"] == "1"
    assert result[-1]["id"] == "3"
