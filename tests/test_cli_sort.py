"""Integration tests for the 'sort' CLI sub-command."""

import csv
import os
import tempfile
from unittest.mock import patch

import pytest

from csvwrangler.cli_sort import run_sort


def _make_args(**kwargs):
    """Build a simple namespace mimicking argparse output."""
    import argparse

    defaults = {
        "keys": ["name"],
        "reverse": False,
        "numeric": False,
        "delimiter": ",",
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _write_csv(rows, fieldnames):
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, newline="", encoding="utf-8"
    )
    writer = csv.DictWriter(tmp, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    tmp.close()
    return tmp.name


ROWS = [
    {"name": "Zara", "score": "10"},
    {"name": "Amy", "score": "20"},
]


def test_run_sort_success(capsys):
    src = _write_csv(ROWS, ["name", "score"])
    dst = src + ".sorted.csv"
    try:
        args = _make_args(input=src, output=dst, keys=["name"])
        run_sort(args)
        captured = capsys.readouterr()
        assert "Sorted 2 row(s)" in captured.out
        with open(dst, newline="", encoding="utf-8") as fh:
            result = list(csv.DictReader(fh))
        assert result[0]["name"] == "Amy"
    finally:
        os.unlink(src)
        if os.path.exists(dst):
            os.unlink(dst)


def test_run_sort_bad_key_exits(capsys):
    src = _write_csv(ROWS, ["name", "score"])
    dst = src + ".sorted.csv"
    try:
        args = _make_args(input=src, output=dst, keys=["nonexistent"])
        with pytest.raises(SystemExit) as exc_info:
            run_sort(args)
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error" in captured.err
    finally:
        os.unlink(src)
        if os.path.exists(dst):
            os.unlink(dst)
