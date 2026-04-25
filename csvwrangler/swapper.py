"""Column value swapper: swap the values of two columns row-by-row."""

import csv
import io
from typing import Iterator


def swap_rows(
    rows: Iterator[dict],
    col_a: str,
    col_b: str,
) -> Iterator[dict]:
    """Yield rows with the values of *col_a* and *col_b* exchanged.

    Rows that are missing one or both columns are passed through unchanged.
    """
    for row in rows:
        if col_a in row and col_b in row:
            new_row = dict(row)
            new_row[col_a], new_row[col_b] = row[col_b], row[col_a]
            yield new_row
        else:
            yield row


def swap_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    col_a: str,
    col_b: str,
) -> None:
    """Read from *reader*, swap *col_a* and *col_b*, write to *writer*."""
    writer.writeheader()
    for row in swap_rows(reader, col_a, col_b):
        writer.writerow(row)
