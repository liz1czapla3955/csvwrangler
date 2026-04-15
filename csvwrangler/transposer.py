"""Transpose CSV: rows become columns and columns become rows."""

import csv
import io
from typing import List, Dict, Optional


def transpose_rows(rows: List[Dict[str, str]], index_col: Optional[str] = None) -> List[Dict[str, str]]:
    """
    Transpose a list of row dicts so that each original column becomes a row.

    If index_col is provided, its values become the new column headers.
    Otherwise, synthetic headers 'row_0', 'row_1', ... are used.

    The first column of the output is always 'field', containing original header names.
    """
    if not rows:
        return []

    headers = list(rows[0].keys())

    if index_col is not None:
        if index_col not in headers:
            raise ValueError(f"index_col '{index_col}' not found in headers: {headers}")
        col_names = [row[index_col] for row in rows]
        value_headers = [h for h in headers if h != index_col]
    else:
        col_names = [f"row_{i}" for i in range(len(rows))]
        value_headers = headers

    out_headers = ["field"] + col_names
    result = []

    for field in value_headers:
        new_row: Dict[str, str] = {"field": field}
        for col_name, row in zip(col_names, rows):
            new_row[col_name] = row.get(field, "")
        result.append(new_row)

    return result


def transpose_file(
    input_path: str,
    output_path: str,
    index_col: Optional[str] = None,
) -> None:
    """Read a CSV file, transpose it, and write the result to output_path."""
    with open(input_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    transposed = transpose_rows(rows, index_col=index_col)

    if not transposed:
        with open(output_path, "w", newline="", encoding="utf-8") as fh:
            fh.write("")
        return

    fieldnames = list(transposed[0].keys())
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(transposed)
