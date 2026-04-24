"""Lag/lead column values by N rows."""

import csv
import io
from collections import deque
from typing import Iterable, Iterator


def lag_rows(
    rows: Iterable[dict],
    column: str,
    n: int = 1,
    output_column: str | None = None,
    fill: str = "",
    lead: bool = False,
) -> Iterator[dict]:
    """Yield rows with a new column containing the lagged (or lead) value.

    Args:
        rows: Iterable of row dicts.
        column: Source column to lag/lead.
        n: Number of positions to shift.  Positive = lag (look back),
           negative values are treated as abs(n) lead regardless of `lead`.
        output_column: Name of the new column.  Defaults to
           '<column>_lag<n>' or '<column>_lead<n>'.
        fill: Value to use when no prior/future row exists.
        lead: If True, shift forward (look ahead) instead of back.
    """
    if n < 0:
        lead = True
        n = abs(n)

    direction = "lead" if lead else "lag"
    out_col = output_column or f"{column}_{direction}{n}"

    rows_list = list(rows)
    total = len(rows_list)

    for i, row in enumerate(rows_list):
        new_row = dict(row)
        if lead:
            src_idx = i + n
        else:
            src_idx = i - n

        if 0 <= src_idx < total:
            new_row[out_col] = rows_list[src_idx].get(column, fill)
        else:
            new_row[out_col] = fill
        yield new_row


def lag_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    column: str,
    n: int,
    output_column: str | None,
    fill: str,
    lead: bool,
) -> None:
    """Stream-process a CSV file applying lag/lead transformation."""
    rows = list(reader)
    if not rows:
        return

    result = list(lag_rows(rows, column, n, output_column, fill, lead))
    writer.fieldnames = list(result[0].keys())
    writer.writeheader()
    for row in result:
        writer.writerow(row)
