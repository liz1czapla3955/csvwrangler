"""Reshape CSV rows: wide-to-long (melt) and long-to-wide (pivot-like unpivot)."""

from __future__ import annotations

import csv
import io
from typing import Iterable, Iterator


def melt_rows(
    rows: Iterable[dict],
    id_vars: list[str],
    value_vars: list[str],
    var_name: str = "variable",
    value_name: str = "value",
) -> Iterator[dict]:
    """Convert wide rows to long format (melt / unpivot).

    Args:
        rows: Iterable of row dicts.
        id_vars: Columns to keep as identifiers.
        value_vars: Columns to unpivot into rows.
        var_name: Name for the new variable column.
        value_name: Name for the new value column.

    Yields:
        One row per id_var/value_var combination.
    """
    for row in rows:
        base = {k: row[k] for k in id_vars if k in row}
        for var in value_vars:
            if var not in row:
                raise KeyError(f"Column '{var}' not found in row")
            yield {**base, var_name: var, value_name: row[var]}


def unmelt_rows(
    rows: Iterable[dict],
    id_vars: list[str],
    var_col: str,
    value_col: str,
) -> list[dict]:
    """Convert long rows back to wide format (unmelt / re-pivot).

    Args:
        rows: Iterable of long-format row dicts.
        id_vars: Columns that identify a unique entity.
        var_col: Column containing variable names.
        value_col: Column containing values.

    Returns:
        List of wide-format rows.
    """
    grouped: dict[tuple, dict] = {}
    for row in rows:
        key = tuple(row.get(k, "") for k in id_vars)
        if key not in grouped:
            grouped[key] = {k: row[k] for k in id_vars if k in row}
        var = row.get(var_col, "")
        grouped[key][var] = row.get(value_col, "")
    return list(grouped.values())


def reshape_file(
    input_path: str,
    output_path: str,
    mode: str,
    id_vars: list[str],
    value_vars: list[str] | None = None,
    var_name: str = "variable",
    value_name: str = "value",
    var_col: str = "variable",
    value_col: str = "value",
) -> None:
    """Read a CSV, reshape it, and write the result."""
    with open(input_path, newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    if mode == "melt":
        if not value_vars:
            raise ValueError("value_vars must be provided for melt mode")
        result = list(melt_rows(rows, id_vars, value_vars, var_name, value_name))
        fieldnames = id_vars + [var_name, value_name]
    elif mode == "unmelt":
        result = unmelt_rows(rows, id_vars, var_col, value_col)
        fieldnames = list(result[0].keys()) if result else []
    else:
        raise ValueError(f"Unknown mode '{mode}'. Use 'melt' or 'unmelt'.")

    with open(output_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result)
