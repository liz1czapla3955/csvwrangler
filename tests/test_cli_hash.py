import csv
import hashlib
import os
import tempfile
import types
import pytest
from csvwrangler.cli_hash import run_hash


def _write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _make_args(**kwargs):
    defaults = {"algorithm": "sha256", "suffix": "_hash"}
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


def test_run_hash_success(tmp_path):
    inp = str(tmp_path / "in.csv")
    out = str(tmp_path / "out.csv")
    _write_csv(inp, [{"id": "1", "email": "a@b.com"}], ["id", "email"])
    args = _make_args(input=inp, output=out, columns="email")
    run_hash(args)
    rows = _read_csv(out)
    expected = hashlib.sha256("a@b.com".encode()).hexdigest()
    assert rows[0]["email_hash"] == expected


def test_run_hash_md5(tmp_path):
    inp = str(tmp_path / "in.csv")
    out = str(tmp_path / "out.csv")
    _write_csv(inp, [{"id": "1", "name": "Alice"}], ["id", "name"])
    args = _make_args(input=inp, output=out, columns="name", algorithm="md5")
    run_hash(args)
    rows = _read_csv(out)
    expected = hashlib.md5("Alice".encode()).hexdigest()
    assert rows[0]["name_hash"] == expected


def test_run_hash_bad_input_exits(tmp_path):
    out = str(tmp_path / "out.csv")
    args = _make_args(input="nonexistent.csv", output=out, columns="email")
    with pytest.raises(SystemExit):
        run_hash(args)
