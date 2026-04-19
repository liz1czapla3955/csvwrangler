"""Flatten repeated column values by filling down empty cells."""

import csv
import io
from typing import List, Dict, Optional


def fill_down_rows(
    rows: List[Dict[str, str]],
    columns: Optional[List[str]] = None,
) -> List[Dict[str, str]]:
    """Fill down empty cells in specified columns using the last non-empty value.

    Args:
        rows: List of row dicts.
        columns: Column names to fill down. If None, fill all columns.

    Returns:
        New list of row dicts with empty cells filled.
    """
    if not rows:
        return []

    target_cols = columns if columns is not None else list(rows[0].keys())
    last_seen: Dict[str, str] = {col: "" for col in target_cols}
    result = []

    for row in rows:
        new_row = dict(row)
        for col in target_cols:
            if col not in new_row:
                continue
            if new_row[col].strip() == "":
                new_row[col] = last_seen.get(col, "")
            else:
                last_seen[col] = new_row[col]
        result.append(new_row)

    return result


def flatten_file(
    input_path: str,
    output_path: str,
    columns: Optional[List[str]] = None,
) -> None:
    """Read a CSV file, fill down empty cells, and write the result.

    Args:
        input_path: Path to the input CSV file.
        output_path: Path to the output CSV file.
        columns: Column names to fill down. If None, fill all columns.
    """
    with open(input_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames
        if not fieldnames:
            raise ValueError("Input CSV has no header row.")
        rows = list(reader)

    if columns:
        missing = [c for c in columns if c not in fieldnames]
        if missing:
            raise ValueError(f"Columns not found in CSV: {missing}")

    filled = fill_down_rows(rows, columns)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filled)


def flatten_string(
    content: str,
    columns: Optional[List[str]] = None,
) -> str:
    """Fill down empty cells in a CSV string and return the result as a string.

    Useful for in-memory processing without touching the filesystem.

    Args:
        content: CSV content as a string.
        columns: Column names to fill down. If None, fill all columns.

    Returns:
        CSV content with empty cells filled, as a string.
    """
    reader = csv.DictReader(io.StringIO(content))
    fieldnames = reader.fieldnames
    if not fieldnames:
        raise ValueError("Input CSV has no header row.")

    if columns:
        missing = [c for c in columns if c not in fieldnames]
        if missing:
            raise ValueError(f"Columns not found in CSV: {missing}")

    filled = fill_down_rows(list(reader), columns)

    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(filled)
    return out.getvalue()
