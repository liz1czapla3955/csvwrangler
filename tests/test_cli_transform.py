import csv
import os
import tempfile
import types
import pytest
from csvwrangler.cli_transform import run_transform


def _write_csv(path, rows):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _make_args(**kwargs):
    defaults = dict(
        filter_expr=None,
        negate=False,
        select=None,
        rename=None,
        add_column=None,
    )
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


@pytest.fixture()
def csv_file(tmp_path):
    rows = [
        {"id": "1", "name": "Alice", "city": "NYC"},
        {"id": "2", "name": "Bob", "city": "LA"},
        {"id": "3", "name": "Alice", "city": "NYC"},
    ]
    p = tmp_path / "input.csv"
    _write_csv(str(p), rows)
    return str(p)


def test_run_transform_filter(csv_file, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _make_args(input=csv_file, output=out, filter_expr="name=Alice")
    run_transform(args)
    rows = _read_csv(out)
    assert len(rows) == 2
    assert all(r["name"] == "Alice" for r in rows)


def test_run_transform_filter_negate(csv_file, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _make_args(input=csv_file, output=out, filter_expr="name=Alice", negate=True)
    run_transform(args)
    rows = _read_csv(out)
    assert len(rows) == 1
    assert rows[0]["name"] == "Bob"


def test_run_transform_select(csv_file, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _make_args(input=csv_file, output=out, select=["id", "name"])
    run_transform(args)
    rows = _read_csv(out)
    assert list(rows[0].keys()) == ["id", "name"]
    assert len(rows) == 3


def test_run_transform_rename(csv_file, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _make_args(input=csv_file, output=out, rename=["name=full_name"])
    run_transform(args)
    rows = _read_csv(out)
    assert "full_name" in rows[0]
    assert "name" not in rows[0]


def test_run_transform_add_column(csv_file, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _make_args(input=csv_file, output=out, add_column="source=test")
    run_transform(args)
    rows = _read_csv(out)
    assert all(r["source"] == "test" for r in rows)


def test_run_transform_bad_filter_exits(csv_file, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _make_args(input=csv_file, output=out, filter_expr="badfilter")
    with pytest.raises(SystemExit):
        run_transform(args)


def test_run_transform_bad_rename_exits(csv_file, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _make_args(input=csv_file, output=out, rename=["badpair"])
    with pytest.raises(SystemExit):
        run_transform(args)
