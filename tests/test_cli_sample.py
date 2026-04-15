"""Integration tests for the sample CLI subcommand."""

import argparse
import csv
import os
import tempfile

import pytest

from csvwrangler.cli_sample import run_sample


def _write_csv(path: str, rows: list, fieldnames: list) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"mode": "random", "seed": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_run_sample_first(tmp_path):
    src = tmp_path / "in.csv"
    dst = tmp_path / "out.csv"
    rows = [{"x": str(i)} for i in range(10)]
    _write_csv(str(src), rows, ["x"])

    args = _make_args(input=str(src), output=str(dst), num_rows=3, mode="first")
    run_sample(args)

    with open(str(dst), newline="") as fh:
        result = list(csv.DictReader(fh))
    assert len(result) == 3
    assert [r["x"] for r in result] == ["0", "1", "2"]


def test_run_sample_random_reproducible(tmp_path):
    src = tmp_path / "in.csv"
    dst1 = tmp_path / "out1.csv"
    dst2 = tmp_path / "out2.csv"
    rows = [{"v": str(i)} for i in range(20)]
    _write_csv(str(src), rows, ["v"])

    for dst in (dst1, dst2):
        args = _make_args(input=str(src), output=str(dst), num_rows=5, mode="random", seed=42)
        run_sample(args)

    with open(str(dst1)) as f1, open(str(dst2)) as f2:
        assert f1.read() == f2.read()


def test_run_sample_bad_n_exits(tmp_path, capsys):
    src = tmp_path / "in.csv"
    _write_csv(str(src), [{"a": "1"}], ["a"])
    dst = tmp_path / "out.csv"

    args = _make_args(input=str(src), output=str(dst), num_rows=-5)
    with pytest.raises(SystemExit) as exc_info:
        run_sample(args)
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Error" in captured.err
