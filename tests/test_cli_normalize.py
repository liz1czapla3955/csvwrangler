"""Tests for csvwrangler.cli_normalize."""

from __future__ import annotations

import argparse
import os
import sys

import pytest

from csvwrangler.cli_normalize import run_normalize


def _write_csv(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "header_case": None,
        "value_case": None,
        "no_strip": False,
        "replace": [],
        "columns": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_run_normalize_lower_headers(tmp_path):
    src = tmp_path / "in.csv"
    dst = tmp_path / "out.csv"
    _write_csv(str(src), "First Name,Last Name\nAlice,Smith\n")
    args = _make_args(input=str(src), output=str(dst), header_case="lower")
    run_normalize(args)
    content = dst.read_text(encoding="utf-8")
    assert "first name" in content
    assert "last name" in content


def test_run_normalize_upper_values(tmp_path):
    src = tmp_path / "in.csv"
    dst = tmp_path / "out.csv"
    _write_csv(str(src), "city\nlondon\nparis\n")
    args = _make_args(input=str(src), output=str(dst), value_case="upper")
    run_normalize(args)
    content = dst.read_text(encoding="utf-8")
    assert "LONDON" in content
    assert "PARIS" in content


def test_run_normalize_replace_header_spaces(tmp_path):
    src = tmp_path / "in.csv"
    dst = tmp_path / "out.csv"
    _write_csv(str(src), "first name,last name\nAlice,Smith\n")
    args = _make_args(input=str(src), output=str(dst), replace=[[" ", "_"]])
    run_normalize(args)
    content = dst.read_text(encoding="utf-8")
    assert "first_name" in content


def test_run_normalize_missing_input_exits(tmp_path):
    dst = tmp_path / "out.csv"
    args = _make_args(input=str(tmp_path / "nope.csv"), output=str(dst))
    with pytest.raises(SystemExit) as exc_info:
        run_normalize(args)
    assert exc_info.value.code == 1
