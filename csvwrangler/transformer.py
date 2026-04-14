"""CSV transformation utilities: filter rows, select columns, rename headers."""

import csv
import io
from typing import Dict, List, Optional


def filter_rows(rows: List[Dict], column: str, value: str, negate: bool = False) -> List[Dict]:
    """Return rows where column matches value (or not, if negate=True)."""
    result = []
    for row in rows:
        if column not in row:
            raise KeyError(f"Column '{column}' not found in row keys: {list(row.keys())}")
        match = row[column] == value
        if negate:
            match = not match
        if match:
            result.append(row)
    return result


def select_columns(rows: List[Dict], columns: List[str]) -> List[Dict]:
    """Return rows containing only the specified columns."""
    missing = [c for c in columns if rows and c not in rows[0]]
    if missing:
        raise KeyError(f"Columns not found in data: {missing}")
    return [{col: row[col] for col in columns} for row in rows]


def rename_columns(rows: List[Dict], mapping: Dict[str, str]) -> List[Dict]:
    """Rename columns according to mapping {old_name: new_name}."""
    result = []
    for row in rows:
        new_row = {}
        for key, val in row.items():
            new_key = mapping.get(key, key)
            new_row[new_key] = val
        result.append(new_row)
    return result


def transform_file(
    input_path: str,
    output_path: str,
    filter_col: Optional[str] = None,
    filter_val: Optional[str] = None,
    negate: bool = False,
    select_cols: Optional[List[str]] = None,
    rename_map: Optional[Dict[str, str]] = None,
) -> int:
    """Apply transformations to a CSV file and write results. Returns row count written."""
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if filter_col and filter_val is not None:
        rows = filter_rows(rows, filter_col, filter_val, negate=negate)

    if rename_map:
        rows = rename_columns(rows, rename_map)

    if select_cols:
        rows = select_columns(rows, select_cols)

    if not rows:
        fieldnames = []
    else:
        fieldnames = list(rows[0].keys())

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)
