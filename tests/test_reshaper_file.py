"""File-level tests for csvwrangler.reshaper.reshape_file."""

from __future__ import annotations

import csv

import pytest

from csvwrangler.reshaper import reshape_file


def _write_csv(path, rows, fieldnames):
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _read_csv(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def test_reshape_file_melt(tmp_path):
    inp = str(tmp_path / "in.csv")
    out = str(tmp_path / "out.csv")
    _write_csv(inp, [{"id": "1", "x": "5", "y": "9"}], ["id", "x", "y"])
    reshape_file(inp, out, "melt", ["id"], ["x", "y"])
    rows = _read_csv(out)
    assert len(rows) == 2
    variables = {r["variable"] for r in rows}
    assert variables == {"x", "y"}


def test_reshape_file_melt_custom_names(tmp_path):
    inp = str(tmp_path / "in.csv")
    out = str(tmp_path / "out.csv")
    _write_csv(inp, [{"id": "1", "jan": "100"}], ["id", "jan"])
    reshape_file(inp, out, "melt", ["id"], ["jan"], var_name="month", value_name="sales")
    rows = _read_csv(out)
    assert rows[0]["month"] == "jan"
    assert rows[0]["sales"] == "100"


def test_reshape_file_unmelt(tmp_path):
    inp = str(tmp_path / "in.csv")
    out = str(tmp_path / "out.csv")
    _write_csv(
        inp,
        [{"id": "1", "variable": "x", "value": "5"}, {"id": "1", "variable": "y", "value": "9"}],
        ["id", "variable", "value"],
    )
    reshape_file(inp, out, "unmelt", ["id"])
    rows = _read_csv(out)
    assert len(rows) == 1
    assert rows[0]["x"] == "5"
    assert rows[0]["y"] == "9"


def test_reshape_file_invalid_mode(tmp_path):
    inp = str(tmp_path / "in.csv")
    out = str(tmp_path / "out.csv")
    _write_csv(inp, [{"id": "1"}], ["id"])
    with pytest.raises(ValueError, match="Unknown mode"):
        reshape_file(inp, out, "rotate", ["id"])


def test_reshape_file_melt_no_value_vars_raises(tmp_path):
    inp = str(tmp_path / "in.csv")
    out = str(tmp_path / "out.csv")
    _write_csv(inp, [{"id": "1", "a": "1"}], ["id", "a"])
    with pytest.raises(ValueError, match="value_vars"):
        reshape_file(inp, out, "melt", ["id"], value_vars=None)
