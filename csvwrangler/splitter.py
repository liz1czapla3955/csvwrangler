"""Split a CSV file into multiple files based on the value of a column."""

import csv
import os
from typing import Dict, IO, List, Optional


def split_rows(
    rows: List[Dict[str, str]],
    column: str,
) -> Dict[str, List[Dict[str, str]]]:
    """Group rows by the value of *column*.

    Returns a dict mapping each distinct value to the list of rows that
    carry that value.  Raises ``KeyError`` if *column* is not present in
    any row.
    """
    if not rows:
        return {}

    if column not in rows[0]:
        raise KeyError(f"Column '{column}' not found in CSV headers.")

    groups: Dict[str, List[Dict[str, str]]] = {}
    for row in rows:
        key = row[column]
        groups.setdefault(key, []).append(row)
    return groups


def split_file(
    input_path: str,
    column: str,
    output_dir: str,
    prefix: str = "",
    keep_column: bool = True,
) -> List[str]:
    """Split *input_path* into one CSV file per distinct value in *column*.

    Files are written to *output_dir* and named ``<prefix><value>.csv``.
    If *keep_column* is ``False`` the split column is omitted from the
    output files.  Returns a sorted list of the paths that were written.
    """
    os.makedirs(output_dir, exist_ok=True)

    with open(input_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        fieldnames: List[str] = list(reader.fieldnames or [])

    groups = split_rows(rows, column)

    out_fieldnames = fieldnames
    if not keep_column:
        out_fieldnames = [f for f in fieldnames if f != column]

    written: List[str] = []
    for value, group_rows in groups.items():
        safe_value = "".join(c if c.isalnum() or c in "-_" else "_" for c in value)
        out_path = os.path.join(output_dir, f"{prefix}{safe_value}.csv")
        with open(out_path, "w", newline="", encoding="utf-8") as out_fh:
            writer = csv.DictWriter(
                out_fh,
                fieldnames=out_fieldnames,
                extrasaction="ignore",
            )
            writer.writeheader()
            writer.writerows(group_rows)
        written.append(out_path)

    return sorted(written)
