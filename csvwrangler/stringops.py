"""String operations on CSV column values."""

import csv
import io
from typing import Iterable, Iterator


DEFAULT_FILL = ""


def _apply_op(value: str, op: str, arg: str = "") -> str:
    if op == "upper":
        return value.upper()
    elif op == "lower":
        return value.lower()
    elif op == "strip":
        return value.strip()
    elif op == "lstrip":
        return value.lstrip()
    elif op == "rstrip":
        return value.rstrip()
    elif op == "title":
        return value.title()
    elif op == "replace":
        if ":" not in arg:
            raise ValueError(f"replace arg must be 'old:new', got: {arg!r}")
        old, new = arg.split(":", 1)
        return value.replace(old, new)
    elif op == "prefix":
        return arg + value
    elif op == "suffix":
        return value + arg
    elif op == "zfill":
        try:
            width = int(arg)
        except (ValueError, TypeError):
            raise ValueError(f"zfill arg must be an integer, got: {arg!r}")
        return value.zfill(width)
    else:
        raise ValueError(f"Unknown string op: {op!r}")


def stringops_rows(
    rows: Iterable[dict],
    column: str,
    op: str,
    arg: str = "",
) -> Iterator[dict]:
    """Apply a string operation to a column in each row."""
    for row in rows:
        row = dict(row)
        if column in row:
            row[column] = _apply_op(row[column], op, arg)
        yield row


def stringops_file(
    input_path: str,
    output_path: str,
    column: str,
    op: str,
    arg: str = "",
) -> None:
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(stringops_rows(reader, column, op, arg))

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
